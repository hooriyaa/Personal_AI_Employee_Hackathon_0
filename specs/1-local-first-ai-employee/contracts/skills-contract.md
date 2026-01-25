# API Contract: Local-First AI Employee Skills

## Vault Read Skill

### Endpoint: `GET /skills/vault-read`
Read content from the vault at a specified path.

#### Request
```json
{
  "path": "string",
  "file_type": "enum(string, markdown, binary)"
}
```

#### Response
```json
{
  "success": "boolean",
  "content": "string | object",
  "error": "string (optional)"
}
```

## Vault Write Skill

### Endpoint: `POST /skills/vault-write`
Write content to a specified path in the vault.

#### Request
```json
{
  "path": "string",
  "content": "string",
  "mode": "enum(overwrite, append)"
}
```

#### Response
```json
{
  "success": "boolean",
  "message": "string",
  "error": "string (optional)"
}
```

## Task Completion Skill

### Endpoint: `POST /skills/task-completion`
Move a processed file from Needs_Action to Done folder.

#### Request
```json
{
  "source_path": "string",
  "destination_folder": "string (default: './vault/Done/')",
  "preserve_original": "boolean (default: false)"
}
```

#### Response
```json
{
  "success": "boolean",
  "moved_file_path": "string",
  "error": "string (optional)"
}
```

## Filesystem Watcher Service

### Event: `FILE_DETECTED`
Emitted when a new file is detected in the Inbox.

#### Payload
```json
{
  "event_type": "FILE_DETECTED",
  "file_path": "string",
  "file_size": "integer",
  "timestamp": "string (ISO 8601)",
  "status": "string"
}
```

### Event: `FILE_MOVED`
Emitted when a file is successfully moved from Inbox to Needs_Action.

#### Payload
```json
{
  "event_type": "FILE_MOVED",
  "original_path": "string",
  "new_path": "string",
  "timestamp": "string (ISO 8601)"
}
```

### Event: `METADATA_CREATED`
Emitted when a metadata trigger file is created.

#### Payload
```json
{
  "event_type": "METADATA_CREATED",
  "trigger_file_path": "string",
  "associated_file_path": "string",
  "timestamp": "string (ISO 8601)"
}
```