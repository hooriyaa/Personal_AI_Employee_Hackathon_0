"""
Filesystem watcher for the AI Employee system.
"""
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import yaml

from .config import (
    INBOX_DIR, NEEDS_ACTION_DIR, LOGS_DIR, POLLING_INTERVAL, CONFIRMATION_DELAY
)
from .utils.file_operations import wait_for_file_stability, move_file_with_timestamp, create_metadata_trigger
from .utils.logging_utils import setup_logging


class InboxHandler(FileSystemEventHandler):
    """Handles file creation events in the Inbox directory."""
    
    def __init__(self, logger):
        self.logger = logger
        
    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        self.logger.info(f"New file detected: {file_path}")
        
        # Wait for the file to be completely written
        self.logger.info(f"Waiting for file to be stable: {file_path}")
        if wait_for_file_stability(file_path, POLLING_INTERVAL, CONFIRMATION_DELAY):
            self.logger.info(f"File is stable: {file_path}")
            
            # Move the file to Needs_Action directory
            moved_file_path = move_file_with_timestamp(file_path, NEEDS_ACTION_DIR)
            self.logger.info(f"Moved file to Needs_Action: {moved_file_path}")
            
            # Create metadata trigger file
            file_info = {
                'filename': moved_file_path.name,
                'size': moved_file_path.stat().st_size,
                'timestamp': datetime.now().isoformat(),
                'original_path': str(moved_file_path)
            }
            
            trigger_path = create_metadata_trigger(file_info, NEEDS_ACTION_DIR)
            self.logger.info(f"Created metadata trigger: {trigger_path}")
        else:
            self.logger.error(f"Could not confirm file stability: {file_path}")


class FilesystemWatcher:
    """Monitors the Inbox folder for new file drops."""
    
    def __init__(self):
        self.observer = Observer()
        self.logger = setup_logging(LOGS_DIR)
        
    def start(self):
        """Start watching the Inbox directory."""
        event_handler = InboxHandler(self.logger)
        self.observer.schedule(event_handler, str(INBOX_DIR), recursive=False)
        
        self.observer.start()
        self.logger.info(f"Started watching Inbox directory: {INBOX_DIR}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            self.logger.info("Filesystem watcher stopped by user")
        
        self.observer.join()