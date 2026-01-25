"""
Data models for the Gmail Reasoning Loop application.

This module defines the core data structures used throughout the application,
including entities for emails, tasks, plans, and approvals.
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import uuid


class UrgencyLevel(Enum):
    """Enumeration for email urgency levels."""
    URGENT = "URGENT"
    IMPORTANT = "IMPORTANT"
    NORMAL = "NORMAL"


class TaskStatus(Enum):
    """Enumeration for task statuses."""
    NEW = "NEW"
    PLANNED = "PLANNED"
    APPROVED = "APPROVED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PlanStatus(Enum):
    """Enumeration for plan statuses."""
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ApprovalStatus(Enum):
    """Enumeration for approval statuses."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class RequestType(Enum):
    """Enumeration for approval request types."""
    EMAIL_SEND = "EMAIL_SEND"
    FILE_MODIFY = "FILE_MODIFY"
    DATA_ACCESS = "DATA_ACCESS"
    OTHER = "OTHER"


@dataclass
class EmailEntity:
    """
    Represents an email message from Gmail.
    
    Attributes:
        id (str): Gmail message ID (unique identifier from Gmail API)
        thread_id (str): Gmail thread ID
        subject (str): Email subject line
        sender (str): Email address of sender
        recipients (List[str]): List of recipient email addresses
        body (str): Email body content (plain text or HTML)
        body_markdown (str): Email body converted to Markdown format
        labels (List[str]): List of Gmail labels applied to the email
        timestamp (datetime): Time the email was received
        received_time (datetime): Time the email was received by the system
        is_read (bool): Whether the email has been marked as read
        size_estimate (int): Approximate size of the email in bytes
        urgency_level (UrgencyLevel): Classification of email importance
    """
    id: str
    thread_id: str
    subject: str
    sender: str
    recipients: List[str]
    body: str
    body_markdown: str
    labels: List[str]
    timestamp: datetime
    received_time: datetime = field(default_factory=datetime.now)
    is_read: bool = False
    size_estimate: int = 0
    urgency_level: UrgencyLevel = UrgencyLevel.NORMAL
    
    def __post_init__(self):
        """Validate the email entity after initialization."""
        if not self.id:
            raise ValueError("Email ID cannot be empty")
        if not self.timestamp:
            raise ValueError("Timestamp cannot be empty")
        if self.urgency_level not in UrgencyLevel:
            raise ValueError(f"Invalid urgency level: {self.urgency_level}")


@dataclass
class TaskEntity:
    """
    Represents a work item that needs processing, derived from an email.
    
    Attributes:
        id (str): Generated UUID, unique identifier for the task
        source_email_id (str): Reference to EmailEntity.id
        title (str): Derived from email subject
        content (str): Markdown content of the task, converted from email
        created_at (datetime): Time the task was created
        updated_at (datetime): Time the task was last updated
        status (TaskStatus): Current status of the task
        assigned_to (str): Optional, who the task is assigned to
        due_date (Optional[datetime]): Optional deadline for the task
        priority (str): Priority level ('HIGH', 'MEDIUM', 'LOW')
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_email_id: str = ""
    title: str = ""
    content: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: TaskStatus = TaskStatus.NEW
    assigned_to: str = ""
    due_date: Optional[datetime] = None
    priority: str = "MEDIUM"
    
    def __post_init__(self):
        """Validate the task entity after initialization."""
        if self.status not in TaskStatus:
            raise ValueError(f"Invalid task status: {self.status}")
        if self.priority not in ["HIGH", "MEDIUM", "LOW"]:
            raise ValueError(f"Invalid priority level: {self.priority}")


@dataclass
class PlanStep:
    """
    Represents a single step in a plan.
    
    Attributes:
        id (str): Unique identifier for the step
        description (str): Description of the step
        completed (bool): Whether the step is completed
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    completed: bool = False


@dataclass
class PlanEntity:
    """
    Represents the reasoning and action plan created for a task.
    
    Attributes:
        id (str): Generated UUID, unique identifier for the plan
        task_id (str): Reference to TaskEntity.id
        title (str): Title of the plan, usually derived from task
        description (str): Detailed description of the plan
        steps (List[PlanStep]): List of steps with id, description, and completion status
        created_at (datetime): Time the plan was created
        updated_at (datetime): Time the plan was last updated
        status (PlanStatus): Current status of the plan
        estimated_duration (Optional[int]): Estimated time in minutes to complete
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    title: str = ""
    description: str = ""
    steps: List[PlanStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: PlanStatus = PlanStatus.DRAFT
    estimated_duration: Optional[int] = None
    
    def __post_init__(self):
        """Validate the plan entity after initialization."""
        if self.status not in PlanStatus:
            raise ValueError(f"Invalid plan status: {self.status}")


@dataclass
class ApprovalEntity:
    """
    Represents a request for human approval before executing an action.
    
    Attributes:
        id (str): Generated UUID, unique identifier for the approval request
        request_type (RequestType): Type of action requiring approval
        request_details (Dict): Details about the action requiring approval
        target_resource (str): The resource that will be affected
        created_at (datetime): Time the approval request was created
        requested_by (str): Who requested the action
        status (ApprovalStatus): Current status of the approval
        approved_by (Optional[str]): Who approved the action, if applicable
        approved_at (Optional[datetime]): When the action was approved, if applicable
        rejection_reason (Optional[str]): Reason for rejection, if applicable
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_type: RequestType = RequestType.OTHER
    request_details: Dict = field(default_factory=dict)
    target_resource: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    requested_by: str = ""
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    def __post_init__(self):
        """Validate the approval entity after initialization."""
        if self.request_type not in RequestType:
            raise ValueError(f"Invalid request type: {self.request_type}")
        if self.status not in ApprovalStatus:
            raise ValueError(f"Invalid approval status: {self.status}")


