"""
Accounting Odoo Skill - Production-ready business finances via Odoo MCP Server.

Gold Tier Compliance:
- Real Odoo XML-RPC API integration (NO MOCKS)
- Human-in-the-Loop approval before invoice creation
- Full audit logging
- Proper error handling for network issues

This skill connects to the Odoo MCP Server to:
- Create draft invoices
- Get total revenue reports
- Get partner/customer information
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

# MCP Client imports
try:
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client, StdioServerParameters
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP library not available. Running in degraded mode.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ApprovalRequest:
    """Represents a HITL approval request."""
    action: str
    details: Dict[str, Any]
    status: str = "pending"  # pending, approved, rejected
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    request_id: Optional[str] = None


class OdooMCPClient:
    """
    MCP Client for connecting to the Odoo MCP Server.
    
    Provides a clean interface to call Odoo tools via MCP protocol.
    """

    def __init__(self, server_script_path: Optional[str] = None):
        """
        Initialize the Odoo MCP Client.

        Args:
            server_script_path: Path to the Odoo MCP server script.
                               If None, uses environment-based connection.
        """
        self.server_script_path = server_script_path
        self._session: Optional[ClientSession] = None
        self._context = None
        self._connected = False

    async def connect(self) -> bool:
        """
        Establish connection to the Odoo MCP Server.

        Returns:
            True if connection successful
        """
        if not MCP_AVAILABLE:
            logger.error("MCP library not available")
            return False

        try:
            # Check for environment credentials
            required_vars = ['ODOO_URL', 'ODOO_DB', 'ODOO_USERNAME', 'ODOO_PASSWORD']
            missing = [var for var in required_vars if not os.environ.get(var)]
            
            if missing:
                logger.warning(f"Missing Odoo credentials: {missing}. Server may not connect.")

            # Set up stdio client with server script
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_script_path or "src/mcp/odoo/server.py"],
                env={**os.environ}
            )

            self._context = stdio_client(server_params)
            self._session = await self._context.__aenter__()
            
            session = ClientSession(self._session[0], self._session[1])
            await session.initialize()
            self._session = session
            self._connected = True
            
            logger.info("Connected to Odoo MCP Server")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Odoo MCP Server: {e}")
            self._connected = False
            return False

    async def disconnect(self):
        """Disconnect from the Odoo MCP Server."""
        if self._context:
            try:
                await self._context.__aexit__(None, None, None)
            except Exception:
                pass
        self._connected = False
        logger.info("Disconnected from Odoo MCP Server")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an Odoo tool via MCP.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool result dictionary
        """
        if not self._connected:
            raise ConnectionError("Not connected to Odoo MCP Server")

        try:
            result = await self._session.call_tool(tool_name, arguments)
            
            # Parse the text response
            if result and hasattr(result, 'content') and result.content:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return json.loads(content.text)
            
            return {"success": False, "error": "Unexpected response format"}

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP response: {e}")
            return {"success": False, "error": f"Response parse error: {e}"}
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}

    async def create_invoice(self, partner_name: str, amount: float,
                             description: str) -> Dict[str, Any]:
        """Create an invoice via MCP."""
        return await self.call_tool("create_invoice", {
            "partner_name": partner_name,
            "amount": amount,
            "description": description
        })

    async def get_total_revenue(self) -> Dict[str, Any]:
        """Get total revenue via MCP."""
        return await self.call_tool("get_total_revenue", {})

    async def get_partner_info(self, partner_name: str) -> Dict[str, Any]:
        """Get partner info via MCP."""
        return await self.call_tool("get_partner_info", {
            "partner_name": partner_name
        })


