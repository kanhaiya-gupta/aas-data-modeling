#!/usr/bin/env python3
"""
AASX Data Quality Tests

This script tests the quality and integrity of AASX data processing.
Validates data completeness, consistency, and structural integrity.
"""

import sys
import os
import json
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append('..')

def test_data_completeness():
    """Test that all required AASX data fields are present"""
    print("Testing Data Completeness")
    print("=" * 40)
    
    try:
        from webapp.aasx.aasx_processor import AASXProcessor
        
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        
        if not os.path.exists(aasx_file):
            print("ERROR: AASX file not found")
            return False
        
        processor = AASXProcessor(aasx_file)
        result = processor.process()
        
        if not result:
            print("ERROR: Failed to process AASX file")
            return False
        
        # Check required top-level fields
        required_fields = ['processing_method', 'assets', 'submodels', 'documents', 'metadata']
        missing_fields = []
        
        for field in required_fields:
            if field not in result:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"ERROR: Missing required fields: {missing_fields}")
            return False
        
        print("OK: All required top-level fields present")
        
        # Check assets have required fields
        assets = result.get('assets', [])
        if assets:
            required_asset_fields = ['id', 'type']
            for i, asset in enumerate(assets):
                missing_asset_fields = [f for f in required_asset_fields if f not in asset]
                if missing_asset_fields:
                    print(f"ERROR: Asset {i} missing fields: {missing_asset_fields}")
                    return False
            print(f"OK: All {len(assets)} assets have required fields")
        
        # Check submodels have required fields
        submodels = result.get('submodels', [])
        if submodels:
            required_submodel_fields = ['id', 'type']
            for i, submodel in enumerate(submodels):
                missing_submodel_fields = [f for f in required_submodel_fields if f not in submodel]
                if missing_submodel_fields:
                    print(f"ERROR: Submodel {i} missing fields: {missing_submodel_fields}")
                    return False
            print(f"OK: All {len(submodels)} submodels have required fields")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Data completeness test failed: {e}")
        return False

def test_data_consistency():
    """Test that AASX data is internally consistent"""
    print("\nTesting Data Consistency")
    print("=" * 40)
    
    try:
        from webapp.aasx.aasx_processor import AASXProcessor
        
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        processor = AASXProcessor(aasx_file)
        result = processor.process()
        
        if not result:
            print("ERROR: Failed to process AASX file")
            return False
        
        # Check for duplicate IDs
        asset_ids = [asset.get('id') for asset in result.get('assets', []) if asset.get('id')]
        submodel_ids = [submodel.get('id') for submodel in result.get('submodels', []) if submodel.get('id')]
        
        duplicate_asset_ids = [id for id in set(asset_ids) if asset_ids.count(id) > 1]
        duplicate_submodel_ids = [id for id in set(submodel_ids) if submodel_ids.count(id) > 1]
        
        if duplicate_asset_ids:
            print(f"ERROR: Duplicate asset IDs found: {duplicate_asset_ids}")
            return False
        
        if duplicate_submodel_ids:
            print(f"ERROR: Duplicate submodel IDs found: {duplicate_submodel_ids}")
            return False
        
        print("OK: No duplicate IDs found")
        
        # Check data types are consistent
        assets = result.get('assets', [])
        for asset in assets:
            if 'id' in asset and not isinstance(asset['id'], str):
                print(f"ERROR: Asset ID should be string, got {type(asset['id'])}")
                return False
        
        submodels = result.get('submodels', [])
        for submodel in submodels:
            if 'id' in submodel and not isinstance(submodel['id'], str):
                print(f"ERROR: Submodel ID should be string, got {type(submodel['id'])}")
                return False
        
        print("OK: Data types are consistent")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Data consistency test failed: {e}")
        return False

def test_data_integrity():
    """Test that AASX data maintains structural integrity"""
    print("\nTesting Data Integrity")
    print("=" * 40)
    
    try:
        from webapp.aasx.aasx_processor import AASXProcessor
        
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        processor = AASXProcessor(aasx_file)
        result = processor.process()
        
        if not result:
            print("ERROR: Failed to process AASX file")
            return False
        
        # Check metadata integrity
        metadata = result.get('metadata', {})
        if 'file_path' not in metadata:
            print("ERROR: Missing file_path in metadata")
            return False
        
        if 'processing_timestamp' not in metadata:
            print("ERROR: Missing processing_timestamp in metadata")
            return False
        
        print("OK: Metadata integrity verified")
        
        # Check that processing method is valid
        valid_methods = ['basic_zip_processing', 'advanced_aas_libraries', 'enhanced_zip_processing']
        processing_method = result.get('processing_method', '')
        
        if processing_method not in valid_methods:
            print(f"WARNING: Unknown processing method: {processing_method}")
        else:
            print(f"OK: Processing method '{processing_method}' is valid")
        
        # Check that arrays are actually arrays
        if not isinstance(result.get('assets', []), list):
            print("ERROR: Assets should be a list")
            return False
        
        if not isinstance(result.get('submodels', []), list):
            print("ERROR: Submodels should be a list")
            return False
        
        if not isinstance(result.get('documents', []), list):
            print("ERROR: Documents should be a list")
            return False
        
        print("OK: Data structure integrity verified")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Data integrity test failed: {e}")
        return False

def test_data_validation():
    """Test that AASX data passes validation rules"""
    print("\nTesting Data Validation")
    print("=" * 40)
    
    try:
        from webapp.aasx.aasx_processor import AASXProcessor
        
        aasx_file = "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"
        processor = AASXProcessor(aasx_file)
        result = processor.process()
        
        if not result:
            print("ERROR: Failed to process AASX file")
            return False
        
        # Validate ID formats (should be non-empty strings)
        assets = result.get('assets', [])
        for asset in assets:
            asset_id = asset.get('id', '')
            if not asset_id or not isinstance(asset_id, str):
                print(f"ERROR: Invalid asset ID: {asset_id}")
                return False
        
        submodels = result.get('submodels', [])
        for submodel in submodels:
            submodel_id = submodel.get('id', '')
            if not submodel_id or not isinstance(submodel_id, str):
                print(f"ERROR: Invalid submodel ID: {submodel_id}")
                return False
        
        print("OK: All IDs are valid")
        
        # Validate that we have at least some data
        total_assets = len(assets)
        total_submodels = len(submodels)
        total_documents = len(result.get('documents', []))
        
        if total_assets == 0 and total_submodels == 0:
            print("WARNING: No assets or submodels found")
        else:
            print(f"OK: Found {total_assets} assets, {total_submodels} submodels, {total_documents} documents")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Data validation test failed: {e}")
        return False

def main():
    """Run all data quality tests"""
    print("="*60)
    print("AASX Data Quality Test Suite")
    print("="*60)
    
    tests = [
        ("Data Completeness", test_data_completeness),
        ("Data Consistency", test_data_consistency),
        ("Data Integrity", test_data_integrity),
        ("Data Validation", test_data_validation)
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
    print(f"Data Quality Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("SUCCESS: All data quality tests passed!")
        return 0
    else:
        print("WARNING: Some data quality tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 