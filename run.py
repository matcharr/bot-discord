#!/usr/bin/env python3
"""Simple script to run the Discord bot."""

import sys
from pathlib import Path

# Add project directory to Python path
project_dir = Path(__file__).parent / "project"
sys.path.insert(0, str(project_dir))

# Import and run the main function
from main import main
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    except Exception as e:
        print(f"Error starting bot: {e}")
        sys.exit(1)