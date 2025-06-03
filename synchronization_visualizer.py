"""
Decentralized AI Node Operating System - Step 3: Synchronization Visualizer
Real-time visualization for threading and synchronization primitives.
"""

import threading
import time
import os
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
from collections import deque
import json

from thread_api import ThreadAPI, ThreadState, ThreadType, ThreadPriority, AIThread

class VisualizationMode(Enum):
    """Visualization display modes"""
    THREAD_DASHBOARD = "Thread Dashboard"
    LOCK_MONITOR = "Lock Monitor"
    CONDITION_TRACKER = "Condition Variable Tracker"
    DEADLOCK_DETECTOR = "Deadlock Detector"
    PERFORMANCE_GRAPH = "Performance Graph"
    TIMELINE_VIEW = "Timeline View"

@dataclass
class SyncEvent:
    """Synchronization event for timeline tracking"""
    timestamp: float
    thread_id: str
    event_type: str  # "lock_acquire", "lock_release", "wait", "notify", etc.
    resource_id: str
    success: bool = True
    wait_time: float = 0.0

@dataclass
class ThreadSnapshot:
    """Thread state snapshot for visualization"""
    thread_id: str
    name: str
    state: ThreadState
    thread_type: ThreadType
    priority: ThreadPriority
    cpu_time: float
    memory_usage: int
    locks_held: List[str]
    waiting_for_lock: Optional[str]
    timestamp: float = field(default_factory=time.time)

