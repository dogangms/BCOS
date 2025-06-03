"""
Decentralized AI Node Operating System - Step 4: File System Visualizer
Real-time visualization and monitoring for the file system.
"""

import os
import time
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json
from collections import deque

from file_system import VirtualFileSystem, FileType, AccessLevel, DirectoryEntry
from file_encryption import FileEncryption, SecurityEvent, EncryptionLevel

class VisualizationMode(Enum):
    """File system visualization modes"""
    DIRECTORY_TREE = "📁 Directory Tree"
    STORAGE_ANALYTICS = "📊 Storage Analytics"
    FILE_OPERATIONS = "⚡ File Operations"
    SECURITY_DASHBOARD = "🔒 Security Dashboard"
    CACHE_MONITOR = "💾 Cache Monitor"
    PERFORMANCE_METRICS = "📈 Performance Metrics"

@dataclass
class FileSystemEvent:
    """File system operation event"""
    timestamp: float
    event_type: str  # "create", "read", "write", "delete", "encrypt", "decrypt"
    file_path: str
    user_id: str
    file_size: int = 0
    success: bool = True
    details: str = ""

class FileSystemVisualizer:
    """
    Comprehensive file system visualizer
    Provides real-time monitoring and analytics for the virtual file system
    """
    
    def __init__(self, file_system: VirtualFileSystem, encryption: Optional[FileEncryption] = None):
        self.file_system = file_system
        self.encryption = encryption
        
        # Monitoring state
        self.running = False
        self.monitor_thread = None
        self.current_mode = VisualizationMode.DIRECTORY_TREE
        
        # Event tracking
        self.fs_events: deque = deque(maxlen=1000)
        self.performance_history: deque = deque(maxlen=100)
        
        # Display settings
        self.refresh_rate = 2.0
        self.display_width = 120
        
        # Statistics
        self.operation_counts = {"create": 0, "read": 0, "write": 0, "delete": 0}
        self.user_activity = {}
        
    def start_monitoring(self):
        """Start real-time file system monitoring"""
        if self.running:
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        print("🔍 File system monitoring started...")
        
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        print("🛑 File system monitoring stopped.")
        
    def add_event(self, event: FileSystemEvent):
        """Add file system event for tracking"""
        self.fs_events.append(event)
        self.operation_counts[event.event_type] = self.operation_counts.get(event.event_type, 0) + 1
        
        # Track user activity
        if event.user_id not in self.user_activity:
            self.user_activity[event.user_id] = {"operations": 0, "data_transferred": 0}
        self.user_activity[event.user_id]["operations"] += 1
        self.user_activity[event.user_id]["data_transferred"] += event.file_size
        
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._clear_screen()
                self._update_performance_metrics()
                
                if self.current_mode == VisualizationMode.DIRECTORY_TREE:
                    self._display_directory_tree()
                elif self.current_mode == VisualizationMode.STORAGE_ANALYTICS:
                    self._display_storage_analytics()
                elif self.current_mode == VisualizationMode.FILE_OPERATIONS:
                    self._display_file_operations()
                elif self.current_mode == VisualizationMode.SECURITY_DASHBOARD:
                    self._display_security_dashboard()
                elif self.current_mode == VisualizationMode.CACHE_MONITOR:
                    self._display_cache_monitor()
                elif self.current_mode == VisualizationMode.PERFORMANCE_METRICS:
                    self._display_performance_metrics()
                    
                self._display_menu()
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                
            time.sleep(self.refresh_rate)
            
    def _clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def _display_directory_tree(self):
        """Display hierarchical directory tree"""
        print("📁 " + "FILE SYSTEM DIRECTORY TREE".center(self.display_width - 4, "═"))
        print()
        
        # File system stats header
        stats = self.file_system.get_file_system_stats()
        print(f"📊 Files: {stats['total_files']} | Directories: {stats['total_directories']} | "
              f"Storage: {stats['used_storage']/1024/1024:.1f}MB / {stats['total_storage']/1024/1024:.1f}MB "
              f"({stats['storage_utilization']:.1f}%)")
        print()
        
        # Display directory tree starting from root
        self._display_tree_recursive("/", 0)
        
    def _display_tree_recursive(self, path: str, depth: int, max_depth: int = 4):
        """Recursively display directory tree"""
        if depth > max_depth:
            return
            
        try:
            entries = self.file_system.list_directory(path)
            
            # Sort entries: directories first, then by name
            entries.sort(key=lambda x: (not x.is_directory, x.name.lower()))
            
            for i, entry in enumerate(entries[:20]):  # Limit to 20 entries per directory
                is_last = i == len(entries) - 1
                
                # Create tree structure indicators
                prefix = "  " * depth
                if depth > 0:
                    prefix += "└── " if is_last else "├── "
                    
                # File type icon and info
                if entry.is_directory:
                    icon = "📁"
                    size_info = f"({len(self.file_system.list_directory(os.path.join(path, entry.name).replace('\\', '/'))) } items)"
                else:
                    # Get file metadata for icon
                    try:
                        file_path = os.path.join(path, entry.name).replace('\\', '/')
                        metadata = self.file_system.get_file_info(file_path)
                        icon = self._get_file_type_icon(metadata.file_type)
                        size_info = f"({self._format_file_size(entry.size)})"
                        
                        # Add encryption indicator
                        if self.encryption and metadata.file_type == FileType.ENCRYPTED:
                            icon += "🔒"
                    except:
                        icon = "📄"
                        size_info = f"({self._format_file_size(entry.size)})"
                        
                # Display entry
                print(f"{prefix}{icon} {entry.name} {size_info}")
                
                # Recurse into subdirectories
                if entry.is_directory and depth < max_depth:
                    subdir_path = os.path.join(path, entry.name).replace('\\', '/')
                    self._display_tree_recursive(subdir_path, depth + 1, max_depth)
                    
        except Exception as e:
            print(f"  ❌ Error accessing {path}: {e}")
            
    def _get_file_type_icon(self, file_type: FileType) -> str:
        """Get icon for file type"""
        icon_map = {
            FileType.REGULAR: "📄",
            FileType.DIRECTORY: "📁",
            FileType.AI_MODEL: "🧠",
            FileType.AI_DATASET: "📊",
            FileType.BLOCKCHAIN_DATA: "⛓️",
            FileType.SMART_CONTRACT: "📜",
            FileType.NETWORK_CONFIG: "🌐",
            FileType.SYSTEM_FILE: "⚙️",
            FileType.ENCRYPTED: "🔒",
            FileType.LINK: "🔗"
        }
        return icon_map.get(file_type, "📄")
        
    def _format_file_size(self, size: int) -> str:
        """Format file size in human readable format"""
        if size < 1024:
            return f"{size}B"
        elif size < 1024**2:
            return f"{size/1024:.1f}KB"
        elif size < 1024**3:
            return f"{size/1024**2:.1f}MB"
        else:
            return f"{size/1024**3:.1f}GB"
            
    def _display_storage_analytics(self):
        """Display storage analytics and usage breakdown"""
        print("📊 " + "STORAGE ANALYTICS DASHBOARD".center(self.display_width - 4, "═"))
        print()
        
        stats = self.file_system.get_file_system_stats()
        
        # Storage overview
        print("💾 STORAGE OVERVIEW:")
        print("─" * 60)
        total_gb = stats['total_storage'] / 1024**3
        used_gb = stats['used_storage'] / 1024**3
        free_gb = total_gb - used_gb
        
        print(f"  Total Storage: {total_gb:.2f} GB")
        print(f"  Used Storage:  {used_gb:.2f} GB ({stats['storage_utilization']:.1f}%)")
        print(f"  Free Storage:  {free_gb:.2f} GB ({100-stats['storage_utilization']:.1f}%)")
        
        # Storage usage bar
        bar_width = 50
        used_bars = int(stats['storage_utilization'] / 100 * bar_width)
        free_bars = bar_width - used_bars
        usage_bar = "█" * used_bars + "░" * free_bars
        print(f"  Usage: [{usage_bar}]")
        print()
        
        # File type breakdown
        print("📁 STORAGE BY FILE TYPE:")
        print("─" * 60)
        storage_by_type = stats['storage_by_type']
        
        for file_type, size in sorted(storage_by_type.items(), key=lambda x: x[1], reverse=True):
            if size > 0:
                percentage = (size / stats['used_storage']) * 100 if stats['used_storage'] > 0 else 0
                size_str = self._format_file_size(size)
                bar_length = int(percentage / 100 * 30)
                bar = "█" * bar_length + "░" * (30 - bar_length)
                print(f"  {file_type[:20]:<20} {size_str:>8} [{bar}] {percentage:.1f}%")
        print()
        
        # Block allocation
        print("🧮 BLOCK ALLOCATION:")
        print("─" * 60)
        print(f"  Total Blocks: {stats['used_blocks'] + stats['free_blocks']}")
        print(f"  Used Blocks:  {stats['used_blocks']}")
        print(f"  Free Blocks:  {stats['free_blocks']}")
        print(f"  Block Size:   {self.file_system.block_size} bytes")
        
        # Fragmentation info (simplified)
        fragmentation = min(stats['used_blocks'] / max(stats['total_files'], 1), 5.0)
        print(f"  Fragmentation: {fragmentation:.2f} blocks/file avg")
        
    def _display_file_operations(self):
        """Display recent file operations and activity"""
        print("⚡ " + "FILE OPERATIONS MONITOR".center(self.display_width - 4, "═"))
        print()
        
        # Operation statistics
        print("📈 OPERATION STATISTICS:")
        print("─" * 80)
        stats = self.file_system.get_file_system_stats()
        
        print(f"  Read Operations:  {stats['read_operations']:>6}")
        print(f"  Write Operations: {stats['write_operations']:>6}")
        print(f"  Cache Hit Rate:   {stats['cache_hit_rate']:>5.1f}%")
        print(f"  Avg I/O Time:     {stats['avg_io_time']*1000:>5.2f}ms")
        print()
        
        # Recent operations
        recent_events = list(self.fs_events)[-15:]  # Last 15 events
        if recent_events:
            print("📋 RECENT FILE OPERATIONS:")
            print("─" * 100)
            print(f"{'Time':<12} {'Operation':<10} {'User':<12} {'File':<30} {'Size':<10} {'Status':<8}")
            print("─" * 100)
            
            for event in recent_events:
                time_str = time.strftime('%H:%M:%S', time.localtime(event.timestamp))
                file_name = os.path.basename(event.file_path)[:29]
                size_str = self._format_file_size(event.file_size)
                status = "✅ OK" if event.success else "❌ FAIL"
                
                print(f"{time_str:<12} {event.event_type:<10} {event.user_id[:11]:<12} "
                      f"{file_name:<30} {size_str:<10} {status:<8}")
        else:
            print("📭 No recent file operations")
            
    def _display_security_dashboard(self):
        """Display security and encryption dashboard"""
        print("🔒 " + "SECURITY DASHBOARD".center(self.display_width - 4, "═"))
        print()
        
        if not self.encryption:
            print("🚫 Encryption module not available")
            return
            
        security_stats = self.encryption.get_security_statistics()
        
        # Security overview
        print("🛡️ SECURITY OVERVIEW:")
        print("─" * 60)
        print(f"  Encryption Keys: {security_stats['total_encryption_keys']}")
        print(f"  Active Keys:     {security_stats['active_encryption_keys']}")
        print(f"  Encrypted Files: {security_stats['encrypted_files']}")
        print(f"  Blocked Users:   {security_stats['blocked_users']}")
        print(f"  Success Rate:    {security_stats['success_rate']:.1f}%")
        print()
        
        # Encryption levels
        print("🔐 ENCRYPTION LEVELS:")
        print("─" * 60)
        for level, count in security_stats['encryption_levels'].items():
            if count > 0:
                print(f"  {level:<20} {count:>3} keys")
        print()
        
        # Security events
        print("🚨 RECENT SECURITY EVENTS:")
        print("─" * 80)
        audit_log = self.encryption.get_audit_log(limit=10)
        
        if audit_log:
            print(f"{'Time':<12} {'Event':<20} {'User':<12} {'Status':<8} {'Details':<25}")
            print("─" * 80)
            
            for event in audit_log:
                time_str = time.strftime('%H:%M:%S', time.localtime(event.timestamp))
                status = "✅ OK" if event.success else "❌ FAIL"
                details = event.details[:24]
                
                print(f"{time_str:<12} {event.event_type.value[:19]:<20} "
                      f"{event.user_id[:11]:<12} {status:<8} {details:<25}")
        else:
            print("📭 No security events recorded")
            
    def _display_cache_monitor(self):
        """Display file system cache monitoring"""
        print("💾 " + "CACHE PERFORMANCE MONITOR".center(self.display_width - 4, "═"))
        print()
        
        stats = self.file_system.get_file_system_stats()
        
        # Cache statistics
        print("📊 CACHE STATISTICS:")
        print("─" * 60)
        print(f"  Cache Hits:    {stats['cache_hits']:>8}")
        print(f"  Cache Misses:  {stats['cache_misses']:>8}")
        print(f"  Hit Rate:      {stats['cache_hit_rate']:>7.1f}%")
        
        # Cache efficiency visualization
        if stats['cache_hits'] + stats['cache_misses'] > 0:
            hit_percentage = stats['cache_hit_rate']
            bar_width = 40
            hit_bars = int(hit_percentage / 100 * bar_width)
            miss_bars = bar_width - hit_bars
            
            print(f"  Cache Efficiency:")
            print(f"    Hits:   [{('█' * hit_bars).ljust(bar_width, '░')}] {hit_percentage:.1f}%")
            print(f"    Misses: [{('█' * miss_bars).ljust(bar_width, '░')}] {100 - hit_percentage:.1f}%")
        print()
        
        # I/O Performance
        print("⚡ I/O PERFORMANCE:")
        print("─" * 60)
        print(f"  Total I/O Time:  {stats['total_io_time']:.3f}s")
        print(f"  Average I/O:     {stats['avg_io_time']*1000:.2f}ms")
        print(f"  Operations/sec:  {(stats['read_operations'] + stats['write_operations']) / max(stats['total_io_time'], 0.001):.1f}")
        
        # Performance over time (simplified)
        if self.performance_history:
            print("\n📈 PERFORMANCE TREND (last 10 samples):")
            recent_perf = list(self.performance_history)[-10:]
            self._draw_simple_graph(recent_perf, "I/O Time (ms)")
            
    def _display_performance_metrics(self):
        """Display comprehensive performance metrics"""
        print("📈 " + "PERFORMANCE METRICS DASHBOARD".center(self.display_width - 4, "═"))
        print()
        
        stats = self.file_system.get_file_system_stats()
        
        # System performance overview
        print("⚡ SYSTEM PERFORMANCE:")
        print("─" * 80)
        print(f"  Total Operations:    {stats['read_operations'] + stats['write_operations']:>8}")
        print(f"  Read Operations:     {stats['read_operations']:>8}")
        print(f"  Write Operations:    {stats['write_operations']:>8}")
        print(f"  Cache Hit Rate:      {stats['cache_hit_rate']:>7.1f}%")
        print(f"  Average I/O Time:    {stats['avg_io_time']*1000:>7.2f}ms")
        print()
        
        # User activity
        print("👥 USER ACTIVITY:")
        print("─" * 60)
        if self.user_activity:
            print(f"{'User':<15} {'Operations':<12} {'Data Transferred':<15}")
            print("─" * 60)
            
            for user_id, activity in sorted(self.user_activity.items(), 
                                          key=lambda x: x[1]['operations'], reverse=True)[:10]:
                data_size = self._format_file_size(activity['data_transferred'])
                print(f"{user_id[:14]:<15} {activity['operations']:<12} {data_size:<15}")
        else:
            print("📭 No user activity recorded")
        print()
        
        # Operation breakdown
        print("🔄 OPERATION BREAKDOWN:")
        print("─" * 60)
        total_ops = sum(self.operation_counts.values())
        if total_ops > 0:
            for op_type, count in sorted(self.operation_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_ops) * 100
                bar_length = int(percentage / 100 * 30)
                bar = "█" * bar_length + "░" * (30 - bar_length)
                print(f"  {op_type.capitalize():<10} {count:>6} [{bar}] {percentage:.1f}%")
                
    def _draw_simple_graph(self, data: List[float], label: str):
        """Draw a simple ASCII graph"""
        if not data or len(data) < 2:
            print("  📊 Insufficient data for graph")
            return
            
        max_val = max(data)
        min_val = min(data)
        graph_height = 6
        graph_width = min(50, len(data))
        
        print(f"  📊 {label}:")
        
        # Normalize data
        if max_val == min_val:
            normalized = [graph_height // 2] * len(data)
        else:
            normalized = [int((val - min_val) / (max_val - min_val) * graph_height) 
                         for val in data[-graph_width:]]
        
        # Draw graph
        for row in range(graph_height, -1, -1):
            line = f"    {(min_val + (max_val - min_val) * row / graph_height):6.2f} │"
            for val in normalized:
                if val >= row:
                    line += "█"
                else:
                    line += " "
            print(line)
            
        # X-axis
        print("           └" + "─" * len(normalized))
        
    def _update_performance_metrics(self):
        """Update performance tracking"""
        stats = self.file_system.get_file_system_stats()
        current_avg_io = stats['avg_io_time'] * 1000  # Convert to ms
        self.performance_history.append(current_avg_io)
        
    def _display_menu(self):
        """Display interactive menu"""
        print("\n" + "─" * self.display_width)
        print("🎛️ CONTROLS:")
        print("  [1] Directory Tree  [2] Storage Analytics  [3] File Operations")
        print("  [4] Security Dashboard  [5] Cache Monitor  [6] Performance Metrics")
        print(f"  Current: {self.current_mode.value} | Refresh: {self.refresh_rate}s | [Q] Quit")
        
    def switch_mode(self, mode: VisualizationMode):
        """Switch visualization mode"""
        self.current_mode = mode
        
    def set_refresh_rate(self, rate: float):
        """Set refresh rate in seconds"""
        self.refresh_rate = max(0.5, rate)
        
    def export_analytics(self, filename: str):
        """Export file system analytics to JSON"""
        analytics_data = {
            "timestamp": time.time(),
            "file_system_stats": self.file_system.get_file_system_stats(),
            "operation_counts": self.operation_counts,
            "user_activity": self.user_activity,
            "recent_events": [
                {
                    "timestamp": event.timestamp,
                    "event_type": event.event_type,
                    "file_path": event.file_path,
                    "user_id": event.user_id,
                    "file_size": event.file_size,
                    "success": event.success,
                    "details": event.details
                }
                for event in list(self.fs_events)[-100:]  # Last 100 events
            ]
        }
        
        if self.encryption:
            analytics_data["security_stats"] = self.encryption.get_security_statistics()
            
        with open(filename, 'w') as f:
            json.dump(analytics_data, f, indent=2)
            
        print(f"📊 Analytics exported to {filename}")

class InteractiveFileSystemMonitor:
    """Interactive monitoring interface for file system"""
    
    def __init__(self, visualizer: FileSystemVisualizer):
        self.visualizer = visualizer
        self.running = False
        
    def start_interactive_mode(self):
        """Start interactive monitoring mode"""
        if self.running:
            return
            
        self.running = True
        self.visualizer.start_monitoring()
        
        print("🎮 Interactive file system monitoring started!")
        print("📝 Use number keys to switch views, 'q' to quit")
        
        self._input_handler()
        
    def stop_interactive_mode(self):
        """Stop interactive monitoring"""
        self.running = False
        self.visualizer.stop_monitoring()
        
    def _input_handler(self):
        """Handle user input for mode switching"""
        while self.running:
            try:
                key = input("\n🎯 Enter command (1-6 for modes, q to quit): ").strip().lower()
                
                if key == 'q':
                    self.stop_interactive_mode()
                    break
                elif key == '1':
                    self.visualizer.switch_mode(VisualizationMode.DIRECTORY_TREE)
                elif key == '2':
                    self.visualizer.switch_mode(VisualizationMode.STORAGE_ANALYTICS)
                elif key == '3':
                    self.visualizer.switch_mode(VisualizationMode.FILE_OPERATIONS)
                elif key == '4':
                    self.visualizer.switch_mode(VisualizationMode.SECURITY_DASHBOARD)
                elif key == '5':
                    self.visualizer.switch_mode(VisualizationMode.CACHE_MONITOR)
                elif key == '6':
                    self.visualizer.switch_mode(VisualizationMode.PERFORMANCE_METRICS)
                elif key.startswith('export'):
                    filename = f"fs_analytics_{int(time.time())}.json"
                    self.visualizer.export_analytics(filename)
                elif key.startswith('refresh'):
                    try:
                        rate = float(key.split()[1]) if len(key.split()) > 1 else 2.0
                        self.visualizer.set_refresh_rate(rate)
                        print(f"📱 Refresh rate set to {rate}s")
                    except (ValueError, IndexError):
                        print("❌ Invalid refresh rate")
                else:
                    print("❌ Invalid command")
                    
            except (EOFError, KeyboardInterrupt):
                self.stop_interactive_mode()
                break
            except Exception as e:
                print(f"❌ Input error: {e}")
                
        print("🛑 Interactive monitoring stopped.") 