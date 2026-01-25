"""
Task Completion Skill for the AI Employee system.
"""
from pathlib import Path
from typing import Dict, Any


def move_to_done(source_path: str, destination_folder: str = "./vault/Done/", preserve_original: bool = False) -> Dict[str, Any]:
    """
    Move a processed file from Needs_Action to Done folder.
    
    Args:
        source_path: Path to the source file
        destination_folder: Destination folder for completed files (default: './vault/Done/')
        preserve_original: Whether to preserve the original file (default: False)
    
    Returns:
        Dictionary with success status and moved file path
    """
    try:
        source_file = Path(source_path)
        dest_dir = Path(destination_folder)
        
        # Create destination directory if it doesn't exist
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Create destination path
        dest_path = dest_dir / source_file.name
        
        # Handle duplicate filenames by appending timestamp
        if dest_path.exists():
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            stem = source_file.stem
            suffix = source_file.suffix
            new_filename = f"{stem}_{timestamp}{suffix}"
            dest_path = dest_dir / new_filename
        
        if preserve_original:
            # Copy the file instead of moving
            import shutil
            shutil.copy2(source_file, dest_path)
        else:
            # Move the file
            source_file.rename(dest_path)
        
        return {
            "success": True,
            "moved_file_path": str(dest_path)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }