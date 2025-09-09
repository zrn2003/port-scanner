#!/usr/bin/env python3
"""
Startup script for the Port Security Scanner full-stack application
Starts both the backend API server and frontend development server
"""

import subprocess
import sys
import os
import time
import threading
import signal
import platform

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    try:
        # Install dependencies if needed
        print("📦 Installing backend dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      cwd=backend_dir, check=True)
        
        # Start the FastAPI server
        print("🔧 Starting FastAPI server on http://localhost:8000")
        subprocess.run([sys.executable, '-m', 'uvicorn', 'app:app', '--host', '0.0.0.0', '--port', '8000', '--reload'], 
                      cwd=backend_dir)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start backend: {e}")
        return False
    except KeyboardInterrupt:
        print("🛑 Backend server stopped")
        return True

def start_frontend():
    """Start the React frontend development server"""
    print("🎨 Starting frontend server...")
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    
    try:
        # Install dependencies if needed
        print("📦 Installing frontend dependencies...")
        if platform.system() == "Windows":
            subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True, shell=True)
            subprocess.run(['npm', 'run', 'dev'], cwd=frontend_dir, shell=True)
        else:
            subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
            subprocess.run(['npm', 'run', 'dev'], cwd=frontend_dir)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")
        return False
    except KeyboardInterrupt:
        print("🛑 Frontend server stopped")
        return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python
    try:
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
            print("❌ Python 3.7+ is required")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
        else:
            print("❌ Node.js is not installed")
            return False
    except FileNotFoundError:
        print("❌ Node.js is not installed")
        return False
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()}")
        else:
            print("❌ npm is not installed")
            return False
    except FileNotFoundError:
        print("❌ npm is not installed")
        return False
    
    # Check Nmap
    try:
        result = subprocess.run(['nmap', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ {version_line}")
        else:
            print("❌ Nmap is not installed")
            print("   Install from: https://nmap.org/download.html")
            return False
    except FileNotFoundError:
        print("❌ Nmap is not installed")
        print("   Install from: https://nmap.org/download.html")
        return False
    
    return True

def main():
    """Main function to start the application"""
    print("🛡️  Port Security Scanner - Full Stack Application")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing dependencies.")
        sys.exit(1)
    
    print("\n✅ All dependencies are available!")
    print("\n🚀 Starting application servers...")
    print("   Backend API: http://localhost:8000")
    print("   Frontend UI: http://localhost:5173")
    print("   API Docs: http://localhost:8000/docs")
    print("\n💡 Press Ctrl+C to stop all servers")
    print("=" * 60)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend in the main thread
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down application...")
        print("✅ Application stopped successfully")

if __name__ == "__main__":
    main()
