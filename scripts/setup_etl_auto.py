#!/usr/bin/env python3
"""
Smart ETL Environment Setup Script

This script automatically detects your operating system and provides
the optimal setup experience for your platform.

Supported platforms:
- Windows (Windows 10/11, Windows 7+)
- Linux (Ubuntu/Debian, CentOS/RHEL/Fedora)
- macOS (10.15+)

Usage:
    python setup_etl_auto.py
"""

import sys
import os
import subprocess
import platform
import urllib.request
import zipfile
import tarfile
from pathlib import Path
import shutil
import ctypes

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"🚀 {title}")
    print("=" * 70)

def print_step(step_num, title):
    """Print a formatted step"""
    print(f"\n📋 Step {step_num}: {title}")
    print("-" * 50)

def run_command(command, description, cwd=None, check=True, shell=True):
    """Run a command and handle errors"""
    print(f"  🔧 {description}...")
    print(f"  Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=cwd,
            shell=shell
        )
        
        if result.returncode == 0:
            print(f"  ✅ {description} completed successfully")
            return True
        else:
            print(f"  ❌ {description} failed:")
            print(f"  Error: {result.stderr}")
            if check:
                return False
            else:
                print(f"  ⚠️  Continuing despite error...")
                return True
            
    except Exception as e:
        print(f"  ❌ {description} failed with exception: {e}")
        if check:
            return False
        else:
            print(f"  ⚠️  Continuing despite error...")
            return True

def detect_platform():
    """Detect the current platform and return platform info"""
    system = platform.system()
    machine = platform.machine()
    
    print(f"🔍 Detecting platform...")
    print(f"  System: {system}")
    print(f"  Architecture: {machine}")
    
    if system == "Windows":
        version = platform.version()
        print(f"  Windows version: {version}")
        return "windows", {"system": system, "machine": machine, "version": version}
    elif system == "Linux":
        # Detect Linux distribution
        distro = None
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('ID='):
                        distro = line.split('=')[1].strip().strip('"')
                        break
        except:
            pass
        print(f"  Distribution: {distro or 'Unknown'}")
        return "linux", {"system": system, "machine": machine, "distro": distro}
    elif system == "Darwin":  # macOS
        version = platform.mac_ver()[0]
        print(f"  macOS version: {version}")
        return "macos", {"system": system, "machine": machine, "version": version}
    else:
        return "unknown", {"system": system, "machine": machine}

def check_python_version():
    """Check Python version compatibility"""
    print_step(1, "Checking Python Installation")
    
    version = sys.version_info
    print(f"  Python version: {version.major}.{version.minor}.{version.micro}")
    print(f"  Executable: {sys.executable}")
    
    if version.major == 3 and version.minor >= 8:
        print("  ✅ Python version is compatible")
        return True
    else:
        print("  ❌ Python 3.8+ is required")
        return False

def install_python_packages():
    """Install Python packages from requirements.txt"""
    print_step(2, "Installing Python Packages")
    
    # Get the project root
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / "requirements.txt"
    
    if not requirements_file.exists():
        print("  ❌ requirements.txt not found")
        return False
    
    # Upgrade pip first
    print("  📦 Upgrading pip...")
    run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip",
        check=False
    )
    
    # Install packages with platform-specific flags
    platform_name, _ = detect_platform()
    if platform_name == "windows":
        # Windows: use --user flag to avoid permission issues
        success = run_command(
            f"{sys.executable} -m pip install -r {requirements_file} --user",
            "Installing packages from requirements.txt"
        )
    else:
        # Linux/macOS: standard installation
        success = run_command(
            f"{sys.executable} -m pip install -r {requirements_file}",
            "Installing packages from requirements.txt"
        )
    
    if not success:
        print("  ⚠️  Some packages may have failed to install")
        print("  💡 Try installing with: pip install --user -r requirements.txt")
    
    return success

def install_system_dependencies(platform_name, platform_info):
    """Install system dependencies based on platform"""
    print_step(3, "Installing System Dependencies")
    
    if platform_name == "windows":
        print("  ⚠️  No system dependencies required for Windows")
        return True
        
    elif platform_name == "linux":
        distro = platform_info.get("distro")
        if distro in ['ubuntu', 'debian']:
            print("  📦 Installing Ubuntu/Debian dependencies...")
            commands = [
                "sudo apt-get update",
                "sudo apt-get install -y build-essential python3-dev python3-pip curl wget",
                "sudo apt-get install -y libssl-dev libffi-dev"
            ]
        elif distro in ['centos', 'rhel', 'fedora']:
            print("  📦 Installing CentOS/RHEL/Fedora dependencies...")
            commands = [
                "sudo yum update -y",
                "sudo yum groupinstall -y 'Development Tools'",
                "sudo yum install -y python3-devel python3-pip curl wget",
                "sudo yum install -y openssl-devel libffi-devel"
            ]
        else:
            print("  ⚠️  Unknown distribution, skipping system dependencies")
            return True
        
        for command in commands:
            success = run_command(command, f"Running: {command}", check=False)
            if not success:
                print("  ⚠️  Some system dependencies failed to install")
        
        return True
        
    elif platform_name == "macos":
        # Check if Homebrew is available
        brew_check = subprocess.run(["which", "brew"], capture_output=True, text=True)
        
        if brew_check.returncode == 0:
            print("  📦 Installing system dependencies via Homebrew...")
            dependencies = ["openssl", "curl", "wget", "cmake"]
            
            for dep in dependencies:
                success = run_command(f"brew install {dep}", f"Installing {dep}", check=False)
                if not success:
                    print(f"  ⚠️  Failed to install {dep}")
        else:
            print("  ⚠️  Homebrew not found, skipping system dependencies")
            print("  💡 Install Homebrew from: https://brew.sh")
        
        return True
    
    return True

def check_dotnet():
    """Check if .NET is installed"""
    print_step(4, "Checking .NET Installation")
    
    # Try different .NET commands
    dotnet_commands = [
        "dotnet --version",
        "dotnet --list-sdks",
        "which dotnet" if platform.system() != "Windows" else "where dotnet"
    ]
    
    for command in dotnet_commands:
        success = run_command(command, f"Checking: {command}", check=False)
        if success:
            print("  ✅ .NET is available")
            return True
    
    print("  ❌ .NET not found")
    return False

def install_dotnet(platform_name, platform_info):
    """Install .NET 6.0 SDK based on platform"""
    print_step(5, "Installing .NET 6.0 SDK")
    
    if platform_name == "windows":
        return install_dotnet_windows()
    elif platform_name == "linux":
        return install_dotnet_linux(platform_info.get("distro"))
    elif platform_name == "macos":
        return install_dotnet_macos()
    else:
        print("  ❌ Unsupported platform for .NET installation")
        return False

