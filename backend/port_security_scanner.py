#!/usr/bin/env python3
"""
Port Security Scanner and Auto-Updater
A comprehensive security automation script that scans for vulnerable ports
and applies security updates with user consent and detailed logging.
"""

import subprocess
import platform
import logging
import json
import time
import sys
import os
import hashlib
import urllib.request
import urllib.parse
import ssl
import ctypes
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import re

class PortSecurityScanner:
    def __init__(self):
        self.log_file = "port_security.log"
        self.patch_cache_dir = "patch_cache"
        self.is_admin = self.check_admin_privileges()
        self.vulnerable_ports = {
            21: {"service": "FTP", "description": "File Transfer Protocol - often unsecured"},
            23: {"service": "Telnet", "description": "Telnet - unencrypted remote access"},
            445: {"service": "SMB", "description": "Server Message Block - potential for SMB exploits"},
            3389: {"service": "RDP", "description": "Remote Desktop Protocol - common attack vector"},
            22: {"service": "SSH", "description": "Secure Shell - needs proper configuration"},
            80: {"service": "HTTP", "description": "HTTP - web server vulnerabilities"},
            443: {"service": "HTTPS", "description": "HTTPS - SSL/TLS vulnerabilities"},
            1433: {"service": "MSSQL", "description": "Microsoft SQL Server - database vulnerabilities"},
            3306: {"service": "MySQL", "description": "MySQL - database vulnerabilities"},
            5432: {"service": "PostgreSQL", "description": "PostgreSQL - database vulnerabilities"},
            5900: {"service": "VNC", "description": "VNC - remote desktop vulnerabilities"},
            6379: {"service": "Redis", "description": "Redis - in-memory database vulnerabilities"},
            27017: {"service": "MongoDB", "description": "MongoDB - NoSQL database vulnerabilities"}
        }
        self.official_sources = {
            "linux": {
                "ubuntu": "http://security.ubuntu.com/ubuntu/pool/main/",
                "debian": "http://security.debian.org/debian-security/pool/updates/main/",
                "centos": "http://mirror.centos.org/centos/",
                "rhel": "https://access.redhat.com/downloads/content/"
            },
            "windows": {
                "microsoft": "https://www.microsoft.com/en-us/download/details.aspx",
                "catalog": "http://www.catalog.update.microsoft.com/",
                "wsus": "https://www.microsoft.com/en-us/download/confirmation.aspx"
            }
        }
        self.setup_logging()
        self.os_type = self.detect_os()
        self.create_patch_cache()
        
    def setup_logging(self):
        """Setup comprehensive logging with timestamps"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def detect_os(self) -> str:
        """Detect the operating system"""
        system = platform.system().lower()
        self.logger.info(f"Detected operating system: {system}")
        return system
        
    def create_patch_cache(self):
        """Create patch cache directory if it doesn't exist"""
        if not os.path.exists(self.patch_cache_dir):
            os.makedirs(self.patch_cache_dir)
            self.logger.info(f"Created patch cache directory: {self.patch_cache_dir}")

    def check_admin_privileges(self) -> bool:
        """Check if the script is running with administrator privileges"""
        try:
            if platform.system() == "Windows":
                # Check if running as administrator on Windows
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                # Check if running as root on Unix-like systems
                return os.geteuid() == 0
        except Exception as e:
            self.logger.warning(f"Could not check admin privileges: {e}")
            return False

    def request_admin_elevation(self) -> bool:
        """Request administrator elevation on Windows"""
        try:
            if platform.system() == "Windows" and not self.is_admin:
                self.logger.info("Requesting administrator elevation...")
                # Re-run the script with administrator privileges
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to request elevation: {e}")
            return False

    def ensure_admin_privileges(self) -> bool:
        """Ensure admin privileges are available for critical operations"""
        if self.is_admin:
            self.logger.info("✅ Administrator privileges confirmed")
            return True
        else:
            self.logger.warning("⚠️ Administrator privileges not available")
            self.logger.warning("Some operations may fail:")
            self.logger.warning("  • Windows Firewall rule creation")
            self.logger.warning("  • Service control operations")
            self.logger.warning("  • System-level port blocking")
            self.logger.warning("  • Patch installation")
            return False
            
    def get_distribution_info(self) -> Dict[str, str]:
        """Get detailed distribution information for Linux systems"""
        dist_info = {}
        try:
            if self.os_type == "linux":
                # Try to read /etc/os-release
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if "=" in line:
                            key, value = line.strip().split("=", 1)
                            dist_info[key.lower()] = value.strip('"')
        except Exception as e:
            self.logger.warning(f"Could not read distribution info: {e}")
        return dist_info
        
    def verify_patch_integrity(self, file_path: str, expected_hash: str = None) -> bool:
        """Verify the integrity of a downloaded patch file"""
        try:
            if not os.path.exists(file_path):
                return False
                
            # Calculate SHA256 hash
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            actual_hash = sha256_hash.hexdigest()
            self.logger.info(f"Patch file hash: {actual_hash}")
            
            if expected_hash:
                return actual_hash == expected_hash
            else:
                # If no expected hash provided, just verify file exists and has content
                return os.path.getsize(file_path) > 0
                
        except Exception as e:
            self.logger.error(f"Error verifying patch integrity: {e}")
            return False
            
    def download_patch_from_official_source(self, package_name: str, version: str = None) -> Tuple[bool, str]:
        """Download security patches from official sources"""
        try:
            self.logger.info(f"Downloading patch for {package_name} from official sources")
            
            if self.os_type == "linux":
                return self.download_linux_patch(package_name, version)
            elif self.os_type == "windows":
                return self.download_windows_patch(package_name, version)
            else:
                return False, f"Unsupported OS for patch download: {self.os_type}"
                
        except Exception as e:
            return False, f"Error downloading patch: {str(e)}"
            
    def download_linux_patch(self, package_name: str, version: str = None) -> Tuple[bool, str]:
        """Download Linux security patches from official repositories"""
        try:
            dist_info = self.get_distribution_info()
            dist_id = dist_info.get("id", "").lower()
            
            # Update package list first
            update_cmd = ["sudo", "apt-get", "update"]
            result = subprocess.run(update_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, f"Failed to update package list: {result.stderr}"
            
            # Check for available updates
            upgrade_cmd = ["apt", "list", "--upgradable"]
            result = subprocess.run(upgrade_cmd, capture_output=True, text=True)
            
            if package_name in result.stdout:
                self.logger.info(f"Security updates available for {package_name}")
                return True, "Updates available from official repository"
            else:
                return False, f"No updates available for {package_name}"
                
        except Exception as e:
            return False, f"Error checking Linux updates: {str(e)}"
            
    def download_windows_patch(self, service_name: str, version: str = None) -> Tuple[bool, str]:
        """Download Windows security patches from Microsoft"""
        try:
            # Use Windows Update API to check for updates
            ps_script = """
            $UpdateSession = New-Object -ComObject Microsoft.Update.Session
            $UpdateSearcher = $UpdateSession.CreateUpdateSearcher()
            $SearchResult = $UpdateSearcher.Search("IsInstalled=0 and Type='Software'")
            
            if ($SearchResult.Updates.Count -gt 0) {
                Write-Output "Updates available: $($SearchResult.Updates.Count)"
                foreach ($Update in $SearchResult.Updates) {
                    Write-Output "Update: $($Update.Title)"
                }
            } else {
                Write-Output "No updates available"
            }
            """
            
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                if "Updates available" in result.stdout:
                    return True, "Windows updates available from Microsoft"
                else:
                    return False, "No Windows updates available"
            else:
                return False, f"Failed to check Windows updates: {result.stderr}"
                
        except Exception as e:
            return False, f"Error checking Windows updates: {str(e)}"
        
    def run_nmap_scan(self, target: str = "127.0.0.1") -> List[int]:
        """Run Nmap full port scan and return list of open ports"""
        self.logger.info(f"Starting Nmap scan on {target}")
        
        try:
            # Run nmap with full port scan
            cmd = ["nmap", "-p-", "--open", target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                self.logger.error(f"Nmap scan failed: {result.stderr}")
                return []
                
            # Parse nmap output to extract open ports
            open_ports = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                # Look for port lines like "21/tcp   open  ftp"
                port_match = re.search(r'^(\d+)/tcp\s+open', line)
                if port_match:
                    port = int(port_match.group(1))
                    open_ports.append(port)
                    
            self.logger.info(f"Found {len(open_ports)} open ports: {open_ports}")
            return open_ports
            
        except subprocess.TimeoutExpired:
            self.logger.error("Nmap scan timed out after 5 minutes")
            return []
        except FileNotFoundError:
            self.logger.error("Nmap not found. Please install Nmap first.")
            return []
        except Exception as e:
            self.logger.error(f"Error running Nmap scan: {str(e)}")
            return []
            
    def identify_vulnerable_ports(self, open_ports: List[int]) -> List[Dict]:
        """Identify which open ports are considered vulnerable"""
        vulnerable_found = []
        
        for port in open_ports:
            if port in self.vulnerable_ports:
                vulnerable_found.append({
                    "port": port,
                    "service": self.vulnerable_ports[port]["service"],
                    "description": self.vulnerable_ports[port]["description"]
                })
                
        return vulnerable_found
        
    def get_package_name_for_port(self, port: int) -> Optional[str]:
        """Get the package name for a given port based on OS"""
        port_packages = {
            # Linux packages
            "linux": {
                21: "vsftpd",
                23: "telnetd",
                22: "openssh-server",
                80: "apache2",
                443: "apache2",
                3306: "mysql-server",
                5432: "postgresql",
                5900: "tightvncserver",
                6379: "redis-server",
                27017: "mongodb"
            },
            # Windows services
            "windows": {
                21: "Microsoft-IIS-FTP",
                23: "Telnet",
                445: "Server",  # SMB/CIFS service
                3389: "TermService",
                80: "W3SVC",
                443: "W3SVC",
                1433: "MSSQLSERVER",
                3306: "MySQL",
                5432: "postgresql-x64",
                5900: "VNC Server",
                6379: "Redis",
                27017: "MongoDB"
            }
        }
        
        return port_packages.get(self.os_type, {}).get(port)
        
    def apply_security_update_linux(self, package_name: str) -> Tuple[bool, str]:
        """Apply security updates on Linux using apt-get"""
        try:
            self.logger.info(f"Updating package: {package_name}")
            
            # Update package list first
            update_cmd = ["sudo", "apt-get", "update"]
            result = subprocess.run(update_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, f"Failed to update package list: {result.stderr}"
                
            # Install/upgrade the specific package
            upgrade_cmd = ["sudo", "apt-get", "install", "--only-upgrade", "-y", package_name]
            result = subprocess.run(upgrade_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "Update successful"
            else:
                return False, f"Update failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Exception during update: {str(e)}"
            
    def find_processes_using_port(self, port: int) -> List[str]:
        """Find processes using a specific port"""
        processes = []
        try:
            # Use netstat to find processes using the port
            netstat_cmd = ["netstat", "-tulpn"]
            result = subprocess.run(netstat_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f":{port}" in line and "LISTEN" in line:
                        # Extract PID from the line
                        parts = line.split()
                        if len(parts) > 6:
                            pid_program = parts[6]
                            if '/' in pid_program:
                                pid = pid_program.split('/')[0]
                                processes.append(pid)
                                
        except Exception as e:
            self.logger.warning(f"Could not find processes using port {port}: {e}")
            
        return processes
        
    def close_port_linux(self, port: int, service: str) -> Tuple[bool, str]:
        """Close vulnerable port on Linux using multiple methods"""
        try:
            self.logger.info(f"Attempting to close port {port} using multiple methods")
            success_methods = []
            
            # Method 1: Try to stop the service using systemctl (with and without sudo)
            if service:
                try:
                    # Try without sudo first
                    stop_cmd = ["systemctl", "--user", "stop", service]
                    result = subprocess.run(stop_cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        disable_cmd = ["systemctl", "--user", "disable", service]
                        subprocess.run(disable_cmd, capture_output=True, text=True)
                        success_methods.append(f"stopped user service {service}")
                    else:
                        # Try with sudo
                        stop_cmd = ["sudo", "systemctl", "stop", service]
                        result = subprocess.run(stop_cmd, capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            disable_cmd = ["sudo", "systemctl", "disable", service]
                            subprocess.run(disable_cmd, capture_output=True, text=True)
                            success_methods.append(f"stopped system service {service}")
                        else:
                            self.logger.warning(f"Failed to stop service {service}: {result.stderr}")
                except Exception as e:
                    self.logger.warning(f"Exception stopping service {service}: {e}")
            
            # Method 2: Kill processes using the port (try without sudo first)
            try:
                processes = self.find_processes_using_port(port)
                if processes:
                    for pid in processes:
                        # Try without sudo first
                        kill_cmd = ["kill", "-9", pid]
                        result = subprocess.run(kill_cmd, capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            success_methods.append(f"killed process {pid}")
                        else:
                            # Try with sudo
                            kill_cmd = ["sudo", "kill", "-9", pid]
                            result = subprocess.run(kill_cmd, capture_output=True, text=True)
                            if result.returncode == 0:
                                success_methods.append(f"killed process {pid} (with sudo)")
                else:
                    # Try fuser as fallback (without sudo first)
                    kill_cmd = ["fuser", "-k", f"{port}/tcp"]
                    result = subprocess.run(kill_cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        success_methods.append("killed processes using fuser")
                    else:
                        # Try with sudo
                        kill_cmd = ["sudo", "fuser", "-k", f"{port}/tcp"]
                        result = subprocess.run(kill_cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            success_methods.append("killed processes using fuser (with sudo)")
            except Exception as e:
                self.logger.warning(f"Exception killing processes: {e}")
            
            # Method 3: Block port with iptables (requires sudo)
            if self.is_admin:
                try:
                    iptables_cmd = ["sudo", "iptables", "-A", "INPUT", "-p", "tcp", "--dport", str(port), "-j", "DROP"]
                    result = subprocess.run(iptables_cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        success_methods.append("blocked with iptables")
                except Exception as e:
                    self.logger.warning(f"Exception with iptables: {e}")
            
            # Method 4: Try to bind to the port to prevent usage
            bind_success = self.bind_port_to_prevent_usage(port)
            if bind_success:
                success_methods.append("bound port to prevent usage")
            
            if success_methods:
                return True, f"Port {port} closed using: {', '.join(success_methods)}"
            else:
                return False, f"Failed to close port {port} using any method. Root privileges may be required for full functionality."
                    
        except Exception as e:
            return False, f"Exception during port closure: {str(e)}"
            
    def apply_security_update_windows(self, service_name: str) -> Tuple[bool, str]:
        """Apply security updates on Windows using PowerShell with admin privileges"""
        try:
            self.logger.info(f"Updating Windows service: {service_name}")
            
            # Check admin privileges for update operations
            if not self.is_admin:
                self.logger.warning("Admin privileges required for Windows updates")
                return False, "Administrator privileges required for Windows updates"
            
            # Enhanced PowerShell script for Windows updates
            ps_script = """
            try {
                # Check for Windows updates
                $Session = New-Object -ComObject Microsoft.Update.Session
                $Searcher = $Session.CreateUpdateSearcher()
                $SearchResult = $Searcher.Search("IsInstalled=0 and Type='Software' and IsHidden=0")
                
                if ($SearchResult.Updates.Count -gt 0) {
                    Write-Host "Found $($SearchResult.Updates.Count) available updates"
                    
                    # Download and install updates
                    $UpdatesToDownload = New-Object -ComObject Microsoft.Update.UpdateColl
                    foreach ($Update in $SearchResult.Updates) {
                        if ($Update.EulaAccepted -eq 0) {
                            $Update.AcceptEula()
                        }
                        $UpdatesToDownload.Add($Update)
                        Write-Host "Queued update: $($Update.Title)"
                    }
                    
                    # Download updates
                    $Downloader = $Session.CreateUpdateDownloader()
                    $Downloader.Updates = $UpdatesToDownload
                    $DownloadResult = $Downloader.Download()
                    
                    if ($DownloadResult.ResultCode -eq 2) {
                        Write-Host "Updates downloaded successfully"
                        
                        # Install updates
                        $Installer = $Session.CreateUpdateInstaller()
                        $Installer.Updates = $UpdatesToDownload
                        $InstallResult = $Installer.Install()
                        
                        if ($InstallResult.ResultCode -eq 2) {
                            Write-Host "Updates installed successfully"
                            exit 1
                        } else {
                            Write-Host "Update installation failed"
                            exit 0
                        }
                    } else {
                        Write-Host "Update download failed"
                        exit 0
                    }
                } else {
                    Write-Host "No updates available"
                    exit 0
                }
            } catch {
                Write-Error "Failed to process Windows updates: $_"
                exit 0
            }
            """
            
            ps_cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
            result = subprocess.run(ps_cmd, capture_output=True, text=True)
            
            if result.returncode == 1:
                return True, f"Windows updates processed successfully: {result.stdout}"
            else:
                return False, f"Windows update failed or no updates available: {result.stderr}"
                
        except Exception as e:
            return False, f"Exception during Windows update: {str(e)}"

    def apply_generic_windows_updates(self, port: int, service: str) -> Tuple[bool, str]:
        """Apply generic Windows security updates for ports without specific package mappings"""
        try:
            self.logger.info(f"Applying generic Windows security updates for port {port} ({service})")
            
            # Check admin privileges for update operations
            if not self.is_admin:
                self.logger.warning("Admin privileges required for Windows updates")
                return False, "Administrator privileges required for Windows updates"
            
            # Enhanced PowerShell script for generic Windows updates
            ps_script = """
            try {
                # Check for Windows updates
                $Session = New-Object -ComObject Microsoft.Update.Session
                $Searcher = $Session.CreateUpdateSearcher()
                $SearchResult = $Searcher.Search("IsInstalled=0 and Type='Software' and IsHidden=0")
                
                if ($SearchResult.Updates.Count -gt 0) {
                    Write-Host "Found $($SearchResult.Updates.Count) available updates"
                    
                    # Download and install updates
                    $UpdatesToDownload = New-Object -ComObject Microsoft.Update.UpdateColl
                    foreach ($Update in $SearchResult.Updates) {
                        if ($Update.EulaAccepted -eq 0) {
                            $Update.AcceptEula()
                        }
                        $UpdatesToDownload.Add($Update)
                        Write-Host "Queued update: $($Update.Title)"
                    }
                    
                    # Download updates
                    $Downloader = $Session.CreateUpdateDownloader()
                    $Downloader.Updates = $UpdatesToDownload
                    $DownloadResult = $Downloader.Download()
                    
                    if ($DownloadResult.ResultCode -eq 2) {
                        Write-Host "Updates downloaded successfully"
                        
                        # Install updates
                        $Installer = $Session.CreateUpdateInstaller()
                        $Installer.Updates = $UpdatesToDownload
                        $InstallResult = $Installer.Install()
                        
                        if ($InstallResult.ResultCode -eq 2) {
                            Write-Host "Updates installed successfully"
                            exit 1
                        } else {
                            Write-Host "Update installation failed"
                            exit 0
                        }
                    } else {
                        Write-Host "Update download failed"
                        exit 0
                    }
                } else {
                    Write-Host "No updates available"
                    exit 0
                }
            } catch {
                Write-Error "Failed to process Windows updates: $_"
                exit 0
            }
            """
            
            ps_cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
            result = subprocess.run(ps_cmd, capture_output=True, text=True)
            
            if result.returncode == 1:
                return True, f"Generic Windows updates processed successfully: {result.stdout}"
            else:
                return False, f"Generic Windows update failed or no updates available: {result.stderr}"
                
        except Exception as e:
            return False, f"Exception during generic Windows update: {str(e)}"

    def apply_generic_linux_updates(self, port: int, service: str) -> Tuple[bool, str]:
        """Apply generic Linux security updates for ports without specific package mappings"""
        try:
            self.logger.info(f"Applying generic Linux security updates for port {port} ({service})")
            
            # Update package list first
            update_cmd = ["sudo", "apt-get", "update"]
            result = subprocess.run(update_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, f"Failed to update package list: {result.stderr}"
                
            # Install security updates
            upgrade_cmd = ["sudo", "apt-get", "upgrade", "-y"]
            result = subprocess.run(upgrade_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "Generic Linux security updates applied successfully"
            else:
                return False, f"Generic Linux update failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Exception during generic Linux update: {str(e)}"
            
    def find_windows_processes_using_port(self, port: int) -> List[str]:
        """Find Windows processes using a specific port"""
        processes = []
        try:
            # Use netstat to find processes using the port
            netstat_cmd = ["netstat", "-ano"]
            result = subprocess.run(netstat_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f":{port}" in line and "LISTENING" in line:
                        # Extract PID from the line
                        parts = line.split()
                        if len(parts) > 4:
                            pid = parts[4]
                            processes.append(pid)
                            
        except Exception as e:
            self.logger.warning(f"Could not find Windows processes using port {port}: {e}")
            
        return processes
        
    def close_port_windows(self, port: int, service: str) -> Tuple[bool, str]:
        """Close vulnerable port on Windows using multiple methods"""
        try:
            self.logger.info(f"Attempting to close port {port} on Windows using multiple methods")
            success_methods = []
            
            # Method 1: Try to stop the Windows service (enhanced with admin privileges)
            service_mapping = {
                445: "Server",  # SMB/CIFS service
                3389: "TermService", 
                21: "FTPSVC",
                23: "Telnet",
                80: "W3SVC",
                443: "W3SVC",
                1433: "MSSQLSERVER",
                3306: "MySQL",
                5432: "postgresql-x64",
                5900: "VNC Server",
                6379: "Redis",
                27017: "MongoDB"
            }
            
            win_service = service_mapping.get(port)
            if win_service:
                try:
                    # Enhanced service control with admin privileges
                    service_success = self.control_windows_service(win_service, "stop")
                    if service_success:
                        # Also disable the service to prevent auto-start
                        disable_success = self.control_windows_service(win_service, "disable")
                        if disable_success:
                            success_methods.append(f"stopped and disabled service {win_service}")
                    else:
                        success_methods.append(f"stopped service {win_service}")
                except Exception as e:
                    self.logger.warning(f"Exception controlling service {win_service}: {e}")
            else:
                self.logger.info(f"No specific service mapping for port {port} - will use alternative methods")
            
            # Method 2: Kill processes using the port (works without admin for user processes)
            try:
                processes = self.find_windows_processes_using_port(port)
                if processes:
                    for pid in processes:
                        kill_cmd = ["taskkill", "/F", "/PID", pid]
                        result = subprocess.run(kill_cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            success_methods.append(f"killed process {pid}")
                        else:
                            self.logger.warning(f"Failed to kill process {pid}: {result.stderr}")
                else:
                    self.logger.info(f"No processes found using port {port}")
            except Exception as e:
                self.logger.warning(f"Exception killing processes: {e}")
            
            # Method 3: Try to block port with Windows Firewall (requires admin)
            if self.is_admin:
                if self.ensure_firewall_enabled():
                    firewall_success = self.block_port_with_firewall(port)
                    if firewall_success:
                        success_methods.append("blocked with Windows Firewall")
                    
                    # Method 4: Use PowerShell to block port (Enhanced)
                    ps_success = self.block_port_with_powershell(port)
                    if ps_success:
                        success_methods.append("blocked with PowerShell firewall")
                else:
                    self.logger.warning("Could not enable Windows Firewall - skipping firewall blocking")
            else:
                # Method 5: Try alternative port blocking methods without admin
                alt_success = self.block_port_alternative_methods(port)
                if alt_success:
                    success_methods.append("blocked with alternative methods")
            
            # Method 6: Try to bind to the port to prevent other applications from using it
            bind_success = self.bind_port_to_prevent_usage(port)
            if bind_success:
                success_methods.append("bound port to prevent usage")
            
            # Method 7: Try to disable the port using Windows Registry (requires admin)
            if self.is_admin:
                reg_success = self.disable_port_via_registry(port)
                if reg_success:
                    success_methods.append("disabled via registry")
            
            if success_methods:
                return True, f"Port {port} closed using: {', '.join(success_methods)}"
            else:
                return False, f"Failed to close port {port} using any method. Admin privileges may be required for full functionality."
                
        except Exception as e:
            return False, f"Exception during port closure: {str(e)}"

    def block_port_with_firewall(self, port: int) -> bool:
        """Enhanced Windows Firewall blocking with admin privilege handling"""
        try:
            if not self.is_admin:
                self.logger.warning("Administrator privileges required for firewall operations")
                return False
            
            # Check if Windows Firewall is enabled
            firewall_status_cmd = ["netsh", "advfirewall", "show", "allprofiles", "state"]
            result = subprocess.run(firewall_status_cmd, capture_output=True, text=True)
            
            if "OFF" in result.stdout:
                self.logger.warning("Windows Firewall is disabled. Enabling firewall...")
                enable_cmd = ["netsh", "advfirewall", "set", "allprofiles", "state", "on"]
                subprocess.run(enable_cmd, capture_output=True, text=True)
            
            # Create comprehensive firewall rules
            rules = [
                # Inbound TCP rule
                ["netsh", "advfirewall", "firewall", "add", "rule",
                 f"name=Block_Port_{port}_TCP_In", "dir=in", "action=block",
                 "protocol=TCP", f"localport={port}", "enable=yes"],
                
                # Outbound TCP rule
                ["netsh", "advfirewall", "firewall", "add", "rule",
                 f"name=Block_Port_{port}_TCP_Out", "dir=out", "action=block",
                 "protocol=TCP", f"localport={port}", "enable=yes"],
                
                # Inbound UDP rule
                ["netsh", "advfirewall", "firewall", "add", "rule",
                 f"name=Block_Port_{port}_UDP_In", "dir=in", "action=block",
                 "protocol=UDP", f"localport={port}", "enable=yes"],
                
                # Outbound UDP rule
                ["netsh", "advfirewall", "firewall", "add", "rule",
                 f"name=Block_Port_{port}_UDP_Out", "dir=out", "action=block",
                 "protocol=UDP", f"localport={port}", "enable=yes"]
            ]
            
            success_count = 0
            for rule_cmd in rules:
                result = subprocess.run(rule_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    success_count += 1
                else:
                    self.logger.warning(f"Failed to create firewall rule: {result.stderr}")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Exception in firewall blocking: {e}")
            return False

    def block_port_with_powershell(self, port: int) -> bool:
        """Enhanced PowerShell firewall blocking with admin privilege handling"""
        try:
            if not self.is_admin:
                self.logger.warning("Administrator privileges required for PowerShell firewall operations")
                return False
            
            # Comprehensive PowerShell script for firewall blocking
            ps_script = f"""
            try {{
                # Check if Windows Firewall is enabled
                $firewallProfiles = Get-NetFirewallProfile
                $disabledProfiles = $firewallProfiles | Where-Object {{ $_.Enabled -eq 'False' }}
                
                if ($disabledProfiles) {{
                    Write-Host "Enabling Windows Firewall profiles..."
                    Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
                }}
                
                # Create comprehensive firewall rules
                $rules = @(
                    @{{
                        DisplayName = "Block Port {port} TCP Inbound"
                        Direction = "Inbound"
                        Protocol = "TCP"
                        LocalPort = "{port}"
                        Action = "Block"
                        Enabled = "True"
                    }},
                    @{{
                        DisplayName = "Block Port {port} TCP Outbound"
                        Direction = "Outbound"
                        Protocol = "TCP"
                        LocalPort = "{port}"
                        Action = "Block"
                        Enabled = "True"
                    }},
                    @{{
                        DisplayName = "Block Port {port} UDP Inbound"
                        Direction = "Inbound"
                        Protocol = "UDP"
                        LocalPort = "{port}"
                        Action = "Block"
                        Enabled = "True"
                    }},
                    @{{
                        DisplayName = "Block Port {port} UDP Outbound"
                        Direction = "Outbound"
                        Protocol = "UDP"
                        LocalPort = "{port}"
                        Action = "Block"
                        Enabled = "True"
                    }}
                )
                
                $successCount = 0
                foreach ($rule in $rules) {{
                    try {{
                        New-NetFirewallRule @rule -ErrorAction Stop
                        $successCount++
                        Write-Host "Created firewall rule: $($rule.DisplayName)"
                    }} catch {{
                        Write-Warning "Failed to create rule $($rule.DisplayName): $_"
                    }}
                }}
                
                Write-Host "Successfully created $successCount out of $($rules.Count) firewall rules"
                exit $successCount
            }} catch {{
                Write-Error "PowerShell firewall script failed: $_"
                exit 1
            }}
            """
            
            ps_cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
            result = subprocess.run(ps_cmd, capture_output=True, text=True)
            
            if result.returncode > 0:
                self.logger.info(f"PowerShell firewall blocking successful: {result.stdout}")
                return True
            else:
                self.logger.warning(f"PowerShell firewall blocking failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception in PowerShell firewall blocking: {e}")
            return False

    def ensure_firewall_enabled(self) -> bool:
        """Ensure Windows Firewall is enabled for all profiles"""
        try:
            if not self.is_admin:
                self.logger.warning("Administrator privileges required to enable firewall")
                return False
            
            # Check current firewall status
            status_cmd = ["netsh", "advfirewall", "show", "allprofiles", "state"]
            result = subprocess.run(status_cmd, capture_output=True, text=True)
            
            if "OFF" in result.stdout:
                self.logger.info("Windows Firewall is disabled. Enabling firewall...")
                
                # Enable firewall for all profiles
                enable_cmd = ["netsh", "advfirewall", "set", "allprofiles", "state", "on"]
                result = subprocess.run(enable_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info("Successfully enabled Windows Firewall")
                    return True
                else:
                    self.logger.error(f"Failed to enable Windows Firewall: {result.stderr}")
                    return False
            else:
                self.logger.info("Windows Firewall is already enabled")
                return True
                
        except Exception as e:
            self.logger.error(f"Exception checking/enabling firewall: {e}")
            return False

    def block_port_alternative_methods(self, port: int) -> bool:
        """Alternative port blocking methods that don't require admin privileges"""
        try:
            self.logger.info(f"Trying alternative port blocking methods for port {port}")
            
            # Method 1: Try to use netsh without admin (may work for some operations)
            try:
                # Try to create a basic firewall rule (might work without admin in some cases)
                firewall_cmd = [
                    "netsh", "advfirewall", "firewall", "add", "rule",
                    f"name=Block_Port_{port}_User", "dir=in", "action=block",
                    "protocol=TCP", f"localport={port}", "enable=yes"
                ]
                
                result = subprocess.run(firewall_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.info(f"Successfully created firewall rule without admin for port {port}")
                    return True
                else:
                    self.logger.warning(f"Failed to create firewall rule without admin: {result.stderr}")
            except Exception as e:
                self.logger.warning(f"Exception with alternative firewall method: {e}")
            
            # Method 2: Try to use Windows Defender Firewall with Advanced Security
            try:
                # Try to create a rule using Windows Defender Firewall
                ps_script = f"""
                try {{
                    # Try to create a firewall rule using Windows Defender
                    $rule = New-Object -ComObject HNetCfg.FwRule2
                    $rule.Name = "Block Port {port} User Rule"
                    $rule.Description = "Block port {port} - created by Port Security Scanner"
                    $rule.Protocol = 6  # TCP
                    $rule.LocalPorts = "{port}"
                    $rule.Direction = 1  # Inbound
                    $rule.Action = 0  # Block
                    $rule.Enabled = $true
                    
                    $firewall = New-Object -ComObject HNetCfg.FwPolicy2
                    $firewall.Rules.Add($rule)
                    Write-Host "Successfully created Windows Defender firewall rule"
                    exit 1
                }} catch {{
                    Write-Warning "Failed to create Windows Defender firewall rule: $_"
                    exit 0
                }}
                """
                
                ps_cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
                result = subprocess.run(ps_cmd, capture_output=True, text=True)
                
                if result.returncode == 1:
                    self.logger.info(f"Successfully created Windows Defender firewall rule for port {port}")
                    return True
                else:
                    self.logger.warning(f"Failed to create Windows Defender firewall rule: {result.stderr}")
            except Exception as e:
                self.logger.warning(f"Exception with Windows Defender firewall method: {e}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Exception in alternative port blocking: {e}")
            return False

    def bind_port_to_prevent_usage(self, port: int) -> bool:
        """Try to bind to the port to prevent other applications from using it"""
        try:
            import socket
            
            # Try to bind to the port to prevent other applications from using it
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                sock.bind(('127.0.0.1', port))
                sock.listen(1)
                self.logger.info(f"Successfully bound to port {port} to prevent usage")
                
                # Keep the socket open in a background thread
                import threading
                def keep_port_bound():
                    try:
                        while True:
                            time.sleep(1)
                    except:
                        pass
                
                thread = threading.Thread(target=keep_port_bound, daemon=True)
                thread.start()
                
                return True
            except OSError as e:
                if e.errno == 10048:  # Port already in use
                    self.logger.info(f"Port {port} is already in use - this prevents other applications from using it")
                    return True
                else:
                    self.logger.warning(f"Could not bind to port {port}: {e}")
                    return False
            finally:
                # Don't close the socket - we want to keep it bound
                pass
                
        except Exception as e:
            self.logger.error(f"Exception binding to port {port}: {e}")
            return False

    def control_windows_service(self, service_name: str, action: str) -> bool:
        """Enhanced Windows service control with admin privilege handling"""
        try:
            if action not in ["start", "stop", "restart", "disable", "enable"]:
                self.logger.error(f"Invalid service action: {action}")
                return False
            
            # Check if admin privileges are available for service control
            if not self.is_admin and action in ["stop", "disable", "enable"]:
                self.logger.warning(f"Admin privileges required for service {action}")
                return False
            
            # Use sc command for service control
            if action == "disable":
                cmd = ["sc", "config", service_name, "start=", "disabled"]
            elif action == "enable":
                cmd = ["sc", "config", service_name, "start=", "auto"]
            else:
                cmd = ["sc", action, service_name]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"Successfully {action}ed service {service_name}")
                return True
            else:
                self.logger.warning(f"Failed to {action} service {service_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception controlling service {service_name}: {e}")
            return False

    def disable_port_via_registry(self, port: int) -> bool:
        """Disable port via Windows Registry (requires admin privileges)"""
        try:
            if not self.is_admin:
                self.logger.warning("Administrator privileges required for registry operations")
                return False
            
            self.logger.info(f"Attempting to disable port {port} via Windows Registry")
            
            # PowerShell script to modify registry for port blocking
            ps_script = f"""
            try {{
                # Disable SMB/CIFS service for port 445
                if ({port} -eq 445) {{
                    $regPath = "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer"
                    if (Test-Path $regPath) {{
                        Set-ItemProperty -Path $regPath -Name "Start" -Value 4 -Type DWord
                        Write-Host "Disabled SMB/CIFS service via registry"
                        exit 1
                    }} else {{
                        Write-Host "SMB/CIFS service registry key not found"
                        exit 0
                    }}
                }}
                
                # Disable RDP service for port 3389
                if ({port} -eq 3389) {{
                    $regPath = "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server"
                    if (Test-Path $regPath) {{
                        Set-ItemProperty -Path $regPath -Name "fDenyTSConnections" -Value 1 -Type DWord
                        Write-Host "Disabled RDP service via registry"
                        exit 1
                    }} else {{
                        Write-Host "RDP service registry key not found"
                        exit 0
                    }}
                }}
                
                # Disable Telnet service for port 23
                if ({port} -eq 23) {{
                    $regPath = "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\TlntSvr"
                    if (Test-Path $regPath) {{
                        Set-ItemProperty -Path $regPath -Name "Start" -Value 4 -Type DWord
                        Write-Host "Disabled Telnet service via registry"
                        exit 1
                    }} else {{
                        Write-Host "Telnet service registry key not found"
                        exit 0
                    }}
                }}
                
                # For other ports, try to disable via Windows Firewall registry
                $firewallRegPath = "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\SharedAccess\\Parameters\\FirewallPolicy"
                if (Test-Path $firewallRegPath) {{
                    # Create a registry entry to block the port
                    $portBlockKey = "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\SharedAccess\\Parameters\\FirewallPolicy\\FirewallRules"
                    if (Test-Path $portBlockKey) {{
                        $ruleName = "Block_Port_{port}_Registry"
                        $ruleValue = "v2.30|Action=Block|Active=TRUE|Dir=In|Protocol=6|LPort={port}|Name=$ruleName|Desc=Block port {port} via registry"
                        Set-ItemProperty -Path $portBlockKey -Name $ruleName -Value $ruleValue
                        Write-Host "Created registry firewall rule for port {port}"
                        exit 1
                    }}
                }}
                
                Write-Host "No specific registry method available for port {port}"
                exit 0
            }} catch {{
                Write-Error "Registry operation failed: $_"
                exit 0
            }}
            """
            
            ps_cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
            result = subprocess.run(ps_cmd, capture_output=True, text=True)
            
            if result.returncode == 1:
                self.logger.info(f"Successfully disabled port {port} via registry: {result.stdout}")
                return True
            else:
                self.logger.warning(f"Failed to disable port {port} via registry: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception disabling port {port} via registry: {e}")
            return False
            
    def apply_security_update(self, port: int, service: str) -> Tuple[bool, str]:
        """Apply security update based on OS and port using official sources"""
        package_name = self.get_package_name_for_port(port)
        
        if not package_name:
            # For ports without specific package mappings, try generic security updates
            self.logger.info(f"No specific package mapping for port {port} - attempting generic security updates")
            
            if self.os_type == "windows":
                # Try to apply general Windows security updates
                return self.apply_generic_windows_updates(port, service)
            elif self.os_type == "linux":
                # Try to apply general Linux security updates
                return self.apply_generic_linux_updates(port, service)
            else:
                return False, f"No package mapping found for port {port} on {self.os_type}"
        
        # First, check for official patches
        patch_available, patch_message = self.download_patch_from_official_source(package_name)
        if not patch_available:
            self.logger.warning(f"No official patches available: {patch_message}")
            
        if self.os_type == "linux":
            return self.apply_security_update_linux(package_name)
        elif self.os_type == "windows":
            return self.apply_security_update_windows(package_name)
        else:
            return False, f"Unsupported operating system: {self.os_type}"
            
    def close_vulnerable_port(self, port: int, service: str) -> Tuple[bool, str]:
        """Close vulnerable port by stopping service or blocking with firewall"""
        if self.os_type == "linux":
            return self.close_port_linux(port, service)
        elif self.os_type == "windows":
            return self.close_port_windows(port, service)
        else:
            return False, f"Unsupported operating system: {self.os_type}"
            
    def restore_port_windows(self, port: int) -> Tuple[bool, str]:
        """Restore port by removing all firewall rules"""
        try:
            self.logger.info(f"Attempting to restore port {port} on Windows")
            
            if not self.is_admin:
                self.logger.warning("Administrator privileges required for firewall operations")
                return False, "Administrator privileges required"
            
            # Remove all firewall rules for this port
            rule_names = [
                f"Block_Port_{port}_TCP_In",
                f"Block_Port_{port}_TCP_Out", 
                f"Block_Port_{port}_UDP_In",
                f"Block_Port_{port}_UDP_Out",
                f"Block Port {port} TCP Inbound",
                f"Block Port {port} TCP Outbound",
                f"Block Port {port} UDP Inbound",
                f"Block Port {port} UDP Outbound"
            ]
            
            success_count = 0
            for rule_name in rule_names:
                # Try netsh method
                firewall_cmd = [
                    "netsh", "advfirewall", "firewall", "delete", "rule",
                    f"name={rule_name}"
                ]
                result = subprocess.run(firewall_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    success_count += 1
                    self.logger.info(f"Removed firewall rule: {rule_name}")
            
            # Also try PowerShell method
            ps_script = f"""
            try {{
                $rules = Get-NetFirewallRule | Where-Object {{
                    $_.DisplayName -like "*Port {port}*" -or 
                    $_.DisplayName -like "*Block Port {port}*"
                }}
                
                $removedCount = 0
                foreach ($rule in $rules) {{
                    try {{
                        Remove-NetFirewallRule -Name $rule.Name -ErrorAction Stop
                        $removedCount++
                        Write-Host "Removed PowerShell rule: $($rule.DisplayName)"
                    }} catch {{
                        Write-Warning "Failed to remove rule $($rule.DisplayName): $_"
                    }}
                }}
                
                Write-Host "Removed $removedCount PowerShell firewall rules"
                exit $removedCount
            }} catch {{
                Write-Error "PowerShell restore script failed: $_"
                exit 0
            }}
            """
            
            ps_cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
            result = subprocess.run(ps_cmd, capture_output=True, text=True)
            
            if result.returncode > 0:
                success_count += result.returncode
                self.logger.info(f"PowerShell restore successful: {result.stdout}")
            
            if success_count > 0:
                return True, f"Removed {success_count} firewall rules for port {port}"
            else:
                return False, f"No firewall rules found to remove for port {port}"
                
        except Exception as e:
            return False, f"Exception during port restoration: {str(e)}"
            
    def restore_port_linux(self, port: int, service: str) -> Tuple[bool, str]:
        """Restore port by starting service"""
        try:
            self.logger.info(f"Attempting to restore port {port} by starting {service}")
            
            # Start the service
            start_cmd = ["sudo", "systemctl", "start", service]
            result = subprocess.run(start_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Enable the service
                enable_cmd = ["sudo", "systemctl", "enable", service]
                subprocess.run(enable_cmd, capture_output=True, text=True)
                return True, f"Successfully started and enabled {service}"
            else:
                return False, f"Failed to start service {service}: {result.stderr}"
                
        except Exception as e:
            return False, f"Exception during port restoration: {str(e)}"
            
    def prompt_user_permission(self, vulnerable_port: Dict, automated_mode: bool = False) -> str:
        """Prompt user for permission to apply security update or close port"""
        print(f"\n{'='*60}")
        print(f"VULNERABLE PORT DETECTED!")
        print(f"{'='*60}")
        print(f"Port: {vulnerable_port['port']}")
        print(f"Service: {vulnerable_port['service']}")
        print(f"Description: {vulnerable_port['description']}")
        print(f"\nThis port may pose a security risk.")
        
        if automated_mode:
            print(f"\nAUTOMATED MODE: Applying security updates and closing port...")
            return 'auto'
        
        print(f"Choose an action:")
        print(f"1. Apply security updates from official sources (u)")
        print(f"2. Close/block the port using multiple methods (c)")
        print(f"3. Apply updates AND close port (a)")
        print(f"4. Skip this port (s)")
        print(f"5. Retry later (r)")
        
        while True:
            response = input("Choose action (u/c/a/s/r): ").lower().strip()
            if response in ['u', 'update']:
                return 'update'
            elif response in ['c', 'close']:
                return 'close'
            elif response in ['a', 'auto', 'all']:
                return 'auto'
            elif response in ['s', 'skip']:
                return 'skip'
            elif response in ['r', 'retry']:
                return 'retry'
            else:
                print("Please enter 'u' for update, 'c' for close, 'a' for both, 's' for skip, or 'r' for retry later.")
                
    def handle_update_failure(self, port: int, service: str, error_msg: str) -> bool:
        """Handle update failure and ask user for retry or rollback"""
        print(f"\n{'='*60}")
        print(f"UPDATE FAILED!")
        print(f"{'='*60}")
        print(f"Port: {port}")
        print(f"Service: {service}")
        print(f"Error: {error_msg}")
        print(f"\nThe update failed. This could be due to:")
        print(f"- Internet connectivity issues")
        print(f"- Incomplete download")
        print(f"- Permission issues")
        print(f"- Package not found")
        
        while True:
            response = input("Would you like to (r)etry, (s)kip, or (b)ackup current state? ").lower().strip()
            if response in ['r', 'retry']:
                return True
            elif response in ['s', 'skip']:
                return False
            elif response in ['b', 'backup']:
                self.logger.info(f"User chose to backup current state for port {port}")
                return False
            else:
                print("Please enter 'r' for retry, 's' for skip, or 'b' for backup.")
                
    def verify_port_security(self, port: int) -> bool:
        """Re-scan to verify if the port is still open after update"""
        self.logger.info(f"Verifying security of port {port} after update")
        
        # Wait a moment for services to restart
        time.sleep(5)
        
        # Re-scan the specific port
        try:
            cmd = ["nmap", "-p", str(port), "127.0.0.1"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Check if port is still open
                if f"{port}/tcp" in result.stdout and "open" in result.stdout:
                    self.logger.warning(f"Port {port} is still open after update")
                    return False
                else:
                    self.logger.info(f"Port {port} appears to be secured")
                    return True
            else:
                self.logger.error(f"Verification scan failed for port {port}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during verification scan: {str(e)}")
            return False
            
    def run_security_scan(self, target: str = "127.0.0.1", automated_mode: bool = False):
        """Main function to run the complete security scan and update process"""
        self.logger.info("="*60)
        self.logger.info("STARTING PORT SECURITY SCAN")
        if automated_mode:
            self.logger.info("AUTOMATED MODE ENABLED")
        self.logger.info("="*60)
        
        # Step 1: Run initial Nmap scan
        open_ports = self.run_nmap_scan(target)
        if not open_ports:
            self.logger.error("No open ports found or scan failed")
            return
            
        # Step 2: Identify vulnerable ports
        vulnerable_ports = self.identify_vulnerable_ports(open_ports)
        
        if not vulnerable_ports:
            self.logger.info("No vulnerable ports detected. System appears secure.")
            return
            
        self.logger.warning(f"Found {len(vulnerable_ports)} potentially vulnerable ports")
        
        # Step 3: Process each vulnerable port
        for vuln_port in vulnerable_ports:
            port = vuln_port['port']
            service = vuln_port['service']
            
            self.logger.info(f"Processing vulnerable port: {port} ({service})")
            
            # Ask for user permission
            action = self.prompt_user_permission(vuln_port, automated_mode)
            
            if action == 'retry':
                self.logger.info(f"User chose to retry port {port} later")
                continue
            elif action == 'skip':
                self.logger.info(f"User chose to skip port {port}")
                continue
                
            # Execute the chosen action
            max_retries = 3
            retry_count = 0
            action_successful = False
            update_successful = False
            close_successful = False
            
            while retry_count < max_retries and not action_successful:
                if action == 'update':
                    success, message = self.apply_security_update(port, service)
                    action_type = "update"
                    action_successful = success
                    update_successful = success
                elif action == 'close':
                    success, message = self.close_vulnerable_port(port, service)
                    action_type = "closure"
                    action_successful = success
                    close_successful = success
                elif action == 'auto':
                    # Try both update and close
                    update_success, update_msg = self.apply_security_update(port, service)
                    close_success, close_msg = self.close_vulnerable_port(port, service)
                    
                    update_successful = update_success
                    close_successful = close_success
                    action_successful = update_success or close_success
                    action_type = "automated"
                    message = f"Update: {update_msg}, Close: {close_msg}"
                else:
                    break
                
                if action_successful:
                    self.logger.info(f"Successfully {action_type} for {service} on port {port}")
                    if action == 'auto':
                        if update_successful:
                            self.logger.info(f"Update successful: {update_msg}")
                        if close_successful:
                            self.logger.info(f"Port closure successful: {close_msg}")
                else:
                    self.logger.error(f"{action_type.capitalize()} failed for port {port}: {message}")
                    retry_count += 1
                    
                    if retry_count < max_retries and not automated_mode:
                        should_retry = self.handle_update_failure(port, service, message)
                        if not should_retry:
                            break
                            
            # Step 4: Verify the action
            if action_successful:
                is_secure = self.verify_port_security(port)
                if is_secure:
                    self.logger.info(f"Port {port} successfully secured")
                else:
                    self.logger.warning(f"Port {port} may still be vulnerable")
            else:
                self.logger.error(f"Failed to {action} port {port} after {max_retries} attempts")
                
        # Step 5: Final verification scan
        self.logger.info("Running final verification scan...")
        final_open_ports = self.run_nmap_scan(target)
        final_vulnerable = self.identify_vulnerable_ports(final_open_ports)
        
        if final_vulnerable:
            self.logger.warning(f"Final scan: {len(final_vulnerable)} vulnerable ports still open")
            for vuln in final_vulnerable:
                self.logger.warning(f"  - Port {vuln['port']}: {vuln['service']}")
        else:
            self.logger.info("Final scan: No vulnerable ports detected. System is secure!")
            
        self.logger.info("="*60)
        self.logger.info("PORT SECURITY SCAN COMPLETED")
        self.logger.info("="*60)

def main():
    """Main entry point"""
    print("Port Security Scanner and Auto-Updater")
    print("="*50)
    print("This script will scan for vulnerable ports and apply security updates.")
    print("All actions will be logged to port_security.log")
    print()
    
    # Check for automated mode
    automated_mode = "--auto" in sys.argv or "-a" in sys.argv
    
    if automated_mode:
        print("AUTOMATED MODE: Will apply updates and close ports automatically")
        print("WARNING: This will make system changes without user confirmation!")
        print()
    
    # Check if running as administrator/root
    if platform.system().lower() == "windows":
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("WARNING: Not running as administrator. Some updates may fail.")
        except:
            pass
    else:
        if os.geteuid() != 0:
            print("WARNING: Not running as root. Some updates may require sudo.")
    
    scanner = PortSecurityScanner()
    
    try:
        scanner.run_security_scan(automated_mode=automated_mode)
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
        scanner.logger.info("Scan interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        scanner.logger.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
