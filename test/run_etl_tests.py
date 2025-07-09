#!/usr/bin/env python3
"""
AASX ETL Pipeline Test Runner

Comprehensive test runner for the complete ETL (Extract, Transform, Load) pipeline
including all components and integration tests.
"""

import unittest
import sys
import os
import time
import json
from pathlib import Path

# Add the webapp directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'webapp'))

def run_etl_tests():
    """Run all ETL pipeline tests"""
    
    print("=" * 80)
    print("AASX ETL PIPELINE TEST SUITE")
    print("=" * 80)
    
    # Test categories
    test_categories = {
        'Extract (Processor)': 'test.aasx.test_aasx_processor',
        'Transform (Transformer)': 'test.aasx.test_aasx_transformer', 
        'Load (Loader)': 'test.aasx.test_aasx_loader',
        'Complete Pipeline': 'test.aasx.test_aasx_etl_pipeline',
        'Integration': 'test.integration.test_aasx_integration',
        'Performance': 'test.performance.test_aasx_performance',
        'Data Quality': 'test.data_quality.test_aasx_data_quality',
        'Error Handling': 'test.error_handling.test_aasx_error_handling'
    }
    
    # Results tracking
    results = {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'errors': 0,
        'categories': {}
    }
    
    start_time = time.time()
    
    # Run each test category
    for category_name, test_module in test_categories.items():
        print(f"\n{'='*60}")
        print(f"Testing: {category_name}")
        print(f"{'='*60}")
        
        try:
            # Import and run test module
            module = __import__(test_module, fromlist=['*'])
            
            # Create test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            
            # Run tests
            runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
            test_result = runner.run(suite)
            
            # Record results
            category_results = {
                'tests_run': test_result.testsRun,
                'failures': len(test_result.failures),
                'errors': len(test_result.errors),
                'skipped': len(test_result.skipped) if hasattr(test_result, 'skipped') else 0
            }
            
            results['categories'][category_name] = category_results
            results['total_tests'] += test_result.testsRun
            results['passed'] += test_result.testsRun - len(test_result.failures) - len(test_result.errors)
            results['failed'] += len(test_result.failures)
            results['errors'] += len(test_result.errors)
            
            # Print category summary
            print(f"\n{category_name} Results:")
            print(f"  Tests Run: {test_result.testsRun}")
            print(f"  Passed: {test_result.testsRun - len(test_result.failures) - len(test_result.errors)}")
            print(f"  Failed: {len(test_result.failures)}")
            print(f"  Errors: {len(test_result.errors)}")
            
            if test_result.failures:
                print(f"\nFailures in {category_name}:")
                for test, traceback in test_result.failures:
                    print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
            
            if test_result.errors:
                print(f"\nErrors in {category_name}:")
                for test, traceback in test_result.errors:
                    print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
                    
        except ImportError as e:
            print(f"Warning: Could not import {test_module}: {e}")
            results['categories'][category_name] = {
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0,
                'import_error': str(e)
            }
            results['errors'] += 1
        except Exception as e:
            print(f"Error running {category_name} tests: {e}")
            results['categories'][category_name] = {
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0,
                'runtime_error': str(e)
            }
            results['errors'] += 1
    
    # Calculate total time
    total_time = time.time() - start_time
    
    # Print final summary
    print(f"\n{'='*80}")
    print("ETL PIPELINE TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Errors: {results['errors']}")
    print(f"Success Rate: {(results['passed']/results['total_tests']*100):.1f}%" if results['total_tests'] > 0 else "Success Rate: N/A")
    print(f"Total Time: {total_time:.2f} seconds")
    
    # Print category breakdown
    print(f"\nCategory Breakdown:")
    for category, stats in results['categories'].items():
        if stats['tests_run'] > 0:
            success_rate = ((stats['tests_run'] - stats['failures'] - stats['errors']) / stats['tests_run']) * 100
            print(f"  {category}: {stats['tests_run']} tests, {success_rate:.1f}% success")
        else:
            print(f"  {category}: {stats['tests_run']} tests, N/A")
    
    # Save results to file
    results['total_time'] = total_time
    results['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
    
    output_file = Path(__file__).parent / 'etl_test_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Return success/failure
    return results['failed'] == 0 and results['errors'] == 0

def run_specific_tests(test_pattern=None):
    """Run specific tests based on pattern"""
    
    if test_pattern:
        print(f"Running tests matching pattern: {test_pattern}")
        
        # Discover and run tests matching pattern
        loader = unittest.TestLoader()
        suite = loader.discover('test', pattern=f'*{test_pattern}*')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return len(result.failures) == 0 and len(result.errors) == 0
    else:
        return run_etl_tests()

def run_performance_tests():
    """Run performance benchmarks"""
    print("Running ETL Performance Tests...")
    
    try:
        from test.performance.test_aasx_performance import TestAASXPerformance
        suite = unittest.TestLoader().loadTestsFromTestCase(TestAASXPerformance)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return len(result.failures) == 0 and len(result.errors) == 0
    except ImportError:
        print("Performance tests not available")
        return True

def run_integration_tests():
    """Run integration tests"""
    print("Running ETL Integration Tests...")
    
    try:
        from test.integration.test_aasx_integration import TestAASXIntegration
        suite = unittest.TestLoader().loadTestsFromTestCase(TestAASXIntegration)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return len(result.failures) == 0 and len(result.errors) == 0
    except ImportError:
        print("Integration tests not available")
        return True

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run AASX ETL Pipeline Tests')
    parser.add_argument('--pattern', '-p', help='Run tests matching pattern')
    parser.add_argument('--performance', action='store_true', help='Run performance tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--quick', '-q', action='store_true', help='Run quick tests only')
    
    args = parser.parse_args()
    
    if args.performance:
        success = run_performance_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.pattern:
        success = run_specific_tests(args.pattern)
    elif args.quick:
        # Run only core ETL tests
        print("Running Quick ETL Tests...")
        success = run_specific_tests('test_aasx_etl_pipeline')
    else:
        success = run_etl_tests()
    
    sys.exit(0 if success else 1) 