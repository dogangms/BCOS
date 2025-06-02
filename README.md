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
- ✅ **Step 2**: Memory Management (Complete)
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

## ✅ Step 2: Memory Management System

### 🎯 **Objectives**
Implement comprehensive memory management with paging, address translation, virtual memory, swapping, and AI/blockchain-specific memory constraints.

### ✨ **Features Implemented**

#### Core Memory Management
- **Paging System** - 4KB page-based memory management
- **Page Tables** - Virtual to physical address translation
- **Virtual Memory** - Process isolation and address space management
- **Memory Allocation/Deallocation** - Dynamic memory management
- **Address Translation** - Hardware-simulated memory management unit (MMU)

#### Advanced Memory Features
- **Memory Swapping** - LRU-based page replacement with swap space
- **Memory Fragmentation Handling** - Detection and defragmentation algorithms
- **Memory Pools** - Specialized pools for different memory types
- **Memory Protection** - Read-only and access control mechanisms
- **Memory Statistics** - Comprehensive performance tracking

#### AI/Blockchain Memory Management
- **Themed Memory Constraints** - Separate limits for AI, blockchain, and system memory
- **Memory Type Classification** - 8 different memory types with performance tiers
- **Pinned Memory** - Critical AI models and blockchain data cannot be swapped
- **Performance Tiers** - Different access speeds for memory types
- **Dynamic Memory Allocation** - Runtime memory allocation for AI workloads

#### Memory Visualization
- **Memory Maps** - Visual representation of physical memory layout
- **Page Table Visualization** - Detailed page table information
- **Fragmentation Analysis** - Real-time fragmentation monitoring
- **Memory Pool Status** - Pool-specific usage and performance
- **Swap Space Monitoring** - Swap usage and operation tracking

### 🏗️ **Architecture**

```
BCOS/
├── memory_manager.py           # Core memory management system
├── memory_visualizer.py        # Memory visualization and monitoring
├── memory_demo.py             # Comprehensive memory demonstrations
├── integrated_process_manager.py # Combined process + memory management
├── test_memory_management.py   # Memory system tests
└── README.md                  # This documentation
```

### 🧠 **Memory Types**

The system supports 8 specialized memory types for AI/blockchain workloads:

- ⚙️ **SYSTEM** - Critical system operations (Tier 1, Pinned)
- 👤 **USER** - User application memory (Tier 1, Swappable)
- 🧠 **AI_MODEL** - Machine learning models (Tier 1, Pinned)
- 📊 **AI_DATA** - Training and inference data (Tier 1, Swappable)
- ⛓️ **BLOCKCHAIN_LEDGER** - Blockchain transaction data (Tier 2, Pinned)
- 🔗 **BLOCKCHAIN_STATE** - Smart contract state (Tier 2, Swappable)
- 🌐 **NETWORK_BUFFER** - P2P communication buffers (Tier 1, Swappable)
- 💾 **CACHE** - General purpose cache (Tier 1, Swappable)

### 📄 **Page States**

- ⬜ **FREE** - Available for allocation
- 🟩 **ALLOCATED** - Currently in use
- 🟨 **SWAPPED** - Moved to swap space
- 🟥 **PINNED** - Cannot be swapped (critical data)
- 🟧 **DIRTY** - Modified, needs write-back
- 🟦 **SHARED** - Shared between processes

### 🚀 **Running Step 2**

#### Prerequisites
- Python 3.7+
- No external dependencies required

#### Quick Start
```bash
cd BCOS
python memory_demo.py
```

#### Available Demo Modes
1. **Basic Paging and Address Translation** - Core memory operations
2. **Memory Types and Constraints** - AI/blockchain memory limits
3. **Swapping and Virtual Memory** - Page replacement and virtual memory
4. **Fragmentation and Defragmentation** - Memory fragmentation handling
5. **Specialized Memory Pools** - Pool-based memory management
6. **Performance Analysis** - Memory performance metrics
7. **Interactive Memory Management** - Real-time memory operations

#### Interactive Memory Commands
```
allocate <size> <type>  - Allocate memory of specific type
deallocate <pid>        - Deallocate process memory
access <pid> <offset>   - Access memory at offset
dashboard               - Show full memory dashboard
fragmentation          - Show fragmentation analysis
defrag                 - Perform memory defragmentation
export                 - Export memory state to JSON
monitor                - Start real-time memory monitoring
quit                   - Exit interactive demo
```