class ApprovalManager:
    """
    Manages Human-in-the-Loop approval workflow.
    
    Creates approval files in Pending_Approval directory.
    Waits for approval before proceeding with sensitive actions.
    """

    def __init__(self, approval_dir: str = "Pending_Approval"):
        """
        Initialize the approval manager.

        Args:
            approval_dir: Directory for approval files
        """
        self.approval_dir = Path(approval_dir)
        self.approval_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Approval manager initialized: {self.approval_dir}")

    def request_approval(self, action: str, details: Dict[str, Any],
                         timeout_minutes: int = 60) -> ApprovalRequest:
        """
        Create an approval request file.

        Args:
            action: Action requiring approval
            details: Action details
            timeout_minutes: Approval timeout

        Returns:
            ApprovalRequest object
        """
        request_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{action.lower()}"
        
        approval_data = {
            "request_id": request_id,
            "action": action,
            "details": details,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "timeout_minutes": timeout_minutes,
            "instructions": f"Review and set status to 'approved' or 'rejected'"
        }

        # Write approval file
        approval_file = self.approval_dir / f"{request_id}.json"
        with open(approval_file, 'w') as f:
            json.dump(approval_data, f, indent=2)

        logger.info(f"Created approval request: {request_id}")
        
        return ApprovalRequest(
            action=action,
            details=details,
            request_id=request_id
        )

    def check_approval(self, request_id: str) -> Optional[ApprovalRequest]:
        """
        Check approval status.

        Args:
            request_id: The approval request ID

        Returns:
            ApprovalRequest if found, None otherwise
        """
        approval_file = self.approval_dir / f"{request_id}.json"
        
        if not approval_file.exists():
            return None

        with open(approval_file, 'r') as f:
            data = json.load(f)

        return ApprovalRequest(
            action=data.get('action'),
            details=data.get('details'),
            status=data.get('status', 'pending'),
            approved_by=data.get('approved_by'),
            approved_at=data.get('approved_at'),
            request_id=data.get('request_id')
        )

    def wait_for_approval(self, request_id: str,
                          timeout_seconds: int = 3600) -> bool:
        """
        Wait for approval (polling).

        Args:
            request_id: The approval request ID
            timeout_seconds: Maximum wait time

        Returns:
            True if approved, False if rejected or timeout
        """
        import time
        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            approval = self.check_approval(request_id)
            if approval:
                if approval.status == 'approved':
                    logger.info(f"Approval granted: {request_id}")
                    return True
                elif approval.status == 'rejected':
                    logger.warning(f"Approval rejected: {request_id}")
                    return False
            
            time.sleep(5)  # Poll every 5 seconds

        logger.warning(f"Approval timeout: {request_id}")
        return False


