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
        self.process_manager = None
        
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
                    
            def do_POST(self):
                parsed_path = urlparse(self.path)
                
                if parsed_path.path == '/api/processes':
                    self._create_process()
                else:
                    self.send_error(404)
                    
            def _create_process(self):
                """Handle process creation API endpoint"""
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(content_length)
                    process_data = json.loads(post_data.decode('utf-8'))
                    
                    # Import process management components
                    try:
                        from process_manager import ProcessManager
                        from process_control_block import ProcessType
                        from schedulers import MLFQScheduler
                    except ImportError:
                        self._send_json_response({
                            'error': 'Process management components not available'
                        }, 500)
                        return
                    
                    # Create process using the process manager
                    if not hasattr(gui_server, 'process_manager') or gui_server.process_manager is None:
                        # Initialize process manager if not exists
                        scheduler = MLFQScheduler(num_levels=3, time_quanta=[1000, 2000, 4000])
                        gui_server.process_manager = ProcessManager(scheduler)
                        gui_server.process_manager.start_scheduler()
                    
                    # Map process type string to ProcessType enum
                    type_mapping = {
                        'ai_inference': ProcessType.AI_INFERENCE,
                        'blockchain_validator': ProcessType.BLOCKCHAIN_VALIDATOR,
                        'data_processing': ProcessType.DATA_PROCESSING,
                        'network_node': ProcessType.NETWORK_NODE,
                        'smart_contract': ProcessType.SMART_CONTRACT,
                        'system': ProcessType.SYSTEM,
                        'user': ProcessType.USER
                    }
                    
                    process_type = type_mapping.get(process_data.get('type'), ProcessType.USER)
                    
                    # Create a simple task function based on process type
                    def create_task_function(proc_type, proc_name, args):
                        def task_function():
                            import time
                            import random
                            print(f"🚀 Starting {proc_name} ({proc_type.value})")
                            
                            # Simulate work based on process type
                            work_duration = random.uniform(5, 15)
                            for i in range(int(work_duration)):
                                time.sleep(1)
                                if i % 3 == 0:
                                    print(f"⚡ {proc_name}: Progress {i+1}/{int(work_duration)}")
                            
                            print(f"✅ {proc_name} completed successfully")
                            return f"{proc_name} execution result"
                        return task_function
                    
                    task_func = create_task_function(process_type, process_data['name'], process_data.get('args', []))
                    
                    # Create the process
                    pid = gui_server.process_manager.create_process(
                        name=process_data['name'],
                        process_type=process_type,
                        target_function=task_func,
                        args=tuple(process_data.get('args', [])),
                        priority=process_data.get('priority', 5),
                        memory_required=process_data.get('memory', 1024)
                    )
                    
                    if pid:
                        self._send_json_response({
                            'success': True,
                            'process_id': pid,
                            'message': f'Process "{process_data["name"]}" created successfully'
                        })
                    else:
                        self._send_json_response({
                            'error': 'Failed to create process - insufficient resources'
                        }, 400)
                        
                except json.JSONDecodeError:
                    self._send_json_response({
                        'error': 'Invalid JSON data'
                    }, 400)
                except Exception as e:
                    self._send_json_response({
                        'error': f'Internal server error: {str(e)}'
                    }, 500)
                    
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
                
            def _send_json_response(self, data, status_code=200):
                """Send JSON response"""
                self.send_response(status_code)
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
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="dashboard" id="dashboard">
        <!-- Main Content with Tab Navigation -->
        <main class="main-content-full" id="main-content">
            <!-- Top Header -->
            <header class="top-header">
                <div class="header-left">
                    <div class="logo-header">
                        <i class="fas fa-atom"></i>
                        <h1>🌟 Decentralized AI Node Operating System</h1>
                    </div>
                </div>
                <div class="header-right">
                    <div class="status-indicators">
                        <div class="status-badge online" id="system-status">
                            <i class="fas fa-circle"></i>
                            <span>ONLINE</span>
                        </div>
                        <div class="uptime-display">
                            <i class="fas fa-clock"></i>
                            <span>Uptime: <span id="uptime">00:00:00</span></span>
                        </div>
                    </div>
                    <div class="header-actions">
                        <button class="action-btn" id="pause-btn" title="Pause/Resume Updates">
                            <i class="fas fa-pause"></i>
                        </button>
                        <button class="action-btn" id="refresh-btn" title="Refresh Data">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                        <button class="action-btn" id="settings-btn" title="Settings">
                            <i class="fas fa-cog"></i>
                        </button>
                        <button class="action-btn" id="fullscreen-btn" title="Toggle Fullscreen">
                            <i class="fas fa-expand"></i>
                        </button>
                    </div>
                </div>
            </header>

            <!-- Tab Navigation -->
            <nav class="tab-navigation">
                <div class="tab-container">
                    <button class="tab-btn active" data-tab="overview">
                        <i class="fas fa-tachometer-alt"></i>
                        <span>System Overview</span>
                    </button>
                    <button class="tab-btn" data-tab="ai-scheduler">
                        <i class="fas fa-brain"></i>
                        <span>AI Scheduler</span>
                    </button>
                    <button class="tab-btn" data-tab="file-system">
                        <i class="fas fa-folder-open"></i>
                        <span>File System</span>
                    </button>
                    <button class="tab-btn" data-tab="processes">
                        <i class="fas fa-cogs"></i>
                        <span>Processes</span>
                    </button>
                    <button class="tab-btn" data-tab="security">
                        <i class="fas fa-shield-alt"></i>
                        <span>Security</span>
                    </button>
                </div>
            </nav>

            <!-- Notification System -->
            <div class="notification-container" id="notifications"></div>

            <!-- Tab Content Container -->
            <div class="tab-content-container">
                <!-- System Overview Tab -->
                <div class="tab-content active" id="overview-tab">
                    <div class="component-header">
                        <h2><i class="fas fa-tachometer-alt"></i> System Overview</h2>
                        <div class="component-actions">
                            <button class="btn-secondary" id="export-metrics">
                                <i class="fas fa-download"></i> Export
                            </button>
                        </div>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric-card cpu-card">
                            <div class="card-header">
                                <h3><i class="fas fa-microchip"></i> CPU Usage</h3>
                                <div class="card-actions">
                                    <span class="metric-trend" id="cpu-trend">
                                        <i class="fas fa-arrow-up"></i>
                                    </span>
                                </div>
                            </div>
                            <div class="card-content">
                                <div class="progress-ring" id="cpu-ring">
                                    <canvas width="120" height="120"></canvas>
                                    <div class="ring-content">
                                        <span class="percentage" id="cpu-percent">0%</span>
                                        <span class="label">Usage</span>
                                    </div>
                                </div>
                                <div class="metric-details">
                                    <div class="detail-item">
                                        <span class="label">Cores Active:</span>
                                        <span class="value" id="cpu-cores">0/8</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="label">Temperature:</span>
                                        <span class="value" id="cpu-temp">42°C</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="metric-card memory-card">
                            <div class="card-header">
                                <h3><i class="fas fa-memory"></i> Memory Usage</h3>
                                <div class="card-actions">
                                    <span class="metric-trend" id="memory-trend">
                                        <i class="fas fa-arrow-down"></i>
                                    </span>
                                </div>
                            </div>
                            <div class="card-content">
                                <div class="progress-ring" id="memory-ring">
                                    <canvas width="120" height="120"></canvas>
                                    <div class="ring-content">
                                        <span class="percentage" id="memory-percent">0%</span>
                                        <span class="label">Used</span>
                                    </div>
                                </div>
                                <div class="metric-details">
                                    <div class="detail-item">
                                        <span class="label">Used:</span>
                                        <span class="value" id="memory-used">0 GB</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="label">Available:</span>
                                        <span class="value" id="memory-available">16 GB</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="metric-card disk-card">
                            <div class="card-header">
                                <h3><i class="fas fa-hdd"></i> Storage</h3>
                                <div class="card-actions">
                                    <span class="metric-trend" id="disk-trend">
                                        <i class="fas fa-minus"></i>
                                    </span>
                                </div>
                            </div>
                            <div class="card-content">
                                <div class="progress-ring" id="disk-ring">
                                    <canvas width="120" height="120"></canvas>
                                    <div class="ring-content">
                                        <span class="percentage" id="disk-percent">0%</span>
                                        <span class="label">Used</span>
                                    </div>
                                </div>
                                <div class="metric-details">
                                    <div class="detail-item">
                                        <span class="label">Used:</span>
                                        <span class="value" id="disk-used">0 TB</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="label">Total:</span>
                                        <span class="value" id="disk-total">2 TB</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="metric-card network-card">
                            <div class="card-header">
                                <h3><i class="fas fa-network-wired"></i> Network</h3>
                                <div class="card-actions">
                                    <span class="metric-trend" id="network-trend">
                                        <i class="fas fa-arrow-up"></i>
                                    </span>
                                </div>
                            </div>
                            <div class="card-content">
                                <div class="progress-ring" id="network-ring">
                                    <canvas width="120" height="120"></canvas>
                                    <div class="ring-content">
                                        <span class="percentage" id="network-percent">0%</span>
                                        <span class="label">Activity</span>
                                    </div>
                                </div>
                                <div class="metric-details">
                                    <div class="detail-item">
                                        <span class="label">Down:</span>
                                        <span class="value" id="network-down">0 MB/s</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="label">Up:</span>
                                        <span class="value" id="network-up">0 MB/s</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Quick Stats Bar -->
                    <div class="quick-stats">
                        <div class="stat-item">
                            <i class="fas fa-bolt"></i>
                            <div class="stat-content">
                                <span class="stat-value" id="power-consumption">450W</span>
                                <span class="stat-label">Power Draw</span>
                            </div>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-thermometer-half"></i>
                            <div class="stat-content">
                                <span class="stat-value" id="system-temp">65°C</span>
                                <span class="stat-label">System Temp</span>
                            </div>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-tachometer-alt"></i>
                            <div class="stat-content">
                                <span class="stat-value" id="performance-score">95%</span>
                                <span class="stat-label">Performance</span>
                            </div>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-shield-alt"></i>
                            <div class="stat-content">
                                <span class="stat-value" id="security-level">High</span>
                                <span class="stat-label">Security</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- AI Scheduler Tab -->
                <div class="tab-content" id="ai-scheduler-tab">
                    <div class="component-header">
                        <h2><i class="fas fa-brain"></i> AI Scheduler Intelligence</h2>
                        <div class="component-actions">
                            <button class="btn-secondary">
                                <i class="fas fa-cog"></i> Configure
                            </button>
                        </div>
                    </div>
                    
                    <div class="scheduler-grid-full">
                        <div class="chart-card">
                            <div class="card-header">
                                <h3><i class="fas fa-chart-line"></i> Performance Metrics</h3>
                                <div class="chart-controls">
                                    <select class="time-range" id="chart-timerange">
                                        <option value="1h">Last Hour</option>
                                        <option value="6h">Last 6 Hours</option>
                                        <option value="24h" selected>Last 24 Hours</option>
                                        <option value="7d">Last Week</option>
                                    </select>
                                </div>
                            </div>
                            <div class="card-content">
                                <canvas id="performance-chart" width="400" height="250"></canvas>
                            </div>
                        </div>
                        
                        <div class="info-card">
                            <div class="card-header">
                                <h3><i class="fas fa-brain"></i> Learning Status</h3>
                                <div class="status-indicator learning-active">
                                    <i class="fas fa-circle"></i>
                                </div>
                            </div>
                            <div class="card-content">
                                <div class="learning-metrics">
                                    <div class="metric-row">
                                        <span class="metric-label">Mode:</span>
                                        <span class="metric-value" id="learning-mode">Adaptive</span>
                                    </div>
                                    <div class="metric-row">
                                        <span class="metric-label">Accuracy:</span>
                                        <span class="metric-value" id="prediction-accuracy">94.7%</span>
                                    </div>
                                    <div class="metric-row">
                                        <span class="metric-label">Adaptations:</span>
                                        <span class="metric-value" id="adaptations">1,247</span>
                                    </div>
                                    <div class="metric-row">
                                        <span class="metric-label">Processes:</span>
                                        <span class="metric-value" id="total-scheduled">342</span>
                                    </div>
                                    <div class="metric-row">
                                        <span class="metric-label">Queue Length:</span>
                                        <span class="metric-value" id="queue-length">12</span>
                                    </div>
                                </div>
                                <div class="learning-progress">
                                    <div class="progress-label">Learning Progress</div>
                                    <div class="progress-bar">
                                        <div class="progress-fill" id="learning-progress" style="width: 78%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- File System Tab -->
                <div class="tab-content" id="file-system-tab">
                    <div class="component-header">
                        <h2><i class="fas fa-folder-open"></i> File System Monitor</h2>
                        <div class="component-actions">
                            <button class="btn-secondary" id="analyze-storage">
                                <i class="fas fa-chart-line"></i> Analyze Storage
                            </button>
                            <button class="btn-secondary" id="search-files">
                                <i class="fas fa-search"></i> Search Files
                            </button>
                            <button class="btn-secondary" id="cleanup-disk">
                                <i class="fas fa-broom"></i> Cleanup
                            </button>
                        </div>
                    </div>
                    
                    <!-- Storage Overview Cards -->
                    <div class="storage-overview-grid">
                        <div class="storage-summary-card">
                            <div class="card-header">
                                <h3><i class="fas fa-hdd"></i> Storage Summary</h3>
                                <div class="health-indicator excellent">
                                    <i class="fas fa-check-circle"></i>
                                    <span>Excellent</span>
                            </div>
                                    </div>
                            <div class="storage-donut-container">
                                <canvas id="storage-donut-chart" width="200" height="200"></canvas>
                                <div class="donut-center-info">
                                    <div class="center-value">
                                        <span class="used-amount" id="storage-used-amount">1.2</span>
                                        <span class="unit">TB</span>
                                    </div>
                                    <div class="center-label">Used</div>
                                </div>
                            </div>
                            <div class="storage-breakdown">
                                <div class="breakdown-item">
                                    <div class="breakdown-color" style="background: var(--accent-blue);"></div>
                                    <span class="breakdown-label">System Files</span>
                                    <span class="breakdown-value" id="system-files-size">420 GB</span>
                                </div>
                                <div class="breakdown-item">
                                    <div class="breakdown-color" style="background: var(--accent-purple);"></div>
                                    <span class="breakdown-label">AI Models</span>
                                    <span class="breakdown-value" id="ai-models-size">680 GB</span>
                                </div>
                                <div class="breakdown-item">
                                    <div class="breakdown-color" style="background: var(--accent-green);"></div>
                                    <span class="breakdown-label">User Data</span>
                                    <span class="breakdown-value" id="user-data-size">120 GB</span>
                                </div>
                                <div class="breakdown-item">
                                    <div class="breakdown-color" style="background: var(--accent-orange);"></div>
                                    <span class="breakdown-label">Cache</span>
                                    <span class="breakdown-value" id="cache-size">45 GB</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="storage-details-card">
                            <div class="card-header">
                                <h3><i class="fas fa-chart-bar"></i> Storage Details</h3>
                                <div class="time-range-selector">
                                    <select id="storage-timeframe">
                                        <option value="24h">Last 24h</option>
                                        <option value="7d" selected>Last Week</option>
                                        <option value="30d">Last Month</option>
                                    </select>
                            </div>
                            </div>
                            <div class="storage-metrics-grid">
                                <div class="metric-item">
                                    <div class="metric-icon">
                                        <i class="fas fa-file-alt"></i>
                                    </div>
                                    <div class="metric-info">
                                        <span class="metric-value" id="total-files">2,847</span>
                                        <span class="metric-label">Total Files</span>
                                        <span class="metric-change positive">+12 today</span>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <div class="metric-icon">
                                        <i class="fas fa-folder"></i>
                                    </div>
                                    <div class="metric-info">
                                        <span class="metric-value" id="total-directories">156</span>
                                        <span class="metric-label">Directories</span>
                                        <span class="metric-change neutral">No change</span>
                                    </div>
                                </div>
                                
                                <div class="metric-item">
                                    <div class="metric-icon">
                                        <i class="fas fa-tachometer-alt"></i>
                                    </div>
                                    <div class="metric-info">
                                        <span class="metric-value" id="cache-hit-rate">94.2%</span>
                                        <span class="metric-label">Cache Hit Rate</span>
                                        <span class="metric-change positive">+2.1%</span>
                                    </div>
                                    </div>
                                
                                <div class="metric-item">
                                    <div class="metric-icon">
                                        <i class="fas fa-exchange-alt"></i>
                                    </div>
                                    <div class="metric-info">
                                        <span class="metric-value" id="io-operations">1,248/s</span>
                                        <span class="metric-label">I/O Operations</span>
                                        <span class="metric-change positive">+5.2%</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="performance-trends-card">
                            <div class="card-header">
                                <h3><i class="fas fa-chart-line"></i> Performance Trends</h3>
                                <div class="trend-indicators">
                                    <div class="trend-item excellent">
                                        <i class="fas fa-arrow-up"></i>
                                        <span>Excellent</span>
                                    </div>
                                </div>
                            </div>
                            <div class="card-content">
                                <canvas id="fs-performance-chart" width="400" height="200"></canvas>
                            </div>
                        </div>
                    </div>

                    <!-- Advanced Analytics Section -->
                    <div class="advanced-analytics-section">
                        <div class="section-header">
                            <h3><i class="fas fa-microscope"></i> Advanced Analytics</h3>
                        </div>
                        
                        <div class="analytics-grid">
                            <div class="analytics-card fragmentation-card">
                                <div class="card-header">
                                    <h4><i class="fas fa-puzzle-piece"></i> Disk Fragmentation</h4>
                                    <span class="status-badge good">Good</span>
                                </div>
                                <div class="fragmentation-visual">
                                    <div class="fragmentation-bar">
                                        <div class="fragmentation-fill" id="fragmentation-fill" style="width: 15%;"></div>
                                    </div>
                                    <div class="fragmentation-stats">
                                        <span class="frag-value" id="fragmentation">2.1%</span>
                                        <span class="frag-label">Fragmented</span>
                                    </div>
                                </div>
                                <div class="fragmentation-recommendation">
                                    <i class="fas fa-lightbulb"></i>
                                    <span>System running optimally. No defragmentation needed.</span>
                                </div>
                            </div>

                            <div class="analytics-card access-patterns-card">
                                <div class="card-header">
                                    <h4><i class="fas fa-route"></i> Access Patterns</h4>
                                </div>
                                <div class="access-pattern-list">
                                    <div class="pattern-item hot">
                                        <div class="pattern-icon">🔥</div>
                                        <div class="pattern-info">
                                            <span class="pattern-path">/ai_models/neural_networks/</span>
                                            <span class="pattern-frequency">1,247 accesses/h</span>
                                        </div>
                                    </div>
                                    <div class="pattern-item warm">
                                        <div class="pattern-icon">⚡</div>
                                        <div class="pattern-info">
                                            <span class="pattern-path">/blockchain/contracts/</span>
                                            <span class="pattern-frequency">523 accesses/h</span>
                                        </div>
                                    </div>
                                    <div class="pattern-item cool">
                                        <div class="pattern-icon">❄️</div>
                                        <div class="pattern-info">
                                            <span class="pattern-path">/logs/archive/</span>
                                            <span class="pattern-frequency">12 accesses/h</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="analytics-card health-score-card">
                                <div class="card-header">
                                    <h4><i class="fas fa-heartbeat"></i> System Health</h4>
                                </div>
                                <div class="health-score-visual">
                                    <div class="health-ring" id="health-ring">
                                        <canvas width="120" height="120"></canvas>
                                        <div class="health-center">
                                            <span class="health-score" id="health-score">95</span>
                                            <span class="health-unit">%</span>
                                        </div>
                                    </div>
                                    <div class="health-factors">
                                        <div class="factor">
                                            <span class="factor-name">Speed</span>
                                            <div class="factor-bar">
                                                <div class="factor-fill" style="width: 92%;"></div>
                                            </div>
                                        </div>
                                        <div class="factor">
                                            <span class="factor-name">Reliability</span>
                                            <div class="factor-bar">
                                                <div class="factor-fill" style="width: 98%;"></div>
                                            </div>
                                        </div>
                                        <div class="factor">
                                            <span class="factor-name">Efficiency</span>
                                            <div class="factor-bar">
                                                <div class="factor-fill" style="width: 96%;"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Processes Tab -->
                <div class="tab-content" id="processes-tab">
                    <div class="component-header">
                        <h2><i class="fas fa-cogs"></i> Process Monitor</h2>
                        <div class="component-actions">
                            <div class="search-box">
                                <i class="fas fa-search"></i>
                                <input type="text" placeholder="Search processes..." id="process-search">
                            </div>
                            <button class="btn-secondary">
                                <i class="fas fa-plus"></i> New Process
                            </button>
                        </div>
                    </div>
                    
                    <div class="process-table-container">
                        <div class="table-controls">
                            <div class="table-filters">
                                <select class="filter-select" id="status-filter">
                                    <option value="all">All Status</option>
                                    <option value="running">Running</option>
                                    <option value="queued">Queued</option>
                                    <option value="paused">Paused</option>
                                </select>
                                <select class="filter-select" id="type-filter">
                                    <option value="all">All Types</option>
                                    <option value="ai_worker">AI Worker</option>
                                    <option value="blockchain_miner">Blockchain Miner</option>
                                    <option value="smart_contract">Smart Contract</option>
                                    <option value="network_handler">Network Handler</option>
                                </select>
                            </div>
                            <div class="table-actions">
                                <button class="btn-icon" title="Refresh">
                                    <i class="fas fa-sync-alt"></i>
                                </button>
                                <button class="btn-icon" title="Export">
                                    <i class="fas fa-download"></i>
                                </button>
                            </div>
                        </div>
                        
                        <table class="process-table">
                            <thead>
                                <tr>
                                    <th><input type="checkbox" id="select-all"></th>
                                    <th>Process ID</th>
                                    <th>Type</th>
                                    <th>CPU Core</th>
                                    <th>Priority</th>
                                    <th>Power Mode</th>
                                    <th>Runtime</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="process-table-body">
                                <!-- Processes will be populated here -->
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Process Creation Modal -->
                <div id="process-modal" class="modal" style="display: none;">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3><i class="fas fa-plus"></i> Create New Process</h3>
                            <button class="modal-close" onclick="closeProcessModal()">&times;</button>
                        </div>
                        <div class="modal-body">
                            <form id="process-form">
                                <div class="form-group">
                                    <label for="process-name">Process Name</label>
                                    <input type="text" id="process-name" name="name" placeholder="Enter process name" required>
                                </div>
                                <div class="form-group">
                                    <label for="process-type">Process Type</label>
                                    <select id="process-type" name="type" required>
                                        <option value="">Select process type</option>
                                        <option value="ai_inference">🧠 AI Inference</option>
                                        <option value="blockchain_validator">⛓️ Blockchain Validator</option>
                                        <option value="data_processing">📊 Data Processing</option>
                                        <option value="network_node">🌐 Network Node</option>
                                        <option value="smart_contract">📜 Smart Contract</option>
                                        <option value="system">⚙️ System Task</option>
                                        <option value="user">👤 User Process</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="process-priority">Priority (0-10)</label>
                                    <input type="range" id="process-priority" name="priority" min="0" max="10" value="5">
                                    <span id="priority-value">5</span>
                                </div>
                                <div class="form-group">
                                    <label for="process-memory">Memory Required (MB)</label>
                                    <input type="number" id="process-memory" name="memory" min="64" max="8192" value="1024" step="64">
                                </div>
                                <div class="form-group">
                                    <label for="process-args">Arguments (optional)</label>
                                    <textarea id="process-args" name="args" placeholder="Enter process arguments, one per line"></textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn-secondary" onclick="closeProcessModal()">Cancel</button>
                            <button type="button" class="btn-primary" onclick="createProcess()">Create Process</button>
                        </div>
                    </div>
                </div>

                <!-- Security Tab -->
                <div class="tab-content" id="security-tab">
                    <div class="component-header">
                        <h2><i class="fas fa-shield-alt"></i> Security Center</h2>
                        <div class="component-actions">
                            <button class="btn-secondary">
                                <i class="fas fa-shield-virus"></i> Run Scan
                            </button>
                            <button class="btn-secondary">
                                <i class="fas fa-key"></i> Manage Keys
                            </button>
                        </div>
                    </div>
                    
                    <div class="security-overview">
                        <!-- Security Status Cards -->
                        <div class="security-cards">
                            <div class="security-card threat-card">
                                <div class="card-header">
                                    <h3><i class="fas fa-exclamation-triangle"></i> Threat Detection</h3>
                                    <div class="status-indicator safe">
                                        <i class="fas fa-check-circle"></i>
                                    </div>
                                </div>
                                <div class="card-content">
                                    <div class="threat-level">
                                        <div class="threat-gauge">
                                            <div class="gauge-fill" style="width: 15%"></div>
                                        </div>
                                        <span class="threat-text">Low Risk</span>
                                    </div>
                                    <div class="threat-stats">
                                        <div class="stat">
                                            <span class="label">Threats Blocked:</span>
                                            <span class="value">247</span>
                                        </div>
                                        <div class="stat">
                                            <span class="label">Last Threat:</span>
                                            <span class="value">3 hours ago</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="security-card encryption-card">
                                <div class="card-header">
                                    <h3><i class="fas fa-lock"></i> Encryption Status</h3>
                                    <div class="status-indicator active">
                                        <i class="fas fa-circle"></i>
                                    </div>
                                </div>
                                <div class="card-content">
                                    <div class="encryption-stats">
                                        <div class="metric-row">
                                            <span class="metric-label">Encrypted Files:</span>
                                            <span class="metric-value" id="security-encrypted-files">1,542</span>
                                        </div>
                                        <div class="metric-row">
                                            <span class="metric-label">Active Keys:</span>
                                            <span class="metric-value" id="security-active-keys">8</span>
                                        </div>
                                        <div class="metric-row">
                                            <span class="metric-label">Encryption Level:</span>
                                            <span class="metric-value">AES-256</span>
                                        </div>
                                        <div class="metric-row">
                                            <span class="metric-label">Key Rotation:</span>
                                            <span class="metric-value">Auto (24h)</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="security-card access-card">
                                <div class="card-header">
                                    <h3><i class="fas fa-users-shield"></i> Access Control</h3>
                                    <div class="status-indicator warning">
                                        <i class="fas fa-exclamation-triangle"></i>
                                    </div>
                                </div>
                                <div class="card-content">
                                    <div class="access-stats">
                                        <div class="metric-row">
                                            <span class="metric-label">Active Sessions:</span>
                                            <span class="metric-value">12</span>
                                        </div>
                                        <div class="metric-row">
                                            <span class="metric-label">Failed Attempts:</span>
                                            <span class="metric-value warning">5</span>
                                        </div>
                                        <div class="metric-row">
                                            <span class="metric-label">Blocked IPs:</span>
                                            <span class="metric-value" id="security-blocked-users">3</span>
                                        </div>
                                        <div class="metric-row">
                                            <span class="metric-label">Success Rate:</span>
                                            <span class="metric-value" id="security-success-rate">99.8%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="security-card audit-card">
                                <div class="card-header">
                                    <h3><i class="fas fa-clipboard-list"></i> Audit Log</h3>
                                    <div class="status-indicator active">
                                        <i class="fas fa-circle"></i>
                                    </div>
                                </div>
                                <div class="card-content">
                                    <div class="audit-stats">
                                        <div class="metric-row">
                                            <span class="metric-label">Log Entries:</span>
                                            <span class="metric-value">24,789</span>
                                        </div>
                                        <div class="metric-row">
                                            <span class="metric-label">Last Entry:</span>
                                            <span class="metric-value" id="security-last-scan">2 min ago</span>
                                        </div>
                                        <div class="metric-row">
                                            <span class="metric-label">Storage Used:</span>
                                            <span class="metric-value">847 MB</span>
                                        </div>
                                        <div class="metric-row">
                                            <span class="metric-label">Retention:</span>
                                            <span class="metric-value">90 days</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Security Timeline -->
                        <div class="security-timeline">
                            <div class="timeline-header">
                                <h3><i class="fas fa-history"></i> Recent Security Events</h3>
                                <button class="btn-secondary">
                                    <i class="fas fa-filter"></i> Filter
                                </button>
                            </div>
                            <div class="timeline-content">
                                <div class="timeline-item success">
                                    <div class="timeline-icon">
                                        <i class="fas fa-check"></i>
                                    </div>
                                    <div class="timeline-content-item">
                                        <h4>Security Scan Completed</h4>
                                        <p>Full system scan completed successfully. No threats detected.</p>
                                        <span class="timestamp">2 minutes ago</span>
                                    </div>
                                </div>
                                <div class="timeline-item warning">
                                    <div class="timeline-icon">
                                        <i class="fas fa-exclamation-triangle"></i>
                                    </div>
                                    <div class="timeline-content-item">
                                        <h4>Failed Login Attempt</h4>
                                        <p>Multiple failed login attempts from IP 192.168.1.245</p>
                                        <span class="timestamp">15 minutes ago</span>
                                    </div>
                                </div>
                                <div class="timeline-item info">
                                    <div class="timeline-icon">
                                        <i class="fas fa-key"></i>
                                    </div>
                                    <div class="timeline-content-item">
                                        <h4>Encryption Key Rotated</h4>
                                        <p>Automatic key rotation completed for database encryption.</p>
                                        <span class="timestamp">1 hour ago</span>
                                    </div>
                                </div>
                                <div class="timeline-item success">
                                    <div class="timeline-icon">
                                        <i class="fas fa-shield-alt"></i>
                                    </div>
                                    <div class="timeline-content-item">
                                        <h4>Firewall Rule Updated</h4>
                                        <p>New firewall rules applied to block suspicious traffic.</p>
                                        <span class="timestamp">3 hours ago</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- Loading Overlay -->
    <div class="loading-overlay" id="loading-overlay">
        <div class="loading-spinner">
            <div class="spinner"></div>
            <span>Loading system data...</span>
        </div>
    </div>

    <script src="/static/dashboard.js"></script>
