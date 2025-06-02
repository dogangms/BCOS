#!/usr/bin/env python3
"""
Comprehensive Demo: Steps 1 & 2 Integration
Demonstrates Process Management + Memory Management working together
"""

import time
import random
from integrated_process_manager import IntegratedProcessManager
from process_control_block import ProcessType
from schedulers import RoundRobinScheduler, PriorityScheduler, MLFQScheduler
from memory_manager import MemoryType

def ai_inference_workload(model_name: str, data_size: int):
    """Simulate AI inference workload"""
    print(f"🧠 Loading AI model: {model_name}")
    time.sleep(0.1)  # Simulate model loading
    
    print(f"📊 Processing {data_size} data samples")
    for i in range(data_size // 100):
        time.sleep(0.01)  # Simulate inference
        if i % 10 == 0:
            print(f"   Processed {i * 100} samples...")
    
    return f"AI inference complete: {data_size} samples processed"

def blockchain_validation_workload(block_count: int):
    """Simulate blockchain validation workload"""
    print(f"⛓️ Validating {block_count} blocks")
    
    for i in range(block_count):
        time.sleep(0.05)  # Simulate validation
        print(f"   Block {i+1}/{block_count} validated ✅")
    
    return f"Blockchain validation complete: {block_count} blocks"

def data_processing_workload(dataset_size: int):
    """Simulate data processing workload"""
    print(f"📈 Processing dataset of size {dataset_size}MB")
    
    for i in range(dataset_size):
        time.sleep(0.02)  # Simulate processing
        if i % 5 == 0:
            print(f"   Processed {i}MB of data...")
    
    return f"Data processing complete: {dataset_size}MB processed"

def network_node_workload(connection_count: int):
    """Simulate network node workload"""
    print(f"🌐 Managing {connection_count} P2P connections")
    
    for i in range(connection_count):
        time.sleep(0.03)  # Simulate network communication
        print(f"   Connection {i+1} established and synced")
    
    return f"Network node operational: {connection_count} connections active"

def main():
    """Main comprehensive demonstration"""
    print("🚀 DECENTRALIZED AI NODE OPERATING SYSTEM")
    print("📋 Comprehensive Demo: Process + Memory Management Integration")
    print("=" * 80)
    
    # Initialize integrated system with different schedulers
    schedulers = [
        ("Round Robin", RoundRobinScheduler(time_quantum=500)),
        ("Priority", PriorityScheduler(preemptive=True)),
        ("MLFQ", MLFQScheduler(num_levels=3, time_quanta=[100, 200, 400]))
    ]
    
    for scheduler_name, scheduler in schedulers:
        print(f"\n🎯 Testing with {scheduler_name} Scheduler")
        print("-" * 50)
        
        # Create integrated manager
        manager = IntegratedProcessManager(
            scheduler=scheduler,
            total_memory=128*1024*1024,  # 128MB
            page_size=4096,
            max_workers=8
        )
        
        print(f"✅ System initialized with {scheduler_name} scheduler")
        print(f"💾 Total Memory: {manager.memory_manager.total_memory // (1024*1024)}MB")
        
        # Start the scheduler
        manager.start_scheduler()
        
        # Create diverse AI/Blockchain workloads
        workloads = [
            {
                'name': 'GPT-4-Inference',
                'type': ProcessType.AI_INFERENCE,
                'function': ai_inference_workload,
                'args': ('GPT-4', 1000),
                'memory': 32*1024*1024,  # 32MB
                'priority': 8
            },
            {
                'name': 'Blockchain-Validator',
                'type': ProcessType.BLOCKCHAIN_VALIDATOR,
                'function': blockchain_validation_workload,
                'args': (5,),
                'memory': 16*1024*1024,  # 16MB
                'priority': 9
            },
            {
                'name': 'Data-Processor',
                'type': ProcessType.DATA_PROCESSING,
                'function': data_processing_workload,
                'args': (10,),
                'memory': 24*1024*1024,  # 24MB
                'priority': 6
            },
            {
                'name': 'P2P-Network-Node',
                'type': ProcessType.NETWORK_NODE,
                'function': network_node_workload,
                'args': (8,),
                'memory': 8*1024*1024,   # 8MB
                'priority': 7
            }
        ]
        
        # Create all processes
        created_processes = []
        for workload in workloads:
            print(f"\n📝 Creating process: {workload['name']}")
            
            pid = manager.create_process(
                name=workload['name'],
                process_type=workload['type'],
                target_function=workload['function'],
                args=workload['args'],
                priority=workload['priority'],
                memory_required=workload['memory']
            )
            
            if pid:
                created_processes.append(pid)
                process_info = manager.get_process_info(pid)
                print(f"   ✅ PID: {pid}")
                print(f"   💾 Memory: 0x{process_info['virtual_base_address']:08X} ({workload['memory']//1024//1024}MB)")
                print(f"   🧠 Type: {process_info['memory_type'].value}")
                print(f"   ⚡ Priority: {workload['priority']}")
            else:
                print(f"   ❌ Failed to create process: {workload['name']}")
        
        # Monitor system for a while
        print(f"\n⏱️ Running {scheduler_name} scheduler for 3 seconds...")
        
        start_time = time.time()
        while time.time() - start_time < 3.0:
            time.sleep(0.5)
            
            # Show system status
            system_info = manager.get_system_info()
            memory_stats = system_info['memory_statistics']
            
            print(f"   📊 Active Processes: {system_info['running_processes']}")
            print(f"   🔄 Context Switches: {system_info['context_switches']}")
            print(f"   💾 Memory Usage: {memory_stats['memory_usage_percent']:.1f}%")
            print(f"   📄 Page Faults: {memory_stats['page_faults']}")
            print(f"   💿 Swap Operations: {memory_stats['swap_outs']}↑ {memory_stats['swap_ins']}↓")
            
            # Test memory operations
            if created_processes:
                test_pid = random.choice(created_processes)
                process_info = manager.get_process_info(test_pid)
                if process_info and process_info['virtual_base_address']:
                    success = manager.access_process_memory(
                        test_pid, 
                        process_info['virtual_base_address']
                    )
                    if success:
                        print(f"   🔍 Memory access test: Process {test_pid} SUCCESS")
        
        # Show final system dashboard
        print(f"\n📈 Final System Status for {scheduler_name}:")
        manager.display_full_dashboard()
        
        # Cleanup
        print(f"\n🧹 Cleaning up {scheduler_name} demo...")
        manager.shutdown()
        
        # Brief pause between scheduler demos
        time.sleep(1)
    
    print("\n" + "=" * 80)
    print("🎊 COMPREHENSIVE DEMO COMPLETE!")
    print("✅ Process Management (Step 1): Schedulers, PCB, Process Lifecycle")
    print("✅ Memory Management (Step 2): Paging, Virtual Memory, AI/Blockchain Constraints")
    print("✅ Integration: Seamless Process + Memory Management")
    print("📊 Performance: Optimized for AI/Blockchain Workloads")
    print("🎯 Next: Step 3 - File System Implementation")
    print("=" * 80)

if __name__ == "__main__":
    main() 