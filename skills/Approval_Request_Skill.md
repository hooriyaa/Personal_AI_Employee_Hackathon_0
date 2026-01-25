# Approval Request Skill

## Purpose
Generate approval files for sensitive actions and write them into the /Pending_Approval directory.

## Inputs
- `action_description`: String describing the action requiring approval
- `justification`: String explaining why the action is necessary
- `potential_impacts`: String describing potential impacts of the action
- `vault_root`: String path to the Obsidian vault directory
- `requestor`: String identifier of the entity requesting approval

## Outputs
- `approval_file_path`: String path of the created approval request file
- `success`: Boolean indicating if the approval request was created successfully
- `error_message`: String error message if operation failed
- `request_id`: String identifier for the approval request

## Preconditions
- The /Pending_Approval directory must exist and be writable
- The action must require human approval based on sensitivity criteria
- The vault root directory must be accessible

## Safety Rules
- Only create approval requests for actions meeting sensitivity criteria
- Include sufficient detail for human reviewers to make informed decisions
- Do not proceed with sensitive actions until explicit approval is granted
- Maintain audit trail of all approval requests

## Files/Folders Used
- /Pending_Approval directory within the vault
- Generated approval request files

## Example Invocation (Claude Code style)
```
<action skill="Approval_Request_Skill">
{
  "action_description": "Modify core authentication system",
  "justification": "Security patch requires changes to auth module",
  "potential_impacts": "May temporarily affect login functionality",
  "vault_root": "/Users/username/Obsidian_Vault",
  "requestor": "AI_Employee_Bot"
}
</action>
```