### 🔬 **Example Usage**

#### Basic Memory Operations
```python
from memory_manager import MemoryManager, MemoryType

# Initialize memory manager
memory_manager = MemoryManager(total_memory=1024*1024*1024, page_size=4096)

# Allocate memory for AI model
process_id = 1001
virtual_address = memory_manager.allocate_memory(
    process_id, 
    size=10*1024*1024,  # 10MB
    memory_type=MemoryType.AI_MODEL
)

# Access memory
success, data = memory_manager.access_memory(process_id, virtual_address)
print(f"Memory access: {'Success' if success else 'Failed'}")

# Get memory statistics
stats = memory_manager.get_memory_statistics()
print(f"Memory usage: {stats['memory_usage_percent']:.1f}%")
```

#### Integrated Process and Memory Management
```python
from integrated_process_manager import IntegratedProcessManager
from process_control_block import ProcessType

# Initialize integrated manager
manager = IntegratedProcessManager(
    total_memory=2*1024*1024*1024,  # 2GB
    page_size=4096
)

# Create AI inference process with automatic memory allocation
def ai_inference_task():
    # Simulate AI model loading and inference
    return "Inference complete"

pid = manager.create_process(
    name="AI-GPT-Inference",
    process_type=ProcessType.AI_INFERENCE,
    target_function=ai_inference_task,
    memory_required=50*1024*1024  # 50MB
)

# Memory type is automatically set to AI_MODEL based on process type
process_info = manager.get_process_info(pid)
print(f"Process {pid} allocated at: 0x{process_info['virtual_base_address']:08X}")
print(f"Memory type: {process_info['memory_type'].value}")

# Allocate additional memory for the process
additional_addr = manager.allocate_additional_memory(pid, 10*1024*1024)
print(f"Additional memory at: 0x{additional_addr:08X}")
```

#### Memory Visualization
```python
from memory_visualizer import MemoryVisualizer

visualizer = MemoryVisualizer(memory_manager)

# Display comprehensive memory dashboard
visualizer.display_full_memory_dashboard()

# Show specific visualizations
visualizer.display_memory_map(scale=64)
visualizer.display_fragmentation_analysis()
visualizer.display_ai_memory_constraints()

# Export memory state
visualizer.export_memory_state("memory_state.json")

# Start real-time monitoring
visualizer.real_time_memory_monitor(refresh_interval=2.0)
```

### 📊 **Memory Constraints**

The system enforces AI/blockchain-specific memory constraints:

| Memory Category | Allocation Limit | Purpose |
|----------------|------------------|---------|
| **AI Total** | 60% of system memory | AI models + data |
| **AI Models** | 24% of system memory | Critical ML models (pinned) |
| **AI Data** | 36% of system memory | Training/inference data |
| **Blockchain Total** | 30% of system memory | Blockchain operations |
| **Blockchain Ledger** | 18% of system memory | Transaction data (pinned) |
| **Blockchain State** | 12% of system memory | Smart contract state |
| **System** | 10% of system memory | OS operations (pinned) |

### 🎯 **Performance Features**

#### Memory Access Performance
- **Tier 1 (Fastest)**: 0.1-0.3ms access time - AI models, system, network buffers
- **Tier 2 (Medium)**: 1.5-2.0ms access time - Blockchain ledger and state
- **Cache Access**: 0.15ms access time - Optimized cache memory

#### Memory Management Algorithms
- **LRU Page Replacement** - Least Recently Used algorithm for swapping
- **First-Fit Allocation** - Efficient memory allocation strategy
- **Defragmentation** - Automated memory compaction
- **Aging Prevention** - Prevents starvation in swapping decisions

#### Performance Monitoring
- **Page Fault Rate** - Frequency of page faults
- **Swap I/O Operations** - Swap-in and swap-out tracking
- **Fragmentation Level** - Real-time fragmentation measurement
- **Memory Efficiency** - Overall system memory efficiency

### 🧪 **Memory Pool Configuration**

