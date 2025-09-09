# Port Security Scanner and Auto-Updater

A comprehensive Python-based security automation script that performs port scanning, identifies vulnerable services, applies security updates from official sources, and closes vulnerable ports using multiple methods with user consent and detailed logging.

## Features

### Core Functionality
- **Full Port Scanning**: Uses Nmap to perform comprehensive port scans (`nmap -p- 127.0.0.1`)
- **Vulnerable Port Detection**: Compares open ports against a predefined list of risky services
- **Multiple Security Actions**: Choose between updating services, closing/blocking ports, or both
- **Official Patch Sources**: Downloads security patches from trusted official repositories
- **Patch Integrity Verification**: SHA256 hash verification for downloaded patches

### Enhanced Port Closure Methods
- **Linux**:
  - Stop services with systemctl
  - Kill processes using netstat and kill commands
  - Block ports with iptables firewall rules
  - Use fuser as fallback method
- **Windows**:
  - Stop services with sc command
  - Kill processes using taskkill
  - Block ports with Windows Firewall (netsh)
  - Use PowerShell firewall rules as additional method

### Advanced Features
- **Automated Mode**: Non-interactive operation with `--auto` flag
- **Process Detection**: Advanced process identification and management
- **Multiple Closure Attempts**: Tries multiple methods to ensure port closure
- **User Consent**: Interactive prompts with multiple action options
- **OS-Agnostic**: Supports both Linux (apt-get) and Windows (PowerShell) package management
- **Comprehensive Logging**: All actions logged to `port_security.log` with timestamps
- **Error Handling**: Robust retry logic and failure detection
- **Verification**: Post-action scans to confirm security improvements
- **Audit Trail**: Complete record of all security actions taken
- **Port Restoration**: Ability to restore closed ports if needed

## Vulnerable Ports Monitored

The script monitors these potentially risky ports:

| Port | Service | Risk Level | Description |
|------|---------|------------|-------------|
| 21 | FTP | High | File Transfer Protocol - often unsecured |
| 23 | Telnet | High | Unencrypted remote access |
| 22 | SSH | Medium | Needs proper configuration |
| 80 | HTTP | Medium | Web server vulnerabilities |
| 443 | HTTPS | Medium | SSL/TLS vulnerabilities |
| 445 | SMB | High | Server Message Block exploits |
| 1433 | MSSQL | High | Microsoft SQL Server vulnerabilities |
| 3306 | MySQL | High | MySQL database vulnerabilities |
| 3389 | RDP | High | Remote Desktop Protocol attacks |
| 5432 | PostgreSQL | High | PostgreSQL database vulnerabilities |
| 5900 | VNC | High | VNC remote desktop vulnerabilities |
| 6379 | Redis | High | Redis database vulnerabilities |
| 27017 | MongoDB | High | MongoDB NoSQL vulnerabilities |

## Prerequisites

### System Requirements

