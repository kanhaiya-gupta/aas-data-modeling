#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AASX Package Explorer Launcher
Launches the AASX Package Explorer application.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def main():
    """Main launcher function"""
    print("🚀 AASX Package Explorer Launcher")
    print("=" * 50)
    
    # Get the project root directory (parent of scripts folder)
    project_root = Path(__file__).parent.parent
    explorer_path = project_root / "AasxPackageExplorer" / "AasxPackageExplorer.exe"
    
    print(f"📁 Project root: {project_root}")
    print(f"🔍 Explorer path: {explorer_path}")
    
    # Check if explorer exists
    if not explorer_path.exists():
        print("❌ Error: AASX Package Explorer not found!")
        print(f"   Expected location: {explorer_path}")
        print("\n💡 Please ensure:")
        print("   1. The AasxPackageExplorer folder exists in the project root")
        print("   2. AasxPackageExplorer.exe is present in the folder")
        print("   3. Windows Desktop Runtime 3.1 is installed")
        return 1
    
    print("✅ AASX Package Explorer found!")
    
    # Check platform
    if platform.system() != "Windows":
        print("⚠️  Warning: This launcher is designed for Windows")
        print("   The AASX Package Explorer is a Windows application")
        return 1
    
    # Launch the explorer
    try:
        print("🚀 Launching AASX Package Explorer...")
        subprocess.Popen([str(explorer_path)])
        print("✅ AASX Package Explorer launched successfully!")
        print("\n💡 Tips:")
        print("   - Use File > Open to load AASX files")
        print("   - Check the content-for-demo folder for sample files")
        print("   - Press Ctrl+C to close this launcher")
        return 0
        
    except Exception as e:
        print(f"❌ Error launching explorer: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Ensure Windows Desktop Runtime 3.1 is installed")
        print("   2. Try running as administrator")
        print("   3. Check Windows Defender/antivirus settings")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Launcher closed by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1) 