</body>
</html>'''

    def _generate_css(self) -> str:
        """Generate CSS styles for the dashboard"""
        return '''/* Enhanced Decentralized AI Node OS - Modern Dashboard Styles */

:root {
    /* Color Palette */
    --primary-bg: #0a0a0f;
    --secondary-bg: #1a1a2e;
    --accent-bg: #16213e;
    --card-bg: rgba(255, 255, 255, 0.05);
    --glass-bg: rgba(255, 255, 255, 0.08);
    --border-color: rgba(255, 255, 255, 0.1);
    --text-primary: #ffffff;
    --text-secondary: #b8bcc8;
    --text-muted: #6c757d;
    
    /* Accent Colors */
    --accent-blue: #00d4ff;
    --accent-purple: #8b5cf6;
    --accent-green: #10b981;
    --accent-orange: #f59e0b;
    --accent-red: #ef4444;
    --accent-pink: #ec4899;
    
    /* Gradients */
    --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --gradient-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --gradient-success: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    --gradient-warning: linear-gradient(135deg, #fad961 0%, #f76b1c 100%);
    
    /* Shadows */
    --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.15);
    --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.2);
    --shadow-xl: 0 16px 64px rgba(0, 0, 0, 0.25);
    
    /* Transitions */
    --transition-fast: 0.2s ease;
    --transition-smooth: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    
    /* Spacing */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    --spacing-2xl: 3rem;
    
    /* Border Radius */
    --radius-sm: 6px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 24px;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--primary-bg);
    color: var(--text-primary);
    line-height: 1.6;
    overflow-x: hidden;
}

