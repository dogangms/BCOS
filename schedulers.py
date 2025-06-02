import time
from abc import ABC, abstractmethod
from collections import deque
from typing import List, Optional, Dict
import heapq
from process_control_block import ProcessControlBlock, ProcessState

class Scheduler(ABC):
    """Abstract base class for all schedulers"""
    
    def __init__(self, name: str):
        self.name = name
        self.total_processes = 0
        self.completed_processes = 0
        self.total_wait_time = 0.0
        self.total_turnaround_time = 0.0
    
    @abstractmethod
    def add_process(self, pcb: ProcessControlBlock):
        """Add a process to the scheduler"""
        pass
    
    @abstractmethod
    def get_next_process(self) -> Optional[ProcessControlBlock]:
        """Get the next process to run"""
        pass
    
    @abstractmethod
    def remove_process(self, pid: int) -> Optional[ProcessControlBlock]:
        """Remove a process from the scheduler"""
        pass
    
    @abstractmethod
    def is_empty(self) -> bool:
        """Check if scheduler has any processes"""
        pass
    
    def get_statistics(self) -> Dict[str, float]:
        """Get scheduler performance statistics"""
        if self.completed_processes == 0:
            return {
                'average_wait_time': 0.0,
                'average_turnaround_time': 0.0,
                'throughput': 0.0
            }
        
        return {
            'average_wait_time': self.total_wait_time / self.completed_processes,
            'average_turnaround_time': self.total_turnaround_time / self.completed_processes,
            'throughput': self.completed_processes / (time.time() - self._start_time) if hasattr(self, '_start_time') else 0.0
        }

class FIFOScheduler(Scheduler):
    """First In, First Out (FCFS) Scheduler"""
    
    def __init__(self):
        super().__init__("FIFO")
        self.ready_queue = deque()
        self._start_time = time.time()
    
    def add_process(self, pcb: ProcessControlBlock):
        """Add process to the end of the FIFO queue"""
        pcb.set_state(ProcessState.READY)
        self.ready_queue.append(pcb)
        self.total_processes += 1
    
    def get_next_process(self) -> Optional[ProcessControlBlock]:
        """Get the first process in the queue"""
        if self.ready_queue:
            pcb = self.ready_queue.popleft()
            pcb.set_state(ProcessState.RUNNING)
            return pcb
        return None
    
    def remove_process(self, pid: int) -> Optional[ProcessControlBlock]:
        """Remove process with given PID from queue"""
        for i, pcb in enumerate(self.ready_queue):
            if pcb.pid == pid:
                removed_pcb = self.ready_queue[i]
                del self.ready_queue[i]
                return removed_pcb
        return None
    
    def is_empty(self) -> bool:
        return len(self.ready_queue) == 0
    
    def get_queue_info(self) -> List[Dict]:
        """Get information about processes in queue"""
        return [pcb.get_process_info() for pcb in self.ready_queue]

class RoundRobinScheduler(Scheduler):
    """Round Robin Scheduler with configurable time quantum"""
    
    def __init__(self, time_quantum: int = 100):
        super().__init__("Round Robin")
        self.time_quantum = time_quantum  # milliseconds
        self.ready_queue = deque()
        self.current_process: Optional[ProcessControlBlock] = None
        self._start_time = time.time()
    
    def add_process(self, pcb: ProcessControlBlock):
        """Add process to the Round Robin queue"""
        pcb.set_state(ProcessState.READY)
        pcb.remaining_time_quantum = self.time_quantum
        self.ready_queue.append(pcb)
        self.total_processes += 1
    
    def get_next_process(self) -> Optional[ProcessControlBlock]:
        """Get next process, implementing round robin logic"""
        if self.ready_queue:
            pcb = self.ready_queue.popleft()
            pcb.set_state(ProcessState.RUNNING)
            pcb.remaining_time_quantum = self.time_quantum
            self.current_process = pcb
            return pcb
        return None
    
    def preempt_current_process(self):
        """Preempt current process and put it back in queue"""
        if self.current_process:
            self.current_process.set_state(ProcessState.READY)
            self.current_process.remaining_time_quantum = self.time_quantum
            self.ready_queue.append(self.current_process)
            self.current_process = None
    
    def remove_process(self, pid: int) -> Optional[ProcessControlBlock]:
        """Remove process with given PID"""
        # Check current process
        if self.current_process and self.current_process.pid == pid:
            removed = self.current_process
            self.current_process = None
            return removed
        
        # Check ready queue
        for i, pcb in enumerate(self.ready_queue):
            if pcb.pid == pid:
                removed_pcb = self.ready_queue[i]
                del self.ready_queue[i]
                return removed_pcb
        return None
    
    def is_empty(self) -> bool:
        return len(self.ready_queue) == 0 and self.current_process is None

