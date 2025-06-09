#!/usr/bin/env python3
"""
Decentralized AI Node Operating System - Process Management Demo
Demonstrates process creation, scheduling, switching, and termination
"""

import time
import random
import threading
from typing import List

from process_control_block import ProcessType
from process_manager import ProcessManager
from schedulers import FIFOScheduler, RoundRobinScheduler, PriorityScheduler, MLFQScheduler
from process_visualizer import ProcessVisualizer

# Sample AI and blockchain workloads
def ai_inference_task(model_name: str, data_size: int):
    """Simulate AI inference workload"""
    print(f"🧠 Running AI inference with {model_name} on {data_size} samples")
    
    # Simulate model loading
    time.sleep(random.uniform(0.5, 1.5))
    print(f"🧠 Model {model_name} loaded")
    
    # Simulate inference computation
    for i in range(data_size):
        time.sleep(random.uniform(0.1, 0.3))
        if i % 10 == 0:
            print(f"🧠 Processed {i}/{data_size} samples")
    
    print(f"🧠 AI inference completed for {model_name}")
    return f"Inference results for {data_size} samples"

def blockchain_validator_task(block_id: str, transactions: int):
    """Simulate blockchain validation workload"""
    print(f"⛓️ Validating block {block_id} with {transactions} transactions")
    
    # Simulate validation work
    for i in range(transactions):
        time.sleep(random.uniform(0.05, 0.15))
        if i % 5 == 0:
            print(f"⛓️ Validated {i}/{transactions} transactions")
    
    print(f"⛓️ Block {block_id} validation completed")
    return f"Block {block_id} validated successfully"

def data_processing_task(dataset_name: str, operations: int):
    """Simulate data processing workload"""
    print(f"📊 Processing dataset {dataset_name} with {operations} operations")
    
    # Simulate data processing
    for i in range(operations):
        time.sleep(random.uniform(0.1, 0.2))
        if i % 3 == 0:
            print(f"📊 Completed {i}/{operations} operations")
    
    print(f"📊 Data processing completed for {dataset_name}")
    return f"Processed {operations} operations on {dataset_name}"

def network_node_task(node_type: str, connections: int):
    """Simulate network node workload"""
    print(f"🌐 Starting {node_type} node with {connections} connections")
    
    # Simulate network activity
    for i in range(connections):
        time.sleep(random.uniform(0.2, 0.4))
        print(f"🌐 Established connection {i+1}/{connections}")
    
    print(f"🌐 Network node {node_type} fully connected")
    return f"Network node {node_type} with {connections} connections"

def system_maintenance_task(task_name: str):
    """Simulate system maintenance workload"""
    print(f"⚙️ Running system maintenance: {task_name}")
    time.sleep(random.uniform(1.0, 2.0))
    print(f"⚙️ System maintenance completed: {task_name}")
    return f"Maintenance task {task_name} completed"

