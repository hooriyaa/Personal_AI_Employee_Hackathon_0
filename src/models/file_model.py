"""
File entity model for the AI Employee system.
"""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class File:
    """
    Represents a document dropped into the system, characterized by name, size, timestamp, and content
    """
    name: str
    size: int
    timestamp: datetime
    original_path: Path
    content: Optional[bytes] = None
    status: str = "pending"  # pending, in-progress, completed
    
    def __post_init__(self):
        if self.status not in ["pending", "in-progress", "completed"]:
            raise ValueError(f"Invalid status: {self.status}. Must be one of: pending, in-progress, completed")
        
        if self.size < 0:
            raise ValueError(f"Size must be a positive integer, got: {self.size}")