"""
Decentralized AI Node Operating System - Step 3: Classical Concurrency Problems
Implementation of classical concurrency problems with AI/Blockchain themes.
"""

import threading
import time
import random
import queue
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from thread_api import ThreadAPI, ThreadType, ThreadPriority, ThreadState

class ConcurrencyProblemType(Enum):
    """Types of concurrency problems"""
    PRODUCER_CONSUMER = "Producer-Consumer"
    DINING_PHILOSOPHERS = "Dining Philosophers"
    READERS_WRITERS = "Readers-Writers"
    SLEEPING_BARBER = "Sleeping Barber"
    BOUNDED_BUFFER = "Bounded Buffer"

@dataclass
class AIDataPacket:
    """AI Data packet for producer-consumer scenarios"""
    packet_id: str
    data_type: str  # "training_data", "inference_request", "model_update", "blockchain_tx"
    size: int  # In KB
    priority: int  # 1-10
    timestamp: float = field(default_factory=time.time)
    processed: bool = False
    processing_time: float = 0.0

class ProducerConsumerAI:
    """
    AI-themed Producer-Consumer problem
    Producers generate AI training data, consumers process it
    """
    
    def __init__(self, buffer_size: int = 10, num_producers: int = 3, num_consumers: int = 2):
        self.buffer_size = buffer_size
        self.buffer = queue.Queue(maxsize=buffer_size)
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)
        
        self.num_producers = num_producers
        self.num_consumers = num_consumers
        
        # Statistics
        self.total_produced = 0
        self.total_consumed = 0
        self.producer_stats = {}
        self.consumer_stats = {}
        
        # Control
        self.running = False
        self.threads = []
        
        # Performance metrics
        self.start_time = 0
        self.packets_in_system = []
        
    def start_simulation(self, duration: float = 30.0):
        """Start the producer-consumer simulation"""
        self.running = True
        self.start_time = time.time()
        
        print("🚀 Starting AI Data Processing Simulation...")
        print(f"📊 Buffer Size: {self.buffer_size}")
        print(f"🤖 Producers: {self.num_producers}")
        print(f"⚡ Consumers: {self.num_consumers}")
        print("─" * 50)
        
        # Start producer threads
        for i in range(self.num_producers):
            producer_thread = threading.Thread(
                target=self._producer_worker,
                args=(f"AI-Producer-{i+1}",),
                daemon=True
            )
            producer_thread.start()
            self.threads.append(producer_thread)
            
        # Start consumer threads
        for i in range(self.num_consumers):
            consumer_thread = threading.Thread(
                target=self._consumer_worker,
                args=(f"AI-Consumer-{i+1}",),
                daemon=True
            )
            consumer_thread.start()
            self.threads.append(consumer_thread)
            
        # Run for specified duration
        time.sleep(duration)
        self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=2.0)
            
        self._print_statistics()
        
    def _producer_worker(self, producer_name: str):
        """Producer thread worker"""
        self.producer_stats[producer_name] = {"produced": 0, "blocked_time": 0}
        
        while self.running:
            # Generate AI data packet
            packet = AIDataPacket(
                packet_id=f"{producer_name}-{self.producer_stats[producer_name]['produced']:04d}",
                data_type=random.choice(["training_data", "inference_request", "model_update", "blockchain_tx"]),
                size=random.randint(100, 1000),  # KB
                priority=random.randint(1, 10)
            )
            
            start_wait = time.time()
            
            with self.not_full:
                while self.buffer.full() and self.running:
                    print(f"🔴 {producer_name} waiting - buffer full")
                    self.not_full.wait(timeout=1.0)
                    
                if not self.running:
                    break
                    
                # Produce the packet
                self.buffer.put(packet)
                self.total_produced += 1
                self.producer_stats[producer_name]["produced"] += 1
                self.producer_stats[producer_name]["blocked_time"] += time.time() - start_wait
                
                print(f"🟢 {producer_name} produced {packet.data_type} packet {packet.packet_id} (size: {packet.size}KB)")
                
                self.not_empty.notify()
                
            # Simulate production time
            time.sleep(random.uniform(0.2, 0.8))  # Reduced production time
            
    def _consumer_worker(self, consumer_name: str):
        """Consumer thread worker"""
        self.consumer_stats[consumer_name] = {"consumed": 0, "processing_time": 0, "blocked_time": 0}
        
        while self.running:
            start_wait = time.time()
            
            with self.not_empty:
                while self.buffer.empty() and self.running:
                    print(f"🔵 {consumer_name} waiting - buffer empty")
                    self.not_empty.wait(timeout=1.0)
                    
                if not self.running:
                    break
                    
                # Consume the packet
                packet = self.buffer.get()
                self.total_consumed += 1
                self.consumer_stats[consumer_name]["consumed"] += 1
                self.consumer_stats[consumer_name]["blocked_time"] += time.time() - start_wait
                
                self.not_full.notify()
                
            # Process the packet outside the lock
            processing_start = time.time()
            processing_time = self._process_packet(packet, consumer_name)
            self.consumer_stats[consumer_name]["processing_time"] += processing_time
            
            print(f"⚡ {consumer_name} processed {packet.data_type} packet {packet.packet_id} in {processing_time:.2f}s")
            
    def _process_packet(self, packet: AIDataPacket, consumer_name: str) -> float:
        """Simulate processing an AI data packet"""
        base_time = 0.1
        
        # Different processing times based on data type
        if packet.data_type == "training_data":
            processing_time = base_time * (packet.size / 100) * random.uniform(0.8, 1.5)
        elif packet.data_type == "inference_request":
            processing_time = base_time * random.uniform(0.3, 0.8)
        elif packet.data_type == "model_update":
            processing_time = base_time * (packet.size / 50) * random.uniform(1.0, 2.0)
        elif packet.data_type == "blockchain_tx":
            processing_time = base_time * random.uniform(0.5, 1.2)
        else:
            processing_time = base_time
            
        # Simulate processing
        time.sleep(processing_time)
        packet.processed = True
        packet.processing_time = processing_time
        
        return processing_time
        
    def _print_statistics(self):
        """Print simulation statistics"""
        duration = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📈 AI DATA PROCESSING SIMULATION RESULTS")
        print("=" * 60)
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📦 Total Produced: {self.total_produced}")
        print(f"⚡ Total Consumed: {self.total_consumed}")
        print(f"📊 Throughput: {self.total_consumed/duration:.2f} packets/sec")
        print(f"🔄 Buffer Utilization: {(self.total_produced - self.total_consumed) / self.buffer_size * 100:.1f}%")
        
        print("\n📈 PRODUCER STATISTICS:")
        for name, stats in self.producer_stats.items():
            print(f"  {name}: {stats['produced']} packets, {stats['blocked_time']:.2f}s blocked")
            
        print("\n⚡ CONSUMER STATISTICS:")
        for name, stats in self.consumer_stats.items():
            avg_processing = stats['processing_time'] / max(stats['consumed'], 1)
            print(f"  {name}: {stats['consumed']} packets, avg {avg_processing:.3f}s/packet, {stats['blocked_time']:.2f}s blocked")