class PriorityScheduler(Scheduler):
    """Priority-based Scheduler using heap queue"""
    
    def __init__(self, preemptive: bool = True):
        super().__init__("Priority")
        self.ready_queue = []  # Min-heap (we'll use negative priority for max-heap behavior)
        self.preemptive = preemptive
        self.current_process: Optional[ProcessControlBlock] = None
        self._counter = 0  # For tie-breaking
        self._start_time = time.time()
    
    def add_process(self, pcb: ProcessControlBlock):
        """Add process to priority queue"""
        pcb.set_state(ProcessState.READY)
        # Use negative priority for max-heap behavior, counter for FIFO tie-breaking
        heapq.heappush(self.ready_queue, (-pcb.priority, self._counter, pcb))
        self._counter += 1
        self.total_processes += 1
        
        # Preemption check
        if self.preemptive and self.current_process:
            if pcb.priority > self.current_process.priority:
                # Higher priority process arrived, preempt current
                self.preempt_current_process()
    
    def get_next_process(self) -> Optional[ProcessControlBlock]:
        """Get highest priority process"""
        if self.ready_queue:
            _, _, pcb = heapq.heappop(self.ready_queue)
            pcb.set_state(ProcessState.RUNNING)
            self.current_process = pcb
            return pcb
        return None
    
    def preempt_current_process(self):
        """Preempt current process and return to queue"""
        if self.current_process:
            self.current_process.set_state(ProcessState.READY)
            heapq.heappush(self.ready_queue, 
                          (-self.current_process.priority, self._counter, self.current_process))
            self._counter += 1
            self.current_process = None
    
    def remove_process(self, pid: int) -> Optional[ProcessControlBlock]:
        """Remove process with given PID"""
        # Check current process
        if self.current_process and self.current_process.pid == pid:
            removed = self.current_process
            self.current_process = None
            return removed
        
        # Check ready queue (inefficient but necessary for heap)
        for i, (_, _, pcb) in enumerate(self.ready_queue):
            if pcb.pid == pid:
                removed_pcb = pcb
                del self.ready_queue[i]
                heapq.heapify(self.ready_queue)  # Restore heap property
                return removed_pcb
        return None
    
    def is_empty(self) -> bool:
        return len(self.ready_queue) == 0 and self.current_process is None

class MLFQScheduler(Scheduler):
    """Multi-Level Feedback Queue Scheduler"""
    
    def __init__(self, num_levels: int = 3, time_quanta: List[int] = None):
        super().__init__("MLFQ")
        self.num_levels = num_levels
        self.time_quanta = time_quanta or [50, 100, 200]  # Different quantum for each level
        
        # Create multiple queues
        self.queues = [deque() for _ in range(num_levels)]
        self.current_level = 0
        self.current_process: Optional[ProcessControlBlock] = None
        self.aging_threshold = 1000  # milliseconds before promoting process
        self._start_time = time.time()
    
    def add_process(self, pcb: ProcessControlBlock):
        """Add new process to highest priority queue (level 0)"""
        pcb.set_state(ProcessState.READY)
        pcb.queue_level = 0
        pcb.time_in_level = 0
        pcb.remaining_time_quantum = self.time_quanta[0]
        self.queues[0].append(pcb)
        self.total_processes += 1
    
    def get_next_process(self) -> Optional[ProcessControlBlock]:
        """Get next process using MLFQ logic"""
        # Check queues from highest to lowest priority
        for level in range(self.num_levels):
            if self.queues[level]:
                pcb = self.queues[level].popleft()
                pcb.set_state(ProcessState.RUNNING)
                pcb.remaining_time_quantum = self.time_quanta[level]
                self.current_process = pcb
                self.current_level = level
                return pcb
        return None
    
    def preempt_current_process(self, completed: bool = False):
        """Handle process preemption in MLFQ"""
        if not self.current_process:
            return
        
        if completed:
            # Process completed normally
            self.current_process.set_state(ProcessState.TERMINATED)
        else:
            # Process was preempted, move to lower priority queue
            current_level = getattr(self.current_process, 'queue_level', 0)
            
            if current_level < self.num_levels - 1:
                # Move to lower priority queue
                new_level = current_level + 1
                self.current_process.queue_level = new_level
                self.current_process.remaining_time_quantum = self.time_quanta[new_level]
            else:
                # Already at lowest level, use round robin
                self.current_process.remaining_time_quantum = self.time_quanta[-1]
            
            self.current_process.set_state(ProcessState.READY)
            self.queues[self.current_process.queue_level].append(self.current_process)
        
        self.current_process = None
    
    def age_processes(self):
        """Implement aging to prevent starvation"""
        current_time = time.time() * 1000  # Convert to milliseconds
        
        for level in range(1, self.num_levels):
            processes_to_promote = []
            for pcb in list(self.queues[level]):
                if (current_time - pcb.last_cpu_time * 1000) > self.aging_threshold:
                    processes_to_promote.append(pcb)
            
            # Promote aged processes
            for pcb in processes_to_promote:
                self.queues[level].remove(pcb)
                pcb.queue_level = max(0, level - 1)
                self.queues[pcb.queue_level].append(pcb)
    
    def remove_process(self, pid: int) -> Optional[ProcessControlBlock]:
        """Remove process from MLFQ"""
        # Check current process
        if self.current_process and self.current_process.pid == pid:
            removed = self.current_process
            self.current_process = None
            return removed
        
        # Check all queues
        for level, queue in enumerate(self.queues):
            for i, pcb in enumerate(queue):
                if pcb.pid == pid:
                    removed_pcb = queue[i]
                    del queue[i]
                    return removed_pcb
        return None
    
    def is_empty(self) -> bool:
        return all(len(queue) == 0 for queue in self.queues) and self.current_process is None
    
    def get_queue_info(self) -> Dict[int, List[Dict]]:
        """Get information about all queue levels"""
        return {
            level: [pcb.get_process_info() for pcb in queue]
            for level, queue in enumerate(self.queues)
        } 