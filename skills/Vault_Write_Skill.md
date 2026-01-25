# Vault Write Skill

## Purpose
Write or update markdown files safely within the Obsidian vault.

## Inputs
- `file_path`: String path to the markdown file relative to the vault root
- `content`: String content to write to the file
- `vault_root`: String path to the Obsidian vault directory
- `overwrite`: Boolean indicating if existing files should be overwritten

## Outputs
- `success`: Boolean indicating if the write operation was successful
- `file_path`: String path of the written file
- `error_message`: String error message if operation failed

## Preconditions
- The vault root directory must exist and be writable
- The file path must be within the vault directory
- The parent directory for the file must exist or be creatable

## Safety Rules
- Only write files within the designated vault directory
- Validate file paths to prevent directory traversal
- Prevent writing files larger than 10MB
- Create backup of existing files before overwriting if `overwrite` is true
- Ensure file content ends with newline character

## Files/Folders Used
- Obsidian vault directory and subdirectories
- Markdown files (.md extension) within the vault
- Backup files for existing content preservation

## Example Invocation (Claude Code style)
```
<action skill="Vault_Write_Skill">
{
  "file_path": "Projects/New_Idea.md",
  "content": "# New Idea\n\nThis is a new project idea...",
  "vault_root": "/Users/username/Obsidian_Vault",
  "overwrite": true
}
</action>
```