class DiningPhilosophersAI:
    """
    AI-themed Dining Philosophers problem
    Philosophers are AI nodes that need blockchain consensus and data access
    """
    
    def __init__(self, num_philosophers: int = 5):
        self.num_philosophers = num_philosophers
        self.forks = [threading.Lock() for _ in range(num_philosophers)]
        self.eating_count = [0] * num_philosophers
        self.thinking_time = [0.0] * num_philosophers
        self.eating_time = [0.0] * num_philosophers
        self.waiting_time = [0.0] * num_philosophers
        
        self.running = False
        self.threads = []
        self.start_time = 0
        
        # AI Node names
        self.node_names = [
            "🤖 AI-Trainer",
            "⛏️ Block-Miner", 
            "🔗 Consensus-Node",
            "📊 Data-Analyzer",
            "🌐 Network-Hub"
        ][:num_philosophers]
        
    def start_simulation(self, duration: float = 30.0):
        """Start the dining philosophers simulation"""
        self.running = True
        self.start_time = time.time()
        
        print("🍽️ Starting AI Node Consensus Simulation...")
        print(f"🤖 AI Nodes: {self.num_philosophers}")
        print("🔄 Each node needs exclusive access to shared blockchain data")
        print("─" * 60)
        
        # Start philosopher threads
        for i in range(self.num_philosophers):
            philosopher_thread = threading.Thread(
                target=self._philosopher_worker,
                args=(i,),
                daemon=True
            )
            philosopher_thread.start()
            self.threads.append(philosopher_thread)
            
        # Run simulation
        time.sleep(duration)
        self.running = False
        
        # Wait for threads
        for thread in self.threads:
            thread.join(timeout=2.0)
            
        self._print_statistics()
        
    def _philosopher_worker(self, philosopher_id: int):
        """Philosopher (AI Node) worker"""
        node_name = self.node_names[philosopher_id]
        left_fork = philosopher_id
        right_fork = (philosopher_id + 1) % self.num_philosophers
        
        while self.running:
            # Think (prepare data/calculations)
            think_start = time.time()
            print(f"🤔 {node_name} is thinking (preparing consensus data)")
            time.sleep(random.uniform(0.1, 0.5))  # Reduced thinking time
            self.thinking_time[philosopher_id] += time.time() - think_start
            
            # Try to acquire forks (blockchain data access)
            wait_start = time.time()
            print(f"🍽️ {node_name} is hungry (needs blockchain access)")
            
            # Avoid deadlock by ordering fork acquisition
            first_fork = min(left_fork, right_fork)
            second_fork = max(left_fork, right_fork)
            
            self.forks[first_fork].acquire()
            print(f"🔒 {node_name} acquired first data lock")
            
            try:
                self.forks[second_fork].acquire()
                print(f"🔒 {node_name} acquired second data lock")
                
                try:
                    self.waiting_time[philosopher_id] += time.time() - wait_start
                    
                    # Eat (perform consensus operation)
                    eat_start = time.time()
                    print(f"🍽️ {node_name} is eating (performing consensus)")
                    time.sleep(random.uniform(0.2, 1.0))  # Reduced eating time
                    
                    self.eating_count[philosopher_id] += 1
                    self.eating_time[philosopher_id] += time.time() - eat_start
                    
                    print(f"✅ {node_name} finished consensus operation #{self.eating_count[philosopher_id]}")
                    
                finally:
                    self.forks[second_fork].release()
                    print(f"🔓 {node_name} released second data lock")
                    
            finally:
                self.forks[first_fork].release()
                print(f"🔓 {node_name} released first data lock")
                
    def _print_statistics(self):
        """Print dining philosophers statistics"""
        duration = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📈 AI NODE CONSENSUS SIMULATION RESULTS")
        print("=" * 60)
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        total_operations = sum(self.eating_count)
        print(f"🔄 Total Consensus Operations: {total_operations}")
        print(f"📊 Average Operations per Node: {total_operations/self.num_philosophers:.1f}")
        
        print("\n📈 NODE STATISTICS:")
        for i in range(self.num_philosophers):
            avg_eating = self.eating_time[i] / max(self.eating_count[i], 1)
            avg_waiting = self.waiting_time[i] / max(self.eating_count[i], 1)
            efficiency = (self.eating_time[i] / duration) * 100
            
            print(f"  {self.node_names[i]}:")
            print(f"    🍽️ Operations: {self.eating_count[i]}")
            print(f"    ⏱️ Avg Operation Time: {avg_eating:.2f}s")
            print(f"    ⏳ Avg Wait Time: {avg_waiting:.2f}s")
            print(f"    📊 Efficiency: {efficiency:.1f}%")

