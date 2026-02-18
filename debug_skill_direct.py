from src.skills.accounting_odoo_skill import AccountingOdooSkill
import logging
import sys

# Logging on karein taake pata chale kahan atka hai
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

print("🚀 Step 1: Initializing Skill...")
try:
    skill = AccountingOdooSkill()
    print("✅ Skill Initialized!")
except Exception as e:
    print(f"❌ Init Error: {e}")
    exit()

print("📧 Step 2: Calling create_invoice function directly...")
try:
    # Hum seedha function call kar rahe hain (No Async, No Runner)
    result = skill.create_invoice(
        customer="Debug Client",
        amount=999.0,
        description="Direct Debug Test"
    )
    print(f"🎉 SUCCESS! Function returned: {result}")
except Exception as e:
    print(f"❌ Function Error: {e}")