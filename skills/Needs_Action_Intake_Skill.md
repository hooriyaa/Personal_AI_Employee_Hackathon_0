# Needs_Action Intake Skill

## Purpose
Parse files in the /Needs_Action directory to extract intent, urgency, and domain information.

## Inputs
- `file_path`: String path to the file in /Needs_Action directory
- `vault_root`: String path to the Obsidian vault directory

## Outputs
- `intent`: String describing the main intent/purpose of the task
- `urgency`: Integer from 1-5 indicating urgency level (5 being highest priority)
- `domain`: String identifying the domain or category of the task
- `parsed_content`: Object containing extracted structured information
- `success`: Boolean indicating if the parsing was successful
- `error_message`: String error message if operation failed

## Preconditions
- The file must exist in the /Needs_Action directory
- The file must be a markdown file (.md extension)
- The file content must follow the expected format for intake processing

## Safety Rules
- Only process files from the /Needs_Action directory
- Validate file content format before processing
- Do not modify the original file during parsing
- Respect human-in-the-loop for sensitive or unclear requests

## Files/Folders Used
- /Needs_Action directory within the vault
- Individual markdown files in the /Needs_Action directory

## Example Invocation (Claude Code style)
```
<action skill="Needs_Action_Intake_Skill">
{
  "file_path": "Needs_Action/Urgent_Task_Request.md",
  "vault_root": "/Users/username/Obsidian_Vault"
}
</action>
```