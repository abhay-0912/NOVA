"""
Professional Logging Setup for NOVA

Provides clean, structured logging with proper formatting, file rotation,
and different log levels for development and production.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color codes for terminal output."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green  
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_console: bool = True,
    enable_file: bool = True
) -> logging.Logger:
    """
    Set up professional logging for NOVA.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        enable_console: Whether to log to console
        enable_file: Whether to log to file
        
    Returns:
        Configured logger instance
    """
    
    # Create root logger
    logger = logging.getLogger("nova")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with safe formatting
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter(
            fmt="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        # Set encoding to handle Unicode characters
        if hasattr(console_handler.stream, 'reconfigure'):
            try:
                console_handler.stream.reconfigure(encoding='utf-8')
            except:
                pass  # Fallback gracefully
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if enable_file:
        if log_file is None:
            log_file = Path("logs/nova.log")
        
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_formatter = logging.Formatter(
            fmt="%(asctime)s | %(name)-20s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Prevent duplicate logs from propagating to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    return logging.getLogger(f"nova.{name}")


# Convenience function for quick setup
def setup_basic_logging(debug: bool = False):
    """Quick setup for basic logging needs."""
    level = "DEBUG" if debug else "INFO"
    return setup_logging(level=level)