body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.15) 0%, transparent 50%);
    pointer-events: none;
    z-index: -1;
}

/* Dashboard Layout - Full Width */
.dashboard {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    transition: var(--transition-smooth);
}

/* Remove all sidebar-related styles and update main content */
.main-content-full {
    flex: 1;
    width: 100%;
    transition: var(--transition-smooth);
}

/* Logo in Header */
.logo-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.logo-header i {
    font-size: 2rem;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: rotate 10s linear infinite;
}

.logo-header h1 {
    margin: 0;
    font-size: 1.8rem;
    font-weight: 700;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Full Width Dashboard Content */
.dashboard-content-full {
    padding: var(--spacing-xl);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
    max-width: 100%;
}

/* Full Width Section Styling */
.section-full {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    box-shadow: var(--shadow-md);
    transition: var(--transition-smooth);
    width: 100%;
}

.section-full:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

/* Enhanced Scheduler Grid for Full Width */
.scheduler-grid-full {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: var(--spacing-lg);
}

/* Top Header */
.top-header {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border-color);
    padding: var(--spacing-lg) var(--spacing-xl);
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 50;
}

.header-left h1 {
    font-size: 1.8rem;
    font-weight: 700;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: var(--spacing-xs);
}

.breadcrumb {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.header-right {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
}

.status-indicators {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.status-badge {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-xl);
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status-badge.online {
    background: linear-gradient(135deg, var(--accent-green), #059669);
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
    animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(16, 185, 129, 0.3); }
    50% { box-shadow: 0 0 30px rgba(16, 185, 129, 0.5); }
}

.uptime-display {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.header-actions {
    display: flex;
    gap: var(--spacing-sm);
}

.action-btn {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-md);
    border: none;
    background: var(--card-bg);
    color: var(--text-secondary);
    cursor: pointer;
    transition: var(--transition-fast);
    display: flex;
    align-items: center;
    justify-content: center;
}

.action-btn:hover {
    background: var(--accent-bg);
    color: var(--text-primary);
    transform: translateY(-2px);
}

/* Notification System */
.notification-container {
    position: fixed;
    top: 100px;
    right: var(--spacing-xl);
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.notification {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--spacing-md);
    min-width: 300px;
    box-shadow: var(--shadow-lg);
    transform: translateX(100%);
    animation: slideIn 0.3s ease forwards;
}

@keyframes slideIn {
    to { transform: translateX(0); }
}

/* Dashboard Content */
.dashboard-content {
    padding: var(--spacing-xl);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
}

/* Section Styling */
.section {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    box-shadow: var(--shadow-md);
    transition: var(--transition-smooth);
}

.section:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--spacing-xl);
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
}

.section-header h2 {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    font-size: 1.5rem;
    font-weight: 600;
    background: var(--gradient-secondary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.section-actions {
    display: flex;
    gap: var(--spacing-md);
}

.btn-secondary, .btn-primary {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-md);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: var(--transition-fast);
    border: none;
}

.btn-secondary {
    background: var(--card-bg);
    color: var(--text-secondary);
    border: 1px solid var(--border-color);
}

.btn-secondary:hover {
    background: var(--accent-bg);
    color: var(--text-primary);
    transform: translateY(-1px);
}

.btn-primary {
    background: var(--gradient-primary);
    color: var(--text-primary);
}

.btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

/* Metrics Grid */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
}

.metric-card {
    background: var(--glass-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    transition: var(--transition-smooth);
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--gradient-primary);
    transform: scaleX(0);
    transition: var(--transition-smooth);
}

.metric-card:hover::before {
    transform: scaleX(1);
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--spacing-lg);
}

.card-header h3 {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
}

.metric-trend {
    display: flex;
    align-items: center;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-md);
    font-size: 0.8rem;
}

.card-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-lg);
}

/* Progress Rings */
.progress-ring {
    position: relative;
    display: inline-block;
}

.progress-ring canvas {
    transform: rotate(-90deg);
    filter: drop-shadow(0 0 10px rgba(0, 212, 255, 0.3));
}

.ring-content {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
}

.percentage {
    display: block;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent-blue);
    line-height: 1;
    margin-bottom: var(--spacing-xs);
}

.ring-content .label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-details {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-sm);
    background: rgba(255, 255, 255, 0.02);
    border-radius: var(--radius-sm);
}

.detail-item .label {
    color: var(--text-secondary);
    font-size: 0.85rem;
}

.detail-item .value {
    color: var(--text-primary);
    font-weight: 600;
    font-size: 0.9rem;
}

/* Quick Stats */
.quick-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-lg);
    padding: var(--spacing-lg);
    background: rgba(255, 255, 255, 0.02);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-color);
}

.stat-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    transition: var(--transition-fast);
}

.stat-item:hover {
    background: var(--card-bg);
}

.stat-item i {
    font-size: 1.5rem;
    color: var(--accent-blue);
}

.stat-content {
    display: flex;
    flex-direction: column;
}

.stat-value {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1;
}

.stat-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Scheduler Grid */
.scheduler-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--spacing-lg);
}

.chart-card, .info-card {
    background: var(--glass-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    transition: var(--transition-smooth);
}

.chart-card:hover, .info-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.chart-controls {
    display: flex;
    gap: var(--spacing-sm);
}

.time-range {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
    color: var(--text-primary);
    font-size: 0.85rem;
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    position: relative;
}

.status-indicator.learning-active {
    background: var(--accent-green);
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
    animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.2); }
}

