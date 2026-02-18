import os
import xmlrpc.client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("ODOO_URL")
db = os.getenv("ODOO_DB")
username = os.getenv("ODOO_USERNAME")
password = os.getenv("ODOO_PASSWORD")

print(f"🔍 Connecting to Odoo at: {url}")
print(f"👤 User: {username}")
print(f"🗄️  Database: {db}")

try:
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    print("⏳ Authenticating...")
    uid = common.authenticate(db, username, password, {})
    
    if uid:
        print(f"✅ SUCCESS! Connected with UID: {uid}")
        
        # Try Creating Invoice Directly
        print("🧾 Attempting to create invoice...")
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        
        # 1. Find/Create Partner
        partner_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{'name': 'Debug Client'}])
        print(f"👤 Partner ID: {partner_id}")
        
        # 2. Create Invoice
        invoice_id = models.execute_kw(db, uid, password, 'account.move', 'create', [{
            'move_type': 'out_invoice',
            'partner_id': partner_id,
            'invoice_date': '2026-02-18',
            'invoice_line_ids': [(0, 0, {'name': 'Test Service', 'price_unit': 100.0})],
        }])
        print(f"🎉 INVOICE CREATED! ID: {invoice_id}")
        
    else:
        print("❌ Login Failed. Check Password/Username.")

except Exception as e:
    print(f"❌ CONNECTION ERROR: {e}")