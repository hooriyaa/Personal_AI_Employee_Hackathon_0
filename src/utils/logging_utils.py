"""
Logging framework for the AI Employee system.
"""
import logging
from pathlib import Path
import sys


def setup_logging(logs_dir: Path, log_level: str = "INFO") -> logging.Logger:
    """
    Set up the logging framework for the AI Employee system.
    
    Args:
        logs_dir: Directory where logs should be stored
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Ensure the logs directory exists
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a custom logger
    logger = logging.getLogger('ai_employee')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove any existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create handlers
    file_handler = logging.FileHandler(logs_dir / "ai_employee.log")
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Set levels for handlers
    file_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatters and add them to handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger