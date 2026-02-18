"""
Gold Tier Test: CEO Briefing Skill
===================================
Tests the CEO Briefing generation by creating dummy business data
and verifying the skill can generate a briefing report.
"""

import os
import shutil
from pathlib import Path

# Paths
VAULT_DIR = Path("vault")
BUSINESS_GOALS_FILE = VAULT_DIR / "Business_Goals.md"
BANK_TRANSACTIONS_FILE = VAULT_DIR / "Bank_Transactions.md"
BRIEFINGS_DIR = Path("Briefings")


def setup_dummy_data():
    """Create dummy business data for testing."""
    # Ensure vault directory exists
    VAULT_DIR.mkdir(exist_ok=True)
    
    # Create Business_Goals.md with $10,000 target
    business_goals_content = """---
type: business_goal
status: active
created: 2026-02-17
---

# Q1 2026 Business Goals

## Revenue Target
- **Target Revenue:** $10,000
- **Period:** Q1 2026 (Jan - Mar)
- **Status:** In Progress

## Key Objectives
1. Launch new product line
2. Expand LinkedIn presence
3. Close 5 enterprise deals
"""
    BUSINESS_GOALS_FILE.write_text(business_goals_content, encoding='utf-8')
    print(f"[OK] Created: {BUSINESS_GOALS_FILE}")
    
    # Create Bank_Transactions.md with $5,000 revenue
    bank_transactions_content = """---
type: bank_transactions
period: 2026-Q1
---

# Bank Transactions - Q1 2026

## Revenue
| Date | Description | Amount |
|------|-------------|--------|
| 2026-01-15 | Client A - Project Alpha | $2,000 |
| 2026-01-28 | Client B - Consulting | $1,500 |
| 2026-02-10 | Client C - License | $1,500 |

## Expenses
| Date | Description | Amount |
|------|-------------|--------|
| 2026-01-05 | Software Subscriptions | $200 |
| 2026-02-01 | Marketing Ads | $300 |

## Summary
- **Total Revenue:** $5,000
- **Total Expenses:** $500
- **Net Profit:** $4,500
"""
    BANK_TRANSACTIONS_FILE.write_text(bank_transactions_content, encoding='utf-8')
    print(f"[OK] Created: {BANK_TRANSACTIONS_FILE}")
    
    # Ensure Briefings directory exists
    BRIEFINGS_DIR.mkdir(exist_ok=True)


def run_gold_tier_test():
    """Run the Gold Tier CEO Briefing test."""
    print("=" * 60)
    print("GOLD TIER TEST: CEO Briefing Skill")
    print("=" * 60)
    print()
    
    # Setup dummy data
    print("Setting up test data...")
    setup_dummy_data()
    print()
    
    # Import and run the skill
    print("Importing CEOBriefingSkill...")
    from src.skills.ceo_briefing_skill import CEOBriefingSkill
    
    print("Initializing skill...")
    skill = CEOBriefingSkill()
    
    print("Generating CEO Briefing...")
    print("-" * 60)
    
    # Execute the skill
    result = skill.generate_briefing()
    
    print("-" * 60)
    print()
    
    # Parse and display results
    if result and result.get("success"):
        summary = result.get("summary", {})
        total_revenue = summary.get("total_revenue", 0)
        target_revenue = result.get("target_revenue", summary.get("target_revenue", 0))
        net_profit = summary.get("net_profit", 0)
        
        print("BRIEFING RESULTS:")
        print(f"  * Total Revenue Found: ${total_revenue:,.2f}")
        print(f"  * Net Profit:          ${net_profit:,.2f}")
        if target_revenue:
            print(f"  * Target Revenue:      ${target_revenue:,.2f}")
        print(f"  * Briefing Generated:  {result.get('briefing_path', 'N/A')}")
        print()
        
        # Verify the test - skill executed successfully
        print("[PASS] GOLD TIER TEST: CEO Briefing Skill executed successfully")
        print(f"       Revenue data extracted from vault: ${total_revenue:,.2f}")
    
    print()
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    try:
        run_gold_tier_test()
    except ImportError as e:
        print(f"[ERROR] IMPORT ERROR: {e}")
        print("   Make sure src/skills/__init__.py exists and exports CEOBriefingSkill")
    except Exception as e:
        print(f"[ERROR] TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
