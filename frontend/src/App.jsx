import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Shield, 
  Search, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Download, 
  Lock, 
  Activity,
  Server,
  Clock,
  LogOut
} from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';
let ws = null;

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [scanTarget, setScanTarget] = useState('127.0.0.1');
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [activeOperations, setActiveOperations] = useState({});
  const [logs, setLogs] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [automatedMode, setAutomatedMode] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    connectWebSocket();
    fetchSystemStatus();
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/system/status');
      setSystemStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  const connectWebSocket = () => {
    ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      setWsConnected(true);
      toast.success('Connected to server');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };
    
    ws.onclose = () => {
      setWsConnected(false);
      toast.error('Disconnected from server');
      setTimeout(connectWebSocket, 3000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      toast.error('WebSocket connection error');
    };
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'scan_update':
        setActiveOperations(prev => ({
          ...prev,
          [data.operation_id]: {
            ...prev[data.operation_id],
            status: data.status,
            progress: data.progress,
            message: data.message
          }
        }));
        break;
        
      case 'scan_complete':
        setActiveOperations(prev => ({
          ...prev,
          [data.operation_id]: {
            ...prev[data.operation_id],
            status: data.status,
            progress: data.progress,
            message: data.message,
            scan_result: data.scan_result
          }
        }));
        
        if (data.status === 'completed' && data.scan_result) {
          setScanResult(data.scan_result);
          setVulnerabilities(data.scan_result.vulnerable_ports);
          setIsScanning(false);
          toast.success(`Scan completed! Found ${data.scan_result.vulnerable_count} vulnerabilities`);
        } else if (data.status === 'failed') {
          setIsScanning(false);
          toast.error(`Scan failed: ${data.message}`);
        }
        break;
        
      case 'action_update':
        setActiveOperations(prev => ({
          ...prev,
          [data.operation_id]: {
            ...prev[data.operation_id],
            status: data.status,
            progress: data.progress,
            message: data.message
          }
        }));
        break;
        
      case 'action_complete':
        setActiveOperations(prev => ({
          ...prev,
          [data.operation_id]: {
            ...prev[data.operation_id],
            status: data.status,
            progress: data.progress,
            message: data.message,
            success: data.success
          }
        }));
        
        if (data.status === 'completed') {
          toast.success(`Action completed: ${data.message}`);
          setVulnerabilities(prev => 
            prev.map(vuln => 
              vuln.port === data.port ? { ...vuln, status: 'secured' } : vuln
            )
          );
        } else if (data.status === 'failed') {
          toast.error(`Action failed: ${data.message}`);
        }
        break;
    }
  };

  const startScan = async () => {
    try {
      setIsScanning(true);
      setScanResult(null);
      setVulnerabilities([]);
      
      const response = await axios.post(`${API_BASE_URL}/scan/start`, {
        target: scanTarget,
        automated_mode: automatedMode
      });
      
      const operationId = response.data.operation_id;
      setActiveOperations(prev => ({
        ...prev,
        [operationId]: {
          status: 'running',
          progress: 0,
          message: 'Starting scan...',
          type: 'scan'
        }
      }));
      
      toast.success('Port scan started');
    } catch (error) {
      setIsScanning(false);
      toast.error(`Failed to start scan: ${error.response?.data?.detail || error.message}`);
    }
  };

  const executeAction = async (port, service, action) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/action/execute`, {
        port,
        service,
        action,
        operation_id: ''
      });
      
      const operationId = response.data.operation_id;
      setActiveOperations(prev => ({
        ...prev,
        [operationId]: {
          status: 'running',
          progress: 0,
          message: `Starting ${action}...`,
          type: 'action',
          port,
          service,
          action
        }
      }));
      
      setVulnerabilities(prev => 
        prev.map(vuln => 
          vuln.port === port ? { ...vuln, status: 'updating' } : vuln
        )
      );
      
      toast.success(`${action} started for port ${port}`);
    } catch (error) {
      toast.error(`Failed to execute action: ${error.response?.data?.detail || error.message}`);
    }
  };

  const rollbackOperation = async (operationId, port) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/rollback`, {
        operation_id: operationId,
        port
      });
      
      const rollbackId = response.data.rollback_id;
      setActiveOperations(prev => ({
        ...prev,
        [rollbackId]: {
          status: 'running',
          progress: 0,
          message: 'Starting rollback...',
          type: 'rollback',
          port
        }
      }));
      
      toast.success('Rollback started');
    } catch (error) {
      toast.error(`Failed to rollback: ${error.response?.data?.detail || error.message}`);
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/logs`);
      setLogs(response.data.logs);
    } catch (error) {
      toast.error(`Failed to fetch logs: ${error.response?.data?.detail || error.message}`);
    }
  };

  const StatusBadge = ({ status }) => {
    const statusConfig = {
      running: { color: 'status-running', icon: Activity, text: 'Running' },
      completed: { color: 'status-completed', icon: CheckCircle, text: 'Completed' },
      failed: { color: 'status-failed', icon: XCircle, text: 'Failed' },
      detected: { color: 'status-detected', icon: AlertTriangle, text: 'Detected' },
      secured: { color: 'status-secured', icon: Shield, text: 'Secured' },
      updating: { color: 'status-running', icon: Download, text: 'Updating' }
    };
    
    const config = statusConfig[status] || statusConfig.detected;
    const Icon = config.icon;
    
    return (
      <span className={`status-badge ${config.color}`}>
        <Icon className="w-3 h-3 mr-1" />
        {config.text}
      </span>
    );
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'High': return 'text-danger-600 bg-danger-50 border-danger-200';
      case 'Medium': return 'text-warning-600 bg-warning-50 border-warning-200';
      case 'Low': return 'text-success-600 bg-success-50 border-success-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-primary-600 mr-3" />
              <h1 className="text-xl font-semibold text-gray-900">Port Security Scanner</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-success-500' : 'bg-danger-500'}`} />
                <span className="text-sm text-gray-600">
                  {wsConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              
              <button
                onClick={() => setCurrentView('logs')}
                className="btn-secondary"
              >
                <LogOut className="w-4 h-4 mr-2" />
                View Logs
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'dashboard' && (
          <div className="space-y-8">
            {/* System Status Card */}
            {systemStatus && (
              <div className="card">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                    <Shield className="w-5 h-5 mr-2" />
                    System Status
                  </h2>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${systemStatus.admin_privileges ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Admin Privileges</p>
                      <p className="text-xs text-gray-500">
                        {systemStatus.admin_privileges ? 'Available' : 'Required for firewall operations'}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${systemStatus.firewall_enabled ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Windows Firewall</p>
                      <p className="text-xs text-gray-500">
                        {systemStatus.firewall_enabled ? 'Enabled' : 'Disabled - Will be enabled automatically'}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Operating System</p>
                      <p className="text-xs text-gray-500 capitalize">{systemStatus.operating_system}</p>
                    </div>
                  </div>
                </div>
                
                {!systemStatus.admin_privileges && (
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-800">
                      <strong>Note:</strong> Administrator privileges are required for firewall operations. 
                      Please run the application as administrator for full functionality.
                    </p>
                  </div>
                )}
              </div>
            )}
            
            <div className="card">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Search className="w-5 h-5 mr-2" />
                  Port Scan Configuration
                </h2>
                <StatusBadge status={isScanning ? 'running' : 'completed'} />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target IP/Hostname
                  </label>
                  <input
                    type="text"
                    value={scanTarget}
                    onChange={(e) => setScanTarget(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="127.0.0.1"
                  />
                </div>
                
                <div className="flex items-end">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={automatedMode}
                      onChange={(e) => setAutomatedMode(e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Automated Mode</span>
                  </label>
                </div>
                
                <div className="flex items-end">
                  <button
                    onClick={startScan}
                    disabled={isScanning}
                    className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isScanning ? (
                      <>
                        <Activity className="w-4 h-4 mr-2 animate-spin" />
                        Scanning...
                      </>
                    ) : (
                      <>
                        <Search className="w-4 h-4 mr-2" />
                        Start Scan
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {scanResult && (
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Server className="w-5 h-5 mr-2" />
                  Scan Results
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{scanResult.total_ports}</div>
                    <div className="text-sm text-blue-600">Total Open Ports</div>
                  </div>
                  <div className="bg-warning-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-warning-600">{scanResult.vulnerable_count}</div>
                    <div className="text-sm text-warning-600">Vulnerable Ports</div>
                  </div>
                  <div className="bg-success-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-success-600">
                      {scanResult.total_ports - scanResult.vulnerable_count}
                    </div>
                    <div className="text-sm text-success-600">Secure Ports</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-gray-600">{scanResult.target}</div>
                    <div className="text-sm text-gray-600">Target</div>
                  </div>
                </div>
              </div>
            )}

            {vulnerabilities.length > 0 && (
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <AlertTriangle className="w-5 h-5 mr-2" />
                  Vulnerable Ports
                </h2>
                
                <div className="space-y-4">
                  {vulnerabilities.map((vuln, index) => (
                    <motion.div
                      key={vuln.port}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-4 mb-2">
                            <span className="font-mono text-lg font-semibold text-gray-900">
                              Port {vuln.port}
                            </span>
                            <span className="text-sm text-gray-600">{vuln.service}</span>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getRiskColor(vuln.risk_level)}`}>
                              {vuln.risk_level} Risk
                            </span>
                            <StatusBadge status={vuln.status} />
                          </div>
                          <p className="text-sm text-gray-600">{vuln.description}</p>
                        </div>
                        
                        <div className="flex space-x-2">
                          {vuln.status === 'detected' && (
                            <>
                              <button
                                onClick={() => executeAction(vuln.port, vuln.service, 'update')}
                                className="btn-primary text-sm"
                              >
                                <Download className="w-4 h-4 mr-1" />
                                Update
                              </button>
                              <button
                                onClick={() => executeAction(vuln.port, vuln.service, 'close')}
                                className="btn-danger text-sm"
                              >
                                <Lock className="w-4 h-4 mr-1" />
                                Close
                              </button>
                              <button
                                onClick={() => executeAction(vuln.port, vuln.service, 'auto')}
                                className="btn-success text-sm"
                              >
                                <Shield className="w-4 h-4 mr-1" />
                                Secure
                              </button>
                            </>
                          )}
                          
                          {vuln.status === 'failed' && (
                            <button
                              onClick={() => rollbackOperation('', vuln.port)}
                              className="btn-secondary text-sm"
                            >
                              <Download className="w-4 h-4 mr-1" />
                              Rollback
                            </button>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {Object.keys(activeOperations).length > 0 && (
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Active Operations
                </h2>
                
                <div className="space-y-4">
                  {Object.entries(activeOperations).map(([operationId, operation]) => (
                    <div key={operationId} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-sm text-gray-600">{operationId.slice(0, 8)}...</span>
                          <StatusBadge status={operation.status} />
                        </div>
                        <span className="text-sm text-gray-500">
                          {new Date(operation.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      
                      <p className="text-sm text-gray-700 mb-3">{operation.message}</p>
                      
                      {operation.status === 'running' && (
                        <div className="progress-bar">
                          <div 
                            className="progress-fill" 
                            style={{ width: `${operation.progress}%` }}
                          />
                        </div>
                      )}
                      
                      {operation.status === 'failed' && operation.type === 'action' && (
                        <button
                          onClick={() => rollbackOperation(operationId, operation.port)}
                          className="btn-secondary text-sm mt-2"
                        >
                          <Download className="w-4 h-4 mr-1" />
                          Rollback & Retry
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {currentView === 'logs' && (
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                <Clock className="w-5 h-5 mr-2" />
                System Logs
              </h2>
              <button
                onClick={fetchLogs}
                className="btn-secondary"
              >
                Refresh Logs
              </button>
            </div>
            
            <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm max-h-96 overflow-y-auto">
              {logs.length === 0 ? (
                <div className="text-gray-500">No logs available</div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="mb-1">
                    <span className="text-gray-400">[{log.timestamp}]</span>
                    <span className={`ml-2 ${
                      log.level === 'ERROR' ? 'text-red-400' :
                      log.level === 'WARNING' ? 'text-yellow-400' :
                      log.level === 'INFO' ? 'text-blue-400' :
                      'text-gray-400'
                    }`}>
                      {log.level}
                    </span>
                    <span className="ml-2">{log.message}</span>
                  </div>
                ))
              )}
            </div>
            
            <div className="mt-4">
              <button
                onClick={() => setCurrentView('dashboard')}
                className="btn-primary"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
