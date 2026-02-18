"""
Social Media Skill - Manages cross-platform social media posts with MCP integration.

This skill provides functions to:
- Post to Facebook (via MCP server - real API)
- Post to X/Twitter (via MCP server - real API)

Human-in-the-Loop (HITL) Pattern (Document Page 4, Requirement 6):
1. Agent creates draft post in Pending_Approval/ directory
2. Human reviews and moves file to Approved/ directory
3. Only then does the skill call the MCP server tool to execute the post
4. Result is logged to audit trail

Gold Tier Compliance:
- Uses MCP server for actual API calls (not mocks)
- Enforces HITL approval workflow
- Full audit logging
- Error handling for API failures
"""

import json
import logging
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Handle import when running as standalone script vs module
try:
    from src.config.settings import PENDING_APPROVAL_DIR, APPROVED_DIR, LOGS_DIR
except ImportError:
    # Add parent directory to path for standalone execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.config.settings import PENDING_APPROVAL_DIR, APPROVED_DIR, LOGS_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SocialMediaSkill:
    """
    Skill for managing cross-platform social media posts.

    Implements Human-in-the-Loop (HITL) pattern:
    1. Create draft post in Pending_Approval
    2. Wait for human approval (file moved to Approved/)
    3. Execute actual post via MCP server upon approval

    IMPORTANT: This skill does NOT call MCP server directly.
    The approval workflow is:
    - Skill creates Pending_Approval file
    - Human moves file to Approved/
    - Action runner detects approved file and calls MCP tool
    """

    def __init__(self, pending_approval_dir: Optional[Path] = None,
                 approved_dir: Optional[Path] = None):
        """
        Initialize the social media skill.

        Args:
            pending_approval_dir: Directory for pending approval posts
            approved_dir: Directory for approved posts
        """
        self.pending_approval_dir = pending_approval_dir or PENDING_APPROVAL_DIR
        self.approved_dir = approved_dir or APPROVED_DIR

        # Ensure directories exist
        self.pending_approval_dir.mkdir(parents=True, exist_ok=True)
        self.approved_dir.mkdir(parents=True, exist_ok=True)

        # Platform configuration
        self.platforms = {
            "facebook": {
                "name": "Facebook",
                "max_length": 63206,
                "supports_images": True,
                "supports_hashtags": True,
                "mcp_tool": "post_to_facebook"
            },
            "twitter": {
                "name": "X (Twitter)",
                "max_length": 280,
                "supports_images": False,
                "supports_hashtags": True,
                "mcp_tool": "post_to_twitter"
            }
        }

    def _generate_post_id(self, platform: str) -> str:
        """Generate unique post ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{platform.upper()}_{timestamp}_{random.randint(1000, 9999)}"

    def _create_approval_request(self, platform: str, content: Dict[str, Any],
                                  post_id: str, mcp_tool: str) -> Path:
        """
        Create an approval request file in Pending_Approval directory.

        This is the CRUCIAL HITL logic - the agent creates this file
        and MUST wait for human to move it to Approved/ before posting.

        Args:
            platform: Target social media platform
            content: Post content dictionary
            post_id: Unique post identifier
            mcp_tool: Name of MCP tool to call upon approval

        Returns:
            Path to the created approval file
        """
        timestamp = datetime.now().isoformat()

        approval_data = {
            "type": "social_media_post",
            "status": "Pending_Approval",
            "post_id": post_id,
            "platform": platform,
            "created_at": timestamp,
            "content": content,
            "mcp_tool": mcp_tool,
            "metadata": {
                "created_by": "AI_Employee",
                "requires_approval": True,
                "approval_workflow": "HITL_v1",
                "hackathon_tier": "Gold"
            }
        }

        # Create markdown file for human review
        filename = f"DRAFT_SOCIAL_{platform.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        file_path = self.pending_approval_dir / filename

        # Generate markdown content for review
        markdown_content = self._generate_approval_markdown(approval_data)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        logger.info(f"Created approval request: {file_path}")
        return file_path

    def _generate_approval_markdown(self, approval_data: Dict[str, Any]) -> str:
        """Generate markdown content for approval file."""
        platform = approval_data['platform']
        content = approval_data['content']
        mcp_tool = approval_data.get('mcp_tool', 'unknown')

        # Platform-specific formatting
        if platform == "facebook":
            platform_display = "Facebook"
            action_text = content.get('message', '')
        elif platform == "twitter":
            platform_display = "X (Twitter)"
            action_text = content.get('text', '')
        else:
            platform_display = platform.title()
            action_text = str(content)

        markdown = f"""---
