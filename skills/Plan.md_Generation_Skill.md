# Plan.md Generation Skill

## Purpose
Convert tasks into structured Plan.md files using checkboxes and clear objectives.

## Inputs
- `task_description`: String describing the task to be planned
- `target_file_path`: String path where the Plan.md file will be created
- `vault_root`: String path to the Obsidian vault directory
- `related_files`: Array of strings representing related file paths in the vault

## Outputs
- `plan_file_path`: String path of the created Plan.md file
- `success`: Boolean indicating if the plan generation was successful
- `error_message`: String error message if operation failed
- `plan_summary`: String summary of the generated plan

## Preconditions
- The target directory must exist and be writable
- The task description must contain sufficient detail to generate a plan
- The vault root directory must be accessible

## Safety Rules
- Only create files in designated planning directories
- Ensure generated plans follow the required structure with checkboxes
- Validate that all referenced files exist before including them in the plan
- Do not overwrite existing Plan.md files without confirmation

## Files/Folders Used
- Target planning directories in the vault
- Generated Plan.md files
- Related files referenced in the plan

## Example Invocation (Claude Code style)
```
<action skill="Plan.md_Generation_Skill">
{
  "task_description": "Implement a new feature for user authentication",
  "target_file_path": "Plans/User_Auth_Feature_Plan.md",
  "vault_root": "/Users/username/Obsidian_Vault",
  "related_files": ["Projects/User_System.md", "Notes/Security_Requirements.md"]
}
</action>
```