# Accounting Odoo Skill - SKILL.md

## Overview

**Tier:** Gold  
**HITL Required:** Yes (for invoice creation)  
**MCP Server:** `src/mcp/odoo/server.py`

This skill provides production-ready business finance management through Odoo ERP integration using the Model Context Protocol (MCP).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AccountingOdooSkill                       │
├─────────────────────────────────────────────────────────────┤
│  - OdooMCPClient (connects to MCP server via stdio)         │
│  - ApprovalManager (HITL workflow in Pending_Approval/)     │
│  - Audit Logger (in-memory log for compliance)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Odoo MCP Server                            │
│              (src/mcp/odoo/server.py)                        │
├─────────────────────────────────────────────────────────────┤
│  Tools:                                                      │
│  - create_invoice(partner_name, amount, description)         │
│  - get_total_revenue()                                       │
│  - get_partner_info(partner_name)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Odoo XML-RPC API                          │
│              (xmlrpc.client.ServerProxy)                     │
├─────────────────────────────────────────────────────────────┤
│  Endpoints:                                                  │
│  - /xmlrpc/2/common (authentication)                         │
│  - /xmlrpc/2/object (model operations)                       │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

Create `.env` file in project root (copy from `.env.example`):

```bash
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

**Security Notes:**
- Never commit `.env` to version control
- Use API keys instead of passwords in production
- Credentials are read from environment, never stored in vault

## API Reference

### `create_invoice(client_name, amount, description, require_approval=True)`

Creates a draft customer invoice in Odoo.

**Parameters:**
- `client_name` (str): Name of the customer/partner
- `amount` (float): Invoice amount (excluding tax)
- `description` (str): Description of goods/services
- `require_approval` (bool): Whether to require HITL approval (default: True)

**Returns:**
```python
{
    "success": True,
    "invoice_id": 123,
    "invoice_number": "INV/2026/0001",
    "partner_id": 456,
    "amount": 1500.0,
    "description": "Consulting Services",
    "client_name": "Acme Corp",
    "message": "Invoice INV/2026/0001 created for Acme Corp"
}
```

**HITL Workflow:**
1. Creates approval file in `Pending_Approval/`
2. Waits for approval (timeout: 1 hour)
3. Proceeds only if approved

### `get_total_revenue()`

Gets total revenue from all posted customer invoices.

**Returns:**
```python
{
    "success": True,
    "total_revenue": 15000.0,
    "currency": "USD",
    "invoice_count": 10,
    "queried_at": "2026-02-18T10:30:00",
    "message": "Total revenue: 15000.0 USD from 10 invoices"
}
```

### `get_partner_info(partner_name)`

Searches for partner/customer information.

**Parameters:**
- `partner_name` (str): Name or partial name to search

**Returns:**
```python
{
    "success": True,
    "found": True,
    "id": 10,
    "name": "Acme Corp",
    "email": "contact@acme.com",
    "phone": "+1-555-0100",
    "address": "123 Main St, City, State 12345, Country",
    "vat": "US123456789",
    "website": "https://acme.com"
}
```

## Usage Examples

### Async Usage (Recommended)

```python
import asyncio
from src.skills.accounting_odoo_skill import AccountingOdooSkill

async def main():
    skill = AccountingOdooSkill()
    
    # Connect to Odoo
    await skill.connect()
    
    # Get revenue report
    revenue = await skill.get_total_revenue()
    print(f"Total Revenue: {revenue['total_revenue']} {revenue['currency']}")
    
    # Get partner info
    partner = await skill.get_partner_info("Acme Corp")
    if partner['found']:
        print(f"Partner: {partner['name']}, Email: {partner['email']}")
    
    # Create invoice (requires approval)
    invoice = await skill.create_invoice(
        client_name="Acme Corp",
        amount=1500.0,
        description="Consulting Services - February 2026"
    )
    
    await skill.disconnect()

asyncio.run(main())
```

### Approval Workflow

When `create_invoice` is called with `require_approval=True`:

1. **Approval File Created:** `Pending_Approval/YYYYMMDD_HHMMSS_create_invoice.json`
2. **Human Reviews:** Check the approval file contents
3. **Approve/Reject:** Modify the file:
   ```json
   {
     "status": "approved",
     "approved_by": "human_user",
     "approved_at": "2026-02-18T10:30:00"
   }
   ```
4. **Skill Proceeds:** Invoice is created in Odoo

## Error Handling

### Connection Errors

```python
{
    "success": False,
    "error": "Connection error: Cannot connect to Odoo server at http://localhost:8069"
}
```

### Authentication Errors

```python
{
    "success": False,
    "error": "AuthenticationError: Authentication failed for user 'admin'"
}
```

### Approval Not Granted

```python
{
    "success": False,
    "error": "Invoice creation not approved",
    "request_id": "20260218_103000_create_invoice"
}
```

## Audit Logging

All operations are logged for compliance:

```python
skill.get_audit_log(limit=100)
# Returns:
[
    {
        "timestamp": "2026-02-18T10:30:00",
        "action": "create_invoice",
        "success": True,
        "result_summary": "{'invoice_id': 123, 'invoice_number': 'INV/2026/0001'}"
    }
]
```

## Testing

### Unit Tests

```bash
pytest tests/test_odoo_mcp_server.py -v
```

### Integration Tests (requires Odoo instance)

```bash
# Set credentials
export ODOO_URL=http://localhost:8069
export ODOO_DB=odoo
export ODOO_USERNAME=admin
export ODOO_PASSWORD=admin

# Run integration tests
pytest tests/test_odoo_mcp_server.py -v -m integration
```

## Dependencies

### MCP Server (`src/mcp/odoo/requirements.txt`)

```
mcp>=1.0.0
python-dotenv>=1.0.0
# xmlrpc.client (stdlib)
```

### Skill Dependencies

```
# Inherited from MCP server
# Plus standard library: asyncio, json, logging, pathlib
```

## Gold Tier Compliance Checklist

- [x] Real Odoo XML-RPC API (no mocks)
- [x] Human-in-the-Loop approval for sensitive actions
- [x] Full audit logging
- [x] Proper error handling for network issues
- [x] Credentials from environment (not vault)
- [x] MCP server pattern for tool registration
- [x] Async/await support
- [x] Comprehensive test coverage

## Troubleshooting

### "Not authenticated with Odoo"

1. Check `.env` file exists with correct credentials
2. Verify Odoo server is running
3. Test connection: `python -c "import xmlrpc.client; c = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common'); print(c.authenticate('odoo', 'admin', 'admin'))"`

### "Connection refused"

1. Verify Odoo server is running on specified URL
2. Check firewall settings
3. Ensure correct port (default: 8069)

### "Approval timeout"

1. Check `Pending_Approval/` folder for approval request
2. Modify approval file to set `"status": "approved"`
3. Increase timeout in `wait_for_approval()` call
