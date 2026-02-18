"""
CEO Briefing Skill - Generates the "Monday Morning CEO Briefing".

This skill:
- Reads Business_Goals.md and Bank_Transactions.md (mock data sources)
- Calculates "Total Revenue" and identifies "Bottlenecks"
- Generates a comprehensive Markdown report in Vault/Briefings/

Designed for weekly executive summaries and strategic insights.
"""

import json
import logging
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

# Handle import when running as standalone script vs module
try:
    from src.config.settings import VAULT_PATH
except ImportError:
    # Add parent directory to path for standalone execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.config.settings import VAULT_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CEOBriefingSkill:
    """
    Skill for generating executive CEO briefings.
    
    Produces comprehensive weekly reports covering:
    - Business performance metrics
    - Revenue analysis
    - Bottleneck identification
    - Goal progress tracking
    - Actionable recommendations
    """
    
    def __init__(self, vault_path: Optional[Path] = None):
        """
        Initialize the CEO briefing skill.
        
        Args:
            vault_path: Base vault directory path
        """
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            # VAULT_PATH from settings may be a string, ensure it's a Path
            self.vault_path = Path(VAULT_PATH) if isinstance(VAULT_PATH, str) else VAULT_PATH
        self.briefings_dir = self.vault_path / "Briefings"
        
        # Ensure briefings directory exists
        self.briefings_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock data sources (would connect to actual systems in production)
        self.business_goals_file = self.vault_path / "Business_Goals.md"
        self.bank_transactions_file = self.vault_path / "Bank_Transactions.md"
        
        # Briefing templates and variability options
        self.greeting_options = [
            "Good morning",
            "Welcome to your weekly briefing",
            "Here's your executive summary",
            "Your Monday morning briefing is ready"
        ]
        
        self.tone_options = [
            "professional",
            "encouraging",
            "data-driven",
            "action-oriented"
        ]
    
    def _read_business_goals(self) -> Dict[str, Any]:
        """
        Read business goals from file.
        
        Returns:
            Dictionary of business goals and their status
        """
        # Mock implementation - reads from file if exists, otherwise returns mock data
        if self.business_goals_file.exists():
            try:
                with open(self.business_goals_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Parse markdown content (simplified)
                return self._parse_goals_markdown(content)
            except Exception as e:
                logger.warning(f"Could not read business goals: {e}")
        
        # Return mock business goals
        return {
            "goals": [
                {
                    "id": 1,
                    "title": "Q1 Revenue Target",
                    "description": "Achieve $500K in Q1 2026 revenue",
                    "target_value": 500000,
                    "current_value": 375000,
                    "unit": "USD",
                    "deadline": "2026-03-31",
                    "status": "on_track",
                    "priority": "high"
                },
                {
                    "id": 2,
                    "title": "Customer Acquisition",
                    "description": "Onboard 100 new enterprise customers",
                    "target_value": 100,
                    "current_value": 67,
                    "unit": "customers",
                    "deadline": "2026-03-31",
                    "status": "at_risk",
                    "priority": "high"
                },
                {
                    "id": 3,
                    "title": "Product Launch",
                    "description": "Launch AI Employee v2.0",
                    "target_value": 1,
                    "current_value": 0.8,
                    "unit": "release",
                    "deadline": "2026-02-28",
                    "status": "on_track",
                    "priority": "critical"
                },
                {
                    "id": 4,
                    "title": "Team Expansion",
                    "description": "Hire 5 senior engineers",
                    "target_value": 5,
                    "current_value": 2,
                    "unit": "employees",
                    "deadline": "2026-04-30",
                    "status": "behind",
                    "priority": "medium"
                }
            ],
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }
    
    def _parse_goals_markdown(self, content: str) -> Dict[str, Any]:
        """Parse business goals from markdown content."""
        # Simplified parser - would be more robust in production
        goals = []
        lines = content.split('\n')
        current_goal = {}
        
        for line in lines:
            if line.startswith('## '):
                if current_goal:
                    goals.append(current_goal)
                current_goal = {"title": line[3:].strip()}
            elif line.startswith('- '):
                parts = line[2:].split(':')
                if len(parts) == 2:
                    key = parts[0].strip().lower().replace(' ', '_')
                    value = parts[1].strip()
                    current_goal[key] = value
        
        if current_goal:
            goals.append(current_goal)
        
        return {"goals": goals, "last_updated": datetime.now().strftime("%Y-%m-%d")}
    
    def _read_bank_transactions(self) -> Dict[str, Any]:
        """
        Read bank transactions from file.
        
        Returns:
            Dictionary of transactions and financial data
        """
        # Mock implementation - reads from file if exists, otherwise returns mock data
        if self.bank_transactions_file.exists():
            try:
                with open(self.bank_transactions_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                return self._parse_transactions_markdown(content)
            except Exception as e:
                logger.warning(f"Could not read bank transactions: {e}")
        
        # Generate mock transactions for the past week
        today = datetime.now()
        transactions = []
        
        # Mock revenue transactions
        revenue_sources = [
            ("Acme Corp", 15000, "Invoice payment - Consulting services"),
            ("TechStart Inc", 8500, "Monthly subscription - Enterprise plan"),
            ("Global Solutions", 22000, "Project milestone payment"),
            ("Innovation Labs", 5000, "Product license renewal"),
            ("Digital Dynamics", 12000, "Custom development work"),
            ("Smart Systems", 18000, "Q1 retainer payment"),
            ("Future Tech", 9500, "Training and onboarding services"),
        ]
        
        # Mock expense transactions
        expense_categories = [
            ("AWS Cloud Services", 3200, "Monthly cloud infrastructure"),
            ("Office Rent", 4500, "February 2026 rent"),
            ("Payroll", 45000, "Bi-weekly payroll"),
            ("Software Licenses", 1800, "Development tools and SaaS"),
            ("Marketing", 5000, "Digital advertising campaign"),
            ("Utilities", 800, "Office utilities"),
        ]
        
        # Generate transactions over the past 7 days
        for i, (client, amount, desc) in enumerate(revenue_sources):
            days_ago = random.randint(0, 6)
            tx_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            transactions.append({
                "id": f"TXN_IN_{1000 + i}",
                "date": tx_date,
                "type": "credit",
                "amount": amount,
                "counterparty": client,
                "description": desc,
                "category": "revenue",
                "status": "completed"
            })
        
        for i, (vendor, amount, desc) in enumerate(expense_categories):
            days_ago = random.randint(0, 6)
            tx_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            transactions.append({
                "id": f"TXN_OUT_{2000 + i}",
                "date": tx_date,
                "type": "debit",
                "amount": amount,
                "counterparty": vendor,
                "description": desc,
                "category": "expense",
                "status": "completed"
            })
        
        # Sort by date
        transactions.sort(key=lambda x: x['date'], reverse=True)
        
        return {
            "transactions": transactions,
            "currency": "USD",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _parse_transactions_markdown(self, content: str) -> Dict[str, Any]:
        """Parse bank transactions from markdown content."""
        transactions = []
        lines = content.split('\n')
        
        for line in lines:
            if line.startswith('|') and 'date' not in line.lower():
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 5:
                    transactions.append({
                        "id": f"TXN_{len(transactions)}",
                        "date": parts[0],
                        "type": "credit" if "+" in parts[2] or parts[1] == "credit" else "debit",
                        "amount": float(parts[2].replace('$', '').replace('+', '').replace('-', '')),
                        "counterparty": parts[3],
                        "description": parts[4],
                        "category": "revenue" if "credit" in line.lower() else "expense",
                        "status": "completed"
                    })
        
        return {
            "transactions": transactions,
            "currency": "USD",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _calculate_total_revenue(self, transactions: Dict[str, Any],
                                  days: int = 7) -> Dict[str, Any]:
        """
        Calculate total revenue for a specified period.
        
        Args:
            transactions: Transaction data dictionary
            days: Number of days to calculate for
            
        Returns:
            Revenue calculation results
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        revenue_transactions = [
            tx for tx in transactions.get('transactions', [])
            if tx.get('type') == 'credit' and tx.get('status') == 'completed'
        ]
        
        # Filter by date
        recent_revenue = []
        for tx in revenue_transactions:
            try:
                tx_date = datetime.strptime(tx['date'], "%Y-%m-%d")
                if tx_date >= cutoff_date:
                    recent_revenue.append(tx)
            except (ValueError, KeyError):
                continue
        
        total_revenue = sum(tx.get('amount', 0) for tx in recent_revenue)
        total_expenses = sum(
            tx.get('amount', 0) for tx in transactions.get('transactions', [])
            if tx.get('type') == 'debit' and tx.get('status') == 'completed'
        )
        
        # Calculate net profit
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Top revenue sources
        top_sources = sorted(recent_revenue, key=lambda x: x.get('amount', 0), reverse=True)[:5]
        
        return {
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_profit": net_profit,
            "profit_margin": round(profit_margin, 2),
            "transaction_count": len(recent_revenue),
            "period_days": days,
            "top_sources": top_sources,
            "currency": transactions.get('currency', 'USD')
        }
    
    def _identify_bottlenecks(self, goals: Dict[str, Any],
                               revenue: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify business bottlenecks and areas of concern.
        
        Args:
            goals: Business goals data
            revenue: Revenue analysis data
            
        Returns:
            List of identified bottlenecks with severity and recommendations
        """
        bottlenecks = []
        
        # Analyze goal progress
        for goal in goals.get('goals', []):
            progress = (goal.get('current_value', 0) / goal.get('target_value', 1)) * 100
            
            # Check if goal is behind
            if goal.get('status') == 'behind' or progress < 50:
                bottlenecks.append({
                    "id": f"BTL_{goal.get('id', 0)}",
                    "type": "goal_delay",
                    "severity": "high" if goal.get('priority') == 'critical' else "medium",
                    "title": f"Goal Behind: {goal.get('title')}",
                    "description": f"Progress at {progress:.1f}% - {goal.get('description')}",
                    "impact": f"Risk of missing {goal.get('deadline')} deadline",
                    "recommendation": self._generate_goal_recommendation(goal, progress)
                })
            elif goal.get('status') == 'at_risk':
                bottlenecks.append({
                    "id": f"BTL_{goal.get('id', 0)}",
                    "type": "goal_at_risk",
                    "severity": "medium",
                    "title": f"Goal At Risk: {goal.get('title')}",
                    "description": f"Progress at {progress:.1f}% - {goal.get('description')}",
                    "impact": f"May miss {goal.get('deadline')} deadline without intervention",
                    "recommendation": self._generate_goal_recommendation(goal, progress)
                })
        
        # Revenue-based bottlenecks
        if revenue.get('profit_margin', 100) < 20:
            bottlenecks.append({
                "id": "BTL_PROFIT",
                "type": "low_margin",
                "severity": "high",
                "title": "Low Profit Margin",
                "description": f"Current profit margin is {revenue.get('profit_margin', 0)}%",
                "impact": "Reduced cash flow and growth capacity",
                "recommendation": "Review pricing strategy and reduce operational costs"
            })
        
        # Add generic bottlenecks based on patterns
        if len(revenue.get('top_sources', [])) < 3:
            bottlenecks.append({
                "id": "BTL_CONCENTRATION",
                "type": "revenue_concentration",
                "severity": "medium",
                "title": "Revenue Concentration Risk",
                "description": "Revenue dependent on few clients",
                "impact": "High risk if major client churns",
                "recommendation": "Diversify client base and develop new revenue streams"
            })
        
        return bottlenecks
    
    def _generate_goal_recommendation(self, goal: Dict[str, Any],
                                       progress: float) -> str:
        """Generate specific recommendation for a goal."""
        priority = goal.get('priority', 'medium')
        deadline = goal.get('deadline', 'unknown')
        
        if progress < 30:
            return f"Immediate action required: Allocate additional resources to accelerate progress toward {goal.get('title')}"
        elif progress < 60:
            return f"Schedule review meeting to identify blockers and create acceleration plan for {goal.get('title')}"
        else:
            return f"Maintain current momentum and monitor weekly to ensure {deadline} deadline is met"
    
    def generate_briefing(self, period: str = "weekly",
                           include_recommendations: bool = True) -> Dict[str, Any]:
        """
        Generate the complete CEO briefing report.
        
        Args:
            period: Reporting period ('daily', 'weekly', 'monthly')
            include_recommendations: Whether to include AI recommendations
            
        Returns:
            Complete briefing data and file path
        """
        # Gather data
        goals_data = self._read_business_goals()
        transactions_data = self._read_bank_transactions()
        
        # Calculate metrics
        days = 7 if period == "weekly" else 30 if period == "monthly" else 1
        revenue_data = self._calculate_total_revenue(transactions_data, days)
        
        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(goals_data, revenue_data)
        
        # Generate briefing document
        briefing_date = datetime.now()
        filename = f"CEO_Briefing_{briefing_date.strftime('%Y-%m-%d')}.md"
        file_path = self.briefings_dir / filename
        
        # Generate markdown content
        markdown_content = self._generate_briefing_markdown(
            date=briefing_date,
            period=period,
            goals=goals_data,
            revenue=revenue_data,
            bottlenecks=bottlenecks,
            include_recommendations=include_recommendations
        )
        
        # Write briefing file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Generated CEO briefing: {file_path}")
        
        return {
            "success": True,
            "briefing_path": str(file_path),
            "date": briefing_date.strftime("%Y-%m-%d"),
            "period": period,
            "summary": {
                "total_revenue": revenue_data['total_revenue'],
                "net_profit": revenue_data['net_profit'],
                "goals_on_track": sum(1 for g in goals_data['goals'] if g.get('status') == 'on_track'),
                "goals_total": len(goals_data['goals']),
                "bottlenecks_identified": len(bottlenecks)
            }
        }
    
    def _generate_briefing_markdown(self, date: datetime, period: str,
                                     goals: Dict[str, Any],
                                     revenue: Dict[str, Any],
                                     bottlenecks: List[Dict[str, Any]],
                                     include_recommendations: bool) -> str:
        """Generate the markdown briefing document."""
        
        # Select random greeting for variety
        greeting = random.choice(self.greeting_options)
        
        # Calculate goal progress summary
        goals_on_track = sum(1 for g in goals['goals'] if g.get('status') == 'on_track')
        goals_total = len(goals['goals'])
        
        markdown = f"""---
type: ceo_briefing
period: {period}
generated_at: {date.isoformat()}
generated_by: AI_Employee
---

# {greeting}, CEO

## Executive Summary - {period.title()} Briefing
**Generated:** {date.strftime("%A, %B %d, %Y at %I:%M %p")}

---

## 📊 Financial Performance

### Revenue Overview ({period})
| Metric | Value |
|--------|-------|
| **Total Revenue** | ${revenue['total_revenue']:,.2f} |
| **Total Expenses** | ${revenue['total_expenses']:,.2f} |
| **Net Profit** | ${revenue['net_profit']:,.2f} |
| **Profit Margin** | {revenue['profit_margin']:.1f}% |
| **Transactions** | {revenue['transaction_count']} |

### Top Revenue Sources
"""
        
        # Add top revenue sources table
        for i, source in enumerate(revenue.get('top_sources', [])[:5], 1):
            markdown += f"| {i}. {source.get('counterparty', 'Unknown')} | ${source.get('amount', 0):,.2f} | {source.get('description', '')} |\n"
        
        if not revenue.get('top_sources'):
            markdown += "| - | No revenue data available | - |\n"
        
        markdown += f"""
---

## 🎯 Business Goals Progress

### Overview
- **Goals On Track:** {goals_on_track}/{goals_total}
- **Completion Rate:** {(goals_on_track/goals_total*100) if goals_total > 0 else 0:.0f}%

### Goal Details
"""
        
        # Add goal details
        for goal in goals.get('goals', []):
            progress = (goal.get('current_value', 0) / goal.get('target_value', 1)) * 100
            status_emoji = "✅" if goal.get('status') == 'on_track' else "⚠️" if goal.get('status') == 'at_risk' else "🔴"
            
            markdown += f"""
#### {status_emoji} {goal.get('title')}
- **Progress:** {goal.get('current_value', 0)}/{goal.get('target_value', 1)} {goal.get('unit', '')} ({progress:.1f}%)
- **Deadline:** {goal.get('deadline', 'N/A')}
- **Priority:** {goal.get('priority', 'medium').upper()}
- **Status:** {goal.get('status', 'unknown').replace('_', ' ').title()}
"""
        
        markdown += f"""
---

## 🚨 Bottlenecks & Areas of Concern

### Identified Issues ({len(bottlenecks)})
"""
        
        # Add bottlenecks
        if bottlenecks:
            for btl in bottlenecks:
                severity_emoji = "🔴" if btl.get('severity') == 'high' else "🟡"
                markdown += f"""
#### {severity_emoji} {btl.get('title')}
- **Type:** {btl.get('type', 'unknown').replace('_', ' ').title()}
- **Description:** {btl.get('description', 'N/A')}
- **Impact:** {btl.get('impact', 'N/A')}
"""
                if include_recommendations and btl.get('recommendation'):
                    markdown += f"- **Recommendation:** {btl.get('recommendation')}\n"
        else:
            markdown += "\n✅ No critical bottlenecks identified at this time.\n"
        
        # Add AI recommendations section
        if include_recommendations:
            markdown += f"""
---

## 💡 AI Recommendations

### Priority Actions for This Week

1. **Revenue Optimization**
   - Review pricing strategy for underperforming services
   - Follow up on pending invoices from top clients
   - Explore upselling opportunities with existing customers

2. **Goal Acceleration**
   - Schedule focused review sessions for at-risk goals
   - Reallocate resources to critical priority items
   - Consider delegating non-essential tasks

3. **Operational Efficiency**
   - Automate recurring manual processes
   - Review and optimize expense categories
   - Implement weekly progress tracking rituals

---
"""
        
        markdown += f"""
## 📅 Next Review

**Next Briefing:** {date.strftime("%A, %B %d, %Y")}
**Focus Areas:** Revenue growth, Goal acceleration, Bottleneck resolution

---

*This briefing was automatically generated by your AI Employee.*
*For questions or adjustments, please provide feedback.*
"""
        
        return markdown


# Convenience functions for direct import and use
def generate_ceo_briefing(period: str = "weekly") -> Dict[str, Any]:
    """
    Generate the Monday Morning CEO Briefing.
    
    Args:
        period: Reporting period ('daily', 'weekly', 'monthly')
        
    Returns:
        Briefing generation result dictionary
    """
    skill = CEOBriefingSkill()
    return skill.generate_briefing(period)


def get_business_goals() -> Dict[str, Any]:
    """Read and return business goals."""
    skill = CEOBriefingSkill()
    return skill._read_business_goals()


def get_financial_summary(days: int = 7) -> Dict[str, Any]:
    """Get financial summary for specified period."""
    skill = CEOBriefingSkill()
    transactions = skill._read_bank_transactions()
    return skill._calculate_total_revenue(transactions, days)


# Example usage and testing
if __name__ == "__main__":
    print("Testing CEO Briefing Skill...")
    print("-" * 50)
    
    # Test briefing generation
    print("\n1. Generating weekly CEO briefing...")
    briefing_result = generate_ceo_briefing(period="weekly")
    print(f"   Result: {json.dumps(briefing_result, indent=2, default=str)}")
    
    # Test business goals read
    print("\n2. Reading business goals...")
    goals = get_business_goals()
    print(f"   Found {len(goals.get('goals', []))} goals")
    
    # Test financial summary
    print("\n3. Getting financial summary...")
    financials = get_financial_summary(days=7)
    print(f"   Total Revenue: ${financials.get('total_revenue', 0):,.2f}")
    print(f"   Net Profit: ${financials.get('net_profit', 0):,.2f}")
    
    print("\n" + "-" * 50)
    print(f"Briefing saved to: {briefing_result.get('briefing_path', 'N/A')}")
