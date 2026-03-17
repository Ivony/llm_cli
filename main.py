#!/usr/bin/env python
"""
AI Command Line Tool

This script serves as an entry point to run the AI CLI tool without relative import errors.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ai_cli.cli import main

if __name__ == "__main__":
    main()
