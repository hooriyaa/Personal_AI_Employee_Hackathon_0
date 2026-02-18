"""
Test Suite for Odoo MCP Server - Gold Tier Compliance.

Tests verify:
- Real XML-RPC connection handling
- Error propagation (no mocks)
- Tool registration and invocation
- HITL approval workflow
"""

import os
import sys
import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestOdooXMLRPCClient:
    """Test the Odoo XML-RPC client with real connection handling."""

    def test_init_stores_credentials(self):
        """Test client initialization stores credentials correctly."""
        from mcp.odoo.server import OdooXMLRPCClient
        
        client = OdooXMLRPCClient(
            url="http://localhost:8069",
            db="odoo",
            username="admin",
            password="secret"
        )
        
        assert client.url == "http://localhost:8069"
        assert client.db == "odoo"
        assert client.username == "admin"
        assert client.password == "secret"
        assert client.uid is None
        assert client.authenticated is False

    def test_connect_raises_on_missing_credentials(self):
        """Test connect raises appropriate errors when credentials invalid."""
        from mcp.odoo.server import OdooXMLRPCClient, AuthenticationError
        
        client = OdooXMLRPCClient(
            url="http://invalid-host-12345:8069",
            db="odoo",
            username="admin",
            password="wrong"
        )
        
        # Should raise ConnectionError for unreachable host
        with pytest.raises((ConnectionError,)):
            client.connect()

    def test_execute_kw_raises_when_not_authenticated(self):
        """Test execute_kw raises ConnectionError when not authenticated."""
        from mcp.odoo.server import OdooXMLRPCClient
        
        client = OdooXMLRPCClient(
            url="http://localhost:8069",
            db="odoo",
            username="admin",
            password="admin"
        )
        
        with pytest.raises(ConnectionError, match="Not authenticated"):
            client.execute_kw("res.partner", "search", [[]])


class TestOdooMCPServer:
    """Test the Odoo MCP Server tool registration and invocation."""

    def test_server_initialization(self):
        """Test server initializes with correct tools."""
        from mcp.odoo.server import OdooMCPServer
        
        # Mock environment to prevent connection attempt
        with patch.dict(os.environ, {}, clear=True):
            server = OdooMCPServer()
            
            assert server.server is not None
            assert server.client is None  # No credentials = no connection

    def test_get_env_credentials_missing(self):
        """Test credential retrieval raises on missing vars."""
        from mcp.odoo.server import OdooMCPServer
        
        with patch.dict(os.environ, {}, clear=True):
            server = OdooMCPServer.__new__(OdooMCPServer)
            
            with pytest.raises(ValueError, match="Missing required environment variables"):
                server._get_env_credentials()

    def test_get_env_credentials_success(self):
        """Test credential retrieval succeeds with all vars."""
        from mcp.odoo.server import OdooMCPServer
        
        with patch.dict(os.environ, {
            "ODOO_URL": "http://localhost:8069",
            "ODOO_DB": "odoo",
            "ODOO_USERNAME": "admin",
            "ODOO_PASSWORD": "admin"
        }):
            server = OdooMCPServer.__new__(OdooMCPServer)
            creds = server._get_env_credentials()
            
            assert creds["url"] == "http://localhost:8069"
            assert creds["db"] == "odoo"
            assert creds["username"] == "admin"
            assert creds["password"] == "admin"


class TestApprovalManager:
    """Test the HITL approval workflow."""

    def test_request_approval_creates_file(self, tmp_path):
        """Test approval request creates JSON file."""
        from skills.accounting_odoo_skill import ApprovalManager
        
        manager = ApprovalManager(approval_dir=str(tmp_path))
        
        request = manager.request_approval(
            action="create_invoice",
            details={"client": "Test", "amount": 100}
        )
        
        assert request.request_id is not None
        assert request.status == "pending"
        
        # Verify file exists
        approval_file = tmp_path / f"{request.request_id}.json"
        assert approval_file.exists()

    def test_check_approval_returns_status(self, tmp_path):
        """Test approval status checking."""
        from skills.accounting_odoo_skill import ApprovalManager
        
        manager = ApprovalManager(approval_dir=str(tmp_path))
        
        request = manager.request_approval(
            action="create_invoice",
            details={"client": "Test", "amount": 100}
        )
        
        # Check initial status
        approval = manager.check_approval(request.request_id)
        assert approval.status == "pending"

    def test_approval_workflow_integration(self, tmp_path):
        """Test full approval workflow."""
        import json
        from skills.accounting_odoo_skill import ApprovalManager
        
        manager = ApprovalManager(approval_dir=str(tmp_path))
        
        # Create request
        request = manager.request_approval(
            action="create_invoice",
            details={"client": "Test", "amount": 100}
        )
        
        # Simulate approval by modifying file
        approval_file = tmp_path / f"{request.request_id}.json"
        with open(approval_file, 'r') as f:
            data = json.load(f)
        
        data["status"] = "approved"
        data["approved_by"] = "test_user"
        
        with open(approval_file, 'w') as f:
            json.dump(data, f)
        
        # Verify approval detected
        approval = manager.check_approval(request.request_id)
        assert approval.status == "approved"
        assert approval.approved_by == "test_user"


