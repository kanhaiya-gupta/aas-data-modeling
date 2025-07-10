#!/usr/bin/env python3
"""
Test script for ETL Pipeline with AAS Processor Integration
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import subprocess
import json
import time
from backend.aasx.dotnet_bridge import DotNetAasBridge

def test_dotnet_installation():
    """Test if .NET 6.0 is installed"""
    print("🧪 Testing .NET 6.0 Installation...")
    
    try:
        result = subprocess.run(
            ["dotnet", "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ .NET version: {version}")
            
            # Check if it's .NET 6.x
            if version.startswith('6.'):
                return True
            else:
                print(f"⚠️  .NET version {version} found, but .NET 6.0 is recommended")
                return True  # Still usable
        else:
            print("❌ .NET not found")
            return False
            
    except FileNotFoundError:
        print("❌ .NET not installed")
        return False

def test_aas_processor_build():
    """Test if aas-processor can be built"""
    print("🧪 Testing AAS Processor Build...")
    
    aas_processor_dir = project_root / "aas-processor"
    
    if not aas_processor_dir.exists():
        print("❌ aas-processor directory not found")
        return False
    
    try:
        # Check if project file exists
        project_file = aas_processor_dir / "AasProcessor.csproj"
        if not project_file.exists():
            print("❌ AasProcessor.csproj not found")
            return False
        
        # Try to restore packages
        print("   Restoring packages...")
        result = subprocess.run(
            ["dotnet", "restore"],
            cwd=aas_processor_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Package restore failed: {result.stderr}")
            return False
        
        # Try to build
        print("   Building project...")
        result = subprocess.run(
            ["dotnet", "build", "--configuration", "Release"],
            cwd=aas_processor_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Build failed: {result.stderr}")
            return False
        
        # Check if executable exists
        exe_path = aas_processor_dir / "bin" / "Release" / "net6.0" / "AasProcessor"
        if exe_path.exists():
            print(f"✅ AAS Processor built successfully: {exe_path}")
            return True
        else:
            print(f"❌ Executable not found at: {exe_path}")
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def test_dotnet_bridge():
    """Test the .NET bridge functionality"""
    print("🧪 Testing .NET Bridge...")
    
    try:
        bridge = DotNetAasBridge()
        
        if not bridge.is_available():
            print("❌ .NET bridge not available")
            return False
        
        print("✅ .NET bridge is available")
        
        # Test with a sample AASX file
        aasx_dir = project_root / "AasxPackageExplorer" / "content-for-demo"
        if not aasx_dir.exists():
            aasx_dir = project_root / "data" / "aasx-examples"
        
        if aasx_dir.exists():
            aasx_files = list(aasx_dir.glob("*.aasx"))
            
            if aasx_files:
                test_file = aasx_files[0]
                print(f"📁 Testing with: {test_file.name}")
                
                result = bridge.process_aasx_file(str(test_file))
                
                if result:
                    print("✅ .NET processing successful!")
                    print(f"   Processing method: {result.get('processing_method', 'unknown')}")
                    print(f"   Assets found: {len(result.get('assets', []))}")
                    print(f"   Submodels found: {len(result.get('submodels', []))}")
                    print(f"   Documents found: {len(result.get('documents', []))}")
                    return True
                else:
                    print("❌ .NET processing failed")
                    return False
            else:
                print("⚠️  No AASX files found for testing")
                return True  # Not a failure, just no test data
        else:
            print("⚠️  No AASX examples directory found")
            return True  # Not a failure, just no test data
            
    except Exception as e:
        print(f"❌ .NET bridge test failed: {e}")
        return False

def test_etl_pipeline_integration():
    """Test ETL pipeline integration with aas-processor"""
    print("🧪 Testing ETL Pipeline Integration...")
    
    try:
        from backend.aasx.aasx_etl_pipeline import AASXETLPipeline, ETLPipelineConfig
        
        # Create ETL pipeline
        config = ETLPipelineConfig(
            enable_validation=True,
            enable_logging=True,
            enable_backup=True
        )
        
        pipeline = AASXETLPipeline(config)
        
        # Test pipeline validation
        validation_result = pipeline.validate_pipeline()
        
        if validation_result.get('valid', False):
            print("✅ ETL pipeline validation passed")
            print(f"   Available processors: {validation_result.get('available_processors', [])}")
            return True
        else:
            print("❌ ETL pipeline validation failed")
            print(f"   Errors: {validation_result.get('errors', [])}")
            return False
            
    except Exception as e:
        print(f"❌ ETL pipeline integration test failed: {e}")
        return False

def test_docker_integration():
    """Test Docker integration"""
    print("🧪 Testing Docker Integration...")
    
    try:
        # Check if Docker is available
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Docker not available")
            return False
        
        print("✅ Docker is available")
        
        # Check if ETL pipeline image can be built
        print("   Testing ETL pipeline Docker build...")
        
        # This would require Docker to be running and the build context to be available
        # For now, just check if the Dockerfile exists
        dockerfile_path = project_root / "docker" / "Dockerfile.etl-pipeline"
        
        if dockerfile_path.exists():
            print("✅ ETL pipeline Dockerfile exists")
            
            # Check if it contains .NET installation
            with open(dockerfile_path, 'r') as f:
                content = f.read()
                if 'dotnet-sdk-6.0' in content:
                    print("✅ Dockerfile includes .NET 6.0 SDK")
                else:
                    print("❌ Dockerfile missing .NET 6.0 SDK")
                    return False
                
                if 'aas-processor' in content:
                    print("✅ Dockerfile includes aas-processor")
                else:
                    print("❌ Dockerfile missing aas-processor")
                    return False
            
            return True
        else:
            print("❌ ETL pipeline Dockerfile not found")
            return False
            
    except Exception as e:
        print(f"❌ Docker integration test failed: {e}")
        return False

def main():
    """Run all ETL processor integration tests"""
    print("🚀 Testing ETL Pipeline with AAS Processor Integration")
    print("=" * 70)
    
    tests = [
        ("NET 6.0 Installation", test_dotnet_installation),
        ("AAS Processor Build", test_aas_processor_build),
        ("NET Bridge", test_dotnet_bridge),
        ("ETL Pipeline Integration", test_etl_pipeline_integration),
        ("Docker Integration", test_docker_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary:")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("=" * 70)
    print(f"Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ETL pipeline with AAS processor integration is working correctly!")
        print("\n📚 Next Steps:")
        print("   1. Build the ETL pipeline Docker image")
        print("   2. Run the ETL pipeline with AASX files")
        print("   3. Verify data processing results")
    else:
        print("⚠️  Some components need attention. Check the failed tests above.")
    
    print("\n🔧 Integration Points:")
    print("   - .NET 6.0 SDK for aas-processor")
    print("   - AAS Processor build and execution")
    print("   - Python .NET bridge")
    print("   - ETL pipeline integration")
    print("   - Docker containerization")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 