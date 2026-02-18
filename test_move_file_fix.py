"""
Test script to verify the "Destination file exists" error fix.

This test verifies that when moving a file from Needs_Action to Done,
if a file with the same name already exists in Done, it is deleted first
before moving the new file.
"""

import os
import shutil
import tempfile
from pathlib import Path
from src.utils.helpers import move_file


def test_move_file_overwrite():
    """Test that move_file with overwrite=True deletes existing destination first."""
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_dir = temp_path / "Needs_Action"
        dest_dir = temp_path / "Done"
        
        source_dir.mkdir(parents=True, exist_ok=True)
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Create source file
        source_file = source_dir / "test_task.md"
        source_file.write_text("This is the NEW task file content")
        
        # Create existing destination file (simulating the error scenario)
        dest_file = dest_dir / "test_task.md"
        dest_file.write_text("This is the OLD task file content that should be deleted")
        
        print(f"Source file exists: {source_file.exists()}")
        print(f"Destination file exists (before): {dest_file.exists()}")
        print(f"Destination content (before): {dest_file.read_text()}")
        
        # Move with overwrite=True
        result = move_file(source_file, dest_file, overwrite=True)
        
        print(f"\nMove result: {result}")
        print(f"Source file exists (after): {source_file.exists()}")
        print(f"Destination file exists (after): {dest_file.exists()}")
        
        if dest_file.exists():
            print(f"Destination content (after): {dest_file.read_text()}")
        
        # Verify
        assert result == True, "Move should succeed with overwrite=True"
        assert not source_file.exists(), "Source file should not exist after move"
        assert dest_file.exists(), "Destination file should exist after move"
        assert dest_file.read_text() == "This is the NEW task file content", \
            "Destination should have new content (old file was deleted first)"
        
        print("\n[PASS] Test PASSED: File was deleted and moved successfully!")
        return True


def test_move_file_no_overwrite():
    """Test that move_file with overwrite=False fails when destination exists."""
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_dir = temp_path / "Needs_Action"
        dest_dir = temp_path / "Done"
        
        source_dir.mkdir(parents=True, exist_ok=True)
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Create source file
        source_file = source_dir / "test_task2.md"
        source_file.write_text("This is the NEW task file content")
        
        # Create existing destination file
        dest_file = dest_dir / "test_task2.md"
        dest_file.write_text("This is the OLD task file content")
        
        print(f"\n--- Testing overwrite=False ---")
        print(f"Source file exists: {source_file.exists()}")
        print(f"Destination file exists (before): {dest_file.exists()}")
        
        # Move with overwrite=False (default)
        result = move_file(source_file, dest_file, overwrite=False)
        
        print(f"\nMove result: {result}")
        print(f"Source file exists (after): {source_file.exists()}")
        print(f"Destination file exists (after): {dest_file.exists()}")
        
        # Verify
        assert result == False, "Move should fail with overwrite=False when destination exists"
        assert source_file.exists(), "Source file should still exist (move failed)"
        assert dest_file.exists(), "Destination file should still exist with old content"
        assert dest_file.read_text() == "This is the OLD task file content", \
            "Destination should still have old content"
        
        print("\n[PASS] Test PASSED: File was NOT moved (as expected with overwrite=False)!")
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("Testing move_file with overwrite logic")
    print("=" * 60)
    
    try:
        test_move_file_overwrite()
        test_move_file_no_overwrite()
        
        print("\n" + "=" * 60)
        print("[PASS] ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
