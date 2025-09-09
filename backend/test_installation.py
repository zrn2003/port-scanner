#!/usr/bin/env python3
"""
Installation Test Script for Port Security Scanner
Verifies that all required dependencies are available.
"""

import subprocess
import platform
import sys
import os

def test_python_version():
    """Test if Python version is adequate"""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 6:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.6+")
        return False

def test_nmap():
    """Test if Nmap is installed and accessible"""
    print("Testing Nmap installation...")
    try:
        result = subprocess.run(["nmap", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ {version_line} - OK")
            return True
        else:
            print("✗ Nmap command failed")
            return False
    except FileNotFoundError:
        print("✗ Nmap not found. Please install Nmap:")
        print("  Linux: sudo apt-get install nmap")
        print("  Windows: Download from https://nmap.org/download.html")
        print("  macOS: brew install nmap")
        return False
    except Exception as e:
        print(f"✗ Error testing Nmap: {str(e)}")
        return False

def test_privileges():
    """Test if running with appropriate privileges"""
    print("Testing privileges...")
    system = platform.system().lower()
    
    if system == "windows":
        try:
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                print("✓ Running as Administrator - OK")
                return True
            else:
                print("⚠ Not running as Administrator - Some updates may fail")
                return False
        except:
            print("⚠ Cannot determine admin status - Some updates may fail")
            return False
    else:
        if os.geteuid() == 0:
            print("✓ Running as root - OK")
            return True
        else:
            print("⚠ Not running as root - Some updates may require sudo")
            return False

def test_package_managers():
    """Test if package managers are available"""
    print("Testing package managers...")
    system = platform.system().lower()
    
    if system == "linux":
        try:
            result = subprocess.run(["apt-get", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ apt-get available - OK")
                return True
            else:
                print("✗ apt-get not working")
                return False
        except FileNotFoundError:
            print("✗ apt-get not found")
            return False
    elif system == "windows":
        try:
            result = subprocess.run(["powershell", "-Command", "Get-Host"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ PowerShell available - OK")
                return True
            else:
                print("✗ PowerShell not working")
                return False
        except FileNotFoundError:
            print("✗ PowerShell not found")
            return False
    else:
        print(f"⚠ Unsupported OS: {system}")
        return False

def test_network_connectivity():
    """Test basic network connectivity"""
    print("Testing network connectivity...")
    try:
        result = subprocess.run(["ping", "-c", "1", "8.8.8.8"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Network connectivity - OK")
            return True
        else:
            print("⚠ Network connectivity issues - Updates may fail")
            return False
    except subprocess.TimeoutExpired:
        print("⚠ Network timeout - Updates may fail")
        return False
    except FileNotFoundError:
        print("⚠ Cannot test network (ping not found)")
        return False
    except Exception as e:
        print(f"⚠ Network test error: {str(e)}")
        return False

def test_script_syntax():
    """Test if the main script has valid syntax"""
    print("Testing script syntax...")
    try:
        with open("port_security_scanner.py", "r") as f:
            code = f.read()
        compile(code, "port_security_scanner.py", "exec")
        print("✓ Script syntax - OK")
        return True
    except FileNotFoundError:
        print("✗ port_security_scanner.py not found")
        return False
    except SyntaxError as e:
        print(f"✗ Syntax error in script: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Error testing script: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Port Security Scanner - Installation Test")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_nmap,
        test_privileges,
        test_package_managers,
        test_network_connectivity,
        test_script_syntax
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {str(e)}")
            results.append(False)
        print()
    
    # Summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        print("✓ System is ready to run the Port Security Scanner")
    else:
        print(f"⚠ {passed}/{total} tests passed")
        print("⚠ Some issues detected. Please resolve them before running the scanner.")
    
    print("\nTo run the Port Security Scanner:")
    print("  python port_security_scanner.py")
    
    if platform.system().lower() == "linux" and os.geteuid() != 0:
        print("  (Consider running with: sudo python port_security_scanner.py)")

if __name__ == "__main__":
    main()
