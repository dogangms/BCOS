"""
Decentralized AI Node Operating System - Step 5: Web-Based GUI Dashboard
Modern web interface for real-time system monitoring and management.
"""

import http.server
import socketserver
import json
import threading
import time
import webbrowser
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

# Import existing components
try:
    from file_system import VirtualFileSystem
    from file_encryption import FileEncryption
    from ai_scheduler import AIScheduler
except ImportError:
    # Fallback for standalone usage
    VirtualFileSystem = None
    FileEncryption = None
    AIScheduler = None

class WebGUIServer:
    """
    Web-based GUI Server for the Decentralized AI Node OS
    Provides real-time dashboard with interactive system monitoring
    """
    
    def __init__(self, file_system=None, encryption=None, ai_scheduler=None, port=8080):
        self.file_system = file_system
        self.encryption = encryption
        self.ai_scheduler = ai_scheduler
        self.port = port
        self.server = None
        self.running = False
        
        # System data for GUI
        self.system_data = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_activity": 0.0,
            "process_count": 0,
            "uptime": 0
        }
        
        self.start_time = time.time()
        
    def start_server(self):
        """Start the web GUI server"""
        if self.running:
            return
            
        self.running = True
        
        # Create custom handler
        handler = self._create_request_handler()
        
        # Start server in thread
        server_thread = threading.Thread(target=self._run_server, args=(handler,), daemon=True)
        server_thread.start()
        
        print(f"🌐 Web GUI Server started at http://localhost:{self.port}")
        print("📊 Dashboard available with real-time system monitoring")
        
        # Open browser automatically
        try:
            webbrowser.open(f"http://localhost:{self.port}")
        except:
            pass  # Browser opening failed, user can manually navigate
            
    def stop_server(self):
        """Stop the web GUI server"""
        self.running = False
        if self.server:
            self.server.shutdown()
            
    def _run_server(self, handler):
        """Run the HTTP server"""
        try:
            with socketserver.TCPServer(("", self.port), handler) as httpd:
                self.server = httpd
                print(f"✅ Server listening on port {self.port}")
                while self.running:
                    httpd.handle_request()
        except Exception as e:
            print(f"❌ Server error: {e}")
            
    def _create_request_handler(self):
        """Create custom HTTP request handler"""
        gui_server = self
        
        class GUIRequestHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                parsed_path = urlparse(self.path)
                
                if parsed_path.path == '/':
                    self._serve_dashboard()
                elif parsed_path.path == '/api/system':
                    self._serve_system_data()
                elif parsed_path.path == '/api/files':
                    self._serve_file_data()
                elif parsed_path.path == '/api/scheduler':
                    self._serve_scheduler_data()
                elif parsed_path.path == '/api/security':
                    self._serve_security_data()
                elif parsed_path.path.startswith('/static/'):
                    self._serve_static_file()
                else:
                    self.send_error(404)
                    
            def _serve_dashboard(self):
                """Serve the main dashboard HTML"""
                html_content = gui_server._generate_dashboard_html()
                self._send_html_response(html_content)
                
            def _serve_system_data(self):
                """Serve system metrics as JSON"""
                data = gui_server._get_system_metrics()
                self._send_json_response(data)
                
            def _serve_file_data(self):
                """Serve file system data as JSON"""
                data = gui_server._get_file_system_data()
                self._send_json_response(data)
                
            def _serve_scheduler_data(self):
                """Serve AI scheduler data as JSON"""
                data = gui_server._get_scheduler_data()
                self._send_json_response(data)
                
            def _serve_security_data(self):
                """Serve security data as JSON"""
                data = gui_server._get_security_data()
                self._send_json_response(data)
                
            def _serve_static_file(self):
                """Serve static files (CSS, JS)"""
                if self.path.endswith('.css'):
                    css_content = gui_server._generate_css()
                    self.send_response(200)
                    self.send_header('Content-type', 'text/css')
                    self.end_headers()
                    self.wfile.write(css_content.encode())
                elif self.path.endswith('.js'):
                    js_content = gui_server._generate_javascript()
                    self.send_response(200)
                    self.send_header('Content-type', 'application/javascript')
                    self.end_headers()
                    self.wfile.write(js_content.encode())
                else:
                    self.send_error(404)
                    
            def _send_html_response(self, content):
                """Send HTML response"""
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content.encode())
                
            def _send_json_response(self, data):
                """Send JSON response"""
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
                
            def log_message(self, format, *args):
                """Suppress default logging"""
                pass
                
        return GUIRequestHandler
        
    def _generate_dashboard_html(self) -> str:
        """Generate the main dashboard HTML"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌟 Decentralized AI Node OS - Dashboard</title>
    <link rel="stylesheet" href="/static/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="dashboard">
        <!-- Header -->
        <header class="header">
            <h1>🌟 Decentralized AI Node Operating System</h1>
            <div class="status-indicators">
                <span class="status online">🟢 ONLINE</span>
                <span class="uptime">⏱️ Uptime: <span id="uptime">00:00:00</span></span>
            </div>
        </header>

        <!-- Main Content -->
        <main class="main-content">
            <!-- System Overview -->
            <section class="section">
                <h2>📊 System Overview</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>💻 CPU Usage</h3>
                        <div class="progress-ring" id="cpu-ring">
                            <canvas width="100" height="100"></canvas>
                            <span class="percentage" id="cpu-percent">0%</span>
                        </div>
                    </div>
                    <div class="metric-card">
                        <h3>🧠 Memory Usage</h3>
                        <div class="progress-ring" id="memory-ring">
                            <canvas width="100" height="100"></canvas>
                            <span class="percentage" id="memory-percent">0%</span>
                        </div>
                    </div>
                    <div class="metric-card">
                        <h3>💾 Disk Usage</h3>
                        <div class="progress-ring" id="disk-ring">
                            <canvas width="100" height="100"></canvas>
                            <span class="percentage" id="disk-percent">0%</span>
                        </div>
                    </div>
                    <div class="metric-card">
                        <h3>🌐 Network</h3>
                        <div class="progress-ring" id="network-ring">
                            <canvas width="100" height="100"></canvas>
                            <span class="percentage" id="network-percent">0%</span>
                        </div>
                    </div>
                </div>
            </section>

            <!-- AI Scheduler Section -->
            <section class="section">
                <h2>🤖 AI Scheduler Intelligence</h2>
                <div class="scheduler-grid">
                    <div class="scheduler-card">
                        <h3>📈 Performance Metrics</h3>
                        <canvas id="performance-chart" width="400" height="200"></canvas>
                    </div>
                    <div class="scheduler-card">
                        <h3>🧠 Learning Status</h3>
                        <div class="learning-info">
                            <p><strong>Mode:</strong> <span id="learning-mode">Balanced</span></p>
                            <p><strong>Accuracy:</strong> <span id="prediction-accuracy">0%</span></p>
                            <p><strong>Adaptations:</strong> <span id="adaptations">0</span></p>
                            <p><strong>Processes:</strong> <span id="total-scheduled">0</span></p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- File System Section -->
            <section class="section">
                <h2>📁 File System Monitor</h2>
                <div class="filesystem-grid">
                    <div class="filesystem-card">
                        <h3>📊 Storage Analytics</h3>
                        <canvas id="storage-chart" width="300" height="300"></canvas>
                    </div>
                    <div class="filesystem-card">
                        <h3>🔒 Security Status</h3>
                        <div class="security-info">
                            <p><strong>Encrypted Files:</strong> <span id="encrypted-files">0</span></p>
                            <p><strong>Active Keys:</strong> <span id="active-keys">0</span></p>
                            <p><strong>Success Rate:</strong> <span id="security-success">0%</span></p>
                            <p><strong>Blocked Users:</strong> <span id="blocked-users">0</span></p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Process Monitor -->
            <section class="section">
                <h2>⚙️ Process Monitor</h2>
                <div class="process-table-container">
                    <table class="process-table">
                        <thead>
                            <tr>
                                <th>Process ID</th>
                                <th>Type</th>
                                <th>CPU Core</th>
                                <th>Priority</th>
                                <th>Power Mode</th>
                                <th>Runtime</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="process-table-body">
                            <!-- Processes will be populated here -->
                        </tbody>
                    </table>
                </div>
            </section>
        </main>
    </div>

    <script src="/static/dashboard.js"></script>
</body>
</html>'''

    def _generate_css(self) -> str:
        """Generate CSS styles for the dashboard"""
        return '''/* Decentralized AI Node OS - Dashboard Styles */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: #ffffff;
    min-height: 100vh;
}

.dashboard {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* Header */
.header {
    background: rgba(0, 0, 0, 0.3);
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.header h1 {
    font-size: 1.8rem;
    background: linear-gradient(45deg, #00d4ff, #ff6b35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.status-indicators {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.status {
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: bold;
}

.status.online {
    background: rgba(46, 204, 113, 0.2);
    border: 1px solid #2ecc71;
}

/* Main Content */
.main-content {
    flex: 1;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.section {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.section h2 {
    margin-bottom: 1rem;
    font-size: 1.4rem;
    background: linear-gradient(45deg, #ff6b35, #f7931e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Metrics Grid */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.metric-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.metric-card h3 {
    margin-bottom: 1rem;
    font-size: 1rem;
    color: #e0e0e0;
}

/* Progress Rings */
.progress-ring {
    position: relative;
    display: inline-block;
}

.progress-ring canvas {
    transform: rotate(-90deg);
}

.percentage {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 1.2rem;
    font-weight: bold;
    color: #00d4ff;
}

/* Scheduler Grid */
.scheduler-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 1rem;
}

.scheduler-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.scheduler-card h3 {
    margin-bottom: 1rem;
    color: #e0e0e0;
}

.learning-info p {
    margin-bottom: 0.5rem;
    color: #b0b0b0;
}

.learning-info span {
    color: #00d4ff;
    font-weight: bold;
}

/* File System Grid */
.filesystem-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.filesystem-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.filesystem-card h3 {
    margin-bottom: 1rem;
    color: #e0e0e0;
}

.security-info p {
    margin-bottom: 0.5rem;
    color: #b0b0b0;
}

.security-info span {
    color: #2ecc71;
    font-weight: bold;
}

/* Process Table */
.process-table-container {
    overflow-x: auto;
}

.process-table {
    width: 100%;
    border-collapse: collapse;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    overflow: hidden;
}

.process-table th,
.process-table td {
    padding: 0.8rem;
    text-align: left;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.process-table th {
    background: rgba(255, 255, 255, 0.1);
    font-weight: bold;
    color: #00d4ff;
}

.process-table td {
    color: #e0e0e0;
}

/* Responsive Design */
@media (max-width: 768px) {
    .header {
        flex-direction: column;
        gap: 1rem;
    }
    
    .main-content {
        padding: 1rem;
    }
    
    .scheduler-grid,
    .filesystem-grid {
        grid-template-columns: 1fr;
    }
    
    .metrics-grid {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }
}

/* Animations */
@keyframes pulse {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.6; }
}

.status.online {
    animation: pulse 2s infinite;
}

/* Chart Containers */
canvas {
    max-width: 100%;
    height: auto;
}''' 

    def _generate_javascript(self) -> str:
        """Generate JavaScript for dashboard functionality"""
        return '''// Decentralized AI Node OS - Dashboard JavaScript

class Dashboard {
    constructor() {
        this.charts = {};
        this.updateInterval = 2000; // 2 seconds
        this.initializeCharts();
        this.startDataUpdates();
    }

    initializeCharts() {
        // Performance Chart
        const perfCtx = document.getElementById('performance-chart').getContext('2d');
        this.charts.performance = new Chart(perfCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Performance Score',
                    data: [],
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { 
                        labels: { color: '#ffffff' }
                    }
                },
                scales: {
                    x: { 
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: { 
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                }
            }
        });

        // Storage Chart
        const storageCtx = document.getElementById('storage-chart').getContext('2d');
        this.charts.storage = new Chart(storageCtx, {
            type: 'doughnut',
            data: {
                labels: ['Used', 'Free'],
                datasets: [{
                    data: [0, 100],
                    backgroundColor: ['#ff6b35', '#2ecc71'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { 
                        labels: { color: '#ffffff' },
                        position: 'bottom'
                    }
                }
            }
        });
    }

    drawProgressRing(elementId, percentage, color = '#00d4ff') {
        const canvas = document.querySelector(`#${elementId} canvas`);
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 35;

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Background circle
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.lineWidth = 8;
        ctx.stroke();

        // Progress arc
        const progress = (percentage / 100) * 2 * Math.PI;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, progress);
        ctx.strokeStyle = color;
        ctx.lineWidth = 8;
        ctx.lineCap = 'round';
        ctx.stroke();

        // Update percentage text
        document.querySelector(`#${elementId.replace('-ring', '-percent')}`).textContent = `${percentage}%`;
    }

    async fetchSystemData() {
        try {
            const response = await fetch('/api/system');
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch system data:', error);
            return null;
        }
    }

    async fetchSchedulerData() {
        try {
            const response = await fetch('/api/scheduler');
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch scheduler data:', error);
            return null;
        }
    }

    async fetchFileSystemData() {
        try {
            const response = await fetch('/api/files');
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch file system data:', error);
            return null;
        }
    }

    async fetchSecurityData() {
        try {
            const response = await fetch('/api/security');
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch security data:', error);
            return null;
        }
    }

    updateSystemMetrics(data) {
        if (!data) return;

        // Update progress rings
        this.drawProgressRing('cpu-ring', data.cpu_usage, '#ff6b35');
        this.drawProgressRing('memory-ring', data.memory_usage, '#f7931e');
        this.drawProgressRing('disk-ring', data.disk_usage, '#2ecc71');
        this.drawProgressRing('network-ring', data.network_activity, '#00d4ff');

        // Update uptime
        const uptimeElement = document.getElementById('uptime');
        if (uptimeElement) {
            const hours = Math.floor(data.uptime / 3600);
            const minutes = Math.floor((data.uptime % 3600) / 60);
            const seconds = Math.floor(data.uptime % 60);
            uptimeElement.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    updateSchedulerMetrics(data) {
        if (!data) return;

        // Update learning info
        document.getElementById('learning-mode').textContent = data.learning_mode || 'Unknown';
        document.getElementById('prediction-accuracy').textContent = `${(data.prediction_accuracy || 0).toFixed(1)}%`;
        document.getElementById('adaptations').textContent = data.adaptation_count || 0;
        document.getElementById('total-scheduled').textContent = data.total_scheduled || 0;

        // Update performance chart
        const now = new Date().toLocaleTimeString();
        const performanceScore = data.avg_performance_score || 0;
        
        if (this.charts.performance.data.labels.length > 20) {
            this.charts.performance.data.labels.shift();
            this.charts.performance.data.datasets[0].data.shift();
        }
        
        this.charts.performance.data.labels.push(now);
        this.charts.performance.data.datasets[0].data.push(performanceScore);
        this.charts.performance.update('none');
    }

    updateFileSystemMetrics(data) {
        if (!data) return;

        // Update storage chart
        const usedPercentage = data.storage_utilization || 0;
        const freePercentage = 100 - usedPercentage;
        
        this.charts.storage.data.datasets[0].data = [usedPercentage, freePercentage];
        this.charts.storage.update();
    }

    updateSecurityMetrics(data) {
        if (!data) return;

        document.getElementById('encrypted-files').textContent = data.encrypted_files || 0;
        document.getElementById('active-keys').textContent = data.active_encryption_keys || 0;
        document.getElementById('security-success').textContent = `${(data.success_rate || 0).toFixed(1)}%`;
        document.getElementById('blocked-users').textContent = data.blocked_users || 0;
    }

    updateProcessTable(schedulerData) {
        const tbody = document.getElementById('process-table-body');
        if (!tbody || !schedulerData) return;

        // Clear existing rows
        tbody.innerHTML = '';

        // Add running processes
        if (schedulerData.running_processes) {
            Object.entries(schedulerData.running_processes).forEach(([coreId, process]) => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${process.id || 'N/A'}</td>
                    <td><span class="process-type">${this.getProcessTypeIcon(process.type)} ${process.type || 'Unknown'}</span></td>
                    <td>Core ${coreId}</td>
                    <td>${process.priority || 'N/A'}</td>
                    <td><span class="power-mode">${this.getPowerModeIcon(process.power_state)} ${process.power_state || 'N/A'}</span></td>
                    <td>${this.formatRuntime(process.actual_runtime || 0)}</td>
                    <td><span class="status running">🟢 Running</span></td>
                `;
            });
        }

        // Add queued processes (first few)
        if (schedulerData.queue_length > 0) {
            for (let i = 0; i < Math.min(3, schedulerData.queue_length); i++) {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>queued_${i + 1}</td>
                    <td><span class="process-type">⏳ Queued Process</span></td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                    <td><span class="status queued">🟡 Queued</span></td>
                `;
            }
        }

        // Show empty state if no processes
        if (tbody.children.length === 0) {
            const row = tbody.insertRow();
            row.innerHTML = '<td colspan="7" style="text-align: center; color: #888;">No active processes</td>';
        }
    }

    getProcessTypeIcon(type) {
        const icons = {
            'ai_worker': '🧠',
            'blockchain_miner': '⛓️',
            'smart_contract': '📜',
            'network_handler': '🌐',
            'system': '⚙️'
        };
        return icons[type] || '📄';
    }

    getPowerModeIcon(mode) {
        const icons = {
            'high_performance': '🚀',
            'balanced': '⚖️',
            'power_saver': '🔋',
            'eco_mode': '🌱'
        };
        return icons[mode] || '⚡';
    }

    formatRuntime(seconds) {
        if (seconds < 60) {
            return `${seconds.toFixed(1)}s`;
        } else if (seconds < 3600) {
            return `${(seconds / 60).toFixed(1)}m`;
        } else {
            return `${(seconds / 3600).toFixed(1)}h`;
        }
    }

    async updateAllData() {
        const [systemData, schedulerData, fileSystemData, securityData] = await Promise.all([
            this.fetchSystemData(),
            this.fetchSchedulerData(),
            this.fetchFileSystemData(),
            this.fetchSecurityData()
        ]);

        this.updateSystemMetrics(systemData);
        this.updateSchedulerMetrics(schedulerData);
        this.updateFileSystemMetrics(fileSystemData);
        this.updateSecurityMetrics(securityData);
        this.updateProcessTable(schedulerData);
    }

    startDataUpdates() {
        // Initial update
        this.updateAllData();

        // Set up periodic updates
        setInterval(() => {
            this.updateAllData();
        }, this.updateInterval);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});'''

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        uptime = time.time() - self.start_time
        
        # Simulate system metrics (in real implementation, these would come from actual system monitoring)
        import random
        
        metrics = {
            "cpu_usage": random.uniform(20, 80),
            "memory_usage": random.uniform(30, 70),
            "disk_usage": 0,
            "network_activity": random.uniform(10, 40),
            "process_count": 0,
            "uptime": uptime
        }
        
        # Get real data from file system if available
        if self.file_system:
            fs_stats = self.file_system.get_file_system_stats()
            metrics["disk_usage"] = fs_stats.get("storage_utilization", 0)
            
        # Get real data from AI scheduler if available
        if self.ai_scheduler:
            scheduler_metrics = self.ai_scheduler.get_ai_metrics()
            metrics["process_count"] = scheduler_metrics.get("active_cores", 0)
            
        return metrics
        
    def _get_file_system_data(self) -> Dict[str, Any]:
        """Get file system data"""
        if not self.file_system:
            return {
                "total_files": 0,
                "total_directories": 0,
                "storage_utilization": 0,
                "cache_hit_rate": 0
            }
            
        return self.file_system.get_file_system_stats()
        
    def _get_scheduler_data(self) -> Dict[str, Any]:
        """Get AI scheduler data"""
        if not self.ai_scheduler:
            return {
                "learning_mode": "Not Available",
                "prediction_accuracy": 0,
                "avg_performance_score": 0,
                "total_scheduled": 0,
                "adaptation_count": 0,
                "queue_length": 0,
                "running_processes": {}
            }
            
        metrics = self.ai_scheduler.get_ai_metrics()
        
        # Add running processes info for process table
        running_processes = {}
        for core_id, process in self.ai_scheduler.running_processes.items():
            running_processes[core_id] = {
                "id": process.get("id", f"proc_{core_id}"),
                "type": process.get("type", {}).get("value", "unknown") if hasattr(process.get("type", {}), "value") else str(process.get("type", "unknown")),
                "priority": process.get("priority", 50),
                "power_state": process.get("power_state", "balanced"),
                "actual_runtime": time.time() - process.get("start_time", time.time()) if process.get("start_time") else 0
            }
            
        metrics["running_processes"] = running_processes
        return metrics
        
    def _get_security_data(self) -> Dict[str, Any]:
        """Get security and encryption data"""
        if not self.encryption:
            return {
                "encrypted_files": 0,
                "active_encryption_keys": 0,
                "success_rate": 100,
                "blocked_users": 0
            }
            
        return self.encryption.get_security_statistics()

def create_integrated_gui(file_system=None, encryption=None, ai_scheduler=None, port=8080):
    """Create integrated web GUI with all system components"""
    gui = WebGUIServer(file_system, encryption, ai_scheduler, port)
    return gui 