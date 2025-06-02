# 🚀 Decentralized AI Node Operating System

## 📋 Project Overview

This project implements a **Decentralized AI Node Operating System** designed specifically for distributed AI and blockchain workloads. The system is built incrementally through multiple steps, each adding core operating system functionality.

### 🎯 System Goals
- **Decentralized Architecture** - Support for distributed AI nodes
- **AI/Blockchain Optimized** - Specialized for AI inference and blockchain validation
- **Educational Focus** - Clear, documented implementation of OS concepts
- **Modular Design** - Step-by-step implementation for learning

### 🗂️ Implementation Steps
- ✅ **Step 1**: Process Management (Complete)
- 🔄 **Step 2**: Memory Management (Upcoming)
- 🔄 **Step 3**: File System (Upcoming) 
- 🔄 **Step 4**: Network Communication (Upcoming)

---

## ✅ Step 1: Process Management System

### 🎯 **Objectives**
Implement core process management functionality including process creation, scheduling, switching, and termination with specialized support for AI and blockchain workloads.

### ✨ **Features Implemented**

#### Core Process Management
- **Process Control Block (PCB)** - Complete process information storage
- **Process Creation, Switching, and Termination** - Full process lifecycle management
- **Memory Simulation** - Basic memory allocation and deallocation
- **Process States** - NEW, READY, RUNNING, WAITING, TERMINATED, SUSPENDED

#### Scheduler Implementations
1. **FIFO (First In, First Out)** - Simple first-come-first-served scheduling
2. **Round Robin** - Time-slice based preemptive scheduling
3. **Priority Scheduler** - Priority-based scheduling with preemption
4. **Multi-Level Feedback Queue (MLFQ)** - Advanced scheduling with aging prevention

#### AI Node Specific Features
- **Themed Process Types** - AI_INFERENCE, DATA_PROCESSING, BLOCKCHAIN_VALIDATOR, NETWORK_NODE, SYSTEM, USER
- **Resource Requirements** - CPU, memory, GPU, and network bandwidth tracking
- **Node Management** - Unique node ID and connection tracking
- **Performance Metrics** - Comprehensive statistics and monitoring

#### Visualization & Monitoring
- **Real-time Dashboard** - Live system status visualization
- **Process Queue Visualization** - Visual representation of scheduler queues
- **Performance Statistics** - Wait time, turnaround time, throughput metrics
- **System State Export** - JSON export for analysis
- **Interactive Console** - Command-line interface for process management

### 🏗️ **Architecture**

```
BCOS/
├── process_control_block.py    # PCB implementation with process states and types
├── schedulers.py              # All scheduler implementations
├── process_manager.py         # Main process manager with threading
├── process_visualizer.py      # Visualization and monitoring system
├── demo.py                   # Comprehensive demonstration script
├── test_basic.py             # Basic functionality tests
└── README.md                 # This documentation
```

### 🎯 **Process Types**

The system supports specialized process types for decentralized AI nodes:

- 🧠 **AI_INFERENCE** - Machine learning inference tasks
- 📊 **DATA_PROCESSING** - Data analysis and transformation
- ⛓️ **BLOCKCHAIN_VALIDATOR** - Blockchain validation and mining
- 🌐 **NETWORK_NODE** - P2P network communication
- ⚙️ **SYSTEM** - System maintenance and management
- 👤 **USER** - User-initiated processes

### 🚀 **Running Step 1**

#### Prerequisites
- Python 3.7+
- No external dependencies required (uses only standard library)

#### Quick Start
```bash
cd BCOS
python demo.py
```

#### Available Demo Modes
1. **FIFO Scheduler Demo** - Demonstrates first-in-first-out scheduling
2. **Round Robin Demo** - Shows time-slice based scheduling
3. **Priority Scheduler Demo** - Exhibits priority-based preemptive scheduling
4. **MLFQ Demo** - Multi-level feedback queue with aging
5. **Interactive Mode** - Command-line interface for real-time interaction
6. **All Demos** - Runs all scheduler demonstrations sequentially

#### Interactive Commands
```
create          - Create a new process
list            - List all active processes  
kill <pid>      - Terminate a process
suspend <pid>   - Suspend a process
resume <pid>    - Resume a suspended process
dashboard       - Show full system dashboard
monitor         - Start real-time monitoring
export          - Export system state to JSON
quit            - Exit the system
```

### 🔬 **Example Usage**

#### Basic Process Creation
```python
from process_manager import ProcessManager
from process_control_block import ProcessType
from schedulers import RoundRobinScheduler

# Initialize with Round Robin scheduler
manager = ProcessManager(RoundRobinScheduler(time_quantum=1000))
manager.start_scheduler()

# Create an AI inference process
def ai_task(model_name, data_size):
    print(f"Running {model_name} on {data_size} samples")
    # Your AI workload here
    return "Inference complete"

pid = manager.create_process(
    name="AI-GPT-4",
    process_type=ProcessType.AI_INFERENCE,
    target_function=ai_task,
    args=("GPT-4", 100),
    priority=5,
    memory_required=2048
)

# Monitor the process
info = manager.get_process_info(pid)
print(f"Process {pid}: {info}")

# Cleanup
manager.shutdown()
```

#### Scheduler Comparison
```python
from schedulers import FIFOScheduler, PriorityScheduler, MLFQScheduler

# Try different schedulers
schedulers = [
    FIFOScheduler(),
    PriorityScheduler(preemptive=True),
    MLFQScheduler(num_levels=3, time_quanta=[100, 200, 400])
]

for scheduler in schedulers:
    manager = ProcessManager(scheduler)
    # Create processes and compare performance
    stats = scheduler.get_statistics()
    print(f"{scheduler.name}: {stats}")
```

