"""
Odoo MCP Server Package - Gold Tier Accounting Integration.

This package provides production-ready Odoo ERP integration via MCP.
"""

from .server import OdooMCPServer, OdooXMLRPCClient, main

__all__ = ["OdooMCPServer", "OdooXMLRPCClient", "main"]
