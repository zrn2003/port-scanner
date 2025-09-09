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
import ctypes
import requests
import json
from datetime import datetime

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
        # Check if npm is available
        try:
            subprocess.run(['npm', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ npm not available - skipping frontend startup")
            print("💡 Install Node.js from https://nodejs.org/ to enable frontend")
            return True
        
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
            print("⚠️ npm is not installed - frontend may not work properly")
            print("   Install Node.js from: https://nodejs.org/")
    except FileNotFoundError:
        print("⚠️ npm is not installed - frontend may not work properly")
        print("   Install Node.js from: https://nodejs.org/")
    
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

def check_admin_privileges():
    """Check if running with admin privileges"""
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False

def wait_for_backend():
    """Wait for backend server to be ready"""
    print("⏳ Waiting for backend server to be ready...")
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get('http://localhost:8000/health', timeout=2)
            if response.status_code == 200:
                print("✅ Backend server is ready!")
                return True
        except:
            pass
        
        attempt += 1
        time.sleep(1)
        if attempt % 5 == 0:
            print(f"⏳ Attempt {attempt}/{max_attempts}...")
    
    print("❌ Backend server failed to start within timeout")
    return False

def check_system_status():
    """Check system status via API"""
    try:
        response = requests.get('http://localhost:8000/system/status', timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def request_admin_elevation():
    """Request admin elevation via API"""
    try:
        response = requests.post('http://localhost:8000/system/elevate', timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def handle_admin_privileges():
    """Handle admin privilege elevation after servers start"""
    print("\n🔐 Checking admin privileges...")
    
    # Wait for backend to be ready
    if not wait_for_backend():
        print("❌ Cannot check admin privileges - backend not ready")
        return False
    
    # Check current admin status
    status = check_system_status()
    
    if status:
        admin_available = status.get('admin_privileges', False)
        firewall_enabled = status.get('firewall_enabled', False)
        
        print(f"📊 System Status:")
        print(f"   • Admin Privileges: {'✅ Available' if admin_available else '❌ Not Available'}")
        print(f"   • Firewall Status: {'✅ Enabled' if firewall_enabled else '❌ Disabled'}")
        print(f"   • Operating System: {status.get('operating_system', 'Unknown')}")
        
        if admin_available:
            print("\n🎉 Full admin privileges are available!")
            print("🔐 All security features are enabled!")
            return True
        else:
            print("\n⚠️ Admin privileges not available")
            print("🔐 Requesting automatic elevation...")
            
            # Request admin elevation
            elevation_result = request_admin_elevation()
            
            if elevation_result and elevation_result.get('success'):
                print("✅ Admin elevation requested!")
                print("📝 A UAC prompt should appear. Please click 'Yes' to grant admin access.")
                print("🔄 The application will automatically detect when admin privileges are available.")
            else:
                print("❌ Failed to request admin elevation")
                print("💡 Please run the application as administrator manually")
    else:
        print("❌ Cannot check system status - API not responding")
    
    return False

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
    
    # Check if already running with admin privileges
    if check_admin_privileges():
        print("✅ Already running with administrator privileges!")
        print("🔐 Full security functionality is available from the start!")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend in a separate thread
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    frontend_thread.start()
    
    # Wait a moment for frontend to start
    time.sleep(3)
    
    # Handle admin privileges in a separate thread
    admin_thread = threading.Thread(target=handle_admin_privileges, daemon=True)
    admin_thread.start()
    
    print("\n💡 The application will automatically handle admin privileges once servers are ready.")
    print("🔄 Check the console for admin privilege status updates.")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down application...")
        print("✅ Application stopped successfully")

if __name__ == "__main__":
    main()
