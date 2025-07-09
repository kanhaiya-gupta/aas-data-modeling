#!/usr/bin/env python3
"""
Web Application Route Tests

This script tests the web application routes and endpoints.
"""

import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append('..')

def test_route_imports():
    """Test that webapp routes can be imported"""
    print("Testing Webapp Route Imports")
    print("=" * 40)
    
    try:
        from webapp import app
        print("OK: FastAPI app imported successfully")
        
        from webapp.routes import router
        print("OK: Routes module imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"ERROR: Import error: {e}")
        return False

def test_route_registration():
    """Test that routes are properly registered"""
    print("\nTesting Route Registration")
    print("=" * 40)
    
    try:
        from webapp import app
        
        # Check that app has routes
        routes = app.routes
        if not routes:
            print("ERROR: No routes found in app")
            return False
        
        print(f"OK: Found {len(routes)} routes registered")
        
        # Check for specific routes
        route_paths = [route.path for route in routes if hasattr(route, 'path')]
        
        expected_routes = ['/', '/aasx', '/ai-rag', '/twin-registry', '/certificate-manager', '/analytics']
        found_routes = []
        
        for expected in expected_routes:
            if any(expected in path for path in route_paths):
                found_routes.append(expected)
                print(f"OK: Route '{expected}' found")
            else:
                print(f"WARNING: Route '{expected}' not found")
        
        if len(found_routes) >= 3:  # At least half of expected routes
            print(f"OK: Found {len(found_routes)}/{len(expected_routes)} expected routes")
            return True
        else:
            print(f"ERROR: Too few routes found: {len(found_routes)}/{len(expected_routes)}")
            return False
        
    except Exception as e:
        print(f"ERROR: Route registration test failed: {e}")
        return False

def test_template_availability():
    """Test that required templates are available"""
    print("\nTesting Template Availability")
    print("=" * 40)
    
    try:
        template_dir = "../webapp/templates"
        
        if not os.path.exists(template_dir):
            print(f"ERROR: Template directory not found: {template_dir}")
            return False
        
        required_templates = [
            "base.html",
            "index.html",
            "aasx.html",
            "twin.html"
        ]
        
        missing_templates = []
        for template in required_templates:
            template_path = os.path.join(template_dir, template)
            if os.path.exists(template_path):
                print(f"OK: Template '{template}' found")
            else:
                missing_templates.append(template)
                print(f"WARNING: Template '{template}' missing")
        
        if missing_templates:
            print(f"WARNING: Missing {len(missing_templates)} templates")
        else:
            print("OK: All required templates available")
        
        return len(missing_templates) == 0
        
    except Exception as e:
        print(f"ERROR: Template availability test failed: {e}")
        return False

def test_static_files():
    """Test that static files are available"""
    print("\nTesting Static Files")
    print("=" * 40)
    
    try:
        static_dir = "../webapp/static"
        
        if not os.path.exists(static_dir):
            print(f"ERROR: Static directory not found: {static_dir}")
            return False
        
        # Check for CSS and JS files
        css_files = []
        js_files = []
        
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                if file.endswith('.css'):
                    css_files.append(file)
                elif file.endswith('.js'):
                    js_files.append(file)
        
        print(f"OK: Found {len(css_files)} CSS files")
        print(f"OK: Found {len(js_files)} JS files")
        
        if len(css_files) > 0 and len(js_files) > 0:
            print("OK: Static files available")
            return True
        else:
            print("WARNING: Few static files found")
            return False
        
    except Exception as e:
        print(f"ERROR: Static files test failed: {e}")
        return False

def test_app_configuration():
    """Test that the app is properly configured"""
    print("\nTesting App Configuration")
    print("=" * 40)
    
    try:
        from webapp import app
        
        # Check app title
        if hasattr(app, 'title') and app.title:
            print(f"OK: App title set: {app.title}")
        else:
            print("WARNING: App title not set")
        
        # Check app version
        if hasattr(app, 'version') and app.version:
            print(f"OK: App version set: {app.version}")
        else:
            print("WARNING: App version not set")
        
        # Check that app is a FastAPI instance
        from fastapi import FastAPI
        if isinstance(app, FastAPI):
            print("OK: App is FastAPI instance")
            return True
        else:
            print("ERROR: App is not a FastAPI instance")
            return False
        
    except Exception as e:
        print(f"ERROR: App configuration test failed: {e}")
        return False

def main():
    """Run all webapp tests"""
    print("="*60)
    print("Web Application Test Suite")
    print("="*60)
    
    tests = [
        ("Route Imports", test_route_imports),
        ("Route Registration", test_route_registration),
        ("Template Availability", test_template_availability),
        ("Static Files", test_static_files),
        ("App Configuration", test_app_configuration)
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
    print(f"Webapp Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("SUCCESS: All webapp tests passed!")
        return 0
    else:
        print("WARNING: Some webapp tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 