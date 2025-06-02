import time
import threading
import uuid
from typing import Dict, List, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor
import logging

from process_control_block import ProcessControlBlock, ProcessState, ProcessType
from schedulers import Scheduler, FIFOScheduler, RoundRobinScheduler, PriorityScheduler, MLFQScheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessManager:
    """
    Main Process Manager for the Decentralized AI Node Operating System
    Handles process creation, scheduling, switching, and termination
    """
    
    def __init__(self, scheduler: Scheduler = None, max_workers: int = 4):
        self.scheduler = scheduler or RoundRobinScheduler()
        self.processes: Dict[int, ProcessControlBlock] = {}
        self.next_pid = 1
        self.running_process: Optional[ProcessControlBlock] = None
        self.max_workers = max_workers
        
        # Thread management
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.scheduler_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.scheduler_lock = threading.Lock()
        
        # Performance metrics
        self.total_context_switches = 0
        self.start_time = time.time()
        
        # Memory simulation (in KB)
        self.total_memory = 1024 * 1024  # 1GB
        self.available_memory = self.total_memory
        self.memory_map: Dict[int, int] = {}  # pid -> memory size
        
        # Node-specific attributes for Decentralized AI
        self.node_id = str(uuid.uuid4())
        self.ai_model_cache = {}
        self.network_connections = {}
        
        logger.info(f"ProcessManager initialized with {self.scheduler.name} scheduler")
    
    def create_process(self, name: str, process_type: ProcessType, 
                      target_function: Callable, args: tuple = (), 
                      priority: int = 0, memory_required: int = 1024,
                      **kwargs) -> Optional[int]:
        """
        Create a new process
        
        Args:
            name: Process name
            process_type: Type of process (AI_INFERENCE, etc.)
            target_function: Function to execute
            args: Arguments for the function
            priority: Process priority
            memory_required: Memory requirement in KB
            **kwargs: Additional process attributes
        
        Returns:
            Process ID if successful, None otherwise
        """
        
        # Check memory availability
        if memory_required > self.available_memory:
            logger.warning(f"Insufficient memory for process {name}")
            return None
        
        with self.scheduler_lock:
            pid = self._generate_pid()
            
            # Create PCB
            pcb = ProcessControlBlock(
                pid=pid,
                name=name,
                process_type=process_type,
                priority=priority,
                memory_required=memory_required
            )
            
            # Set additional attributes
            for key, value in kwargs.items():
                setattr(pcb, key, value)
            
            # Allocate memory
            self._allocate_memory(pcb)
            
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
            
            logger.info(f"Created process {pid}: {name} ({process_type.value})")
            return pid
    
    def _process_wrapper(self, pcb: ProcessControlBlock, target_function: Callable, args: tuple):
        """Wrapper function for process execution"""
        try:
            pcb.set_state(ProcessState.RUNNING)
            pcb.is_active = True
            
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
        """
        Terminate a process
        
        Args:
            pid: Process ID to terminate
            force: Force termination without cleanup
        
        Returns:
            True if successful, False otherwise
        """
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
                    # Note: Python doesn't support thread interruption
                    # In a real OS, this would send a signal
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
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("Process scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                with self.scheduler_lock:
                    # Age processes if using MLFQ
                    if isinstance(self.scheduler, MLFQScheduler):
                        self.scheduler.age_processes()
                    
                    # Get next process to run
                    next_process = self.scheduler.get_next_process()
                    
                    if next_process and not next_process.is_active:
                        # Context switch
                        self._context_switch(next_process)
                
                # Sleep to prevent busy waiting
                time.sleep(0.01)  # 10ms
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
    
    def _context_switch(self, new_process: ProcessControlBlock):
        """Perform context switch to new process"""
        old_process = self.running_process
        
        if old_process:
            # Save context of old process
            old_process.program_counter += 1
            # In real OS, would save CPU registers
        
        # Switch to new process
        self.running_process = new_process
        self.total_context_switches += 1
        
        # Start the process if it's new
        if new_process.state == ProcessState.READY and not new_process.thread.is_alive():
            new_process.thread.start()
        
        logger.debug(f"Context switch: {old_process.pid if old_process else 'None'} -> {new_process.pid}")
    
    def _cleanup_process(self, pid: int):
        """Clean up terminated process"""
        if pid in self.processes:
            pcb = self.processes[pid]
            
            # Deallocate memory
            self._deallocate_memory(pcb)
            
            # Update scheduler statistics
            self.scheduler.completed_processes += 1
            self.scheduler.total_wait_time += pcb.wait_time
            self.scheduler.total_turnaround_time += pcb.turnaround_time
            
            # Remove from processes
            del self.processes[pid]
            
            logger.info(f"Cleaned up process {pid}")
    
    def _generate_pid(self) -> int:
        """Generate unique process ID"""
        pid = self.next_pid
        self.next_pid += 1
        return pid
    
    def _allocate_memory(self, pcb: ProcessControlBlock):
        """Allocate memory for process"""
        if pcb.memory_required <= self.available_memory:
            # Simulate memory allocation
            base_address = hash(pcb.pid) % 1000000  # Fake address
            pcb.allocate_memory(base_address, pcb.memory_required)
            self.available_memory -= pcb.memory_required
            self.memory_map[pcb.pid] = pcb.memory_required
            return True
        return False
    
    def _deallocate_memory(self, pcb: ProcessControlBlock):
        """Deallocate process memory"""
        if pcb.pid in self.memory_map:
            self.available_memory += self.memory_map[pcb.pid]
            del self.memory_map[pcb.pid]
            pcb.deallocate_memory()
    
    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get information about a specific process"""
        if pid in self.processes:
            return self.processes[pid].get_process_info()
        return None
    
    def list_processes(self) -> List[Dict[str, Any]]:
        """List all processes"""
        return [pcb.get_process_info() for pcb in self.processes.values()]
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            'node_id': self.node_id,
            'scheduler': self.scheduler.name,
            'total_processes': len(self.processes),
            'running_processes': len([p for p in self.processes.values() if p.state == ProcessState.RUNNING]),
            'total_memory': self.total_memory,
            'available_memory': self.available_memory,
            'memory_usage_percent': ((self.total_memory - self.available_memory) / self.total_memory) * 100,
            'context_switches': self.total_context_switches,
            'uptime': time.time() - self.start_time,
            'scheduler_stats': self.scheduler.get_statistics()
        }
    
    def change_scheduler(self, new_scheduler: Scheduler):
        """Change the scheduling algorithm"""
        with self.scheduler_lock:
            # Transfer processes from old scheduler to new one
            old_processes = []
            while not self.scheduler.is_empty():
                process = self.scheduler.get_next_process()
                if process:
                    old_processes.append(process)
            
            self.scheduler = new_scheduler
            
            # Add processes to new scheduler
            for process in old_processes:
                self.scheduler.add_process(process)
            
            logger.info(f"Changed scheduler to {new_scheduler.name}")
    
    def shutdown(self):
        """Shutdown the process manager"""
        logger.info("Shutting down process manager...")
        
        # Stop scheduler
        self.stop_scheduler()
        
        # Terminate all processes
        with self.scheduler_lock:
            pids = list(self.processes.keys())
            for pid in pids:
                self.terminate_process(pid, force=True)
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        
        logger.info("Process manager shutdown complete") 