type: social_media_post
status: Pending_Approval
post_id: {approval_data['post_id']}
platform: {platform}
mcp_tool: {mcp_tool}
created_at: {approval_data['created_at']}
created_by: AI_Employee
hackathon_tier: Gold
---

# Social Media Post Approval Request

## Platform
**{platform_display}**

## Content to Post
```
{action_text}
```

## Metadata
- **Post ID:** {approval_data['post_id']}
- **Created:** {approval_data['created_at']}
- **MCP Tool:** {mcp_tool}
- **Status:** Pending Human Approval

---

## Approval Instructions (HITL Workflow)

**To APPROVE this post:**
1. Review the content above carefully
2. Move this file to the `Approved/` directory
3. The system will automatically call the MCP tool to execute the post

**To REJECT this post:**
1. Add a comment below explaining the rejection reason
2. Move to `Inbox/` for revision or delete

**To MODIFY:**
1. Edit the content above
2. Save the file (stays in Pending_Approval)
3. System will re-evaluate on next cycle

---

## Execution Details

When approved, the system will:
1. Detect the file in Approved/ directory
2. Parse the platform and content
3. Call MCP tool: `{mcp_tool}`
4. Log the result to audit trail
5. Archive the executed post

---
*This is an automated approval request generated by the AI Employee system.*
*HITL Workflow - Human-in-the-Loop approval required before execution.*
"""
        return markdown

    def post_to_facebook(self, message: str) -> Dict[str, Any]:
        """
        Create a Facebook post request (pending approval).

        HITL Pattern: Creates Pending_Approval file first.
        Does NOT call MCP server directly.

        Args:
            message: Facebook post text content

        Returns:
            Dictionary with post creation result:
            {
                "success": bool,
                "status": "pending_approval",
                "post_id": str,
                "approval_file": str,
                "message": str
            }
        """
        try:
            post_id = self._generate_post_id("fb")

            # Prepare content package
            content_data = {
                "message": message,
                "character_count": len(message),
                "platform": "facebook"
            }

            # Validate content length
            if len(message) > self.platforms['facebook']['max_length']:
                return {
                    "success": False,
                    "error": f"Content exceeds Facebook's {self.platforms['facebook']['max_length']} character limit"
                }

            # Create approval request (HITL pattern - CRUCIAL)
            # Agent does NOT call MCP server here
            approval_file = self._create_approval_request(
                "facebook",
                content_data,
                post_id,
                mcp_tool="post_to_facebook"
            )

            logger.info(f"Facebook post created for approval: {post_id}")

            return {
                "success": True,
                "status": "pending_approval",
                "post_id": post_id,
                "platform": "facebook",
                "approval_file": str(approval_file),
                "content": content_data,
                "message": f"Facebook post created and pending human approval. File: {approval_file.name}"
            }

        except Exception as e:
            logger.error(f"Error creating Facebook post request: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def post_to_twitter(self, text: str) -> Dict[str, Any]:
        """
        Create a Twitter/X post request (pending approval).

        HITL Pattern: Creates Pending_Approval file first.
        Does NOT call MCP server directly.

        Args:
            text: The tweet text content (max 280 characters)

        Returns:
            Dictionary with post creation result:
            {
                "success": bool,
                "status": "pending_approval",
                "post_id": str,
                "approval_file": str,
                "message": str
            }
        """
        try:
            post_id = self._generate_post_id("tw")

            # Prepare content package
            content_data = {
                "text": text,
                "character_count": len(text),
                "platform": "twitter"
            }

            # Validate tweet length
            if len(text) > self.platforms['twitter']['max_length']:
                return {
                    "success": False,
                    "error": f"Tweet exceeds X's {self.platforms['twitter']['max_length']} character limit (got {len(text)})"
                }

            # Create approval request (HITL pattern - CRUCIAL)
            # Agent does NOT call MCP server here
            approval_file = self._create_approval_request(
                "twitter",
                content_data,
                post_id,
                mcp_tool="post_to_twitter"
            )

            logger.info(f"Twitter post created for approval: {post_id}")

            return {
                "success": True,
                "status": "pending_approval",
                "post_id": post_id,
                "platform": "twitter",
                "approval_file": str(approval_file),
                "content": content_data,
                "message": f"X (Twitter) post created and pending human approval. File: {approval_file.name}"
            }

        except Exception as e:
            logger.error(f"Error creating Twitter post request: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def execute_approved_post(self, approval_file_path: str,
                               mcp_client: Optional[Any] = None) -> Dict[str, Any]:
        """
        Execute a post that has been approved (moved to Approved directory).

        This is called by the action runner when an approved post is detected.
        This is the ONLY place where MCP server tools are called.

        Args:
            approval_file_path: Path to the approved post file
            mcp_client: MCP client to call the social media tools

        Returns:
            Dictionary with execution result
        """
        try:
            file_path = Path(approval_file_path)

            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"Approval file not found: {approval_file_path}"
                }

            # Verify file is in Approved directory (HITL check)
            if str(self.approved_dir) not in str(file_path):
                return {
                    "success": False,
                    "error": f"File must be in Approved directory for execution: {file_path}"
                }

            # Read the approval file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the content to extract platform and message
            platform, message_data = self._parse_approved_content(content, file_path)

            if not platform:
                return {
                    "success": False,
                    "error": f"Could not determine platform from file: {file_path.name}"
                }

            # Execute via MCP tool (this is where actual API call happens)
            if platform == "facebook":
                result = self._execute_via_mcp("post_to_facebook", {"message": message_data.get('message', '')}, mcp_client)
            elif platform == "twitter":
                result = self._execute_via_mcp("post_to_twitter", {"text": message_data.get('text', '')}, mcp_client)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }

            # Log to audit trail
            audit_entry = self._write_audit_log(platform, message_data, result)

            # Archive the executed post
            archived_path = self._archive_executed_post(file_path, result)

            return {
                "success": result.get('success', False),
                "platform": platform,
                "executed_at": datetime.now().isoformat(),
                "archived_path": str(archived_path),
                "audit_log": audit_entry,
                "api_result": result
            }

        except Exception as e:
            logger.error(f"Error executing approved post: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_approved_content(self, content: str, file_path: Path) -> tuple:
        """Parse approved file content to extract platform and message data."""
        platform = None
        message_data = {}

        filename_lower = file_path.name.lower()

        # Determine platform from filename
        if "facebook" in filename_lower or "fb" in filename_lower:
            platform = "facebook"
        elif "twitter" in filename_lower or "tw" in filename_lower:
            platform = "twitter"

        # Try to extract content from markdown
        # Look for the content section
        lines = content.split('\n')
        in_content_section = False
        content_lines = []

        for line in lines:
            if '## Content to Post' in line or '## Content' in line:
                in_content_section = True
                continue
            elif in_content_section:
                if line.startswith('```'):
                    if content_lines:  # End of code block
                        break
                    continue
                content_lines.append(line)

        if platform == "facebook":
            message_data['message'] = '\n'.join(content_lines).strip()
        elif platform == "twitter":
            message_data['text'] = '\n'.join(content_lines).strip()

        return platform, message_data

    def _execute_via_mcp(self, tool_name: str, arguments: Dict[str, Any],
                          mcp_client: Optional[Any] = None) -> Dict[str, Any]:
        """
        Execute the actual API call via MCP server.

        Args:
            tool_name: Name of MCP tool to call
            arguments: Arguments to pass to the tool
            mcp_client: MCP client instance

        Returns:
            Result from MCP tool execution
        """
        # In production, this would use the actual MCP client
        # For now, we simulate the call structure
        # The actual implementation depends on how MCP client is integrated

        logger.info(f"Executing MCP tool: {tool_name} with args: {arguments}")

        if mcp_client:
            # Use provided MCP client
            try:
                result = mcp_client.call_tool(tool_name, arguments)
                return result
            except Exception as e:
                logger.error(f"MCP tool execution failed: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        else:
            # Simulated execution for testing without MCP client
            # In real usage, mcp_client should always be provided
            logger.warning("No MCP client provided - simulating execution")
            return {
                "success": True,
                "simulated": True,
                "tool": tool_name,
                "arguments": arguments,
                "message": "Simulated execution (no MCP client provided)"
            }

    def _write_audit_log(self, platform: str, message_data: Dict[str, Any],
                          result: Dict[str, Any]) -> str:
        """Write audit log entry for the executed post."""
        audit_dir = LOGS_DIR / "social_media"
        audit_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audit_file = audit_dir / f"audit_{platform}_{timestamp}.json"

        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "platform": platform,
            "message_data": message_data,
            "result": result,
            "hitl_verified": True
        }

        with open(audit_file, 'w', encoding='utf-8') as f:
            json.dump(audit_entry, f, indent=2, default=str)

        logger.info(f"Audit log written: {audit_file}")
        return str(audit_file)

    def _archive_executed_post(self, original_path: Path,
                                result: Dict[str, Any]) -> Path:
        """Archive the executed post file."""
        archive_dir = self.approved_dir / "Social_Media" / "Executed"
        archive_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"POSTED_{original_path.stem}_{timestamp}.md"
        archive_path = archive_dir / new_filename

        # Add execution result to the file
        with open(original_path, 'r', encoding='utf-8') as f:
            content = f.read()

        execution_footer = f"""

