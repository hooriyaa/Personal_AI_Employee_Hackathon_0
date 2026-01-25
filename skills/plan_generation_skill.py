"""
Plan Generation Skill - Creates structured plans for tasks.

This skill reads task files from the Needs_Action directory and creates
corresponding plan files in the Plans directory with a structured format
that includes a checklist of steps to complete the task.
"""

import os
import re
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict

from src.models.entities import PlanEntity, PlanStep, TaskEntity, create_task_entity_from_email
from src.utils.helpers import find_files, sanitize_filename
from src.config.settings import PENDING_APPROVAL_DIR
from src.utils.helpers import move_file
from src.config.settings import NEEDS_ACTION_DIR, DONE_DIR


class PlanGenerationSkill:
    """Generates structured plans for tasks that need action."""
    
    def __init__(self, needs_action_dir=None, plans_dir=None):
        """
        Initialize the plan generation skill.
        
        Args:
            needs_action_dir (str or Path): Directory containing task files
            plans_dir (str or Path): Directory to save plan files
        """
        from src.config.settings import NEEDS_ACTION_DIR, PLANS_DIR
        
        self.needs_action_dir = Path(needs_action_dir) if needs_action_dir else NEEDS_ACTION_DIR
        self.plans_dir = Path(plans_dir) if plans_dir else PLANS_DIR
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('Logs/plan_generation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def extract_task_info_from_markdown(self, file_path: Path) -> TaskEntity:
        """
        Extract task information from a Markdown file.
        
        Args:
            file_path (Path): Path to the Markdown file containing the task
            
        Returns:
            TaskEntity: Extracted task information
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract information using regex
        # Extract subject (first H1 or first line)
        subject_match = re.search(r'^#\s+(.+)$|^# (.+)$', content, re.MULTILINE)
        subject = subject_match.group(1) if subject_match else file_path.stem
        
        # Extract sender/from
        sender_match = re.search(r'\*\*From:\*\*\s*(.+)', content)
        sender = sender_match.group(1) if sender_match else "Unknown"
        
        # Extract body content (everything after headers)
        body_start = content.find("---")
        if body_start != -1:
            body = content[body_start + 4:].strip()  # Skip "---\n"
        else:
            body = content
        
        # Create a basic task entity
        task = TaskEntity(
            title=subject,
            content=body,
            assigned_to=sender,
            priority="MEDIUM"  # Default priority, could be enhanced based on email urgency
        )
        
        return task

    def generate_plan_steps(self, task_entity: TaskEntity) -> List[PlanStep]:
        """
        Generate a list of steps for the plan based on the task.
        
        Args:
            task_entity (TaskEntity): The task entity to generate steps for
            
        Returns:
            List[PlanStep]: List of steps for the plan
        """
        steps = []
        
        # Analyze the task content to determine appropriate steps
        content_lower = task_entity.content.lower()
        
        # Common patterns that suggest specific actions
        if any(keyword in content_lower for keyword in ['meeting', 'schedule', 'appointment']):
            steps.append(PlanStep(description="Check calendar for available slots"))
            steps.append(PlanStep(description="Propose meeting times to participants"))
            steps.append(PlanStep(description="Schedule confirmed meeting"))
        
        if any(keyword in content_lower for keyword in ['report', 'summary', 'analysis']):
            steps.append(PlanStep(description="Gather required data"))
            steps.append(PlanStep(description="Analyze the data"))
            steps.append(PlanStep(description="Draft the report"))
            steps.append(PlanStep(description="Review and finalize report"))
        
        if any(keyword in content_lower for keyword in ['follow up', 'follow-up', 'check in']):
            steps.append(PlanStep(description="Identify the person/entity to follow up with"))
            steps.append(PlanStep(description="Prepare follow-up message"))
            steps.append(PlanStep(description="Send follow-up communication"))
        
        if any(keyword in content_lower for keyword in ['urgent', 'asap', 'immediately']):
            steps.append(PlanStep(description="Prioritize this task"))
            steps.append(PlanStep(description="Address the urgent matter immediately"))
        
        # Add generic steps if no specific ones were identified
        if not steps:
            steps.append(PlanStep(description="Review the request in detail"))
            steps.append(PlanStep(description="Determine the appropriate response/action"))
            steps.append(PlanStep(description="Execute the required action"))
            steps.append(PlanStep(description="Confirm completion"))
        
        # Add a final step to mark as complete
        steps.append(PlanStep(description="Mark task as completed and archive"))
        
        return steps

    def create_plan_from_task(self, task_file_path: Path) -> Path:
        """
        Create a plan from a task file.

        Args:
            task_file_path (Path): Path to the task file

        Returns:
            Path: Path to the created plan file
        """
        try:
            # Extract task info from the file
            task_entity = self.extract_task_info_from_markdown(task_file_path)

            # Generate steps for the plan
            steps = self.generate_plan_steps(task_entity)

            # Create plan entity
            plan_entity = PlanEntity(
                task_id=task_entity.id,
                title=f"Plan for: {task_entity.title}",
                description=f"Action plan generated for task: {task_entity.title}",
                steps=steps,
                status="DRAFT"
            )

            # Create plan file name based on the task file
            task_stem = task_file_path.stem
            safe_task_stem = sanitize_filename(task_stem)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plan_filename = f"PLAN_{timestamp}_{safe_task_stem}.md"

            plan_file_path = self.plans_dir / plan_filename

            # Write the plan to a markdown file
            self.write_plan_to_file(plan_entity, plan_file_path)

            self.logger.info(f"Created plan file: {plan_file_path}")

            # Also create a file in Pending_Approval for automated reply
            self.create_approval_file(task_file_path, task_entity)

            return plan_file_path

        except Exception as e:
            self.logger.error(f"Error creating plan from task {task_file_path}: {e}")
            raise

    def create_approval_file(self, task_file_path: Path, task_entity: TaskEntity):
        """
        Create a file in Pending_Approval for automated reply.

        Args:
            task_file_path (Path): Path to the original task file
            task_entity (TaskEntity): The task entity with extracted information
        """
        try:
            # Extract sender and subject from the task entity
            # For this, we need to parse the original file content to extract the sender
            with open(task_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract sender from the "From:" field in the markdown
            sender_match = re.search(r'\*\*From:\*\*\s*(.+)', content)
            sender_full = sender_match.group(1).strip() if sender_match else "unknown@example.com"

            # Extract just the name from the sender field (e.g., "Ali" from "Ali <email@domain.com>")
            sender_name = sender_full.strip()
            has_name = False  # Flag to check if we have a proper name

            # Define the AI employee's name to avoid self-addressing
            ai_employee_names = ["Hooriya M.Fareed", "hooriya m.fareed", "hooriya m fareed"]

            if '<' in sender_full and '>' in sender_full:
                # Handle format like "Name <email@domain.com>" or Name <email@domain.com>
                name_part = sender_full.split('<')[0].strip()
                if name_part:
                    # Remove quotes if they exist
                    sender_name = name_part.strip().strip('"\'')
                    # Check if we have a meaningful name (not just quotes)
                    if sender_name and sender_name not in ['"', "'"]:
                        # Check if the name is the AI employee's own name (avoid self-addressing)
                        if sender_name.lower() not in [name.lower() for name in ai_employee_names]:
                            has_name = True
                        else:
                            has_name = False  # Don't use the AI's own name in greeting
                    else:
                        # If name is just quotes or empty, extract from email
                        email_part = sender_full.split('<')[1].split('>')[0]
                        sender_name = email_part.split('@')[0]  # Use part before @ as name
                        has_name = False
                else:
                    # If there's no name part, extract from email
                    email_part = sender_full.split('<')[1].split('>')[0]
                    sender_name = email_part.split('@')[0]  # Use part before @ as name
                    has_name = False
            elif '@' in sender_full and ' ' not in sender_full:
                # Just email address, extract name from before @
                sender_name = sender_full.split('@')[0]
                has_name = False
            else:
                # If it's just a name without email format, use it
                sender_name = sender_full.strip().strip('"\'')
                # Check if the name is the AI employee's own name (avoid self-addressing)
                if sender_name and sender_name not in ['"', "'"]:
                    if sender_name.lower() not in [name.lower() for name in ai_employee_names]:
                        has_name = True
                    else:
                        has_name = False  # Don't use the AI's own name in greeting
                else:
                    has_name = False

            # Extract subject from the H1 header
            subject_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            original_subject = subject_match.group(1).strip() if subject_match else "No Subject"

            # Create professional, personalized email body using the requested template
            # Format the body with newlines for proper multi-line handling
            if has_name:
                greeting = f"Dear {sender_name},"
            else:
                greeting = "Dear,"

            email_body = f"""{greeting}

Thank you for reaching out regarding "{original_subject}".

I have received your email and marked it as a priority. I am currently reviewing the details you provided and will get back to you with a comprehensive response shortly.

If there are any immediate deadlines I should be aware of, please let me know.

Best Regards,

Hooriya M. Fareed
Agentic AI | Frontend Developer 
(Sent via AI Employee)"""

            # Create approval file content with proper format for multi-line body
            # Using the format where headers and body are separated by an empty line
            approval_content = f"""type: email_send
to: {sender_full}
subject: Re: {original_subject}

{greeting}

Thank you for reaching out regarding "{original_subject}".

I have received your email and marked it as a priority. I am currently reviewing the details you provided and will get back to you with a comprehensive response shortly.

If there are any immediate deadlines I should be aware of, please let me know.

Best Regards,

Hooriya M. Fareed
Agentic AI | Frontend Developer
(Sent via AI Employee)"""

            # Create approval file name based on the task file
            task_stem = task_file_path.stem
            safe_task_stem = sanitize_filename(task_stem)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            approval_filename = f"APPROVAL_{timestamp}_{safe_task_stem}.txt"

            approval_file_path = PENDING_APPROVAL_DIR / approval_filename

            # Write the approval content to a text file
            with open(approval_file_path, 'w', encoding='utf-8') as f:
                f.write(approval_content)

            self.logger.info(f"Created approval file: {approval_file_path}")

        except Exception as e:
            self.logger.error(f"Error creating approval file from task {task_file_path}: {e}")
            raise

    def write_plan_to_file(self, plan_entity: PlanEntity, file_path: Path):
        """
        Write a plan entity to a Markdown file with a structured format.
        
        Args:
            plan_entity (PlanEntity): The plan entity to write
            file_path (Path): Path to the file to write to
        """
        # Ensure the plans directory exists
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            # Write plan header
            f.write(f"# {plan_entity.title}\n\n")
            f.write(f"**Task ID:** {plan_entity.task_id}\n")
            f.write(f"**Created:** {plan_entity.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Status:** {plan_entity.status.value if hasattr(plan_entity.status, 'value') else plan_entity.status}\n")
            
            if plan_entity.estimated_duration:
                f.write(f"**Estimated Duration:** {plan_entity.estimated_duration} minutes\n")
            
            f.write(f"\n## Description\n{plan_entity.description}\n\n")
            
            # Write steps as a checklist
            f.write("## Action Steps\n\n")
            for step in plan_entity.steps:
                status = "x" if step.completed else " "
                f.write(f"- [{status}] {step.description}  \n")
            
            # Add a section for notes
            f.write("\n## Notes\n\n")
            f.write("<!-- Add any additional notes or context here -->\n\n")
            
            # Add a section for completion
            f.write("## Completion\n\n")
            f.write("- [ ] Review and approve plan\n")
            f.write("- [ ] Execute all steps\n")
            f.write("- [ ] Mark task as completed\n")

    def process_tasks(self) -> List[Path]:
        """
        Process all task files in the Needs_Action directory.

        Returns:
            List[Path]: List of paths to created plan files
        """
        created_plans = []

        # Find all markdown files in the needs action directory
        task_files = find_files(self.needs_action_dir, "*.md", recursive=False)

        self.logger.info(f"Found {len(task_files)} task files to process")

        for task_file in task_files:
            try:
                # Create a plan for each task file
                plan_file = self.create_plan_from_task(task_file)
                created_plans.append(plan_file)

                # Move the task file to the Done directory after plan creation
                done_dir = DONE_DIR
                done_dir.mkdir(parents=True, exist_ok=True)

                # Create destination path in Done directory
                dest_path = done_dir / task_file.name

                # Move the file
                if move_file(task_file, dest_path):
                    self.logger.info(f"Moved task file from Needs_Action to Done: {task_file.name}")
                else:
                    self.logger.error(f"Failed to move task file: {task_file.name}")

            except Exception as e:
                self.logger.error(f"Error processing task file {task_file}: {e}")

        return created_plans

    def run_once(self):
        """Run the plan generation process once."""
        self.logger.info("Starting plan generation process...")
        
        try:
            created_plans = self.process_tasks()
            self.logger.info(f"Completed plan generation. Created {len(created_plans)} plan files.")
            
            for plan_path in created_plans:
                self.logger.info(f"Created plan: {plan_path}")
                
        except Exception as e:
            self.logger.error(f"Error during plan generation: {e}")


def main():
    """Main entry point for testing the plan generation skill."""
    skill = PlanGenerationSkill()
    skill.run_once()


if __name__ == "__main__":
    main()