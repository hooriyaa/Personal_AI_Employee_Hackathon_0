"""
Vault Read Skill for the AI Employee system.
"""
from pathlib import Path
from typing import Union, Dict, Any
import json


def read_from_vault(path: Union[str, Path], file_type: str = "string") -> Dict[str, Any]:
    """
    Read content from the vault at a specified path.
    
    Args:
        path: Path to the file to read
        file_type: Type of file to read ('string', 'markdown', 'binary')
    
    Returns:
        Dictionary with success status and content
    """
    try:
        file_path = Path(path)
        
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File does not exist: {path}"
            }
        
        if file_type.lower() == "binary":
            with open(file_path, 'rb') as f:
                content = f.read()
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
        return {
            "success": True,
            "content": content
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }