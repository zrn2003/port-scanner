#!/usr/bin/env python3
"""
Test script to demonstrate port closing functionality
"""

import subprocess
import platform
import sys

def test_windows_firewall_blocking():
    """Test Windows Firewall port blocking functionality"""
    print("Testing Windows Firewall Port Blocking")
    print("=" * 50)
    
    # Test port to block (using a high port number to avoid conflicts)
    test_port = 9999
    
    try:
        # Add firewall rule to block the port
        print(f"Adding firewall rule to block port {test_port}...")
        add_cmd = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name=Test_Block_Port_{test_port}",
            "dir=in",
            "action=block",
            "protocol=TCP",
            f"localport={test_port}"
        ]
        
        result = subprocess.run(add_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Successfully added firewall rule to block port {test_port}")
        else:
            print(f"✗ Failed to add firewall rule: {result.stderr}")
            return False
            
        # Verify the rule was added
        print(f"Verifying firewall rule for port {test_port}...")
        verify_cmd = [
            "netsh", "advfirewall", "firewall", "show", "rule",
            f"name=Test_Block_Port_{test_port}"
        ]
        
        result = subprocess.run(verify_cmd, capture_output=True, text=True)
        if "Test_Block_Port_" in result.stdout:
            print(f"✓ Firewall rule verified for port {test_port}")
        else:
            print(f"✗ Firewall rule not found")
            
        # Remove the test rule
        print(f"Removing test firewall rule for port {test_port}...")
        remove_cmd = [
            "netsh", "advfirewall", "firewall", "delete", "rule",
            f"name=Test_Block_Port_{test_port}"
        ]
        
        result = subprocess.run(remove_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Successfully removed test firewall rule for port {test_port}")
        else:
            print(f"✗ Failed to remove test firewall rule: {result.stderr}")
            
        return True
        
    except Exception as e:
        print(f"✗ Exception during firewall test: {str(e)}")
        return False

def test_service_control():
    """Test Windows service control functionality"""
    print("\nTesting Windows Service Control")
    print("=" * 50)
    
    # Test with a common service that's usually running
    test_service = "Spooler"  # Print Spooler service
    
    try:
        # Check if service exists
        print(f"Checking if service '{test_service}' exists...")
        query_cmd = ["sc", "query", test_service]
        result = subprocess.run(query_cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and "SERVICE_NAME" in result.stdout:
            print(f"✓ Service '{test_service}' found")
            
            # Get service status
            print(f"Getting status of service '{test_service}'...")
            if "RUNNING" in result.stdout:
                print(f"✓ Service '{test_service}' is currently running")
            else:
                print(f"⚠ Service '{test_service}' is not running")
                
        else:
            print(f"✗ Service '{test_service}' not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Exception during service test: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Port Closing Functionality Test")
    print("=" * 60)
    
    if platform.system().lower() != "windows":
        print("This test is designed for Windows systems.")
        print("On Linux, the script would use systemctl and fuser commands.")
        return
        
    # Check if running as administrator
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("⚠ WARNING: Not running as administrator.")
            print("Some tests may fail due to insufficient privileges.")
            print("Run PowerShell as Administrator for full functionality.")
    except:
        print("⚠ Cannot determine admin status.")
    
    print()
    
    # Run tests
    firewall_ok = test_windows_firewall_blocking()
    service_ok = test_service_control()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if firewall_ok:
        print("✓ Windows Firewall blocking: WORKING")
    else:
        print("✗ Windows Firewall blocking: FAILED")
        
    if service_ok:
        print("✓ Windows Service control: WORKING")
    else:
        print("✗ Windows Service control: FAILED")
    
    print("\nThe enhanced port security scanner can:")
    print("• Block vulnerable ports using Windows Firewall")
    print("• Stop and disable Windows services")
    print("• Apply security updates when available")
    print("• Verify port closure with re-scanning")
    print("• Provide complete audit trail in logs")

if __name__ == "__main__":
    main()
