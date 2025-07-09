#!/usr/bin/env python3
"""
Basic Unit Tests for QI Digital Platform

Tests basic functionality and imports.
"""

import sys
import os

# Add parent directory to path
sys.path.append('..')

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing module imports...")
    
    try:
        # Test webapp imports
        from webapp import app
        print("  OK: webapp.app imported successfully")
        
        from webapp.aasx import aasx_processor
        print("  OK: webapp.aasx.aasx_processor imported successfully")
        
        from webapp.aasx import dotnet_bridge
        print("  OK: webapp.aasx.dotnet_bridge imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"  ERROR: Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic platform functionality"""
    print("Testing basic functionality...")
    
    try:
        # Test that we can import the module
        from webapp.aasx import aasx_processor
        print("  OK: AASX processor module imported successfully")
        
        # Test that we can access the class
        AASXProcessor = aasx_processor.AASXProcessor
        print("  OK: AASXProcessor class accessible")
        
        # Test basic file operations
        test_file = "test_file.txt"
        with open(test_file, 'w') as f:
            f.write("test")
        
        if os.path.exists(test_file):
            print("  OK: File operations working")
            os.remove(test_file)
        else:
            print("  ERROR: File operations failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ERROR: Basic functionality error: {e}")
        return False

def test_directory_structure():
    """Test that required directories exist"""
    print("Testing directory structure...")
    
    required_dirs = [
        "../webapp",
        "../webapp/aasx",
        "../webapp/templates",
        "../webapp/static",
        "../aas-processor",
        "../AasxPackageExplorer"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  OK: {dir_path} exists")
        else:
            print(f"  ERROR: {dir_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all basic tests"""
    print("="*50)
    print("Basic Unit Tests")
    print("="*50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Directory Structure", test_directory_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 30)
        
        if test_func():
            print(f"PASSED: {test_name}")
            passed += 1
        else:
            print(f"FAILED: {test_name}")
    
    print("\n" + "="*50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("SUCCESS: All basic tests passed!")
        return 0
    else:
        print("WARNING: Some basic tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 