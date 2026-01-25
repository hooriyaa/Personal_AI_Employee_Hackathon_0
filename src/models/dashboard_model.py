"""
Dashboard entity model for the AI Employee system.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List
from .task_model import Task


@dataclass
class Dashboard:
    """
    A central status tracker showing the current state of tasks and system health
    """
    id: str  # Unique identifier
    tasks_summary: Dict[str, int]  # Summary of tasks by status
    last_updated: datetime  # When the dashboard was last updated
    content: str  # The Markdown content of the dashboard
    tasks: List[Task] = None  # References to multiple Task entities
    
    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []
            
        if self.last_updated is None:
            self.last_updated = datetime.now()
            
        # Validate tasks_summary keys
        valid_statuses = {"pending", "in-progress", "completed"}
        for status in self.tasks_summary.keys():
            if status not in valid_statuses:
                raise ValueError(f"Invalid status in tasks_summary: {status}. Must be one of: {valid_statuses}")