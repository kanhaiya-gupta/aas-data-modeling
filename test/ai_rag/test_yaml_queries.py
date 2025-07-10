#!/usr/bin/env python3
"""
Test script for YAML query configuration validation
Tests the AI/RAG YAML query configuration file for syntax and structure
"""

import yaml
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """Load YAML configuration file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"ERROR: Configuration file not found: {file_path}")
        return {}
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML syntax in {file_path}: {e}")
        return {}

def validate_global_settings(config: Dict[str, Any]) -> bool:
    """Validate global settings section"""
    print("Validating global settings...")
    
    if 'global_settings' not in config:
        print("ERROR: Missing 'global_settings' section")
        return False
    
    global_settings = config['global_settings']
    required_fields = ['default_model', 'max_tokens', 'temperature']
    
    for field in required_fields:
        if field not in global_settings:
            print(f"ERROR: Missing required field '{field}' in global_settings")
            return False
    
    print("PASS: Global settings validation passed")
    return True

def validate_query_categories(config: Dict[str, Any]) -> bool:
    """Validate query categories section"""
    print("Validating query categories...")
    
    if 'query_categories' not in config:
        print("ERROR: Missing 'query_categories' section")
        return False
    
    categories = config['query_categories']
    if not isinstance(categories, dict):
        print("ERROR: 'query_categories' must be a dictionary")
        return False
    
    for category_name, category_config in categories.items():
        if not isinstance(category_config, dict):
            print(f"ERROR: Category '{category_name}' must be a dictionary")
            return False
        
        if 'description' not in category_config:
            print(f"ERROR: Category '{category_name}' missing description")
            return False
        
        if 'queries' not in category_config:
            print(f"ERROR: Category '{category_name}' missing queries")
            return False
        
        if not isinstance(category_config['queries'], list):
            print(f"ERROR: Category '{category_name}' queries must be a list")
            return False
    
    print("PASS: Query categories validation passed")
    return True

def validate_demo_queries(config: Dict[str, Any]) -> bool:
    """Validate demo queries section"""
    print("Validating demo queries...")
    
    if 'demo_queries' not in config:
        print("ERROR: Missing 'demo_queries' section")
        return False
    
    demo_queries = config['demo_queries']
    if not isinstance(demo_queries, list):
        print("ERROR: 'demo_queries' must be a list")
        return False
    
    for i, query in enumerate(demo_queries):
        if not isinstance(query, dict):
            print(f"ERROR: Demo query {i} must be a dictionary")
            return False
        
        required_fields = ['name', 'query', 'analysis_type']
        for field in required_fields:
            if field not in query:
                print(f"ERROR: Demo query {i} missing required field '{field}'")
                return False
    
    print("PASS: Demo queries validation passed")
    return True

def validate_query_templates(config: Dict[str, Any]) -> bool:
    """Validate query templates section"""
    print("Validating query templates...")
    
    if 'query_templates' not in config:
        print("ERROR: Missing 'query_templates' section")
        return False
    
    templates = config['query_templates']
    if not isinstance(templates, dict):
        print("ERROR: 'query_templates' must be a dictionary")
        return False
    
    for template_name, template_config in templates.items():
        if not isinstance(template_config, dict):
            print(f"ERROR: Template '{template_name}' must be a dictionary")
            return False
        
        if 'template' not in template_config:
            print(f"ERROR: Template '{template_name}' missing template field")
            return False
        
        if 'variables' not in template_config:
            print(f"ERROR: Template '{template_name}' missing variables field")
            return False
    
    print("PASS: Query templates validation passed")
    return True

def validate_individual_queries(config: Dict[str, Any]) -> bool:
    """Validate individual queries in categories"""
    print("Validating individual queries...")
    
    categories = config.get('query_categories', {})
    total_queries = 0
    valid_queries = 0
    
    for category_name, category_config in categories.items():
        queries = category_config.get('queries', [])
        total_queries += len(queries)
        
        for i, query in enumerate(queries):
            if not isinstance(query, dict):
                print(f"ERROR: Query {i} in category '{category_name}' must be a dictionary")
                continue
            
            required_fields = ['name', 'query', 'analysis_type']
            missing_fields = [field for field in required_fields if field not in query]
            
            if missing_fields:
                print(f"ERROR: Query '{query.get('name', f'#{i}')}' in category '{category_name}' missing fields: {missing_fields}")
                continue
            
            # Validate analysis type
            valid_types = ['general', 'quality', 'risk', 'optimization']
            if query['analysis_type'] not in valid_types:
                print(f"ERROR: Query '{query['name']}' has invalid analysis_type: {query['analysis_type']}")
                continue
            
            valid_queries += 1
    
    print(f"PASS: Individual queries validation: {valid_queries}/{total_queries} queries valid")
    return valid_queries == total_queries

def test_yaml_syntax(config_path: str) -> bool:
    """Test YAML syntax and basic structure"""
    print(f"Testing YAML syntax: {config_path}")
    
    config = load_yaml_config(config_path)
    if not config:
        return False
    
    # Run all validations
    validations = [
        validate_global_settings,
        validate_query_categories,
        validate_demo_queries,
        validate_query_templates,
        validate_individual_queries
    ]
    
    all_valid = True
    for validation in validations:
        if not validation(config):
            all_valid = False
    
    return all_valid

def test_query_execution_simulation(config_path: str) -> bool:
    """Simulate query execution to test template variables"""
    print("Testing query execution simulation...")
    
    config = load_yaml_config(config_path)
    if not config:
        return False
    
    templates = config.get('query_templates', {})
    demo_queries = config.get('demo_queries', [])
    
    # Test template variable substitution
    for template_name, template_config in templates.items():
        template = template_config.get('template', '')
        variables = template_config.get('variables', {})
        
        try:
            # Simple template variable substitution test
            test_query = template
            for var_name, var_value in variables.items():
                placeholder = f"{{{var_name}}}"
                if placeholder in test_query:
                    test_query = test_query.replace(placeholder, str(var_value))
            
            print(f"PASS: Template '{template_name}' variable substitution successful")
        except Exception as e:
            print(f"ERROR in template '{template_name}': {e}")
            return False
    
    # Test demo queries
    for i, query in enumerate(demo_queries):
        try:
            query_text = query.get('query', '')
            analysis_type = query.get('analysis_type', '')
            
            if not query_text or not analysis_type:
                print(f"ERROR: Demo query {i} has empty query or analysis_type")
                return False
            
            print(f"PASS: Demo query '{query.get('name', f'#{i}')}' validation successful")
        except Exception as e:
            print(f"ERROR in demo query {i}: {e}")
            return False
    
    print("PASS: Query execution simulation passed")
    return True

def test_configuration_completeness(config_path: str) -> bool:
    """Test configuration completeness and consistency"""
    print("Testing configuration completeness...")
    
    config = load_yaml_config(config_path)
    if not config:
        return False
    
    # Check for required sections
    required_sections = ['global_settings', 'query_categories', 'demo_queries', 'query_templates']
    missing_sections = [section for section in required_sections if section not in config]
    
    if missing_sections:
        print(f"ERROR: Missing required sections: {missing_sections}")
        return False
    
    # Check for at least one demo query
    demo_queries = config.get('demo_queries', [])
    if not demo_queries:
        print("ERROR: No demo queries found")
        return False
    
    # Check for at least one category
    categories = config.get('query_categories', {})
    if not categories:
        print("ERROR: No query categories found")
        return False
    
    # Check for at least one template
    templates = config.get('query_templates', {})
    if not templates:
        print("ERROR: No query templates found")
        return False
    
    print("PASS: Configuration completeness check passed")
    return True

def main():
    """Main test function"""
    print("Starting YAML Query Configuration Tests")
    print("=" * 50)
    
    # Find the config file
    config_paths = [
        "config/ai_rag_queries.yaml",
        "../config/ai_rag_queries.yaml",
        "../../config/ai_rag_queries.yaml"
    ]
    
    config_path = None
    for path in config_paths:
        if os.path.exists(path):
            config_path = path
            break
    
    if not config_path:
        print("ERROR: Could not find ai_rag_queries.yaml configuration file")
        print("Searched in:")
        for path in config_paths:
            print(f"  - {path}")
        return False
    
    print(f"Found configuration file: {config_path}")
    print()
    
    # Run all tests
    tests = [
        ("YAML Syntax", test_yaml_syntax),
        ("Query Execution Simulation", test_query_execution_simulation),
        ("Configuration Completeness", test_configuration_completeness)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} Test...")
        print("-" * 30)
        
        try:
            result = test_func(config_path)
            results.append((test_name, result))
            
            if result:
                print(f"PASS: {test_name}")
            else:
                print(f"FAIL: {test_name}")
        except Exception as e:
            print(f"ERROR: {test_name} - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All tests passed! YAML configuration is valid.")
        return True
    else:
        print("WARNING: Some tests failed. Please review the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 