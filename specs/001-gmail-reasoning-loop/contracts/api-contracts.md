# API Contracts: Gmail Reasoning Loop

## Gmail Service API

### GET /api/v1/gmail/messages
Retrieve messages from Gmail inbox based on filters

**Query Parameters**:
- `label` (optional): Filter by Gmail label (e.g., "URGENT", "IMPORTANT")
- `unread` (optional): Filter by read status (true/false)
- `max_results` (optional): Maximum number of messages to return (default: 10, max: 100)

**Response**:
```json
{
  "messages": [
    {
      "id": "string",
      "threadId": "string",
      "subject": "string",
      "sender": "string",
      "recipients": ["string"],
      "body": "string",
      "bodyMarkdown": "string",
      "labels": ["string"],
      "timestamp": "ISO 8601 datetime",
      "isRead": true,
      "sizeEstimate": 1234,
      "urgencyLevel": "URGENT|IMPORTANT|NORMAL"
    }
  ],
  "nextPageToken": "string (optional)"
}
```

**Authentication**: OAuth 2.0 (Bearer token)

### POST /api/v1/gmail/messages/{messageId}/mark-read
Mark a message as read in Gmail

**Path Parameters**:
- `messageId`: The ID of the message to mark as read

**Response**:
```json
{
  "success": true,
  "messageId": "string"
}
```

**Authentication**: OAuth 2.0 (Bearer token)

### GET /api/v1/gmail/token-status
Check the validity of the current Gmail API token

**Response**:
```json
{
  "valid": true,
  "expiresAt": "ISO 8601 datetime",
  "scopes": ["string"]
}
```

**Authentication**: OAuth 2.0 (Bearer token)

## File System Service API

### POST /api/v1/filesystem/move
Move a file from source to destination

**Request Body**:
```json
{
  "source": "string (source file path)",
  "destination": "string (destination file path)"
}
```

**Response**:
```json
{
  "success": true,
  "message": "string (confirmation message)",
  "movedFile": {
    "id": "string",
    "filename": "string",
    "sourcePath": "string",
    "destinationPath": "string",
    "sizeBytes": 1234,
    "createdAt": "ISO 8601 datetime"
  }
}
```

### GET /api/v1/filesystem/watch
Monitor a directory for file system events

**Query Parameters**:
- `directory`: The directory to watch
- `recursive` (optional): Whether to watch subdirectories (default: false)

**Response Stream**:
```json
{
  "eventType": "CREATED|MODIFIED|DELETED|MOVED",
  "filePath": "string",
  "timestamp": "ISO 8601 datetime",
  "fileInfo": {
    "filename": "string",
    "sizeBytes": 1234,
    "checksum": "string"
  }
}
```

## Approval Service API

### POST /api/v1/approvals/request
Request approval for an action

**Request Body**:
```json
{
  "requestType": "EMAIL_SEND|FILE_MODIFY|DATA_ACCESS|OTHER",
  "requestDetails": {
    "action": "string (description of the action)",
    "targetResource": "string (resource to be acted upon)",
    "estimatedDuration": "integer (estimated time in minutes)"
  },
  "requestedBy": "string (who is requesting the approval)"
}
```

**Response**:
```json
{
  "approvalId": "string",
  "status": "PENDING",
  "requestType": "EMAIL_SEND|FILE_MODIFY|DATA_ACCESS|OTHER",
  "requestedBy": "string",
  "createdAt": "ISO 8601 datetime"
}
```

### POST /api/v1/approvals/{approvalId}/approve
Approve a pending approval request

**Path Parameters**:
- `approvalId`: The ID of the approval request

**Response**:
```json
{
  "success": true,
  "approvalId": "string",
  "status": "APPROVED",
  "approvedBy": "string",
  "approvedAt": "ISO 8601 datetime"
}
```

### GET /api/v1/approvals/pending
Get all pending approval requests

**Response**:
```json
{
  "approvals": [
    {
      "id": "string",
      "requestType": "EMAIL_SEND|FILE_MODIFY|DATA_ACCESS|OTHER",
      "requestDetails": {},
      "requestedBy": "string",
      "createdAt": "ISO 8601 datetime",
      "status": "PENDING"
    }
  ]
}
```

## Plan Service API

### POST /api/v1/plans/generate
Generate a plan for a given task

**Request Body**:
```json
{
  "taskId": "string",
  "taskContent": "string (content of the task to plan for)"
}
```

**Response**:
```json
{
  "planId": "string",
  "taskId": "string",
  "title": "string",
  "description": "string",
  "steps": [
    {
      "id": "string",
      "description": "string",
      "completed": false
    }
  ],
  "createdAt": "ISO 8601 datetime",
  "status": "DRAFT"
}
```

### PUT /api/v1/plans/{planId}/update-step
Update the status of a specific step in a plan

**Path Parameters**:
- `planId`: The ID of the plan

**Request Body**:
```json
{
  "stepId": "string",
  "completed": true
}
```

**Response**:
```json
{
  "success": true,
  "planId": "string",
  "stepId": "string",
  "completed": true
}
```