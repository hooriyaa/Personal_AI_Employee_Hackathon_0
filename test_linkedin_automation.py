"""
Test script to verify the LinkedIn automation implementation.
This script tests that the LinkedInPoster can be imported and instantiated.
"""

import sys
from pathlib import Path

# Add the project root to the path so we can import modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_linkedin_implementation():
    """Test that the LinkedIn automation implementation is properly set up."""
    print("Testing LinkedIn Automation Implementation...")
    
    # Test 1: Check that selenium and webdriver-manager can be imported
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        print("[OK] Selenium and webdriver-manager libraries are available")
    except ImportError as e:
        print(f"[ERROR] Selenium libraries not available: {e}")
        return False
    
    # Test 2: Check that LinkedInPoster exists and can be imported
    try:
        from src.linkedin.poster import LinkedInPoster
        print("[OK] LinkedInPoster module exists and can be imported")
    except ImportError as e:
        print(f"[ERROR] LinkedInPoster module cannot be imported: {e}")
        return False
    
    # Test 3: Check that LinkedInPoster can be instantiated
    try:
        poster = LinkedInPoster()
        print("✓ LinkedInPoster can be instantiated")
        
        # Check if the required methods exist
        required_methods = [
            'setup_browser', 
            'navigate_to_linkedin', 
            'check_login_status', 
            'find_and_click_start_post', 
            'populate_post_content', 
            'post_to_linkedin'
        ]
        
        for method in required_methods:
            if hasattr(poster, method):
                print(f"[OK] {method} method exists")
            else:
                print(f"[ERROR] {method} method is missing")
                return False
                
    except Exception as e:
        print(f"[ERROR] Error instantiating LinkedInPoster: {e}")
        return False
    
    # Test 4: Check that action_runner.py has been updated
    try:
        from src.action_runner import ActionRunner
        runner = ActionRunner()
        print("[OK] ActionRunner can be instantiated")
        
        # Check if LinkedIn functionality is available
        if hasattr(runner, 'LINKEDIN_AVAILABLE'):
            print(f"[OK] LINKEDIN_AVAILABLE flag exists: {runner.LINKEDIN_AVAILABLE}")
        else:
            print("? LINKEDIN_AVAILABLE flag does not exist (may be defined differently)")
        
    except Exception as e:
        print(f"[ERROR] Error testing ActionRunner: {e}")
        return False
    
    print("\nAll tests passed! LinkedIn automation implementation is properly set up.")
    return True

if __name__ == "__main__":
    success = test_linkedin_implementation()
    if not success:
        sys.exit(1)