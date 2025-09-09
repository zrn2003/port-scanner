# 🛡️ Port Security Scanner

A comprehensive full-stack port security scanner with automatic vulnerability detection, patch management, and port closure capabilities.

## 🚀 Quick Start

### Option 1: Full Stack (Recommended)
```bash
python start_app.py
```
- Requires: Python, Node.js, npm, Nmap
- Provides: Web UI + Backend API + Admin privileges

### Option 2: Backend Only
```bash
python start_backend_only.py
```
- Requires: Python, Nmap
- Provides: Backend API + Admin privileges
- Use when Node.js/npm is not available

## 🔐 Admin Privileges

The application automatically handles admin privilege elevation:
- ✅ **Automatic Detection**: Checks admin status after servers start
- ✅ **UAC Elevation**: Requests admin privileges when needed
- ✅ **Full Security**: Enables firewall, service control, and patch management
- ✅ **Seamless Experience**: Works with or without admin privileges

## 🛡️ Features

### Port Security
- **Real-time Scanning**: Nmap-based port detection
- **Vulnerability Assessment**: Risk analysis for common ports
- **Multi-method Closure**: Service stopping, process killing, firewall blocking
- **Port Binding**: Prevents other applications from using vulnerable ports

### Patch Management
- **Official Sources**: Downloads from official repositories
- **Windows Updates**: Full Microsoft Update integration
- **Integrity Verification**: SHA256 hash verification
- **Rollback Support**: Automatic rollback on failed updates

### Firewall Management
- **Windows Firewall**: Comprehensive rule creation
- **PowerShell Integration**: Advanced firewall operations
- **Multi-protocol**: TCP/UDP inbound/outbound blocking
- **Auto-enable**: Automatically enables firewall if disabled

## 🌐 API Endpoints

- `GET /health` - Health check
- `GET /system/status` - System and admin status
- `POST /system/elevate` - Request admin elevation
- `POST /scan/start` - Start port scan
- `POST /action/execute` - Execute security actions
- `POST /rollback` - Rollback failed operations

## 📊 System Requirements

### Required
- **Python 3.8+**
- **Nmap** (Network scanner)

### Optional (for full stack)
- **Node.js 16+** (Frontend development)
- **npm** (Package manager)

## 🔧 Installation

1. **Clone the repository**
2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. **Install Nmap**
   - Windows: Download from https://nmap.org/download.html
   - Linux: `sudo apt-get install nmap`
   - macOS: `brew install nmap`

## 🎯 Usage

### Web Interface
1. Run `python start_app.py`
2. Open http://localhost:5173
3. Configure scan target and options
4. Start scanning and manage vulnerabilities

### API Only
1. Run `python start_backend_only.py`
2. Access API at http://localhost:8000
3. Use API documentation at http://localhost:8000/docs

## 🔐 Security Features

### With Admin Privileges
- ✅ Windows Firewall management
- ✅ Service control operations
- ✅ System-level port blocking
- ✅ Patch installation and updates
- ✅ Process termination
- ✅ Registry modifications

### Without Admin Privileges
- ✅ Port scanning and detection
- ✅ Vulnerability assessment
- ✅ User process control
- ✅ Port binding prevention
- ✅ Basic security operations

## 📝 Logging

All operations are logged with detailed information:
- **Backend Logs**: `backend/port_security.log`
- **Web Interface**: Real-time log viewer
- **System Events**: Windows Event Viewer integration

## 🆘 Troubleshooting

### Common Issues
1. **Port 8000 in use**: Change port in startup script
2. **Admin privileges required**: Run as administrator
3. **Nmap not found**: Install Nmap and add to PATH
4. **Frontend not loading**: Install Node.js and npm

### Getting Help
- Check the logs for detailed error messages
- Verify system requirements
- Ensure proper admin privileges
- Review Windows Event Viewer for system errors

## 🎉 Features Summary

- **🔍 Port Scanning**: Comprehensive vulnerability detection
- **🛡️ Security Actions**: Patch updates and port closure
- **🔐 Admin Management**: Automatic privilege elevation
- **🌐 Web Interface**: Modern React-based UI
- **📊 Real-time Updates**: WebSocket-based live updates
- **🔄 Rollback Support**: Automatic failure recovery
- **📝 Comprehensive Logging**: Full audit trail
- **⚡ High Performance**: Optimized for speed and reliability

**The Port Security Scanner provides enterprise-grade security management with a user-friendly interface and automatic admin privilege handling!** 🚀
