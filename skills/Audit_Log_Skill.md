# Audit Log Skill

## Purpose
Append structured logs to /Logs/YYYY-MM-DD.json for tracking all AI actions.

## Inputs
- `action_type`: String type of action performed by the AI
- `details`: Object containing specific details about the action
- `timestamp`: String timestamp of when the action occurred (ISO 8601 format)
- `success`: Boolean indicating if the action was successful
- `vault_root`: String path to the Obsidian vault directory

## Outputs
- `success`: Boolean indicating if the log entry was successfully added
- `log_file_path`: String path of the log file updated
- `error_message`: String error message if operation failed
- `entry_id`: String identifier for the log entry

## Preconditions
- The /Logs directory must exist and be writable
- The vault root directory must be accessible
- The log file for the current date must be accessible or creatable

## Safety Rules
- Ensure all logged data is sanitized and doesn't contain sensitive information
- Maintain consistent log format for easy parsing and analysis
- Create daily log files in YYYY-MM-DD format
- Handle log file rotation appropriately
- Never allow log operations to fail silently

## Files/Folders Used
- /Logs directory within the vault
- Daily log files in YYYY-MM-DD.json format
- Temporary files during log rotation

## Example Invocation (Claude Code style)
```
<action skill="Audit_Log_Skill">
{
  "action_type": "File_Read",
  "details": {
    "file_path": "Projects/Sensitive_Project.md",
    "skill_used": "Vault_Read_Skill",
    "result": "Success"
  },
  "timestamp": "2026-01-22T10:30:00Z",
  "success": true,
  "vault_root": "/Users/username/Obsidian_Vault"
}
</action>
```