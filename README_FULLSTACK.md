# Port Security Scanner - Full Stack Application

A comprehensive full-stack web application for port security scanning, vulnerability detection, and automated security patching with real-time updates and rollback capabilities.

## 🏗️ Architecture

### Backend (FastAPI + WebSocket)
- **FastAPI REST API** for port scanning and security operations
- **WebSocket** for real-time progress updates and notifications
- **Background tasks** for long-running operations
- **Comprehensive logging** with audit trails
- **Rollback functionality** for failed operations

### Frontend (React + Tailwind CSS)
- **Modern React UI** with real-time updates
- **Tailwind CSS** for responsive design
- **WebSocket integration** for live status updates
- **Progress tracking** for all operations
- **Interactive vulnerability management**

## 🚀 Quick Start

### Prerequisites
- **Python 3.7+**
- **Node.js 16+**
- **Nmap** (Network Mapper)
- **Administrative privileges** (for security operations)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd portscanner
   ```

2. **Run the startup script**
   ```bash
   python start_app.py
   ```

   This will:
   - Check all dependencies
   - Install backend Python packages
   - Install frontend npm packages
   - Start both servers automatically

3. **Access the application**
   - **Frontend UI**: http://localhost:5173
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

## 🎯 Features

### 1. Port Scanning
- **Full port scan** using Nmap
- **Real-time progress** updates via WebSocket
- **Customizable targets** (IP addresses, hostnames)
- **Comprehensive port detection**

### 2. Vulnerability Detection
- **Automated vulnerability identification**
- **Risk level assessment** (High, Medium, Low)
- **Service identification** and description
- **Visual risk indicators**

### 3. Security Actions
- **Update patches** from official sources
- **Close vulnerable ports** using multiple methods
- **Combined security** (update + close)
- **Automated mode** for batch operations

### 4. Real-time Monitoring
- **Live operation tracking**
- **Progress bars** for long-running tasks
- **Status updates** via WebSocket
- **Operation history** and logging

### 5. Rollback & Recovery
- **Automatic rollback** for failed operations
- **Manual retry** options
- **Operation recovery** mechanisms
- **Comprehensive error handling**

### 6. Logging & Audit
- **Real-time log viewer**
- **Operation audit trails**
- **Error tracking** and reporting
- **System status monitoring**

## 🖥️ User Interface

### Dashboard
- **Scan configuration** with target input
- **Automated mode** toggle
- **Real-time connection status**
- **Scan results** with statistics

### Vulnerability Management
- **Interactive vulnerability list**
- **Risk level indicators**
- **Action buttons** for each vulnerability
- **Status tracking** for each port

### Operation Monitoring
- **Active operations** panel
- **Progress tracking** with visual indicators
- **Rollback options** for failed operations
- **Real-time status updates**

### Log Viewer
- **System logs** in real-time
- **Color-coded** log levels
- **Searchable** log history
- **Export capabilities**

## 🔧 API Endpoints

### Scan Operations
- `POST /scan/start` - Start a new port scan
- `GET /scan/status/{operation_id}` - Get scan status
- `GET /operations` - List all operations

### Security Actions
- `POST /action/execute` - Execute security action
- `GET /action/status/{operation_id}` - Get action status
- `POST /rollback` - Rollback failed operation

### System Information
- `GET /health` - Health check
- `GET /logs` - Get system logs
- `DELETE /operations/{operation_id}` - Delete operation

### WebSocket
- `WS /ws` - Real-time updates and notifications

## 🛡️ Security Features

### Port Closure Methods
- **Service stopping** (systemctl, sc)
- **Process termination** (kill, taskkill)
- **Firewall blocking** (iptables, Windows Firewall)
- **Multiple fallback** methods

### Patch Management
- **Official sources only** (Ubuntu, Debian, Microsoft)
- **Integrity verification** (SHA256 hashing)
- **Secure downloads** (HTTPS)
- **Cache management**

### Access Control
- **Administrative privileges** required
- **User consent** for all operations
- **Audit logging** for compliance
- **Rollback capabilities**

## 📊 Monitoring & Logging

### Real-time Updates
- **WebSocket connections** for live updates
- **Progress tracking** for all operations
- **Status notifications** via toast messages
- **Connection monitoring**

### Comprehensive Logging
- **Operation logs** with timestamps
- **Error tracking** and reporting
- **Audit trails** for compliance
- **System status** monitoring

### Performance Metrics
- **Scan duration** tracking
- **Operation success rates**
- **Error frequency** monitoring
- **Resource usage** tracking

## 🔄 Workflow

### 1. Initial Scan
```
User Input → Backend API → Nmap Scan → Vulnerability Detection → Frontend Display
```

### 2. Security Action
```
User Action → Backend Processing → Official Patch Download → Port Closure → Verification → Status Update
```

### 3. Real-time Updates
```
Backend Operation → WebSocket Broadcast → Frontend Update → User Notification
```

### 4. Rollback Process
```
Failed Operation → Rollback Trigger → Previous State Restoration → Retry Option
```

## 🚨 Error Handling

### Automatic Recovery
- **Connection retry** for WebSocket
- **Operation retry** for failed actions
- **Rollback mechanisms** for failed updates
- **Graceful degradation** for partial failures

### User Notifications
- **Toast notifications** for all events
- **Error messages** with actionable advice
- **Success confirmations** for completed operations
- **Warning alerts** for potential issues

### Logging & Debugging
- **Comprehensive error logging**
- **Stack trace capture**
- **Operation context** preservation
- **Debug information** for troubleshooting

## 🔧 Configuration

### Backend Configuration
- **API port**: 8000 (configurable)
- **WebSocket port**: 8000 (same as API)
- **Log level**: INFO (configurable)
- **Operation timeout**: 300 seconds

### Frontend Configuration
- **Development port**: 5173 (Vite default)
- **API endpoint**: http://localhost:8000
- **WebSocket endpoint**: ws://localhost:8000/ws
- **Update interval**: Real-time via WebSocket

## 📱 Browser Compatibility

- **Chrome** 90+
- **Firefox** 88+
- **Safari** 14+
- **Edge** 90+

## 🔒 Security Considerations

### Network Security
- **Local network** scanning only
- **Administrative privileges** required
- **Secure WebSocket** connections
- **Input validation** for all endpoints

### Data Protection
- **No sensitive data** storage
- **Temporary operation** data only
- **Secure logging** practices
- **Audit trail** maintenance

### Access Control
- **Local access** only
- **Administrative privileges** required
- **User consent** for all operations
- **Operation logging** for accountability

## 🚀 Deployment

### Development
```bash
python start_app.py
```

### Production
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run build
npm run preview
```

