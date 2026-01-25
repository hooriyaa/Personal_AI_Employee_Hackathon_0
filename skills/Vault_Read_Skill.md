# Vault Read Skill

## Purpose
Read markdown files from the Obsidian vault for processing and analysis.

## Inputs
- `file_path`: String path to the markdown file relative to the vault root
- `vault_root`: String path to the Obsidian vault directory

## Outputs
- `content`: String content of the markdown file
- `success`: Boolean indicating if the read operation was successful
- `error_message`: String error message if operation failed

## Preconditions
- The vault root directory must exist and be accessible
- The file path must point to an existing markdown file
- The file must be readable by the current process

## Safety Rules
- Only read files within the designated vault directory
- Validate file paths to prevent directory traversal attacks
- Do not read files larger than 10MB to prevent memory issues
- Do not expose file system structure outside the vault

## Files/Folders Used
- Obsidian vault directory and subdirectories
- Markdown files (.md extension) within the vault

## Example Invocation (Claude Code style)
```
<action skill="Vault_Read_Skill">
{
  "file_path": "Projects/New_Idea.md",
  "vault_root": "/Users/username/Obsidian_Vault"
}
</action>
```