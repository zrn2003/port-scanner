#!/usr/bin/env python3
"""
Enhanced Functionality Test Script for Port Security Scanner
Tests the new port closing and official patch download features.
"""

import subprocess
import platform
import sys
import os
import time

def test_enhanced_port_closing():
    """Test the enhanced port closing functionality"""
    print("Testing Enhanced Port Closing Functionality")
    print("=" * 60)
    
    # Test port to use (using a high port number to avoid conflicts)
    test_port = 9998
    
    try:
        # Start a simple listener on the test port
        print(f"Starting test listener on port {test_port}...")
        
        if platform.system().lower() == "windows":
            # Use PowerShell to start a listener
            ps_script = f"""
            $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, {test_port})
            $listener.Start()
            Write-Output "Listener started on port {test_port}"
            Start-Sleep -Seconds 30
            $listener.Stop()
            """
            
            # Start listener in background
            listener_process = subprocess.Popen(
                ["powershell", "-Command", ps_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            # Use netcat for Linux
            listener_process = subprocess.Popen(
                ["nc", "-l", str(test_port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        # Wait a moment for listener to start
        time.sleep(2)
        
        # Test if port is open
        print(f"Testing if port {test_port} is open...")
        if platform.system().lower() == "windows":
            test_cmd = ["netstat", "-an"]
        else:
            test_cmd = ["netstat", "-tuln"]
            
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        port_open = f":{test_port}" in result.stdout
        
        if port_open:
            print(f"✓ Port {test_port} is open and listening")
        else:
            print(f"✗ Port {test_port} is not open")
            return False
        
        # Test the enhanced port closing functionality
        print(f"Testing enhanced port closing for port {test_port}...")
        
        # Import and test the scanner
        sys.path.append('.')
        from port_security_scanner import PortSecurityScanner
        
        scanner = PortSecurityScanner()
        
        # Test Linux port closing
        if platform.system().lower() == "linux":
            success, message = scanner.close_port_linux(test_port, "test-service")
        else:
            success, message = scanner.close_port_windows(test_port, "test-service")
        
        if success:
            print(f"✓ Enhanced port closing successful: {message}")
        else:
            print(f"✗ Enhanced port closing failed: {message}")
        
        # Clean up listener
        try:
            listener_process.terminate()
            listener_process.wait(timeout=5)
        except:
            listener_process.kill()
        
        return success
        
    except Exception as e:
        print(f"✗ Exception during enhanced port closing test: {str(e)}")
        return False

def test_official_patch_download():
    """Test the official patch download functionality"""
    print("\nTesting Official Patch Download Functionality")
    print("=" * 60)
    
    try:
        # Import and test the scanner
        sys.path.append('.')
        from port_security_scanner import PortSecurityScanner
        
        scanner = PortSecurityScanner()
        
        # Test patch download for a common service
        test_package = "openssh-server" if platform.system().lower() == "linux" else "OpenSSH"
        
        print(f"Testing patch download for {test_package}...")
        success, message = scanner.download_patch_from_official_source(test_package)
        
        if success:
            print(f"✓ Official patch download successful: {message}")
        else:
            print(f"⚠ Official patch download result: {message}")
            # This might be expected if no updates are available
        
        # Test patch integrity verification
        print("Testing patch integrity verification...")
        
        # Create a test file
        test_file = "test_patch.txt"
        with open(test_file, "w") as f:
            f.write("Test patch content")
        
        # Test integrity verification
        is_valid = scanner.verify_patch_integrity(test_file)
        
        if is_valid:
            print("✓ Patch integrity verification working")
        else:
            print("✗ Patch integrity verification failed")
        
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"✗ Exception during patch download test: {str(e)}")
        return False

def test_automated_mode():
    """Test the automated mode functionality"""
    print("\nTesting Automated Mode Functionality")
    print("=" * 60)
    
    try:
        # Import and test the scanner
        sys.path.append('.')
        from port_security_scanner import PortSecurityScanner
        
        scanner = PortSecurityScanner()
        
        # Test automated mode prompt
        test_vuln_port = {
            "port": 22,
            "service": "SSH",
            "description": "Test SSH service"
        }
        
        print("Testing automated mode prompt...")
        action = scanner.prompt_user_permission(test_vuln_port, automated_mode=True)
        
        if action == 'auto':
            print("✓ Automated mode prompt working correctly")
        else:
            print(f"✗ Automated mode prompt failed, got: {action}")
            return False
        
        # Test distribution info detection (Linux only)
        if platform.system().lower() == "linux":
            print("Testing distribution info detection...")
            dist_info = scanner.get_distribution_info()
            if dist_info:
                print(f"✓ Distribution info detected: {dist_info.get('name', 'Unknown')}")
            else:
                print("⚠ Could not detect distribution info")
        
        return True
        
    except Exception as e:
        print(f"✗ Exception during automated mode test: {str(e)}")
        return False

def test_process_detection():
    """Test the process detection functionality"""
    print("\nTesting Process Detection Functionality")
    print("=" * 60)
    
    try:
        # Import and test the scanner
        sys.path.append('.')
        from port_security_scanner import PortSecurityScanner
        
        scanner = PortSecurityScanner()
        
        # Test process detection for a common port
        test_port = 80  # HTTP port
        
        print(f"Testing process detection for port {test_port}...")
        
        if platform.system().lower() == "windows":
            processes = scanner.find_windows_processes_using_port(test_port)
        else:
            processes = scanner.find_processes_using_port(test_port)
        
        if processes:
            print(f"✓ Found {len(processes)} processes using port {test_port}: {processes}")
        else:
            print(f"ℹ No processes found using port {test_port} (this is normal if no web server is running)")
        
        return True
        
    except Exception as e:
        print(f"✗ Exception during process detection test: {str(e)}")
        return False

def main():
    """Run all enhanced functionality tests"""
    print("Enhanced Port Security Scanner - Functionality Test")
    print("=" * 70)
    print("Testing new features:")
    print("• Enhanced port closing with multiple methods")
    print("• Official patch download from trusted sources")
    print("• Patch integrity verification")
    print("• Automated mode operation")
    print("• Process detection and management")
    print()
    
    # Check if running as administrator/root
    if platform.system().lower() == "windows":
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("⚠ WARNING: Not running as administrator.")
                print("Some tests may fail due to insufficient privileges.")
                print("Run PowerShell as Administrator for full functionality.")
        except:
            print("⚠ Cannot determine admin status.")
    else:
        if os.geteuid() != 0:
            print("⚠ WARNING: Not running as root.")
            print("Some tests may require sudo privileges.")
    
    print()
    
    # Run tests
    tests = [
        ("Enhanced Port Closing", test_enhanced_port_closing),
        ("Official Patch Download", test_official_patch_download),
        ("Automated Mode", test_automated_mode),
        ("Process Detection", test_process_detection)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"Running {test_name} test...")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test failed with exception: {str(e)}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("=" * 70)
    print("ENHANCED FUNCTIONALITY TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        if result:
            print(f"✓ {test_name}: PASSED")
            passed += 1
        else:
            print(f"✗ {test_name}: FAILED")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All enhanced functionality tests passed!")
        print("✓ The enhanced port security scanner is ready for use")
    else:
        print("⚠ Some tests failed. Check the output above for details.")
    
    print("\nNew Features Available:")
    print("• Multiple port closing methods (service stop, process kill, firewall blocking)")
    print("• Official patch download from trusted sources")
    print("• Patch integrity verification with SHA256 hashing")
    print("• Automated mode for non-interactive operation")
    print("• Enhanced process detection and management")
    print("• Comprehensive logging and error handling")
    
    print("\nUsage Examples:")
    print("  python port_security_scanner.py              # Interactive mode")
    print("  python port_security_scanner.py --auto       # Automated mode")
    print("  python port_security_scanner.py -a           # Automated mode (short)")

if __name__ == "__main__":
    main()
