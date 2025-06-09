#!/usr/bin/env python3
"""
Comprehensive Demo: File Operations (Create, Read, Write, Delete)
Demonstrates all four core file operations in our file system
"""

from file_system import VirtualFileSystem, FileType, AccessLevel

def main():
    print("🚀 File Operations Demo - CREATE, READ, WRITE, DELETE")
    print("=" * 60)
    
    # Create file system
    fs = VirtualFileSystem(total_blocks=50, block_size=1024)
    
    # Make sure we have the test directory
    try:
        fs.create_directory('/test_files')
    except FileExistsError:
        pass
    
    print("\n📁 Initial directory structure:")
    for entry in fs.list_directory('/'):
        icon = '📁' if entry.is_directory else '📄'
        print(f"  {icon} {entry.name}")
    
    # ================================
    # 1. FILE CREATION
    # ================================
    print("\n" + "="*50)
    print("🆕 1. FILE CREATION OPERATIONS")
    print("="*50)
    
    # Create different types of files
    files_to_create = [
        ('/test_files/readme.txt', b'This is a readme file with important information.', FileType.REGULAR),
        ('/test_files/ai_model.pkl', b'Binary AI model data here...', FileType.AI_MODEL),
        ('/test_files/smart_contract.sol', b'pragma solidity ^0.8.0;\ncontract Token {}', FileType.SMART_CONTRACT),
        ('/test_files/blockchain_data.dat', b'Genesis block data and transaction history', FileType.BLOCKCHAIN_DATA),
    ]
    
    for file_path, content, file_type in files_to_create:
        try:
            file_id = fs.create_file(file_path, content, file_type)
            print(f"✅ Created: {file_path} (ID: {file_id[:8]}...) - {file_type.value}")
        except Exception as e:
            print(f"❌ Failed to create {file_path}: {e}")
    
    # Show files in test directory
    print(f"\n📂 Files in /test_files directory:")
    for entry in fs.list_directory('/test_files'):
        print(f"  📄 {entry.name} ({entry.size} bytes)")
    
    # ================================
    # 2. FILE READING
    # ================================
    print("\n" + "="*50)
    print("📖 2. FILE READING OPERATIONS")
    print("="*50)
    
    # Read each file
    for file_path, _, _ in files_to_create:
        try:
            content = fs.read_file(file_path)
            print(f"📄 Reading {file_path}:")
            # Show first 50 characters for readability
            preview = content.decode('utf-8', errors='ignore')[:50]
            if len(content) > 50:
                preview += "..."
            print(f"   Content: \"{preview}\"")
            print(f"   Size: {len(content)} bytes")
            
            # Show file metadata
            metadata = fs.get_file_info(file_path)
            print(f"   Type: {metadata.file_type.value}")
            print(f"   Owner: {metadata.owner}")
            if metadata.ai_accuracy:
                print(f"   AI Accuracy: {metadata.ai_accuracy}")
            if metadata.blockchain_hash:
                print(f"   Blockchain Hash: {metadata.blockchain_hash[:16]}...")
            print()
            
        except Exception as e:
            print(f"❌ Failed to read {file_path}: {e}")
    
    # ================================
    # 3. FILE WRITING/UPDATING
    # ================================
    print("="*50)
    print("✏️ 3. FILE WRITING/UPDATING OPERATIONS")
    print("="*50)
    
    # Update readme file
    try:
        new_content = b'This is an UPDATED readme file with MORE important information!\nVersion 2.0 with additional details.'
        success = fs.write_file('/test_files/readme.txt', new_content)
        if success:
            print("✅ Updated readme.txt with new content")
            # Read and show updated content
            updated_content = fs.read_file('/test_files/readme.txt')
            print(f"   New content: \"{updated_content.decode()[:60]}...\"")
            print(f"   New size: {len(updated_content)} bytes")
        else:
            print("❌ Failed to update readme.txt")
    except Exception as e:
        print(f"❌ Error updating readme.txt: {e}")
    
    # Append to a file
    try:
        append_text = b'\n\nAppended section: This text was added later.'
        success = fs.write_file('/test_files/readme.txt', append_text, append=True)
        if success:
            print("✅ Appended text to readme.txt")
            # Show final content
            final_content = fs.read_file('/test_files/readme.txt')
            print(f"   Final size: {len(final_content)} bytes")
        else:
            print("❌ Failed to append to readme.txt")
    except Exception as e:
        print(f"❌ Error appending to readme.txt: {e}")
    
    # Create a new file with write operation
    try:
        file_id = fs.create_file('/test_files/log.txt', b'Initial log entry')
        print("✅ Created new log.txt file")
        
        # Write multiple log entries
        log_entries = [
            b'Log entry 1: System started',
            b'Log entry 2: AI model loaded',  
            b'Log entry 3: Blockchain sync complete',
            b'Log entry 4: All systems operational'
        ]
        
        for i, entry in enumerate(log_entries):
            if i == 0:
                fs.write_file('/test_files/log.txt', entry)
            else:
                fs.write_file('/test_files/log.txt', b'\n' + entry, append=True)
        
        print("✅ Added multiple log entries")
        final_log = fs.read_file('/test_files/log.txt')
        print(f"   Final log content:\n{final_log.decode()}")
        
    except Exception as e:
        print(f"❌ Error with log operations: {e}")
    
    # ================================
    # 4. FILE DELETION
    # ================================
    print("\n" + "="*50)
    print("🗑️ 4. FILE DELETION OPERATIONS")
    print("="*50)
    
    # Show files before deletion
    print("📂 Files before deletion:")
    for entry in fs.list_directory('/test_files'):
        print(f"  📄 {entry.name} ({entry.size} bytes)")
    
    # Delete some files
    files_to_delete = ['/test_files/log.txt', '/test_files/smart_contract.sol']
    
    for file_path in files_to_delete:
        try:
            success = fs.delete_file(file_path)
            if success:
                print(f"✅ Deleted: {file_path}")
            else:
                print(f"❌ Failed to delete: {file_path}")
        except Exception as e:
            print(f"❌ Error deleting {file_path}: {e}")
    
    # Show files after deletion
    print("\n📂 Files after deletion:")
    remaining_files = fs.list_directory('/test_files')
    if remaining_files:
        for entry in remaining_files:
            print(f"  📄 {entry.name} ({entry.size} bytes)")
    else:
        print("  (No files remaining)")
    
    # ================================
    # 5. FILE SYSTEM STATISTICS
    # ================================
    print("\n" + "="*50)
    print("📊 FILE SYSTEM FINAL STATISTICS")
    print("="*50)
    
    stats = fs.get_file_system_stats()
    print(f"📊 Total Files: {stats['total_files']}")
    print(f"📁 Total Directories: {stats['total_directories']}")
    print(f"💾 Storage Used: {stats['storage_utilization']:.1f}%")
    print(f"📖 Read Operations: {stats['read_operations']}")
    print(f"✏️ Write Operations: {stats['write_operations']}")
    print(f"⚡ Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
    print(f"⏱️ Average I/O Time: {stats['avg_io_time']*1000:.2f}ms")
    
    print("\n🎉 All file operations completed successfully!")
    print("✅ CREATE ✅ READ ✅ WRITE ✅ DELETE - All implemented!")

if __name__ == "__main__":
    main() 