from src.skills.social_media_skill import SocialMediaSkill
import os

# Fake Env Setup (Taake error na aaye)
os.environ["FB_PAGE_ACCESS_TOKEN"] = "fake_token"
os.environ["FB_PAGE_ID"] = "12345"

print("🤖 Agent: Creating a Facebook Post about 'New AI Employee'...")

try:
    skill = SocialMediaSkill()
    # Hum 'True' bhej rahe hain taake wo samjhe ke ye Draft hai
    result = skill.create_social_post(
        platform="facebook",
        content="Hello World! My AI Employee is live now! 🚀 #AI #Hackathon",
        require_approval=True 
    )
    print(result)
    print("\n✅ Check your 'Vault/Pending_Approval' folder now!")

except Exception as e:
    print(f"❌ Error: {e}")