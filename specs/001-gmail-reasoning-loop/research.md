# Research: Gmail Reasoning Loop

## Gmail API Authentication Research

**Decision**: Use OAuth 2.0 with user credentials
**Rationale**: OAuth 2.0 is the standard and secure way to access Gmail API. It provides appropriate permissions without exposing user passwords.
**Alternatives considered**: 
- Basic authentication (deprecated and insecure)
- API keys (insufficient for Gmail access)

**Resources**:
- Google's Python Quickstart: https://developers.google.com/gmail/api/quickstart/python
- OAuth 2.0 flow for desktop applications

## Rate Limiting Research

**Decision**: Implement 60-120 second polling intervals
**Rationale**: Gmail API has daily quotas (e.g., 1 million units/day) and per-user rate limits. A 60-120 second interval respects these limits while maintaining reasonable responsiveness.
**Alternatives considered**: 
- Push notifications (requires web server to receive callbacks, more complex)
- Shorter polling intervals (higher risk of hitting rate limits)

**Details**:
- Gmail API has a default rate limit of 250 requests per user per second
- Daily quotas vary by application but are typically 1M units/day
- Each API call has a cost in "units" (e.g., getting a message costs 5 units)

## File System Monitoring Research

**Decision**: Use watchdog library for cross-platform file system monitoring
**Rationale**: Well-maintained, cross-platform, event-driven, and lightweight. Perfect for monitoring directory changes.
**Alternatives considered**: 
- Built-in os.stat polling (less efficient, higher CPU usage)
- Platform-specific solutions (would require separate implementations for Windows/Mac/Linux)

**Resources**:
- Watchdog documentation: https://python-watchdog.readthedocs.io/
- Event handlers for file creation, modification, and movement

## Approval Mechanism Research

**Decision**: File-based approval system with `/Pending_Approval` and `/Approved` directories
**Rationale**: Simple, transparent, allows human oversight without complex UI. Leverages existing file system monitoring infrastructure.
**Alternatives considered**: 
- Database tracking (adds complexity with little benefit)
- Email confirmations (creates circular dependency issue)
- Interactive prompts (would interrupt automated workflow)

**Workflow**:
1. System identifies action requiring approval
2. Creates file in `/Pending_Approval` directory
3. User reviews and moves file to `/Approved` directory
4. System detects file move and executes action

## Security Considerations

**Credential Storage**:
- Store credentials.json and token.json in `/secrets/` directory
- Add `/secrets/` to `.gitignore` to prevent committing sensitive data
- Use proper file permissions to restrict access to credential files

**API Best Practices**:
- Implement proper error handling for API failures
- Include retry logic with exponential backoff
- Log API interactions for debugging while protecting sensitive data