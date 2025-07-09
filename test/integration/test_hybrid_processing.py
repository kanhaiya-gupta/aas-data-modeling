#!/usr/bin/env python3
"""
Test Hybrid AASX Processing (Python + .NET)

This script tests the hybrid processing approach.
"""

import sys
import os

# Add parent directory to path
sys.path.append('..')

def test_hybrid_processing():
    """Test hybrid processing functionality"""
    print("Testing Hybrid AASX Processing (Python + .NET)")
    print("=" * 60)
    
    try:
        # Import both Python and .NET processors
        from webapp.aasx.aasx_processor import AASXProcessor
        from webapp.aasx.dotnet_bridge import DotNetAasBridge
        
        print("OK: Both processors imported successfully")
        
        # Test with AASX file
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        
        if not os.path.exists(aasx_file):
            print(f"ERROR: AASX file not found: {aasx_file}")
            return False
        
        print(f"OK: Testing with: {aasx_file}")
        
        # Create instances
        python_processor = AASXProcessor(aasx_file)
        dotnet_bridge = DotNetAasBridge()
        
        print("OK: Processor instances created")
        
        # Test Python processing
        print("\nTesting Python processing...")
        python_result = python_processor.process()
        
        if python_result:
            print("OK: Python processing successful")
            print(f"   Method: {python_result.get('processing_method', 'unknown')}")
        else:
            print("WARNING: Python processing failed")
        
        # Test .NET processing
        print("\nTesting .NET processing...")
        if dotnet_bridge.is_available():
            dotnet_result = dotnet_bridge.process_aasx_file(aasx_file)
            
            if dotnet_result:
                print("OK: .NET processing successful")
                print(f"   Method: {dotnet_result.get('processing_method', 'unknown')}")
            else:
                print("WARNING: .NET processing failed")
        else:
            print("WARNING: .NET processor not available")
        
        # Compare results if both succeeded
        if python_result and dotnet_result:
            print("\nComparing results...")
            
            python_assets = len(python_result.get('assets', []))
            dotnet_assets = len(dotnet_result.get('assets', []))
            
            python_submodels = len(python_result.get('submodels', []))
            dotnet_submodels = len(dotnet_result.get('submodels', []))
            
            print(f"   Assets - Python: {python_assets}, .NET: {dotnet_assets}")
            print(f"   Submodels - Python: {python_submodels}, .NET: {dotnet_submodels}")
            
            if python_assets == dotnet_assets and python_submodels == dotnet_submodels:
                print("OK: Results match between Python and .NET")
            else:
                print("WARNING: Results differ between Python and .NET")
        
        return True
        
    except ImportError as e:
        print(f"ERROR: Import error: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Hybrid processing test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_hybrid_processing()
    if success:
        print("\nSUCCESS: Hybrid processing test completed!")
        sys.exit(0)
    else:
        print("\nFAILED: Hybrid processing test failed!")
        sys.exit(1) 