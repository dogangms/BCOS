#!/usr/bin/env python3
"""
Memory Management System for Decentralized AI Node Operating System
Implements paging, address translation, memory allocation, and AI-specific features
"""

import time
import math
import random
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict

class MemoryType(Enum):
    """Types of memory for AI/Blockchain workloads"""
    SYSTEM = "system"
    USER = "user"
    AI_MODEL = "ai_model"
    AI_DATA = "ai_data"
    BLOCKCHAIN_LEDGER = "blockchain_ledger"
    BLOCKCHAIN_STATE = "blockchain_state"
    NETWORK_BUFFER = "network_buffer"
    CACHE = "cache"

class PageState(Enum):
    """Page states for memory management"""
    FREE = "free"
    ALLOCATED = "allocated"
    SWAPPED = "swapped"
    PINNED = "pinned"  # Cannot be swapped (critical AI models)
    DIRTY = "dirty"    # Modified, needs write-back
    SHARED = "shared"  # Shared between processes

@dataclass
class Page:
    """Physical page representation"""
    page_number: int
    physical_address: int
    state: PageState
    process_id: Optional[int] = None
    memory_type: MemoryType = MemoryType.USER
    last_access_time: float = 0.0
    reference_count: int = 0  # For shared pages
    dirty: bool = False
    pinned: bool = False
    
    def __post_init__(self):
        self.last_access_time = time.time()

@dataclass
class PageTableEntry:
    """Page table entry for address translation"""
    virtual_page: int
    physical_page: Optional[int] = None
    present: bool = False
    read_only: bool = False
    dirty: bool = False
    accessed: bool = False
    user_accessible: bool = True
    cache_disabled: bool = False
    
    def get_physical_address(self, page_size: int, offset: int) -> Optional[int]:
        """Convert to physical address"""
        if not self.present or self.physical_page is None:
            return None
        return (self.physical_page * page_size) + offset

class PageTable:
    """Page table for virtual to physical address translation"""
    
    def __init__(self, process_id: int, page_size: int = 4096):
        self.process_id = process_id
        self.page_size = page_size
        self.entries: Dict[int, PageTableEntry] = {}
        self.creation_time = time.time()
        
    def add_mapping(self, virtual_page: int, physical_page: int, 
                   read_only: bool = False, user_accessible: bool = True):
        """Add virtual to physical page mapping"""
        entry = PageTableEntry(
            virtual_page=virtual_page,
            physical_page=physical_page,
            present=True,
            read_only=read_only,
            user_accessible=user_accessible
        )
        self.entries[virtual_page] = entry
        
    def remove_mapping(self, virtual_page: int):
        """Remove page mapping"""
        if virtual_page in self.entries:
            del self.entries[virtual_page]
    
    def translate_address(self, virtual_address: int) -> Tuple[Optional[int], bool]:
        """Translate virtual address to physical address"""
        virtual_page = virtual_address // self.page_size
        offset = virtual_address % self.page_size
        
        if virtual_page not in self.entries:
            return None, False  # Page fault
        
        entry = self.entries[virtual_page]
        if not entry.present:
            return None, False  # Page fault
        
        # Mark as accessed
        entry.accessed = True
        
        physical_address = entry.get_physical_address(self.page_size, offset)
        return physical_address, True

class MemoryPool:
    """Specialized memory pool for different memory types"""
    
    def __init__(self, name: str, memory_type: MemoryType, size: int, 
                 pinned: bool = False, performance_tier: int = 1):
        self.name = name
        self.memory_type = memory_type
        self.size = size
        self.pinned = pinned
        self.performance_tier = performance_tier  # 1=fastest, 3=slowest
        self.allocated_pages: Set[int] = set()
        self.access_count = 0
        self.last_access = time.time()
        
    def get_access_speed(self) -> float:
        """Get memory access speed based on tier"""
        speed_map = {1: 0.001, 2: 0.005, 3: 0.01}  # seconds
        return speed_map.get(self.performance_tier, 0.01)

