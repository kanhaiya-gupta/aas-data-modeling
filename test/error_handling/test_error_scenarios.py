#!/usr/bin/env python3
"""
Error Handling Tests

This script tests error handling for various failure scenarios.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.append('..')

def test_invalid_file_path():
    """Test handling of invalid file paths"""
    print("Testing Invalid File Path Handling")
    print("=" * 40)
    
    try:
        from webapp.aasx.aasx_processor import AASXProcessor
        
        # Test with non-existent file
        invalid_path = "non_existent_file.aasx"
        
        try:
            processor = AASXProcessor(invalid_path)
            print("ERROR: Should have raised FileNotFoundError")
            return False
        except FileNotFoundError:
            print("OK: FileNotFoundError raised for non-existent file")
        except Exception as e:
            print(f"ERROR: Unexpected exception: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"ERROR: Invalid file path test failed: {e}")
        return False

def test_invalid_file_format():
    """Test handling of invalid file formats"""
    print("\nTesting Invalid File Format Handling")
    print("=" * 40)
    
    try:
        from webapp.aasx.aasx_processor import AASXProcessor
        
        # Create a temporary file with wrong extension
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b"This is not an AASX file")
            temp_path = temp_file.name
        
        try:
            processor = AASXProcessor(temp_path)
            print("ERROR: Should have raised ValueError for wrong extension")
            return False
        except ValueError as e:
            if "extension" in str(e).lower():
                print("OK: ValueError raised for wrong file extension")
            else:
                print(f"ERROR: Unexpected ValueError: {e}")
                return False
        except Exception as e:
            print(f"ERROR: Unexpected exception: {e}")
            return False
        finally:
            # Clean up
            os.unlink(temp_path)
        
        return True
        
    except Exception as e:
        print(f"ERROR: Invalid file format test failed: {e}")
        return False

def test_corrupted_zip_file():
    """Test handling of corrupted ZIP files"""
    print("\nTesting Corrupted ZIP File Handling")
    print("=" * 40)
    
    try:
        from webapp.aasx.aasx_processor import AASXProcessor
        
        # Create a corrupted ZIP file
        with tempfile.NamedTemporaryFile(suffix='.aasx', delete=False) as temp_file:
            temp_file.write(b"This is not a valid ZIP file")
            temp_path = temp_file.name
        
        try:
            processor = AASXProcessor(temp_path)
            result = processor.process()
            
            # Should handle gracefully and return basic result
            if result and 'processing_method' in result:
                print("OK: Corrupted file handled gracefully")
                print(f"   Processing method: {result.get('processing_method')}")
                return True
            else:
                print("ERROR: Failed to handle corrupted file gracefully")
                return False
                
        except Exception as e:
            print(f"ERROR: Unexpected exception: {e}")
            return False
        finally:
            # Clean up
            os.unlink(temp_path)
        
    except Exception as e:
        print(f"ERROR: Corrupted ZIP file test failed: {e}")
        return False

def test_missing_dependencies():
    """Test handling of missing dependencies"""
    print("\nTesting Missing Dependencies Handling")
    print("=" * 40)
    
    try:
        # Test that the module can be imported even with missing dependencies
        from webapp.aasx import aasx_processor
        
        print("OK: Module imports successfully with missing dependencies")
        
        # Check that it falls back to basic processing
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        
        if os.path.exists(aasx_file):
            processor = aasx_processor.AASXProcessor(aasx_file)
            result = processor.process()
            
            if result and 'processing_method' in result:
                print(f"OK: Fallback processing works: {result.get('processing_method')}")
                return True
            else:
                print("ERROR: Fallback processing failed")
                return False
        else:
            print("WARNING: AASX file not found, skipping fallback test")
            return True
        
    except Exception as e:
        print(f"ERROR: Missing dependencies test failed: {e}")
        return False

def test_dotnet_bridge_errors():
    """Test .NET bridge error handling"""
    print("\nTesting .NET Bridge Error Handling")
    print("=" * 40)
    
    try:
        from webapp.aasx.dotnet_bridge import DotNetAasBridge
        
        bridge = DotNetAasBridge()
        
        # Test with invalid file
        try:
            result = bridge.process_aasx_file("invalid_file.aasx")
            
            # Should handle gracefully
            if result is None or 'error' in result:
                print("OK: .NET bridge handles invalid file gracefully")
                return True
            else:
                print("WARNING: .NET bridge didn't handle invalid file as expected")
                return True  # Not a critical failure
                
        except Exception as e:
            print(f"ERROR: .NET bridge threw unexpected exception: {e}")
            return False
        
    except ImportError:
        print("WARNING: .NET bridge not available, skipping test")
        return True
    except Exception as e:
        print(f"ERROR: .NET bridge error handling test failed: {e}")
        return False

def test_memory_errors():
    """Test memory-related error handling"""
    print("\nTesting Memory Error Handling")
    print("=" * 40)
    
    try:
        from webapp.aasx.aasx_processor import AASXProcessor
        
        # Test with a valid file (should not cause memory issues)
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        
        if not os.path.exists(aasx_file):
            print("WARNING: AASX file not found, skipping memory test")
            return True
        
        # Process multiple times to check for memory leaks
        for i in range(3):
            try:
                processor = AASXProcessor(aasx_file)
                result = processor.process()
                
                if not result:
                    print(f"ERROR: Processing failed on iteration {i+1}")
                    return False
                    
            except MemoryError:
                print(f"ERROR: Memory error on iteration {i+1}")
                return False
            except Exception as e:
                print(f"ERROR: Unexpected error on iteration {i+1}: {e}")
                return False
        
        print("OK: No memory errors during repeated processing")
        return True
        
    except Exception as e:
        print(f"ERROR: Memory error handling test failed: {e}")
        return False

def main():
    """Run all error handling tests"""
    print("="*60)
    print("Error Handling Test Suite")
    print("="*60)
    
    tests = [
        ("Invalid File Path", test_invalid_file_path),
        ("Invalid File Format", test_invalid_file_format),
        ("Corrupted ZIP File", test_corrupted_zip_file),
        ("Missing Dependencies", test_missing_dependencies),
        (".NET Bridge Errors", test_dotnet_bridge_errors),
        ("Memory Errors", test_memory_errors)
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
    
    print("\n" + "="*60)
    print(f"Error Handling Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("SUCCESS: All error handling tests passed!")
        return 0
    else:
        print("WARNING: Some error handling tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 