"""
Decentralized AI Node Operating System - Step 5: AI-Based Intelligent Scheduler
Advanced machine learning scheduler that adapts to AI/blockchain workloads and optimizes performance.
"""

import time
import random
import math
import json
import threading
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
import statistics

# Import existing components
try:
    from process_control_block import Process, ProcessState, ProcessType
    from scheduler import SchedulingAlgorithm
except ImportError:
    # Fallback definitions for standalone usage
    class ProcessState(Enum):
        NEW = "new"
        READY = "ready"
        RUNNING = "running"
        WAITING = "waiting"
        TERMINATED = "terminated"
    
    class ProcessType(Enum):
        SYSTEM = "system"
        AI_WORKER = "ai_worker"
        BLOCKCHAIN_MINER = "blockchain_miner"
        SMART_CONTRACT = "smart_contract"
        NETWORK_HANDLER = "network_handler"

class SchedulingMetric(Enum):
    """Metrics for evaluating scheduling performance"""
    THROUGHPUT = "throughput"
    RESPONSE_TIME = "response_time"
    TURNAROUND_TIME = "turnaround_time"
    CPU_UTILIZATION = "cpu_utilization"
    POWER_EFFICIENCY = "power_efficiency"
    AI_ACCURACY = "ai_accuracy"
    BLOCKCHAIN_HASH_RATE = "blockchain_hash_rate"

class LearningMode(Enum):
    """AI learning modes for different optimization strategies"""
    PERFORMANCE = "🚀 Performance Optimization"
    POWER_SAVING = "🔋 Power Saving"
    BALANCED = "⚖️ Balanced"
    AI_FOCUSED = "🧠 AI Workload Focused"
    BLOCKCHAIN_FOCUSED = "⛓️ Blockchain Focused"

@dataclass
class ProcessPattern:
    """Pattern data for process behavior analysis"""
    process_type: ProcessType
    avg_cpu_time: float = 0.0
    avg_memory_usage: float = 0.0
    avg_io_operations: float = 0.0
    success_rate: float = 1.0
    power_consumption: float = 0.0
    priority_effectiveness: float = 0.0
    execution_count: int = 0
    last_updated: float = field(default_factory=time.time)

@dataclass
class SchedulingDecision:
    """Record of a scheduling decision and its outcome"""
    timestamp: float
    process_id: str
    process_type: ProcessType
    predicted_runtime: float
    actual_runtime: float
    cpu_core: int
    priority: int
    power_mode: str
    performance_score: float
    success: bool

class PowerManager:
    """Power-aware scheduling component"""
    
    def __init__(self):
        self.power_states = {
            "high_performance": {"multiplier": 1.0, "base_power": 100},
            "balanced": {"multiplier": 0.8, "base_power": 80},
            "power_saver": {"multiplier": 0.6, "base_power": 60},
            "eco_mode": {"multiplier": 0.4, "base_power": 40}
        }
        self.current_power_budget = 100.0
        self.power_history = deque(maxlen=100)
        
    def get_optimal_power_state(self, process_type: ProcessType, system_load: float) -> str:
        """Determine optimal power state for process type and system load"""
        if process_type == ProcessType.AI_WORKER and system_load < 0.7:
            return "high_performance"  # AI needs performance
        elif process_type == ProcessType.BLOCKCHAIN_MINER:
            return "balanced"  # Blockchain needs sustained performance
        elif system_load > 0.9:
            return "power_saver"  # High load, save power
        else:
            return "balanced"
            
    def calculate_power_cost(self, process_type: ProcessType, runtime: float, power_state: str) -> float:
        """Calculate estimated power consumption"""
        base_power = self.power_states[power_state]["base_power"]
        type_multiplier = {
            ProcessType.AI_WORKER: 1.5,
            ProcessType.BLOCKCHAIN_MINER: 1.8,
            ProcessType.SMART_CONTRACT: 1.0,
            ProcessType.NETWORK_HANDLER: 0.8,
            ProcessType.SYSTEM: 0.6
        }.get(process_type, 1.0)
        
        return base_power * type_multiplier * runtime / 3600  # Watt-hours

