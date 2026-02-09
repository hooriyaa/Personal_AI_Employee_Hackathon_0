"""
Main entry point for the Gmail Reasoning Loop application.

This script orchestrates the different components of the system:
- Gmail Watcher: Monitors Gmail for new emails
- Plan Generation Skill: Creates action plans for tasks
- File System Watcher: Monitors file system changes
"""

import threading
import time
import logging
import signal
import sys
from datetime import datetime

from src.gmail.gmail_watcher import GmailWatcher
from skills.plan_generation_skill import PlanGenerationSkill
from src.filesystem.watcher import FileSystemWatcher
from src.action_runner import ActionRunner
from src.config.settings import (
    NEEDS_ACTION_DIR, PLANS_DIR, PENDING_APPROVAL_DIR,
    APPROVED_DIR, DONE_DIR, LOGS_DIR
)


class GmailReasoningLoop:
    """Main orchestrator for the Gmail Reasoning Loop application."""

    def __init__(self):
        """Initialize the main application."""
        self.gmail_watcher = GmailWatcher()
        self.plan_skill = PlanGenerationSkill()
        self.file_system_watcher = FileSystemWatcher()
        self.action_runner = ActionRunner()

        # Thread management
        self.threads = []
        self.running = False

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOGS_DIR / 'main.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_file_system_monitoring(self):
        """Set up file system monitoring for relevant directories."""
        # Add directories to watch
        watch_dirs = [
            NEEDS_ACTION_DIR,
            PLANS_DIR,
            PENDING_APPROVAL_DIR,
            APPROVED_DIR,
            DONE_DIR
        ]
        
        for directory in watch_dirs:
            self.file_system_watcher.add_watch_directory(directory)
        
        # Set up callback for file system events
        self.file_system_watcher.callback = self.handle_file_system_event

    def handle_file_system_event(self, event_type, path_info):
        """
        Handle file system events.

        Args:
            event_type (str): Type of event ('created', 'modified', 'deleted', 'moved')
            path_info (str or dict): Path information for the event
        """
        self.logger.info(f"File system event: {event_type} - {path_info}")

        # If a new file appears in Needs_Action, trigger plan generation
        if event_type == 'created':
            if isinstance(path_info, str) and str(NEEDS_ACTION_DIR) in path_info:
                # Deduplication Check: Before processing a file from Needs_Action,
                # check if a Plan with the same Task ID or Source Name already exists in the Plans folder.
                import os
                from pathlib import Path

                file_path = Path(path_info)
                file_stem = file_path.stem  # Get the filename without extension

                # Look for existing plan files in the Plans directory that match this source name
                existing_plans = list(PLANS_DIR.glob(f"*{file_stem}*"))

                if existing_plans:
                    self.logger.info(f"Duplicate detected: Plan already exists for {file_stem}, skipping...")
                    return  # Skip processing if a plan already exists

                self.logger.info("New task file detected, triggering plan generation...")
                # Run plan generation in a separate thread to avoid blocking
                plan_thread = threading.Thread(target=self.plan_skill.run_once)
                plan_thread.daemon = True
                plan_thread.start()

    def run_gmail_watcher(self):
        """Run the Gmail watcher in a separate thread."""
        self.gmail_watcher.run()

    def run_plan_generation_monitor(self):
        """Run the plan generation skill in a loop to periodically check for new tasks."""
        while self.running:
            try:
                self.plan_skill.run_once()
                # Sleep for a period before checking again
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in plan generation monitor: {e}")
                time.sleep(60)  # Wait longer if there's an error

    def run_file_system_watcher(self):
        """Run the file system watcher."""
        self.file_system_watcher.start()

        try:
            while self.running:
                time.sleep(1)  # Keep the thread alive
        except KeyboardInterrupt:
            pass
        finally:
            self.file_system_watcher.stop()

    def run_action_runner(self):
        """Run the action runner in a separate thread."""
        self.action_runner.run()

    def start(self):
        """Start all components of the application."""
        self.logger.info("Starting Gmail Reasoning Loop application...")
        self.running = True

        # Set up file system monitoring
        self.setup_file_system_monitoring()

        # Create and start threads for each component
        gmail_thread = threading.Thread(target=self.run_gmail_watcher, name="GmailWatcher")
        plan_thread = threading.Thread(target=self.run_plan_generation_monitor, name="PlanGeneration")
        fs_thread = threading.Thread(target=self.run_file_system_watcher, name="FileSystemWatcher")
        action_thread = threading.Thread(target=self.run_action_runner, name="ActionRunner")

        self.threads = [gmail_thread, plan_thread, fs_thread, action_thread]

        # Start all threads
        for thread in self.threads:
            thread.daemon = True  # Dies when main thread dies
            thread.start()
            self.logger.info(f"Started thread: {thread.name}")

        self.logger.info("All components started successfully.")

    def stop(self):
        """Stop all components of the application."""
        self.logger.info("Stopping Gmail Reasoning Loop application...")
        self.running = False

        # Stop the Gmail watcher
        self.gmail_watcher.stop()

        # Stop the action runner
        self.action_runner.stop()

        # Wait for threads to finish (with timeout)
        for thread in self.threads:
            thread.join(timeout=5)  # Wait up to 5 seconds for each thread
            if thread.is_alive():
                self.logger.warning(f"Thread {thread.name} did not stop gracefully")

        self.logger.info("All components stopped.")

    def run(self):
        """Run the application until interrupted."""
        # Set up signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            self.logger.info("Received interrupt signal, shutting down...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            self.start()
            
            # Keep main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt, shutting down...")
            self.stop()


def main():
    """Main entry point."""
    app = GmailReasoningLoop()
    app.run()


if __name__ == "__main__":
    main()