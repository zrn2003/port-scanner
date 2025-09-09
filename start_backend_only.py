#!/usr/bin/env python3
"""
Backend-only startup script for Port Security Scanner
Use this when npm/Node.js is not available
"""

import subprocess
import sys
import os
import time
import threading
import platform
import ctypes
import requests
import json
from datetime import datetime

def check_admin_privileges():
    """Check if running with admin privileges"""
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False

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
    """Handle admin privilege elevation after server starts"""
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
    """Main function to start backend only"""
    print("🛡️  Port Security Scanner - Backend Only")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if already running with admin privileges
    if check_admin_privileges():
        print("✅ Already running with administrator privileges!")
        print("🔐 Full security functionality is available from the start!")
    
    print("\n🚀 Starting backend server...")
    print("📝 Note: Frontend requires Node.js/npm - use start_app.py for full stack")
    
    try:
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        
        # Wait a moment for backend to start
        time.sleep(3)
        
        # Handle admin privileges in a separate thread
        admin_thread = threading.Thread(target=handle_admin_privileges, daemon=True)
        admin_thread.start()
        
        print("\n🎉 Backend server is starting up!")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("\n💡 The application will automatically handle admin privileges once server is ready.")
        print("🔄 Check the console for admin privilege status updates.")
        print("\n📝 To use the web interface, install Node.js and run: python start_app.py")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down application...")
            print("✅ Application stopped successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
