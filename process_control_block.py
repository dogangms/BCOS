import time
from enum import Enum
from typing import Dict, Any, Optional
import threading

class ProcessState(Enum):
    """Enumeration of possible process states"""
    NEW = "new"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"

class ProcessType(Enum):
    """Types of processes in the Decentralized AI Node OS"""
    AI_INFERENCE = "ai_inference"
    DATA_PROCESSING = "data_processing"
    BLOCKCHAIN_VALIDATOR = "blockchain_validator"
    NETWORK_NODE = "network_node"
    SYSTEM = "system"
    USER = "user"

class ProcessControlBlock:
    """
    Process Control Block (PCB) - Contains all information about a process
    """
    
    def __init__(self, pid: int, name: str, process_type: ProcessType, 
                 priority: int = 0, memory_required: int = 1024):
        self.pid = pid  # Process ID
        self.name = name  # Process name
        self.process_type = process_type  # Type of process
        self.state = ProcessState.NEW  # Current state
        self.priority = priority  # Process priority (higher number = higher priority)
        
        # Timing information
        self.creation_time = time.time()
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.cpu_time_used = 0.0
        self.last_cpu_time = 0.0
        
        # Memory management
        self.memory_required = memory_required
        self.memory_allocated = 0
        self.memory_base_address: Optional[int] = None
        
        # Scheduling information
        self.time_quantum = 100  # milliseconds
        self.remaining_time_quantum = 100
        self.wait_time = 0.0
        self.turnaround_time = 0.0
        
        # Context switching
        self.program_counter = 0
        self.cpu_registers: Dict[str, Any] = {}
        
        # Thread management
        self.thread: Optional[threading.Thread] = None
        self.is_active = False
        self.completion_callback = None
        
        # AI Node specific attributes
        self.node_id: Optional[str] = None
        self.resource_requirements: Dict[str, int] = {
            'cpu': 1,
            'memory': memory_required,
            'gpu': 0,
            'network_bandwidth': 0
        }
        
        # Parent-child relationships
        self.parent_pid: Optional[int] = None
        self.child_pids: list = []
        
        # I/O information
        self.io_operations = []
        self.blocked_on_io = False
        
    def set_state(self, new_state: ProcessState):
        """Change process state with timestamp logging"""
        old_state = self.state
        self.state = new_state
        
        if new_state == ProcessState.RUNNING and old_state != ProcessState.RUNNING:
            self.start_time = time.time()
        elif old_state == ProcessState.RUNNING and new_state != ProcessState.RUNNING:
            if self.start_time:
                self.cpu_time_used += time.time() - self.start_time
        elif new_state == ProcessState.TERMINATED:
            self.end_time = time.time()
            if self.creation_time:
                self.turnaround_time = self.end_time - self.creation_time
    
    def allocate_memory(self, base_address: int, size: int):
        """Allocate memory to the process"""
        self.memory_base_address = base_address
        self.memory_allocated = size
    
    def deallocate_memory(self):
        """Deallocate process memory"""
        self.memory_base_address = None
        self.memory_allocated = 0
    
    def add_child(self, child_pid: int):
        """Add a child process"""
        if child_pid not in self.child_pids:
            self.child_pids.append(child_pid)
    
    def remove_child(self, child_pid: int):
        """Remove a child process"""
        if child_pid in self.child_pids:
            self.child_pids.remove(child_pid)
    
    def get_process_info(self) -> Dict[str, Any]:
        """Get comprehensive process information"""
        return {
            'pid': self.pid,
            'name': self.name,
            'type': self.process_type.value,
            'state': self.state.value,
            'priority': self.priority,
            'creation_time': self.creation_time,
            'cpu_time_used': self.cpu_time_used,
            'memory_required': self.memory_required,
            'memory_allocated': self.memory_allocated,
            'turnaround_time': self.turnaround_time,
            'wait_time': self.wait_time,
            'parent_pid': self.parent_pid,
            'child_count': len(self.child_pids),
            'node_id': self.node_id,
            'resource_requirements': self.resource_requirements
        }
    
    def __str__(self):
        return f"PCB[PID:{self.pid}, Name:{self.name}, State:{self.state.value}, Type:{self.process_type.value}]"
    
    def __repr__(self):
        return self.__str__() 