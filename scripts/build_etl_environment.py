#!/usr/bin/env python3
"""
ETL Environment Builder Script

This script builds the complete ETL environment including:
- Python packages
- .NET AAS processor
- Environment validation

Usage:
    python build_etl_environment.py
"""

import sys
import os
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_step(step_num, title):
    """Print a formatted step"""
    print(f"\n📋 Step {step_num}: {title}")
    print("-" * 40)

def run_command(command, description, cwd=None):
    """Run a command and handle errors"""
    print(f"  🔧 {description}...")
    print(f"  Command: {command}")
    
    try:
        result = subprocess.run(
            command.split() if isinstance(command, str) else command,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        
        if result.returncode == 0:
            print(f"  ✅ {description} completed successfully")
            return True
        else:
            print(f"  ❌ {description} failed:")
            print(f"  Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ {description} failed with exception: {e}")
        return False

def check_python_version():
    """Check Python version"""
    print_step(1, "Checking Python Version")
    
    version = sys.version_info
    print(f"  Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("  ✅ Python version is compatible")
        return True
    else:
        print("  ❌ Python 3.8+ is required")
        return False

def install_python_packages():
    """Install Python packages"""
    print_step(2, "Installing Python Packages")
    
    # Get the project root
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / "requirements.txt"
    
    if not requirements_file.exists():
        print("  ❌ requirements.txt not found")
        return False
    
    # Install from requirements.txt
    success = run_command(
        f"pip install -r {requirements_file}",
        "Installing packages from requirements.txt"
    )
    
    if not success:
        print("  ⚠️  Some packages may have failed to install")
        print("  You can try installing them manually:")
        print("  pip install -r requirements.txt")
    
    return success

def check_dotnet():
    """Check .NET installation"""
    print_step(3, "Checking .NET Installation")
    
    success = run_command(
        "dotnet --version",
        "Checking .NET version"
    )
    
    if success:
        print("  ✅ .NET is available")
        return True
    else:
        print("  ❌ .NET not found")
        print("  Please install .NET 6.0 SDK from: https://dotnet.microsoft.com/download/dotnet/6.0")
        return False

def build_dotnet_processor():
    """Build the .NET AAS processor"""
    print_step(4, "Building .NET AAS Processor")
    
    # Get the aas-processor directory
    project_root = Path(__file__).parent.parent
    aas_processor_dir = project_root / "aas-processor"
    
    if not aas_processor_dir.exists():
        print("  ❌ aas-processor directory not found")
        return False
    
    # Restore packages
    restore_success = run_command(
        "dotnet restore",
        "Restoring .NET packages",
        cwd=aas_processor_dir
    )
    
    if not restore_success:
        return False
    
    # Build the project
    build_success = run_command(
        "dotnet build --configuration Release",
        "Building .NET project",
        cwd=aas_processor_dir
    )
    
    if not build_success:
        return False
    
    # Check if executable exists
    exe_path = aas_processor_dir / "bin" / "Release" / "net6.0" / "AasProcessor"
    if exe_path.exists():
        print(f"  ✅ AAS Processor built successfully: {exe_path}")
        return True
    else:
        print(f"  ❌ Executable not found at: {exe_path}")
        return False

def validate_environment():
    """Validate the built environment"""
    print_step(5, "Validating Environment")
    
    # Test imports
    test_imports = [
        ('yaml', 'PyYAML'),
        ('neo4j', 'Neo4j driver'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('sklearn', 'Scikit-learn'),
        ('torch', 'PyTorch'),
        ('transformers', 'Transformers'),
        ('qdrant_client', 'Qdrant client'),
        ('chromadb', 'ChromaDB'),
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic')
    ]
    
    # Special packages that require .NET build
    special_imports = [
        ('aas_core3', 'AAS Core 3.0'),
        ('aasx_package', 'AASX Package')
    ]
    
    all_imports_success = True
    
    print("  📦 Regular packages:")
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"    ✅ {name}")
        except ImportError:
            print(f"    ❌ {name}")
            all_imports_success = False
    
    print("  📦 Special packages (require .NET build):")
    special_available = True
    for module, name in special_imports:
        try:
            __import__(module)
            print(f"    ✅ {name}")
        except ImportError:
            print(f"    ⚠️  {name} (not available - requires .NET processor)")
            special_available = False
    
    return all_imports_success and special_available

def create_directories():
    """Create necessary directories"""
    print_step(6, "Creating Directories")
    
    project_root = Path(__file__).parent.parent
    directories = [
        "data/aasx-examples",
        "output/etl_results",
        "logs",
        "temp"
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {directory}")

def main():
    """Main build function"""
    print_header("ETL Environment Builder")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install Python packages
    install_python_packages()
    
    # Check .NET
    dotnet_available = check_dotnet()
    
    # Build .NET processor if available
    dotnet_success = True
    if dotnet_available:
        dotnet_success = build_dotnet_processor()
    else:
        print("  ⚠️  Skipping .NET processor build (not available)")
    
    # Validate environment
    validation_success = validate_environment()
    
    # Create directories
    create_directories()
    
    # Final summary
    print_header("Build Summary")
    
    print("📊 Results:")
    print(f"  Python packages: {'✅ Installed' if validation_success else '❌ Issues detected'}")
    print(f"  .NET processor: {'✅ Built' if dotnet_success else '❌ Not available'}")
    print(f"  Directories: ✅ Created")
    
    if validation_success and dotnet_success:
        print("\n🎉 Environment built successfully!")
        print("All packages and .NET processor are ready.")
        print("You can now run:")
        print("  python run_etl.py --check")
        print("  python run_etl.py")
        return 0
    elif validation_success:
        print("\n⚠️  Environment built with limitations")
        print("Python packages are ready, but .NET processor is not available")
        print("AAS Core 3.0 and AASX Package libraries will not be available")
        print("You can still run the ETL pipeline with basic processing")
        print("To enable advanced AAS processing, install .NET 6.0 SDK and rebuild")
        return 0
    else:
        print("\n❌ Environment build failed")
        print("Please check the errors above and try again")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 