class ReadersWritersAI:
    """
    AI-themed Readers-Writers problem
    Multiple AI nodes reading shared model data, fewer nodes updating models
    """
    
    def __init__(self, num_readers: int = 5, num_writers: int = 2):
        self.num_readers = num_readers
        self.num_writers = num_writers
        
        # Shared resource (AI model data)
        self.shared_model_data = {"version": 1, "accuracy": 0.85, "parameters": 1000000}
        
        # Synchronization primitives
        self.read_count = 0
        self.read_count_lock = threading.Lock()
        self.write_lock = threading.Lock()
        
        # Statistics
        self.read_operations = {}
        self.write_operations = {}
        self.reader_wait_times = {}
        self.writer_wait_times = {}
        
        self.running = False
        self.threads = []
        self.start_time = 0
        
    def start_simulation(self, duration: float = 30.0):
        """Start the readers-writers simulation"""
        self.running = True
        self.start_time = time.time()
        
        print("📚 Starting AI Model Access Simulation...")
        print(f"👥 Reader Nodes: {self.num_readers}")
        print(f"✏️ Writer Nodes: {self.num_writers}")
        print("📊 Shared AI Model Data Access Control")
        print("─" * 50)
        
        # Start reader threads
        for i in range(self.num_readers):
            reader_name = f"AI-Reader-{i+1}"
            self.read_operations[reader_name] = 0
            self.reader_wait_times[reader_name] = 0.0
            
            reader_thread = threading.Thread(
                target=self._reader_worker,
                args=(reader_name,),
                daemon=True
            )
            reader_thread.start()
            self.threads.append(reader_thread)
            
        # Start writer threads
        for i in range(self.num_writers):
            writer_name = f"AI-Writer-{i+1}"
            self.write_operations[writer_name] = 0
            self.writer_wait_times[writer_name] = 0.0
            
            writer_thread = threading.Thread(
                target=self._writer_worker,
                args=(writer_name,),
                daemon=True
            )
            writer_thread.start()
            self.threads.append(writer_thread)
            
        # Run simulation
        time.sleep(duration)
        self.running = False
        
        # Wait for threads
        for thread in self.threads:
            thread.join(timeout=2.0)
            
        self._print_statistics()
        
    def _reader_worker(self, reader_name: str):
        """Reader thread worker (reads AI model data)"""
        while self.running:
            wait_start = time.time()
            
            # Reader entry protocol
            with self.read_count_lock:
                self.read_count += 1
                if self.read_count == 1:
                    self.write_lock.acquire()  # First reader locks out writers
                    
            self.reader_wait_times[reader_name] += time.time() - wait_start
            
            # Read the shared model data
            print(f"📖 {reader_name} reading model v{self.shared_model_data['version']} (acc: {self.shared_model_data['accuracy']:.2f})")
            time.sleep(random.uniform(0.1, 0.3))  # Reduced reading time
            self.read_operations[reader_name] += 1
            
            # Reader exit protocol
            with self.read_count_lock:
                self.read_count -= 1
                if self.read_count == 0:
                    self.write_lock.release()  # Last reader allows writers
                    
            print(f"✅ {reader_name} finished reading")
            
            # Think time before next read
            time.sleep(random.uniform(0.3, 1.0))  # Reduced think time
            
    def _writer_worker(self, writer_name: str):
        """Writer thread worker (updates AI model data)"""
        while self.running:
            wait_start = time.time()
            
            # Writer protocol - exclusive access
            self.write_lock.acquire()
            self.writer_wait_times[writer_name] += time.time() - wait_start
            
            try:
                # Update the shared model data
                old_version = self.shared_model_data['version']
                self.shared_model_data['version'] += 1
                self.shared_model_data['accuracy'] = round(random.uniform(0.80, 0.95), 3)
                self.shared_model_data['parameters'] += random.randint(1000, 10000)
                
                print(f"✏️ {writer_name} updating model v{old_version} -> v{self.shared_model_data['version']}")
                time.sleep(random.uniform(0.2, 0.8))  # Reduced writing time
                self.write_operations[writer_name] += 1
                
                print(f"💾 {writer_name} saved model v{self.shared_model_data['version']} (acc: {self.shared_model_data['accuracy']:.3f})")
                
            finally:
                self.write_lock.release()
                
            # Think time before next write
            time.sleep(random.uniform(1.0, 2.5))  # Reduced think time
            
    def _print_statistics(self):
        """Print readers-writers statistics"""
        duration = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📈 AI MODEL ACCESS SIMULATION RESULTS")
        print("=" * 60)
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Final Model Version: {self.shared_model_data['version']}")
        print(f"🎯 Final Model Accuracy: {self.shared_model_data['accuracy']:.3f}")
        
        total_reads = sum(self.read_operations.values())
        total_writes = sum(self.write_operations.values())
        
        print(f"📖 Total Read Operations: {total_reads}")
        print(f"✏️ Total Write Operations: {total_writes}")
        print(f"📊 Read/Write Ratio: {total_reads/max(total_writes, 1):.1f}:1")
        
        print("\n📖 READER STATISTICS:")
        for reader_name, operations in self.read_operations.items():
            avg_wait = self.reader_wait_times[reader_name] / max(operations, 1)
            print(f"  {reader_name}: {operations} reads, avg wait {avg_wait:.3f}s")
            
        print("\n✏️ WRITER STATISTICS:")
        for writer_name, operations in self.write_operations.items():
            avg_wait = self.writer_wait_times[writer_name] / max(operations, 1)
            print(f"  {writer_name}: {operations} writes, avg wait {avg_wait:.3f}s")