.learning-metrics {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-sm);
    border-radius: var(--radius-sm);
}

.metric-row:nth-child(even) {
    background: rgba(255, 255, 255, 0.02);
}

.metric-label {
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.metric-value {
    color: var(--text-primary);
    font-weight: 600;
    font-size: 0.95rem;
}

.learning-progress {
    margin-top: var(--spacing-lg);
}

.progress-label {
    color: var(--text-secondary);
    font-size: 0.85rem;
    margin-bottom: var(--spacing-sm);
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-sm);
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: var(--gradient-primary);
    border-radius: var(--radius-sm);
    transition: var(--transition-smooth);
    position: relative;
}

.progress-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

/* Enhanced File System Styles */
.storage-overview-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
}

.storage-summary-card,
.storage-details-card,
.performance-trends-card {
    background: var(--glass-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    transition: var(--transition-smooth);
    position: relative;
    overflow: hidden;
}

.storage-summary-card::before,
.storage-details-card::before,
.performance-trends-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--gradient-primary);
    transform: scaleX(0);
    transition: var(--transition-smooth);
}

.storage-summary-card:hover::before,
.storage-details-card:hover::before,
.performance-trends-card:hover::before {
    transform: scaleX(1);
}

.storage-summary-card:hover,
.storage-details-card:hover,
.performance-trends-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

.health-indicator {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-xl);
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.health-indicator.excellent {
    background: rgba(16, 185, 129, 0.2);
    color: var(--accent-green);
    border: 1px solid var(--accent-green);
}

.storage-donut-container {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: var(--spacing-lg) 0;
}

.donut-center-info {
    position: absolute;
    text-align: center;
}

.center-value {
    display: block;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1;
}

.center-value .used-amount {
    color: var(--accent-blue);
}

.center-value .unit {
    font-size: 1rem;
    color: var(--text-secondary);
}

.center-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: var(--spacing-xs);
}

.storage-breakdown {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.breakdown-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm);
    background: rgba(255, 255, 255, 0.02);
    border-radius: var(--radius-sm);
    transition: var(--transition-fast);
}

.breakdown-item:hover {
    background: rgba(255, 255, 255, 0.05);
}

.breakdown-color {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
}

.breakdown-label {
    flex: 1;
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.breakdown-value {
    color: var(--text-primary);
    font-weight: 600;
    font-size: 0.9rem;
}

.time-range-selector select {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
    color: var(--text-primary);
    font-size: 0.85rem;
}

.storage-metrics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-md);
}

.metric-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    background: rgba(255, 255, 255, 0.02);
    border-radius: var(--radius-md);
    transition: var(--transition-fast);
}

.metric-item:hover {
    background: rgba(255, 255, 255, 0.05);
    transform: translateY(-2px);
}

.metric-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--accent-blue);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: 1.2rem;
}

.metric-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}

.metric-info .metric-value {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1;
}

.metric-info .metric-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-change {
    font-size: 0.8rem;
    font-weight: 500;
    padding: 2px 6px;
    border-radius: var(--radius-sm);
}

.metric-change.positive {
    color: var(--accent-green);
    background: rgba(16, 185, 129, 0.1);
}

.metric-change.negative {
    color: var(--accent-red);
    background: rgba(239, 68, 68, 0.1);
}

.metric-change.neutral {
    color: var(--text-muted);
    background: rgba(255, 255, 255, 0.05);
}

.trend-indicators {
    display: flex;
    gap: var(--spacing-sm);
}

.trend-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-xl);
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.trend-item.excellent {
    background: rgba(16, 185, 129, 0.2);
    color: var(--accent-green);
    border: 1px solid var(--accent-green);
}

/* Advanced Analytics Section */
.advanced-analytics-section {
    margin-top: var(--spacing-xl);
}

.advanced-analytics-section .section-header {
    margin-bottom: var(--spacing-lg);
    padding-bottom: var(--spacing-md);
    border-bottom: 1px solid var(--border-color);
}

.advanced-analytics-section .section-header h3 {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--text-primary);
}

.analytics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: var(--spacing-lg);
}

.analytics-card {
    background: var(--glass-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    transition: var(--transition-smooth);
    position: relative;
    overflow: hidden;
}

.analytics-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--gradient-secondary);
    transform: scaleX(0);
    transition: var(--transition-smooth);
}

.analytics-card:hover::before {
    transform: scaleX(1);
}

.analytics-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

.analytics-card .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--spacing-lg);
}

.analytics-card .card-header h4 {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
}

.status-badge.good {
    background: rgba(16, 185, 129, 0.2);
    color: var(--accent-green);
    border: 1px solid var(--accent-green);
}

/* Fragmentation Visual */
.fragmentation-visual {
    margin-bottom: var(--spacing-lg);
}

.fragmentation-bar {
    width: 100%;
    height: 12px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-sm);
    overflow: hidden;
    margin-bottom: var(--spacing-md);
}

.fragmentation-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-green), var(--accent-orange), var(--accent-red));
    border-radius: var(--radius-sm);
    transition: var(--transition-smooth);
}

.fragmentation-stats {
    text-align: center;
}

.frag-value {
    display: block;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent-green);
    line-height: 1;
}

.frag-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.fragmentation-recommendation {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm);
    background: rgba(16, 185, 129, 0.05);
    border-radius: var(--radius-sm);
    border-left: 3px solid var(--accent-green);
    color: var(--text-secondary);
    font-size: 0.9rem;
}

/* Access Patterns */
.access-pattern-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.pattern-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    transition: var(--transition-fast);
}

.pattern-item:hover {
    background: rgba(255, 255, 255, 0.05);
}

.pattern-item.hot {
    background: rgba(239, 68, 68, 0.05);
    border-left: 3px solid var(--accent-red);
}

.pattern-item.warm {
    background: rgba(245, 158, 11, 0.05);
    border-left: 3px solid var(--accent-orange);
}

.pattern-item.cool {
    background: rgba(59, 130, 246, 0.05);
    border-left: 3px solid var(--accent-blue);
}

.pattern-icon {
    font-size: 1.5rem;
    width: 40px;
    text-align: center;
}

.pattern-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}

.pattern-path {
    font-family: 'Monaco', 'Consolas', monospace;
    color: var(--text-primary);
    font-size: 0.9rem;
    font-weight: 500;
}

.pattern-frequency {
    color: var(--text-secondary);
    font-size: 0.8rem;
}

/* Health Score Visual */
.health-score-visual {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-lg);
}

.health-ring {
    position: relative;
    display: inline-block;
}

.health-center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
}

.health-score {
    display: block;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent-green);
    line-height: 1;
}

.health-unit {
    font-size: 1rem;
    color: var(--text-secondary);
}

.health-factors {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.factor {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}

.factor-name {
    font-size: 0.85rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.factor-bar {
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-sm);
    overflow: hidden;
}

.factor-fill {
    height: 100%;
    background: var(--gradient-primary);
    border-radius: var(--radius-sm);
    transition: var(--transition-smooth);
}

/* File System Grid (Legacy) */
.filesystem-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-lg);
}

.storage-legend {
    display: flex;
    justify-content: center;
    gap: var(--spacing-lg);
    margin-top: var(--spacing-md);
}

.legend-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.color-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}

.color-dot.used {
    background: var(--accent-orange);
}

.color-dot.free {
    background: var(--accent-green);
}

/* Responsive Design for File System */
@media (max-width: 1200px) {
    .storage-overview-grid {
        grid-template-columns: 1fr 1fr;
    }
    
    .performance-trends-card {
        grid-column: 1 / -1;
    }
}

@media (max-width: 768px) {
    .storage-overview-grid {
        grid-template-columns: 1fr;
    }
    
    .storage-metrics-grid {
        grid-template-columns: 1fr;
    }
    
    .analytics-grid {
        grid-template-columns: 1fr;
    }
}

.security-status-indicator {
    color: var(--accent-green);
    font-size: 1.2rem;
}

.security-actions {
    margin-top: var(--spacing-lg);
    text-align: center;
}

/* Process Table */
.process-table-container {
    background: var(--glass-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.table-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
    background: rgba(255, 255, 255, 0.02);
}

.table-filters {
    display: flex;
    gap: var(--spacing-md);
}

.filter-select {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    color: var(--text-primary);
    font-size: 0.85rem;
}

.search-box {
    position: relative;
    display: flex;
    align-items: center;
}

.search-box i {
    position: absolute;
    left: var(--spacing-md);
    color: var(--text-secondary);
}

.search-box input {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--spacing-sm) var(--spacing-md) var(--spacing-sm) 2.5rem;
    color: var(--text-primary);
    font-size: 0.9rem;
    width: 250px;
}

.search-box input::placeholder {
    color: var(--text-muted);
}

.table-actions {
    display: flex;
    gap: var(--spacing-sm);
}

.btn-icon {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-sm);
    border: none;
    background: var(--card-bg);
    color: var(--text-secondary);
    cursor: pointer;
    transition: var(--transition-fast);
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-icon:hover {
    background: var(--accent-bg);
    color: var(--text-primary);
}

.process-table {
    width: 100%;
    border-collapse: collapse;
}

.process-table th,
.process-table td {
    padding: var(--spacing-md);
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

.process-table th {
    background: rgba(255, 255, 255, 0.05);
    font-weight: 600;
    color: var(--text-primary);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.process-table td {
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.process-table tbody tr {
    transition: var(--transition-fast);
}

.process-table tbody tr:hover {
    background: rgba(255, 255, 255, 0.02);
}

.process-type, .power-mode {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.status {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-xl);
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status.running {
    background: rgba(16, 185, 129, 0.2);
    color: var(--accent-green);
    border: 1px solid var(--accent-green);
}

.status.queued {
    background: rgba(245, 158, 11, 0.2);
    color: var(--accent-orange);
    border: 1px solid var(--accent-orange);
}

.status.paused {
    background: rgba(239, 68, 68, 0.2);
    color: var(--accent-red);
    border: 1px solid var(--accent-red);
}

/* Loading Overlay */
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(10, 10, 15, 0.95);
    backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    opacity: 0;
    visibility: hidden;
    transition: var(--transition-smooth);
}

.loading-overlay.show {
    opacity: 1;
    visibility: visible;
}

.loading-spinner {
    text-align: center;
    color: var(--text-primary);
}

.spinner {
    width: 50px;
    height: 50px;
    border: 3px solid rgba(255, 255, 255, 0.1);
    border-top: 3px solid var(--accent-blue);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto var(--spacing-md);
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 1200px) {
    .scheduler-grid,
    .filesystem-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
    }
    
    .sidebar.show {
        transform: translateX(0);
    }
    
    .main-content {
        margin-left: 0;
    }
    
    .dashboard-content {
        padding: var(--spacing-md);
    }
    
    .metrics-grid {
        grid-template-columns: 1fr;
    }
    
    .top-header {
        padding: var(--spacing-md);
        flex-direction: column;
        gap: var(--spacing-md);
    }
    
    .header-right {
        width: 100%;
        justify-content: space-between;
    }
    
    .quick-stats {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .search-box input {
        width: 200px;
    }
}

@media (max-width: 480px) {
    .metrics-grid {
        grid-template-columns: 1fr;
    }
    
    .quick-stats {
        grid-template-columns: 1fr;
    }
    
    .table-controls {
        flex-direction: column;
        gap: var(--spacing-md);
    }
    
    .search-box input {
        width: 100%;
    }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--primary-bg);
}

::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: var(--radius-sm);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
}

/* Selection */
::selection {
    background: rgba(0, 212, 255, 0.3);
    color: var(--text-primary);
}

/* Focus States */
button:focus,
input:focus,
select:focus {
    outline: 2px solid var(--accent-blue);
    outline-offset: 2px;
}

/* Print Styles */
@media print {
    .sidebar,
    .header-actions,
    .section-actions {
        display: none;
    }
    
    .main-content {
        margin-left: 0;
    }
    
    .section {
        break-inside: avoid;
    }
}

/* Security Section Styles */
.security-overview {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
}

.security-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--spacing-lg);
}

.security-card {
    background: var(--glass-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    transition: var(--transition-smooth);
    position: relative;
    overflow: hidden;
}

.security-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--gradient-primary);
    transform: scaleX(0);
    transition: var(--transition-smooth);
}

.security-card:hover::before {
    transform: scaleX(1);
}

.security-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

