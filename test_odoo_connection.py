import xmlrpc.client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("ODOO_URL")
db = os.getenv("ODOO_DB")
username = os.getenv("ODOO_USERNAME")
password = os.getenv("ODOO_PASSWORD")

print(f"Connecting to {url}...")

try:
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    
    if uid:
        print(f"✅ SUCCESS! Connected to Odoo. User ID: {uid}")
        
        # Check permissions
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        partner_count = models.execute_kw(db, uid, password, 'res.partner', 'search_count', [[]])
        print(f"📊 Found {partner_count} partners (customers) in the database.")
    else:
        print("❌ Login Failed. Check username/password in .env")

except Exception as e:
    print(f"❌ Connection Error: {e}")