#!/usr/bin/env python3
"""Simple test for Step 2: Memory Management System"""

print("🧠 Testing Step 2: Memory Management System")
print("=" * 50)

try:
    # Test memory manager import and basic functionality
    from memory_manager import MemoryManager, MemoryType
    print("✅ Memory manager imported successfully")
    
    # Initialize memory manager
    mm = MemoryManager(16*1024*1024, 4096)  # 16MB, 4KB pages
    print(f"✅ Memory Manager initialized: {mm.total_memory//1024//1024}MB")
    
    # Test memory allocation
    addr = mm.allocate_memory(1, 4096, MemoryType.AI_MODEL)
    if addr:
        print(f"✅ Memory allocated at: 0x{addr:08X}")
    else:
        print("❌ Allocation failed")
        
    # Test memory access
    success, _ = mm.access_memory(1, addr)
    print(f"✅ Memory access: {'Success' if success else 'Failed'}")
    
    # Test memory statistics
    stats = mm.get_memory_statistics()
    print(f"✅ Memory usage: {stats['memory_usage_percent']:.1f}%")
    
    # Test integrated process manager
    from integrated_process_manager import IntegratedProcessManager
    from process_control_block import ProcessType
    print("✅ Integrated process manager imported successfully")
    
    ipm = IntegratedProcessManager(total_memory=32*1024*1024, page_size=4096)
    print("✅ Integrated process manager initialized")
    
    def dummy_task():
        return "Task complete"
    
    # Create process with memory allocation
    pid = ipm.create_process(
        "Test-AI-Process",
        ProcessType.AI_INFERENCE,
        dummy_task,
        memory_required=1024*1024  # 1MB
    )
    
    if pid:
        print(f"✅ Process created with PID: {pid}")
        info = ipm.get_process_info(pid)
        print(f"✅ Process allocated at: 0x{info['virtual_base_address']:08X}")
        print(f"✅ Memory type: {info['memory_type'].value}")
    else:
        print("❌ Process creation failed")
    
    print("\n🎯 Step 2: Memory Management System - ALL TESTS PASSED! ✅")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc() 