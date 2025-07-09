#!/usr/bin/env python3
"""
QI Digital Platform - Main Application
Local development server that orchestrates all services
"""

import asyncio
import uvicorn
import subprocess
import threading
import time
import os
import sys
import signal
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QIDigitalPlatform:
    """Main platform orchestrator for local development"""
    
    def __init__(self):
        self.services = {}
        self.processes = {}
        self.running = False
        
        # Service configurations - all services are now part of the main webapp
        self.service_configs = {
            'webapp': {
                'name': 'QI Digital Platform',
                'port': 5000,
                'command': [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '0.0.0.0', '--port', '5000', '--reload'],
                'cwd': 'webapp',
                'health_url': 'http://localhost:5000/health'
            }
        }
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        logger.info("Checking dependencies...")
        
        # Check core Python packages (skip problematic ones for now)
        core_packages = [
            ('fastapi', 'fastapi'),
            ('uvicorn', 'uvicorn'),
            ('requests', 'requests'),
            ('jinja2', 'jinja2'),
            ('aiofiles', 'aiofiles')
        ]
        
        missing_packages = []
        for package_name, import_name in core_packages:
            try:
                __import__(import_name)
                logger.debug(f"✓ {package_name} is available")
            except ImportError as e:
                logger.debug(f"✗ {package_name} import failed: {e}")
                missing_packages.append(package_name)
            except Exception as e:
                logger.warning(f"⚠ {package_name} import had issues: {e}")
                # Continue anyway for problematic packages
        
        # Check optional AI packages separately to avoid crashes
        ai_packages = [
            ('sentence-transformers', 'sentence_transformers'),
            ('torch', 'torch'),
            ('numpy', 'numpy'),
            ('openai', 'openai'),
            ('anthropic', 'anthropic')
        ]
        
        for package_name, import_name in ai_packages:
            try:
                __import__(import_name)
                logger.debug(f"✓ {package_name} is available")
            except Exception as e:
                logger.warning(f"⚠ {package_name} not available (optional): {e}")
                # Don't add to missing packages as these are optional for basic functionality
        
        if missing_packages:
            logger.warning(f"Some core packages may be missing: {missing_packages}")
            logger.info("Attempting to install missing packages...")
            return False
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], check=True, capture_output=True, text=True, shell=True)
            logger.debug(f"Node.js version: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Node.js is not installed or not in PATH")
            return False
        
        # Check npm
        try:
            result = subprocess.run(['npm', '--version'], check=True, capture_output=True, text=True, shell=True)
            logger.debug(f"npm version: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("npm is not installed or not in PATH")
            return False
        
        logger.info("Core dependencies are available")
        return True
    
    def install_dependencies(self):
        """Install required dependencies"""
        logger.info("Installing dependencies...")
        
        # Install Python dependencies from basic requirements.txt
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-basic.txt'], check=True)
            logger.info("Python dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Python dependencies: {e}")
            return False
        
        # All services are now Python/FastAPI - no Node.js dependencies needed
        logger.info("All services are Python/FastAPI - no Node.js dependencies required")
        
        logger.info("Dependencies installed successfully")
        return True
    
    def setup_environment(self):
        """Setup environment variables and configuration"""
        logger.info("Setting up environment...")
        
        # Create .env file if it doesn't exist
        env_file = Path('.env')
        if not env_file.exists():
            env_content = """# Database Configuration
DATABASE_URL=postgresql://aasx_user:aasx_password@localhost:5432/aasx_data
REDIS_URL=redis://localhost:6379

# AI Services (Optional)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Application Settings
JWT_SECRET=your_jwt_secret_key_here
NODE_ENV=development
"""
            env_file.write_text(env_content)
            logger.info("Created .env file")
        
        # Create necessary directories
        directories = ['digital-twins', 'certificates', 'logs', 'backup']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        
        logger.info("Environment setup completed")
    
    def start_service(self, service_key: str) -> bool:
        """Start a specific service"""
        config = self.service_configs[service_key]
        logger.info(f"Starting {config['name']}...")
        
        try:
            # Change to service directory
            cwd = Path(config['cwd'])
            if not cwd.exists():
                logger.error(f"Service directory not found: {cwd}")
                return False
            
            # Start the service
            command_str = ' '.join(config['command']) if isinstance(config['command'], list) else config['command']
            logger.info(f"Starting {config['name']} with command: {command_str}")
            
            process = subprocess.Popen(
                command_str,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            
            self.processes[service_key] = process
            logger.info(f"{config['name']} started (PID: {process.pid})")
            
            # Wait a bit for service to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                logger.info(f"{config['name']} is running successfully")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"{config['name']} failed to start")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to start {config['name']}: {e}")
            return False
    
    def stop_service(self, service_key: str):
        """Stop a specific service"""
        if service_key in self.processes:
            process = self.processes[service_key]
            config = self.service_configs[service_key]
            
            logger.info(f"Stopping {config['name']}...")
            
            try:
                process.terminate()
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            del self.processes[service_key]
            logger.info(f"{config['name']} stopped")
    
    def check_service_health(self, service_key: str) -> bool:
        """Check if a service is healthy"""
        config = self.service_configs[service_key]
        
        try:
            import requests
            response = requests.get(config['health_url'], timeout=5)
            if response.status_code == 200:
                # For Python services, check if they're responding even if external deps are missing
                if service_key in ['ai_rag', 'twin_registry']:
                    try:
                        data = response.json()
                        # Consider healthy if service responds, even if external deps are disconnected
                        return data.get('status') == 'healthy'
                    except:
                        return True  # If we can't parse JSON, but got 200, consider healthy
                return True
            return False
        except Exception as e:
            logger.debug(f"Health check failed for {service_key}: {e}")
            return False
    
    def start_all_services(self):
        """Start all services"""
        logger.info("Starting all services...")
        
        # Start services in order
        service_order = ['webapp']
        started_services = []
        
        for service_key in service_order:
            if self.start_service(service_key):
                started_services.append(service_key)
                logger.info(f"✓ {service_key} started successfully")
            else:
                logger.warning(f"✗ {service_key} failed to start - continuing with other services")
        
        if not started_services:
            logger.error("No services could be started")
            return False
        
        # Wait for services to be ready with retries
        logger.info("Waiting for services to be ready...")
        max_retries = 5
        retry_delay = 3
        
        for attempt in range(max_retries):
            time.sleep(retry_delay)
            healthy_services = 0
            
            for service_key in started_services:
                if self.check_service_health(service_key):
                    config = self.service_configs[service_key]
                    logger.info(f"✓ {config['name']} is healthy")
                    healthy_services += 1
                else:
                    config = self.service_configs[service_key]
                    logger.warning(f"✗ {config['name']} health check failed (attempt {attempt + 1}/{max_retries})")
            
            logger.info(f"Health check attempt {attempt + 1}: {healthy_services}/{len(started_services)} services healthy")
            
            if healthy_services == len(started_services):
                logger.info("All started services are healthy!")
                return True
            elif attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
        
        logger.warning("Some services may not be fully ready, but platform is starting...")
        return True  # Continue anyway for development
    
    def stop_all_services(self):
        """Stop all services"""
        logger.info("Stopping all services...")
        
        for service_key in list(self.processes.keys()):
            self.stop_service(service_key)
        
        logger.info("All services stopped")
    
    def show_status(self):
        """Show status of all services"""
        logger.info("Service Status:")
        
        for service_key, config in self.service_configs.items():
            status = "Running" if service_key in self.processes else "Stopped"
            health = "Healthy" if self.check_service_health(service_key) else "Unhealthy"
            
            print(f"  {config['name']}: {status} ({health})")
        
        print("\nService URLs:")
        print("  🏠 Homepage: http://localhost:5000")
        print("  AI/RAG System: http://localhost:5000/ai-rag")
        print("  Digital Twin Registry: http://localhost:5000/twin-registry")
        print("  Certificate Manager: http://localhost:5000/certificates")
        print("  QI Analytics Dashboard: http://localhost:5000/analytics")
        print("  API Documentation: http://localhost:5000/docs")
    
    def run(self):
        """Run the platform"""
        logger.info("Starting QI Digital Platform (Local Development)")
        
        # Check dependencies
        if not self.check_dependencies():
            logger.info("Installing dependencies...")
            if not self.install_dependencies():
                logger.error("Failed to install dependencies")
                return False
        
        # Setup environment
        self.setup_environment()
        
        # All services are now Python/FastAPI - no Node.js dependencies needed
        logger.info("All services are Python/FastAPI - no Node.js dependencies required")
        
        # Start services
        if not self.start_all_services():
            logger.error("Failed to start services")
            return False
        
        self.running = True
        
        # Show status
        self.show_status()
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal")
            self.stop_all_services()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Keep running
        try:
            logger.info("Platform is running. Press Ctrl+C to stop.")
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.stop_all_services()

def main():
    """Main entry point"""
    platform = QIDigitalPlatform()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'start':
            platform.run()
        elif command == 'status':
            platform.show_status()
        elif command == 'install':
            platform.install_dependencies()
        elif command == 'setup':
            platform.setup_environment()
        else:
            print("Unknown command. Use: start, status, install, or setup")
    else:
        # Default: start the platform
        platform.run()

if __name__ == "__main__":
    main() 