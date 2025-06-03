"""
Decentralized AI Node Operating System - Step 3: Thread API
A basic thread API implementation for the AI Node OS with synchronization support.
"""

import threading
import time
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from queue import Queue
import random

class ThreadState(Enum):
    """Thread states for the AI Node OS"""
    CREATED = "CREATED"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"
    SUSPENDED = "SUSPENDED"

class ThreadType(Enum):
    """AI Node specific thread types"""
    AI_WORKER = "🤖 AI Worker"
    BLOCKCHAIN_MINER = "⛏️ Blockchain Miner"
    NETWORK_HANDLER = "🌐 Network Handler"
    DATA_PROCESSOR = "📊 Data Processor"
    CONSENSUS_NODE = "🔗 Consensus Node"
    SMART_CONTRACT = "📜 Smart Contract"
    SYSTEM_DAEMON = "⚙️ System Daemon"
    USER_THREAD = "👤 User Thread"

class ThreadPriority(Enum):
    """Thread priority levels"""
    CRITICAL = 0    # System critical threads
    HIGH = 1        # Important AI/blockchain operations
    NORMAL = 2      # Regular operations
    LOW = 3         # Background tasks
    IDLE = 4        # Idle time processing

@dataclass
class AIThread:
    """AI Node Thread Control Block"""
    thread_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    thread_type: ThreadType = ThreadType.USER_THREAD
    priority: ThreadPriority = ThreadPriority.NORMAL
    state: ThreadState = ThreadState.CREATED
    parent_thread_id: Optional[str] = None
    
    # Thread execution context
    function: Optional[Callable] = None
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    
    # Timing information
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    cpu_time: float = 0.0
    wait_time: float = 0.0
    
    # Resource usage
    memory_usage: int = 0  # In KB
    network_usage: int = 0  # In bytes
    disk_io: int = 0  # In bytes
    
    # AI/Blockchain specific metrics
    ai_operations: int = 0
    blockchain_transactions: int = 0
    consensus_votes: int = 0
    smart_contract_calls: int = 0
    
    # Thread synchronization
    locks_held: List[str] = field(default_factory=list)
    waiting_for_lock: Optional[str] = None
    
    # Internal threading object
    _thread: Optional[threading.Thread] = None
    _result: Any = None
    _exception: Optional[Exception] = None

