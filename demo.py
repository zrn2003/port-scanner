#!/usr/bin/env python3
"""
Port Security Scanner Demo
Demonstrates the full-stack application capabilities
"""

import requests
import json
import time
import webbrowser
import subprocess
import sys
import os
from threading import Thread

API_BASE_URL = "http://localhost:8000"

def open_browser():
    """Open the frontend in browser after a delay"""
    time.sleep(8)  # Wait for frontend to start
    print("🌐 Opening frontend in browser...")
    webbrowser.open("http://localhost:5173")

def demo_scan():
    """Demonstrate a port scan"""
    print("🔍 Starting demo port scan...")
    
    try:
        # Start scan
        response = requests.post(f"{API_BASE_URL}/scan/start", 
                               json={"target": "127.0.0.1", "automated_mode": False})
        
        if response.status_code == 200:
            data = response.json()
            operation_id = data["operation_id"]
            print(f"✅ Scan started: {operation_id}")
            
            # Monitor progress
            while True:
                status_response = requests.get(f"{API_BASE_URL}/scan/status/{operation_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status")
                    progress = status_data.get("progress", 0)
                    message = status_data.get("message", "")
                    
                    print(f"📊 Progress: {progress}% - {message}")
                    
                    if status in ["completed", "failed"]:
                        if status == "completed":
                            print("✅ Scan completed successfully!")
                            scan_result = status_data.get("scan_result")
                            if scan_result:
                                print(f"   Found {scan_result.get('vulnerable_count', 0)} vulnerable ports")
                                print(f"   Total open ports: {scan_result.get('total_ports', 0)}")
                        else:
                            print("❌ Scan failed")
                        break
                    
                    time.sleep(2)
                else:
                    print("❌ Failed to get scan status")
                    break
        else:
            print("❌ Failed to start scan")
            
    except Exception as e:
        print(f"❌ Demo scan error: {e}")

def demo_logs():
    """Demonstrate log viewing"""
    print("📋 Fetching system logs...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/logs")
        if response.status_code == 200:
            data = response.json()
            logs = data.get("logs", [])
            print(f"✅ Retrieved {len(logs)} log entries")
            
            # Show last few logs
            for log in logs[-3:]:
                print(f"   [{log.get('timestamp', '')}] {log.get('level', '')}: {log.get('message', '')}")
        else:
            print("❌ Failed to fetch logs")
            
    except Exception as e:
        print(f"❌ Demo logs error: {e}")

def main():
    """Run the demo"""
    print("🛡️  Port Security Scanner - Full Stack Demo")
    print("=" * 50)
    print("This demo will:")
    print("1. Start the backend server")
    print("2. Start the frontend server")
    print("3. Open the web interface")
    print("4. Demonstrate port scanning")
    print("5. Show system logs")
    print("=" * 50)
    
    # Check if servers are already running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✅ Backend server is already running")
        else:
            print("❌ Backend server is not responding correctly")
            return
    except:
        print("❌ Backend server is not running")
        print("Please start the application first:")
        print("   python start_app.py")
        return
    
    # Open browser in background
    browser_thread = Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    print("\n🎬 Starting demo...")
    print("💡 The web interface will open automatically in your browser")
    print("💡 You can also manually navigate to: http://localhost:5173")
    
    # Wait a moment
    time.sleep(3)
    
    # Run demo functions
    print("\n" + "=" * 50)
    print("🔍 DEMO: Port Scanning")
    print("=" * 50)
    demo_scan()
    
    print("\n" + "=" * 50)
    print("📋 DEMO: System Logs")
    print("=" * 50)
    demo_logs()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("=" * 50)
    print("The web interface is now open in your browser.")
    print("You can:")
    print("• Start new port scans")
    print("• View vulnerabilities")
    print("• Execute security actions")
    print("• Monitor operations in real-time")
    print("• View system logs")
    print("\nPress Ctrl+C to stop the servers when done.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
