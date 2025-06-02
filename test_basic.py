#!/usr/bin/env python3
"""
Basic test to verify the process management system components
"""

import time
from process_control_block import ProcessControlBlock, ProcessState, ProcessType
from schedulers import FIFOScheduler, RoundRobinScheduler, PriorityScheduler, MLFQScheduler
from process_manager import ProcessManager
from process_visualizer import ProcessVisualizer

def simple_task(task_name, duration):
    """Simple test task"""
    print(f"Starting task: {task_name}")
    time.sleep(duration)
    print(f"Completed task: {task_name}")
    return f"Result from {task_name}"

def test_pcb():
    """Test Process Control Block"""
    print("Testing Process Control Block...")
    
    pcb = ProcessControlBlock(
        pid=1,
        name="test_process",
        process_type=ProcessType.AI_INFERENCE,
        priority=5,
        memory_required=1024
    )
    
    assert pcb.pid == 1
    assert pcb.name == "test_process"
    assert pcb.state == ProcessState.NEW
    assert pcb.priority == 5
    
    pcb.set_state(ProcessState.READY)
    assert pcb.state == ProcessState.READY
    
    info = pcb.get_process_info()
    assert info['pid'] == 1
    assert info['name'] == "test_process"
    
    print("✅ PCB test passed")

def test_schedulers():
    """Test all schedulers"""
    print("Testing Schedulers...")
    
    # Test FIFO
    fifo = FIFOScheduler()
    pcb1 = ProcessControlBlock(1, "proc1", ProcessType.SYSTEM)
    pcb2 = ProcessControlBlock(2, "proc2", ProcessType.USER)
    
    fifo.add_process(pcb1)
    fifo.add_process(pcb2)
    
    next_proc = fifo.get_next_process()
    assert next_proc.pid == 1  # First in, first out
    
    # Test Round Robin
    rr = RoundRobinScheduler(time_quantum=1000)
    rr.add_process(ProcessControlBlock(3, "proc3", ProcessType.AI_INFERENCE))
    assert not rr.is_empty()
    
    # Test Priority
    priority = PriorityScheduler()
    high_priority = ProcessControlBlock(4, "high", ProcessType.SYSTEM, priority=10)
    low_priority = ProcessControlBlock(5, "low", ProcessType.USER, priority=1)
    
    priority.add_process(low_priority)
    priority.add_process(high_priority)
    
    next_proc = priority.get_next_process()
    assert next_proc.pid == 4  # Higher priority should come first
    
    # Test MLFQ
    mlfq = MLFQScheduler(num_levels=3)
    mlfq.add_process(ProcessControlBlock(6, "mlfq_test", ProcessType.DATA_PROCESSING))
    assert not mlfq.is_empty()
    
    print("✅ Scheduler tests passed")

def test_process_manager():
    """Test Process Manager"""
    print("Testing Process Manager...")
    
    manager = ProcessManager(FIFOScheduler())
    manager.start_scheduler()
    
    # Create a test process
    pid = manager.create_process(
        name="test_process",
        process_type=ProcessType.AI_INFERENCE,
        target_function=simple_task,
        args=("test_task", 0.5),
        priority=1
    )
    
    assert pid is not None
    assert pid in manager.processes
    
    # Wait for process to complete
    time.sleep(2)
    
    # Get system info
    system_info = manager.get_system_info()
    assert 'node_id' in system_info
    assert 'scheduler' in system_info
    
    manager.shutdown()
    print("✅ Process Manager test passed")

def test_visualizer():
    """Test Process Visualizer"""
    print("Testing Process Visualizer...")
    
    manager = ProcessManager(RoundRobinScheduler())
    visualizer = ProcessVisualizer(manager)
    
    # Test visualization methods (they should not crash)
    visualizer.display_header()
    visualizer.display_memory_info()
    visualizer.display_ai_node_info()
    
    # Test export
    visualizer.export_system_state("test_export.json")
    
    manager.shutdown()
    print("✅ Visualizer test passed")

def run_integration_test():
    """Run a complete integration test"""
    print("Running Integration Test...")
    
    # Test with different schedulers
    schedulers = [
        ("FIFO", FIFOScheduler()),
        ("Round Robin", RoundRobinScheduler(time_quantum=500)),
        ("Priority", PriorityScheduler()),
        ("MLFQ", MLFQScheduler(num_levels=2, time_quanta=[250, 500]))
    ]
    
    for name, scheduler in schedulers:
        print(f"Testing with {name} scheduler...")
        
        manager = ProcessManager(scheduler)
        manager.start_scheduler()
        
        # Create multiple processes
        pids = []
        for i in range(3):
            pid = manager.create_process(
                name=f"task_{i}",
                process_type=ProcessType.DATA_PROCESSING,
                target_function=simple_task,
                args=(f"task_{i}", 0.2),
                priority=i
            )
            pids.append(pid)
        
        # Wait for completion
        time.sleep(2)
        
        # Check statistics
        stats = scheduler.get_statistics()
        print(f"  Completed processes: {scheduler.completed_processes}")
        
        manager.shutdown()
        time.sleep(0.5)
    
    print("✅ Integration test passed")

def main():
    """Run all tests"""
    print("🧪 STARTING BASIC TESTS FOR PROCESS MANAGEMENT SYSTEM")
    print("=" * 60)
    
    try:
        test_pcb()
        test_schedulers()
        test_process_manager()
        test_visualizer()
        run_integration_test()
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Process Management System is working correctly")
        print("\nYou can now run the full demo with: python demo.py")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    
    print("=" * 60)

if __name__ == "__main__":
    main() 