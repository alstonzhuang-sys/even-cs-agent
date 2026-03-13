#!/usr/bin/env python3
"""
Validate Even CS Agent Configuration

This script checks:
1. GEMINI_API_KEY environment variable
2. config/channels.json file
3. Required fields in configuration
4. Rosen's contact information

Usage:
    python3 validate_config.py
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from output_switch import verify_config

if __name__ == "__main__":
    success = verify_config()
    sys.exit(0 if success else 1)
