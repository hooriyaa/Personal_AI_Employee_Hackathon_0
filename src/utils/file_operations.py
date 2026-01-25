"""
Utility functions for file operations in the AI Employee system.
"""
import os
import time
from pathlib import Path
from typing import Optional


def wait_for_file_stability(file_path: Path, polling_interval: float = 1.0, confirmation_delay: float = 2.0) -> bool:
    """
    Wait for a file to be completely written by checking if its size remains stable.
    
    Args:
        file_path: Path to the file to check
        polling_interval: Time in seconds between size checks
        confirmation_delay: Time in seconds to wait before confirming stability
    
    Returns:
        True if file is stable, False if it doesn't exist or other error occurs
    """
    if not file_path.exists():
        return False
    
    initial_size = file_path.stat().st_size
    time.sleep(polling_interval)
    
    # Keep checking until the size stabilizes
    while True:
        current_size = file_path.stat().st_size
        
        if current_size == initial_size:
            # Wait for confirmation delay to ensure it stays stable
            time.sleep(confirmation_delay)
            final_check_size = file_path.stat().st_size
            
            if final_check_size == initial_size:
                # File size has remained stable through the confirmation period
                return True
            else:
                # File is still changing, update initial size and continue
                initial_size = final_check_size
        else:
            # File size changed, update initial size and continue
            initial_size = current_size
            time.sleep(polling_interval)


def move_file_with_timestamp(source_path: Path, dest_dir: Path) -> Path:
    """
    Move a file to destination directory, appending a timestamp if a file with the same name exists.
    
    Args:
        source_path: Path to the source file
        dest_dir: Destination directory
    
    Returns:
        Path to the moved file
    """
    dest_path = dest_dir / source_path.name
    
    # If file with same name exists, append timestamp
    if dest_path.exists():
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        stem = source_path.stem
        suffix = source_path.suffix
        new_filename = f"{stem}_{timestamp}{suffix}"
        dest_path = dest_dir / new_filename
    
    # Perform the move
    source_path.rename(dest_path)
    return dest_path


def create_metadata_trigger(file_info: dict, dest_dir: Path) -> Path:
    """
    Create a metadata trigger file with YAML frontmatter.
    
    Args:
        file_info: Dictionary containing file information (filename, size, timestamp, original_path)
        dest_dir: Destination directory for the trigger file
    
    Returns:
        Path to the created trigger file
    """
    import yaml
    from datetime import datetime
    
    # Create the YAML frontmatter
    yaml_frontmatter = yaml.dump({
        'filename': file_info.get('filename'),
        'size': file_info.get('size'),
        'timestamp': file_info.get('timestamp', datetime.now().isoformat()),
        'original_path': file_info.get('original_path')
    }, default_flow_style=False)
    
    # Create the trigger filename
    original_stem = Path(file_info.get('filename')).stem
    trigger_filename = f"{original_stem}_trigger.md"
    trigger_path = dest_dir / trigger_filename
    
    # Write the file with YAML frontmatter
    with open(trigger_path, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write(yaml_frontmatter)
        f.write("---\n\n")
        f.write("# File Processing Request\n\n")
        f.write(f"A new file has been detected and moved to Needs_Action for processing.\n")
    
    return trigger_path