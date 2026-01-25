"""
Vault Write Skill for the AI Employee system.
"""
from pathlib import Path
from typing import Dict, Any


def write_to_vault(path: str, content: str, mode: str = "overwrite") -> Dict[str, Any]:
    """
    Write content to a specified path in the vault.
    
    Args:
        path: Path where content should be written
        content: Content to write
        mode: Write mode ('overwrite', 'append')
    
    Returns:
        Dictionary with success status and message
    """
    try:
        file_path = Path(path)
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if mode.lower() == "append":
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
        else:  # overwrite
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        return {
            "success": True,
            "message": f"Successfully wrote to {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }