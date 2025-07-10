#!/usr/bin/env python3
"""
Simple Frontend Runner for AASX Digital Twin Analytics Framework
Just runs the FastAPI webapp without complex orchestration
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Run the frontend webapp"""
    print("🚀 Starting AASX Digital Twin Analytics Framework")
    print("=" * 50)
    
    # Check if webapp directory exists
    webapp_dir = Path("webapp")
    if not webapp_dir.exists():
        print("❌ Webapp directory not found!")
        sys.exit(1)
    
    # Check if app.py exists
    app_path = webapp_dir / "app.py"
    if not app_path.exists():
        print("❌ app.py not found in webapp directory!")
        sys.exit(1)
    
    print(f"📁 Webapp directory: {webapp_dir.absolute()}")
    print(f"📄 App file: {app_path.absolute()}")
    
    print("✅ Starting FastAPI webapp...")
    print("🌐 Webapp will be available at: http://localhost:5000")
    print("📖 API docs will be available at: http://localhost:5000/docs")
    print("🔄 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Run the FastAPI app from the webapp directory
        uvicorn.run(
            "webapp.app:app",
            host="0.0.0.0",
            port=5000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 