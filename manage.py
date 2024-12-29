#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

def main():
    """Run administrative tasks."""
    # Explicitly set the settings module path
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    
    # Print current directory and settings module for debugging
    print(f"Current directory: {Path.cwd()}")
    print(f"Settings module: {os.environ['DJANGO_SETTINGS_MODULE']}")
    
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()