class ProcessDemo:
    """Demonstration class for the process management system"""
    
    def __init__(self):
        self.process_manager = None
        self.visualizer = None
    
    def demo_fifo_scheduler(self):
        """Demonstrate FIFO scheduler"""
        print("\n🎯 DEMONSTRATING FIFO SCHEDULER")
        print("=" * 50)
        
        scheduler = FIFOScheduler()
        self.process_manager = ProcessManager(scheduler)
        self.visualizer = ProcessVisualizer(self.process_manager)
        
        # Start the scheduler
        self.process_manager.start_scheduler()
        
        # Create various processes
        processes = [
            ("AI-Model-GPT", ProcessType.AI_INFERENCE, ai_inference_task, ("GPT-4", 5), 3),
            ("Blockchain-Validator", ProcessType.BLOCKCHAIN_VALIDATOR, blockchain_validator_task, ("block_001", 8), 2),
            ("Data-Processor", ProcessType.DATA_PROCESSING, data_processing_task, ("dataset_x", 6), 1),
            ("Network-Node", ProcessType.NETWORK_NODE, network_node_task, ("peer_node", 4), 1),
            ("System-Cleanup", ProcessType.SYSTEM, system_maintenance_task, ("cache_cleanup",), 0),
        ]
        
        # Create processes with delays
        for name, ptype, func, args, priority in processes:
            pid = self.process_manager.create_process(name, ptype, func, args, priority=priority)
            print(f"Created process {pid}: {name}")
            time.sleep(0.5)
        
        # Show visualization
        time.sleep(2)
        self.visualizer.display_full_dashboard()
        
        # Wait for processes to complete
        time.sleep(10)
        self.visualizer.display_full_dashboard()
        
        self.process_manager.shutdown()
    
    def demo_round_robin_scheduler(self):
        """Demonstrate Round Robin scheduler"""
        print("\n🎯 DEMONSTRATING ROUND ROBIN SCHEDULER")
        print("=" * 50)
        
        scheduler = RoundRobinScheduler(time_quantum=2000)  # 2 second quantum
        self.process_manager = ProcessManager(scheduler)
        self.visualizer = ProcessVisualizer(self.process_manager)
        
        self.process_manager.start_scheduler()
        
        # Create CPU-intensive processes
        processes = [
            ("AI-Vision", ProcessType.AI_INFERENCE, ai_inference_task, ("ResNet", 15), 0),
            ("AI-NLP", ProcessType.AI_INFERENCE, ai_inference_task, ("BERT", 12), 0),
            ("Blockchain-Mining", ProcessType.BLOCKCHAIN_VALIDATOR, blockchain_validator_task, ("block_002", 20), 0),
            ("Data-Analytics", ProcessType.DATA_PROCESSING, data_processing_task, ("analytics_data", 10), 0),
        ]
        
        for name, ptype, func, args, priority in processes:
            pid = self.process_manager.create_process(name, ptype, func, args, priority=priority)
            print(f"Created process {pid}: {name}")
            time.sleep(0.3)
        
        # Monitor for a while
        for i in range(5):
            time.sleep(3)
            self.visualizer.display_full_dashboard()
        
        self.process_manager.shutdown()
    
    def demo_priority_scheduler(self):
        """Demonstrate Priority scheduler"""
        print("\n🎯 DEMONSTRATING PRIORITY SCHEDULER")
        print("=" * 50)
        
        scheduler = PriorityScheduler(preemptive=True)
        self.process_manager = ProcessManager(scheduler)
        self.visualizer = ProcessVisualizer(self.process_manager)
        
        self.process_manager.start_scheduler()
        
        # Create processes with different priorities
        processes = [
            ("Low-Priority-Task", ProcessType.USER, data_processing_task, ("background_data", 8), 1),
            ("Medium-AI-Task", ProcessType.AI_INFERENCE, ai_inference_task, ("medium_model", 6), 5),
            ("Critical-System", ProcessType.SYSTEM, system_maintenance_task, ("critical_update",), 10),
            ("High-Priority-AI", ProcessType.AI_INFERENCE, ai_inference_task, ("emergency_ai", 4), 8),
            ("Blockchain-High", ProcessType.BLOCKCHAIN_VALIDATOR, blockchain_validator_task, ("urgent_block", 10), 7),
        ]
        
        # Create processes with delays to show preemption
        for i, (name, ptype, func, args, priority) in enumerate(processes):
            pid = self.process_manager.create_process(name, ptype, func, args, priority=priority)
            print(f"Created process {pid}: {name} (Priority: {priority})")
            time.sleep(2)
            
            if i == 2:  # Show dashboard after creating critical process
                self.visualizer.display_full_dashboard()
                time.sleep(3)
        
        time.sleep(8)
        self.visualizer.display_full_dashboard()
        
        self.process_manager.shutdown()
    
    def demo_mlfq_scheduler(self):
        """Demonstrate Multi-Level Feedback Queue scheduler"""
        print("\n🎯 DEMONSTRATING MLFQ SCHEDULER")
        print("=" * 50)
        
        scheduler = MLFQScheduler(num_levels=3, time_quanta=[1000, 2000, 4000])
        self.process_manager = ProcessManager(scheduler)
        self.visualizer = ProcessVisualizer(self.process_manager)
        
        self.process_manager.start_scheduler()
        
        # Create mix of short and long processes
        processes = [
            ("Quick-AI", ProcessType.AI_INFERENCE, ai_inference_task, ("quick_model", 3), 0),
            ("Long-Blockchain", ProcessType.BLOCKCHAIN_VALIDATOR, blockchain_validator_task, ("large_block", 25), 0),
            ("Medium-Data", ProcessType.DATA_PROCESSING, data_processing_task, ("medium_set", 8), 0),
            ("Interactive-Task", ProcessType.USER, system_maintenance_task, ("user_request",), 0),
            ("Background-AI", ProcessType.AI_INFERENCE, ai_inference_task, ("background_ai", 20), 0),
        ]
        
        for name, ptype, func, args, priority in processes:
            pid = self.process_manager.create_process(name, ptype, func, args, priority=priority)
            print(f"Created process {pid}: {name}")
            time.sleep(1)
        
        # Monitor the queue levels
        for i in range(6):
            time.sleep(4)
            self.visualizer.display_full_dashboard()
        
        self.process_manager.shutdown()
    
    def demo_interactive_mode(self):
        """Interactive demonstration mode"""
        print("\n🎯 INTERACTIVE DEMONSTRATION MODE")
        print("=" * 50)
        
        # Let user choose scheduler
        print("Choose a scheduler:")
        print("1. FIFO")
        print("2. Round Robin")
        print("3. Priority")
        print("4. Multi-Level Feedback Queue")
        
        choice = input("Enter choice (1-4): ").strip()
        
        schedulers = {
            '1': FIFOScheduler(),
            '2': RoundRobinScheduler(time_quantum=1500),
            '3': PriorityScheduler(preemptive=True),
            '4': MLFQScheduler(num_levels=3, time_quanta=[800, 1600, 3200])
        }
        
        scheduler = schedulers.get(choice, RoundRobinScheduler())
        self.process_manager = ProcessManager(scheduler)
        self.visualizer = ProcessVisualizer(self.process_manager)
        
        self.process_manager.start_scheduler()
        
        print(f"\n🚀 Started with {scheduler.name} scheduler")
        print("\nAvailable commands:")
        print("  create - Create a new process")
        print("  list - List all processes")
        print("  kill <pid> - Terminate a process")
        print("  suspend <pid> - Suspend a process")
        print("  resume <pid> - Resume a process")
        print("  dashboard - Show full dashboard")
        print("  monitor - Start real-time monitoring")
        print("  export - Export system state")
        print("  quit - Exit")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "create":
                    self._interactive_create_process()
                elif command == "list":
                    processes = self.process_manager.list_processes()
                    for proc in processes:
                        print(f"PID {proc['pid']}: {proc['name']} ({proc['state']})")
                elif command.startswith("kill "):
                    pid = int(command.split()[1])
                    self.process_manager.terminate_process(pid)
                elif command.startswith("suspend "):
                    pid = int(command.split()[1])
                    self.process_manager.suspend_process(pid)
                elif command.startswith("resume "):
                    pid = int(command.split()[1])
                    self.process_manager.resume_process(pid)
                elif command == "dashboard":
                    self.visualizer.display_full_dashboard()
                elif command == "monitor":
                    self.visualizer.real_time_monitor()
                elif command == "export":
                    self.visualizer.export_system_state()
                else:
                    print("Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        self.process_manager.shutdown()
    
    def _interactive_create_process(self):
        """Interactive process creation"""
        print("\nProcess types:")
        print("1. AI Inference")
        print("2. Data Processing")
        print("3. Blockchain Validator")
        print("4. Network Node")
        print("5. System Task")
        
        type_choice = input("Choose type (1-5): ").strip()
        name = input("Process name: ").strip()
        priority = int(input("Priority (0-10): ").strip() or "0")
        
        type_map = {
            '1': (ProcessType.AI_INFERENCE, ai_inference_task, ("interactive_ai", 5)),
            '2': (ProcessType.DATA_PROCESSING, data_processing_task, ("interactive_data", 6)),
            '3': (ProcessType.BLOCKCHAIN_VALIDATOR, blockchain_validator_task, ("interactive_block", 8)),
            '4': (ProcessType.NETWORK_NODE, network_node_task, ("interactive_net", 3)),
            '5': (ProcessType.SYSTEM, system_maintenance_task, ("interactive_sys",))
        }
        
        if type_choice in type_map:
            ptype, func, args = type_map[type_choice]
            pid = self.process_manager.create_process(name, ptype, func, args, priority=priority)
            print(f"Created process {pid}: {name}")
        else:
            print("Invalid choice")

def main():
    """Main demonstration function"""
    print("🚀 DECENTRALIZED AI NODE OPERATING SYSTEM")
    print("Process Management System Demo")
    print("=" * 60)
    
    demo = ProcessDemo()
    
    print("\nChoose demonstration mode:")
    print("1. FIFO Scheduler Demo")
    print("2. Round Robin Scheduler Demo")
    print("3. Priority Scheduler Demo")
    print("4. MLFQ Scheduler Demo")
    print("5. Interactive Mode")
    print("6. Run All Demos")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    try:
        if choice == '1':
            demo.demo_fifo_scheduler()
        elif choice == '2':
            demo.demo_round_robin_scheduler()
        elif choice == '3':
            demo.demo_priority_scheduler()
        elif choice == '4':
            demo.demo_mlfq_scheduler()
        elif choice == '5':
            demo.demo_interactive_mode()
        elif choice == '6':
            print("\n🎯 Running all scheduler demonstrations...")
            demo.demo_fifo_scheduler()
            time.sleep(2)
            demo.demo_round_robin_scheduler()
            time.sleep(2)
            demo.demo_priority_scheduler()
            time.sleep(2)
            demo.demo_mlfq_scheduler()
        else:
            print("Invalid choice. Running interactive mode...")
            demo.demo_interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    print("\n🏁 Demo completed. Thank you!")

if __name__ == "__main__":
    main() 