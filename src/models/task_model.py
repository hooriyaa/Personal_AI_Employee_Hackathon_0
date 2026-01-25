"""
Task entity model for the AI Employee system.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .file_model import File


@dataclass
class Task:
    """
    Represents a file that requires processing, with status (pending, in-progress, completed)
    """
    id: str  # Unique identifier (based on filename + timestamp)
    file_ref: File  # Reference to the associated File entity
    status: str = "pending"  # pending, in-progress, completed
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
            
        if self.status not in ["pending", "in-progress", "completed"]:
            raise ValueError(f"Invalid status: {self.status}. Must be one of: pending, in-progress, completed")
            
        if self.status == "completed" and self.completed_at is None:
            self.completed_at = datetime.now()