class AccountingOdooSkill:
    """
    Gold Tier skill for managing business finances through Odoo.

    Provides methods to:
    - Create draft invoices (with HITL approval)
    - Get total revenue reports
    - Get partner/customer information

    Architecture:
    - Connects to Odoo MCP Server for all operations
    - Enforces HITL approval for invoice creation
    - Logs all operations for audit purposes
    """

    def __init__(self, mcp_client: Optional[OdooMCPClient] = None,
                 approval_manager: Optional[ApprovalManager] = None):
        """
        Initialize the accounting skill.

        Args:
            mcp_client: Odoo MCP client instance
            approval_manager: HITL approval manager
        """
        self.mcp_client = mcp_client or OdooMCPClient()
        self.approval_manager = approval_manager or ApprovalManager()
        self._audit_log: list = []
        self._connected = False

    def _log_audit(self, action: str, result: Dict[str, Any],
                   success: bool = True):
        """Log action for audit purposes."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "success": success,
            "result_summary": str(result)[:500]  # Truncate for safety
        }
        self._audit_log.append(entry)
        
        # Keep log manageable
        if len(self._audit_log) > 1000:
            self._audit_log = self._audit_log[-500:]

        logger.info(f"Audit: {action} - {'Success' if success else 'Failed'}")

    async def connect(self) -> bool:
        """
        Establish connection to Odoo MCP Server.

        Returns:
            True if connection successful
        """
        self._connected = await self.mcp_client.connect()
        return self._connected

    async def disconnect(self):
        """Disconnect from Odoo MCP Server."""
        await self.mcp_client.disconnect()
        self._connected = False

    async def create_invoice(self, client_name: str, amount: float,
                             description: str,
                             require_approval: bool = True) -> Dict[str, Any]:
        """
        Create a draft invoice in Odoo with HITL approval.

        Args:
            client_name: Name of the client/customer
            amount: Invoice amount (excluding tax)
            description: Description of goods/services
            require_approval: Whether to require HITL approval (default: True)

        Returns:
            Dictionary with invoice creation result:
            {
                "success": bool,
                "invoice_id": int,
                "invoice_number": str,
                "partner_id": int,
                "amount": float,
                "message": str
            }
        """
        try:
            # Ensure connection
            if not self._connected:
                if not await self.connect():
                    return {
                        "success": False,
                        "error": "Failed to connect to Odoo MCP Server"
                    }

            # HITL Approval for invoice creation
            if require_approval:
                approval_request = self.approval_manager.request_approval(
                    action="create_invoice",
                    details={
                        "client_name": client_name,
                        "amount": amount,
                        "description": description
                    }
                )

                logger.info(f"Waiting for approval: {approval_request.request_id}")
                
                # Wait for approval (with timeout)
                approved = self.approval_manager.wait_for_approval(
                    approval_request.request_id,
                    timeout_seconds=3600  # 1 hour
                )

                if not approved:
                    self._log_audit("create_invoice", {
                        "client_name": client_name,
                        "amount": amount,
                        "reason": "Approval not granted"
                    }, success=False)
                    
                    return {
                        "success": False,
                        "error": "Invoice creation not approved",
                        "request_id": approval_request.request_id
                    }

            # Create invoice via MCP
            result = await self.mcp_client.create_invoice(
                partner_name=client_name,
                amount=amount,
                description=description
            )

            # Check for errors in result
            if isinstance(result, str) and ("Error" in result or "ConnectionError" in result):
                self._log_audit("create_invoice", result, success=False)
                return {
                    "success": False,
                    "error": result
                }

            self._log_audit("create_invoice", result, success=True)
            
            return {
                "success": True,
                "invoice_id": result.get("invoice_id"),
                "invoice_number": result.get("invoice_number"),
                "partner_id": result.get("partner_id"),
                "amount": result.get("amount"),
                "description": description,
                "client_name": client_name,
                "message": f"Invoice {result.get('invoice_number')} created for {client_name}"
            }

        except ConnectionError as e:
            logger.error(f"Connection error creating invoice: {e}")
            self._log_audit("create_invoice", {"error": str(e)}, success=False)
            return {
                "success": False,
                "error": f"Connection error: {e}"
            }
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            self._log_audit("create_invoice", {"error": str(e)}, success=False)
            return {
                "success": False,
                "error": str(e)
            }

    async def get_total_revenue(self) -> Dict[str, Any]:
        """
        Get total revenue from posted customer invoices.

        Returns:
            Dictionary with daily revenue report:
            {
                "success": bool,
                "total_revenue": float,
                "currency": str,
                "invoice_count": int,
                "message": str
            }
        """
        try:
            # Ensure connection
            if not self._connected:
                if not await self.connect():
                    return {
                        "success": False,
                        "error": "Failed to connect to Odoo MCP Server"
                    }

            result = await self.mcp_client.get_total_revenue()

            # Check for errors in result
            if isinstance(result, str) and ("Error" in result or "ConnectionError" in result):
                self._log_audit("get_total_revenue", result, success=False)
                return {
                    "success": False,
                    "error": result
                }

            self._log_audit("get_total_revenue", result, success=True)

            return {
                "success": True,
                "total_revenue": result.get("total_revenue", 0),
                "currency": result.get("currency", "USD"),
                "invoice_count": result.get("invoice_count", 0),
                "queried_at": result.get("queried_at"),
                "message": f"Total revenue: {result.get('total_revenue', 0)} {result.get('currency', 'USD')} from {result.get('invoice_count', 0)} invoices"
            }

        except ConnectionError as e:
            logger.error(f"Connection error getting revenue: {e}")
            self._log_audit("get_total_revenue", {"error": str(e)}, success=False)
            return {
                "success": False,
                "error": f"Connection error: {e}"
            }
        except Exception as e:
            logger.error(f"Error getting revenue: {e}")
            self._log_audit("get_total_revenue", {"error": str(e)}, success=False)
            return {
                "success": False,
                "error": str(e)
            }

    async def get_partner_info(self, partner_name: str) -> Dict[str, Any]:
        """
        Get partner/customer information from Odoo.

        Args:
            partner_name: Name or partial name to search

        Returns:
            Dictionary with partner details:
            {
                "success": bool,
                "found": bool,
                "id": int,
                "name": str,
                "email": str,
                "phone": str,
                "address": str,
                "message": str
            }
        """
        try:
            # Ensure connection
            if not self._connected:
                if not await self.connect():
                    return {
                        "success": False,
                        "error": "Failed to connect to Odoo MCP Server"
                    }

            result = await self.mcp_client.get_partner_info(partner_name=partner_name)

            # Check for errors in result
            if isinstance(result, str) and ("Error" in result or "ConnectionError" in result):
                self._log_audit("get_partner_info", result, success=False)
                return {
                    "success": False,
                    "error": result
                }

            self._log_audit("get_partner_info", result, success=True)

            if result.get("found"):
                return {
                    "success": True,
                    "found": True,
                    "id": result.get("id"),
                    "name": result.get("name"),
                    "email": result.get("email"),
                    "phone": result.get("phone"),
                    "address": result.get("address"),
                    "city": result.get("city"),
                    "country": result.get("country"),
                    "vat": result.get("vat"),
                    "website": result.get("website"),
                    "message": f"Found partner: {result.get('name')}"
                }
            else:
                return {
                    "success": True,
                    "found": False,
                    "search_term": result.get("search_term"),
                    "message": f"No partner found matching: {partner_name}"
                }

        except ConnectionError as e:
            logger.error(f"Connection error getting partner info: {e}")
            self._log_audit("get_partner_info", {"error": str(e)}, success=False)
            return {
                "success": False,
                "error": f"Connection error: {e}"
            }
        except Exception as e:
            logger.error(f"Error getting partner info: {e}")
            self._log_audit("get_partner_info", {"error": str(e)}, success=False)
            return {
                "success": False,
                "error": str(e)
            }

    def get_audit_log(self, limit: int = 100) -> list:
        """Get recent audit log entries."""
        return self._audit_log[-limit:]


# Convenience async functions for direct import and use
async def create_invoice(client_name: str, amount: float,
                         description: str) -> Dict[str, Any]:
    """
    Create a draft invoice with HITL approval.

    Args:
        client_name: Name of the client
        amount: Invoice amount
        description: Description of goods/services

    Returns:
        Invoice creation result dictionary
    """
    skill = AccountingOdooSkill()
    return await skill.create_invoice(client_name, amount, description)


async def get_total_revenue() -> Dict[str, Any]:
    """
    Get total revenue from posted invoices.

    Returns:
        Revenue report dictionary
    """
    skill = AccountingOdooSkill()
    return await skill.get_total_revenue()


async def get_partner_info(partner_name: str) -> Dict[str, Any]:
    """
    Get partner information.

    Args:
        partner_name: Name to search

    Returns:
        Partner info dictionary
    """
    skill = AccountingOdooSkill()
    return await skill.get_partner_info(partner_name)


# Example usage and testing
async def main():
    """Test the Accounting Odoo Skill."""
    print("Testing Accounting Odoo Skill (Production Mode)...")
    print("-" * 50)

    skill = AccountingOdooSkill()

    # Test connection
    print("\n1. Connecting to Odoo MCP Server...")
    connected = await skill.connect()
    print(f"   Connected: {connected}")

    if not connected:
        print("   Skipping tests - no connection")
        return

    # Test get partner info
    print("\n2. Getting partner info...")
    partner_result = await skill.get_partner_info("Admin")
    print(f"   Result: {json.dumps(partner_result, indent=2)}")

    # Test get total revenue
    print("\n3. Getting total revenue...")
    revenue_result = await skill.get_total_revenue()
    print(f"   Result: {json.dumps(revenue_result, indent=2)}")

    # Test invoice creation (requires approval)
    print("\n4. Creating invoice (requires approval)...")
    print("   Check Pending_Approval folder for approval request")
    invoice_result = await skill.create_invoice(
        "Test Client",
        1500.00,
        "Consulting Services - Test"
    )
    print(f"   Result: {json.dumps(invoice_result, indent=2)}")

    # Show audit log
    print("\n5. Audit Log:")
    for entry in skill.get_audit_log():
        print(f"   - {entry['timestamp']}: {entry['action']} ({'OK' if entry['success'] else 'FAIL'})")

    await skill.disconnect()

    print("\n" + "-" * 50)
    print("Tests completed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