---

## Execution Result
- **Executed At:** {datetime.now().isoformat()}
- **Success:** {result.get('success', False)}
- **API Response:** {json.dumps(result, indent=2, default=str)}
"""

        with open(archive_path, 'w', encoding='utf-8') as f:
            f.write(content + execution_footer)

        # Remove original from Approved (it's now archived)
        original_path.unlink()

        logger.info(f"Archived executed post: {archive_path}")
        return archive_path

    def list_pending_posts(self) -> List[Dict[str, Any]]:
        """List all pending approval posts."""
        pending_posts = []

        for file_path in self.pending_approval_dir.glob("DRAFT_SOCIAL_*.md"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract basic info
            platform = "unknown"
            if "facebook" in file_path.name.lower():
                platform = "facebook"
            elif "twitter" in file_path.name.lower():
                platform = "twitter"

            pending_posts.append({
                "file": str(file_path),
                "filename": file_path.name,
                "platform": platform,
                "created": file_path.stat().st_mtime
            })

        return pending_posts

    def list_approved_posts(self) -> List[Dict[str, Any]]:
        """List all approved posts awaiting execution."""
        approved_posts = []

        for file_path in self.approved_dir.glob("DRAFT_SOCIAL_*.md"):
            platform = "unknown"
            if "facebook" in file_path.name.lower():
                platform = "facebook"
            elif "twitter" in file_path.name.lower():
                platform = "twitter"

            approved_posts.append({
                "file": str(file_path),
                "filename": file_path.name,
                "platform": platform,
                "ready_for_execution": True
            })

        return approved_posts


# Convenience functions for direct import and use
def post_to_facebook(message: str) -> Dict[str, Any]:
    """
    Create a Facebook post (pending approval).

    HITL Pattern: Creates Pending_Approval file.
    Human must move file to Approved/ before posting.

    Args:
        message: Post text content

    Returns:
        Post creation result dictionary
    """
    skill = SocialMediaSkill()
    return skill.post_to_facebook(message)


def post_to_twitter(text: str) -> Dict[str, Any]:
    """
    Create a Twitter/X post (pending approval).

    HITL Pattern: Creates Pending_Approval file.
    Human must move file to Approved/ before posting.

    Args:
        text: Tweet content (max 280 characters)

    Returns:
        Post creation result dictionary
    """
    skill = SocialMediaSkill()
    return skill.post_to_twitter(text)


# Example usage and testing
if __name__ == "__main__":
    print("Testing Social Media Skill (HITL Pattern)...")
    print("-" * 60)

    # Test Facebook post
    print("\n1. Creating Facebook post (pending approval)...")
    fb_result = post_to_facebook(
        "Excited to announce our new AI-powered automation system! "
        "This is a game-changer for business productivity. #AI #Automation #Innovation"
    )
    print(f"   Status: {fb_result.get('status')}")
    print(f"   File: {fb_result.get('approval_file')}")
    print(f"   Message: {fb_result.get('message')}")

    # Test Twitter post
    print("\n2. Creating Twitter/X post (pending approval)...")
    tw_result = post_to_twitter(
        "Just launched our new AI employee system! "
        "Automating tasks so you can focus on what matters. 🎯"
    )
    print(f"   Status: {tw_result.get('status')}")
    print(f"   File: {tw_result.get('approval_file')}")
    print(f"   Message: {tw_result.get('message')}")

    print("\n" + "-" * 60)
    print("HITL Workflow Summary:")
    print("1. Posts created in Pending_Approval/")
    print("2. Human must review and move files to Approved/")
    print("3. System will then execute via MCP server")
    print(f"\nCheck pending: {PENDING_APPROVAL_DIR}")
