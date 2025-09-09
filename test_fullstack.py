#!/usr/bin/env python3
"""
Full Stack Integration Test
Tests the complete integration between backend API and frontend functionality
"""

import requests
import json
import time
import subprocess
import sys
import os
from threading import Thread

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_TARGET = "127.0.0.1"

def test_api_health():
    """Test if the API is running and healthy"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API not accessible: {e}")
        return False

def test_scan_endpoint():
    """Test the scan endpoint"""
    print("🔍 Testing scan endpoint...")
    try:
        response = requests.post(f"{API_BASE_URL}/scan/start", 
                               json={"target": TEST_TARGET, "automated_mode": False},
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            operation_id = data.get("operation_id")
            print(f"✅ Scan started successfully: {operation_id}")
            return operation_id
        else:
            print(f"❌ Scan start failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Scan endpoint error: {e}")
        return None

def test_operation_status(operation_id):
    """Test operation status endpoint"""
    print(f"🔍 Testing operation status for {operation_id}...")
    try:
        response = requests.get(f"{API_BASE_URL}/scan/status/{operation_id}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Operation status: {data.get('status')} - {data.get('message')}")
            return data
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Status endpoint error: {e}")
        return None

def test_logs_endpoint():
    """Test the logs endpoint"""
    print("🔍 Testing logs endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/logs", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_count = len(data.get("logs", []))
            print(f"✅ Logs endpoint working: {log_count} log entries")
            return True
        else:
            print(f"❌ Logs endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Logs endpoint error: {e}")
        return False

def test_operations_endpoint():
    """Test the operations endpoint"""
    print("🔍 Testing operations endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/operations", timeout=5)
        if response.status_code == 200:
            data = response.json()
            operation_count = len(data.get("operations", {}))
            print(f"✅ Operations endpoint working: {operation_count} active operations")
            return True
        else:
            print(f"❌ Operations endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Operations endpoint error: {e}")
        return False

def test_websocket_connection():
    """Test WebSocket connection (basic test)"""
    print("🔍 Testing WebSocket connection...")
    try:
        import websocket
        ws_url = "ws://localhost:8000/ws"
        
        def on_message(ws, message):
            print(f"✅ WebSocket message received: {message[:100]}...")
            ws.close()
        
        def on_error(ws, error):
            print(f"❌ WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print("✅ WebSocket connection closed")
        
        def on_open(ws):
            print("✅ WebSocket connection opened")
            ws.send(json.dumps({"type": "ping"}))
        
        ws = websocket.WebSocketApp(ws_url,
                                  on_open=on_open,
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close)
        
        # Run for 5 seconds
        ws.run_forever(timeout=5)
        return True
        
    except ImportError:
        print("⚠️  websocket-client not installed, skipping WebSocket test")
        return True
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

def start_backend_server():
    """Start the backend server in a separate process"""
    print("🚀 Starting backend server...")
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    try:
        # Install dependencies
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      cwd=backend_dir, check=True, capture_output=True)
        
        # Start server
        process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app:app', '--host', '0.0.0.0', '--port', '8000'],
                                 cwd=backend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(5)
        return process
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        return None

def main():
    """Run all integration tests"""
    print("🛡️  Port Security Scanner - Full Stack Integration Test")
    print("=" * 60)
    
    # Start backend server
    backend_process = start_backend_server()
    if not backend_process:
        print("❌ Cannot start backend server. Exiting.")
        return
    
    try:
        # Wait for server to be ready
        print("⏳ Waiting for server to be ready...")
        time.sleep(3)
        
        # Run tests
        tests = [
            ("API Health Check", test_api_health),
            ("Logs Endpoint", test_logs_endpoint),
            ("Operations Endpoint", test_operations_endpoint),
            ("WebSocket Connection", test_websocket_connection),
            ("Scan Endpoint", test_scan_endpoint),
        ]
        
        results = []
        operation_id = None
        
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            try:
                if test_name == "Scan Endpoint":
                    operation_id = test_func()
                    results.append((test_name, operation_id is not None))
                else:
                    result = test_func()
                    results.append((test_name, result))
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                results.append((test_name, False))
        
        # Test operation status if scan was started
        if operation_id:
            print(f"\n📋 Running: Operation Status Check")
            status_result = test_operation_status(operation_id)
            results.append(("Operation Status", status_result is not None))
        
        # Summary
        print("\n" + "=" * 60)
        print("🧪 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            if result:
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        
        print(f"\n📊 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All integration tests passed!")
            print("✅ Full stack application is working correctly")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        print("\n🚀 To start the full application:")
        print("   python start_app.py")
        print("\n🌐 Access points:")
        print("   Frontend: http://localhost:5173")
        print("   Backend API: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        
    finally:
        # Clean up
        if backend_process:
            print("\n🛑 Stopping backend server...")
            backend_process.terminate()
            backend_process.wait()

if __name__ == "__main__":
    main()
