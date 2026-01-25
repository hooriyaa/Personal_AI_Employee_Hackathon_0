# Data Model: Local-First AI Employee (Bronze Tier)

## Entities

### File
- **Attributes**:
  - name (string): The original filename
  - size (integer): Size in bytes
  - timestamp (datetime): When the file was detected/moved
  - original_path (string): The original path in the vault
  - content (binary): The file content
  - status (enum): pending, in-progress, completed

### Task
- **Attributes**:
  - id (string): Unique identifier (based on filename + timestamp)
  - file_ref (reference): Reference to the associated File entity
  - status (enum): pending, in-progress, completed
  - created_at (datetime): When the task was created
  - completed_at (datetime): When the task was completed (nullable)

### MetadataTrigger
- **Attributes**:
  - id (string): Unique identifier
  - filename (string): The name of the original file
  - size (integer): Size of the original file in bytes
  - timestamp (datetime): When the file was detected
  - original_path (string): Path of the original file in the vault
  - created_at (datetime): When the trigger was created

### Dashboard
- **Attributes**:
  - id (string): Unique identifier
  - tasks_summary (object): Summary of tasks by status
  - last_updated (datetime): When the dashboard was last updated
  - content (string): The Markdown content of the dashboard

## Relationships
- A File entity can be associated with one Task entity (1:1 relationship)
- A Task entity is associated with one MetadataTrigger entity (1:1 relationship)
- The Dashboard entity contains references to multiple Task entities (1:many relationship)

## State Transitions

### File Status Transitions
- `pending` → `in-progress` (when picked up for processing)
- `in-progress` → `completed` (when processing is finished)
- `in-progress` → `pending` (if processing fails and needs retry)

### Task Status Transitions
- `pending` → `in-progress` (when agent starts processing)
- `in-progress` → `completed` (when agent finishes processing)
- `in-progress` → `pending` (if processing fails and needs retry)

## Validation Rules
- File names must be unique within the same destination folder
- Timestamps must be in ISO 8601 format
- File sizes must be positive integers
- Status values must be one of the defined enum values
- MetadataTrigger must contain all required fields (filename, size, timestamp, original_path)