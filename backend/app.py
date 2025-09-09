#!/usr/bin/env python3
"""
Port Security Scanner Backend API
FastAPI-based REST API with WebSocket support for real-time updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import asyncio
import json
import uuid
import threading
import time
import subprocess
from datetime import datetime
import logging
import os
import sys

# Add the current directory to Python path to import the scanner
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from port_security_scanner import PortSecurityScanner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Port Security Scanner API", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for managing connections and operations
active_connections: List[WebSocket] = []
active_operations: Dict[str, Dict] = {}
scanner_instance = None

# Pydantic models for API requests/responses
class ScanRequest(BaseModel):
    target: str = "127.0.0.1"
    automated_mode: bool = False

class ActionRequest(BaseModel):
    port: int
    service: str
    action: str  # 'update', 'close', 'auto', 'skip'
    operation_id: str

class RollbackRequest(BaseModel):
    operation_id: str
    port: int

class OperationStatus(BaseModel):
    operation_id: str
    status: str  # 'running', 'completed', 'failed', 'cancelled'
    progress: int  # 0-100
    message: str
    details: Optional[Dict] = None
    timestamp: str

class VulnerabilityInfo(BaseModel):
    port: int
    service: str
    description: str
    risk_level: str
    status: str = "detected"  # detected, updating, closed, secured, failed

class ScanResult(BaseModel):
    scan_id: str
    target: str
    open_ports: List[int]
    vulnerable_ports: List[VulnerabilityInfo]
    scan_status: str
    timestamp: str
    total_ports: int
    vulnerable_count: int

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# Initialize scanner instance
def get_scanner():
    global scanner_instance
    if scanner_instance is None:
        scanner_instance = PortSecurityScanner()
    return scanner_instance

# Background task for port scanning
async def run_port_scan(operation_id: str, target: str, automated_mode: bool = False):
    """Run port scan in background and send updates via WebSocket"""
    try:
        scanner = get_scanner()
        
        # Update operation status
        active_operations[operation_id] = {
            "status": "running",
            "progress": 0,
            "message": "Starting port scan...",
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "automated_mode": automated_mode
        }
        
        await manager.broadcast(json.dumps({
            "type": "scan_update",
            "operation_id": operation_id,
            "status": "running",
            "progress": 0,
            "message": "Starting port scan...",
            "timestamp": datetime.now().isoformat()
        }))
        
        # Run Nmap scan
        await manager.broadcast(json.dumps({
            "type": "scan_update",
            "operation_id": operation_id,
            "status": "running",
            "progress": 25,
            "message": f"Scanning {target} with Nmap...",
            "timestamp": datetime.now().isoformat()
        }))
        
        open_ports = scanner.run_nmap_scan(target)
        
        if not open_ports:
            active_operations[operation_id]["status"] = "failed"
            active_operations[operation_id]["message"] = "No open ports found or scan failed"
            await manager.broadcast(json.dumps({
                "type": "scan_complete",
                "operation_id": operation_id,
                "status": "failed",
                "message": "No open ports found or scan failed",
                "timestamp": datetime.now().isoformat()
            }))
            return
        
        await manager.broadcast(json.dumps({
            "type": "scan_update",
            "operation_id": operation_id,
            "status": "running",
            "progress": 50,
            "message": f"Found {len(open_ports)} open ports. Analyzing vulnerabilities...",
            "timestamp": datetime.now().isoformat()
        }))
        
        # Identify vulnerable ports
        vulnerable_ports = scanner.identify_vulnerable_ports(open_ports)
        
        # Convert to VulnerabilityInfo objects
        vuln_info = []
        for vuln in vulnerable_ports:
            risk_level = "High" if vuln["port"] in [21, 23, 445, 3389, 1433, 3306, 5432, 5900, 6379, 27017] else "Medium"
            vuln_info.append(VulnerabilityInfo(
                port=vuln["port"],
                service=vuln["service"],
                description=vuln["description"],
                risk_level=risk_level,
                status="detected"
            ))
        
        # Create scan result
        scan_result = ScanResult(
            scan_id=operation_id,
            target=target,
            open_ports=open_ports,
            vulnerable_ports=vuln_info,
            scan_status="completed",
            timestamp=datetime.now().isoformat(),
            total_ports=len(open_ports),
            vulnerable_count=len(vuln_info)
        )
        
        # Update operation status
        active_operations[operation_id].update({
            "status": "completed",
            "progress": 100,
            "message": f"Scan completed. Found {len(vuln_info)} vulnerable ports.",
            "scan_result": scan_result.model_dump()
        })
        
        await manager.broadcast(json.dumps({
            "type": "scan_complete",
            "operation_id": operation_id,
            "status": "completed",
            "progress": 100,
            "message": f"Scan completed. Found {len(vuln_info)} vulnerable ports.",
            "scan_result": scan_result.model_dump(),
            "timestamp": datetime.now().isoformat()
        }))
        
    except Exception as e:
        logger.error(f"Error in port scan: {str(e)}")
        active_operations[operation_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"Scan failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        
        await manager.broadcast(json.dumps({
            "type": "scan_complete",
            "operation_id": operation_id,
            "status": "failed",
            "message": f"Scan failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }))

# Background task for security actions
async def run_security_action(operation_id: str, port: int, service: str, action: str):
    """Run security action (update/close) in background"""
    try:
        scanner = get_scanner()
        
        # Update operation status
        active_operations[operation_id] = {
            "status": "running",
            "progress": 0,
            "message": f"Starting {action} for port {port}...",
            "timestamp": datetime.now().isoformat(),
            "port": port,
            "service": service,
            "action": action
        }
        
        await manager.broadcast(json.dumps({
            "type": "action_update",
            "operation_id": operation_id,
            "status": "running",
            "progress": 0,
            "message": f"Starting {action} for port {port}...",
            "timestamp": datetime.now().isoformat()
        }))
        
        success = False
        message = ""
        
        if action == "update":
            await manager.broadcast(json.dumps({
                "type": "action_update",
                "operation_id": operation_id,
                "status": "running",
                "progress": 30,
                "message": "Downloading patches from official sources...",
                "timestamp": datetime.now().isoformat()
            }))
            
            success, message = scanner.apply_security_update(port, service)
            
        elif action == "close":
            await manager.broadcast(json.dumps({
                "type": "action_update",
                "operation_id": operation_id,
                "status": "running",
                "progress": 30,
                "message": "Closing port using multiple methods...",
                "timestamp": datetime.now().isoformat()
            }))
            
            success, message = scanner.close_vulnerable_port(port, service)
            
        elif action == "auto":
            await manager.broadcast(json.dumps({
                "type": "action_update",
                "operation_id": operation_id,
                "status": "running",
                "progress": 20,
                "message": "Applying updates and closing port...",
                "timestamp": datetime.now().isoformat()
            }))
            
            # Try update first
            update_success, update_msg = scanner.apply_security_update(port, service)
            
            await manager.broadcast(json.dumps({
                "type": "action_update",
                "operation_id": operation_id,
                "status": "running",
                "progress": 60,
                "message": "Closing port...",
                "timestamp": datetime.now().isoformat()
            }))
            
            # Then try to close port
            close_success, close_msg = scanner.close_vulnerable_port(port, service)
            
            success = update_success or close_success
            message = f"Update: {update_msg}, Close: {close_msg}"
        
        # Update final status
        final_status = "completed" if success else "failed"
        progress = 100 if success else 0
        
        active_operations[operation_id].update({
            "status": final_status,
            "progress": progress,
            "message": message,
            "success": success
        })
        
        await manager.broadcast(json.dumps({
            "type": "action_complete",
            "operation_id": operation_id,
            "status": final_status,
            "progress": progress,
            "message": message,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }))
        
    except Exception as e:
        logger.error(f"Error in security action: {str(e)}")
        active_operations[operation_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"Action failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        
        await manager.broadcast(json.dumps({
            "type": "action_complete",
            "operation_id": operation_id,
            "status": "failed",
            "message": f"Action failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }))

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Port Security Scanner API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/system/status")
async def system_status():
    """Get system status including admin privileges and firewall status"""
    try:
        scanner = PortSecurityScanner()
        
        status = {
            "admin_privileges": scanner.is_admin,
            "operating_system": scanner.os_type,
            "firewall_enabled": False,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check firewall status on Windows
        if scanner.os_type == "windows":
            try:
                firewall_cmd = ["netsh", "advfirewall", "show", "allprofiles", "state"]
                result = subprocess.run(firewall_cmd, capture_output=True, text=True)
                status["firewall_enabled"] = "ON" in result.stdout and "OFF" not in result.stdout
            except Exception as e:
                status["firewall_error"] = str(e)
        
        return status
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@app.post("/scan/start")
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """Start a new port scan"""
    operation_id = str(uuid.uuid4())
    
    # Start background task
    background_tasks.add_task(run_port_scan, operation_id, request.target, request.automated_mode)
    
    return {
        "operation_id": operation_id,
        "status": "started",
        "message": "Port scan started",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/scan/status/{operation_id}")
async def get_scan_status(operation_id: str):
    """Get status of a scan operation"""
    if operation_id not in active_operations:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    return active_operations[operation_id]

@app.post("/action/execute")
async def execute_action(request: ActionRequest, background_tasks: BackgroundTasks):
    """Execute a security action on a vulnerable port"""
    operation_id = str(uuid.uuid4())
    
    # Start background task
    background_tasks.add_task(run_security_action, operation_id, request.port, request.service, request.action)
    
    return {
        "operation_id": operation_id,
        "status": "started",
        "message": f"Security action '{request.action}' started for port {request.port}",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/action/status/{operation_id}")
async def get_action_status(operation_id: str):
    """Get status of a security action"""
    if operation_id not in active_operations:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    return active_operations[operation_id]

@app.post("/rollback")
async def rollback_operation(request: RollbackRequest, background_tasks: BackgroundTasks):
    """Rollback a failed operation"""
    if request.operation_id not in active_operations:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    operation = active_operations[request.operation_id]
    
    if operation["status"] != "failed":
        raise HTTPException(status_code=400, detail="Can only rollback failed operations")
    
    # Create new operation for rollback
    rollback_id = str(uuid.uuid4())
    
    # Start rollback task
    background_tasks.add_task(run_security_action, rollback_id, request.port, operation.get("service", ""), "auto")
    
    return {
        "rollback_id": rollback_id,
        "status": "started",
        "message": f"Rollback started for port {request.port}",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/logs")
async def get_logs():
    """Get recent log entries"""
    try:
        scanner = get_scanner()
        log_file = scanner.log_file
        
        if not os.path.exists(log_file):
            return {"logs": [], "message": "No logs found"}
        
        # Read last 100 lines
        with open(log_file, 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-100:] if len(lines) > 100 else lines
        
        logs = []
        for line in recent_lines:
            if line.strip():
                # Parse log format: timestamp - level - message
                parts = line.split(' - ', 2)
                if len(parts) >= 3:
                    logs.append({
                        "timestamp": parts[0],
                        "level": parts[1],
                        "message": parts[2].strip()
                    })
        
        return {"logs": logs, "count": len(logs)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading logs: {str(e)}")

@app.get("/operations")
async def get_all_operations():
    """Get all active and recent operations"""
    return {"operations": active_operations}

@app.delete("/operations/{operation_id}")
async def delete_operation(operation_id: str):
    """Delete an operation from memory"""
    if operation_id in active_operations:
        del active_operations[operation_id]
        return {"message": "Operation deleted"}
    else:
        raise HTTPException(status_code=404, detail="Operation not found")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await manager.send_personal_message(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