def install_dotnet_windows():
    """Install .NET 6.0 SDK on Windows"""
    print("  📦 Installing .NET 6.0 SDK on Windows...")
    
    # Download .NET installer
    installer_url = "https://download.microsoft.com/download/6/6/1/661e274b-1df6-4cd4-87c0-2d7e8c4b5c5d/dotnet-sdk-6.0.428-win-x64.exe"
    
    # Create downloads directory if it doesn't exist
    downloads_dir = Path.home() / "Downloads"
    downloads_dir.mkdir(exist_ok=True)
    
    installer_path = downloads_dir / "dotnet-sdk-6.0.428-win-x64.exe"
    
    try:
        print("  📥 Downloading .NET 6.0 SDK...")
        urllib.request.urlretrieve(installer_url, installer_path)
        
        print("  🔧 Running .NET installer...")
        result = subprocess.run(
            [str(installer_path), "/quiet", "/norestart"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("  ✅ .NET 6.0 SDK installed successfully")
            return True
        else:
            print("  ❌ .NET installation failed")
            print("  💡 Please install .NET 6.0 SDK manually from:")
            print("     https://dotnet.microsoft.com/download/dotnet/6.0")
            return False
            
    except Exception as e:
        print(f"  ❌ Failed to install .NET: {e}")
        print("  💡 Please install .NET 6.0 SDK manually from:")
        print("     https://dotnet.microsoft.com/download/dotnet/6.0")
        return False

def install_dotnet_linux(distro):
    """Install .NET 6.0 SDK on Linux"""
    if distro in ['ubuntu', 'debian']:
        print("  📦 Installing .NET 6.0 SDK on Ubuntu/Debian...")
        commands = [
            "wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb",
            "sudo dpkg -i packages-microsoft-prod.deb",
            "rm packages-microsoft-prod.deb",
            "sudo apt-get update",
            "sudo apt-get install -y apt-transport-https",
            "sudo apt-get update",
            "sudo apt-get install -y dotnet-sdk-6.0"
        ]
    elif distro in ['centos', 'rhel', 'fedora']:
        print("  📦 Installing .NET 6.0 SDK on CentOS/RHEL...")
        commands = [
            "sudo rpm -Uvh https://packages.microsoft.com/config/centos/7/packages-microsoft-prod.rpm",
            "sudo yum install -y dotnet-sdk-6.0"
        ]
    else:
        print("  ⚠️  Unknown distribution, manual installation required")
        print("  💡 Install .NET 6.0 SDK manually from:")
        print("     https://dotnet.microsoft.com/download/dotnet/6.0")
        return False
    
    for command in commands:
        success = run_command(command, f"Running: {command}", check=False)
        if not success:
            print("  ⚠️  Some commands failed, but continuing...")
    
    # Verify installation
    return check_dotnet()

def install_dotnet_macos():
    """Install .NET 6.0 SDK on macOS"""
    print("  📦 Installing .NET 6.0 SDK on macOS...")
    
    # Try Homebrew first
    brew_check = subprocess.run(["which", "brew"], capture_output=True, text=True)
    
    if brew_check.returncode == 0:
        print("  📦 Installing .NET 6.0 SDK via Homebrew...")
        success = run_command("brew install dotnet", "Installing .NET via Homebrew", check=False)
        if success:
            return check_dotnet()
    
    # Fallback to manual installation
    print("  📥 Installing .NET 6.0 SDK manually...")
    
    installer_url = "https://download.microsoft.com/download/6/6/1/661e274b-1df6-4cd4-87c0-2d7e8c4b5c5d/dotnet-sdk-6.0.428-osx-x64.tar.gz"
    
    downloads_dir = Path.home() / "Downloads"
    downloads_dir.mkdir(exist_ok=True)
    
    installer_path = downloads_dir / "dotnet-sdk-6.0.428-osx-x64.tar.gz"
    
    try:
        urllib.request.urlretrieve(installer_url, installer_path)
        
        with tarfile.open(installer_path, 'r:gz') as tar:
            tar.extractall('/usr/local/share/')
        
        run_command("sudo ln -sf /usr/local/share/dotnet/dotnet /usr/local/bin/dotnet", "Creating symlink", check=False)
        
        print("  ✅ .NET 6.0 SDK installed successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to install .NET: {e}")
        print("  💡 Please install .NET 6.0 SDK manually from:")
        print("     https://dotnet.microsoft.com/download/dotnet/6.0")
        return False

def build_dotnet_processor():
    """Build the .NET AAS processor"""
    print_step(6, "Building .NET AAS Processor")
    
    # Get the aas-processor directory
    project_root = Path(__file__).parent.parent
    aas_processor_dir = project_root / "aas-processor"
    
    if not aas_processor_dir.exists():
        print("  ❌ aas-processor directory not found")
        return False
    
    # Check if project file exists
    project_file = aas_processor_dir / "AasProcessor.csproj"
    if not project_file.exists():
        print("  ❌ AasProcessor.csproj not found")
        return False
    
    print("  📦 Restoring .NET packages...")
    restore_success = run_command(
        "dotnet restore",
        "Restoring .NET packages",
        cwd=aas_processor_dir
    )
    
    if not restore_success:
        print("  ❌ Package restore failed")
        return False
    
    print("  🔨 Building .NET project...")
    build_success = run_command(
        "dotnet build --configuration Release",
        "Building .NET project",
        cwd=aas_processor_dir
    )
    
    if not build_success:
        print("  ❌ Build failed")
        return False
    
    # Check if executable exists (platform-specific)
    platform_name, _ = detect_platform()
    if platform_name == "windows":
        exe_path = aas_processor_dir / "bin" / "Release" / "net6.0" / "AasProcessor.exe"
    else:
        exe_path = aas_processor_dir / "bin" / "Release" / "net6.0" / "AasProcessor"
        # Make executable on Unix systems
        run_command(f"chmod +x {exe_path}", "Making executable", check=False)
    
    if exe_path.exists():
        print(f"  ✅ AAS Processor built successfully: {exe_path}")
        return True
    else:
        print(f"  ❌ Executable not found at: {exe_path}")
        return False

def create_directories():
    """Create necessary project directories"""
    print_step(7, "Creating Project Directories")
    
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

def test_environment():
    """Test the complete environment"""
    print_step(8, "Testing Environment")
    
    # Test Python imports
    test_imports = [
        ('yaml', 'PyYAML'),
        ('neo4j', 'Neo4j driver'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('sklearn', 'Scikit-learn'),  # This will import scikit-learn
        ('torch', 'PyTorch'),
        ('transformers', 'Transformers'),
        ('qdrant_client', 'Qdrant client'),
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic')
    ]
    
    print("  📦 Python packages:")
    python_success = True
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"    ✅ {name}")
        except ImportError:
            print(f"    ❌ {name}")
            python_success = False
    
    # Test .NET processor
    print("  🔧 .NET processor:")
    project_root = Path(__file__).parent.parent
    platform_name, _ = detect_platform()
    
    if platform_name == "windows":
        exe_path = project_root / "aas-processor" / "bin" / "Release" / "net6.0" / "AasProcessor.exe"
    else:
        exe_path = project_root / "aas-processor" / "bin" / "Release" / "net6.0" / "AasProcessor"
    
    if exe_path.exists():
        print(f"    ✅ AAS Processor executable found")
        dotnet_success = True
    else:
        print(f"    ❌ AAS Processor executable not found")
        dotnet_success = False
    
    return python_success, dotnet_success

def main():
    """Main setup function"""
    print_header("Smart ETL Environment Setup")
    
    print("This script will automatically detect your platform and set up:")
    print("  📦 Python packages")
    print("  🔧 .NET 6.0 SDK (if needed)")
    print("  🏗️  AAS Core 3.0 and AASX Package libraries")
    print("  ⚙️  .NET AAS processor build")
    print("  🧪 Environment validation and testing")
    print()
    
    # Detect platform
    platform_name, platform_info = detect_platform()
    
    if platform_name == "unknown":
        print("❌ Unsupported platform detected")
        print("Supported platforms: Windows, Linux, macOS")
        return 1
    
    print(f"✅ Platform detected: {platform_name.title()}")
    print()
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install system dependencies
    install_system_dependencies(platform_name, platform_info)
    
    # Install Python packages
    install_python_packages()
    
    # Check .NET
    dotnet_available = check_dotnet()
    
    # Install .NET if needed
    if not dotnet_available:
        print("\n🔧 .NET 6.0 SDK is required for AAS libraries")
        install_success = install_dotnet(platform_name, platform_info)
        if not install_success:
            print("\n⚠️  .NET installation failed. You can:")
            print("  1. Install .NET 6.0 SDK manually from: https://dotnet.microsoft.com/download/dotnet/6.0")
            print("  2. Run this script again")
            print("  3. Continue without .NET (limited functionality)")
            
            choice = input("\nContinue without .NET? (y/N): ").lower()
            if choice != 'y':
                return 1
    
    # Build .NET processor
    dotnet_success = True
    if dotnet_available or check_dotnet():
        dotnet_success = build_dotnet_processor()
    else:
        print("  ⚠️  Skipping .NET processor build (not available)")
    
    # Create directories
    create_directories()
    
    # Test environment
    python_success, dotnet_success = test_environment()
    
    # Final summary
    print_header("Setup Complete!")
    
    print("📊 Results:")
    print(f"  Python packages: {'✅ Ready' if python_success else '❌ Issues detected'}")
    print(f"  .NET processor: {'✅ Built' if dotnet_success else '❌ Not available'}")
    print(f"  AAS Core 3.0: {'✅ Available' if dotnet_success else '❌ Not available'}")
    print(f"  AASX Package: {'✅ Available' if dotnet_success else '❌ Not available'}")
    print(f"  Directories: ✅ Created")
    
    if python_success and dotnet_success:
        print("\n🎉 Complete ETL environment setup successful!")
        print("All components are ready:")
        print("  ✅ Python packages installed")
        print("  ✅ .NET 6.0 SDK available")
        print("  ✅ AAS Core 3.0 library available")
        print("  ✅ AASX Package library available")
        print("  ✅ .NET AAS processor built")
        print("\nYou can now run:")
        print("  python run_etl.py --check")
        print("  python run_etl.py")
        return 0
    elif python_success:
        print("\n⚠️  Environment setup completed with limitations")
        print("Python packages are ready, but .NET components are not available")
        print("You can still run the ETL pipeline with basic processing")
        print("To enable advanced AAS processing, install .NET 6.0 SDK and run this script again")
        return 0
    else:
        print("\n❌ Environment setup failed")
        print("Please check the errors above and try again")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 