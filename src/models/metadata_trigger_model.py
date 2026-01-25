"""
MetadataTrigger entity model for the AI Employee system.
"""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class MetadataTrigger:
    """
    A Markdown file containing information about a file that needs processing
    """
    id: str  # Unique identifier
    filename: str  # The name of the original file
    size: int  # Size of the original file in bytes
    timestamp: datetime  # When the file was detected
    original_path: Path  # Path of the original file in the vault
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
            
        if self.size < 0:
            raise ValueError(f"Size must be a positive integer, got: {self.size}")