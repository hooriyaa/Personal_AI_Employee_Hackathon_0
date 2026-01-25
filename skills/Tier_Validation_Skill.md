# Tier Validation Skill

## Purpose
Ensure actions do not exceed Bronze Tier permissions and validate compliance with current tier limitations.

## Inputs
- `proposed_action`: String description of the action to be validated
- `required_tier`: String indicating the minimum tier required for the action ('Bronze', 'Silver', 'Gold', 'Platinum')
- `current_tier`: String indicating the current operational tier ('Bronze', 'Silver', 'Gold', 'Platinum')
- `action_parameters`: Object containing parameters of the proposed action

## Outputs
- `approved`: Boolean indicating if the action is approved for the current tier
- `validation_message`: String message explaining the validation result
- `suggested_alternative`: String suggesting alternative if action exceeds current tier
- `compliance_score`: Number from 0-100 indicating how well the action complies with tier requirements
- `error_message`: String error message if validation failed

## Preconditions
- The current operational tier must be defined and accessible
- The proposed action must be clearly described
- Tier requirements and limitations must be accessible

## Safety Rules
- Block any action that exceeds current tier permissions
- Provide clear feedback when actions are rejected for tier reasons
- Suggest compliant alternatives when possible
- Log all tier validation attempts for audit purposes
- Never escalate tier permissions without proper authorization

## Files/Folders Used
- Tier configuration files
- Current tier status files
- Validation rule definitions

## Example Invocation (Claude Code style)
```
<action skill="Tier_Validation_Skill">
{
  "proposed_action": "Access external API for data retrieval",
  "required_tier": "Silver",
  "current_tier": "Bronze",
  "action_parameters": {
    "api_endpoint": "https://external-service.com/data",
    "authentication": "oauth2"
  }
}
</action>
```