@dataclass
class FileEntity:
    """
    Represents a file in the system's directory structure.
    
    Attributes:
        id (str): Generated UUID
        filename (str): Name of the file
        filepath (str): Full path to the file
        relative_path (str): Path relative to vault root
        size_bytes (int): Size of the file in bytes
        created_at (datetime): Time the file was created
        modified_at (datetime): Time the file was last modified
        checksum (str): SHA-256 hash of the file content
        status (str): Current status ('ACTIVE', 'MOVED', 'DELETED', 'ARCHIVED')
        original_location (Optional[str]): Where the file originated from
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    filepath: str = ""
    relative_path: str = ""
    size_bytes: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    checksum: str = ""
    status: str = "ACTIVE"
    original_location: Optional[str] = None
    
    def __post_init__(self):
        """Validate the file entity after initialization."""
        if self.status not in ["ACTIVE", "MOVED", "DELETED", "ARCHIVED"]:
            raise ValueError(f"Invalid file status: {self.status}")


# Helper functions for creating entities
def create_email_entity_from_gmail_message(gmail_message: dict) -> EmailEntity:
    """
    Create an EmailEntity from a Gmail API message object.
    
    Args:
        gmail_message (dict): Gmail API message object
        
    Returns:
        EmailEntity: Created email entity
    """
    headers = {h['name'].lower(): h['value'] for h in gmail_message.get('payload', {}).get('headers', [])}
    
    # Determine urgency level based on labels
    labels = gmail_message.get('labelIds', [])
    urgency_level = UrgencyLevel.NORMAL
    if 'URGENT' in labels or 'urgent' in labels:
        urgency_level = UrgencyLevel.URGENT
    elif 'IMPORTANT' in labels or 'important' in labels:
        urgency_level = UrgencyLevel.IMPORTANT
    
    return EmailEntity(
        id=gmail_message['id'],
        thread_id=gmail_message['threadId'],
        subject=headers.get('subject', 'No Subject'),
        sender=headers.get('from', 'Unknown Sender'),
        recipients=[r.strip() for r in headers.get('to', '').split(',')] if headers.get('to') else [],
        body=gmail_message.get('snippet', ''),
        body_markdown="",  # Will be populated later
        labels=labels,
        timestamp=datetime.fromtimestamp(int(gmail_message.get('internalDate', 0)) / 1000),
        is_read='UNREAD' not in gmail_message.get('labelIds', []),
        size_estimate=gmail_message.get('sizeEstimate', 0),
        urgency_level=urgency_level
    )


def create_task_entity_from_email(email_entity: EmailEntity) -> TaskEntity:
    """
    Create a TaskEntity from an EmailEntity.
    
    Args:
        email_entity (EmailEntity): Source email entity
        
    Returns:
        TaskEntity: Created task entity
    """
    return TaskEntity(
        source_email_id=email_entity.id,
        title=email_entity.subject,
        content=email_entity.body_markdown or email_entity.body,
        priority="HIGH" if email_entity.urgency_level == UrgencyLevel.URGENT else 
                "MEDIUM" if email_entity.urgency_level == UrgencyLevel.IMPORTANT else "LOW"
    )


# Example usage
if __name__ == "__main__":
    # Example of creating entities
    print("Data models loaded successfully.")
    
    # Create a sample email entity
    sample_email = EmailEntity(
        id=str(uuid.uuid4()),
        thread_id="thread123",
        subject="Test Email",
        sender="sender@example.com",
        recipients=["recipient@example.com"],
        body="This is a test email body.",
        body_markdown="# Test Email\n\nThis is a test email body.",
        labels=["INBOX", "IMPORTANT"],
        timestamp=datetime.now(),
        urgency_level=UrgencyLevel.IMPORTANT
    )
    
    print(f"Created sample email: {sample_email.subject}")
    print(f"Urgency level: {sample_email.urgency_level.value}")
    
    # Create a sample task from the email
    sample_task = create_task_entity_from_email(sample_email)
    print(f"Created sample task: {sample_task.title}")
    print(f"Task priority: {sample_task.priority}")