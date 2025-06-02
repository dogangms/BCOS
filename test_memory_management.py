#!/usr/bin/env python3
"""
Comprehensive tests for Memory Management System
Tests paging, address translation, swapping, fragmentation, and AI-specific features
"""

import unittest
import time
from memory_manager import MemoryManager, MemoryType, PageState
from memory_visualizer import MemoryVisualizer
from integrated_process_manager import IntegratedProcessManager
from process_control_block import ProcessType
from schedulers import RoundRobinScheduler

class TestMemoryManager(unittest.TestCase):
    """Test cases for MemoryManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.memory_manager = MemoryManager(total_memory=16*1024*1024, page_size=4096)  # 16MB for testing
    
    def test_memory_initialization(self):
        """Test memory manager initialization"""
        self.assertEqual(self.memory_manager.total_memory, 16*1024*1024)
        self.assertEqual(self.memory_manager.page_size, 4096)
        self.assertEqual(self.memory_manager.total_pages, 4096)
        self.assertEqual(len(self.memory_manager.free_pages), 4096)
    
    def test_page_table_creation(self):
        """Test page table creation and management"""
        process_id = 100
        page_table = self.memory_manager.create_page_table(process_id)
        
        self.assertIsNotNone(page_table)
        self.assertEqual(page_table.process_id, process_id)
        self.assertEqual(page_table.page_size, 4096)
        self.assertIn(process_id, self.memory_manager.page_tables)
    
    def test_basic_memory_allocation(self):
        """Test basic memory allocation"""
        process_id = 101
        size = 8192  # 2 pages
        
        virtual_addr = self.memory_manager.allocate_memory(process_id, size, MemoryType.USER)
        
        self.assertIsNotNone(virtual_addr)
        self.assertIn(process_id, self.memory_manager.page_tables)
        
        # Check that pages were allocated
        page_table = self.memory_manager.page_tables[process_id]
        self.assertTrue(len(page_table.entries) >= 2)  # At least 2 pages
    
    def test_address_translation(self):
        """Test virtual to physical address translation"""
        process_id = 102
        size = 4096  # 1 page
        
        virtual_addr = self.memory_manager.allocate_memory(process_id, size, MemoryType.USER)
        self.assertIsNotNone(virtual_addr)
        
        # Test address translation
        page_table = self.memory_manager.page_tables[process_id]
        physical_addr, success = page_table.translate_address(virtual_addr)
        
        self.assertTrue(success)
        self.assertIsNotNone(physical_addr)
    
    def test_memory_access(self):
        """Test memory access operations"""
        process_id = 103
        size = 4096
        
        virtual_addr = self.memory_manager.allocate_memory(process_id, size, MemoryType.USER)
        self.assertIsNotNone(virtual_addr)
        
        # Test read access
        success, data = self.memory_manager.access_memory(process_id, virtual_addr, write=False)
        self.assertTrue(success)
        
        # Test write access
        success, data = self.memory_manager.access_memory(process_id, virtual_addr, write=True)
        self.assertTrue(success)
        
        # Verify memory access counter
        self.assertGreater(self.memory_manager.memory_accesses, 0)
    
    def test_memory_type_constraints(self):
        """Test AI/Blockchain memory type constraints"""
        process_id = 104
        
        # Test AI model allocation (should succeed within limits)
        ai_model_addr = self.memory_manager.allocate_memory(
            process_id, 1024*1024, MemoryType.AI_MODEL
        )
        self.assertIsNotNone(ai_model_addr)
        
        # Test blockchain allocation
        blockchain_addr = self.memory_manager.allocate_memory(
            process_id + 1, 512*1024, MemoryType.BLOCKCHAIN_LEDGER
        )
        self.assertIsNotNone(blockchain_addr)
        
        # Test very large allocation (should fail due to constraints)
        large_addr = self.memory_manager.allocate_memory(
            process_id + 2, 15*1024*1024, MemoryType.AI_MODEL  # Too large
        )
        self.assertIsNone(large_addr)
    
    def test_swapping_mechanism(self):
        """Test memory swapping functionality"""
        # Fill up memory to trigger swapping
        allocations = []
        for i in range(20):
            process_id = 200 + i
            size = 512 * 1024  # 512KB each
            
            virtual_addr = self.memory_manager.allocate_memory(process_id, size, MemoryType.USER)
            if virtual_addr is not None:
                allocations.append((process_id, virtual_addr))
        
        # Should have some successful allocations
        self.assertGreater(len(allocations), 0)
        
        # Access some old allocations to trigger swap-ins
        if allocations:
            old_process, old_addr = allocations[0]
            success, _ = self.memory_manager.access_memory(old_process, old_addr)
            # Should succeed even if page was swapped
            self.assertTrue(success)
    
    def test_fragmentation_calculation(self):
        """Test memory fragmentation calculation"""
        # Initially no fragmentation
        initial_frag = self.memory_manager.calculate_fragmentation()
        self.assertEqual(initial_frag, 0.0)
        
        # Allocate and deallocate to create fragmentation
        process_ids = []
        for i in range(10):
            process_id = 300 + i
            size = 4096  # 1 page each
            virtual_addr = self.memory_manager.allocate_memory(process_id, size, MemoryType.USER)
            if virtual_addr is not None:
                process_ids.append(process_id)
        
        # Deallocate every other process
        for i, pid in enumerate(process_ids):
            if i % 2 == 0:
                self.memory_manager.cleanup_process_memory(pid)
        
        # Should have some fragmentation now
        fragmentation = self.memory_manager.calculate_fragmentation()
        self.assertGreater(fragmentation, 0.0)
    
    def test_defragmentation(self):
        """Test memory defragmentation"""
        # Create fragmentation first
        process_ids = []
        for i in range(20):
            process_id = 400 + i
            size = 4096
            virtual_addr = self.memory_manager.allocate_memory(process_id, size, MemoryType.USER)
            if virtual_addr is not None:
                process_ids.append(process_id)
        
        # Deallocate random processes
        for i, pid in enumerate(process_ids):
            if i % 3 == 0:
                self.memory_manager.cleanup_process_memory(pid)
        
        # Measure fragmentation before defrag
        frag_before = self.memory_manager.calculate_fragmentation()
        
        # Perform defragmentation
        pages_moved = self.memory_manager.defragment_memory()
        
        # Should have moved some pages (or at least attempted to)
        self.assertGreaterEqual(pages_moved, 0)
        
        # Fragmentation should be same or better
        frag_after = self.memory_manager.calculate_fragmentation()
        self.assertLessEqual(frag_after, frag_before)
    
    def test_memory_cleanup(self):
        """Test process memory cleanup"""
        process_id = 500
        size = 8192
        
        virtual_addr = self.memory_manager.allocate_memory(process_id, size, MemoryType.USER)
        self.assertIsNotNone(virtual_addr)
        
        # Verify allocation exists
        self.assertIn(process_id, self.memory_manager.page_tables)
        
        # Cleanup process memory
        self.memory_manager.cleanup_process_memory(process_id)
        
        # Verify cleanup
        self.assertNotIn(process_id, self.memory_manager.page_tables)

class TestMemoryVisualizer(unittest.TestCase):
    """Test cases for MemoryVisualizer"""
    
    def setUp(self):
        """Set up test environment"""
        self.memory_manager = MemoryManager(total_memory=8*1024*1024, page_size=4096)
        self.visualizer = MemoryVisualizer(self.memory_manager)
    
    def test_visualizer_initialization(self):
        """Test visualizer initialization"""
        self.assertIsNotNone(self.visualizer.memory_manager)
        self.assertEqual(len(self.visualizer.memory_type_icons), 8)
        self.assertEqual(len(self.visualizer.page_state_icons), 6)
    
    def test_memory_statistics_export(self):
        """Test memory statistics and export"""
        # Create some memory activity
        process_id = 600
        self.memory_manager.allocate_memory(process_id, 4096, MemoryType.AI_MODEL)
        
        # Test statistics
        stats = self.memory_manager.get_memory_statistics()
        self.assertIn('total_memory', stats)
        self.assertIn('memory_usage_percent', stats)
        self.assertIn('page_faults', stats)
        
        # Test export (just verify it doesn't crash)
        try:
            self.visualizer.export_memory_state("test_memory_export.json")
            import os
            self.assertTrue(os.path.exists("test_memory_export.json"))
            os.remove("test_memory_export.json")  # Cleanup
        except Exception as e:
            self.fail(f"Memory export failed: {e}")

class TestIntegratedProcessManager(unittest.TestCase):
    """Test cases for IntegratedProcessManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.manager = IntegratedProcessManager(
            scheduler=RoundRobinScheduler(time_quantum=100),
            total_memory=32*1024*1024,  # 32MB for testing
            page_size=4096
        )
    
    def test_integrated_manager_initialization(self):
        """Test integrated manager initialization"""
        self.assertIsNotNone(self.manager.memory_manager)
        self.assertIsNotNone(self.manager.memory_visualizer)
        self.assertIsNotNone(self.manager.scheduler)
    
    def test_process_creation_with_memory(self):
        """Test process creation with memory allocation"""
        def dummy_ai_task():
            time.sleep(0.1)
            return "AI task complete"
        
        pid = self.manager.create_process(
            name="AI-Test-Process",
            process_type=ProcessType.AI_INFERENCE,
            target_function=dummy_ai_task,
            memory_required=1024*1024  # 1MB
        )
        
        self.assertIsNotNone(pid)
        
        # Verify process exists
        process_info = self.manager.get_process_info(pid)
        self.assertIsNotNone(process_info)
        self.assertEqual(process_info['name'], "AI-Test-Process")
        self.assertEqual(process_info['process_type'], ProcessType.AI_INFERENCE.value)
        self.assertIsNotNone(process_info['virtual_base_address'])
    
    def test_memory_type_mapping(self):
        """Test automatic memory type mapping for process types"""
        def dummy_task():
            return "complete"
        
        # Test AI inference -> AI_MODEL memory
        ai_pid = self.manager.create_process(
            "AI-Process", ProcessType.AI_INFERENCE, dummy_task, memory_required=512*1024
        )
        ai_info = self.manager.get_process_info(ai_pid)
        self.assertEqual(ai_info['memory_type'], MemoryType.AI_MODEL)
        
        # Test blockchain validator -> BLOCKCHAIN_LEDGER memory
        bc_pid = self.manager.create_process(
            "BC-Process", ProcessType.BLOCKCHAIN_VALIDATOR, dummy_task, memory_required=512*1024
        )
        bc_info = self.manager.get_process_info(bc_pid)
        self.assertEqual(bc_info['memory_type'], MemoryType.BLOCKCHAIN_LEDGER)
    
    def test_additional_memory_allocation(self):
        """Test additional memory allocation for existing processes"""
        def dummy_task():
            time.sleep(0.2)
            return "complete"
        
        pid = self.manager.create_process(
            "Test-Process", ProcessType.USER, dummy_task, memory_required=512*1024
        )
        
        initial_info = self.manager.get_process_info(pid)
        initial_memory = initial_info['allocated_memory']
        
        # Allocate additional memory
        additional_addr = self.manager.allocate_additional_memory(pid, 256*1024)
        self.assertIsNotNone(additional_addr)
        
        # Verify increased memory allocation
        updated_info = self.manager.get_process_info(pid)
        self.assertGreater(updated_info['allocated_memory'], initial_memory)
    
    def test_memory_access_through_manager(self):
        """Test memory access through the integrated manager"""
        def dummy_task():
            return "complete"
        
        pid = self.manager.create_process(
            "Access-Test", ProcessType.USER, dummy_task, memory_required=4096
        )
        
        process_info = self.manager.get_process_info(pid)
        virtual_addr = process_info['virtual_base_address']
        
        # Test memory access
        success = self.manager.access_process_memory(pid, virtual_addr, write=False)
        self.assertTrue(success)
        
        success = self.manager.access_process_memory(pid, virtual_addr, write=True)
        self.assertTrue(success)
    
    def test_process_termination_and_cleanup(self):
        """Test process termination with memory cleanup"""
        def dummy_task():
            time.sleep(0.1)
            return "complete"
        
        pid = self.manager.create_process(
            "Cleanup-Test", ProcessType.USER, dummy_task, memory_required=1024*1024
        )
        
        # Verify process and memory exist
        self.assertIsNotNone(self.manager.get_process_info(pid))
        self.assertIn(pid, self.manager.memory_manager.page_tables)
        
        # Terminate process
        success = self.manager.terminate_process(pid, force=True)
        self.assertTrue(success)
        
        # Allow time for cleanup
        time.sleep(0.1)
        
        # Verify cleanup - process and memory should be gone
        self.assertIsNone(self.manager.get_process_info(pid))
        self.assertNotIn(pid, self.manager.memory_manager.page_tables)
    
    def test_system_info_integration(self):
        """Test integrated system information"""
        system_info = self.manager.get_system_info()
        
        self.assertIn('node_id', system_info)
        self.assertIn('scheduler', system_info)
        self.assertIn('memory_statistics', system_info)
        
        memory_stats = system_info['memory_statistics']
        self.assertIn('total_memory', memory_stats)
        self.assertIn('page_faults', memory_stats)

