#!/usr/bin/env python3
"""
Memory Management Demo for Decentralized AI Node Operating System
Demonstrates paging, address translation, swapping, and AI-specific features
"""

import time
import random
import threading
from typing import List, Dict
from memory_manager import MemoryManager, MemoryType, PageState
from memory_visualizer import MemoryVisualizer

class MemoryDemo:
    """Comprehensive memory management demonstration"""
    
    def __init__(self, memory_size: int = 64 * 1024 * 1024):  # 64MB for demo
        self.memory_manager = MemoryManager(memory_size, page_size=4096)
        self.visualizer = MemoryVisualizer(self.memory_manager)
        self.active_processes: List[int] = []
        
    def demo_basic_paging(self):
        """Demonstrate basic paging and address translation"""
        print("🔥 DEMO: Basic Paging and Address Translation")
        print("=" * 60)
        
        # Create a process and allocate memory
        process_id = 1001
        
        # Allocate memory for different purposes
        allocations = [
            (8192, MemoryType.AI_MODEL, "AI Model Storage"),
            (16384, MemoryType.AI_DATA, "Training Data"),
            (4096, MemoryType.USER, "User Buffer"),
            (12288, MemoryType.NETWORK_BUFFER, "Network Buffer")
        ]
        
        allocated_addresses = []
        
        for size, mem_type, description in allocations:
            print(f"\n📥 Allocating {size} bytes for {description}")
            virtual_addr = self.memory_manager.allocate_memory(process_id, size, mem_type)
            
            if virtual_addr is not None:
                allocated_addresses.append((virtual_addr, size, description))
                print(f"   ✅ Allocated at virtual address: 0x{virtual_addr:08X}")
                
                # Demonstrate address translation
                test_offset = size // 2  # Middle of allocation
                test_virtual = virtual_addr + test_offset
                success, data = self.memory_manager.access_memory(process_id, test_virtual)
                
                if success:
                    print(f"   🔍 Address translation test: 0x{test_virtual:08X} -> SUCCESS")
                else:
                    print(f"   ❌ Address translation failed for: 0x{test_virtual:08X}")
            else:
                print(f"   ❌ Allocation failed!")
        
        # Show page table information
        print(f"\n📋 Page Table for Process {process_id}:")
        self.visualizer.display_page_table_info(process_id)
        
        self.active_processes.append(process_id)
        input("\nPress Enter to continue...")
    
    def demo_memory_types_and_constraints(self):
        """Demonstrate AI/Blockchain memory types and constraints"""
        print("\n🤖 DEMO: AI/Blockchain Memory Types and Constraints")
        print("=" * 60)
        
        # Test memory constraints by allocating large amounts
        test_allocations = [
            (MemoryType.AI_MODEL, 20 * 1024 * 1024, "Large AI Model"),
            (MemoryType.AI_DATA, 30 * 1024 * 1024, "Training Dataset"),
            (MemoryType.BLOCKCHAIN_LEDGER, 10 * 1024 * 1024, "Blockchain Ledger"),
            (MemoryType.BLOCKCHAIN_STATE, 8 * 1024 * 1024, "Smart Contract State"),
            (MemoryType.NETWORK_BUFFER, 2 * 1024 * 1024, "P2P Network Buffer")
        ]
        
        process_id = 2001
        
        for mem_type, size, description in test_allocations:
            print(f"\n📊 Testing {description} ({size // (1024 * 1024)} MB)")
            virtual_addr = self.memory_manager.allocate_memory(process_id, size, mem_type)
            
            if virtual_addr is not None:
                print(f"   ✅ Allocation successful: 0x{virtual_addr:08X}")
            else:
                print(f"   ❌ Allocation failed - memory constraint violated!")
                print(f"       This demonstrates the {mem_type.value} memory limit enforcement")
        
        # Show memory constraints status
        self.visualizer.display_ai_memory_constraints()
        
        self.active_processes.append(process_id)
        input("\nPress Enter to continue...")
    
    def demo_swapping_and_virtual_memory(self):
        """Demonstrate memory swapping and virtual memory"""
        print("\n💿 DEMO: Memory Swapping and Virtual Memory")
        print("=" * 60)
        
        # Fill up memory to trigger swapping
        process_id = 3001
        allocation_size = 1024 * 1024  # 1MB per allocation
        
        print("🔄 Allocating memory until swapping is triggered...")
        
        allocations = []
        for i in range(30):  # Try to allocate 30MB
            virtual_addr = self.memory_manager.allocate_memory(
                process_id + i, allocation_size, MemoryType.USER
            )
            
            if virtual_addr is not None:
                allocations.append((process_id + i, virtual_addr))
                print(f"   Allocation {i+1}: ✅ Virtual address: 0x{virtual_addr:08X}")
                
                # Access some allocations to create access patterns
                if i % 3 == 0:  # Access every 3rd allocation
                    self.memory_manager.access_memory(process_id + i, virtual_addr)
                    
            else:
                print(f"   Allocation {i+1}: ❌ Failed")
                break
            
            # Show swap status every 5 allocations
            if (i + 1) % 5 == 0:
                stats = self.memory_manager.get_memory_statistics()
                print(f"   📊 Page faults: {stats['page_faults']}, Swaps: {stats['swap_outs']}↑ {stats['swap_ins']}↓")
        
        # Show swap space information
        print("\n💿 Current Swap Space Status:")
        self.visualizer.display_swap_space_info()
        
        # Demonstrate page fault by accessing swapped pages
        print("\n🔍 Testing page fault handling by accessing old allocations...")
        for pid, addr in allocations[:5]:  # Access first 5 allocations
            print(f"   Accessing process {pid} at 0x{addr:08X}...")
            success, _ = self.memory_manager.access_memory(pid, addr)
            if success:
                print(f"   ✅ Access successful (may have triggered swap-in)")
            else:
                print(f"   ❌ Access failed")
        
        final_stats = self.memory_manager.get_memory_statistics()
        print(f"\n📈 Final statistics:")
        print(f"   Total page faults: {final_stats['page_faults']}")
        print(f"   Swap operations: {final_stats['swap_outs']} out, {final_stats['swap_ins']} in")
        
        self.active_processes.extend([pid for pid, _ in allocations])
        input("\nPress Enter to continue...")
    
    def demo_fragmentation_and_defragmentation(self):
        """Demonstrate memory fragmentation and defragmentation"""
        print("\n🧩 DEMO: Memory Fragmentation and Defragmentation")
        print("=" * 60)
        
        # Create fragmentation by allocating and deallocating randomly
        print("🔀 Creating memory fragmentation...")
        
        process_id = 4001
        allocations = []
        
        # Allocate multiple small blocks
        for i in range(20):
            size = random.randint(4096, 16384)  # Random size between 4KB and 16KB
            virtual_addr = self.memory_manager.allocate_memory(process_id + i, size, MemoryType.USER)
            if virtual_addr is not None:
                allocations.append((process_id + i, virtual_addr))
        
        print(f"   ✅ Created {len(allocations)} allocations")
        
        # Deallocate random blocks to create holes
        deallocate_count = len(allocations) // 3
        to_deallocate = random.sample(allocations, deallocate_count)
        
        for pid, addr in to_deallocate:
            self.memory_manager.cleanup_process_memory(pid)
            allocations.remove((pid, addr))
        
        print(f"   🗑️ Deallocated {deallocate_count} random blocks")
        
        # Show fragmentation before defragmentation
        print("\n📊 Fragmentation Analysis (Before Defragmentation):")
        self.visualizer.display_fragmentation_analysis()
        
        # Perform defragmentation
        print("🔧 Performing memory defragmentation...")
        pages_moved = self.memory_manager.defragment_memory()
        print(f"   ✅ Defragmentation complete: {pages_moved} pages reorganized")
        
        # Show fragmentation after defragmentation
        print("\n📊 Fragmentation Analysis (After Defragmentation):")
        self.visualizer.display_fragmentation_analysis()
        
        self.active_processes.extend([pid for pid, _ in allocations])
        input("\nPress Enter to continue...")
    
    def demo_memory_pools(self):
        """Demonstrate specialized memory pools"""
        print("\n🏊 DEMO: Specialized Memory Pools")
        print("=" * 60)
        
        # Test different memory pools with realistic AI/Blockchain workloads
        workloads = [
            ("AI Model Loading", MemoryType.AI_MODEL, 5 * 1024 * 1024, 5001),
            ("Training Data", MemoryType.AI_DATA, 10 * 1024 * 1024, 5002),
            ("Blockchain Ledger", MemoryType.BLOCKCHAIN_LEDGER, 3 * 1024 * 1024, 5003),
            ("Smart Contract State", MemoryType.BLOCKCHAIN_STATE, 2 * 1024 * 1024, 5004),
            ("Network Buffers", MemoryType.NETWORK_BUFFER, 1 * 1024 * 1024, 5005),
            ("Cache Data", MemoryType.CACHE, 4 * 1024 * 1024, 5006)
        ]
        
        for name, mem_type, size, pid in workloads:
            print(f"\n🚀 Starting {name} workload ({size // (1024 * 1024)} MB)")
            
            # Allocate memory
            virtual_addr = self.memory_manager.allocate_memory(pid, size, mem_type)
            
            if virtual_addr is not None:
                print(f"   ✅ Memory allocated at: 0x{virtual_addr:08X}")
                
                # Simulate memory access patterns
                access_count = 10
                for i in range(access_count):
                    offset = random.randint(0, size - 1)
                    success, _ = self.memory_manager.access_memory(pid, virtual_addr + offset)
                    if not success:
                        print(f"   ⚠️ Access failed at offset {offset}")
                
                # Show access timing based on memory type
                access_delay = self.memory_manager._get_memory_access_delay(mem_type)
                print(f"   ⏱️ Access time: {access_delay:.2f} ms (Tier based)")
                
            else:
                print(f"   ❌ Allocation failed!")
        
        # Show memory pools status
        print("\n🏊 Current Memory Pools Status:")
        self.visualizer.display_memory_pools()
        
        self.active_processes.extend([pid for _, _, _, pid in workloads])
        input("\nPress Enter to continue...")
    
    def demo_performance_analysis(self):
        """Demonstrate memory performance analysis"""
        print("\n⚡ DEMO: Memory Performance Analysis")
        print("=" * 60)
        
        # Generate some memory activity for performance analysis
        print("🏃 Generating memory activity for performance analysis...")
        
        # Simulate realistic memory access patterns
        processes = []
        for i in range(5):
            pid = 6000 + i
            size = random.randint(1024 * 1024, 4 * 1024 * 1024)  # 1-4 MB
            mem_type = random.choice(list(MemoryType))
            
            virtual_addr = self.memory_manager.allocate_memory(pid, size, mem_type)
            if virtual_addr is not None:
                processes.append((pid, virtual_addr, size))
        
        # Simulate heavy memory access
        access_count = 100
        for _ in range(access_count):
            if processes:
                pid, addr, size = random.choice(processes)
                offset = random.randint(0, size - 1)
                self.memory_manager.access_memory(pid, addr + offset, write=random.choice([True, False]))
        
        print(f"   ✅ Completed {access_count} memory accesses")
        
        # Show comprehensive performance analysis
        print("\n📊 Memory Performance Analysis:")
        self.visualizer.display_memory_performance()
        
        self.active_processes.extend([pid for pid, _, _ in processes])
        input("\nPress Enter to continue...")
    
    def demo_interactive_memory_management(self):
        """Interactive memory management demo"""
        print("\n🎮 DEMO: Interactive Memory Management")
        print("=" * 60)
        
        while True:
            print("\nAvailable Commands:")
            print("1. allocate <size> <type> - Allocate memory")
            print("2. deallocate <pid> - Deallocate process memory")
            print("3. access <pid> <offset> - Access memory")
            print("4. dashboard - Show full memory dashboard")
            print("5. fragmentation - Show fragmentation analysis")
            print("6. defrag - Perform defragmentation")
            print("7. export - Export memory state")
            print("8. monitor - Start real-time monitoring")
            print("9. quit - Exit interactive demo")
            
            command = input("\nEnter command: ").strip().lower()
            
            if command.startswith('allocate'):
                self._handle_allocate_command(command)
            elif command.startswith('deallocate'):
                self._handle_deallocate_command(command)
            elif command.startswith('access'):
                self._handle_access_command(command)
            elif command == 'dashboard':
                self.visualizer.display_full_memory_dashboard()
            elif command == 'fragmentation':
                self.visualizer.display_fragmentation_analysis()
            elif command == 'defrag':
                pages_moved = self.memory_manager.defragment_memory()
                print(f"✅ Defragmentation complete: {pages_moved} pages moved")
            elif command == 'export':
                self.visualizer.export_memory_state()
            elif command == 'monitor':
                print("Starting real-time monitoring (Ctrl+C to stop)...")
                self.visualizer.real_time_memory_monitor()
            elif command == 'quit':
                break
            else:
                print("❌ Invalid command")
    
    def _handle_allocate_command(self, command: str):
        """Handle allocate command"""
        try:
            parts = command.split()
            if len(parts) < 3:
                print("Usage: allocate <size> <type>")
                return
            
            size = int(parts[1])
            mem_type_str = parts[2].upper()
            
            # Convert string to MemoryType
            mem_type = None
            for mt in MemoryType:
                if mt.value.upper() == mem_type_str:
                    mem_type = mt
                    break
            
            if mem_type is None:
                print(f"Invalid memory type. Available: {[mt.value for mt in MemoryType]}")
                return
            
            pid = random.randint(7000, 7999)
            virtual_addr = self.memory_manager.allocate_memory(pid, size, mem_type)
            
            if virtual_addr is not None:
                print(f"✅ Allocated {size} bytes for process {pid} at 0x{virtual_addr:08X}")
                self.active_processes.append(pid)
            else:
                print("❌ Allocation failed!")
                
        except ValueError:
            print("❌ Invalid size value")
    
    def _handle_deallocate_command(self, command: str):
        """Handle deallocate command"""
        try:
            parts = command.split()
            if len(parts) < 2:
                print("Usage: deallocate <pid>")
                return
            
            pid = int(parts[1])
            self.memory_manager.cleanup_process_memory(pid)
            
            if pid in self.active_processes:
                self.active_processes.remove(pid)
            
            print(f"✅ Deallocated memory for process {pid}")
            
        except ValueError:
            print("❌ Invalid PID value")
    
    def _handle_access_command(self, command: str):
        """Handle access command"""
        try:
            parts = command.split()
            if len(parts) < 3:
                print("Usage: access <pid> <offset>")
                return
            
            pid = int(parts[1])
            offset = int(parts[2])
            
            if pid in self.memory_manager.page_tables:
                # Find first virtual address for this process
                page_table = self.memory_manager.page_tables[pid]
                if page_table.entries:
                    first_virtual = min(page_table.entries.keys()) * self.memory_manager.page_size
                    virtual_addr = first_virtual + offset
                    
                    success, data = self.memory_manager.access_memory(pid, virtual_addr)
                    
                    if success:
                        print(f"✅ Memory access successful at 0x{virtual_addr:08X}")
                    else:
                        print(f"❌ Memory access failed at 0x{virtual_addr:08X}")
                else:
                    print(f"❌ No memory allocated for process {pid}")
            else:
                print(f"❌ Process {pid} not found")
                
        except ValueError:
            print("❌ Invalid PID or offset value")
    
    def run_all_demos(self):
        """Run all memory management demos"""
        demos = [
            ("Basic Paging and Address Translation", self.demo_basic_paging),
            ("Memory Types and Constraints", self.demo_memory_types_and_constraints),
            ("Swapping and Virtual Memory", self.demo_swapping_and_virtual_memory),
            ("Fragmentation and Defragmentation", self.demo_fragmentation_and_defragmentation),
            ("Specialized Memory Pools", self.demo_memory_pools),
            ("Performance Analysis", self.demo_performance_analysis)
        ]
        
        print("🚀 DECENTRALIZED AI NODE OS - MEMORY MANAGEMENT DEMOS")
        print("=" * 70)
        print("This demo will showcase all memory management features:")
        for i, (name, _) in enumerate(demos, 1):
            print(f"  {i}. {name}")
        print("  7. Interactive Memory Management")
        print("=" * 70)
        
        choice = input("\nSelect demo (1-7, or 'all' for all demos): ").strip().lower()
        
        if choice == 'all':
            for name, demo_func in demos:
                print(f"\n🎯 Starting: {name}")
                demo_func()
        elif choice.isdigit() and 1 <= int(choice) <= 6:
            demo_index = int(choice) - 1
            name, demo_func = demos[demo_index]
            print(f"\n🎯 Starting: {name}")
            demo_func()
        elif choice == '7':
            self.demo_interactive_memory_management()
        else:
            print("❌ Invalid selection")
            return
        
        # Final memory dashboard
        print("\n🎊 DEMO COMPLETE - Final Memory State")
        print("=" * 50)
        self.visualizer.display_full_memory_dashboard()
        
        # Cleanup
        print("\n🧹 Cleaning up demo processes...")
        for pid in self.active_processes:
            self.memory_manager.cleanup_process_memory(pid)
        print("✅ Cleanup complete")

def main():
    """Main demo function"""
    print("🧠 Memory Management System Demo")
    print("Initializing memory manager...")
    
    # Create demo with smaller memory size for better visualization
    demo = MemoryDemo(memory_size=64 * 1024 * 1024)  # 64MB
    
    print("✅ Memory manager initialized")
    print(f"   Total memory: {demo.memory_manager.total_memory // (1024 * 1024)} MB")
    print(f"   Page size: {demo.memory_manager.page_size} bytes")
    print(f"   Total pages: {demo.memory_manager.total_pages}")
    
    try:
        demo.run_all_demos()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    print("\n🎯 Thank you for exploring the Memory Management System!")

if __name__ == "__main__":
    main() 