.security-card .status-indicator.safe {
    color: var(--accent-green);
}

.security-card .status-indicator.warning {
    color: var(--accent-orange);
}

.security-card .status-indicator.danger {
    color: var(--accent-red);
}

.security-card .status-indicator.active {
    color: var(--accent-blue);
}

.threat-level {
    text-align: center;
    margin-bottom: var(--spacing-lg);
}

.threat-gauge {
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-sm);
    overflow: hidden;
    margin-bottom: var(--spacing-sm);
}

.gauge-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-green), var(--accent-orange), var(--accent-red));
    border-radius: var(--radius-sm);
    transition: var(--transition-smooth);
}

.threat-text {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--accent-green);
}

.threat-stats, .encryption-stats, .access-stats, .audit-stats {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.threat-stats .stat {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-sm);
    background: rgba(255, 255, 255, 0.02);
    border-radius: var(--radius-sm);
}

.threat-stats .label {
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.threat-stats .value {
    color: var(--text-primary);
    font-weight: 600;
}

.metric-value.warning {
    color: var(--accent-orange);
}

/* Security Timeline */
.security-timeline {
    background: var(--glass-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
}

.timeline-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
    padding-bottom: var(--spacing-md);
    border-bottom: 1px solid var(--border-color);
}

.timeline-header h3 {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    color: var(--text-primary);
    font-size: 1.1rem;
}

.timeline-content {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.timeline-item {
    display: flex;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    transition: var(--transition-fast);
    position: relative;
}

.timeline-item:hover {
    background: rgba(255, 255, 255, 0.02);
}

.timeline-item::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    border-radius: var(--radius-sm);
    transition: var(--transition-fast);
}

.timeline-item.success::before {
    background: var(--accent-green);
}

.timeline-item.warning::before {
    background: var(--accent-orange);
}

.timeline-item.info::before {
    background: var(--accent-blue);
}

.timeline-item.danger::before {
    background: var(--accent-red);
}

.timeline-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    transition: var(--transition-fast);
}

.timeline-item.success .timeline-icon {
    background: rgba(16, 185, 129, 0.2);
    color: var(--accent-green);
}

.timeline-item.warning .timeline-icon {
    background: rgba(245, 158, 11, 0.2);
    color: var(--accent-orange);
}

.timeline-item.info .timeline-icon {
    background: rgba(0, 212, 255, 0.2);
    color: var(--accent-blue);
}

.timeline-item.danger .timeline-icon {
    background: rgba(239, 68, 68, 0.2);
    color: var(--accent-red);
}

.timeline-content-item {
    flex: 1;
    min-width: 0;
}

.timeline-content-item h4 {
    color: var(--text-primary);
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: var(--spacing-xs);
}

.timeline-content-item p {
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.4;
    margin-bottom: var(--spacing-xs);
}

.timestamp {
    color: var(--text-muted);
    font-size: 0.8rem;
    font-style: italic;
}

/* Responsive adjustments for security section */
@media (max-width: 1200px) {
    .security-cards {
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    }
}

@media (max-width: 768px) {
    .security-cards {
        grid-template-columns: 1fr;
    }
    
    .timeline-item {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .timeline-icon {
        align-self: flex-start;
    }
}

/* Responsive Design - Updated for full width */
@media (max-width: 1200px) {
    .scheduler-grid-full {
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    }
    
    .metrics-grid {
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    }
}

@media (max-width: 768px) {
    .dashboard-content-full {
        padding: var(--spacing-md);
    }
    
    .metrics-grid {
        grid-template-columns: 1fr;
    }
    
    .top-header {
        padding: var(--spacing-md);
        flex-direction: column;
        gap: var(--spacing-md);
    }
    
    .header-right {
        width: 100%;
        justify-content: space-between;
    }
    
    .scheduler-grid-full {
        grid-template-columns: 1fr;
    }
    
    .quick-stats {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .search-box input {
        width: 200px;
    }
    
    .security-cards {
        grid-template-columns: 1fr;
    }
    
    .timeline-item {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .timeline-icon {
        align-self: flex-start;
    }
}

@media (max-width: 480px) {
    .metrics-grid {
        grid-template-columns: 1fr;
    }
    
    .quick-stats {
        grid-template-columns: 1fr;
    }
    
    .table-controls {
        flex-direction: column;
        gap: var(--spacing-md);
    }
    
    .search-box input {
        width: 100%;
    }
    
    .security-cards {
        grid-template-columns: 1fr;
    }
    
    .header-actions {
        flex-wrap: wrap;
        gap: var(--spacing-sm);
    }
}

/* Tab Navigation Styles */
.tab-navigation {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border-color);
    padding: 0 var(--spacing-xl);
    position: sticky;
    top: 80px;
    z-index: 40;
}

.tab-container {
    display: flex;
    gap: 0;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
}

.tab-container::-webkit-scrollbar {
    display: none;
}

.tab-btn {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-md) var(--spacing-lg);
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    transition: var(--transition-smooth);
    position: relative;
    white-space: nowrap;
    font-size: 0.9rem;
    font-weight: 500;
    border-radius: var(--radius-md) var(--radius-md) 0 0;
    margin-bottom: -1px;
}

.tab-btn::before {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--accent-blue);
    transform: scaleX(0);
    transition: var(--transition-smooth);
}

.tab-btn:hover {
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-primary);
}

.tab-btn.active {
    background: var(--card-bg);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    border-bottom: 1px solid var(--card-bg);
}

.tab-btn.active::before {
    transform: scaleX(1);
}

.tab-btn i {
    font-size: 1rem;
}

/* Tab Content Styles */
.tab-content-container {
    position: relative;
    min-height: calc(100vh - 200px);
}

.tab-content {
    display: none;
    padding: var(--spacing-xl);
    animation: fadeIn 0.3s ease-in-out;
}

.tab-content.active {
    display: block;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Component Header Styles */
.component-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--spacing-xl);
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
}

