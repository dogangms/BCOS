#!/usr/bin/env python3
"""
Integrated Process and Memory Manager for Decentralized AI Node Operating System
Combines process management with comprehensive memory management
"""

import time
import threading
import uuid
from typing import Dict, List, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor
import logging

from process_control_block import ProcessControlBlock, ProcessState, ProcessType
from schedulers import Scheduler, FIFOScheduler, RoundRobinScheduler, PriorityScheduler, MLFQScheduler
from memory_manager import MemoryManager, MemoryType
from memory_visualizer import MemoryVisualizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedProcessManager:
    """
    Integrated Process and Memory Manager for Decentralized AI Node OS
    Combines process lifecycle management with comprehensive memory management
    """
    
    def __init__(self, scheduler: Scheduler = None, max_workers: int = 4,
                 total_memory: int = 1024*1024*1024, page_size: int = 4096):
        # Process management
        self.scheduler = scheduler or RoundRobinScheduler()
        self.processes: Dict[int, ProcessControlBlock] = {}
        self.next_pid = 1
        self.running_process: Optional[ProcessControlBlock] = None
        self.max_workers = max_workers
        
        # Memory management integration
        self.memory_manager = MemoryManager(total_memory, page_size)
        self.memory_visualizer = MemoryVisualizer(self.memory_manager)
        
        # Thread management
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.scheduler_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.scheduler_lock = threading.Lock()
        
        # Performance metrics
        self.total_context_switches = 0
        self.start_time = time.time()
        
        # Memory allocation tracking for processes
        self.process_memory_allocations: Dict[int, List[int]] = {}  # pid -> [virtual_addresses]
        
        # Node-specific attributes for Decentralized AI
        self.node_id = str(uuid.uuid4())
        self.ai_model_cache = {}
        self.network_connections = {}
        
        logger.info(f"Integrated ProcessManager initialized with {self.scheduler.name} scheduler")
        logger.info(f"Memory Manager: {total_memory // (1024*1024)} MB, Page size: {page_size} bytes")
    
    def create_process(self, name: str, process_type: ProcessType, 
                      target_function: Callable, args: tuple = (), 
                      priority: int = 0, memory_required: int = 1024*1024,
                      memory_type: MemoryType = None, **kwargs) -> Optional[int]:
        """
        Create a new process with integrated memory management
        
        Args:
            name: Process name
            process_type: Type of process (AI_INFERENCE, etc.)
            target_function: Function to execute
            args: Arguments for the function
            priority: Process priority
            memory_required: Memory requirement in bytes
            memory_type: Type of memory to allocate
            **kwargs: Additional process attributes
        
        Returns:
            Process ID if successful, None otherwise
        """
        
        with self.scheduler_lock:
            pid = self._generate_pid()
            
            # Determine memory type based on process type if not specified
            if memory_type is None:
                memory_type = self._get_memory_type_for_process(process_type)
            
            # Allocate memory through memory manager
            virtual_address = self.memory_manager.allocate_memory(
                pid, memory_required, memory_type
            )
            
            if virtual_address is None:
                logger.warning(f"Insufficient memory for process {name} ({memory_required} bytes)")
                return None
            
            # Create PCB
            pcb = ProcessControlBlock(
                pid=pid,
                name=name,
                process_type=process_type,
                priority=priority,
                memory_required=memory_required
            )
            
            # Add memory management attributes to PCB
            pcb.virtual_base_address = virtual_address
            pcb.memory_type = memory_type
            pcb.allocated_memory = memory_required
            
            # Track memory allocations
            self.process_memory_allocations[pid] = [virtual_address]
            
            # Set additional attributes
            for key, value in kwargs.items():
                setattr(pcb, key, value)
            
            # Create and configure thread
            pcb.thread = threading.Thread(
                target=self._process_wrapper,
                args=(pcb, target_function, args),
                name=f"Process-{pid}-{name}"
            )
            
            # Store process
            self.processes[pid] = pcb
            
            # Add to scheduler
            self.scheduler.add_process(pcb)
            
            logger.info(f"Created process {pid}: {name} ({process_type.value}) at 0x{virtual_address:08X}")
            return pid
    
    def _get_memory_type_for_process(self, process_type: ProcessType) -> MemoryType:
        """Map process type to appropriate memory type"""
        mapping = {
            ProcessType.AI_INFERENCE: MemoryType.AI_MODEL,
            ProcessType.DATA_PROCESSING: MemoryType.AI_DATA,
            ProcessType.BLOCKCHAIN_VALIDATOR: MemoryType.BLOCKCHAIN_LEDGER,
            ProcessType.NETWORK_NODE: MemoryType.NETWORK_BUFFER,
            ProcessType.SYSTEM: MemoryType.SYSTEM,
            ProcessType.USER: MemoryType.USER
        }
        return mapping.get(process_type, MemoryType.USER)
    
    def allocate_additional_memory(self, pid: int, size: int, 
                                 memory_type: MemoryType = None) -> Optional[int]:
        """Allocate additional memory for an existing process"""
        if pid not in self.processes:
            return None
        
        pcb = self.processes[pid]
        if memory_type is None:
            memory_type = pcb.memory_type
        
        virtual_address = self.memory_manager.allocate_memory(pid, size, memory_type)
        
        if virtual_address is not None:
            # Track additional allocation
            if pid in self.process_memory_allocations:
                self.process_memory_allocations[pid].append(virtual_address)
            else:
                self.process_memory_allocations[pid] = [virtual_address]
            
            pcb.allocated_memory += size
            logger.info(f"Allocated additional {size} bytes for process {pid} at 0x{virtual_address:08X}")
        
        return virtual_address
    
    def access_process_memory(self, pid: int, virtual_address: int, write: bool = False) -> bool:
        """Access memory for a process"""
        if pid not in self.processes:
            return False
        
        success, data = self.memory_manager.access_memory(pid, virtual_address, write)
        
        if success:
            # Update process statistics
            pcb = self.processes[pid]
            if not hasattr(pcb, 'context_switches'):
                pcb.context_switches = 0
            pcb.context_switches += 1  # Simulated memory access overhead
        
        return success
    
    def _process_wrapper(self, pcb: ProcessControlBlock, target_function: Callable, args: tuple):
        """Wrapper function for process execution with memory management"""
        try:
            pcb.set_state(ProcessState.RUNNING)
            pcb.is_active = True
            
            # Simulate memory access at process start
            if hasattr(pcb, 'virtual_base_address'):
                self.access_process_memory(pcb.pid, pcb.virtual_base_address)
            
            # Execute the target function
            result = target_function(*args)
            
            # Process completed successfully
            pcb.set_state(ProcessState.TERMINATED)
            
            if pcb.completion_callback:
                pcb.completion_callback(pcb.pid, result)
                
        except Exception as e:
            logger.error(f"Process {pcb.pid} ({pcb.name}) failed: {e}")
            pcb.set_state(ProcessState.TERMINATED)
        finally:
            pcb.is_active = False
            self._cleanup_process(pcb.pid)
    
    def terminate_process(self, pid: int, force: bool = False) -> bool:
        """Terminate a process and clean up its memory"""
        with self.scheduler_lock:
            if pid not in self.processes:
                logger.warning(f"Process {pid} not found")
                return False
            
            pcb = self.processes[pid]
            
            if force or pcb.state in [ProcessState.NEW, ProcessState.READY]:
                # Can terminate immediately
                pcb.set_state(ProcessState.TERMINATED)
                self.scheduler.remove_process(pid)
                self._cleanup_process(pid)
                logger.info(f"Terminated process {pid}")
                return True
            
            elif pcb.state == ProcessState.RUNNING:
                # Need to interrupt running process
                if pcb.thread and pcb.thread.is_alive():
                    pcb.set_state(ProcessState.TERMINATED)
                    logger.info(f"Marked process {pid} for termination")
                return True
            
            return False
    
    def suspend_process(self, pid: int) -> bool:
        """Suspend a process"""
        with self.scheduler_lock:
            if pid not in self.processes:
                return False
            
            pcb = self.processes[pid]
            if pcb.state in [ProcessState.READY, ProcessState.RUNNING]:
                pcb.set_state(ProcessState.SUSPENDED)
                self.scheduler.remove_process(pid)
                logger.info(f"Suspended process {pid}")
                return True
            return False
    
    def resume_process(self, pid: int) -> bool:
        """Resume a suspended process"""
        with self.scheduler_lock:
            if pid not in self.processes:
                return False
            
            pcb = self.processes[pid]
            if pcb.state == ProcessState.SUSPENDED:
                self.scheduler.add_process(pcb)
                logger.info(f"Resumed process {pid}")
                return True
            return False
    
    def start_scheduler(self):
        """Start the process scheduler"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            name="ProcessScheduler"
        )
        self.scheduler_thread.start()
        logger.info("Process scheduler started")
    
    def stop_scheduler(self):
        """Stop the process scheduler"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("Process scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                with self.scheduler_lock:
                    next_process = self.scheduler.get_next_process()
                    
                    if next_process and next_process.state == ProcessState.READY:
                        self._context_switch(next_process)
                
                time.sleep(0.01)  # 10ms scheduling quantum
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
    
    def _context_switch(self, new_process: ProcessControlBlock):
        """Perform context switch with memory access simulation"""
        # Suspend current process if any
        if self.running_process and self.running_process != new_process:
            if self.running_process.state == ProcessState.RUNNING:
                self.running_process.set_state(ProcessState.READY)
        
        # Switch to new process
        old_process = self.running_process
        self.running_process = new_process
        
        if new_process.state == ProcessState.READY:
            new_process.set_state(ProcessState.RUNNING)
            
            # Start thread if not already started
            if not new_process.thread.is_alive():
                try:
                    new_process.thread.start()
                except RuntimeError:
                    # Thread already started, this is normal
                    pass
        
        # Simulate memory context switch overhead
        if hasattr(new_process, 'virtual_base_address'):
            self.access_process_memory(new_process.pid, new_process.virtual_base_address)
        
        self.total_context_switches += 1
        
        # Log context switch
        old_pid = old_process.pid if old_process else "None"
        logger.debug(f"Context switch: {old_pid} -> {new_process.pid}")
    
    def _cleanup_process(self, pid: int):
        """Clean up process and its memory allocations"""
        if pid in self.processes:
            pcb = self.processes[pid]
            
            # Clean up memory allocations
            self.memory_manager.cleanup_process_memory(pid)
            
            # Remove tracking
            if pid in self.process_memory_allocations:
                del self.process_memory_allocations[pid]
            
            # Remove from scheduler
            self.scheduler.remove_process(pid)
            
            # Remove from process list
            del self.processes[pid]
            
            logger.info(f"Cleaned up process {pid} ({pcb.name})")
    
    def _generate_pid(self) -> int:
        """Generate next process ID"""
        pid = self.next_pid
        self.next_pid += 1
        return pid
    
    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get detailed process information including memory"""
        if pid not in self.processes:
            return None
        
        pcb = self.processes[pid]
        memory_info = self.memory_manager.get_process_memory_info(pid)
        
        return {
            'pid': pcb.pid,
            'name': pcb.name,
            'state': pcb.state.value,
            'process_type': pcb.process_type.value,
            'priority': pcb.priority,
            'creation_time': pcb.creation_time,
            'cpu_time': pcb.cpu_time_used,
            'context_switches': getattr(pcb, 'context_switches', 0),
            'memory_required': pcb.memory_required,
            'memory_info': memory_info,
            'virtual_base_address': getattr(pcb, 'virtual_base_address', None),
            'memory_type': getattr(pcb, 'memory_type', None),
            'allocated_memory': getattr(pcb, 'allocated_memory', 0)
        }
    
    def list_processes(self) -> List[Dict[str, Any]]:
        """List all processes with memory information"""
        return [self.get_process_info(pid) for pid in self.processes.keys()]
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        memory_stats = self.memory_manager.get_memory_statistics()
        
        return {
            'node_id': self.node_id,
            'scheduler': self.scheduler.name,
            'total_processes': len(self.processes),
            'running_processes': len([p for p in self.processes.values() if p.state == ProcessState.RUNNING]),
            'context_switches': self.total_context_switches,
            'uptime': time.time() - self.start_time,
            'memory_statistics': memory_stats,
            'scheduler_statistics': self.scheduler.get_statistics() if hasattr(self.scheduler, 'get_statistics') else {}
        }
    
    def display_full_dashboard(self):
        """Display comprehensive system dashboard"""
        print("═" * 120)
        print("🚀 DECENTRALIZED AI NODE OPERATING SYSTEM - INTEGRATED DASHBOARD")
        print("═" * 120)
        
        # System overview
        system_info = self.get_system_info()
        print(f"🆔 Node ID: {system_info['node_id'][:8]}...")
        print(f"📊 Scheduler: {system_info['scheduler']} | Processes: {system_info['total_processes']} | "
              f"Context Switches: {system_info['context_switches']}")
        
        # Process information
        print("\n📋 ACTIVE PROCESSES")
        print("-" * 120)
        print(f"{'PID':<6} {'Name':<20} {'Type':<15} {'State':<12} {'Memory':<10} {'Virtual Addr':<12} {'Mem Type'}")
        print("-" * 120)
        
        for process_info in self.list_processes():
            if process_info:
                memory_mb = (process_info.get('allocated_memory', 0)) // (1024 * 1024)
                virtual_addr = process_info.get('virtual_base_address')
                addr_str = f"0x{virtual_addr:08X}" if virtual_addr else "None"
                mem_type = process_info.get('memory_type')
                mem_type_str = mem_type.value if mem_type else "None"
                
                print(f"{process_info['pid']:<6} {process_info['name']:<20} {process_info['process_type']:<15} "
                      f"{process_info['state']:<12} {memory_mb:<10} {addr_str:<12} {mem_type_str}")
        
        # Memory dashboard
        print("\n")
        self.memory_visualizer.display_memory_header()
        self.memory_visualizer.display_memory_pools()
        self.memory_visualizer.display_ai_memory_constraints()
    
    def change_scheduler(self, new_scheduler: Scheduler):
        """Change the scheduling algorithm"""
        with self.scheduler_lock:
            # Migrate all processes to new scheduler
            old_processes = []
            while True:
                process = self.scheduler.get_next_process()
                if process is None:
                    break
                old_processes.append(process)
            
            # Set new scheduler
            self.scheduler = new_scheduler
            
            # Add processes to new scheduler
            for process in old_processes:
                self.scheduler.add_process(process)
            
            logger.info(f"Changed scheduler to {new_scheduler.name}")
    
    def trigger_memory_defragmentation(self) -> int:
        """Trigger memory defragmentation"""
        pages_moved = self.memory_manager.defragment_memory()
        logger.info(f"Memory defragmentation completed: {pages_moved} pages moved")
        return pages_moved
    
    def export_system_state(self, filename: str = None):
        """Export complete system state including processes and memory"""
        self.memory_visualizer.export_memory_state(filename)
    
    def start_memory_monitoring(self, refresh_interval: float = 2.0):
        """Start real-time memory monitoring"""
        self.memory_visualizer.real_time_memory_monitor(refresh_interval)
    
    def shutdown(self):
        """Shutdown the integrated process and memory manager"""
        logger.info("Shutting down Integrated Process Manager...")
        
        # Stop scheduler
        self.stop_scheduler()
        
        # Terminate all processes
        for pid in list(self.processes.keys()):
            self.terminate_process(pid, force=True)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Clean up memory
        for pid in list(self.process_memory_allocations.keys()):
            self.memory_manager.cleanup_process_memory(pid)
        
        logger.info("Integrated Process Manager shutdown complete") 