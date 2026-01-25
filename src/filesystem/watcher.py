"""
File system monitoring module using the watchdog library.

This module monitors specified directories for file system events
such as file creation, modification, and deletion.
"""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import logging
from datetime import datetime


class FileSystemEventLogger(FileSystemEventHandler):
    """Custom event handler to log file system events."""
    
    def __init__(self, callback=None):
        """
        Initialize the event handler.
        
        Args:
            callback (callable, optional): Callback function to call when events occur
        """
        super().__init__()
        self.callback = callback
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('Logs/filesystem_watcher.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def on_created(self, event):
        """Handle file/directory creation events."""
        if not event.is_directory:
            self.logger.info(f"File created: {event.src_path}")
            if self.callback:
                self.callback('created', event.src_path)

    def on_modified(self, event):
        """Handle file/directory modification events."""
        if not event.is_directory:
            self.logger.info(f"File modified: {event.src_path}")
            if self.callback:
                self.callback('modified', event.src_path)

    def on_deleted(self, event):
        """Handle file/directory deletion events."""
        if not event.is_directory:
            self.logger.info(f"File deleted: {event.src_path}")
            if self.callback:
                self.callback('deleted', event.src_path)

    def on_moved(self, event):
        """Handle file/directory move events."""
        if not event.is_directory:
            self.logger.info(f"File moved: {event.src_path} -> {event.dest_path}")
            if self.callback:
                self.callback('moved', {'src_path': event.src_path, 'dest_path': event.dest_path})


class FileSystemWatcher:
    """Monitors file system events in specified directories."""
    
    def __init__(self, watch_directories=None, recursive=True, callback=None):
        """
        Initialize the file system watcher.
        
        Args:
            watch_directories (list): List of directories to watch
            recursive (bool): Whether to watch subdirectories
            callback (callable): Callback function to call when events occur
        """
        self.watch_directories = watch_directories or []
        self.recursive = recursive
        self.callback = callback
        self.observer = Observer()
        self.event_handlers = {}
        self.running = False
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('Logs/filesystem_watcher.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def add_watch_directory(self, directory_path):
        """
        Add a directory to watch.
        
        Args:
            directory_path (str or Path): Path to the directory to watch
        """
        dir_path = Path(directory_path)
        if not dir_path.exists():
            self.logger.warning(f"Directory does not exist: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {dir_path}")
        
        if str(dir_path) not in self.watch_directories:
            self.watch_directories.append(str(dir_path))
            self.logger.info(f"Added directory to watch: {dir_path}")

    def remove_watch_directory(self, directory_path):
        """
        Remove a directory from watching.
        
        Args:
            directory_path (str or Path): Path to the directory to remove from watching
        """
        dir_str = str(Path(directory_path))
        if dir_str in self.watch_directories:
            self.watch_directories.remove(dir_str)
            self.logger.info(f"Removed directory from watch: {dir_str}")

    def start(self):
        """Start monitoring file system events."""
        if self.running:
            self.logger.warning("File system watcher is already running")
            return

        # Create event handlers for each directory
        for directory in self.watch_directories:
            event_handler = FileSystemEventLogger(callback=self.callback)
            self.observer.schedule(event_handler, directory, recursive=self.recursive)
            self.logger.info(f"Scheduled observer for: {directory}")

        self.observer.start()
        self.running = True
        self.logger.info("File system watcher started")

    def stop(self):
        """Stop monitoring file system events."""
        if not self.running:
            self.logger.warning("File system watcher is not running")
            return

        self.observer.stop()
        self.observer.join()
        self.running = False
        self.logger.info("File system watcher stopped")

    def is_running(self):
        """Check if the watcher is currently running."""
        return self.running

    def get_watched_directories(self):
        """Get the list of currently watched directories."""
        return self.watch_directories.copy()


def main():
    """Main entry point for testing the file system watcher."""
    # Define callback function to handle events
    def event_callback(event_type, path_info):
        if event_type == 'moved':
            print(f"File moved: {path_info['src_path']} -> {path_info['dest_path']}")
        else:
            print(f"File {event_type}: {path_info}")

    # Create watcher instance
    watcher = FileSystemWatcher(
        watch_directories=[
            './Needs_Action',
            './Plans',
            './Pending_Approval',
            './Approved',
            './Done'
        ],
        recursive=False,
        callback=event_callback
    )

    try:
        # Start watching
        watcher.start()
        print("File system watcher started. Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping file system watcher...")
        watcher.stop()


if __name__ == "__main__":
    main()