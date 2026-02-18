"""
File Manager Skill - Core Agent Skill for vault file operations.

This skill provides safe read/write/list operations for the Obsidian vault
and other project directories. It follows the hackathon security constraints:
- No credentials or secrets written to vault
- Path validation to prevent directory traversal
- Audit logging for all write operations

Tier: Core (Required for all tiers)
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Union


class FileManagerSkill:
    """
    Core Agent Skill for file system operations.
    
    Provides secure read, write, list, and move operations for the
    Obsidian vault and project directories.
    """

    def __init__(self, vault_root: Optional[str] = None):
        """
        Initialize the File Manager Skill.
        
        Args:
            vault_root: Root path of the Obsidian vault
        """
        self.vault_root = Path(vault_root) if vault_root else Path.cwd()
        self.logger = logging.getLogger(__name__)
        
        # Security: Define allowed directories
        self.allowed_dirs = [
            self.vault_root,
            self.vault_root / "Inbox",
            self.vault_root / "Needs_Action",
            self.vault_root / "Plans",
            self.vault_root / "Pending_Approval",
            self.vault_root / "Approved",
            self.vault_root / "Done",
            self.vault_root / "Briefings",
            self.vault_root / "Logs",
            self.vault_root / "specs",
            self.vault_root / "skills",
        ]

    def _validate_path(self, path: Union[str, Path]) -> Path:
        """
        Validate that a path is within allowed directories.
        
        Args:
            path: Path to validate
            
        Returns:
            Validated Path object
            
        Raises:
            ValueError: If path is outside allowed directories
        """
        resolved_path = Path(path).resolve()
        
        # Check if path is within any allowed directory
        for allowed_dir in self.allowed_dirs:
            try:
                resolved_path.relative_to(allowed_dir.resolve())
                return resolved_path
            except ValueError:
                continue
        
        # Also allow paths within the project root
        project_root = Path.cwd()
        try:
            resolved_path.relative_to(project_root.resolve())
            return resolved_path
        except ValueError:
            pass
        
        # Path is outside allowed directories
        raise ValueError(f"Path '{path}' is outside allowed directories")

    def _ensure_parent_exists(self, path: Path) -> None:
        """Create parent directories if they don't exist."""
        path.parent.mkdir(parents=True, exist_ok=True)

    def read_file(self, path: Union[str, Path], encoding: str = "utf-8") -> Dict[str, Any]:
        """
        Read content from a file.
        
        Args:
            path: Path to the file to read
            encoding: File encoding (default: utf-8)
            
        Returns:
            Dictionary with:
            {
                "success": bool,
                "content": str or None,
                "path": str,
                "size_bytes": int,
                "modified_time": str,
                "error": str or None
            }
        """
        try:
            file_path = self._validate_path(path)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "content": None,
                    "path": str(path),
                    "error": f"File does not exist: {path}"
                }
            
            if not file_path.is_file():
                return {
                    "success": False,
                    "content": None,
                    "path": str(path),
                    "error": f"Path is not a file: {path}"
                }
            
            # Read file content
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Get file metadata
            stat = file_path.stat()
            
            return {
                "success": True,
                "content": content,
                "path": str(file_path),
                "size_bytes": stat.st_size,
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "error": None
            }
            
        except ValueError as e:
            return {
                "success": False,
                "content": None,
                "path": str(path),
                "error": f"Security validation failed: {e}"
            }
        except Exception as e:
            self.logger.error(f"Error reading file {path}: {e}")
            return {
                "success": False,
                "content": None,
                "path": str(path),
                "error": str(e)
            }

    def write_file(self, path: Union[str, Path], content: str, 
                   mode: str = "overwrite", encoding: str = "utf-8") -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            path: Path to the file to write
            content: Content to write
            mode: Write mode - "overwrite" or "append"
            encoding: File encoding (default: utf-8)
            
        Returns:
            Dictionary with:
            {
                "success": bool,
                "path": str,
                "bytes_written": int,
                "mode": str,
                "timestamp": str,
                "error": str or None
            }
        """
        try:
            file_path = self._validate_path(path)
            
            # Security check: Don't write to sensitive locations
            forbidden_patterns = ['secrets', '.env', 'credentials', 'password', 'token']
            for pattern in forbidden_patterns:
                if pattern.lower() in str(file_path).lower():
                    return {
                        "success": False,
                        "path": str(path),
                        "error": f"Writing to '{pattern}' paths is not allowed for security"
                    }
            
            # Ensure parent directory exists
            self._ensure_parent_exists(file_path)
            
            # Determine write mode
            write_mode = 'a' if mode.lower() == 'append' else 'w'
            
            # Write content
            with open(file_path, write_mode, encoding=encoding) as f:
                f.write(content)
            
            # Get bytes written
            bytes_written = len(content.encode(encoding))
            
            self.logger.info(f"File written: {file_path} ({bytes_written} bytes, mode={mode})")
            
            return {
                "success": True,
                "path": str(file_path),
                "bytes_written": bytes_written,
                "mode": mode,
                "timestamp": datetime.now().isoformat(),
                "error": None
            }
            
        except ValueError as e:
            return {
                "success": False,
                "path": str(path),
                "error": f"Security validation failed: {e}"
            }
        except Exception as e:
            self.logger.error(f"Error writing file {path}: {e}")
            return {
                "success": False,
                "path": str(path),
                "error": str(e)
            }

    def list_directory(self, path: Union[str, Path], 
                       pattern: Optional[str] = None,
                       recursive: bool = False) -> Dict[str, Any]:
        """
        List contents of a directory.
        
        Args:
            path: Path to the directory
            pattern: Optional glob pattern to filter files (e.g., "*.md")
            recursive: Whether to list recursively
            
        Returns:
            Dictionary with:
            {
                "success": bool,
                "path": str,
                "files": list,
                "directories": list,
                "total_items": int,
                "error": str or None
            }
        """
        try:
            dir_path = self._validate_path(path)
            
            if not dir_path.exists():
                return {
                    "success": False,
                    "path": str(path),
                    "error": f"Directory does not exist: {path}"
                }
            
            if not dir_path.is_dir():
                return {
                    "success": False,
                    "path": str(path),
                    "error": f"Path is not a directory: {path}"
                }
            
            files = []
            directories = []
            
            if recursive:
                # Recursive listing
                for item in dir_path.rglob(pattern or "*"):
                    rel_path = item.relative_to(dir_path)
                    if item.is_file():
                        files.append(str(rel_path))
                    elif item.is_dir():
                        directories.append(str(rel_path))
            else:
                # Non-recursive listing
                for item in dir_path.iterdir():
                    if pattern and not item.match(pattern):
                        continue
                    if item.is_file():
                        files.append(item.name)
                    elif item.is_dir():
                        directories.append(item.name)
            
            return {
                "success": True,
                "path": str(dir_path),
                "files": sorted(files),
                "directories": sorted(directories),
                "total_items": len(files) + len(directories),
                "error": None
            }
            
        except ValueError as e:
            return {
                "success": False,
                "path": str(path),
                "error": f"Security validation failed: {e}"
            }
        except Exception as e:
            self.logger.error(f"Error listing directory {path}: {e}")
            return {
                "success": False,
                "path": str(path),
                "error": str(e)
            }

    def move_file(self, source: Union[str, Path], 
                  destination: Union[str, Path],
                  overwrite: bool = False) -> Dict[str, Any]:
        """
        Move a file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination path (file or directory)
            overwrite: Whether to overwrite existing file
            
        Returns:
            Dictionary with:
            {
                "success": bool,
                "source": str,
                "destination": str,
                "timestamp": str,
                "error": str or None
            }
        """
        try:
            source_path = self._validate_path(source)
            dest_path = self._validate_path(destination)
            
            if not source_path.exists():
                return {
                    "success": False,
                    "source": str(source),
                    "destination": str(destination),
                    "error": f"Source file does not exist: {source}"
                }
            
            # If destination is a directory, append filename
            if dest_path.is_dir():
                dest_path = dest_path / source_path.name

            # Handle existing destination
            if dest_path.exists():
                if overwrite:
                    # Delete the existing file first
                    os.remove(str(dest_path))
                    self.logger.info(f"Deleted existing destination file: {dest_path}")
                else:
                    # Add timestamp to avoid collision
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    stem = dest_path.stem
                    suffix = dest_path.suffix
                    dest_path = dest_path.parent / f"{stem}_{timestamp}{suffix}"

            # Ensure parent directory exists
            self._ensure_parent_exists(dest_path)

            # Move the file
            shutil.move(str(source_path), str(dest_path))
            
            self.logger.info(f"File moved: {source} -> {dest_path}")
            
            return {
                "success": True,
                "source": str(source_path),
                "destination": str(dest_path),
                "timestamp": datetime.now().isoformat(),
                "error": None
            }
            
        except ValueError as e:
            return {
                "success": False,
                "source": str(source),
                "destination": str(destination),
                "error": f"Security validation failed: {e}"
            }
        except Exception as e:
            self.logger.error(f"Error moving file {source} -> {destination}: {e}")
            return {
                "success": False,
                "source": str(source),
                "destination": str(destination),
                "error": str(e)
            }

    def delete_file(self, path: Union[str, Path]) -> Dict[str, Any]:
        """
        Delete a file.
        
        Args:
            path: Path to the file to delete
            
        Returns:
            Dictionary with:
            {
                "success": bool,
                "path": str,
                "timestamp": str,
                "error": str or None
            }
        """
        try:
            file_path = self._validate_path(path)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "path": str(path),
                    "error": f"File does not exist: {path}"
                }
            
            if not file_path.is_file():
                return {
                    "success": False,
                    "path": str(path),
                    "error": f"Path is not a file: {path}"
                }
            
            # Delete the file
            file_path.unlink()
            
            self.logger.info(f"File deleted: {path}")
            
            return {
                "success": True,
                "path": str(file_path),
                "timestamp": datetime.now().isoformat(),
                "error": None
            }
            
        except ValueError as e:
            return {
                "success": False,
                "path": str(path),
                "error": f"Security validation failed: {e}"
            }
        except Exception as e:
            self.logger.error(f"Error deleting file {path}: {e}")
            return {
                "success": False,
                "path": str(path),
                "error": str(e)
            }

    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a file operation.
        
        This is the main entry point that follows the Agent Skill interface.
        
        Args:
            operation: Operation to perform ("read", "write", "list", "move", "delete")
            **kwargs: Operation-specific arguments
            
        Returns:
            Dictionary with operation result
        """
        operations = {
            "read": lambda: self.read_file(kwargs.get("path")),
            "write": lambda: self.write_file(
                kwargs.get("path"), 
                kwargs.get("content", ""),
                kwargs.get("mode", "overwrite")
            ),
            "list": lambda: self.list_directory(
                kwargs.get("path"),
                kwargs.get("pattern"),
                kwargs.get("recursive", False)
            ),
            "move": lambda: self.move_file(
                kwargs.get("source"),
                kwargs.get("destination"),
                kwargs.get("overwrite", False)
            ),
            "delete": lambda: self.delete_file(kwargs.get("path"))
        }
        
        if operation not in operations:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}. Valid: {list(operations.keys())}"
            }
        
        try:
            return operations[operation]()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Convenience functions for direct skill invocation
