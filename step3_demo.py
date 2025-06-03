"""
Decentralized AI Node Operating System - Step 3: Concurrency & Synchronization Demo
Comprehensive demonstration of threading, synchronization, and classical concurrency problems.
"""

import threading
import time
import random
import sys
from typing import List, Dict, Optional

from thread_api import ThreadAPI, ThreadType, ThreadPriority, ThreadState
from concurrency_problems import (
    ProducerConsumerAI, DiningPhilosophersAI, ReadersWritersAI, 
    ConcurrencyProblemSuite, ConcurrencyProblemType
)
from synchronization_visualizer import (
    SynchronizationVisualizer, InteractiveMonitor, SyncEvent, VisualizationMode
)

class Step3Demo:
    """
    Comprehensive demo for Step 3: Concurrency & Synchronization
    Showcases all features with interactive modes and real-time monitoring
    """
    
    def __init__(self):
        self.thread_api = ThreadAPI()
        self.visualizer = SynchronizationVisualizer(self.thread_api)
        self.interactive_monitor = InteractiveMonitor(self.visualizer)
        self.concurrency_suite = ConcurrencyProblemSuite()
        
        # Demo control
        self.demo_threads: List[str] = []
        self.running = False
        
    def run_comprehensive_demo(self):
        """Run the complete Step 3 demonstration"""
        print("🚀 " + "STEP 3: CONCURRENCY & SYNCHRONIZATION DEMO".center(80, "═"))
        print()
        
        while True:
            print("📋 DEMO MENU:")
            print("  [1] Thread API Basics")
            print("  [2] Synchronization Primitives")
            print("  [3] Producer-Consumer Problem")
            print("  [4] Dining Philosophers Problem")
            print("  [5] Readers-Writers Problem")
            print("  [6] Real-time Monitoring Dashboard")
            print("  [7] Interactive Concurrency Simulation")
            print("  [8] All Problems Sequential")
            print("  [9] Multi-threaded OS Tasks (Creativity)")
            print("  [0] Exit")
            print()
            
            choice = input("🎯 Select demo option: ").strip()
            
            if choice == '1':
                self.demo_thread_api_basics()
            elif choice == '2':
                self.demo_synchronization_primitives()
            elif choice == '3':
                self.demo_producer_consumer()
            elif choice == '4':
                self.demo_dining_philosophers()
            elif choice == '5':
                self.demo_readers_writers()
            elif choice == '6':
                self.demo_monitoring_dashboard()
            elif choice == '7':
                self.demo_interactive_simulation()
            elif choice == '8':
                self.demo_all_problems()
            elif choice == '9':
                self.demo_multithreaded_os_tasks()
            elif choice == '0':
                print("👋 Exiting Step 3 demo...")
                break
            else:
                print("❌ Invalid choice, please try again.")
                
            print("\n" + "─" * 80 + "\n")
            
    def demo_thread_api_basics(self):
        """Demonstrate basic Thread API functionality"""
        print("🧵 THREAD API BASICS DEMONSTRATION")
        print("═" * 60)
        
        def ai_worker_task(worker_id: int, work_duration: float):
            """Sample AI worker task"""
            print(f"🤖 AI Worker {worker_id} starting neural network training...")
            time.sleep(work_duration)
            result = random.randint(85, 98)  # Simulated accuracy
            print(f"✅ AI Worker {worker_id} completed training with {result}% accuracy")
            return result
            
        def blockchain_miner_task(miner_id: int, blocks_to_mine: int):
            """Sample blockchain miner task"""
            print(f"⛏️ Blockchain Miner {miner_id} starting to mine {blocks_to_mine} blocks...")
            for block in range(blocks_to_mine):
                time.sleep(random.uniform(0.5, 1.5))
                print(f"💎 Miner {miner_id} mined block #{block + 1}")
            print(f"🏆 Miner {miner_id} finished mining {blocks_to_mine} blocks")
            return blocks_to_mine
            
        print("🔄 Creating different types of threads...")
        
        # Create various AI/blockchain threads
        threads = []
        
        # AI Worker threads
        for i in range(3):
            thread_id = self.thread_api.create_thread(
                function=ai_worker_task,
                args=(i + 1, random.uniform(2.0, 4.0)),
                name=f"AI-Worker-{i + 1}",
                thread_type=ThreadType.AI_WORKER,
                priority=ThreadPriority.HIGH
            )
            threads.append(thread_id)
            
        # Blockchain Miner threads
        for i in range(2):
            thread_id = self.thread_api.create_thread(
                function=blockchain_miner_task,
                args=(i + 1, random.randint(2, 4)),
                name=f"Blockchain-Miner-{i + 1}",
                thread_type=ThreadType.BLOCKCHAIN_MINER,
                priority=ThreadPriority.NORMAL
            )
            threads.append(thread_id)
            
        print(f"📊 Created {len(threads)} threads")
        
        # Start all threads
        print("🚀 Starting all threads...")
        for thread_id in threads:
            self.thread_api.start_thread(thread_id)
            
        # Monitor thread execution
        print("👀 Monitoring thread execution...")
        start_time = time.time()
        
        while True:
            active_count = len(self.thread_api.list_running_threads())
            stats = self.thread_api.get_system_stats()
            
            print(f"📈 Active: {active_count}, Completed: {stats['total_threads_completed']}, "
                  f"CPU: {stats['average_cpu_utilization']:.1f}%")
            
            if active_count == 0:
                break
                
            time.sleep(1)
            
        duration = time.time() - start_time
        final_stats = self.thread_api.get_system_stats()
        
        print("\n📋 EXECUTION SUMMARY:")
        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print(f"🔢 Threads Created: {final_stats['total_threads_created']}")
        print(f"✅ Threads Completed: {final_stats['total_threads_completed']}")
        print(f"🕐 Total CPU Time: {final_stats['total_cpu_time']:.2f} seconds")
        print(f"📊 Average CPU Utilization: {final_stats['average_cpu_utilization']:.1f}%")
        
    def demo_synchronization_primitives(self):
        """Demonstrate locks, condition variables, and semaphores"""
        print("🔒 SYNCHRONIZATION PRIMITIVES DEMONSTRATION")
        print("═" * 60)
        
        # Create synchronization primitives
        self.thread_api.create_lock("shared_resource_lock")
        self.thread_api.create_condition_variable("data_ready_cv", "shared_resource_lock")
        self.thread_api.create_semaphore("connection_pool", 3)
        
        # Shared resources
        shared_data = {"value": 0, "ready": False}
        results = []
        
        def producer_with_sync(producer_id: int):
            """Producer using synchronization primitives"""
            thread_id = f"producer-{producer_id}"
            
            for i in range(5):
                # Acquire lock
                if self.thread_api.acquire_lock("shared_resource_lock", thread_id):
                    try:
                        # Simulate data production
                        time.sleep(random.uniform(0.1, 0.3))
                        shared_data["value"] += random.randint(1, 10)
                        shared_data["ready"] = True
                        
                        print(f"🔵 Producer {producer_id} produced data: {shared_data['value']}")
                        
                        # Notify waiting consumers
                        self.thread_api.notify_condition("data_ready_cv", notify_all=True)
                        
                    finally:
                        self.thread_api.release_lock("shared_resource_lock", thread_id)
                        
                time.sleep(random.uniform(0.5, 1.0))
                
        def consumer_with_sync(consumer_id: int):
            """Consumer using synchronization primitives"""
            thread_id = f"consumer-{consumer_id}"
            
            for i in range(3):
                # Acquire semaphore (simulate connection pool)
                if self.thread_api.acquire_semaphore("connection_pool", thread_id):
                    try:
                        # Wait for data to be ready
                        if self.thread_api.acquire_lock("shared_resource_lock", thread_id):
                            try:
                                while not shared_data["ready"]:
                                    print(f"🟡 Consumer {consumer_id} waiting for data...")
                                    self.thread_api.wait_condition("data_ready_cv", thread_id, timeout=2.0)
                                    
                                if shared_data["ready"]:
                                    value = shared_data["value"]
                                    shared_data["ready"] = False
                                    results.append(value)
                                    print(f"🟢 Consumer {consumer_id} consumed data: {value}")
                                    
                            finally:
                                self.thread_api.release_lock("shared_resource_lock", thread_id)
                                
                    finally:
                        self.thread_api.release_semaphore("connection_pool", thread_id)
                        
                time.sleep(random.uniform(0.8, 1.5))
        
        print("🔄 Starting synchronized producers and consumers...")
        
        # Create and start threads
        sync_threads = []
        
        # Producer threads
        for i in range(2):
            thread_id = self.thread_api.create_thread(
                function=producer_with_sync,
                args=(i + 1,),
                name=f"SyncProducer-{i + 1}",
                thread_type=ThreadType.DATA_PROCESSOR
            )
            sync_threads.append(thread_id)
            self.thread_api.start_thread(thread_id)
            
        # Consumer threads
        for i in range(3):
            thread_id = self.thread_api.create_thread(
                function=consumer_with_sync,
                args=(i + 1,),
                name=f"SyncConsumer-{i + 1}",
                thread_type=ThreadType.DATA_PROCESSOR
            )
            sync_threads.append(thread_id)
            self.thread_api.start_thread(thread_id)
            
        # Wait for completion
        for thread_id in sync_threads:
            self.thread_api.join_thread(thread_id)
            
        print(f"\n📊 Synchronization completed! Processed {len(results)} data items")
        print(f"💾 Results: {results}")
        
    def demo_producer_consumer(self):
        """Demonstrate Producer-Consumer problem"""
        print("🔄 PRODUCER-CONSUMER AI DATA PROCESSING")
        print("═" * 60)
        
        producer_consumer = ProducerConsumerAI(
            buffer_size=8,
            num_producers=3,
            num_consumers=2
        )
        
        print("🚀 Starting AI data processing simulation...")
        producer_consumer.start_simulation(duration=20.0)
        
    def demo_dining_philosophers(self):
        """Demonstrate Dining Philosophers problem"""
        print("🍽️ DINING PHILOSOPHERS AI NODE CONSENSUS")
        print("═" * 60)
        
        dining_philosophers = DiningPhilosophersAI(num_philosophers=5)
        
        print("🚀 Starting AI node consensus simulation...")
        dining_philosophers.start_simulation(duration=25.0)
        
    def demo_readers_writers(self):
        """Demonstrate Readers-Writers problem"""
        print("📚 READERS-WRITERS AI MODEL ACCESS")
        print("═" * 60)
        
        readers_writers = ReadersWritersAI(
            num_readers=4,
            num_writers=2
        )
        
        print("🚀 Starting AI model access simulation...")
        readers_writers.start_simulation(duration=20.0)
        
    def demo_monitoring_dashboard(self):
        """Demonstrate real-time monitoring"""
        print("📊 REAL-TIME SYNCHRONIZATION MONITORING")
        print("═" * 60)
        
        # Start some background activity
        self._start_background_activity()
        
        print("🔍 Starting monitoring dashboard...")
        print("📝 The dashboard will show real-time synchronization metrics")
        print("⏱️  Monitoring for 30 seconds...")
        
        self.visualizer.start_monitoring()
        time.sleep(30)
        self.visualizer.stop_monitoring()
        
        self._stop_background_activity()
        
    def demo_interactive_simulation(self):
        """Demonstrate interactive simulation with live monitoring"""
        print("🎮 INTERACTIVE CONCURRENCY SIMULATION")
        print("═" * 60)
        
        print("🔄 This will start a multi-problem simulation with live monitoring")
        print("📊 You can switch between different visualization modes")
        print("⚠️  Press Ctrl+C to stop the simulation")
        
        try:
            # Start various concurrency problems in background
            self._start_complex_simulation()
            
            # Start interactive monitoring
            self.interactive_monitor.start_interactive_mode()
            
            # Keep running until user stops
            input("Press Enter to stop interactive simulation...")
            
        except KeyboardInterrupt:
            print("\n⏹️ Stopping interactive simulation...")
        finally:
            self.interactive_monitor.stop_interactive_mode()
            self._stop_background_activity()
            
    def demo_all_problems(self):
        """Run all concurrency problems sequentially"""
        print("🌟 ALL CONCURRENCY PROBLEMS DEMONSTRATION")
        print("═" * 60)
        
        self.concurrency_suite.run_all_problems(duration=15.0)
        
    def demo_multithreaded_os_tasks(self):
        """Creativity: Multi-threaded OS tasks with file I/O + UI simulation"""
        print("✨ MULTI-THREADED OS TASKS (CREATIVITY FEATURE)")
        print("═" * 60)
        
        def file_io_task(task_id: int):
            """Simulated file I/O operations"""
            operations = ["read", "write", "copy", "compress", "encrypt"]
            
            for i in range(random.randint(3, 6)):
                operation = random.choice(operations)
                file_size = random.randint(100, 2000)  # KB
                
                print(f"📁 FileIO-{task_id}: {operation} operation on {file_size}KB file")
                time.sleep(random.uniform(0.3, 1.0))  # I/O delay
                
                print(f"✅ FileIO-{task_id}: {operation} completed")
                
        def ui_update_task(ui_id: int):
            """Simulated UI update operations"""
            widgets = ["progress_bar", "status_text", "chart", "notification", "menu"]
            
            for i in range(random.randint(8, 12)):
                widget = random.choice(widgets)
                update_time = random.uniform(0.1, 0.3)
                
                print(f"🖥️ UI-{ui_id}: Updating {widget}")
                time.sleep(update_time)
                
                print(f"✨ UI-{ui_id}: {widget} updated")
                
        def network_task(net_id: int):
            """Simulated network operations"""
            operations = ["download", "upload", "sync", "ping", "resolve"]
            
            for i in range(random.randint(4, 7)):
                operation = random.choice(operations)
                latency = random.uniform(0.2, 0.8)
                
                print(f"🌐 Network-{net_id}: {operation} operation")
                time.sleep(latency)
                
                print(f"📡 Network-{net_id}: {operation} completed")
                
        print("🚀 Starting multi-threaded OS task simulation...")
        print("📁 File I/O threads, 🖥️ UI update threads, 🌐 Network threads")
        
        # Create shared resources and synchronization
        self.thread_api.create_lock("ui_update_lock")
        self.thread_api.create_semaphore("network_connections", 3)
        self.thread_api.create_condition_variable("task_coordination")
        
        # Start monitoring
        self.visualizer.start_monitoring()
        
        os_threads = []
        
        # File I/O threads
        for i in range(3):
            thread_id = self.thread_api.create_thread(
                function=file_io_task,
                args=(i + 1,),
                name=f"FileIO-{i + 1}",
                thread_type=ThreadType.SYSTEM_DAEMON,
                priority=ThreadPriority.NORMAL
            )
            os_threads.append(thread_id)
            
        # UI update threads  
        for i in range(2):
            thread_id = self.thread_api.create_thread(
                function=ui_update_task,
                args=(i + 1,),
                name=f"UI-Update-{i + 1}",
                thread_type=ThreadType.USER_THREAD,
                priority=ThreadPriority.HIGH
            )
            os_threads.append(thread_id)
            
        # Network threads
        for i in range(4):
            thread_id = self.thread_api.create_thread(
                function=network_task,
                args=(i + 1,),
                name=f"Network-{i + 1}",
                thread_type=ThreadType.NETWORK_HANDLER,
                priority=ThreadPriority.NORMAL
            )
            os_threads.append(thread_id)
            
        # Start all threads
        for thread_id in os_threads:
            self.thread_api.start_thread(thread_id)
            
        print(f"⚡ Started {len(os_threads)} OS task threads")
        print("📊 Monitoring real-time execution...")
        
        # Monitor execution
        while len(self.thread_api.list_running_threads()) > 0:
            time.sleep(2)
            
        print("🏁 All OS tasks completed!")
        
        # Stop monitoring and show final stats
        self.visualizer.stop_monitoring()
        
        final_stats = self.thread_api.get_system_stats()
        print("\n📈 FINAL STATISTICS:")
        print(f"🔢 Total Threads: {final_stats['total_threads_created']}")
        print(f"✅ Completed: {final_stats['total_threads_completed']}")
        print(f"🕐 Total CPU Time: {final_stats['total_cpu_time']:.2f}s")
        print(f"📊 Avg CPU Utilization: {final_stats['average_cpu_utilization']:.1f}%")
        
    def _start_background_activity(self):
        """Start background threads for monitoring demonstration"""
        def background_worker(worker_id: int):
            for i in range(20):
                time.sleep(random.uniform(0.5, 1.5))
                
        self.demo_threads = []
        for i in range(5):
            thread_id = self.thread_api.create_thread(
                function=background_worker,
                args=(i + 1,),
                name=f"Background-{i + 1}",
                thread_type=random.choice(list(ThreadType)),
                priority=random.choice(list(ThreadPriority))
            )
            self.demo_threads.append(thread_id)
            self.thread_api.start_thread(thread_id)
            
    def _start_complex_simulation(self):
        """Start complex multi-problem simulation"""
        # This would start multiple concurrency problems running simultaneously
        # For demo purposes, we'll start background activity
        self._start_background_activity()
        
    def _stop_background_activity(self):
        """Stop background demonstration threads"""
        for thread_id in self.demo_threads:
            self.thread_api.terminate_thread(thread_id)
        self.demo_threads.clear()

def main():
    """Main demo entry point"""
    print("🎯 " + "DECENTRALIZED AI NODE OS - STEP 3 DEMO".center(80, "="))
    print("🧵 Concurrency & Synchronization Features")
    print("=" * 80)
    print()
    
    demo = Step3Demo()
    
    try:
        demo.run_comprehensive_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    finally:
        # Cleanup
        demo.visualizer.stop_monitoring()
        print("🧹 Demo cleanup completed")
        print("👋 Thank you for trying Step 3 of the Decentralized AI Node OS!")

if __name__ == "__main__":
    main() 