class SynchronizationVisualizer:
    """
    Real-time visualizer for threading and synchronization
    Provides multiple views of concurrent system behavior
    """
    
    def __init__(self, thread_api: ThreadAPI):
        self.thread_api = thread_api
        self.running = False
        self.visualization_thread = None
        
        # Event tracking
        self.sync_events: deque = deque(maxlen=1000)
        self.thread_snapshots: Dict[str, deque] = {}
        self.performance_history: deque = deque(maxlen=100)
        
        # Visualization settings
        self.refresh_rate = 1.0  # seconds
        self.current_mode = VisualizationMode.THREAD_DASHBOARD
        self.display_width = 120
        
        # Lock dependency graph for deadlock detection
        self.lock_dependency_graph: Dict[str, set] = {}
        self.potential_deadlocks: List[Tuple[List[str], List[str]]] = []
        
        # Performance metrics
        self.throughput_history = deque(maxlen=50)
        self.lock_contention_history = deque(maxlen=50)
        self.thread_utilization_history = deque(maxlen=50)
        
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.running:
            return
            
        self.running = True
        self.visualization_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.visualization_thread.start()
        print("🔍 Synchronization monitoring started...")
        
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.running = False
        if self.visualization_thread:
            self.visualization_thread.join(timeout=2.0)
        print("🛑 Synchronization monitoring stopped.")
        
    def add_sync_event(self, event: SyncEvent):
        """Add a synchronization event for tracking"""
        self.sync_events.append(event)
        self._update_lock_dependency_graph(event)
        
    def take_thread_snapshot(self):
        """Take a snapshot of all current threads"""
        threads = self.thread_api.list_threads()
        
        for thread in threads:
            snapshot = ThreadSnapshot(
                thread_id=thread.thread_id,
                name=thread.name,
                state=thread.state,
                thread_type=thread.thread_type,
                priority=thread.priority,
                cpu_time=thread.cpu_time,
                memory_usage=thread.memory_usage,
                locks_held=thread.locks_held.copy(),
                waiting_for_lock=thread.waiting_for_lock
            )
            
            if thread.thread_id not in self.thread_snapshots:
                self.thread_snapshots[thread.thread_id] = deque(maxlen=50)
            self.thread_snapshots[thread.thread_id].append(snapshot)
            
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._clear_screen()
                self.take_thread_snapshot()
                self._update_performance_metrics()
                self._detect_potential_deadlocks()
                
                if self.current_mode == VisualizationMode.THREAD_DASHBOARD:
                    self._display_thread_dashboard()
                elif self.current_mode == VisualizationMode.LOCK_MONITOR:
                    self._display_lock_monitor()
                elif self.current_mode == VisualizationMode.CONDITION_TRACKER:
                    self._display_condition_tracker()
                elif self.current_mode == VisualizationMode.DEADLOCK_DETECTOR:
                    self._display_deadlock_detector()
                elif self.current_mode == VisualizationMode.PERFORMANCE_GRAPH:
                    self._display_performance_graph()
                elif self.current_mode == VisualizationMode.TIMELINE_VIEW:
                    self._display_timeline_view()
                    
                self._display_menu()
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                
            time.sleep(self.refresh_rate)
            
    def _clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def _display_thread_dashboard(self):
        """Display the main thread dashboard"""
        print("🔍 " + "AI NODE SYNCHRONIZATION DASHBOARD".center(self.display_width - 4, "═"))
        print()
        
        # System overview
        stats = self.thread_api.get_system_stats()
        print(f"⏱️  System Uptime: {stats['uptime']:.2f}s")
        print(f"🔢 Active Threads: {stats['active_threads']}")
        print(f"📊 CPU Utilization: {stats['average_cpu_utilization']:.1f}%")
        print(f"🔒 Active Locks: {stats['locks_count']}")
        print(f"📡 Condition Variables: {stats['condition_variables_count']}")
        print()
        
        # Thread state summary
        print("📋 THREAD STATE SUMMARY:")
        print("─" * 60)
        state_icons = {
            "CREATED": "🆕", "READY": "⏳", "RUNNING": "🟢",
            "BLOCKED": "🔴", "WAITING": "🔵", "TERMINATED": "⚫", "SUSPENDED": "⏸️"
        }
        
        for state, count in stats['threads_by_state'].items():
            if count > 0:
                icon = state_icons.get(state, "❓")
                print(f"  {icon} {state}: {count}")
        print()
        
        # Active threads details
        active_threads = self.thread_api.list_running_threads()
        if active_threads:
            print("🏃 ACTIVE THREADS:")
            print("─" * 100)
            print(f"{'ID':<10} {'Name':<20} {'Type':<18} {'Priority':<10} {'CPU Time':<10} {'Locks':<15}")
            print("─" * 100)
            
            for thread in active_threads[:10]:  # Show top 10
                locks_str = f"{len(thread.locks_held)} held"
                if thread.waiting_for_lock:
                    locks_str += f", waiting: {thread.waiting_for_lock[:8]}"
                    
                print(f"{thread.thread_id:<10} {thread.name[:19]:<20} "
                      f"{thread.thread_type.value[:17]:<18} {thread.priority.name:<10} "
                      f"{thread.cpu_time:.3f}s    {locks_str[:14]:<15}")
        else:
            print("💤 No active threads")
            
        print()
        
        # Thread type distribution
        print("🎯 THREAD TYPE DISTRIBUTION:")
        print("─" * 60)
        for thread_type, count in stats['threads_by_type'].items():
            if count > 0:
                bar_length = min(count * 2, 30)
                bar = "█" * bar_length
                print(f"  {thread_type[:25]:<25} {bar} {count}")
                
    def _display_lock_monitor(self):
        """Display lock monitoring view"""
        print("🔒 " + "LOCK CONTENTION MONITOR".center(self.display_width - 4, "═"))
        print()
        
        # Lock status
        locks = self.thread_api.locks
        print(f"🔢 Total Locks: {len(locks)}")
        print()
        
        if locks:
            print("🔒 LOCK STATUS:")
            print("─" * 80)
            print(f"{'Lock ID':<20} {'Status':<15} {'Holder Thread':<20} {'Waiters':<15}")
            print("─" * 80)
            
            for lock_id in locks:
                # Simplified status checking (in real implementation, would need more tracking)
                status = "🟢 Available" if not self._is_lock_held(lock_id) else "🔴 Held"
                holder = self._get_lock_holder(lock_id) or "None"
                waiters = len(self._get_lock_waiters(lock_id))
                
                print(f"{lock_id[:19]:<20} {status:<15} {holder[:19]:<20} {waiters:<15}")
        else:
            print("💤 No locks created")
            
        print()
        
        # Lock contention graph
        if self.lock_contention_history:
            print("📊 LOCK CONTENTION OVER TIME:")
            self._draw_simple_graph(list(self.lock_contention_history), "Contention")
            
    def _display_condition_tracker(self):
        """Display condition variable tracking"""
        print("📡 " + "CONDITION VARIABLE TRACKER".center(self.display_width - 4, "═"))
        print()
        
        cvs = self.thread_api.condition_variables
        print(f"🔢 Total Condition Variables: {len(cvs)}")
        print()
        
        if cvs:
            print("📡 CONDITION VARIABLE STATUS:")
            print("─" * 70)
            print(f"{'CV ID':<20} {'Waiting Threads':<20} {'Recent Notifications':<20}")
            print("─" * 70)
            
            for cv_id in cvs:
                waiting_count = len(self._get_cv_waiters(cv_id))
                recent_notifications = len([e for e in list(self.sync_events)[-20:] 
                                          if e.resource_id == cv_id and e.event_type == "notify"])
                
                print(f"{cv_id[:19]:<20} {waiting_count:<20} {recent_notifications:<20}")
        else:
            print("💤 No condition variables created")
            
    def _display_deadlock_detector(self):
        """Display deadlock detection results"""
        print("☠️ " + "DEADLOCK DETECTION SYSTEM".center(self.display_width - 4, "═"))
        print()
        
        if self.potential_deadlocks:
            print("⚠️ POTENTIAL DEADLOCKS DETECTED:")
            print("─" * 80)
            
            for i, (cycle, threads) in enumerate(self.potential_deadlocks):
                print(f"🚨 Deadlock {i+1}:")
                print(f"   Lock Cycle: {' → '.join(cycle)} → {cycle[0]}")
                print(f"   Involved Threads: {', '.join(threads)}")
                print()
        else:
            print("✅ No deadlocks detected")
            print()
            
        # Wait-for graph visualization
        print("🕸️ LOCK DEPENDENCY GRAPH:")
        print("─" * 60)
        
        if self.lock_dependency_graph:
            for thread_id, waiting_locks in self.lock_dependency_graph.items():
                if waiting_locks:
                    locks_str = ", ".join(list(waiting_locks)[:3])
                    if len(waiting_locks) > 3:
                        locks_str += "..."
                    print(f"  {thread_id[:15]} waiting for: {locks_str}")
        else:
            print("  📭 No dependencies")
            
    def _display_performance_graph(self):
        """Display performance metrics graphs"""
        print("📈 " + "PERFORMANCE METRICS".center(self.display_width - 4, "═"))
        print()
        
        # Throughput graph
        if self.throughput_history:
            print("🚀 SYSTEM THROUGHPUT (operations/sec):")
            self._draw_simple_graph(list(self.throughput_history), "Ops/sec")
            print()
            
        # Thread utilization
        if self.thread_utilization_history:
            print("⚡ THREAD UTILIZATION (%):")
            self._draw_simple_graph(list(self.thread_utilization_history), "CPU %")
            print()
            
        # Recent performance summary
        stats = self.thread_api.get_system_stats()
        print("📊 CURRENT METRICS:")
        print("─" * 50)
        print(f"  🔄 Threads Created: {stats['total_threads_created']}")
        print(f"  ✅ Threads Completed: {stats['total_threads_completed']}")
        print(f"  ⚡ Active Threads: {stats['active_threads']}")
        print(f"  🕐 Total CPU Time: {stats['total_cpu_time']:.2f}s")
        
    def _display_timeline_view(self):
        """Display timeline of recent synchronization events"""
        print("⏰ " + "SYNCHRONIZATION TIMELINE".center(self.display_width - 4, "═"))
        print()
        
        recent_events = list(self.sync_events)[-20:]  # Last 20 events
        
        if recent_events:
            print("📅 RECENT SYNCHRONIZATION EVENTS:")
            print("─" * 100)
            print(f"{'Time':<12} {'Thread':<15} {'Event':<18} {'Resource':<15} {'Status':<10} {'Wait':<8}")
            print("─" * 100)
            
            for event in recent_events:
                time_str = f"{event.timestamp:.3f}"[-9:]  # Last 9 chars of timestamp
                status = "✅ Success" if event.success else "❌ Failed"
                wait_str = f"{event.wait_time:.3f}s" if event.wait_time > 0 else "-"
                
                print(f"{time_str:<12} {event.thread_id[:14]:<15} {event.event_type[:17]:<18} "
                      f"{event.resource_id[:14]:<15} {status:<10} {wait_str:<8}")
        else:
            print("📭 No synchronization events recorded")
            
    def _display_menu(self):
        """Display interactive menu"""
        print("\n" + "─" * self.display_width)
        print("🎛️ CONTROLS:")
        print("  [1] Thread Dashboard  [2] Lock Monitor  [3] Condition Tracker")
        print("  [4] Deadlock Detector [5] Performance  [6] Timeline  [Q] Quit")
        print(f"  Current: {self.current_mode.value} | Refresh: {self.refresh_rate}s")
        
    def _draw_simple_graph(self, data: List[float], label: str):
        """Draw a simple ASCII graph"""
        if not data:
            return
            
        max_val = max(data) if data else 1
        min_val = min(data) if data else 0
        graph_height = 8
        graph_width = min(60, len(data))
        
        # Normalize data
        if max_val == min_val:
            normalized = [graph_height // 2] * len(data)
        else:
            normalized = [int((val - min_val) / (max_val - min_val) * graph_height) 
                         for val in data[-graph_width:]]
        
        # Draw graph
        for row in range(graph_height, -1, -1):
            line = f"{(min_val + (max_val - min_val) * row / graph_height):6.1f} │"
            for val in normalized:
                if val >= row:
                    line += "█"
                else:
                    line += " "
            print(line)
            
        # X-axis
        print("       └" + "─" * graph_width)
        print(f"        {label} (last {len(normalized)} samples)")
        
    def _update_performance_metrics(self):
        """Update performance tracking metrics"""
        stats = self.thread_api.get_system_stats()
        
        # Calculate throughput (completed threads per second)
        if hasattr(self, '_last_completed'):
            completed_delta = stats['total_threads_completed'] - self._last_completed
            throughput = completed_delta / self.refresh_rate
            self.throughput_history.append(throughput)
        self._last_completed = stats['total_threads_completed']
        
        # Calculate lock contention (simplified)
        blocked_threads = len([t for t in self.thread_api.list_threads() 
                              if t.state == ThreadState.BLOCKED])
        contention = blocked_threads / max(stats['active_threads'], 1) * 100
        self.lock_contention_history.append(contention)
        
        # Thread utilization
        self.thread_utilization_history.append(stats['average_cpu_utilization'])
        
    def _update_lock_dependency_graph(self, event: SyncEvent):
        """Update lock dependency graph for deadlock detection"""
        if event.event_type == "lock_acquire":
            if event.thread_id not in self.lock_dependency_graph:
                self.lock_dependency_graph[event.thread_id] = set()
            if not event.success:
                self.lock_dependency_graph[event.thread_id].add(event.resource_id)
        elif event.event_type == "lock_release":
            if event.thread_id in self.lock_dependency_graph:
                self.lock_dependency_graph[event.thread_id].discard(event.resource_id)
                
    def _detect_potential_deadlocks(self):
        """Simple deadlock detection using cycle detection"""
        # This is a simplified implementation
        # In practice, would use more sophisticated algorithms like DFS cycle detection
        self.potential_deadlocks.clear()
        
        # Check for circular dependencies
        for thread_id, waiting_locks in self.lock_dependency_graph.items():
            for lock_id in waiting_locks:
                holder = self._get_lock_holder(lock_id)
                if holder and holder in self.lock_dependency_graph:
                    holder_waiting = self.lock_dependency_graph[holder]
                    # Check if holder is waiting for any lock that this thread holds
                    thread_locks = set(self.thread_api.get_thread_info(thread_id).locks_held) if thread_id in self.thread_api.threads else set()
                    if holder_waiting.intersection(thread_locks):
                        cycle = [lock_id, list(holder_waiting)[0] if holder_waiting else "unknown"]
                        threads = [thread_id, holder]
                        if (cycle, threads) not in self.potential_deadlocks:
                            self.potential_deadlocks.append((cycle, threads))
                            
    def _is_lock_held(self, lock_id: str) -> bool:
        """Check if a lock is currently held"""
        # Simplified check - in practice would need better tracking
        return any(lock_id in thread.locks_held 
                  for thread in self.thread_api.list_threads())
                  
    def _get_lock_holder(self, lock_id: str) -> Optional[str]:
        """Get the thread holding a specific lock"""
        for thread in self.thread_api.list_threads():
            if lock_id in thread.locks_held:
                return thread.thread_id
        return None
        
    def _get_lock_waiters(self, lock_id: str) -> List[str]:
        """Get threads waiting for a specific lock"""
        return [thread.thread_id for thread in self.thread_api.list_threads()
                if thread.waiting_for_lock == lock_id]
                
    def _get_cv_waiters(self, cv_id: str) -> List[str]:
        """Get threads waiting on a condition variable"""
        return [thread.thread_id for thread in self.thread_api.list_threads()
                if thread.state == ThreadState.WAITING]
                
    def switch_mode(self, mode: VisualizationMode):
        """Switch visualization mode"""
        self.current_mode = mode
        
    def set_refresh_rate(self, rate: float):
        """Set the refresh rate in seconds"""
        self.refresh_rate = max(0.1, rate)
        
    def export_monitoring_data(self, filename: str):
        """Export monitoring data to JSON file"""
        data = {
            "timestamp": time.time(),
            "sync_events": [
                {
                    "timestamp": event.timestamp,
                    "thread_id": event.thread_id,
                    "event_type": event.event_type,
                    "resource_id": event.resource_id,
                    "success": event.success,
                    "wait_time": event.wait_time
                }
                for event in self.sync_events
            ],
            "performance_metrics": {
                "throughput_history": list(self.throughput_history),
                "lock_contention_history": list(self.lock_contention_history),
                "thread_utilization_history": list(self.thread_utilization_history)
            },
            "system_stats": self.thread_api.get_system_stats(),
            "potential_deadlocks": self.potential_deadlocks
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"📊 Monitoring data exported to {filename}")

class InteractiveMonitor:
    """Interactive monitoring interface for user control"""
    
    def __init__(self, visualizer: SynchronizationVisualizer):
        self.visualizer = visualizer
        self.running = False
        self.input_thread = None
        
    def start_interactive_mode(self):
        """Start interactive monitoring mode"""
        if self.running:
            return
            
        self.running = True
        self.visualizer.start_monitoring()
        
        print("🎮 Interactive monitoring started!")
        print("📝 Use number keys to switch views, 'q' to quit")
        
        self.input_thread = threading.Thread(target=self._input_handler, daemon=True)
        self.input_thread.start()
        
    def stop_interactive_mode(self):
        """Stop interactive monitoring"""
        self.running = False
        self.visualizer.stop_monitoring()
        
    def _input_handler(self):
        """Handle user input for mode switching"""
        while self.running:
            try:
                # Note: In a real terminal application, you'd use proper input handling
                # This is simplified for demonstration
                key = input().strip().lower()
                
                if key == 'q':
                    self.stop_interactive_mode()
                    break
                elif key == '1':
                    self.visualizer.switch_mode(VisualizationMode.THREAD_DASHBOARD)
                elif key == '2':
                    self.visualizer.switch_mode(VisualizationMode.LOCK_MONITOR)
                elif key == '3':
                    self.visualizer.switch_mode(VisualizationMode.CONDITION_TRACKER)
                elif key == '4':
                    self.visualizer.switch_mode(VisualizationMode.DEADLOCK_DETECTOR)
                elif key == '5':
                    self.visualizer.switch_mode(VisualizationMode.PERFORMANCE_GRAPH)
                elif key == '6':
                    self.visualizer.switch_mode(VisualizationMode.TIMELINE_VIEW)
                elif key.startswith('export'):
                    filename = f"sync_monitoring_{int(time.time())}.json"
                    self.visualizer.export_monitoring_data(filename)
                    
            except (EOFError, KeyboardInterrupt):
                self.stop_interactive_mode()
                break
            except Exception as e:
                print(f"❌ Input error: {e}")
                
        print("🛑 Interactive monitoring stopped.") 