class ConcurrencyProblemSuite:
    """Suite of all concurrency problems for comprehensive testing"""
    
    def __init__(self):
        self.problems = {
            ConcurrencyProblemType.PRODUCER_CONSUMER: ProducerConsumerAI,
            ConcurrencyProblemType.DINING_PHILOSOPHERS: DiningPhilosophersAI,
            ConcurrencyProblemType.READERS_WRITERS: ReadersWritersAI
        }
        
    def run_all_problems(self, duration: float = 20.0):
        """Run all concurrency problems sequentially"""
        print("🚀 STARTING COMPREHENSIVE CONCURRENCY SIMULATION")
        print("=" * 80)
        
        for problem_type, problem_class in self.problems.items():
            print(f"\n🔄 Running {problem_type.value} Problem...")
            
            if problem_type == ConcurrencyProblemType.PRODUCER_CONSUMER:
                problem = problem_class(buffer_size=5, num_producers=2, num_consumers=2)
            elif problem_type == ConcurrencyProblemType.DINING_PHILOSOPHERS:
                problem = problem_class(num_philosophers=4)
            elif problem_type == ConcurrencyProblemType.READERS_WRITERS:
                problem = problem_class(num_readers=3, num_writers=1)
                
            problem.start_simulation(duration)
            print(f"✅ {problem_type.value} simulation completed\n")
            time.sleep(2)  # Brief pause between simulations
            
        print("🎉 ALL CONCURRENCY SIMULATIONS COMPLETED!")
        
    def run_specific_problem(self, problem_type: ConcurrencyProblemType, duration: float = 30.0, **kwargs):
        """Run a specific concurrency problem with custom parameters"""
        if problem_type not in self.problems:
            raise ValueError(f"Unknown problem type: {problem_type}")
            
        problem_class = self.problems[problem_type]
        problem = problem_class(**kwargs)
        problem.start_simulation(duration)
        
        return problem 