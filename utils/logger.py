"""
Logging utilities for Even CS Agent.

Provides centralized logging configuration with file and console output.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Create logs directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file with date
LOG_FILE = LOG_DIR / f"agent-{datetime.now().strftime('%Y-%m-%d')}.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stderr)
    ]
)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger for a module.
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
