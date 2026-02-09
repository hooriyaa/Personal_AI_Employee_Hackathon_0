"""
Plan Generation Skill - Creates structured plans for tasks.

This skill reads task files from the Needs_Action directory and creates
corresponding plan files in the Plans directory with a structured format
that includes a checklist of steps to complete the task.
"""

import os
import re
import random
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict

from src.models.entities import PlanEntity, PlanStep, TaskEntity, create_task_entity_from_email
from src.utils.helpers import find_files, sanitize_filename
from src.config.settings import PENDING_APPROVAL_DIR
from src.utils.helpers import move_file
from src.config.settings import NEEDS_ACTION_DIR, DONE_DIR

# Import the new Gemini service
try:
    from src.services.gemini_service import GeminiService
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Google Generative AI library not found. Install with: pip install google-generativeai")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


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

        # Configure logging first
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('Logs/plan_generation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Load environment variables to ensure API keys are available
        load_dotenv()

        # Initialize the Gemini service if available
        self.gemini_service = None
        if GEMINI_AVAILABLE:
            try:
                self.gemini_service = GeminiService()
            except Exception as e:
                self.logger.warning(f"Gemini service initialization failed: {e}. Falling back to static templates.")

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
        Create a file in Pending_Approval for automated reply or LinkedIn post.

        Args:
            task_file_path (Path): Path to the original task file
            task_entity (TaskEntity): The task entity with extracted information
        """
        try:
            # Read the content of the task file
            with open(task_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Initialize variables to prevent UnboundLocalError
            sender_name = "Unknown"
            email_body_content = ""

            # Check if the content explicitly indicates a LinkedIn post request
            content_lower = content.lower()

            # Extract subject for explicit check
            subject_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            subject = subject_match.group(1).strip().lower() if subject_match else ""

            # Check for explicit LinkedIn post request
            is_linkedin_post = (
                'linkedin post' in subject or
                'generate post' in subject or
                content_lower.startswith('please write a post') or
                content_lower.startswith('draft a post')
            )

            if is_linkedin_post:
                # Extract body content to use as topic for LinkedIn post
                body_start = content.find("---")
                if body_start != -1:
                    email_body_content = content[body_start + 4:].strip()  # Skip "---\n"
                else:
                    email_body_content = content

                # Use the email body content as the topic for the LinkedIn post
                topic = email_body_content.strip() if email_body_content.strip() else "the latest tech trends"
                
                # Generate a creative, professional LinkedIn post about the specific topic
                linkedin_post_content = self.generate_linkedin_post(topic)

                # Create approval file content for LinkedIn post
                approval_content = f"""type: linkedin_post
content: {linkedin_post_content}"""

                # Create approval file name for LinkedIn post
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                approval_filename = f"DRAFT_LINKEDIN_POST_{timestamp}.md"

                approval_file_path = PENDING_APPROVAL_DIR / approval_filename

                # Write the approval content to a text file
                with open(approval_file_path, 'w', encoding='utf-8') as f:
                    f.write(approval_content)

                self.logger.info(f"Created LinkedIn post draft: {approval_file_path}")
            else:
                # Handle the original email reply functionality
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

                # Extract body content to analyze intent
                body_start = content.find("---")
                if body_start != -1:
                    email_body_content = content[body_start + 4:].strip()  # Skip "---\n"
                else:
                    email_body_content = content

                # Analyze intent based on keywords
                subject_lower = original_subject.lower()
                content_lower = email_body_content.lower()
                
                # Combine subject and body for comprehensive analysis
                full_text_to_analyze = f"{subject_lower} {content_lower}"

                # Step A (Analyze): Check the combined subject and body for keywords to determine the "Intent"
                if any(keyword in full_text_to_analyze for keyword in ['schedule', 'availability', 'time']):
                    intent = "SCHEDULING"
                elif any(keyword in full_text_to_analyze for keyword in ['price', 'quote', 'invoice', 'cost']):
                    intent = "BUSINESS"
                elif any(keyword in full_text_to_analyze for keyword in ['job', 'hiring', 'resume', 'opportunity']):
                    intent = "CAREER"
                elif any(keyword in full_text_to_analyze for keyword in ['help', 'error', 'bug', 'issue']):
                    intent = "SUPPORT"
                elif any(keyword in full_text_to_analyze for keyword in ['happy', 'birthday', 'congrats', 'congratulation', 'thanks', 'welcome', 'good job', 'wishes', 'celebration', 'party', 'gift']):
                    intent = "SOCIAL"
                else:
                    intent = "GENERAL"

                # Extract information from the email for context-aware responses
                # Extract subject for topic awareness
                subject_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                extracted_topic = subject_match.group(1).strip() if subject_match else "your inquiry"

                # Clean the topic to make it more natural in the response
                extracted_topic_clean = extracted_topic.replace('_', ' ').replace('-', ' ')

                # Define dynamic variables for email generation with context awareness
                greetings_list = [
                    f"Dear {sender_name},",
                    f"Hi {sender_name},",
                    f"Hello {sender_name},",
                    f"Greetings {sender_name},"
                ] if has_name else [
                    "Dear,",
                    "Hi there,",
                    "Hello,",
                    "Greetings,"
                ]

                # Context-aware openers based on intent and extracted information
                if intent == "CAREER":
                    openers_list = [
                        f"Thank you for applying for the '{extracted_topic_clean}' position. I have received your resume and am reviewing your qualifications...",
                        f"I appreciate your interest in the '{extracted_topic_clean}' role. Your application has been noted...",
                        f"Thank you for your application regarding '{extracted_topic_clean}'. I'm reviewing your submission now..."
                    ]
                elif intent == "SCHEDULING":
                    openers_list = [
                        f"I received your request to discuss '{extracted_topic_clean}'. I am checking my availability for this...",
                        f"Thank you for reaching out about scheduling for '{extracted_topic_clean}'. I'm looking at my calendar now...",
                        f"I understand you'd like to schedule time to discuss '{extracted_topic_clean}'. Checking my availability..."
                    ]
                elif intent == "SUPPORT":
                    openers_list = [
                        f"I understand you're experiencing an issue with '{extracted_topic_clean}'. I've logged this ticket...",
                        f"Thank you for reporting the '{extracted_topic_clean}' issue. I'm addressing this immediately...",
                        f"I acknowledge your concern about '{extracted_topic_clean}'. This has been escalated for resolution..."
                    ]
                elif intent == "SOCIAL":
                    openers_list = [
                        "Thank you so much for the kind words!",
                        "It was such a pleasant surprise to hear from you.",
                        "Thanks for the warm wishes!"
                    ]
                elif intent == "BUSINESS":
                    openers_list = [
                        f"I have received your inquiry regarding '{extracted_topic_clean}'. I'm reviewing the details now...",
                        f"Thank you for your business inquiry about '{extracted_topic_clean}'. I'm analyzing the requirements...",
                        f"I acknowledge your request for information about '{extracted_topic_clean}'. Reviewing the details..."
                    ]
                else:  # GENERAL
                    # Check if the content looks like a problem or issue
                    problem_indicators = ['problem', 'issue', 'error', 'bug', 'help', 'fix', 'trouble', 'concern', 'difficulty']
                    if any(indicator in content_lower for indicator in problem_indicators):
                        openers_list = [
                            f"I have received your message about '{extracted_topic_clean}'. I understand you're facing an issue and am looking into it...",
                            f"Thank you for bringing '{extracted_topic_clean}' to my attention. I'm evaluating the situation...",
                            f"I acknowledge your concern about '{extracted_topic_clean}'. I'm investigating this matter..."
                        ]
                    else:
                        openers_list = [
                            f"I have received your message about '{extracted_topic_clean}'. I appreciate you reaching out...",
                            f"Thank you for contacting me regarding '{extracted_topic_clean}'. I acknowledge your communication...",
                            f"I've received your note about '{extracted_topic_clean}' and will get back to you."
                        ]

                # Context-aware solutions based on intent
                if intent == "CAREER":
                    solutions_list = [
                        f"I am actively reviewing your qualifications for the '{extracted_topic_clean}' position and will get back to you soon.",
                        f"Your application for '{extracted_topic_clean}' is being carefully considered by our team.",
                        f"I have prioritized your application for '{extracted_topic_clean}' and am coordinating with the hiring team."
                    ]
                elif intent == "SCHEDULING":
                    solutions_list = [
                        f"I am checking my calendar for '{extracted_topic_clean}' and will confirm available times shortly.",
                        f"I'm coordinating schedules for '{extracted_topic_clean}' and will provide options soon.",
                        f"I have added '{extracted_topic_clean}' to my priority tasks and will confirm timing shortly."
                    ]
                elif intent == "SUPPORT":
                    solutions_list = [
                        f"I am actively troubleshooting '{extracted_topic_clean}' and will provide updates on resolution.",
                        f"This '{extracted_topic_clean}' issue is being handled promptly by our support system.",
                        f"I have escalated '{extracted_topic_clean}' immediately and am monitoring the situation."
                    ]
                elif intent == "SOCIAL":
                    solutions_list = [
                        "I really appreciate you thinking of me.",
                        "It means a lot to receive this message.",
                        "You made my day!"
                    ]
                elif intent == "BUSINESS":
                    solutions_list = [
                        f"I am reviewing the details of '{extracted_topic_clean}' and will provide you with accurate information.",
                        f"The '{extracted_topic_clean}' inquiry is being processed and I'll share relevant details soon.",
                        f"I'm analyzing the requirements for '{extracted_topic_clean}' and will follow up with specifics."
                    ]
                else:  # GENERAL
                    # Check if the content looks like a problem or issue
                    problem_indicators = ['problem', 'issue', 'error', 'bug', 'help', 'fix', 'trouble', 'concern', 'difficulty']
                    if any(indicator in content_lower for indicator in problem_indicators):
                        solutions_list = [
                            f"I am actively working on resolving '{extracted_topic_clean}' and will provide updates on progress.",
                            f"This '{extracted_topic_clean}' matter is being handled promptly by our system.",
                            f"I have prioritized '{extracted_topic_clean}' and am monitoring the situation closely."
                        ]
                    else:
                        solutions_list = [
                            f"I've reviewed your note about '{extracted_topic_clean}' and will follow up with more information soon.",
                            f"I'm considering your message about '{extracted_topic_clean}' and will get back to you with details.",
                            f"I have received your communication about '{extracted_topic_clean}' and will respond appropriately."
                        ]

                if intent == "SOCIAL":
                    closings_list = [
                        "Best wishes,",
                        "Warmly,",
                        "Talk soon,",
                        "With gratitude,",
                        "Affectionately,",
                        "Cheers,"
                    ]
                else:
                    # For GENERAL intent, use softer language if not a problem/issue
                    problem_indicators = ['problem', 'issue', 'error', 'bug', 'help', 'fix', 'trouble', 'concern', 'difficulty']
                    if any(indicator in content_lower for indicator in problem_indicators):
                        closings_list = [
                            "Best regards,",
                            "Best,",
                            "Kind regards,",
                            "Warm regards,",
                            "Sincerely,",
                            "Cheers,"
                        ]
                    else:
                        closings_list = [
                            "Best regards,",
                            "Best,",
                            "Kind regards,",
                            "Warm regards,",
                            "Sincerely,",
                            "Talk soon,",
                            "Cheers,"
                        ]

                signatures_list = [
                    "Hooriya M. Fareed\nAgentic AI | Frontend Developer\n(Sent via AI Employee)",
                    "Hooriya M. Fareed\nAI Agent Specialist\n(Sent via AI Employee)",
                    "Hooriya M. Fareed\nAutomated Response System\n(Sent via AI Employee)"
                ]

                # Step B (Draft): Generate the reply content based on the Intent
                # Initialize variables to prevent NameError in exception handling
                greeting = ""
                opener = ""
                solution = ""
                closing = ""
                signature = random.choice([
                    "Hooriya M. Fareed\nAgentic AI | Frontend Developer\n(Sent via AI Employee)",
                    "Hooriya M. Fareed\nAI Agent Specialist\n(Sent via AI Employee)",
                    "Hooriya M. Fareed\nAutomated Response System\n(Sent via AI Employee)"
                ])

                # Use Gemini service if available, otherwise fall back to static templates
                if self.gemini_service:
                    try:
                        result = self.gemini_service.generate_email_reply(
                            email_body=email_body_content,
                            sender_name=sender_name,
                            intent=intent
                        )

                        if result.get("success"):
                            # If Gemini is successful, use the generated content directly
                            email_body = result["content"]
                        else:
                            # Use fallback message if Gemini API fails
                            self.logger.warning(f"Gemini API failed for email reply: {result.get('error')}")
                            # For fallback, we'll use the static template approach below
                            use_static_template = True
                    except Exception as e:
                        self.logger.error(f"Error using Gemini service for email reply: {e}")
                        # Fall back to static templates if Gemini service fails
                        use_static_template = True
                else:
                    # Fall back to static templates if Gemini service is not available
                    use_static_template = True

                # If we need to use static templates (either Gemini not available or failed)
                if 'use_static_template' in locals() and use_static_template:
                    # Select random elements from each list for static template approach
                    greeting = random.choice(greetings_list)
                    opener = random.choice(openers_list)
                    solution = random.choice(solutions_list)
                    closing = random.choice(closings_list)
                    signature = random.choice([
                        "Hooriya M. Fareed\nAgentic AI | Frontend Developer\n(Sent via AI Employee)",
                        "Hooriya M. Fareed\nAI Agent Specialist\n(Sent via AI Employee)",
                        "Hooriya M. Fareed\nAutomated Response System\n(Sent via AI Employee)"
                    ])

                    # Create dynamic email body based on intent with context awareness
                    if intent == "SOCIAL":
                        # For social emails, use a simpler format to avoid repetitive content
                        email_body = f"""{greeting}

{opener}

{closing}

{signature}"""
                    else:
                        email_body = f"""{greeting}

{opener}

{solution}

{closing}

{signature}"""

                # Extract email address from sender_full (e.g., from "Name <email@domain.com>")
                email_pattern = r'<([^>]+)>'
                email_match = re.search(email_pattern, sender_full)

                if email_match:
                    extracted_email = email_match.group(1)
                else:
                    # If no email found in angle brackets, try to extract any email-like string
                    potential_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', sender_full)
                    if potential_emails:
                        extracted_email = potential_emails[0]
                    else:
                        extracted_email = sender_full  # Use the raw string if no email found
                        self.logger.warning(f"No email address found in sender field: {sender_full}. Using raw string.")

                # Step C (Format): Ensure the final file in /Pending_Approval follows strict YAML format for ActionRunner
                approval_content = f"""type: email_send
to: {extracted_email}
subject: Re: {original_subject}

{email_body}"""

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

    def generate_linkedin_post(self, topic):
        """
        Generate a creative, professional LinkedIn post about a specific topic.

        Args:
            topic (str): The topic to write the LinkedIn post about

        Returns:
            str: Generated LinkedIn post content with hashtags
        """
        # Use Gemini service if available, otherwise fall back to static templates
        if self.gemini_service:
            try:
                result = self.gemini_service.generate_linkedin_post(topic)
                if result.get("success"):
                    return result["content"]
                else:
                    # Use fallback message if Gemini API fails
                    self.logger.warning(f"Gemini API failed for LinkedIn post: {result.get('error')}")
                    return result.get("fallback_message", f"Just exploring {topic} today. The potential for innovation is incredible!")
            except Exception as e:
                self.logger.error(f"Error using Gemini service for LinkedIn post: {e}")
                # Fall back to static templates if Gemini service fails
                return self._generate_static_linkedin_post(topic)
        else:
            # Use static templates if Gemini service is not available
            return self._generate_static_linkedin_post(topic)

    def _generate_static_linkedin_post(self, topic):
        """
        Generate a LinkedIn post using static templates (fallback method).

        Args:
            topic (str): The topic to write the LinkedIn post about

        Returns:
            str: Generated LinkedIn post content with hashtags
        """
        import random

        # Create a list of randomized templates that include the topic variable
        templates = [
            f"🚀 Just started working on {topic}! It's amazing to see how this technology is transforming our workflow. #Tech #Innovation",
            f"💡 Insight of the day: {topic} is a game changer. Excited to share more updates soon! #Learning #Growth",
            f"Exploring {topic} today. The possibilities are endless! What are your thoughts? #Developer #AI",
            f"{topic} is fascinating! The potential for innovation is incredible. #Technology #Future",
            f"Delving deep into {topic} lately. The insights are remarkable! #Innovation #Tech"
        ]

        return random.choice(templates)

    def _generate_static_email_reply(self, greetings_list, openers_list, solutions_list, closings_list, signatures_list, intent):
        """
        Generate an email reply using static templates (fallback method).

        Args:
            greetings_list (list): List of greeting options
            openers_list (list): List of opener options
            solutions_list (list): List of solution options
            closings_list (list): List of closing options
            signatures_list (list): List of signature options
            intent (str): The intent of the reply

        Returns:
            str: Generated email body
        """
        # Select random elements from each list
        greeting = random.choice(greetings_list)
        opener = random.choice(openers_list)
        solution = random.choice(solutions_list)
        closing = random.choice(closings_list)
        signature = random.choice(signatures_list)

        # Create dynamic email body based on intent with context awareness
        if intent == "SOCIAL":
            # For social emails, use a simpler format to avoid repetitive content
            email_body = f"""{greeting}

{opener}

{closing}

{signature}"""
        else:
            email_body = f"""{greeting}

{opener}

{solution}

{closing}

{signature}"""
        
        return email_body

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
                try:
                    if move_file(task_file, dest_path):
                        self.logger.info(f"Moved task file from Needs_Action to Done: {task_file.name}")
                    else:
                        self.logger.warning(f"Failed to move task file: {task_file.name}")
                except PermissionError as e:
                    self.logger.warning(f"PermissionError moving task file {task_file.name}: {e}. Skipping this cycle.")
                except Exception as e:
                    self.logger.error(f"Unexpected error moving task file {task_file.name}: {e}")

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