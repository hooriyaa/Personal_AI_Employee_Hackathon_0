# Dashboard Update Skill

## Purpose
Update Dashboard.md summaries following the single-writer rule to prevent conflicts.

## Inputs
- `summary_section`: String section of the dashboard to update
- `content`: String content to add or update in the dashboard
- `vault_root`: String path to the Obsidian vault directory
- `update_type`: String indicating type of update ('append', 'replace', 'delete')

## Outputs
- `success`: Boolean indicating if the dashboard update was successful
- `dashboard_path`: String path of the updated dashboard file
- `error_message`: String error message if operation failed
- `timestamp`: String timestamp of the update

## Preconditions
- The Dashboard.md file must exist in the vault
- No other process should be currently writing to the dashboard
- The vault root directory must be accessible and writable

## Safety Rules
- Implement locking mechanism to enforce single-writer rule
- Validate dashboard format before and after updates
- Create backup before making significant changes
- Ensure updates don't corrupt dashboard structure

## Files/Folders Used
- Dashboard.md file in the vault root
- Temporary lock files for single-writer enforcement
- Backup files for dashboard recovery

## Example Invocation (Claude Code style)
```
<action skill="Dashboard_Update_Skill">
{
  "summary_section": "Daily_Tasks",
  "content": "- [x] Completed project proposal\n- [ ] Awaiting feedback on design",
  "vault_root": "/Users/username/Obsidian_Vault",
  "update_type": "replace"
}
</action>
```