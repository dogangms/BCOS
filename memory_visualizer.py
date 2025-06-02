#!/usr/bin/env python3
"""
Memory Visualization System for AI Node Operating System
Provides comprehensive visualization of memory usage, page tables, and fragmentation
"""

import time
import os
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
from collections import defaultdict
from memory_manager import MemoryManager, MemoryType, PageState

class MemoryVisualizer:
    """Advanced memory visualization system"""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        
        # Memory type colors and icons
        self.memory_type_icons = {
            MemoryType.SYSTEM: '⚙️',
            MemoryType.USER: '👤',
            MemoryType.AI_MODEL: '🧠',
            MemoryType.AI_DATA: '📊',
            MemoryType.BLOCKCHAIN_LEDGER: '⛓️',
            MemoryType.BLOCKCHAIN_STATE: '🔗',
            MemoryType.NETWORK_BUFFER: '🌐',
            MemoryType.CACHE: '💾'
        }
        
        # Page state indicators
        self.page_state_icons = {
            PageState.FREE: '⬜',
            PageState.ALLOCATED: '🟩',
            PageState.SWAPPED: '🟨',
            PageState.PINNED: '🟥',
            PageState.DIRTY: '🟧',
            PageState.SHARED: '🟦'
        }
        
        # Performance indicators
        self.performance_icons = {
            'excellent': '🟢',
            'good': '🟡',
            'poor': '🟠',
            'critical': '🔴'
        }
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_memory_header(self):
        """Display memory system header"""
        stats = self.memory_manager.get_memory_statistics()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("═" * 100)
        print("🧠 DECENTRALIZED AI NODE OPERATING SYSTEM - MEMORY MANAGEMENT 🧠")
        print("═" * 100)
        
        # System information
        total_mb = stats['total_memory'] // (1024 * 1024)
        allocated_mb = stats['total_allocated'] // (1024 * 1024)
        free_mb = stats['total_free'] // (1024 * 1024)
        
        print(f"📅 Time: {current_time}")
        print(f"💾 Total Memory: {total_mb} MB | Allocated: {allocated_mb} MB | Free: {free_mb} MB")
        print(f"📊 Usage: {stats['memory_usage_percent']:.1f}% | Fragmentation: {stats['fragmentation_percent']:.1f}%")
        print(f"📄 Page Faults: {stats['page_faults']} | Swap I/O: {stats['swap_ins']}↓ {stats['swap_outs']}↑")
        print(f"🔢 Active Page Tables: {stats['active_page_tables']} | Uptime: {stats['uptime']:.1f}s")
        print("═" * 100)
    
    def display_memory_map(self, scale: int = 64):
        """Display visual memory map"""
        print("🗺️  PHYSICAL MEMORY MAP")
        print("-" * 80)
        
        total_pages = self.memory_manager.total_pages
        pages_per_line = scale
        lines = (total_pages + pages_per_line - 1) // pages_per_line
        
        # Create memory map
        memory_map = []
        for i in range(total_pages):
            if i in self.memory_manager.physical_pages:
                page = self.memory_manager.physical_pages[i]
                icon = self.memory_type_icons.get(page.memory_type, '❓')
                state_icon = self.page_state_icons.get(page.state, '❓')
                memory_map.append(f"{icon}")
            else:
                memory_map.append("⬜")  # Free page
        
        # Display memory map
        for line in range(min(lines, 20)):  # Limit to 20 lines for readability
            start_idx = line * pages_per_line
            end_idx = min(start_idx + pages_per_line, total_pages)
            
            # Address range
            start_addr = start_idx * self.memory_manager.page_size
            end_addr = (end_idx - 1) * self.memory_manager.page_size
            
            print(f"0x{start_addr:08X} │{''.join(memory_map[start_idx:end_idx]):<{pages_per_line}}│ 0x{end_addr:08X}")
        
        if lines > 20:
            print(f"... ({lines - 20} more lines) ...")
        
        # Legend
        print("\nLegend:")
        print("⬜ Free   🧠 AI Model   📊 AI Data   ⛓️ Blockchain   🌐 Network   ⚙️ System   👤 User   💾 Cache")
        print()
    
    def display_memory_pools(self):
        """Display memory pool information"""
        print("🏊 MEMORY POOLS STATUS")
        print("-" * 80)
        
        stats = self.memory_manager.get_memory_statistics()
        pools = stats['memory_pools']
        
        print(f"{'Pool Name':<20} {'Type':<12} {'Size':<10} {'Used':<10} {'Usage%':<8} {'Tier':<6} {'Status'}")
        print("-" * 80)
        
        for pool_name, pool_data in pools.items():
            pool = self.memory_manager.memory_pools[pool_name]
            size_mb = pool_data['size'] // (1024 * 1024)
            used_pages = pool_data['allocated_pages']
            used_mb = used_pages * self.memory_manager.page_size // (1024 * 1024)
            
            usage_percent = (used_pages * self.memory_manager.page_size / pool_data['size']) * 100 if pool_data['size'] > 0 else 0
            
            # Status indicator
            if usage_percent < 50:
                status = self.performance_icons['excellent']
            elif usage_percent < 75:
                status = self.performance_icons['good']
            elif usage_percent < 90:
                status = self.performance_icons['poor']
            else:
                status = self.performance_icons['critical']
            
            type_icon = self.memory_type_icons.get(pool.memory_type, '❓')
            
            print(f"{pool_name:<20} {type_icon}{pool.memory_type.value:<11} {size_mb:<10} {used_mb:<10} "
                  f"{usage_percent:<8.1f} Tier{pool_data['performance_tier']:<5} {status}")
        
        print()
    
    def display_page_table_info(self, process_id: int = None):
        """Display page table information"""
        print("📋 PAGE TABLES INFORMATION")
        print("-" * 80)
        
        if process_id is not None:
            # Show specific process page table
            if process_id in self.memory_manager.page_tables:
                self._display_single_page_table(process_id)
            else:
                print(f"No page table found for process {process_id}")
        else:
            # Show summary of all page tables
            print(f"{'PID':<6} {'Virtual Pages':<15} {'Present':<10} {'Swapped':<10} {'Memory Size':<12} {'Created'}")
            print("-" * 80)
            
            for pid in sorted(self.memory_manager.page_tables.keys()):
                info = self.memory_manager.get_process_memory_info(pid)
                if info:
                    created_time = datetime.fromtimestamp(info['page_table_created']).strftime("%H:%M:%S")
                    memory_size_kb = info['physical_memory_size'] // 1024
                    
                    print(f"{pid:<6} {info['total_virtual_pages']:<15} {info['present_pages']:<10} "
                          f"{info['swapped_pages']:<10} {memory_size_kb:<12} {created_time}")
        
        print()
    
    def _display_single_page_table(self, process_id: int):
        """Display detailed page table for a specific process"""
        page_table = self.memory_manager.page_tables[process_id]
        
        print(f"Page Table for Process {process_id}:")
        print(f"{'Virtual Page':<15} {'Physical Page':<15} {'Present':<10} {'R/W':<6} {'Dirty':<8} {'Accessed'}")
        print("-" * 70)
        
        for virtual_page in sorted(page_table.entries.keys())[:20]:  # Show first 20 entries
            entry = page_table.entries[virtual_page]
            physical_page = entry.physical_page if entry.physical_page is not None else "None"
            present = "Yes" if entry.present else "No"
            rw = "R/O" if entry.read_only else "R/W"
            dirty = "Yes" if entry.dirty else "No"
            accessed = "Yes" if entry.accessed else "No"
            
            print(f"{virtual_page:<15} {physical_page:<15} {present:<10} {rw:<6} {dirty:<8} {accessed}")
        
        if len(page_table.entries) > 20:
            print(f"... ({len(page_table.entries) - 20} more entries)")
        print()
    
    def display_fragmentation_analysis(self):
        """Display memory fragmentation analysis"""
        print("🧩 MEMORY FRAGMENTATION ANALYSIS")
        print("-" * 80)
        
        fragmentation = self.memory_manager.calculate_fragmentation()
        free_pages = sorted(self.memory_manager.free_pages)
        
        # Analyze fragmentation
        if not free_pages:
            print("No free pages available - memory fully allocated")
            return
        
        # Find contiguous blocks
        blocks = []
        current_block = [free_pages[0]]
        
        for i in range(1, len(free_pages)):
            if free_pages[i] == free_pages[i-1] + 1:
                current_block.append(free_pages[i])
            else:
                blocks.append(current_block)
                current_block = [free_pages[i]]
        blocks.append(current_block)
        
        # Sort blocks by size
        blocks.sort(key=len, reverse=True)
        
        print(f"Overall Fragmentation Level: {fragmentation * 100:.1f}%")
        print(f"Total Free Pages: {len(free_pages)}")
        print(f"Number of Free Blocks: {len(blocks)}")
        
        if fragmentation > 0.7:
            print("🔴 CRITICAL: High fragmentation - consider defragmentation")
        elif fragmentation > 0.5:
            print("🟠 WARNING: Moderate fragmentation detected")
        elif fragmentation > 0.2:
            print("🟡 NOTICE: Some fragmentation present")
        else:
            print("🟢 GOOD: Low fragmentation level")
        
        # Show largest blocks
        print("\nLargest Free Blocks:")
        print(f"{'Block Size':<12} {'Start Page':<12} {'Size (KB)':<12} {'Start Address'}")
        print("-" * 60)
        
        for i, block in enumerate(blocks[:10]):  # Show top 10 blocks
            size_pages = len(block)
            start_page = block[0]
            size_kb = size_pages * self.memory_manager.page_size // 1024
            start_addr = start_page * self.memory_manager.page_size
            
            print(f"{size_pages:<12} {start_page:<12} {size_kb:<12} 0x{start_addr:08X}")
        
        print()
    
    def display_swap_space_info(self):
        """Display swap space information"""
        print("💿 SWAP SPACE INFORMATION")
        print("-" * 80)
        
        stats = self.memory_manager.get_memory_statistics()
        swap_used = stats['swap_space_used']
        swap_size_mb = self.memory_manager.swap_space_size // (1024 * 1024)
        swap_used_mb = swap_used * self.memory_manager.page_size // (1024 * 1024)
        swap_usage_percent = (swap_used_mb / swap_size_mb) * 100 if swap_size_mb > 0 else 0
        
        print(f"Swap Size: {swap_size_mb} MB")
        print(f"Swap Used: {swap_used_mb} MB ({swap_usage_percent:.1f}%)")
        print(f"Swap Operations: {stats['swap_ins']} swap-ins, {stats['swap_outs']} swap-outs")
        
        # Swap usage bar
        bar_length = 50
        used_length = int(swap_usage_percent / 100 * bar_length)
        free_length = bar_length - used_length
        
        print(f"Usage: [{'█' * used_length}{'░' * free_length}] {swap_usage_percent:.1f}%")
        
        if swap_usage_percent > 80:
            print("🔴 WARNING: High swap usage - consider adding more RAM")
        elif swap_usage_percent > 50:
            print("🟡 NOTICE: Moderate swap usage")
        else:
            print("🟢 GOOD: Low swap usage")
        
        print()
    
    def display_memory_performance(self):
        """Display memory performance metrics"""
        print("⚡ MEMORY PERFORMANCE METRICS")
        print("-" * 80)
        
        stats = self.memory_manager.get_memory_statistics()
        
        # Calculate performance indicators
        page_fault_rate = stats['page_fault_rate'] * 100
        memory_efficiency = 100 - stats['fragmentation_percent']
        
        # Performance ratings
        def get_performance_rating(value, thresholds):
            if value >= thresholds[0]:
                return self.performance_icons['excellent']
            elif value >= thresholds[1]:
                return self.performance_icons['good']
            elif value >= thresholds[2]:
                return self.performance_icons['poor']
            else:
                return self.performance_icons['critical']
        
        memory_rating = get_performance_rating(memory_efficiency, [90, 75, 50])
        fault_rating = get_performance_rating(100 - page_fault_rate, [95, 85, 70])
        
        print(f"Memory Accesses: {stats['memory_accesses']:,}")
        print(f"Page Faults: {stats['page_faults']:,} ({page_fault_rate:.2f}%) {fault_rating}")
        print(f"Memory Efficiency: {memory_efficiency:.1f}% {memory_rating}")
        print(f"Average Access Time: {self._calculate_avg_access_time():.2f} ms")
        
        # Performance over time (simulated)
        print("\nPerformance Trend (last 10 samples):")
        self._display_performance_graph()
        
        print()
    
    def _calculate_avg_access_time(self) -> float:
        """Calculate average memory access time"""
        total_time = 0.0
        total_pages = 0
        
        for page in self.memory_manager.physical_pages.values():
            access_time = self.memory_manager._get_memory_access_delay(page.memory_type)
            total_time += access_time
            total_pages += 1
        
        return total_time / max(total_pages, 1)
    
    def _display_performance_graph(self):
        """Display ASCII performance graph"""
        # Simulate performance data
        samples = 10
        data = [85 + i * 2 - (i % 3) * 5 for i in range(samples)]
        
        max_val = max(data)
        min_val = min(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        height = 5
        for row in range(height - 1, -1, -1):
            line = f"{min_val + (range_val * row / (height - 1)):5.1f} │"
            for value in data:
                normalized = (value - min_val) / range_val
                if normalized >= (row / (height - 1)):
                    line += "█"
                else:
                    line += " "
            line += "│"
            print(line)
        
        print(f"{'':>5} └{'─' * len(data)}┘")
        print(f"{'':>7}{' '.join(str(i) for i in range(len(data)))}")
    
    def display_ai_memory_constraints(self):
        """Display AI/Blockchain specific memory constraints"""
        print("🤖 AI/BLOCKCHAIN MEMORY CONSTRAINTS")
        print("-" * 80)
        
        # Calculate current usage by type
        usage_by_type = {}
        for memory_type in MemoryType:
            usage_by_type[memory_type] = self.memory_manager._get_memory_usage_by_type(memory_type)
        
        # Define limits
        limits = {
            'AI Total': self.memory_manager.ai_memory_limit,
            'Blockchain Total': self.memory_manager.blockchain_memory_limit,
            'System Total': self.memory_manager.system_memory_limit
        }
        
        # Calculate totals
        ai_total = usage_by_type[MemoryType.AI_MODEL] + usage_by_type[MemoryType.AI_DATA]
        blockchain_total = usage_by_type[MemoryType.BLOCKCHAIN_LEDGER] + usage_by_type[MemoryType.BLOCKCHAIN_STATE]
        system_total = usage_by_type[MemoryType.SYSTEM]
        
        current_usage = {
            'AI Total': ai_total,
            'Blockchain Total': blockchain_total,
            'System Total': system_total
        }
        
        print(f"{'Constraint':<20} {'Used (MB)':<12} {'Limit (MB)':<12} {'Usage%':<10} {'Status'}")
        print("-" * 70)
        
        for constraint, limit in limits.items():
            used = current_usage[constraint]
            used_mb = used // (1024 * 1024)
            limit_mb = limit // (1024 * 1024)
            usage_percent = (used / limit) * 100 if limit > 0 else 0
            
            if usage_percent < 70:
                status = self.performance_icons['excellent']
            elif usage_percent < 85:
                status = self.performance_icons['good']
            elif usage_percent < 95:
                status = self.performance_icons['poor']
            else:
                status = self.performance_icons['critical']
            
            print(f"{constraint:<20} {used_mb:<12} {limit_mb:<12} {usage_percent:<10.1f} {status}")
        
        # Individual memory types
        print("\nDetailed Memory Type Usage:")
        print(f"{'Type':<20} {'Icon':<5} {'Used (MB)':<12} {'Percentage'}")
        print("-" * 50)
        
        for memory_type, usage in usage_by_type.items():
            icon = self.memory_type_icons.get(memory_type, '❓')
            used_mb = usage // (1024 * 1024)
            percentage = (usage / self.memory_manager.total_memory) * 100
            
            print(f"{memory_type.value:<20} {icon:<5} {used_mb:<12} {percentage:.1f}%")
        
        print()
    
    def display_full_memory_dashboard(self):
        """Display complete memory management dashboard"""
        self.clear_screen()
        self.display_memory_header()
        self.display_memory_pools()
        self.display_memory_map(scale=64)
        self.display_fragmentation_analysis()
        self.display_swap_space_info()
        self.display_memory_performance()
        self.display_ai_memory_constraints()
        
        print("═" * 100)
        print("Memory Management Commands: allocate | deallocate | defrag | page_table <pid> | export")
        print("═" * 100)
    
    def export_memory_state(self, filename: str = None):
        """Export memory state to JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"memory_state_{timestamp}.json"
        
        # Gather comprehensive memory state
        memory_state = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.memory_manager.get_memory_statistics(),
            'page_tables': {
                pid: self.memory_manager.get_process_memory_info(pid)
                for pid in self.memory_manager.page_tables.keys()
            },
            'physical_pages': {
                page_num: {
                    'physical_address': page.physical_address,
                    'state': page.state.value,
                    'process_id': page.process_id,
                    'memory_type': page.memory_type.value,
                    'last_access_time': page.last_access_time,
                    'dirty': page.dirty,
                    'pinned': page.pinned
                }
                for page_num, page in self.memory_manager.physical_pages.items()
            },
            'memory_pools': {
                name: {
                    'memory_type': pool.memory_type.value,
                    'size': pool.size,
                    'pinned': pool.pinned,
                    'performance_tier': pool.performance_tier,
                    'allocated_pages': list(pool.allocated_pages),
                    'access_count': pool.access_count
                }
                for name, pool in self.memory_manager.memory_pools.items()
            },
            'allocation_history': self.memory_manager.allocation_history[-100:],  # Last 100 allocations
            'fragmentation_level': self.memory_manager.fragmentation_level,
            'free_pages': self.memory_manager.free_pages[:100],  # First 100 free pages
            'swap_space': {
                'size': self.memory_manager.swap_space_size,
                'used_slots': len(self.memory_manager.swap_space),
                'swapped_pages_count': len(self.memory_manager.swapped_pages)
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(memory_state, f, indent=2, default=str)
        
        print(f"📁 Memory state exported to {filename}")
        size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"   File size: {size_mb:.2f} MB")
    
    def real_time_memory_monitor(self, refresh_interval: float = 2.0):
        """Start real-time memory monitoring"""
        try:
            while True:
                self.display_full_memory_dashboard()
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            print("\n👋 Memory monitoring stopped by user") 