class PerformancePredictor:
    """ML-based performance prediction component"""
    
    def __init__(self):
        self.patterns = defaultdict(lambda: ProcessPattern(ProcessType.SYSTEM))
        self.prediction_history = deque(maxlen=1000)
        self.learning_rate = 0.1
        self.model_weights = {
            "cpu_time": 0.3,
            "memory": 0.2,
            "io_ops": 0.15,
            "priority": 0.2,
            "type_bonus": 0.15
        }
        
    def record_execution(self, process_id: str, process_type: ProcessType, 
                        runtime: float, memory_used: float, io_ops: int, 
                        success: bool):
        """Record process execution for learning"""
        pattern = self.patterns[process_type]
        
        # Update pattern using exponential moving average
        if pattern.execution_count == 0:
            pattern.avg_cpu_time = runtime
            pattern.avg_memory_usage = memory_used
            pattern.avg_io_operations = io_ops
            pattern.success_rate = 1.0 if success else 0.0
        else:
            alpha = self.learning_rate
            pattern.avg_cpu_time = (1 - alpha) * pattern.avg_cpu_time + alpha * runtime
            pattern.avg_memory_usage = (1 - alpha) * pattern.avg_memory_usage + alpha * memory_used
            pattern.avg_io_operations = (1 - alpha) * pattern.avg_io_operations + alpha * io_ops
            pattern.success_rate = (1 - alpha) * pattern.success_rate + alpha * (1.0 if success else 0.0)
            
        pattern.execution_count += 1
        pattern.last_updated = time.time()
        
    def predict_runtime(self, process_type: ProcessType, base_estimate: float = None) -> float:
        """Predict process runtime based on historical patterns"""
        if process_type not in self.patterns or self.patterns[process_type].execution_count == 0:
            # No historical data, use base estimate with type-specific adjustments
            base = base_estimate or random.uniform(0.1, 2.0)
            type_multipliers = {
                ProcessType.AI_WORKER: 1.5,
                ProcessType.BLOCKCHAIN_MINER: 2.0,
                ProcessType.SMART_CONTRACT: 0.8,
                ProcessType.NETWORK_HANDLER: 0.6,
                ProcessType.SYSTEM: 0.4
            }
            return base * type_multipliers.get(process_type, 1.0)
        
        pattern = self.patterns[process_type]
        predicted = pattern.avg_cpu_time
        
        # Add some variance based on success rate
        variance_factor = 1.0 + (1.0 - pattern.success_rate) * 0.5
        return predicted * variance_factor
        
    def calculate_priority_score(self, process_type: ProcessType, system_load: float) -> int:
        """Calculate intelligent priority based on ML insights"""
        base_priorities = {
            ProcessType.SYSTEM: 90,
            ProcessType.AI_WORKER: 70,
            ProcessType.BLOCKCHAIN_MINER: 60,
            ProcessType.SMART_CONTRACT: 80,
            ProcessType.NETWORK_HANDLER: 65
        }
        
        base_priority = base_priorities.get(process_type, 50)
        
        # Adjust based on system load and success rate
        if process_type in self.patterns:
            pattern = self.patterns[process_type]
            success_adjustment = (pattern.success_rate - 0.5) * 20
            load_adjustment = (1.0 - system_load) * 10
            base_priority += success_adjustment + load_adjustment
            
        return max(1, min(100, int(base_priority)))