.component-header h2 {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    font-size: 1.5rem;
    font-weight: 600;
    background: var(--gradient-secondary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.component-actions {
    display: flex;
    gap: var(--spacing-md);
}

/* Modal Styles */
.modal {
    display: none;
    position: fixed;
    z-index: 10000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(5px);
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.3s ease-in-out;
}

.modal-content {
    background: var(--card-bg);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color);
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
    width: 90%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
    animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
    from {
        transform: translateY(30px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
    margin: 0;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.modal-close {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 1.5rem;
    cursor: pointer;
    padding: var(--spacing-xs);
    border-radius: var(--border-radius);
    transition: var(--transition-smooth);
}

.modal-close:hover {
    background: rgba(255, 255, 255, 0.1);
    color: var(--text-primary);
}

.modal-body {
    padding: var(--spacing-lg);
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: var(--spacing-md);
    padding: var(--spacing-lg);
    border-top: 1px solid var(--border-color);
}

.form-group {
    margin-bottom: var(--spacing-lg);
}

.form-group label {
    display: block;
    color: var(--text-primary);
    font-weight: 500;
    margin-bottom: var(--spacing-xs);
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: var(--spacing-md);
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    color: var(--text-primary);
    font-size: 0.9rem;
    transition: var(--transition-smooth);
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    outline: none;
    border-color: var(--accent-blue);
    box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2);
}

.form-group textarea {
    min-height: 80px;
    resize: vertical;
}

.form-group input[type="range"] {
    margin-bottom: var(--spacing-xs);
}

#priority-value {
    display: inline-block;
    background: var(--accent-blue);
    color: white;
    padding: 2px 8px;
    border-radius: var(--border-radius);
    font-size: 0.8rem;
    font-weight: 600;
    margin-left: var(--spacing-sm);
}

/* Process Table Styles */
.process-type {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
}

.priority-badge {
    padding: 2px 8px;
    border-radius: var(--border-radius);
    font-size: 0.8rem;
    font-weight: 600;
}

.priority-high {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
    border: 1px solid #ef4444;
}

.priority-medium {
    background: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
    border: 1px solid #f59e0b;
}

.priority-low {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
    border: 1px solid #10b981;
}

.status {
    padding: 4px 8px;
    border-radius: var(--border-radius);
    font-size: 0.8rem;
    font-weight: 600;
}

.status-running {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
    border: 1px solid #10b981;
}

.status-queued {
    background: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
    border: 1px solid #f59e0b;
}

.power-mode {
    font-size: 0.8rem;
    color: var(--text-secondary);
    text-transform: capitalize;
}

/* Responsive Design - Updated for tab layout */
@media (max-width: 768px) {
    .tab-container {
        padding: 0 var(--spacing-md);
    }
    
    .tab-btn span {
        display: none;
    }
    
    .tab-btn {
        padding: var(--spacing-md);
    }
    
    .modal-content {
        width: 95%;
        margin: var(--spacing-lg);
    }
    
    .modal-footer {
        flex-direction: column;
    }
    
    .modal-footer button {
        width: 100%;
    }
}'''

    def _generate_javascript(self) -> str:
        """Generate JavaScript for dashboard functionality"""
        return '''// Enhanced Decentralized AI Node OS - Modern Dashboard JavaScript

class EnhancedDashboard {
    constructor() {
        this.charts = {};
        this.updateInterval = 3000; // Changed to 3 seconds for smoother experience
        this.isLoading = false;
        this.theme = 'dark';
        this.notifications = [];
        this.sidebarCollapsed = false;
        this.updatesPaused = false; // Add pause functionality
        this.lastUpdateTime = 0; // Track last update
        this.animationQueue = []; // Queue for smooth animations
        
        this.initializeComponents();
        this.initializeCharts();
        this.bindEventListeners();
        this.startDataUpdates();
        this.showWelcomeNotification();
        this.updateProcessTable();
    }

    initializeComponents() {
        // Initialize theme
        this.applyTheme();
        
        // Hide loading overlay
        setTimeout(() => {
            this.hideLoading();
        }, 1000);
        
        // Initialize tooltips
        this.initializeTooltips();
        
        // Setup intersection observer for animations
        this.setupScrollAnimations();
    }

    initializeCharts() {
        // Performance Chart with enhanced styling
        const perfCtx = document.getElementById('performance-chart')?.getContext('2d');
        if (perfCtx) {
        this.charts.performance = new Chart(perfCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Performance Score',
                    data: [],
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#00d4ff',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }, {
                        label: 'CPU Usage',
                        data: [],
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3
                    }, {
                        label: 'Memory Usage',
                        data: [],
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3
                }]
            },
            options: {
                responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    },
                plugins: {
                    legend: { 
                            labels: { 
                                color: '#ffffff',
                                usePointStyle: true,
                                padding: 20
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#00d4ff',
                            borderWidth: 1
                    }
                },
                scales: {
                    x: { 
                            ticks: { color: '#b8bcc8' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: { 
                            ticks: { color: '#b8bcc8' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            beginAtZero: true,
                            max: 100
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeInOutQuart'
                }
            }
        });
        }

        // Enhanced Storage Donut Chart
        const storageDonutCtx = document.getElementById('storage-donut-chart')?.getContext('2d');
        if (storageDonutCtx) {
            this.charts.storageDonut = new Chart(storageDonutCtx, {
                type: 'doughnut',
                data: {
                    labels: ['System Files', 'AI Models', 'User Data', 'Cache'],
                    datasets: [{
                        data: [35, 45, 10, 10],
                        backgroundColor: [
                            '#00d4ff',
                            '#8b5cf6',
                            '#10b981',
                            '#f59e0b'
                        ],
                        borderWidth: 0,
                        cutout: '75%',
                        spacing: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.9)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#00d4ff',
                            borderWidth: 1,
                            callbacks: {
                                label: function(context) {
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((context.parsed / total) * 100).toFixed(1);
                                    return context.label + ': ' + percentage + '%';
                                }
                            }
                        }
                    },
                    animation: {
                        duration: 2000,
                        easing: 'easeInOutQuart',
                        animateRotate: true,
                        animateScale: true
                    }
                }
            });
        }

        // File System Performance Chart
        const fsPerformanceCtx = document.getElementById('fs-performance-chart')?.getContext('2d');
        if (fsPerformanceCtx) {
            this.charts.fsPerformance = new Chart(fsPerformanceCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Read Speed (MB/s)',
                        data: [],
                        borderColor: '#00d4ff',
                        backgroundColor: 'rgba(0, 212, 255, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }, {
                        label: 'Write Speed (MB/s)',
                        data: [],
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    },
                    plugins: {
                        legend: { 
                            labels: { 
                                color: '#ffffff',
                                usePointStyle: true,
                                padding: 15
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#00d4ff',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        x: { 
                            ticks: { color: '#b8bcc8' },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        },
                        y: { 
                            ticks: { color: '#b8bcc8' },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            beginAtZero: true
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeInOutQuart'
                    }
                }
            });
        }

        // Storage Chart (Legacy - keep for backward compatibility)
        const storageCtx = document.getElementById('storage-chart')?.getContext('2d');
        if (storageCtx) {
        this.charts.storage = new Chart(storageCtx, {
            type: 'doughnut',
            data: {
                    labels: ['Used Space', 'Free Space', 'System Reserved'],
                datasets: [{
                        data: [45, 50, 5],
                        backgroundColor: [
                            '#f59e0b',
                            '#10b981',
                            '#6b7280'
                        ],
                        borderWidth: 0,
                        cutout: '70%'
                }]
            },
            options: {
                responsive: true,
                    maintainAspectRatio: false,
                plugins: {
                    legend: { 
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#00d4ff',
                            borderWidth: 1,
                            callbacks: {
                                label: function(context) {
                                    return context.label + ': ' + context.parsed + '%';
                                }
                            }
                        }
                    },
                    animation: {
                        duration: 1500,
                        easing: 'easeInOutQuart'
                }
            }
        });
        }
    }

    bindEventListeners() {
        // Theme toggle (moved to settings button)
        const settingsBtn = document.getElementById('settings-btn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.toggleTheme());
        }

        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // Pause/Resume button
        const pauseBtn = document.getElementById('pause-btn');
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => this.toggleUpdates());
        }

        // Fullscreen toggle
        const fullscreenBtn = document.getElementById('fullscreen-btn');
        if (fullscreenBtn) {
            fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
        }

        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.closest('.tab-btn').dataset.tab));
        });

        // Search functionality
        const processSearch = document.getElementById('process-search');
        if (processSearch) {
            processSearch.addEventListener('input', (e) => this.filterProcesses(e.target.value));
        }

        // Table filters
        const statusFilter = document.getElementById('status-filter');
        const typeFilter = document.getElementById('type-filter');
        if (statusFilter) statusFilter.addEventListener('change', () => this.applyTableFilters());
        if (typeFilter) typeFilter.addEventListener('change', () => this.applyTableFilters());

        // File System action buttons
        const analyzeStorageBtn = document.getElementById('analyze-storage');
        const searchFilesBtn = document.getElementById('search-files');
        const cleanupDiskBtn = document.getElementById('cleanup-disk');
        
        if (analyzeStorageBtn) {
            analyzeStorageBtn.addEventListener('click', () => this.analyzeStorage());
        }
        if (searchFilesBtn) {
            searchFilesBtn.addEventListener('click', () => this.searchFiles());
        }
        if (cleanupDiskBtn) {
            cleanupDiskBtn.addEventListener('click', () => this.cleanupDisk());
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));

        // Window resize handler
        window.addEventListener('resize', () => this.handleResize());
    }

    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        this.applyTheme();
        
        // Update toggle button icon (now settings button)
        const settingsBtn = document.getElementById('settings-btn');
        if (settingsBtn) {
            const icon = settingsBtn.querySelector('i');
            if (this.theme === 'dark') {
                icon.className = 'fas fa-cog';
                settingsBtn.setAttribute('title', 'Settings (Dark Mode)');
            } else {
                icon.className = 'fas fa-sun';
                settingsBtn.setAttribute('title', 'Settings (Light Mode)');
            }
        }
        
        this.showNotification('Theme changed to ' + this.theme + ' mode', 'info');
    }

    applyTheme() {
        const dashboard = document.getElementById('dashboard');
        if (dashboard) {
            dashboard.setAttribute('data-theme', this.theme);
        }
    }

    handleNavigation(e) {
        // Navigation removed - single page layout displays all sections
    }

    updateBreadcrumb(section) {
        // Breadcrumb removed - single page layout doesn't need navigation
    }

    refreshData() {
        this.showLoading();
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            const icon = refreshBtn.querySelector('i');
            icon.style.animation = 'spin 1s linear infinite';
            
            setTimeout(() => {
                icon.style.animation = '';
                this.hideLoading();
                this.showNotification('Data refreshed successfully', 'success');
            }, 1500);
        }
        
        this.updateAllData();
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            const icon = document.querySelector('#fullscreen-btn i');
            if (icon) icon.className = 'fas fa-compress';
        } else {
            document.exitFullscreen();
            const icon = document.querySelector('#fullscreen-btn i');
            if (icon) icon.className = 'fas fa-expand';
        }
    }

    handleKeyboardShortcuts(e) {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'r':
                    e.preventDefault();
                    this.refreshData();
                    break;
                case 'f':
                    e.preventDefault();
                    this.toggleFullscreen();
                    break;
                case 't':
                    e.preventDefault();
                    this.toggleTheme();
                    break;
                case 'p':
                    e.preventDefault();
                    this.toggleUpdates();
                    break;
                case '1':
                    e.preventDefault();
                    this.switchTab('overview');
                    break;
                case '2':
                    e.preventDefault();
                    this.switchTab('ai-scheduler');
                    break;
                case '3':
                    e.preventDefault();
                    this.switchTab('file-system');
                    break;
                case '4':
                    e.preventDefault();
                    this.switchTab('processes');
                    break;
                case '5':
                    e.preventDefault();
                    this.switchTab('security');
                    break;
            }
        }
    }

    handleResize() {
        // Update charts on resize
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.resize();
        });
        
        // Full-width layout - no sidebar handling needed
    }

    drawProgressRing(elementId, percentage, color = '#00d4ff', animated = true) {
        const canvas = document.querySelector(`#${elementId} canvas`);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 45;

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
        
        // Create gradient
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        gradient.addColorStop(0, color);
        gradient.addColorStop(1, this.lightenColor(color, 20));
        
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 8;
        ctx.lineCap = 'round';
        ctx.stroke();

        // Add glow effect
        ctx.shadowColor = color;
        ctx.shadowBlur = 10;
        ctx.stroke();
        
        // Update percentage text with animation
        const percentElement = document.querySelector(`#${elementId.replace('-ring', '-percent')}`);
        if (percentElement && animated) {
            this.animateNumber(percentElement, 0, percentage, 1000, '%');
        } else if (percentElement) {
            percentElement.textContent = `${percentage}%`;
        }
    }

    animateNumber(element, start, end, duration, suffix = '') {
        const startTime = performance.now();
        const updateNumber = (currentTime) => {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1);
            const currentValue = start + (end - start) * this.easeOutCubic(progress);
            
            element.textContent = Math.round(currentValue) + suffix;
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        };
        requestAnimationFrame(updateNumber);
    }

    easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    lightenColor(color, percent) {
        const num = parseInt(color.replace("#", ""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    }

    showNotification(message, type = 'info', duration = 3000) {
        const container = document.getElementById('notifications');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="${icons[type]}"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="margin-left: auto; background: none; border: none; color: inherit; cursor: pointer;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
    }

    showWelcomeNotification() {
        setTimeout(() => {
            this.showNotification('🌟 Welcome to Decentralized AI Node OS Dashboard!', 'success', 5000);
        }, 1500);
    }

    showLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('show');
            this.isLoading = true;
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('show');
            this.isLoading = false;
        }
    }

    initializeTooltips() {
        document.querySelectorAll('[title]').forEach(element => {
            element.addEventListener('mouseenter', this.showTooltip.bind(this));
            element.addEventListener('mouseleave', this.hideTooltip.bind(this));
        });
    }

    showTooltip(e) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = e.target.getAttribute('title');
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            z-index: 10000;
            pointer-events: none;
            backdrop-filter: blur(10px);
        `;
        
        document.body.appendChild(tooltip);
        
        const updatePosition = (e) => {
            tooltip.style.left = e.clientX + 10 + 'px';
            tooltip.style.top = e.clientY - 30 + 'px';
        };
        
        updatePosition(e);
        e.target.addEventListener('mousemove', updatePosition);
        e.target.tooltip = tooltip;
    }

    hideTooltip(e) {
        if (e.target.tooltip) {
            e.target.tooltip.remove();
            delete e.target.tooltip;
        }
    }

    setupScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.section, .metric-card').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });

        // Add CSS for animation
        const style = document.createElement('style');
        style.textContent = `
            .animate-in {
                opacity: 1 !important;
                transform: translateY(0) !important;
            }
        `;
        document.head.appendChild(style);
    }

    // Process creation functionality
    showProcessModal() {
        const modal = document.getElementById('process-modal');
        if (modal) {
            modal.style.display = 'flex';
            // Reset form
            document.getElementById('process-form').reset();
            document.getElementById('priority-value').textContent = '5';
        }
    }

    async createProcess() {
        const form = document.getElementById('process-form');
        const formData = new FormData(form);
        
        const processData = {
            name: formData.get('name'),
            type: formData.get('type'),
            priority: parseInt(formData.get('priority')),
            memory: parseInt(formData.get('memory')),
            args: formData.get('args').split('\\n').filter(arg => arg.trim())
        };

        if (!processData.name || !processData.type) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }

        try {
            this.showLoading();
            const response = await fetch('/api/processes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(processData)
            });

            const result = await response.json();
            
            if (response.ok) {
                this.hideLoading();
                this.closeProcessModal();
                this.showNotification(`✅ Process "${processData.name}" created successfully!`, 'success');
                // Refresh process list
                this.updateProcessTable();
            } else {
                throw new Error(result.error || 'Failed to create process');
            }
        } catch (error) {
            this.hideLoading();
            this.showNotification(`❌ Failed to create process: ${error.message}`, 'error');
        }
    }

    closeProcessModal() {
        const modal = document.getElementById('process-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    async updateProcessTable() {
        try {
            const data = await this.fetchSchedulerData();
            if (data && data.running_processes) {
                const tbody = document.getElementById('process-table-body');
                if (tbody) {
                    tbody.innerHTML = '';
                    
                    const processes = data.running_processes;
                    if (Object.keys(processes).length === 0) {
                        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: #888;">No active processes</td></tr>';
                    } else {
                        Object.entries(processes).forEach(([coreId, process]) => {
                            const row = document.createElement('tr');
                            const runtime = this.formatRuntime(process.actual_runtime || 0);
                            const statusClass = process.status === 'running' ? 'status-running' : 'status-queued';
                            
                            row.innerHTML = `
                                <td><input type="checkbox" data-process-id="${process.id}"></td>
                                <td>${process.id}</td>
                                <td><span class="process-type">${this.getProcessTypeIcon(process.type)} ${process.type}</span></td>
                                <td>Core ${coreId}</td>
                                <td><span class="priority-badge priority-${this.getPriorityClass(process.priority)}">${process.priority}</span></td>
                                <td><span class="power-mode">${process.power_state || 'balanced'}</span></td>
                                <td>${runtime}</td>
                                <td><span class="status ${statusClass}">Running</span></td>
                                <td>
                                    <button class="btn-icon" onclick="dashboard.pauseProcess('${process.id}')" title="Pause">
                                        <i class="fas fa-pause"></i>
                                    </button>
                                    <button class="btn-icon" onclick="dashboard.terminateProcess('${process.id}')" title="Terminate">
                                        <i class="fas fa-stop"></i>
                                    </button>
                                </td>
                            `;
                            tbody.appendChild(row);
                        });
                    }
                }
            }
        } catch (error) {
            console.error('Failed to update process table:', error);
        }
    }

    getProcessTypeIcon(type) {
        const icons = {
            'ai_inference': '🧠',
            'blockchain_validator': '⛓️',
            'data_processing': '📊',
            'network_node': '🌐',
            'smart_contract': '📜',
            'system': '⚙️',
            'user': '👤'
        };
        return icons[type] || '💻';
    }

    getPriorityClass(priority) {
        if (priority >= 8) return 'high';
        if (priority >= 5) return 'medium';
        return 'low';
    }

    formatRuntime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    }

    async pauseProcess(processId) {
        this.showNotification(`Pausing process ${processId}...`, 'info');
        // Implementation would depend on your process manager
    }

    async terminateProcess(processId) {
        if (confirm(`Are you sure you want to terminate process ${processId}?`)) {
            this.showNotification(`Terminating process ${processId}...`, 'info');
            // Implementation would depend on your process manager
        }
    }

    async fetchSystemData() {
        try {
            const response = await fetch('/api/system');
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Failed to fetch system data:', error);
            this.showNotification('Failed to fetch system data', 'error');
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
        if (!data || this.updatesPaused) return;

        // Throttle updates to prevent performance issues
        const now = Date.now();
        if (now - this.lastUpdateTime < 1000) return; // Minimum 1 second between updates
        this.lastUpdateTime = now;

        // Update progress rings with smoother animations and stagger them
        setTimeout(() => this.drawProgressRing('cpu-ring', data.cpu_usage, '#f59e0b', true), 0);
        setTimeout(() => this.drawProgressRing('memory-ring', data.memory_usage, '#8b5cf6', true), 100);
        setTimeout(() => this.drawProgressRing('disk-ring', data.disk_usage, '#10b981', true), 200);
        setTimeout(() => this.drawProgressRing('network-ring', data.network_activity, '#00d4ff', true), 300);

        // Update trend indicators smoothly
        this.smoothUpdateTrendIndicator('cpu-trend', Math.random() > 0.5);
        this.smoothUpdateTrendIndicator('memory-trend', Math.random() > 0.5);
        this.smoothUpdateTrendIndicator('disk-trend', Math.random() > 0.5);
        this.smoothUpdateTrendIndicator('network-trend', Math.random() > 0.5);

        // Update detailed metrics with smooth transitions
        this.smoothUpdateText('cpu-cores', `${Math.floor(data.cpu_usage / 15)}/8`);
        this.smoothUpdateText('cpu-temp', `${(40 + data.cpu_usage * 0.3).toFixed(0)}°C`);
        this.smoothUpdateText('memory-used', `${(data.memory_usage * 0.16).toFixed(1)} GB`);
        this.smoothUpdateText('disk-used', `${(data.disk_usage * 0.02).toFixed(1)} TB`);
        this.smoothUpdateText('network-down', `${(data.network_activity * 2.5).toFixed(1)} MB/s`);
        this.smoothUpdateText('network-up', `${(data.network_activity * 0.8).toFixed(1)} MB/s`);

        // Update quick stats with fade transitions
        this.smoothUpdateText('power-consumption', `${(400 + data.cpu_usage * 2).toFixed(0)}W`);
        this.smoothUpdateText('system-temp', `${(55 + data.cpu_usage * 0.2).toFixed(0)}°C`);
        this.smoothUpdateText('performance-score', `${(85 + Math.random() * 10).toFixed(0)}%`);

        // Update uptime smoothly
        this.updateUptimeSmooth(data.uptime);
    }

    smoothUpdateTrendIndicator(elementId, isUp) {
        const element = document.getElementById(elementId);
        if (element) {
            const icon = element.querySelector('i');
            const currentIsUp = icon.className.includes('arrow-up');
            
            // Only update if direction changed
            if (currentIsUp !== isUp) {
                element.style.transition = 'all 0.3s ease';
                element.style.transform = 'scale(0.8)';
                
                setTimeout(() => {
                    if (isUp) {
                        icon.className = 'fas fa-arrow-up';
                        element.style.color = '#10b981';
                    } else {
                        icon.className = 'fas fa-arrow-down';
                        element.style.color = '#ef4444';
                    }
                    element.style.transform = 'scale(1)';
                }, 150);
            }
        }
    }

    smoothUpdateText(id, text) {
        const element = document.getElementById(id);
        if (element && element.textContent !== text) {
            // Fade out, change text, fade in
            element.style.transition = 'opacity 0.3s ease';
            element.style.opacity = '0.7';
            
            setTimeout(() => {
                element.textContent = text;
                element.style.opacity = '1';
            }, 150);
        }
    }

    updateUptimeSmooth(uptime) {
        const hours = Math.floor(uptime / 3600);
        const minutes = Math.floor((uptime % 3600) / 60);
        const seconds = Math.floor(uptime % 60);
        const uptimeElement = document.getElementById('uptime');
        if (uptimeElement) {
            uptimeElement.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    updateSchedulerMetrics(data) {
        if (!data || this.updatesPaused) return;

        // Update learning info with smooth transitions
        this.smoothUpdateText('learning-mode', data.learning_mode || 'Adaptive');
        this.smoothUpdateText('prediction-accuracy', `${(data.prediction_accuracy || 94.7).toFixed(1)}%`);
        this.smoothUpdateText('adaptations', data.adaptation_count || 1247);
        this.smoothUpdateText('total-scheduled', data.total_scheduled || 342);
        this.smoothUpdateText('queue-length', data.queue_length || 12);
        
        // Update process table
        this.updateProcessTable();

        // Update performance chart with smooth animation
        const now = new Date().toLocaleTimeString();
        const performanceScore = data.avg_performance_score || (85 + Math.random() * 15);
        const cpuUsage = data.cpu_usage || Math.random() * 100;
        const memoryUsage = data.memory_usage || Math.random() * 100;
        
        if (this.charts.performance) {
            // Limit data points to prevent performance issues
            if (this.charts.performance.data.labels.length > 15) {
                this.charts.performance.data.labels.shift();
                this.charts.performance.data.datasets.forEach(dataset => dataset.data.shift());
            }
            
            this.charts.performance.data.labels.push(now);
            this.charts.performance.data.datasets[0].data.push(performanceScore);
            this.charts.performance.data.datasets[1].data.push(cpuUsage);
            this.charts.performance.data.datasets[2].data.push(memoryUsage);
            
            // Use smooth animation mode
            this.charts.performance.update('active');
        }

        // Update learning progress with smooth animation
        const progressFill = document.getElementById('learning-progress');
        if (progressFill) {
            const progress = 70 + Math.random() * 20;
            progressFill.style.transition = 'width 0.8s ease';
            progressFill.style.width = progress + '%';
        }
    }

    updateFileSystemMetrics(data) {
        if (!data || this.updatesPaused) return;

        // Update enhanced storage donut chart
        if (this.charts.storageDonut) {
            const systemFiles = 30 + Math.random() * 10;
            const aiModels = 40 + Math.random() * 10;
            const userData = 8 + Math.random() * 5;
            const cache = 3 + Math.random() * 4;
            
            this.charts.storageDonut.data.datasets[0].data = [systemFiles, aiModels, userData, cache];
            this.charts.storageDonut.update('active');
            
            // Update storage breakdown values
            this.smoothUpdateText('system-files-size', `${(systemFiles * 12).toFixed(0)} GB`);
            this.smoothUpdateText('ai-models-size', `${(aiModels * 12).toFixed(0)} GB`);
            this.smoothUpdateText('user-data-size', `${(userData * 12).toFixed(0)} GB`);
            this.smoothUpdateText('cache-size', `${(cache * 12).toFixed(0)} GB`);
            
            // Update total used amount
            const totalUsed = (systemFiles + aiModels + userData + cache) * 0.12;
            this.smoothUpdateText('storage-used-amount', totalUsed.toFixed(1));
        }

        // Update file system performance chart
        if (this.charts.fsPerformance) {
            const now = new Date().toLocaleTimeString();
            const readSpeed = 120 + Math.random() * 80;
            const writeSpeed = 80 + Math.random() * 60;
            
            // Limit data points
            if (this.charts.fsPerformance.data.labels.length > 10) {
                this.charts.fsPerformance.data.labels.shift();
                this.charts.fsPerformance.data.datasets.forEach(dataset => dataset.data.shift());
            }
            
            this.charts.fsPerformance.data.labels.push(now);
            this.charts.fsPerformance.data.datasets[0].data.push(readSpeed);
            this.charts.fsPerformance.data.datasets[1].data.push(writeSpeed);
            this.charts.fsPerformance.update('active');
        }

        // Update health score ring
        this.drawHealthRing('health-ring', 90 + Math.random() * 8, '#10b981');

        // Update fragmentation fill
        const fragmentation = data.fragmentation || (1.5 + Math.random() * 2);
        const fragFill = document.getElementById('fragmentation-fill');
        if (fragFill) {
            const fillPercentage = (fragmentation / 10) * 100; // Scale to 0-100%
            fragFill.style.width = `${Math.min(fillPercentage, 100)}%`;
        }

        // Update access pattern frequencies with realistic data
        this.updateAccessPatterns();

        // Legacy storage chart update
        const usedPercentage = data.storage_utilization || (40 + Math.random() * 20);
        const reservedPercentage = 5;
        const freePercentage = 100 - usedPercentage - reservedPercentage;
        
        if (this.charts.storage) {
            this.charts.storage.data.datasets[0].data = [usedPercentage, freePercentage, reservedPercentage];
            this.charts.storage.update('active');
        }
    }

    drawHealthRing(elementId, percentage, color = '#10b981') {
        const canvas = document.querySelector(`#${elementId} canvas`);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 45;

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Background circle
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.lineWidth = 8;
        ctx.stroke();

        // Health arc
        const progress = (percentage / 100) * 2 * Math.PI;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, progress);
        
        // Create gradient based on health score
        let gradientColor = color;
        if (percentage >= 90) gradientColor = '#10b981'; // Green
        else if (percentage >= 70) gradientColor = '#f59e0b'; // Orange
        else gradientColor = '#ef4444'; // Red
        
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        gradient.addColorStop(0, gradientColor);
        gradient.addColorStop(1, this.lightenColor(gradientColor, 20));
        
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 8;
        ctx.lineCap = 'round';
        ctx.stroke();

        // Add glow effect
        ctx.shadowColor = gradientColor;
        ctx.shadowBlur = 10;
        ctx.stroke();
        
        // Update health score text
        const scoreElement = document.getElementById('health-score');
        if (scoreElement) {
            this.animateNumber(scoreElement, parseInt(scoreElement.textContent) || 0, Math.round(percentage), 1000);
        }
    }

    updateAccessPatterns() {
        // Simulate realistic access pattern changes
        const patterns = [
            { element: null, base: 1200, variance: 200 },
            { element: null, base: 500, variance: 100 },
            { element: null, base: 10, variance: 5 }
        ];
        
        const patternElements = document.querySelectorAll('.pattern-frequency');
        patternElements.forEach((el, index) => {
            if (patterns[index]) {
                const frequency = patterns[index].base + (Math.random() - 0.5) * patterns[index].variance;
                el.textContent = `${Math.round(frequency)} accesses/h`;
            }
        });
    }

    updateSecurityMetrics(data) {
        if (!data || this.updatesPaused) return;

        // Update security section elements with smooth transitions
        this.smoothUpdateText('security-encrypted-files', data.encrypted_files || 1542);
        this.smoothUpdateText('security-active-keys', data.active_encryption_keys || 8);
        this.smoothUpdateText('security-success-rate', `${(data.success_rate || 99.8).toFixed(1)}%`);
        this.smoothUpdateText('security-blocked-users', data.blocked_users || 3);
        this.smoothUpdateText('security-last-scan', '2 min ago');
        
        // Update legacy elements for backward compatibility (if they exist)
        this.smoothUpdateText('encrypted-files', data.encrypted_files || 1542);
        this.smoothUpdateText('active-keys', data.active_encryption_keys || 8);
        this.smoothUpdateText('security-success', `${(data.success_rate || 99.8).toFixed(1)}%`);
        this.smoothUpdateText('blocked-users', data.blocked_users || 3);
        this.smoothUpdateText('last-scan', '2 min ago');

        // Update file system stats with smooth transitions
        this.smoothUpdateText('total-files', data.total_files || 2847);
        this.smoothUpdateText('total-directories', data.total_directories || 156);
        this.smoothUpdateText('cache-hit-rate', `${(data.cache_hit_rate || 94.2).toFixed(1)}%`);
        this.smoothUpdateText('fragmentation', `${(data.fragmentation || 2.1).toFixed(1)}%`);
        this.smoothUpdateText('io-operations', `${data.io_operations || 1248}/s`);
    }

    filterProcesses(searchTerm) {
        const rows = document.querySelectorAll('#process-table-body tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const shouldShow = text.includes(searchTerm.toLowerCase());
            row.style.display = shouldShow ? '' : 'none';
        });
    }

    applyTableFilters() {
        const statusFilter = document.getElementById('status-filter')?.value;
        const typeFilter = document.getElementById('type-filter')?.value;
        const rows = document.querySelectorAll('#process-table-body tr');
        
        rows.forEach(row => {
            const statusCell = row.querySelector('td:nth-child(8)');
            const typeCell = row.querySelector('td:nth-child(3)');
            
            let shouldShow = true;
            
            if (statusFilter && statusFilter !== 'all') {
                const status = statusCell?.textContent.toLowerCase();
                shouldShow = shouldShow && status?.includes(statusFilter);
            }
            
            if (typeFilter && typeFilter !== 'all') {
                const type = typeCell?.textContent.toLowerCase();
                shouldShow = shouldShow && type?.includes(typeFilter);
            }
            
            row.style.display = shouldShow ? '' : 'none';
        });
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
                    <td><input type="checkbox"></td>
                    <td>${process.id || 'N/A'}</td>
                    <td><span class="process-type">${this.getProcessTypeIcon(process.type)} ${process.type || 'Unknown'}</span></td>
                    <td>Core ${coreId}</td>
                    <td>${process.priority || 'N/A'}</td>
                    <td><span class="power-mode">${this.getPowerModeIcon(process.power_state)} ${process.power_state || 'N/A'}</span></td>
                    <td>${this.formatRuntime(process.actual_runtime || 0)}</td>
                    <td><span class="status running">🟢 Running</span></td>
                    <td>
                        <button class="btn-icon" onclick="dashboard.pauseProcess('${process.id}')" title="Pause">
                            <i class="fas fa-pause"></i>
                        </button>
                        <button class="btn-icon" onclick="dashboard.stopProcess('${process.id}')" title="Stop">
                            <i class="fas fa-stop"></i>
                        </button>
                    </td>
                `;
                
                // Add hover effects
                row.addEventListener('mouseenter', () => {
                    row.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
                });
                row.addEventListener('mouseleave', () => {
                    row.style.backgroundColor = '';
                });
            });
        }

        // Add queued processes
        if (schedulerData.queue_length > 0) {
            for (let i = 0; i < Math.min(5, schedulerData.queue_length); i++) {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td><input type="checkbox"></td>
                    <td>queued_${i + 1}</td>
                    <td><span class="process-type">⏳ Queued Process</span></td>
                    <td>-</td>
                    <td>${50 + Math.floor(Math.random() * 50)}</td>
                    <td>-</td>
                    <td>-</td>
                    <td><span class="status queued">🟡 Queued</span></td>
                    <td>
                        <button class="btn-icon" onclick="dashboard.prioritizeProcess('queued_${i + 1}')" title="Prioritize">
                            <i class="fas fa-arrow-up"></i>
                        </button>
                        <button class="btn-icon" onclick="dashboard.cancelProcess('queued_${i + 1}')" title="Cancel">
                            <i class="fas fa-times"></i>
                        </button>
                    </td>
                `;
            }
        }

        // Show empty state if no processes
        if (tbody.children.length === 0) {
            const row = tbody.insertRow();
            row.innerHTML = '<td colspan="9" style="text-align: center; color: #888; padding: 2rem;">No active processes</td>';
        }
    }

    // Process management methods
    pauseProcess(processId) {
        this.showNotification(`Process ${processId} paused`, 'info');
    }

    stopProcess(processId) {
        this.showNotification(`Process ${processId} stopped`, 'warning');
    }

    prioritizeProcess(processId) {
        this.showNotification(`Process ${processId} prioritized`, 'success');
    }

    cancelProcess(processId) {
        this.showNotification(`Process ${processId} cancelled`, 'warning');
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
        if (this.isLoading || this.updatesPaused) return;

        // Prevent concurrent updates
        if (this.updateInProgress) return;
        this.updateInProgress = true;

        try {
            // Use Promise.allSettled to prevent one failed request from breaking all updates
            const results = await Promise.allSettled([
                this.fetchSystemData(),
                this.fetchSchedulerData(),
                this.fetchFileSystemData(),
                this.fetchSecurityData()
            ]);

            // Process results even if some failed
            const [systemResult, schedulerResult, fileSystemResult, securityResult] = results;

            if (systemResult.status === 'fulfilled' && systemResult.value) {
                this.updateSystemMetrics(systemResult.value);
            }

            if (schedulerResult.status === 'fulfilled' && schedulerResult.value) {
                this.updateSchedulerMetrics(schedulerResult.value);
                this.updateProcessTable(schedulerResult.value);
            }

            if (fileSystemResult.status === 'fulfilled' && fileSystemResult.value) {
                this.updateFileSystemMetrics(fileSystemResult.value);
            }

            if (securityResult.status === 'fulfilled' && securityResult.value) {
                this.updateSecurityMetrics(securityResult.value);
            }

            // Check for any failures and show warning
            const failures = results.filter(result => result.status === 'rejected');
            if (failures.length > 0) {
                console.warn('Some data updates failed:', failures);
                // Don't show notification for every failure to avoid spam
            }

        } catch (error) {
            console.error('Critical error updating data:', error);
            this.showNotification('Error updating dashboard data', 'error');
        } finally {
            this.updateInProgress = false;
        }
    }

    startDataUpdates() {
        // Initial update with delay to allow UI to settle
        setTimeout(() => {
            this.updateAllData();
        }, 1000);

        // Set up periodic updates with improved timing
        this.updateIntervalId = setInterval(() => {
            if (!this.isLoading && !this.updatesPaused && !document.hidden) {
                this.updateAllData();
            }
        }, this.updateInterval);

        // Pause updates when page is hidden (performance optimization)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                // Resume updates when page becomes visible again
                setTimeout(() => {
                    this.resumeUpdates();
                }, 500);
            }
        });
    }

    // Add pause/resume functionality for better performance
    pauseUpdates() {
        this.updatesPaused = true;
        this.showNotification('Dashboard updates paused', 'info');
    }

    resumeUpdates() {
        this.updatesPaused = false;
        this.showNotification('Dashboard updates resumed', 'success');
        this.updateAllData(); // Immediate update when resuming
    }

    toggleUpdates() {
        if (this.updatesPaused) {
            this.resumeUpdates();
        } else {
            this.pauseUpdates();
        }
        
        // Update pause button icon
        const pauseBtn = document.getElementById('pause-btn');
        if (pauseBtn) {
            const icon = pauseBtn.querySelector('i');
            const title = this.updatesPaused ? 'Resume Updates' : 'Pause Updates';
            icon.className = this.updatesPaused ? 'fas fa-play' : 'fas fa-pause';
            pauseBtn.setAttribute('title', title);
        }
    }

    // Tab switching functionality
    switchTab(tabName) {
        // Remove active class from all tabs and content
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        
        // Add active class to selected tab and content
        const selectedTab = document.querySelector(`[data-tab="${tabName}"]`);
        const selectedContent = document.getElementById(`${tabName}-tab`);
        
        if (selectedTab && selectedContent) {
            selectedTab.classList.add('active');
            selectedContent.classList.add('active');
            
            // Show notification about tab switch
            this.showNotification(`Switched to ${selectedTab.textContent.trim()}`, 'info', 1500);
            
            // Refresh charts when switching to relevant tabs
            setTimeout(() => {
                if (tabName === 'ai-scheduler' && this.charts.performance) {
                    this.charts.performance.resize();
                }
                if (tabName === 'file-system') {
                    if (this.charts.storage) this.charts.storage.resize();
                    if (this.charts.storageDonut) this.charts.storageDonut.resize();
                    if (this.charts.fsPerformance) this.charts.fsPerformance.resize();
                }
            }, 100);
        }
    }

    // File System Action Methods
    analyzeStorage() {
        this.showLoading();
        this.showNotification('🔍 Analyzing storage patterns...', 'info');
        
        // Simulate analysis process
        setTimeout(() => {
            this.hideLoading();
            this.showNotification('✅ Storage analysis complete! Optimization recommendations available.', 'success', 4000);
            
            // Update analytics with "analyzed" data
            this.updateFileSystemMetrics({
                fragmentation: 1.8 + Math.random() * 1.5,
                storage_utilization: 65 + Math.random() * 15
            });
        }, 2000);
    }

    searchFiles() {
        this.showNotification('🔍 Opening advanced file search interface...', 'info');
        
        // In a real implementation, this would open a search modal
        setTimeout(() => {
            this.showNotification('📁 File search interface would open here in full implementation.', 'info', 3000);
        }, 500);
    }

    cleanupDisk() {
        this.showLoading();
        this.showNotification('🧹 Starting disk cleanup...', 'info');
        
        // Simulate cleanup process
        setTimeout(() => {
            this.hideLoading();
            const spaceFreed = (Math.random() * 2 + 0.5).toFixed(1);
            this.showNotification(`✅ Cleanup complete! ${spaceFreed} GB of space freed.`, 'success', 4000);
            
            // Update storage visualization to show freed space
            if (this.charts.storageDonut) {
                const currentData = this.charts.storageDonut.data.datasets[0].data;
                // Reduce cache size to simulate cleanup
                currentData[3] = Math.max(currentData[3] - 2, 1);
                this.charts.storageDonut.update('active');
            }
        }, 3000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new EnhancedDashboard();
    
    // Add event listener for New Process button
    const newProcessBtn = document.querySelector('.btn-secondary');
    if (newProcessBtn && newProcessBtn.textContent.includes('New Process')) {
        newProcessBtn.onclick = () => window.dashboard.showProcessModal();
    }
    
    // Add event listener for priority slider
    const prioritySlider = document.getElementById('process-priority');
    if (prioritySlider) {
        prioritySlider.addEventListener('input', (e) => {
            document.getElementById('priority-value').textContent = e.target.value;
        });
    }
});

