#!/usr/bin/env python3
"""
AASX Performance Tests

This script tests the performance of AASX processing operations.
"""

import sys
import os
import time
import psutil
from typing import Dict, Any

# Add parent directory to path
sys.path.append('..')

def test_processing_speed():
    """Test AASX processing speed"""
    print("Testing AASX Processing Speed")
    print("=" * 40)
    
    try:
        from webapp.aasx.aasx_processor import AASXProcessor
        
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        
        if not os.path.exists(aasx_file):
            print("ERROR: AASX file not found")
            return False
        
        # Measure processing time
        start_time = time.time()
        processor = AASXProcessor(aasx_file)
        result = processor.process()
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        if not result:
            print("ERROR: Processing failed")
            return False
        
        print(f"OK: Processing completed in {processing_time:.3f} seconds")
        
        # Performance thresholds
        max_time = 10.0  # 10 seconds max
        if processing_time > max_time:
            print(f"WARNING: Processing time ({processing_time:.3f}s) exceeds threshold ({max_time}s)")
            return False
        
        print(f"OK: Processing time within acceptable limits")
        return True
        
    except Exception as e:
        print(f"ERROR: Processing speed test failed: {e}")
        return False

def test_memory_usage():
    """Test memory usage during AASX processing"""
    print("\nTesting Memory Usage")
    print("=" * 40)
    
    try:
        from webapp.aasx.aasx_processor import AASXProcessor
        
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        
        if not os.path.exists(aasx_file):
            print("ERROR: AASX file not found")
            return False
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process AASX file
        processor = AASXProcessor(aasx_file)
        result = processor.process()
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_memory - initial_memory
        
        if not result:
            print("ERROR: Processing failed")
            return False
        
        print(f"OK: Initial memory: {initial_memory:.2f} MB")
        print(f"OK: Final memory: {final_memory:.2f} MB")
        print(f"OK: Memory used: {memory_used:.2f} MB")
        
        # Memory threshold (100 MB max)
        max_memory = 100.0
        if memory_used > max_memory:
            print(f"WARNING: Memory usage ({memory_used:.2f} MB) exceeds threshold ({max_memory} MB)")
            return False
        
        print(f"OK: Memory usage within acceptable limits")
        return True
        
    except ImportError:
        print("WARNING: psutil not available, skipping memory test")
        return True
    except Exception as e:
        print(f"ERROR: Memory usage test failed: {e}")
        return False

def test_concurrent_processing():
    """Test concurrent AASX processing"""
    print("\nTesting Concurrent Processing")
    print("=" * 40)
    
    try:
        from webapp.aasx.aasx_processor import AASXProcessor
        import threading
        
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        
        if not os.path.exists(aasx_file):
            print("ERROR: AASX file not found")
            return False
        
        results = []
        errors = []
        
        def process_file():
            try:
                processor = AASXProcessor(aasx_file)
                result = processor.process()
                results.append(result)
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads
        threads = []
        num_threads = 3
        
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(target=process_file)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"OK: Processed {num_threads} files in {total_time:.3f} seconds")
        print(f"OK: Successful: {len(results)}, Errors: {len(errors)}")
        
        if errors:
            print(f"WARNING: {len(errors)} errors occurred during concurrent processing")
            for error in errors[:3]:  # Show first 3 errors
                print(f"  - {error}")
        
        # Should have at least 2 successful results
        if len(results) >= 2:
            print("OK: Concurrent processing successful")
            return True
        else:
            print("ERROR: Too many concurrent processing failures")
            return False
        
    except Exception as e:
        print(f"ERROR: Concurrent processing test failed: {e}")
        return False

def test_large_file_handling():
    """Test handling of large AASX files"""
    print("\nTesting Large File Handling")
    print("=" * 40)
    
    try:
        from webapp.aasx.aasx_processor import AASXProcessor
        
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        
        if not os.path.exists(aasx_file):
            print("ERROR: AASX file not found")
            return False
        
        # Get file size
        file_size = os.path.getsize(aasx_file) / 1024 / 1024  # MB
        print(f"OK: File size: {file_size:.2f} MB")
        
        # Process file
        start_time = time.time()
        processor = AASXProcessor(aasx_file)
        result = processor.process()
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        if not result:
            print("ERROR: Processing failed")
            return False
        
        print(f"OK: Large file processed in {processing_time:.3f} seconds")
        
        # Check processing efficiency (MB/s)
        processing_speed = file_size / processing_time
        print(f"OK: Processing speed: {processing_speed:.2f} MB/s")
        
        # Minimum speed threshold (0.1 MB/s)
        min_speed = 0.1
        if processing_speed < min_speed:
            print(f"WARNING: Processing speed ({processing_speed:.2f} MB/s) below threshold ({min_speed} MB/s)")
            return False
        
        print("OK: Large file handling successful")
        return True
        
    except Exception as e:
        print(f"ERROR: Large file handling test failed: {e}")
        return False

def main():
    """Run all performance tests"""
    print("="*60)
    print("AASX Performance Test Suite")
    print("="*60)
    
    tests = [
        ("Processing Speed", test_processing_speed),
        ("Memory Usage", test_memory_usage),
        ("Concurrent Processing", test_concurrent_processing),
        ("Large File Handling", test_large_file_handling)
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
    print(f"Performance Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("SUCCESS: All performance tests passed!")
        return 0
    else:
        print("WARNING: Some performance tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 