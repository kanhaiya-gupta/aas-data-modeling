#!/usr/bin/env python3
"""
Python Environment Check Script

This script checks your Python setup and helps determine
the correct command to use for your system.
"""

import sys
import subprocess
import platform

def check_python_command(command):
    """Check if a Python command is available and get its version"""
    try:
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

def main():
    print("🔍 Python Environment Check")
    print("=" * 50)
    
    # Check current Python
    print(f"Current Python executable: {sys.executable}")
    print(f"Current Python version: {sys.version}")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print()
    
    # Check different Python commands
    commands = ['python', 'python3', 'py']
    results = {}
    
    print("📋 Available Python commands:")
    for cmd in commands:
        version = check_python_command(cmd)
        if version:
            results[cmd] = version
            print(f"  ✅ {cmd}: {version}")
        else:
            print(f"  ❌ {cmd}: Not available")
    
    print()
    
    # Recommendations
    print("💡 Recommendations:")
    
    if 'python' in results:
        print("  ✅ Use 'python' for your scripts")
        print("  ✅ This is the correct command for your setup")
    elif 'python3' in results:
        print("  ✅ Use 'python3' for your scripts")
        print("  ✅ This is the correct command for your setup")
    elif 'py' in results:
        print("  ✅ Use 'py' for your scripts")
        print("  ✅ This is the Windows Python launcher")
    else:
        print("  ❌ No Python commands found")
        print("  💡 Please install Python 3.8+")
    
    print()
    
    # Check if we're in Git Bash
    if 'GIT_BASH' in os.environ.get('SHELL', '').upper() or 'bash' in os.environ.get('SHELL', '').lower():
        print("🐚 Git Bash detected:")
        print("  ✅ 'python' command should work fine")
        print("  ✅ Your setup scripts will use 'python'")
    
    print()
    print("🚀 Ready to run setup scripts with 'python' command!")

if __name__ == "__main__":
    import os
    main() 