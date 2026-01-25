"""
Main entry point for the AI Employee Filesystem Watcher.
"""
from src.filesystem_watcher import FilesystemWatcher


def main():
    """Run the filesystem watcher."""
    watcher = FilesystemWatcher()
    watcher.start()


if __name__ == "__main__":
    main()