class TestMemoryDemonstration(unittest.TestCase):
    """Test cases for memory demonstration functionality"""
    
    def test_memory_demo_initialization(self):
        """Test memory demo can be initialized"""
        from memory_demo import MemoryDemo
        
        demo = MemoryDemo(memory_size=16*1024*1024)
        self.assertIsNotNone(demo.memory_manager)
        self.assertIsNotNone(demo.visualizer)
        self.assertEqual(demo.memory_manager.total_memory, 16*1024*1024)

def run_performance_test():
    """Run performance test for memory operations"""
    print("\n🚀 Running Memory Management Performance Test...")
    
    memory_manager = MemoryManager(total_memory=128*1024*1024, page_size=4096)
    
    # Test allocation performance
    start_time = time.time()
    allocations = []
    
    for i in range(100):
        virtual_addr = memory_manager.allocate_memory(
            i, 64*1024, MemoryType.USER  # 64KB each
        )
        if virtual_addr is not None:
            allocations.append((i, virtual_addr))
    
    allocation_time = time.time() - start_time
    
    # Test access performance
    start_time = time.time()
    access_count = 0
    
    for pid, addr in allocations[:50]:  # Test first 50
        success, _ = memory_manager.access_memory(pid, addr)
        if success:
            access_count += 1
    
    access_time = time.time() - start_time
    
    # Test cleanup performance
    start_time = time.time()
    
    for pid, _ in allocations:
        memory_manager.cleanup_process_memory(pid)
    
    cleanup_time = time.time() - start_time
    
    # Report results
    print(f"✅ Performance Test Results:")
    print(f"   Allocations: {len(allocations)} in {allocation_time:.3f}s ({len(allocations)/allocation_time:.1f} ops/sec)")
    print(f"   Memory Access: {access_count} in {access_time:.3f}s ({access_count/access_time:.1f} ops/sec)")
    print(f"   Cleanup: {len(allocations)} in {cleanup_time:.3f}s ({len(allocations)/cleanup_time:.1f} ops/sec)")
    print(f"   Memory Statistics: {memory_manager.get_memory_statistics()}")

def main():
    """Run all memory management tests"""
    print("🧠 Memory Management System - Comprehensive Tests")
    print("=" * 60)
    
    # Run unit tests
    print("\n📋 Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance test
    run_performance_test()
    
    print("\n🎯 All tests completed!")

if __name__ == "__main__":
    main() 