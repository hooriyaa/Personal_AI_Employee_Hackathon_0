"""
Utility functions for file operations and path management.

This module provides common utility functions used throughout the application,
particularly for file operations, path management, and other helper functions.
"""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
import logging


def ensure_directory_exists(path):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path (str or Path): Path to the directory
        
    Returns:
        Path: The directory path as a Path object
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def move_file(source, destination, overwrite=False):
    """
    Move a file from source to destination.

    Args:
        source (str or Path): Source file path
        destination (str or Path): Destination file path
        overwrite (bool): Whether to overwrite if destination exists

    Returns:
        bool: True if successful, False otherwise
    """
    source_path = Path(source)
    dest_path = Path(destination)

    if not source_path.exists():
        logging.error(f"Source file does not exist: {source_path}")
        return False

    if dest_path.exists() and not overwrite:
        logging.error(f"Destination file exists and overwrite is False: {dest_path}")
        return False

    try:
        # Ensure destination directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # If destination exists and overwrite is True, delete it first
        if dest_path.exists() and overwrite:
            os.remove(str(dest_path))
            logging.info(f"Deleted existing destination file: {dest_path}")

        # Move the file
        shutil.move(str(source_path), str(dest_path))
        logging.info(f"Moved file from {source_path} to {dest_path}")
        return True
    except Exception as e:
        logging.error(f"Error moving file: {e}")
        return False


def copy_file(source, destination, overwrite=False):
    """
    Copy a file from source to destination.
    
    Args:
        source (str or Path): Source file path
        destination (str or Path): Destination file path
        overwrite (bool): Whether to overwrite if destination exists
        
    Returns:
        bool: True if successful, False otherwise
    """
    source_path = Path(source)
    dest_path = Path(destination)
    
    if not source_path.exists():
        logging.error(f"Source file does not exist: {source_path}")
        return False
    
    if dest_path.exists() and not overwrite:
        logging.error(f"Destination file exists and overwrite is False: {dest_path}")
        return False
    
    try:
        # Ensure destination directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the file
        shutil.copy2(str(source_path), str(dest_path))
        logging.info(f"Copied file from {source_path} to {dest_path}")
        return True
    except Exception as e:
        logging.error(f"Error copying file: {e}")
        return False


def get_file_checksum(filepath, algorithm='sha256'):
    """
    Calculate the checksum of a file.
    
    Args:
        filepath (str or Path): Path to the file
        algorithm (str): Hash algorithm to use (default: sha256)
        
    Returns:
        str: Hex digest of the file checksum
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File does not exist: {filepath}")
    
    hash_func = hashlib.new(algorithm)
    
    with open(filepath, 'rb') as f:
        # Read file in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def get_file_metadata(filepath):
    """
    Get metadata for a file.
    
    Args:
        filepath (str or Path): Path to the file
        
    Returns:
        dict: Dictionary containing file metadata
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File does not exist: {filepath}")
    
    stat = filepath.stat()
    
    return {
        'name': filepath.name,
        'path': str(filepath),
        'size_bytes': stat.st_size,
        'created': datetime.fromtimestamp(stat.st_ctime),
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'accessed': datetime.fromtimestamp(stat.st_atime),
        'checksum_sha256': get_file_checksum(filepath, 'sha256')
    }


def find_files(directory, pattern="*", recursive=True):
    """
    Find files in a directory matching a pattern.
    
    Args:
        directory (str or Path): Directory to search in
        pattern (str): Pattern to match (supports wildcards)
        recursive (bool): Whether to search recursively
        
    Returns:
        list: List of matching file paths
    """
    directory = Path(directory)
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"Directory does not exist or is not a directory: {directory}")
    
    if recursive:
        return list(directory.rglob(pattern))
    else:
        return list(directory.glob(pattern))


def create_unique_filename(base_path, extension=None, max_attempts=100):
    """
    Create a unique filename by appending a counter if the file exists.
    
    Args:
        base_path (str or Path): Base path for the file
        extension (str): File extension (if not included in base_path)
        max_attempts (int): Maximum number of attempts to find a unique name
        
    Returns:
        Path: Unique file path
    """
    base_path = Path(base_path)
    
    # If extension is provided and not in base_path, add it
    if extension and not base_path.suffix:
        base_path = base_path.with_suffix(extension)
    
    # If the file doesn't exist, return as is
    if not base_path.exists():
        return base_path
    
    # Try appending numbers until we find a unique name
    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent
    
    for i in range(1, max_attempts + 1):
        new_path = parent / f"{stem}_{i}{suffix}"
        if not new_path.exists():
            return new_path
    
    # If we couldn't find a unique name, raise an exception
    raise RuntimeError(f"Could not create a unique filename after {max_attempts} attempts")


def format_file_size(size_bytes):
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Human-readable file size
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def is_subpath(child, parent):
    """
    Check if child path is a subpath of parent path.
    
    Args:
        child (str or Path): Child path to check
        parent (str or Path): Parent path to check against
        
    Returns:
        bool: True if child is a subpath of parent, False otherwise
    """
    child_path = Path(child).resolve()
    parent_path = Path(parent).resolve()
    
    try:
        child_path.relative_to(parent_path)
        return True
    except ValueError:
        return False


def sanitize_filename(filename):
    """
    Sanitize a filename by removing or replacing invalid characters.
    
    Args:
        filename (str): Filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters for most file systems
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove control characters
    filename = ''.join(c for c in filename if ord(c) >= 32)
    
    # Limit length (most file systems limit to 255 characters)
    if len(filename) > 250:  # Leave some room for extension
        name, ext = os.path.splitext(filename)
        filename = name[:250-len(ext)] + ext
    
    return filename


# Example usage and testing
if __name__ == "__main__":
    # Example usage of utility functions
    print("Utility functions loaded successfully.")
    
    # Test creating a unique filename
    try:
        unique_path = create_unique_filename("./test_file.txt")
        print(f"Unique filename: {unique_path}")
    except RuntimeError as e:
        print(f"Error creating unique filename: {e}")
    
    # Test sanitizing a filename
    dirty_name = 'invalid<file>:name?.txt'
    clean_name = sanitize_filename(dirty_name)
    print(f"Sanitized filename: '{dirty_name}' -> '{clean_name}'")