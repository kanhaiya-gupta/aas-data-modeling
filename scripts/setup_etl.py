#!/usr/bin/env python3
"""
Smart ETL Environment Setup

This script automatically detects your operating system and provides
the optimal setup experience for your platform.

Supported platforms:
- Windows (Windows 10/11, Windows 7+)
- Linux (Ubuntu/Debian, CentOS/RHEL/Fedora)
- macOS (10.15+)

Usage:
    python setup_etl.py
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run the smart ETL setup"""
    # Get the path to the auto setup script
    script_dir = Path(__file__).parent
    auto_script = script_dir / "setup_etl_auto.py"
    
    if not auto_script.exists():
        print("❌ Setup script not found!")
        print(f"Expected: {auto_script}")
        return 1
    
    print("🚀 Starting Smart ETL Environment Setup...")
    print("This will automatically detect your platform and run the optimal setup.")
    print()
    
    # Run the auto setup script
    result = subprocess.run([sys.executable, str(auto_script)])
    return result.returncode

if __name__ == "__main__":
    sys.exit(main()) 