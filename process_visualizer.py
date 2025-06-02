import time
import os
import json
from typing import Dict, List, Any
from datetime import datetime
from process_control_block import ProcessState, ProcessType
from process_manager import ProcessManager
from schedulers import MLFQScheduler

class ProcessVisualizer:
    """
    Visualization system for the Decentralized AI Node Operating System
    Displays process queues, system information, and performance metrics
    """
    
    def __init__(self, process_manager: ProcessManager):
        self.process_manager = process_manager
        self.theme_colors = {
            'AI_INFERENCE': '🧠',
            'DATA_PROCESSING': '📊', 
            'BLOCKCHAIN_VALIDATOR': '⛓️',
            'NETWORK_NODE': '🌐',
            'SYSTEM': '⚙️',
            'USER': '👤'
        }
        
        self.state_colors = {
            'new': '🆕',
            'ready': '⏳',
            'running': '🏃',
            'waiting': '⏸️',
            'terminated': '💀',
            'suspended': '😴'
        }
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """Display system header"""
        system_info = self.process_manager.get_system_info()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("═" * 80)
        print("🚀 DECENTRALIZED AI NODE OPERATING SYSTEM - PROCESS MANAGER 🚀")
        print("═" * 80)
        print(f"📅 Time: {current_time}")
        print(f"🆔 Node ID: {system_info['node_id'][:8]}...")
        print(f"📊 Scheduler: {system_info['scheduler']}")
        print(f"⏱️  Uptime: {system_info['uptime']:.1f}s")
        print(f"🔀 Context Switches: {system_info['context_switches']}")
        print("═" * 80)
    
    def display_memory_info(self):
        """Display memory information"""
        system_info = self.process_manager.get_system_info()
        total_mb = system_info['total_memory'] / 1024
        available_mb = system_info['available_memory'] / 1024
        used_mb = total_mb - available_mb
        usage_percent = system_info['memory_usage_percent']
        
        print(f"💾 MEMORY STATUS")
        print(f"   Total: {total_mb:.1f} MB")
        print(f"   Used:  {used_mb:.1f} MB ({usage_percent:.1f}%)")
        print(f"   Free:  {available_mb:.1f} MB")
        
        # Memory bar
        bar_length = 40
        used_bars = int((usage_percent / 100) * bar_length)
        free_bars = bar_length - used_bars
        
        print(f"   [{'█' * used_bars}{'░' * free_bars}] {usage_percent:.1f}%")
        print()
    
    def display_process_list(self):
        """Display list of all processes"""
        processes = self.process_manager.list_processes()
        
        if not processes:
            print("📋 No processes currently running")
            return
        
        print("📋 ACTIVE PROCESSES")
        print("-" * 80)
        print(f"{'PID':<4} {'Name':<20} {'Type':<15} {'State':<10} {'Priority':<8} {'Memory':<8}")
        print("-" * 80)
        
        for proc in sorted(processes, key=lambda x: x['pid']):
            type_icon = self.theme_colors.get(proc['type'], '❓')
            state_icon = self.state_colors.get(proc['state'], '❓')
            
            print(f"{proc['pid']:<4} {proc['name']:<20} {type_icon}{proc['type']:<14} "
                  f"{state_icon}{proc['state']:<9} {proc['priority']:<8} {proc['memory_required']:<8}")
        print()
    
    def display_scheduler_queues(self):
        """Display scheduler queue information"""
        scheduler = self.process_manager.scheduler
        
        print(f"🎯 SCHEDULER QUEUES ({scheduler.name})")
        print("-" * 50)
        
        if hasattr(scheduler, 'get_queue_info'):
            if isinstance(scheduler, MLFQScheduler):
                # Multi-level queue display
                queue_info = scheduler.get_queue_info()
                for level, processes in queue_info.items():
                    print(f"  Level {level} (Quantum: {scheduler.time_quanta[level]}ms): {len(processes)} processes")
                    for proc in processes[:3]:  # Show first 3 processes
                        type_icon = self.theme_colors.get(proc['type'], '❓')
                        print(f"    • {type_icon} {proc['name']} (PID: {proc['pid']})")
                    if len(processes) > 3:
                        print(f"    ... and {len(processes) - 3} more")
            else:
                # Single queue display
                queue_info = scheduler.get_queue_info()
                print(f"  Ready Queue: {len(queue_info)} processes")
                for proc in queue_info[:5]:  # Show first 5 processes
                    type_icon = self.theme_colors.get(proc['type'], '❓')
                    print(f"    • {type_icon} {proc['name']} (PID: {proc['pid']})")
                if len(queue_info) > 5:
                    print(f"    ... and {len(queue_info) - 5} more")
        else:
            print(f"  Queue size: {0 if scheduler.is_empty() else 'Non-empty'}")
        print()
    
    def display_statistics(self):
        """Display performance statistics"""
        stats = self.process_manager.scheduler.get_statistics()
        system_info = self.process_manager.get_system_info()
        
        print("📊 PERFORMANCE STATISTICS")
        print("-" * 40)
        print(f"  Total Processes: {system_info['total_processes']}")
        print(f"  Running Processes: {system_info['running_processes']}")
        print(f"  Completed Processes: {self.process_manager.scheduler.completed_processes}")
        print(f"  Average Wait Time: {stats['average_wait_time']:.2f}s")
        print(f"  Average Turnaround Time: {stats['average_turnaround_time']:.2f}s")
        print(f"  Throughput: {stats['throughput']:.2f} processes/sec")
        print()
    
    def display_ai_node_info(self):
        """Display AI Node specific information"""
        print("🤖 AI NODE STATUS")
        print("-" * 30)
        
        # Count AI-related processes
        ai_processes = [p for p in self.process_manager.list_processes() 
                       if p['type'] in ['AI_INFERENCE', 'DATA_PROCESSING']]
        blockchain_processes = [p for p in self.process_manager.list_processes() 
                              if p['type'] == 'BLOCKCHAIN_VALIDATOR']
        network_processes = [p for p in self.process_manager.list_processes() 
                           if p['type'] == 'NETWORK_NODE']
        
        print(f"  🧠 AI Processes: {len(ai_processes)}")
        print(f"  ⛓️  Blockchain Processes: {len(blockchain_processes)}")
        print(f"  🌐 Network Processes: {len(network_processes)}")
        print(f"  🗄️  Model Cache Size: {len(self.process_manager.ai_model_cache)}")
        print(f"  🔗 Network Connections: {len(self.process_manager.network_connections)}")
        print()
    
    def display_full_dashboard(self):
        """Display complete system dashboard"""
        self.clear_screen()
        self.display_header()
        self.display_memory_info()
        self.display_process_list()
        self.display_scheduler_queues()
        self.display_statistics()
        self.display_ai_node_info()
        print("═" * 80)
        print("Press Ctrl+C to exit dashboard")
        print("═" * 80)
    
    def export_system_state(self, filename: str = None):
        """Export current system state to JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"system_state_{timestamp}.json"
        
        system_state = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self.process_manager.get_system_info(),
            'processes': self.process_manager.list_processes(),
            'scheduler_stats': self.process_manager.scheduler.get_statistics()
        }
        
        with open(filename, 'w') as f:
            json.dump(system_state, f, indent=2, default=str)
        
        print(f"📁 System state exported to {filename}")
    
    def real_time_monitor(self, refresh_interval: float = 2.0):
        """Start real-time monitoring dashboard"""
        try:
            while True:
                self.display_full_dashboard()
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
    
    def display_process_tree(self):
        """Display process hierarchy tree"""
        processes = self.process_manager.list_processes()
        
        # Build parent-child relationships
        children_map = {}
        root_processes = []
        
        for proc in processes:
            parent_pid = proc.get('parent_pid')
            if parent_pid is None:
                root_processes.append(proc)
            else:
                if parent_pid not in children_map:
                    children_map[parent_pid] = []
                children_map[parent_pid].append(proc)
        
        print("🌳 PROCESS TREE")
        print("-" * 40)
        
        def print_tree(process, indent=0):
            type_icon = self.theme_colors.get(process['type'], '❓')
            state_icon = self.state_colors.get(process['state'], '❓')
            
            prefix = "  " * indent + ("├─ " if indent > 0 else "")
            print(f"{prefix}{type_icon} {process['name']} (PID: {process['pid']}) {state_icon}")
            
            # Print children
            pid = process['pid']
            if pid in children_map:
                for child in children_map[pid]:
                    print_tree(child, indent + 1)
        
        if not root_processes:
            print("  No root processes found")
        else:
            for root_proc in root_processes:
                print_tree(root_proc)
        print() 