| Pool Name | Size | Performance Tier | Pinned | Purpose |
|-----------|------|------------------|--------|---------|
| **AI Models** | 25% of memory | Tier 1 | Yes | ML model storage |
| **AI Data** | 33% of memory | Tier 1 | No | Training data |
| **Blockchain Ledger** | 17% of memory | Tier 2 | Yes | Transaction history |
| **Blockchain State** | 13% of memory | Tier 2 | No | Contract state |
| **Network Buffers** | 10% of memory | Tier 1 | No | P2P communication |
| **System** | 5% of memory | Tier 1 | Yes | OS operations |

### 🎨 **Visualization Features**

#### Memory Dashboard Elements
- **Memory Header** - System overview with statistics
- **Physical Memory Map** - Visual representation of memory layout
- **Memory Pools Status** - Pool-specific usage and performance
- **Page Table Information** - Virtual memory mappings
- **Fragmentation Analysis** - Memory holes and defragmentation status
- **Swap Space Monitoring** - Swap usage and performance
- **AI/Blockchain Constraints** - Memory limit enforcement status

#### Real-time Monitoring
- **Live Memory Usage** - Continuously updated memory statistics
- **Performance Graphs** - ASCII-based performance visualization
- **Memory Access Patterns** - Real-time access monitoring
- **Alert System** - Warnings for high fragmentation or swap usage

### 🧪 **Testing and Validation**

#### Comprehensive Test Suite
```bash
# Run all memory management tests
python test_memory_management.py

# Test specific components
python -c "from memory_manager import MemoryManager; print('Memory manager loaded')"
python -c "from integrated_process_manager import IntegratedProcessManager; print('Integration works')"
```

#### Performance Benchmarks
- **Memory Allocation**: 100+ allocations per second
- **Address Translation**: 1000+ translations per second
- **Memory Access**: 500+ accesses per second
- **Defragmentation**: Completes in <1 second for 16MB memory

### ✅ **Step 2 Results**
- **Paging System**: ✅ Complete with 4KB pages and page tables
- **Address Translation**: ✅ Virtual to physical address mapping
- **Memory Swapping**: ✅ LRU-based page replacement with swap space
- **Fragmentation Handling**: ✅ Detection, analysis, and defragmentation
- **AI/Blockchain Constraints**: ✅ Themed memory limits and pools
- **Memory Visualization**: ✅ Comprehensive dashboards and monitoring
- **Integration**: ✅ Seamless process-memory management integration
- **Performance**: ✅ Optimized for AI/blockchain workloads

---

## 🔄 Step 3: File System

### 🎯 **Objectives** (Upcoming)
*Will be implemented in the next phase*

### 📋 **Planned Features**
- Virtual File System
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
python test_memory_management.py

# Start interactive demo
python demo.py
python memory_demo.py
```

### Testing
```bash
# Run basic functionality tests
python test_basic.py

# Run memory management tests
python test_memory_management.py

# Test individual components
python -c "from schedulers import *; print('Schedulers loaded successfully')"
python -c "from memory_manager import *; print('Memory manager loaded successfully')"
```

---

## 🤝 Contributing

This project welcomes contributions for:

### Current (Steps 1 & 2)
- Additional scheduler algorithms
- Memory allocation optimizations
- Enhanced visualization features
- Better AI/ML workload simulation
- Performance improvements

### Future Steps
- File system implementations
- Network protocols
- Security enhancements
- Distributed computing features

---

## 📚 Learning Resources

This project demonstrates key operating system concepts:

1. **Process Management** - Scheduling algorithms, context switching
2. **Memory Management** - Paging, virtual memory, swapping
3. **System Calls** - Process and memory management APIs
4. **Concurrency** - Multi-threading and synchronization
5. **Performance Analysis** - Metrics collection and visualization
6. **System Design** - Modular architecture and clean interfaces

---

## 📝 License

This project is part of an educational operating system development series focused on decentralized AI and blockchain applications.

---

## 📊 Current Status

| Component | Status | Features | Performance |
|-----------|--------|----------|-------------|
| **Step 1: Process Management** | ✅ Complete | 4 schedulers, visualization, AI workloads | Excellent |
| **Step 2: Memory Management** | ✅ Complete | Paging, swapping, AI constraints, visualization | Excellent |
| **Step 3: File System** | 🔄 Planned | Distributed storage, AI model caching | - |
| **Step 4: Network Communication** | 🔄 Planned | P2P protocols, inter-node communication | - |

**Current Milestone**: Step 2 Complete ✅  
**Next Milestone**: Step 3 - File System Implementation  
**Project Completion**: 50% (2/4 major steps)