class MemoryManager:
    """Comprehensive Memory Management System"""
    
    def __init__(self, total_memory: int = 1024*1024*1024, page_size: int = 4096):
        self.total_memory = total_memory
        self.page_size = page_size
        self.total_pages = total_memory // page_size
        
        # Physical memory management
        self.physical_pages: Dict[int, Page] = {}
        self.free_pages: List[int] = list(range(self.total_pages))
        self.allocated_pages: Set[int] = set()
        
        # Page tables for each process
        self.page_tables: Dict[int, PageTable] = {}
        
        # Memory pools for different types
        self.memory_pools = self._initialize_memory_pools()
        
        # Swapping and virtual memory
        self.swap_space_size = total_memory // 2  # 50% of physical memory
        self.swap_space: Dict[int, bytes] = {}  # Simulated swap space
        self.swapped_pages: Dict[int, int] = {}  # page_num -> swap_slot
        
        # Memory allocation tracking
        self.allocation_history: List[Dict] = []
        self.fragmentation_level = 0.0
        
        # Performance metrics
        self.page_faults = 0
        self.swap_ins = 0
        self.swap_outs = 0
        self.memory_accesses = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        # AI-specific constraints
        self.ai_memory_limit = total_memory * 0.6  # 60% for AI workloads
        self.blockchain_memory_limit = total_memory * 0.3  # 30% for blockchain
        self.system_memory_limit = total_memory * 0.1  # 10% for system
        
        self.start_time = time.time()
    
    def _initialize_memory_pools(self) -> Dict[str, MemoryPool]:
        """Initialize specialized memory pools"""
        pools = {}
        
        # High-performance AI model memory (pinned, fastest)
        pools['ai_models'] = MemoryPool(
            "AI Models", MemoryType.AI_MODEL, 
            self.total_memory // 4, pinned=True, performance_tier=1
        )
        
        # AI data processing memory
        pools['ai_data'] = MemoryPool(
            "AI Data", MemoryType.AI_DATA,
            self.total_memory // 3, pinned=False, performance_tier=1
        )
        
        # Blockchain ledger (medium performance, pinned)
        pools['blockchain_ledger'] = MemoryPool(
            "Blockchain Ledger", MemoryType.BLOCKCHAIN_LEDGER,
            self.total_memory // 6, pinned=True, performance_tier=2
        )
        
        # Blockchain state (swappable)
        pools['blockchain_state'] = MemoryPool(
            "Blockchain State", MemoryType.BLOCKCHAIN_STATE,
            self.total_memory // 8, pinned=False, performance_tier=2
        )
        
        # Network buffers (fast access)
        pools['network_buffers'] = MemoryPool(
            "Network Buffers", MemoryType.NETWORK_BUFFER,
            self.total_memory // 10, pinned=False, performance_tier=1
        )
        
        # System memory (pinned)
        pools['system'] = MemoryPool(
            "System", MemoryType.SYSTEM,
            self.total_memory // 20, pinned=True, performance_tier=1
        )
        
        return pools
    
    def create_page_table(self, process_id: int) -> PageTable:
        """Create page table for a process"""
        page_table = PageTable(process_id, self.page_size)
        self.page_tables[process_id] = page_table
        return page_table
    
    def allocate_memory(self, process_id: int, size: int, 
                       memory_type: MemoryType = MemoryType.USER,
                       read_only: bool = False) -> Optional[int]:
        """Allocate memory for a process"""
        pages_needed = math.ceil(size / self.page_size)
        
        # Check memory type constraints
        if not self._check_memory_constraints(memory_type, size):
            return None
        
        # Get page table
        if process_id not in self.page_tables:
            self.create_page_table(process_id)
        
        page_table = self.page_tables[process_id]
        
        # Allocate physical pages
        allocated_pages = []
        virtual_base = self._get_next_virtual_address(page_table)
        
        for i in range(pages_needed):
            physical_page = self._allocate_physical_page(process_id, memory_type)
            if physical_page is None:
                # Try swapping to make room
                if self._try_swap_out():
                    physical_page = self._allocate_physical_page(process_id, memory_type)
                
                if physical_page is None:
                    # Cleanup allocated pages and fail
                    for page_num in allocated_pages:
                        self._free_physical_page(page_num)
                    return None
            
            allocated_pages.append(physical_page)
            virtual_page = (virtual_base // self.page_size) + i
            page_table.add_mapping(virtual_page, physical_page, read_only)
        
        # Record allocation
        self._record_allocation(process_id, virtual_base, size, memory_type, allocated_pages)
        
        return virtual_base
    
    def deallocate_memory(self, process_id: int, virtual_address: int):
        """Deallocate memory for a process"""
        if process_id not in self.page_tables:
            return False
        
        page_table = self.page_tables[process_id]
        virtual_page = virtual_address // self.page_size
        
        if virtual_page not in page_table.entries:
            return False
        
        entry = page_table.entries[virtual_page]
        if entry.physical_page is not None:
            self._free_physical_page(entry.physical_page)
        
        page_table.remove_mapping(virtual_page)
        return True
    
    def access_memory(self, process_id: int, virtual_address: int, 
                     write: bool = False) -> Tuple[bool, Optional[bytes]]:
        """Access memory at virtual address"""
        self.memory_accesses += 1
        
        if process_id not in self.page_tables:
            return False, None
        
        page_table = self.page_tables[process_id]
        physical_address, success = page_table.translate_address(virtual_address)
        
        if not success:
            # Page fault - try to handle it
            return self._handle_page_fault(process_id, virtual_address, write)
        
        # Simulate memory access time based on memory type
        virtual_page = virtual_address // self.page_size
        if virtual_page in page_table.entries:
            entry = page_table.entries[virtual_page]
            if entry.physical_page in self.physical_pages:
                page = self.physical_pages[entry.physical_page]
                access_delay = self._get_memory_access_delay(page.memory_type)
                time.sleep(access_delay / 1000)  # Convert to seconds
                
                # Update access information
                page.last_access_time = time.time()
                entry.accessed = True
                
                if write and not entry.read_only:
                    entry.dirty = True
                    page.dirty = True
        
        return True, b"simulated_data"
    
    def _allocate_physical_page(self, process_id: int, 
                               memory_type: MemoryType) -> Optional[int]:
        """Allocate a physical page"""
        if not self.free_pages:
            return None
        
        page_num = self.free_pages.pop(0)
        page = Page(
            page_number=page_num,
            physical_address=page_num * self.page_size,
            state=PageState.ALLOCATED,
            process_id=process_id,
            memory_type=memory_type
        )
        
        # Set pinned status based on memory type
        if memory_type in [MemoryType.AI_MODEL, MemoryType.SYSTEM, MemoryType.BLOCKCHAIN_LEDGER]:
            page.pinned = True
            page.state = PageState.PINNED
        
        self.physical_pages[page_num] = page
        self.allocated_pages.add(page_num)
        
        return page_num
    
    def _free_physical_page(self, page_num: int):
        """Free a physical page"""
        if page_num in self.physical_pages:
            del self.physical_pages[page_num]
        if page_num in self.allocated_pages:
            self.allocated_pages.remove(page_num)
        if page_num not in self.free_pages:
            self.free_pages.append(page_num)
    
    def _handle_page_fault(self, process_id: int, virtual_address: int, 
                          write: bool) -> Tuple[bool, Optional[bytes]]:
        """Handle page fault by loading from swap or allocating new page"""
        self.page_faults += 1
        virtual_page = virtual_address // self.page_size
        
        # Check if page is in swap space
        if virtual_page in self.swapped_pages:
            return self._swap_in_page(process_id, virtual_page)
        
        # Allocate new page
        physical_page = self._allocate_physical_page(process_id, MemoryType.USER)
        if physical_page is None:
            # Try swapping out a page
            if self._try_swap_out():
                physical_page = self._allocate_physical_page(process_id, MemoryType.USER)
            
            if physical_page is None:
                return False, None  # Out of memory
        
        # Add mapping
        if process_id in self.page_tables:
            self.page_tables[process_id].add_mapping(virtual_page, physical_page)
        
        return True, b"new_page_data"
    
    def _swap_in_page(self, process_id: int, virtual_page: int) -> Tuple[bool, Optional[bytes]]:
        """Swap in a page from swap space"""
        self.swap_ins += 1
        
        # Allocate physical page
        physical_page = self._allocate_physical_page(process_id, MemoryType.USER)
        if physical_page is None:
            if self._try_swap_out():
                physical_page = self._allocate_physical_page(process_id, MemoryType.USER)
            
            if physical_page is None:
                return False, None
        
        # Load from swap space (simulated)
        swap_slot = self.swapped_pages[virtual_page]
        if swap_slot in self.swap_space:
            data = self.swap_space[swap_slot]
            del self.swap_space[swap_slot]
            del self.swapped_pages[virtual_page]
        
        # Update page table
        if process_id in self.page_tables:
            self.page_tables[process_id].add_mapping(virtual_page, physical_page)
        
        return True, b"swapped_in_data"
    
    def _try_swap_out(self) -> bool:
        """Try to swap out a page to make room"""
        # Find a good candidate for swapping (LRU algorithm)
        candidate_page = self._find_swap_candidate()
        
        if candidate_page is None:
            return False
        
        return self._swap_out_page(candidate_page)
    
    def _find_swap_candidate(self) -> Optional[int]:
        """Find best page to swap out using LRU"""
        candidates = []
        
        for page_num, page in self.physical_pages.items():
            if page.pinned or page.state == PageState.PINNED:
                continue  # Cannot swap pinned pages
            
            candidates.append((page.last_access_time, page_num))
        
        if not candidates:
            return None
        
        # Sort by last access time (LRU)
        candidates.sort()
        return candidates[0][1]
    
    def _swap_out_page(self, page_num: int) -> bool:
        """Swap out a specific page"""
        if page_num not in self.physical_pages:
            return False
        
        page = self.physical_pages[page_num]
        if page.pinned:
            return False
        
        self.swap_outs += 1
        
        # Find virtual page number
        virtual_page = None
        if page.process_id in self.page_tables:
            page_table = self.page_tables[page.process_id]
            for vp, entry in page_table.entries.items():
                if entry.physical_page == page_num:
                    virtual_page = vp
                    break
        
        if virtual_page is None:
            return False
        
        # Store in swap space (simulated)
        swap_slot = len(self.swap_space)
        self.swap_space[swap_slot] = b"swapped_page_data"
        self.swapped_pages[virtual_page] = swap_slot
        
        # Update page table entry
        if page.process_id in self.page_tables:
            page_table = self.page_tables[page.process_id]
            if virtual_page in page_table.entries:
                page_table.entries[virtual_page].present = False
                page_table.entries[virtual_page].physical_page = None
        
        # Free the physical page
        self._free_physical_page(page_num)
        
        return True
    
    def _check_memory_constraints(self, memory_type: MemoryType, size: int) -> bool:
        """Check if allocation violates memory type constraints"""
        current_usage = self._get_memory_usage_by_type(memory_type)
        
        limits = {
            MemoryType.AI_MODEL: self.ai_memory_limit * 0.4,
            MemoryType.AI_DATA: self.ai_memory_limit * 0.6,
            MemoryType.BLOCKCHAIN_LEDGER: self.blockchain_memory_limit * 0.6,
            MemoryType.BLOCKCHAIN_STATE: self.blockchain_memory_limit * 0.4,
            MemoryType.SYSTEM: self.system_memory_limit,
            MemoryType.USER: self.total_memory * 0.2,
            MemoryType.NETWORK_BUFFER: self.total_memory * 0.05,
            MemoryType.CACHE: self.total_memory * 0.1
        }
        
        limit = limits.get(memory_type, self.total_memory * 0.1)
        return (current_usage + size) <= limit
    
    def _get_memory_usage_by_type(self, memory_type: MemoryType) -> int:
        """Get current memory usage for a specific type"""
        usage = 0
        for page in self.physical_pages.values():
            if page.memory_type == memory_type:
                usage += self.page_size
        return usage
    
    def _get_memory_access_delay(self, memory_type: MemoryType) -> float:
        """Get memory access delay in milliseconds"""
        delays = {
            MemoryType.AI_MODEL: 0.1,      # Fastest access
            MemoryType.AI_DATA: 0.2,
            MemoryType.NETWORK_BUFFER: 0.3,
            MemoryType.SYSTEM: 0.5,
            MemoryType.USER: 1.0,
            MemoryType.BLOCKCHAIN_LEDGER: 1.5,
            MemoryType.BLOCKCHAIN_STATE: 2.0,
            MemoryType.CACHE: 0.15
        }
        return delays.get(memory_type, 1.0)
    
    def _get_next_virtual_address(self, page_table: PageTable) -> int:
        """Get next available virtual address"""
        if not page_table.entries:
            return 0x1000  # Start at 4KB
        
        max_page = max(page_table.entries.keys())
        return (max_page + 1) * self.page_size
    
    def _record_allocation(self, process_id: int, virtual_address: int, size: int,
                          memory_type: MemoryType, physical_pages: List[int]):
        """Record memory allocation for tracking"""
        allocation = {
            'timestamp': time.time(),
            'process_id': process_id,
            'virtual_address': virtual_address,
            'size': size,
            'memory_type': memory_type.value,
            'physical_pages': physical_pages,
            'pages_count': len(physical_pages)
        }
        self.allocation_history.append(allocation)
        
        # Keep only recent allocations
        if len(self.allocation_history) > 1000:
            self.allocation_history = self.allocation_history[-1000:]
    
    def calculate_fragmentation(self) -> float:
        """Calculate memory fragmentation level"""
        if not self.free_pages:
            return 0.0
        
        # External fragmentation - measure largest contiguous block
        free_pages_sorted = sorted(self.free_pages)
        largest_block = 1
        current_block = 1
        
        for i in range(1, len(free_pages_sorted)):
            if free_pages_sorted[i] == free_pages_sorted[i-1] + 1:
                current_block += 1
                largest_block = max(largest_block, current_block)
            else:
                current_block = 1
        
        total_free = len(self.free_pages)
        if total_free == 0:
            return 0.0
        
        fragmentation = 1.0 - (largest_block / total_free)
        self.fragmentation_level = fragmentation
        return fragmentation
    
    def defragment_memory(self) -> int:
        """Defragment memory by compacting allocated pages"""
        # This is a simplified defragmentation simulation
        old_fragmentation = self.calculate_fragmentation()
        
        # Simulate defragmentation by sorting free pages
        self.free_pages.sort()
        
        new_fragmentation = self.calculate_fragmentation()
        pages_moved = int((old_fragmentation - new_fragmentation) * 100)
        
        return max(0, pages_moved)
    
    def get_memory_statistics(self) -> Dict:
        """Get comprehensive memory statistics"""
        total_allocated = len(self.allocated_pages) * self.page_size
        total_free = len(self.free_pages) * self.page_size
        fragmentation = self.calculate_fragmentation()
        
        # Calculate usage by type
        usage_by_type = {}
        for memory_type in MemoryType:
            usage_by_type[memory_type.value] = self._get_memory_usage_by_type(memory_type)
        
        # Performance metrics
        uptime = time.time() - self.start_time
        page_fault_rate = self.page_faults / max(self.memory_accesses, 1)
        
        return {
            'total_memory': self.total_memory,
            'total_allocated': total_allocated,
            'total_free': total_free,
            'memory_usage_percent': (total_allocated / self.total_memory) * 100,
            'fragmentation_percent': fragmentation * 100,
            'page_faults': self.page_faults,
            'page_fault_rate': page_fault_rate,
            'swap_ins': self.swap_ins,
            'swap_outs': self.swap_outs,
            'memory_accesses': self.memory_accesses,
            'active_page_tables': len(self.page_tables),
            'swap_space_used': len(self.swap_space),
            'usage_by_type': usage_by_type,
            'memory_pools': {
                name: {
                    'size': pool.size,
                    'allocated_pages': len(pool.allocated_pages),
                    'access_count': pool.access_count,
                    'performance_tier': pool.performance_tier
                }
                for name, pool in self.memory_pools.items()
            },
            'uptime': uptime
        }
    
    def cleanup_process_memory(self, process_id: int):
        """Clean up all memory for a process"""
        if process_id not in self.page_tables:
            return
        
        page_table = self.page_tables[process_id]
        
        # Free all allocated pages
        for virtual_page, entry in page_table.entries.items():
            if entry.physical_page is not None:
                self._free_physical_page(entry.physical_page)
        
        # Remove page table
        del self.page_tables[process_id]
    
    def get_process_memory_info(self, process_id: int) -> Dict:
        """Get memory information for a specific process"""
        if process_id not in self.page_tables:
            return {}
        
        page_table = self.page_tables[process_id]
        total_pages = len(page_table.entries)
        present_pages = sum(1 for entry in page_table.entries.values() if entry.present)
        swapped_pages = total_pages - present_pages
        
        return {
            'process_id': process_id,
            'total_virtual_pages': total_pages,
            'present_pages': present_pages,
            'swapped_pages': swapped_pages,
            'virtual_memory_size': total_pages * self.page_size,
            'physical_memory_size': present_pages * self.page_size,
            'page_table_created': page_table.creation_time
        } 