### 📊 **Performance Metrics**

#### Process Metrics
- **Creation Time** - When process was created
- **CPU Time Used** - Total CPU time consumed
- **Wait Time** - Time spent waiting in queues
- **Turnaround Time** - Total time from creation to completion
- **Memory Usage** - Allocated memory size

#### Scheduler Metrics
- **Average Wait Time** - Mean time processes wait
- **Average Turnaround Time** - Mean total completion time
- **Throughput** - Processes completed per second
- **Context Switches** - Number of process switches

#### System Metrics
- **Memory Usage** - Total system memory utilization
- **Active Processes** - Currently running processes
- **Queue Lengths** - Processes waiting in each queue level
- **Uptime** - System operational time

### 🎨 **Visualization Features**

#### Dashboard Elements
- **System Header** - Node ID, scheduler type, uptime, context switches
- **Memory Status** - Usage bar and statistics
- **Process List** - All active processes with icons and states
- **Scheduler Queues** - Queue contents for each level
- **Performance Statistics** - Real-time metrics
- **AI Node Status** - Specialized process type counts

#### Process Icons & State Indicators
- 🧠 AI Inference processes | 🆕 NEW - Just created
- 📊 Data Processing tasks | ⏳ READY - Waiting to run
- ⛓️ Blockchain Validators | 🏃 RUNNING - Currently executing
- 🌐 Network Nodes | ⏸️ WAITING - Blocked on I/O
- ⚙️ System processes | 😴 SUSPENDED - Temporarily stopped
- 👤 User tasks | 💀 TERMINATED - Completed

### 🧪 **Scheduler Comparison**

| Scheduler | Best For | Characteristics | Use Case |
|-----------|----------|-----------------|----------|
| **FIFO** | Batch processing | No preemption, run to completion | Background data processing |
| **Round Robin** | Interactive systems | Time-slice preemption, equal sharing | Multi-user AI inference |
| **Priority** | Different importance levels | Higher priority preempts lower | Critical blockchain validation |
| **MLFQ** | Mixed workload environments | Adaptive priority, prevents starvation | Decentralized AI/blockchain nodes |

### ✅ **Step 1 Results**
- **Process Management**: ✅ Complete with creation, switching, termination
- **Process Control Block**: ✅ Comprehensive PCB implementation
- **Schedulers**: ✅ 4 different algorithms implemented
- **Visualization**: ✅ Real-time dashboard and monitoring
- **AI Node Features**: ✅ Specialized process types and workloads
- **Performance Tracking**: ✅ Comprehensive metrics and analysis

---

## 🔄 Step 2: Memory Management System

### 🎯 **Objectives** (Upcoming)
*Will be implemented in the next phase*

### 📋 **Planned Features**
- Virtual Memory Management
- Paging and Segmentation
- Memory Allocation Algorithms
- Garbage Collection for AI Models
- Memory Protection and Isolation

---

## 🔄 Step 3: File System

### 🎯 **Objectives** (Upcoming)
*Will be implemented in a future phase*

### 📋 **Planned Features**
- Distributed File System
- AI Model Storage and Caching
- Blockchain Data Management
- File Allocation and Organization

---

## 🔄 Step 4: Network Communication

### 🎯 **Objectives** (Upcoming)
*Will be implemented in a future phase*

### 📋 **Planned Features**
- P2P Network Protocol
- Inter-node Communication
- Distributed Process Migration
- Network Security and Encryption

---

## 🔧 Installation & Development

### Prerequisites
- Python 3.7 or higher
- Standard library only (no external dependencies)

### Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd BlockchainOS/BCOS

# Run tests
python test_basic.py

# Start interactive demo
python demo.py
```

### Testing
```bash
# Run basic functionality tests
python test_basic.py

# Test individual components
python -c "from schedulers import *; print('Schedulers loaded successfully')"
python -c "from process_manager import *; print('Process manager loaded successfully')"
```

---

## 🤝 Contributing

This project welcomes contributions for:

### Current (Step 1)
- Additional scheduler algorithms
- Performance optimizations
- Enhanced visualization features
- Better AI/ML workload simulation

### Future Steps
- Memory management algorithms
- File system implementations
- Network protocols
- Security enhancements

---

## 📚 Learning Resources

This project demonstrates key operating system concepts:

1. **Process Management** - Scheduling algorithms, context switching
2. **System Calls** - Process creation and management APIs
3. **Concurrency** - Multi-threading and synchronization
4. **Performance Analysis** - Metrics collection and visualization
5. **System Design** - Modular architecture and clean interfaces

---

## 📝 License

This project is part of an educational operating system development series focused on decentralized AI and blockchain applications.

---

## 📊 Current Status

| Component | Status | Features | Performance |
|-----------|--------|----------|-------------|
| **Step 1: Process Management** | ✅ Complete | 4 schedulers, visualization, AI workloads | Excellent |
| **Step 2: Memory Management** | 🔄 Planned | Virtual memory, paging, allocation | - |
| **Step 3: File System** | 🔄 Planned | Distributed storage, AI model caching | - |
| **Step 4: Network Communication** | 🔄 Planned | P2P protocols, inter-node communication | - |

**Current Milestone**: Step 1 Complete ✅  
**Next Milestone**: Step 2 - Memory Management System  
**Project Completion**: 25% (1/4 major steps)