1. **Nmap**: Network mapping tool for port scanning
   - **Linux**: `sudo apt-get install nmap`
   - **Windows**: Download from [nmap.org](https://nmap.org/download.html)
   - **macOS**: `brew install nmap`

2. **Administrative Privileges**:
   - **Linux**: `sudo` access for package management
   - **Windows**: Administrator privileges for Windows Update

3. **Python 3.6+**: The script uses standard library only

### Installation

1. Clone or download the script:
   ```bash
   git clone <repository-url>
   cd portscanner
   ```

2. Install Nmap (if not already installed):
   ```bash
   # Linux
   sudo apt-get update && sudo apt-get install nmap
   
   # Windows
   # Download and install from https://nmap.org/download.html
   
   # macOS
   brew install nmap
   ```

3. Make the script executable (Linux/macOS):
   ```bash
   chmod +x port_security_scanner.py
   ```

## Usage

### Basic Usage

```bash
# Run with default settings (scans 127.0.0.1) - Interactive mode
python port_security_scanner.py

# Run in automated mode (applies updates and closes ports automatically)
python port_security_scanner.py --auto
python port_security_scanner.py -a  # Short form

# Run as administrator/root for full functionality
sudo python port_security_scanner.py  # Linux
# Run PowerShell as Administrator on Windows
```

### Testing the Enhanced Functionality

```bash
# Test the enhanced port closing and patch download features
python test_enhanced_functionality.py

# Test basic installation requirements
python test_installation.py

# Test port closing functionality specifically
python test_port_closing.py
```

### What the Script Does

1. **Initial Scan**: Performs a full port scan using Nmap
2. **Vulnerability Assessment**: Identifies open ports that match known vulnerable services
3. **User Interaction**: Prompts for action choice (update/close/both/skip/retry)
4. **Security Actions**: 
   - **Updates**: Downloads and applies security patches from official sources
   - **Port Closure**: Uses multiple methods to close/block vulnerable ports
   - **Combined**: Applies updates AND closes ports for maximum security
5. **Process Management**: Identifies and manages processes using vulnerable ports
6. **Error Handling**: Manages failures with retry options and rollback capabilities
7. **Verification**: Re-scans to confirm security improvements
8. **Final Report**: Provides comprehensive security status

### Example Output

```
Port Security Scanner and Auto-Updater
==================================================
This script will scan for vulnerable ports and apply security updates.
All actions will be logged to port_security.log

============================================================
VULNERABLE PORT DETECTED!
============================================================
Port: 445
Service: SMB
Description: Server Message Block - potential for SMB exploits

This port may pose a security risk.
Choose an action:
1. Apply security updates from official sources (u)
2. Close/block the port using multiple methods (c)
3. Apply updates AND close port (a)
4. Skip this port (s)
5. Retry later (r)
Choose action (u/c/a/s/r): a
```

## Logging

All activities are logged to `port_security.log` with timestamps:

```
2024-01-15 10:30:15,123 - INFO - Starting Nmap scan on 127.0.0.1
2024-01-15 10:30:45,456 - INFO - Found 5 open ports: [21, 22, 80, 443, 3389]
2024-01-15 10:30:45,457 - WARNING - Found 3 potentially vulnerable ports
2024-01-15 10:30:45,458 - INFO - Processing vulnerable port: 21 (FTP)
2024-01-15 10:31:00,789 - INFO - Successfully updated FTP on port 21
2024-01-15 10:31:05,012 - INFO - Port 21 successfully secured
```

## Security Considerations

### User Control
- **No Automatic Updates**: All updates require explicit user consent
- **Transparent Process**: Full logging of all actions taken
- **Rollback Options**: Ability to retry or skip failed updates

### Safety Features
- **Verification Scans**: Confirms security improvements after updates
- **Error Detection**: Identifies and handles update failures
- **Audit Trail**: Complete record for compliance and review

### Best Practices
- Run during maintenance windows
- Review logs before and after execution
- Test in non-production environments first
- Keep backups of critical configurations

## Troubleshooting

### Common Issues

1. **Nmap Not Found**
   ```
   Error: Nmap not found. Please install Nmap first.
   ```
   **Solution**: Install Nmap using your system's package manager

2. **Permission Denied**
   ```
   WARNING: Not running as administrator. Some updates may fail.
   ```
   **Solution**: Run with appropriate privileges (sudo/Administrator)

3. **Update Failures**
   ```
   UPDATE FAILED!
   Error: Package not found
   ```
   **Solution**: The script will prompt for retry/skip options

4. **Network Issues**
   ```
   Error: Internet connectivity issues
   ```
   **Solution**: Check network connection and retry

### Log Analysis

Check `port_security.log` for detailed information:
- Scan results and timing
- User decisions and permissions
- Update success/failure details
- Verification scan results

## Customization

### Adding New Vulnerable Ports

Edit the `vulnerable_ports` dictionary in the script:

```python
self.vulnerable_ports = {
    # Add new ports here
    8080: {"service": "HTTP-Alt", "description": "Alternative HTTP port"},
    8443: {"service": "HTTPS-Alt", "description": "Alternative HTTPS port"},
}
```

### Modifying Package Mappings

Update the `get_package_name_for_port` method for different package names:

```python
port_packages = {
    "linux": {
        21: "vsftpd",  # Change to your preferred FTP server
        # Add more mappings
    }
}
```

## License

This script is provided as-is for educational and security purposes. Use responsibly and in accordance with your organization's security policies.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Disclaimer

This tool is designed for legitimate security testing and system hardening. Users are responsible for:
- Obtaining proper authorization before scanning systems
- Complying with local laws and regulations
- Understanding the impact of security updates
- Maintaining system backups before applying changes

Use at your own risk and ensure you have proper authorization for all security testing activities.
