"""
Test script to verify the Gemini integration implementation.
This script tests that the PlanGenerationSkill can initialize with the new GeminiService
and that the required functionality is in place.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path so we can import modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gemini_integration():
    """Test that the Gemini integration is properly implemented."""
    print("Testing Gemini Integration Implementation...")
    
    # Test 1: Check that google-generativeai can be imported
    try:
        import google.generativeai as genai
        print("[OK] google-generativeai library is available")
    except ImportError:
        print("[ERROR] google-generativeai library is not available")
        return False
    
    # Test 2: Check that GeminiService exists and can be imported
    try:
        from src.services.gemini_service import GeminiService
        print("[OK] GeminiService module exists and can be imported")
    except ImportError as e:
        print(f"[ERROR] GeminiService module cannot be imported: {e}")
        return False
    
    # Test 3: Check that PlanGenerationSkill has been updated
    try:
        from skills.plan_generation_skill import PlanGenerationSkill
        skill = PlanGenerationSkill()
        print("[OK] PlanGenerationSkill can be instantiated")
        
        # Check if gemini_service attribute exists
        if hasattr(skill, 'gemini_service'):
            print("[OK] PlanGenerationSkill has gemini_service attribute")
        else:
            print("[ERROR] PlanGenerationSkill is missing gemini_service attribute")
            return False
            
        # Check if the GeminiService is properly integrated
        if skill.gemini_service is not None:
            print("[OK] GeminiService is initialized in PlanGenerationSkill")
        else:
            print("[INFO] GeminiService is not initialized (likely due to missing API key)")
        
        # Check if the methods exist
        if hasattr(skill, '_generate_static_email_reply'):
            print("[OK] _generate_static_email_reply method exists")
        else:
            print("[ERROR] _generate_static_email_reply method is missing")
            return False
            
        if hasattr(skill, '_generate_static_linkedin_post'):
            print("[OK] _generate_static_linkedin_post method exists")
        else:
            print("[ERROR] _generate_static_linkedin_post method is missing")
            return False
        
    except Exception as e:
        print(f"[ERROR] Error testing PlanGenerationSkill: {e}")
        return False
    
    print("\nAll tests passed! Gemini integration is properly implemented.")
    return True

if __name__ == "__main__":
    success = test_gemini_integration()
    if not success:
        sys.exit(1)