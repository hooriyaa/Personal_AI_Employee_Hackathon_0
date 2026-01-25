# File State Transition Skill

## Purpose
Move files between workflow states: /Needs_Action → /Plans → /Pending_Approval → /Done.

## Inputs
- `source_path`: String path of the source file/directory
- `destination_path`: String path of the destination file/directory
- `transition_reason`: String explaining the reason for the transition
- `vault_root`: String path to the Obsidian vault directory
- `preserve_original`: Boolean indicating if the original should be preserved (for logging purposes)

## Outputs
- `success`: Boolean indicating if the transition was successful
- `original_path`: String path of the original file
- `new_path`: String path of the file after transition
- `error_message`: String error message if operation failed
- `transition_log`: String record of the transition for audit purposes

## Preconditions
- The source file must exist and be accessible
- The destination directory must exist and be writable
- The transition must follow the allowed workflow path
- The vault root directory must be accessible

## Safety Rules
- Only allow transitions between predefined workflow states
- Validate that the transition follows the correct sequence
- Create backup before moving files
- Update any references to the file in other documents
- Maintain atomicity - either complete the transition or revert to original state

## Files/Folders Used
- /Needs_Action directory
- /Plans directory
- /Pending_Approval directory
- /Done directory
- Source and destination files during transition

## Example Invocation (Claude Code style)
```
<action skill="File_State_Transition_Skill">
{
  "source_path": "Needs_Action/Urgent_Task_Request.md",
  "destination_path": "Plans/Urgent_Task_Plan.md",
  "transition_reason": "Task analyzed and plan created",
  "vault_root": "/Users/username/Obsidian_Vault",
  "preserve_original": false
}
</action>
```