// Global functions for modal
function closeProcessModal() {
    if (window.dashboard) {
        window.dashboard.closeProcessModal();
    }
}

function createProcess() {
    if (window.dashboard) {
        window.dashboard.createProcess();
    }
}

// Handle page visibility change to pause updates when tab is not active
document.addEventListener('visibilitychange', () => {
    if (window.dashboard) {
        if (document.hidden) {
            window.dashboard.updateInterval = 10000; // Slow down updates to 10 seconds when hidden
        } else {
            window.dashboard.updateInterval = 3000; // Resume 3-second updates when visible
            // Immediate update when tab becomes visible again
            if (!window.dashboard.updatesPaused) {
                window.dashboard.updateAllData();
            }
        }
    }
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
                "total_files": 2847,
                "total_directories": 156,
                "storage_utilization": 45,
                "cache_hit_rate": 94.2,
                "fragmentation": 2.1,
                "io_operations": 1248
            }
            
        fs_stats = self.file_system.get_file_system_stats()
        
        # Add additional computed metrics
        import random
        fs_stats.update({
            "total_files": fs_stats.get("total_files", 2847),
            "total_directories": fs_stats.get("total_directories", 156),
            "cache_hit_rate": fs_stats.get("cache_hit_rate", 90 + random.random() * 8),
            "fragmentation": random.uniform(1.5, 3.5),
            "io_operations": random.randint(800, 1500)
        })
        
        return fs_stats
        
    def _get_scheduler_data(self) -> Dict[str, Any]:
        """Get AI scheduler data"""
        if not self.ai_scheduler:
            return {
                "learning_mode": "Adaptive",
                "prediction_accuracy": 94.7,
                "avg_performance_score": 89.5,
                "total_scheduled": 342,
                "adaptation_count": 1247,
                "queue_length": 12,
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
            import random
            return {
                "encrypted_files": 1542,
                "active_encryption_keys": 8,
                "success_rate": 99.8,
                "blocked_users": 3,
                "total_files": 2847,
                "total_directories": 156,
                "cache_hit_rate": 94.2,
                "fragmentation": 2.1,
                "io_operations": 1248,
                "threats_blocked": 247,
                "last_threat": "3 hours ago",
                "active_sessions": 12,
                "failed_attempts": 5,
                "log_entries": 24789,
                "storage_used": "847 MB"
            }
            
        security_stats = self.encryption.get_security_statistics()
        
        # Add additional security metrics
        import random
        security_stats.update({
            "total_files": random.randint(2500, 3000),
            "total_directories": random.randint(150, 200),
            "cache_hit_rate": 90 + random.random() * 8,
            "fragmentation": random.uniform(1.5, 3.5),
            "io_operations": random.randint(800, 1500),
            "threats_blocked": random.randint(200, 300),
            "last_threat": "3 hours ago",
            "active_sessions": random.randint(8, 15),
            "failed_attempts": random.randint(3, 8),
            "log_entries": random.randint(20000, 30000),
            "storage_used": f"{random.randint(700, 900)} MB"
        })
        
        return security_stats

def create_integrated_gui(file_system=None, encryption=None, ai_scheduler=None, port=8080):
    """Create integrated web GUI with all system components"""
    gui = WebGUIServer(file_system, encryption, ai_scheduler, port)
    return gui 