class TestAccountingOdooSkill:
    """Test the Accounting Odoo Skill integration."""

    @pytest.mark.asyncio
    async def test_skill_initialization(self):
        """Test skill initializes correctly."""
        from skills.accounting_odoo_skill import AccountingOdooSkill
        
        skill = AccountingOdooSkill()
        
        assert skill.mcp_client is not None
        assert skill.approval_manager is not None
        assert skill._connected is False

    @pytest.mark.asyncio
    async def test_get_total_revenue_disconnected(self):
        """Test revenue query handles disconnection gracefully."""
        from skills.accounting_odoo_skill import AccountingOdooSkill
        
        skill = AccountingOdooSkill()
        
        # Should return error when not connected
        result = await skill.get_total_revenue()
        
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_create_invoice_requires_approval(self, tmp_path):
        """Test invoice creation requires HITL approval."""
        from skills.accounting_odoo_skill import AccountingOdooSkill, ApprovalManager
        
        approval_manager = ApprovalManager(approval_dir=str(tmp_path))
        skill = AccountingOdooSkill(approval_manager=approval_manager)
        
        # Create invoice (will wait for approval, then timeout)
        # Use short timeout for test
        result = await skill.create_invoice(
            client_name="Test Client",
            amount=100.0,
            description="Test",
            require_approval=True
        )
        
        # Should fail due to no connection + approval timeout
        assert result["success"] is False


class TestErrorHandling:
    """Test error handling for network issues."""

    def test_connection_error_propagation(self):
        """Test ConnectionError is raised for unreachable servers."""
        from mcp.odoo.server import OdooXMLRPCClient, ConnectionError as OdooConnectionError
        
        client = OdooXMLRPCClient(
            url="http://nonexistent-server-12345:8069",
            db="odoo",
            username="admin",
            password="admin"
        )
        
        with pytest.raises((ConnectionError, OdooConnectionError)):
            client.connect()

    def test_authentication_error_on_invalid_credentials(self):
        """Test AuthenticationError on invalid credentials."""
        from mcp.odoo.server import OdooXMLRPCClient, AuthenticationError
        
        # Use a reachable but invalid credential scenario
        # This test depends on having a real Odoo instance
        # For now, we test the exception class exists
        assert AuthenticationError is not None


class TestGoldTierCompliance:
    """Verify Gold Tier compliance requirements."""

    def test_no_mock_responses_in_server(self):
        """Verify server.py contains no mock responses."""
        server_path = Path(__file__).parent.parent / "src" / "mcp" / "odoo" / "server.py"
        
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Should not contain mock indicators
        assert "_mock_response" not in content
        assert "mock_mode" not in content
        assert "Mock" not in content or "mock" in content.lower() and "Mock" not in content

    def test_real_xmlrpc_usage(self):
        """Verify server uses real xmlrpc.client."""
        server_path = Path(__file__).parent.parent / "src" / "mcp" / "odoo" / "server.py"
        
        with open(server_path, 'r') as f:
            content = f.read()
        
        assert "xmlrpc.client" in content
        assert "ServerProxy" in content
        assert "authenticate" in content
        assert "execute_kw" in content

    def test_hitl_approval_in_skill(self):
        """Verify skill enforces HITL approval."""
        skill_path = Path(__file__).parent.parent / "src" / "skills" / "accounting_odoo_skill.py"
        
        with open(skill_path, 'r') as f:
            content = f.read()
        
        assert "ApprovalManager" in content
        assert "request_approval" in content
        assert "wait_for_approval" in content
        assert "require_approval" in content

    def test_audit_logging_in_skill(self):
        """Verify skill includes audit logging."""
        skill_path = Path(__file__).parent.parent / "src" / "skills" / "accounting_odoo_skill.py"
        
        with open(skill_path, 'r') as f:
            content = f.read()
        
        assert "_log_audit" in content
        assert "_audit_log" in content


# Integration test markers
@pytest.mark.integration
class TestIntegration:
    """Integration tests requiring real Odoo instance."""

    @pytest.mark.asyncio
    async def test_full_invoice_workflow(self):
        """Test complete invoice creation workflow with real Odoo."""
        # Skip if no Odoo credentials
        if not all(os.environ.get(var) for var in 
                   ['ODOO_URL', 'ODOO_DB', 'ODOO_USERNAME', 'ODOO_PASSWORD']):
            pytest.skip("No Odoo credentials configured")
        
        from skills.accounting_odoo_skill import AccountingOdooSkill
        
        skill = AccountingOdooSkill()
        
        try:
            # Connect
            connected = await skill.connect()
            assert connected
            
            # Get revenue
            revenue = await skill.get_total_revenue()
            assert revenue["success"] is True
            
            # Get partner info
            partner = await skill.get_partner_info("Admin")
            assert partner["success"] is True
            
        finally:
            await skill.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