def read_file(path: str) -> Dict[str, Any]:
    """Read a file from the vault."""
    skill = FileManagerSkill()
    return skill.read_file(path)


def write_file(path: str, content: str, mode: str = "overwrite") -> Dict[str, Any]:
    """Write content to a file in the vault."""
    skill = FileManagerSkill()
    return skill.write_file(path, content, mode)


def list_directory(path: str, pattern: Optional[str] = None) -> Dict[str, Any]:
    """List contents of a directory."""
    skill = FileManagerSkill()
    return skill.list_directory(path, pattern)


# Skill metadata for registry
SKILL_METADATA = {
    "name": "FileManagerSkill",
    "version": "1.0.0",
    "tier": "Core",
    "description": "Secure file operations for Obsidian vault (read/write/list/move/delete)",
    "hitl_required": False,
    "functions": ["execute", "read_file", "write_file", "list_directory", "move_file", "delete_file"],
    "inputs": {
        "operation": "str - Operation to perform",
        "path": "str - File/directory path",
        "content": "str - Content to write (for write operation)",
        "mode": "str - Write mode: overwrite/append",
        "pattern": "str - Glob pattern for filtering (for list operation)",
        "source": "str - Source path (for move operation)",
        "destination": "str - Destination path (for move operation)"
    },
    "outputs": {
        "success": "bool - Whether the operation succeeded",
        "content": "str - File content (for read operation)",
        "files": "list - List of files (for list operation)",
        "directories": "list - List of directories (for list operation)",
        "error": "str - Error message if failed"
    }
}


if __name__ == "__main__":
    # Test the skill
    print("Testing File Manager Skill...")
    print("-" * 50)
    
    skill = FileManagerSkill()
    
    # Test write
    print("\n1. Testing write_file...")
    result = skill.write_file("test_file.md", "# Test File\n\nThis is a test.")
    print(f"   Write result: {result}")
    
    # Test read
    print("\n2. Testing read_file...")
    result = skill.read_file("test_file.md")
    print(f"   Read result: {result['success']}, Content: {result.get('content', '')[:50]}...")
    
    # Test list
    print("\n3. Testing list_directory...")
    result = skill.list_directory(".", pattern="*.md")
    print(f"   List result: {result['total_items']} files found")
    
    # Test move
    print("\n4. Testing move_file...")
    result = skill.move_file("test_file.md", "Done/test_file.md")
    print(f"   Move result: {result}")
    
    print("\n" + "-" * 50)
    print("File Manager Skill tests completed!")
