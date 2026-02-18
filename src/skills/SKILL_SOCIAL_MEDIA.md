# SKILL: Social Media Posting

## Overview
Skill for managing cross-platform social media posts with Human-in-the-Loop (HITL) approval workflow.

**Hackathon Tier:** Gold (Multiple MCP Servers)

**Architecture:** Local-First with MCP Server Integration

---

## Purpose

This skill enables the AI Employee to:
- Create social media posts for Facebook and X/Twitter
- Enforce Human-in-the-Loop approval before any external posting
- Integrate with Social Media MCP Server for actual API calls
- Maintain full audit trail of all posting activities

---

## Human-in-the-Loop (HITL) Workflow

### Critical Rule
**The Agent/Skill MUST NOT call MCP server tools directly.**

All social media posts follow this approval workflow:

```
┌─────────────────────────────────────────────────────────────────┐
│                    HITL Approval Workflow                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Agent creates post content                                   │
│     ↓                                                            │
│  2. Skill creates file in Pending_Approval/                      │
│     DRAFT_SOCIAL_FACEBOOK_20260218_143022.md                    │
│     ↓                                                            │
│  3. Human reviews content                                        │
│     ↓                                                            │
│  4. Human moves file to Approved/ (APPROVAL)                     │
│     ↓                                                            │
│  5. Action Runner detects approved file                          │
│     ↓                                                            │
│  6. Action Runner calls MCP tool: post_to_facebook               │
│     ↓                                                            │
│  7. MCP Server executes API call                                 │
│     ↓                                                            │
│  8. Result logged to audit trail                                 │
│     ↓                                                            │
│  9. File archived in Approved/Social_Media/Executed/             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Files

### Skill Implementation
- `src/skills/social_media_skill.py` - Main skill logic with HITL enforcement

### MCP Server
- `src/mcp/social/server.py` - MCP server for Facebook/Twitter APIs
- `src/mcp/social/requirements.txt` - Python dependencies
- `src/mcp/social/__init__.py` - Package initialization

### Configuration
- `.env.example` - Environment variable templates

---

## Functions

### `post_to_facebook(message: str) -> Dict`
Create a Facebook post request (pending approval).

**Parameters:**
- `message`: Facebook post text content (max 63,206 characters)

**Returns:**
```json
{
  "success": true,
  "status": "pending_approval",
  "post_id": "FB_20260218_143022_4521",
  "platform": "facebook",
  "approval_file": "/path/to/Pending_Approval/DRAFT_SOCIAL_FACEBOOK_*.md",
  "content": {"message": "...", "character_count": 150},
  "message": "Facebook post created and pending human approval"
}
```

### `post_to_twitter(text: str) -> Dict`
Create a Twitter/X post request (pending approval).

**Parameters:**
- `text`: Tweet text content (max 280 characters)

**Returns:**
```json
{
  "success": true,
  "status": "pending_approval",
  "post_id": "TW_20260218_143022_8734",
  "platform": "twitter",
  "approval_file": "/path/to/Pending_Approval/DRAFT_SOCIAL_TWITTER_*.md",
  "content": {"text": "...", "character_count": 140},
  "message": "X (Twitter) post created and pending human approval"
}
```

### `execute_approved_post(approval_file_path: str, mcp_client: Any) -> Dict`
Execute a post that has been approved (moved to Approved directory).

**Parameters:**
- `approval_file_path`: Path to the approved post file
- `mcp_client`: MCP client instance for tool execution

**Returns:**
```json
{
  "success": true,
  "platform": "facebook",
  "executed_at": "2026-02-18T14:35:00.000000",
  "archived_path": "/path/to/Approved/Social_Media/Executed/POSTED_*.md",
  "audit_log": "/path/to/Logs/social_media/audit_*.json",
  "api_result": {"success": true, "post_id": "..."}
}
```

---

## MCP Tools

The Social Media MCP Server exposes these tools:

### `post_to_facebook`
- **Endpoint:** `https://graph.facebook.com/v19.0/{page_id}/feed`
- **Method:** POST
- **Payload:** `{'message': message, 'access_token': token}`
- **Error Handling:** 400/401/500 errors raised as exceptions

### `post_to_twitter`
- **Endpoint:** `https://api.twitter.com/2/tweets`
- **Method:** POST
- **Headers:** `Authorization: Bearer {token}`
- **Payload:** `{'text': text}`
- **Error Handling:** 400/401/403/500 errors raised as exceptions

---

## Environment Variables

Required in `.env` (NOT in vault):

```bash
# Facebook
FB_PAGE_ACCESS_TOKEN=your_page_access_token
FB_PAGE_ID=your_page_id

# Twitter/X
TWITTER_BEARER_TOKEN=your_bearer_token
```

---

## Directory Structure

```
hackathon_0/
├── Pending_Approval/
│   └── DRAFT_SOCIAL_FACEBOOK_20260218_143022.md  ← Created by skill
├── Approved/
│   └── Social_Media/
│       └── Executed/
│           └── POSTED_DRAFT_SOCIAL_FACEBOOK_*.md  ← Archived after execution
├── Logs/
│   └── social_media/
│       └── audit_facebook_20260218_143500.json   ← Audit trail
└── src/
    ├── mcp/
    │   └── social/
    │       ├── server.py                          ← MCP server
    │       ├── requirements.txt
    │       └── __init__.py
    └── skills/
        └── social_media_skill.py                   ← This skill
```

---

## Approval File Format

```markdown
---
type: social_media_post
status: Pending_Approval
post_id: FB_20260218_143022_4521
platform: facebook
mcp_tool: post_to_facebook
created_at: 2026-02-18T14:30:22
created_by: AI_Employee
hackathon_tier: Gold
---

# Social Media Post Approval Request

## Platform
**Facebook**

## Content to Post
```
Excited to announce our new AI-powered automation system!
```

## Metadata
- **Post ID:** FB_20260218_143022_4521
- **Created:** 2026-02-18T14:30:22
- **MCP Tool:** post_to_facebook
- **Status:** Pending Human Approval

---

## Approval Instructions (HITL Workflow)

**To APPROVE this post:**
1. Review the content above carefully
2. Move this file to the `Approved/` directory
3. The system will automatically call the MCP tool to execute the post
```

---

## Error Handling

### Skill Level
- Character limit validation (Facebook: 63,206, Twitter: 280)
- File system errors for approval file creation
- Empty content validation

### MCP Server Level
- `AuthenticationError` (401): Invalid/missing credentials
- `FacebookAPIError` / `TwitterAPIError` (400): Bad request
- `FacebookAPIError` / `TwitterAPIError` (500): Server errors
- Network timeouts and connection errors

---

## Audit Trail

Every executed post creates an audit log entry:

```json
{
  "timestamp": "2026-02-18T14:35:00.000000",
  "platform": "facebook",
  "message_data": {"message": "...", "character_count": 150},
  "result": {"success": true, "post_id": "..."},
  "hitl_verified": true
}
```

Location: `Logs/social_media/audit_*.json`

---

## Testing

```bash
# Test skill directly
python src/skills/social_media_skill.py

# Test MCP server (requires credentials)
python src/mcp/social/server.py

# Check pending posts
python -c "from src.skills.social_media_skill import SocialMediaSkill; s = SocialMediaSkill(); print(s.list_pending_posts())"
```

---

## Security Considerations

1. **Credentials:** Never stored in vault, only in `.env`
2. **HITL:** All posts require human approval before execution
3. **Audit:** Full audit trail of all posting activities
4. **Rate Limits:** MCP server handles API rate limiting
5. **Validation:** Content length validated before approval file creation

---

## Hackathon Compliance

| Requirement | Status |
|-------------|--------|
| Gold Tier - Multiple MCP Servers | ✅ Social Media MCP + Odoo MCP |
| HITL Approval Workflow | ✅ Pending_Approval → Approved |
| Local-First Architecture | ✅ Obsidian Vault as source of truth |
| No Credentials in Vault | ✅ Environment variables only |
| Audit Logging | ✅ Logs/social_media/ |
| Error Handling | ✅ 400/401/500 errors |
| Reusable Skill | ✅ SKILL.md documented |

---

## Related Skills

- `vault_read_skill.py` - Read from Obsidian Vault
- `vault_write_skill.py` - Write to Obsidian Vault
- `linkedin_skill.py` - LinkedIn posting (similar pattern)

## Related MCP Servers

- `src/mcp/odoo/server.py` - Odoo ERP integration
- `src/mcp/social/server.py` - Social Media APIs (this)