## 📈 Performance

### Backend Performance
- **Async operations** for non-blocking I/O
- **Background tasks** for long operations
- **Connection pooling** for database operations
- **Caching** for frequently accessed data

### Frontend Performance
- **Real-time updates** via WebSocket
- **Optimized rendering** with React
- **Lazy loading** for large datasets
- **Efficient state management**

## 🐛 Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check if backend is running on port 8000
   - Verify firewall settings
   - Check browser console for errors

2. **Nmap Not Found**
   - Install Nmap: `sudo apt-get install nmap` (Linux)
   - Download from: https://nmap.org/download.html (Windows)

3. **Permission Denied**
   - Run with administrative privileges
   - Check sudo access (Linux)
   - Run as Administrator (Windows)

4. **Port Already in Use**
   - Change port in configuration
   - Kill existing processes
   - Check for conflicting services

### Debug Mode
```bash
# Backend with debug logging
cd backend
uvicorn app:app --reload --log-level debug

# Frontend with verbose output
cd frontend
npm run dev -- --verbose
```

## 📚 Documentation

- **API Documentation**: http://localhost:8000/docs
- **Backend Code**: `/backend/`
- **Frontend Code**: `/frontend/`
- **Configuration**: See individual README files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is designed for legitimate security testing and system hardening. Users are responsible for:
- Obtaining proper authorization before scanning systems
- Complying with local laws and regulations
- Understanding the impact of security updates
- Maintaining system backups before applying changes

Use at your own risk and ensure you have proper authorization for all security testing activities.

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2024