class ThreadAPI:
    """
    Basic Thread API for the Decentralized AI Node Operating System
    Provides thread creation, management, and synchronization primitives.
    """
    
    def __init__(self):
        self.threads: Dict[str, AIThread] = {}
        self.running_threads: Dict[str, AIThread] = {}
        self.thread_groups: Dict[str, List[str]] = {}
        
        # Synchronization primitives
        self.locks: Dict[str, threading.Lock] = {}
        self.condition_variables: Dict[str, threading.Condition] = {}
        self.semaphores: Dict[str, threading.Semaphore] = {}
        self.barriers: Dict[str, threading.Barrier] = {}
        
        # Thread scheduling
        self.scheduler_lock = threading.Lock()
        self.thread_counter = 0
        self.max_threads = 100
        
        # Performance metrics
        self.total_threads_created = 0
        self.total_threads_completed = 0
        self.total_cpu_time = 0.0
        self.start_time = time.time()
        
    def create_thread(self, 
                     function: Callable, 
                     args: tuple = (), 
                     kwargs: dict = None,
                     name: str = "",
                     thread_type: ThreadType = ThreadType.USER_THREAD,
                     priority: ThreadPriority = ThreadPriority.NORMAL,
                     parent_id: Optional[str] = None) -> str:
        """Create a new thread"""
        if kwargs is None:
            kwargs = {}
            
        if len(self.threads) >= self.max_threads:
            raise RuntimeError("Maximum thread limit reached")
            
        thread = AIThread(
            name=name or f"Thread-{self.thread_counter}",
            thread_type=thread_type,
            priority=priority,
            parent_thread_id=parent_id,
            function=function,
            args=args,
            kwargs=kwargs
        )
        
        self.threads[thread.thread_id] = thread
        self.thread_counter += 1
        self.total_threads_created += 1
        
        return thread.thread_id
    
    def start_thread(self, thread_id: str) -> bool:
        """Start a thread"""
        if thread_id not in self.threads:
            return False
            
        thread = self.threads[thread_id]
        if thread.state != ThreadState.CREATED:
            return False
            
        def thread_wrapper():
            thread.started_at = time.time()
            thread.state = ThreadState.RUNNING
            self.running_threads[thread_id] = thread
            
            try:
                start_time = time.time()
                result = thread.function(*thread.args, **thread.kwargs)
                thread._result = result
                thread.cpu_time += time.time() - start_time
                
                # Update AI/Blockchain specific metrics
                if thread.thread_type == ThreadType.AI_WORKER:
                    thread.ai_operations += random.randint(10, 100)
                elif thread.thread_type == ThreadType.BLOCKCHAIN_MINER:
                    thread.blockchain_transactions += random.randint(1, 10)
                elif thread.thread_type == ThreadType.CONSENSUS_NODE:
                    thread.consensus_votes += random.randint(5, 20)
                    
            except Exception as e:
                thread._exception = e
            finally:
                thread.finished_at = time.time()
                thread.state = ThreadState.TERMINATED
                if thread_id in self.running_threads:
                    del self.running_threads[thread_id]
                self.total_threads_completed += 1
                self.total_cpu_time += thread.cpu_time
        
        thread._thread = threading.Thread(target=thread_wrapper, name=thread.name)
        thread._thread.daemon = True
        thread._thread.start()
        thread.state = ThreadState.READY
        
        return True
    
    def join_thread(self, thread_id: str, timeout: Optional[float] = None) -> bool:
        """Wait for a thread to complete"""
        if thread_id not in self.threads:
            return False
            
        thread = self.threads[thread_id]
        if thread._thread is None:
            return False
            
        thread._thread.join(timeout)
        return thread.state == ThreadState.TERMINATED
    
    def suspend_thread(self, thread_id: str) -> bool:
        """Suspend a thread (simplified implementation)"""
        if thread_id not in self.threads:
            return False
            
        thread = self.threads[thread_id]
        if thread.state == ThreadState.RUNNING:
            thread.state = ThreadState.SUSPENDED
            return True
        return False
    
    def resume_thread(self, thread_id: str) -> bool:
        """Resume a suspended thread"""
        if thread_id not in self.threads:
            return False
            
        thread = self.threads[thread_id]
        if thread.state == ThreadState.SUSPENDED:
            thread.state = ThreadState.RUNNING
            return True
        return False
    
    def terminate_thread(self, thread_id: str) -> bool:
        """Terminate a thread (graceful)"""
        if thread_id not in self.threads:
            return False
            
        thread = self.threads[thread_id]
        thread.state = ThreadState.TERMINATED
        if thread_id in self.running_threads:
            del self.running_threads[thread_id]
        return True
    
    def get_thread_info(self, thread_id: str) -> Optional[AIThread]:
        """Get thread information"""
        return self.threads.get(thread_id)
    
    def list_threads(self, state_filter: Optional[ThreadState] = None) -> List[AIThread]:
        """List all threads, optionally filtered by state"""
        threads = list(self.threads.values())
        if state_filter:
            threads = [t for t in threads if t.state == state_filter]
        return threads
    
    def list_running_threads(self) -> List[AIThread]:
        """List currently running threads"""
        return list(self.running_threads.values())
    
    # Synchronization Primitives
    
    def create_lock(self, lock_id: str) -> bool:
        """Create a new lock"""
        if lock_id in self.locks:
            return False
        self.locks[lock_id] = threading.Lock()
        return True
    
    def acquire_lock(self, lock_id: str, thread_id: str, blocking: bool = True, timeout: Optional[float] = None) -> bool:
        """Acquire a lock"""
        if lock_id not in self.locks:
            return False
            
        thread = self.threads.get(thread_id)
        if not thread:
            return False
            
        try:
            acquired = self.locks[lock_id].acquire(blocking, timeout or -1)
            if acquired:
                thread.locks_held.append(lock_id)
                thread.waiting_for_lock = None
            else:
                thread.waiting_for_lock = lock_id
                thread.state = ThreadState.BLOCKED
            return acquired
        except:
            return False
    
    def release_lock(self, lock_id: str, thread_id: str) -> bool:
        """Release a lock"""
        if lock_id not in self.locks:
            return False
            
        thread = self.threads.get(thread_id)
        if not thread or lock_id not in thread.locks_held:
            return False
            
        try:
            self.locks[lock_id].release()
            thread.locks_held.remove(lock_id)
            if thread.state == ThreadState.BLOCKED:
                thread.state = ThreadState.READY
            return True
        except:
            return False
    
    def create_condition_variable(self, cv_id: str, lock_id: Optional[str] = None) -> bool:
        """Create a condition variable"""
        if cv_id in self.condition_variables:
            return False
            
        if lock_id and lock_id in self.locks:
            self.condition_variables[cv_id] = threading.Condition(self.locks[lock_id])
        else:
            self.condition_variables[cv_id] = threading.Condition()
        return True
    
    def wait_condition(self, cv_id: str, thread_id: str, timeout: Optional[float] = None) -> bool:
        """Wait on a condition variable"""
        if cv_id not in self.condition_variables:
            return False
            
        thread = self.threads.get(thread_id)
        if not thread:
            return False
            
        thread.state = ThreadState.WAITING
        try:
            result = self.condition_variables[cv_id].wait(timeout)
            thread.state = ThreadState.READY if result else ThreadState.RUNNING
            return result
        except:
            return False
    
    def notify_condition(self, cv_id: str, notify_all: bool = False) -> bool:
        """Notify threads waiting on a condition variable"""
        if cv_id not in self.condition_variables:
            return False
            
        try:
            if notify_all:
                self.condition_variables[cv_id].notify_all()
            else:
                self.condition_variables[cv_id].notify()
            return True
        except:
            return False
    
    def create_semaphore(self, sem_id: str, initial_value: int = 1) -> bool:
        """Create a semaphore"""
        if sem_id in self.semaphores:
            return False
        self.semaphores[sem_id] = threading.Semaphore(initial_value)
        return True
    
    def acquire_semaphore(self, sem_id: str, thread_id: str, blocking: bool = True, timeout: Optional[float] = None) -> bool:
        """Acquire a semaphore"""
        if sem_id not in self.semaphores:
            return False
            
        thread = self.threads.get(thread_id)
        if not thread:
            return False
            
        try:
            acquired = self.semaphores[sem_id].acquire(blocking, timeout)
            if not acquired:
                thread.state = ThreadState.BLOCKED
            return acquired
        except:
            return False
    
    def release_semaphore(self, sem_id: str, thread_id: str) -> bool:
        """Release a semaphore"""
        if sem_id not in self.semaphores:
            return False
            
        try:
            self.semaphores[sem_id].release()
            return True
        except:
            return False
    
    def get_system_stats(self) -> dict:
        """Get system-wide threading statistics"""
        uptime = time.time() - self.start_time
        active_threads = len(self.running_threads)
        
        return {
            "uptime": uptime,
            "total_threads_created": self.total_threads_created,
            "total_threads_completed": self.total_threads_completed,
            "active_threads": active_threads,
            "total_cpu_time": self.total_cpu_time,
            "average_cpu_utilization": (self.total_cpu_time / uptime) * 100 if uptime > 0 else 0,
            "locks_count": len(self.locks),
            "condition_variables_count": len(self.condition_variables),
            "semaphores_count": len(self.semaphores),
            "threads_by_state": self._get_threads_by_state(),
            "threads_by_type": self._get_threads_by_type(),
            "threads_by_priority": self._get_threads_by_priority()
        }
    
    def _get_threads_by_state(self) -> dict:
        """Get thread count by state"""
        state_counts = {}
        for state in ThreadState:
            state_counts[state.value] = len([t for t in self.threads.values() if t.state == state])
        return state_counts
    
    def _get_threads_by_type(self) -> dict:
        """Get thread count by type"""
        type_counts = {}
        for thread_type in ThreadType:
            type_counts[thread_type.value] = len([t for t in self.threads.values() if t.thread_type == thread_type])
        return type_counts
    
    def _get_threads_by_priority(self) -> dict:
        """Get thread count by priority"""
        priority_counts = {}
        for priority in ThreadPriority:
            priority_counts[priority.name] = len([t for t in self.threads.values() if t.priority == priority])
        return priority_counts 