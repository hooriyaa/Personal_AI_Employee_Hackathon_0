"""
Dashboard initialization and update functionality for the AI Employee system.
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def initialize_dashboard(dashboard_path: Path) -> None:
    """
    Initialize the dashboard file with default content if it doesn't exist.
    
    Args:
        dashboard_path: Path to the dashboard file
    """
    if not dashboard_path.exists():
        dashboard_content = """# AI Employee Dashboard

Welcome to your AI Employee dashboard. This file tracks the status of tasks processed by your AI employee.

## Task Summary

| Status | Count |
|--------|-------|
| Pending | 0 |
| In Progress | 0 |
| Completed | 0 |

## Recent Activity

- No recent activity
"""
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)


def update_dashboard_status(dashboard_path: Path, task_updates: Dict[str, Any]) -> None:
    """
    Update the dashboard with new task status information.
    
    Args:
        dashboard_path: Path to the dashboard file
        task_updates: Dictionary containing task updates
    """
    # Read the current dashboard content
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the task summary section
    # This is a simplified implementation - in a real system, you'd want to parse and update the markdown more carefully
    lines = content.split('\n')
    updated_lines = []
    
    # Find and update the task summary table
    in_task_summary = False
    for line in lines:
        if "| Status | Count |" in line:
            in_task_summary = True
            updated_lines.append(line)
        elif in_task_summary and line.strip() == "| Completed | 0 |":
            # This is where we'd update the counts based on actual data
            # For now, just add the update as a recent activity
            updated_lines.append(f"| Completed | {task_updates.get('completed_count', 0)} |")
            in_task_summary = False
        elif in_task_summary and line.startswith("|"):
            # Skip the old counts, we'll update them properly
            continue
        elif "## Recent Activity" in line:
            # Add the new activity to the recent activity section
            updated_lines.append(line)
            updated_lines.append("")
            updated_lines.append(f"- {task_updates.get('activity', 'New activity')} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            updated_lines.append(line)
    
    # Write the updated content back to the dashboard
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(updated_lines))