# Data Model: Gmail Reasoning Loop

## Entities

### EmailEntity
Represents an email message from Gmail

**Fields**:
- `id`: str (Gmail message ID, unique identifier from Gmail API)
- `thread_id`: str (Gmail thread ID)
- `subject`: str (email subject line)
- `sender`: str (email address of sender)
- `recipients`: List[str] (list of recipient email addresses)
- `body`: str (email body content, plain text or HTML)
- `body_markdown`: str (email body converted to Markdown format)
- `labels`: List[str] (list of Gmail labels applied to the email)
- `timestamp`: datetime (time the email was received)
- `received_time`: datetime (time the email was received by the system)
- `is_read`: bool (whether the email has been marked as read)
- `size_estimate`: int (approximate size of the email in bytes)
- `urgency_level`: Enum('URGENT', 'IMPORTANT', 'NORMAL') (classification of email importance)

**Relationships**:
- One-to-many with TaskEntity (an email can generate multiple tasks)

### TaskEntity
Represents a work item that needs processing, derived from an email

**Fields**:
- `id`: str (generated UUID, unique identifier for the task)
- `source_email_id`: str (reference to EmailEntity.id)
- `title`: str (derived from email subject)
- `content`: str (Markdown content of the task, converted from email)
- `created_at`: datetime (time the task was created)
- `updated_at`: datetime (time the task was last updated)
- `status`: Enum('NEW', 'PLANNED', 'APPROVED', 'IN_PROGRESS', 'COMPLETED', 'FAILED')
- `assigned_to`: str (optional, who the task is assigned to)
- `due_date`: Optional[datetime] (optional deadline for the task)
- `priority`: Enum('HIGH', 'MEDIUM', 'LOW')

**Relationships**:
- Many-to-one with EmailEntity (many tasks can come from one email)
- One-to-one with PlanEntity (each task has one associated plan)

### PlanEntity
Represents the reasoning and action plan created for a task

**Fields**:
- `id`: str (generated UUID, unique identifier for the plan)
- `task_id`: str (reference to TaskEntity.id)
- `title`: str (title of the plan, usually derived from task)
- `description`: str (detailed description of the plan)
- `steps`: List[Dict] (list of steps with id, description, and completion status)
- `created_at`: datetime (time the plan was created)
- `updated_at`: datetime (time the plan was last updated)
- `status`: Enum('DRAFT', 'REVIEW', 'APPROVED', 'EXECUTING', 'COMPLETED', 'CANCELLED')
- `estimated_duration`: Optional[int] (estimated time in minutes to complete)

**Relationships**:
- Many-to-one with TaskEntity (many plans can be associated with one task - though typically 1:1)
- One-to-many with ApprovalEntity (a plan may require multiple approvals)

### ApprovalEntity
Represents a request for human approval before executing an action

**Fields**:
- `id`: str (generated UUID, unique identifier for the approval request)
- `request_type`: Enum('EMAIL_SEND', 'FILE_MODIFY', 'DATA_ACCESS', 'OTHER') (type of action requiring approval)
- `request_details`: Dict (details about the action requiring approval)
- `target_resource`: str (the resource that will be affected)
- `created_at`: datetime (time the approval request was created)
- `requested_by`: str (who requested the action)
- `status`: Enum('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED')
- `approved_by`: Optional[str] (who approved the action, if applicable)
- `approved_at`: Optional[datetime] (when the action was approved, if applicable)
- `rejection_reason`: Optional[str] (reason for rejection, if applicable)

**Relationships**:
- Many-to-one with PlanEntity (many approvals can be associated with one plan)

### FileEntity
Represents a file in the system's directory structure

**Fields**:
- `id`: str (generated UUID)
- `filename`: str (name of the file)
- `filepath`: str (full path to the file)
- `relative_path`: str (path relative to vault root)
- `size_bytes`: int (size of the file in bytes)
- `created_at`: datetime (time the file was created)
- `modified_at`: datetime (time the file was last modified)
- `checksum`: str (SHA-256 hash of the file content)
- `status`: Enum('ACTIVE', 'MOVED', 'DELETED', 'ARCHIVED')
- `original_location`: Optional[str] (where the file originated from)

**Relationships**:
- One-to-one with EmailEntity (when the file represents an email)
- One-to-one with TaskEntity (when the file represents a task)
- One-to-one with PlanEntity (when the file represents a plan)

## State Transitions

### Task Status Transitions
```
NEW → PLANNED → APPROVED → IN_PROGRESS → COMPLETED
         ↓                              ↗
      IN_PROGRESS ←—————— COMPLETED ←———
         ↓
      FAILED → NEW (retry)
```

### Plan Status Transitions
```
DRAFT → REVIEW → APPROVED → EXECUTING → COMPLETED
                    ↓              ↗
                 CANCELLED ←——————
```

### Approval Status Transitions
```
PENDING → APPROVED
    ↓
 REJECTED (with reason)
    ↑
PENDING (if resubmitted)
```

## Validation Rules

### EmailEntity
- `id` must be non-empty string
- `timestamp` must be a valid datetime
- `urgency_level` must be one of the defined enum values
- `body` and `body_markdown` must not exceed 1MB in length

### TaskEntity
- `id` must be a valid UUID
- `status` must be one of the defined enum values
- `priority` must be one of the defined enum values
- `source_email_id` must reference an existing EmailEntity

### PlanEntity
- `id` must be a valid UUID
- `status` must be one of the defined enum values
- `steps` must be a list of dictionaries with required fields
- `task_id` must reference an existing TaskEntity

### ApprovalEntity
- `id` must be a valid UUID
- `status` must be one of the defined enum values
- `request_type` must be one of the defined enum values
- `request_details` must be a non-empty dictionary

## Indexes

For performance optimization:
- EmailEntity: index on `id`, `timestamp`, `is_read`, `urgency_level`
- TaskEntity: index on `id`, `source_email_id`, `status`, `created_at`
- PlanEntity: index on `id`, `task_id`, `status`, `created_at`
- ApprovalEntity: index on `id`, `status`, `created_at`
- FileEntity: index on `id`, `filepath`, `status`