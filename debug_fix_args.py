import inspect
from src.skills.accounting_odoo_skill import AccountingOdooSkill
import sys

print("🔍 Inspecting function arguments...")

try:
    skill = AccountingOdooSkill()
    # Check what arguments the function REALLY wants
    sig = inspect.signature(skill.create_invoice)
    print(f"📋 FUNCTION EXPECTS: {sig}")

    print("\n🧪 Attempting Fix 1: Using 'client_name'...")
    try:
        # Try with 'client_name' instead of 'customer'
        result = skill.create_invoice(
            client_name="Debug Client", 
            amount=550.0, 
            description="Fixed Args Test"
        )
        print(f"✅ SUCCESS! Invoice Created: {result}")
        
    except TypeError as e:
        print(f"⚠️ 'client_name' failed: {e}")
        
        print("\n🧪 Attempting Fix 2: Using 'partner_name'...")
        try:
            result = skill.create_invoice(
                partner_name="Debug Client", 
                amount=550.0, 
                description="Fixed Args Test"
            )
            print(f"✅ SUCCESS! Invoice Created: {result}")
        except Exception as e:
             print(f"❌ Fix 2 Failed: {e}")

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")