class AIScheduler:
    """
    AI-Based Intelligent Scheduler
    Uses machine learning to optimize scheduling decisions for AI/blockchain workloads
    """
    
    def __init__(self, num_cores: int = 4):
        self.num_cores = num_cores
        self.learning_mode = LearningMode.BALANCED
        
        # Core components
        self.predictor = PerformancePredictor()
        self.power_manager = PowerManager()
        
        # State tracking
        self.ready_queue = deque()
        self.running_processes = {}  # core_id -> process
        self.core_loads = [0.0] * num_cores
        self.system_metrics = {
            "throughput": 0.0,
            "avg_response_time": 0.0,
            "power_consumption": 0.0,
            "cpu_utilization": 0.0
        }
        
        # Learning data
        self.decision_history = deque(maxlen=1000)
        self.performance_scores = deque(maxlen=100)
        
        # Synchronization
        self.scheduler_lock = threading.RLock()
        
        # Statistics
        self.total_scheduled = 0
        self.successful_predictions = 0
        self.adaptation_count = 0
        
    def add_process(self, process_id: str, process_type: ProcessType, 
                   estimated_time: float = None, memory_req: float = 100.0):
        """Add process to scheduling queue with AI-based prioritization"""
        with self.scheduler_lock:
            # Predict runtime and calculate intelligent priority
            predicted_runtime = self.predictor.predict_runtime(process_type, estimated_time)
            system_load = sum(self.core_loads) / len(self.core_loads)
            priority = self.predictor.calculate_priority_score(process_type, system_load)
            
            # Determine optimal power state
            power_state = self.power_manager.get_optimal_power_state(process_type, system_load)
            
            process_info = {
                "id": process_id,
                "type": process_type,
                "predicted_runtime": predicted_runtime,
                "priority": priority,
                "power_state": power_state,
                "memory_req": memory_req,
                "arrival_time": time.time(),
                "start_time": None,
                "actual_runtime": 0.0
            }
            
            # Insert in priority order (higher priority first)
            inserted = False
            for i, existing in enumerate(self.ready_queue):
                if priority > existing["priority"]:
                    self.ready_queue.insert(i, process_info)
                    inserted = True
                    break
                    
            if not inserted:
                self.ready_queue.append(process_info)
                
            self.total_scheduled += 1
            
    def schedule_next(self) -> Optional[Dict]:
        """Schedule next process using AI-optimized algorithm"""
        with self.scheduler_lock:
            if not self.ready_queue:
                return None
                
            # Find best core for next process
            best_process_idx = None
            best_core = None
            best_score = float('-inf')
            
            for proc_idx, process in enumerate(self.ready_queue):
                for core_id in range(self.num_cores):
                    if core_id not in self.running_processes:
                        score = self._calculate_scheduling_score(process, core_id)
                        if score > best_score:
                            best_score = score
                            best_process_idx = proc_idx
                            best_core = core_id
                            
            if best_process_idx is not None and best_core is not None:
                process = self.ready_queue[best_process_idx]
                del self.ready_queue[best_process_idx]
                
                # Assign to core
                process["core_id"] = best_core
                process["start_time"] = time.time()
                self.running_processes[best_core] = process
                self.core_loads[best_core] = min(1.0, self.core_loads[best_core] + 0.3)
                
                # Record scheduling decision
                decision = SchedulingDecision(
                    timestamp=time.time(),
                    process_id=process["id"],
                    process_type=process["type"],
                    predicted_runtime=process["predicted_runtime"],
                    actual_runtime=0.0,  # Will be updated when process completes
                    cpu_core=best_core,
                    priority=process["priority"],
                    power_mode=process["power_state"],
                    performance_score=best_score,
                    success=True
                )
                self.decision_history.append(decision)
                
                return process
                
            return None
            
    def _calculate_scheduling_score(self, process: Dict, core_id: int) -> float:
        """Calculate scheduling score for process-core combination"""
        # Base score from priority
        score = process["priority"]
        
        # Core load penalty
        load_penalty = self.core_loads[core_id] * 50
        score -= load_penalty
        
        # Type-specific bonuses
        type_bonuses = {
            ProcessType.AI_WORKER: 10,
            ProcessType.BLOCKCHAIN_MINER: 8,
            ProcessType.SMART_CONTRACT: 12,
            ProcessType.NETWORK_HANDLER: 6,
            ProcessType.SYSTEM: 15
        }
        score += type_bonuses.get(process["type"], 0)
        
        # Power efficiency bonus
        if process["power_state"] in ["balanced", "power_saver"]:
            score += 5
            
        # Learning mode adjustments
        if self.learning_mode == LearningMode.AI_FOCUSED and process["type"] == ProcessType.AI_WORKER:
            score += 20
        elif self.learning_mode == LearningMode.BLOCKCHAIN_FOCUSED and process["type"] == ProcessType.BLOCKCHAIN_MINER:
            score += 20
        elif self.learning_mode == LearningMode.POWER_SAVING:
            if process["power_state"] in ["power_saver", "eco_mode"]:
                score += 15
                
        return score
        
    def complete_process(self, core_id: int, success: bool = True, 
                        actual_memory: float = None, io_operations: int = 0):
        """Mark process as completed and update learning data"""
        with self.scheduler_lock:
            if core_id not in self.running_processes:
                return
                
            process = self.running_processes[core_id]
            actual_runtime = time.time() - process["start_time"]
            process["actual_runtime"] = actual_runtime
            
            # Update predictor with execution data
            self.predictor.record_execution(
                process["id"],
                process["type"],
                actual_runtime,
                actual_memory or process["memory_req"],
                io_operations,
                success
            )
            
            # Update decision history
            for decision in reversed(self.decision_history):
                if decision.process_id == process["id"] and decision.actual_runtime == 0.0:
                    decision.actual_runtime = actual_runtime
                    decision.success = success
                    
                    # Calculate prediction accuracy
                    prediction_error = abs(decision.predicted_runtime - actual_runtime) / max(actual_runtime, 0.1)
                    if prediction_error < 0.3:  # Within 30% is considered successful
                        self.successful_predictions += 1
                    break
                    
            # Update core state
            self.core_loads[core_id] = max(0.0, self.core_loads[core_id] - 0.3)
            del self.running_processes[core_id]
            
            # Calculate performance score for this execution
            response_time = actual_runtime
            efficiency_score = min(100, (process["predicted_runtime"] / max(actual_runtime, 0.1)) * 100)
            power_cost = self.power_manager.calculate_power_cost(
                process["type"], actual_runtime, process["power_state"]
            )
            
            performance_score = efficiency_score - power_cost * 10
            self.performance_scores.append(performance_score)
            
            # Adaptive learning based on performance
            if len(self.performance_scores) >= 10:
                avg_performance = statistics.mean(list(self.performance_scores)[-10:])
                if avg_performance < 50:  # Poor performance, adapt
                    self._adapt_scheduling_strategy()
                    
    def _adapt_scheduling_strategy(self):
        """Adapt scheduling strategy based on recent performance"""
        self.adaptation_count += 1
        
        # Analyze recent performance patterns
        recent_decisions = list(self.decision_history)[-20:]
        if not recent_decisions:
            return
            
        # Check if AI or blockchain processes are underperforming
        ai_performance = [d.performance_score for d in recent_decisions 
                         if d.process_type == ProcessType.AI_WORKER and d.success]
        blockchain_performance = [d.performance_score for d in recent_decisions 
                                if d.process_type == ProcessType.BLOCKCHAIN_MINER and d.success]
        
        if ai_performance and statistics.mean(ai_performance) < 40:
            self.learning_mode = LearningMode.AI_FOCUSED
            self.predictor.learning_rate = min(0.3, self.predictor.learning_rate * 1.2)
        elif blockchain_performance and statistics.mean(blockchain_performance) < 40:
            self.learning_mode = LearningMode.BLOCKCHAIN_FOCUSED
            self.predictor.learning_rate = min(0.3, self.predictor.learning_rate * 1.2)
        else:
            self.learning_mode = LearningMode.BALANCED
            self.predictor.learning_rate = max(0.05, self.predictor.learning_rate * 0.9)
            
    def get_ai_metrics(self) -> Dict[str, Any]:
        """Get comprehensive AI scheduler metrics"""
        with self.scheduler_lock:
            prediction_accuracy = 0.0
            if self.total_scheduled > 0:
                prediction_accuracy = (self.successful_predictions / self.total_scheduled) * 100
                
            avg_performance = 0.0
            if self.performance_scores:
                avg_performance = statistics.mean(self.performance_scores)
                
            system_load = sum(self.core_loads) / len(self.core_loads)
            
            # Process type distribution
            type_distribution = defaultdict(int)
            for decision in list(self.decision_history)[-50:]:
                type_distribution[decision.process_type.value] += 1
                
            return {
                "learning_mode": self.learning_mode.value,
                "prediction_accuracy": prediction_accuracy,
                "avg_performance_score": avg_performance,
                "total_scheduled": self.total_scheduled,
                "successful_predictions": self.successful_predictions,
                "adaptation_count": self.adaptation_count,
                "system_load": system_load,
                "active_cores": len(self.running_processes),
                "queue_length": len(self.ready_queue),
                "process_patterns": len(self.predictor.patterns),
                "recent_decisions": len(self.decision_history),
                "type_distribution": dict(type_distribution),
                "core_loads": self.core_loads.copy(),
                "power_budget": self.power_manager.current_power_budget,
                "learning_rate": self.predictor.learning_rate
            }
            
    def set_learning_mode(self, mode: LearningMode):
        """Set AI learning and optimization mode"""
        with self.scheduler_lock:
            self.learning_mode = mode
            
            # Adjust learning parameters based on mode
            if mode == LearningMode.PERFORMANCE:
                self.predictor.learning_rate = 0.2
            elif mode == LearningMode.POWER_SAVING:
                self.predictor.learning_rate = 0.1
            elif mode == LearningMode.AI_FOCUSED:
                self.predictor.learning_rate = 0.15
            elif mode == LearningMode.BLOCKCHAIN_FOCUSED:
                self.predictor.learning_rate = 0.15
            else:  # BALANCED
                self.predictor.learning_rate = 0.1
                
    def export_learning_data(self, filename: str):
        """Export AI learning data for analysis"""
        learning_data = {
            "timestamp": time.time(),
            "scheduler_metrics": self.get_ai_metrics(),
            "process_patterns": {
                str(ptype): {
                    "avg_cpu_time": pattern.avg_cpu_time,
                    "avg_memory_usage": pattern.avg_memory_usage,
                    "avg_io_operations": pattern.avg_io_operations,
                    "success_rate": pattern.success_rate,
                    "execution_count": pattern.execution_count
                }
                for ptype, pattern in self.predictor.patterns.items()
            },
            "recent_decisions": [
                {
                    "timestamp": d.timestamp,
                    "process_type": d.process_type.value,
                    "predicted_runtime": d.predicted_runtime,
                    "actual_runtime": d.actual_runtime,
                    "cpu_core": d.cpu_core,
                    "priority": d.priority,
                    "power_mode": d.power_mode,
                    "performance_score": d.performance_score,
                    "success": d.success
                }
                for d in list(self.decision_history)[-100:]
            ],
            "performance_history": list(self.performance_scores)
        }
        
        with open(filename, 'w') as f:
            json.dump(learning_data, f, indent=2)
            
    def simulate_workload(self, duration: float = 30.0):
        """Simulate AI/blockchain workload for demonstration"""
        print("🤖 Starting AI scheduler workload simulation...")
        start_time = time.time()
        process_counter = 0
        
        while time.time() - start_time < duration:
            # Generate realistic workload
            if random.random() < 0.7:  # 70% chance to add process
                process_counter += 1
                process_type = random.choices(
                    list(ProcessType),
                    weights=[10, 30, 25, 20, 15],  # Favor AI and blockchain
                    k=1
                )[0]
                
                estimated_time = random.uniform(0.5, 3.0)
                memory_req = random.uniform(50, 500)
                
                self.add_process(f"proc_{process_counter}", process_type, estimated_time, memory_req)
                
            # Schedule processes
            scheduled = self.schedule_next()
            if scheduled:
                # Simulate process execution
                threading.Thread(
                    target=self._simulate_process_execution,
                    args=(scheduled,),
                    daemon=True
                ).start()
                
            time.sleep(random.uniform(0.1, 0.5))
            
        print(f"✅ Simulation completed. Scheduled {self.total_scheduled} processes.")
        
    def _simulate_process_execution(self, process: Dict):
        """Simulate process execution with realistic timing"""
        # Simulate variable execution time
        base_time = process["predicted_runtime"]
        actual_time = base_time * random.uniform(0.7, 1.4)  # ±40% variance
        
        time.sleep(actual_time)
        
        # Simulate success/failure
        success_rates = {
            ProcessType.SYSTEM: 0.95,
            ProcessType.AI_WORKER: 0.85,
            ProcessType.BLOCKCHAIN_MINER: 0.90,
            ProcessType.SMART_CONTRACT: 0.88,
            ProcessType.NETWORK_HANDLER: 0.92
        }
        
        success = random.random() < success_rates.get(process["type"], 0.9)
        memory_used = process["memory_req"] * random.uniform(0.8, 1.2)
        io_ops = random.randint(0, 50)
        
        self.complete_process(process["core_id"], success, memory_used, io_ops) 