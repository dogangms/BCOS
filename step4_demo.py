"""
Decentralized AI Node Operating System - Step 4: File System Demo
Comprehensive demonstration of file system capabilities including encryption and visualization.
"""

import threading
import time
import random
import json
import os
from typing import List, Dict

from file_system import VirtualFileSystem, FileType, AccessLevel
from file_encryption import FileEncryption, EncryptionLevel
from file_system_visualizer import FileSystemVisualizer, InteractiveFileSystemMonitor, FileSystemEvent

class Step4Demo:
    """
    Comprehensive demo for Step 4: File System Implementation
    Showcases all features with interactive modes and real-time monitoring
    """
    
    def __init__(self):
        # Initialize file system (16MB total, 4KB blocks)
        self.file_system = VirtualFileSystem(total_blocks=4096, block_size=4096)
        self.encryption = FileEncryption()
        self.visualizer = FileSystemVisualizer(self.file_system, self.encryption)
        self.interactive_monitor = InteractiveFileSystemMonitor(self.visualizer)
        
        # Demo state
        self.demo_files = []
        self.demo_users = ["alice", "bob", "charlie", "admin"]
        
    def run_comprehensive_demo(self):
        """Run the complete Step 4 demonstration"""
        print("🚀 " + "STEP 4: FILE SYSTEM IMPLEMENTATION DEMO".center(80, "═"))
        print()
        
        while True:
            print("📋 DEMO MENU:")
            print("  [1] Basic File Operations")
            print("  [2] Directory Management")
            print("  [3] File Types & AI/Blockchain Features")
            print("  [4] Encryption & Security")
            print("  [5] File Search & Indexing")
            print("  [6] Cache Performance Demo")
            print("  [7] Real-time File System Monitor")
            print("  [8] Multi-user File Sharing Simulation")
            print("  [9] Comprehensive File System Test")
            print("  [0] Exit")
            print()
            
            choice = input("🎯 Select demo option: ").strip()
            
            if choice == '1':
                self.demo_basic_file_operations()
            elif choice == '2':
                self.demo_directory_management()
            elif choice == '3':
                self.demo_ai_blockchain_features()
            elif choice == '4':
                self.demo_encryption_security()
            elif choice == '5':
                self.demo_file_search()
            elif choice == '6':
                self.demo_cache_performance()
            elif choice == '7':
                self.demo_file_system_monitor()
            elif choice == '8':
                self.demo_multi_user_simulation()
            elif choice == '9':
                self.demo_comprehensive_test()
            elif choice == '0':
                print("👋 Exiting Step 4 demo...")
                break
            else:
                print("❌ Invalid choice, please try again.")
                
            print("\n" + "─" * 80 + "\n")
            
    def demo_basic_file_operations(self):
        """Demonstrate basic file system operations"""
        print("📄 BASIC FILE OPERATIONS DEMONSTRATION")
        print("═" * 60)
        
        # Create files
        print("🔄 Creating files...")
        
        # Text file
        content1 = b"Hello, Decentralized AI Node OS! This is a sample text file."
        file_id1 = self.file_system.create_file(
            "/users/sample.txt",
            content1,
            FileType.REGULAR,
            "alice",
            AccessLevel.USER
        )
        print(f"✅ Created text file: {file_id1[:8]}")
        self._log_event("create", "/users/sample.txt", "alice", len(content1))
        
        # Binary file
        content2 = b"\x89PNG\r\n\x1a\n" + b"fake image data" * 100
        file_id2 = self.file_system.create_file(
            "/users/image.png",
            content2,
            FileType.REGULAR,
            "alice"
        )
        print(f"✅ Created image file: {file_id2[:8]}")
        self._log_event("create", "/users/image.png", "alice", len(content2))
        
        # Read files
        print("\n📖 Reading files...")
        read_content1 = self.file_system.read_file("/users/sample.txt", AccessLevel.USER)
        print(f"📄 Text file content: {read_content1.decode()[:50]}...")
        self._log_event("read", "/users/sample.txt", "alice", len(read_content1))
        
        read_content2 = self.file_system.read_file("/users/image.png", AccessLevel.USER)
        print(f"🖼️ Image file size: {len(read_content2)} bytes")
        self._log_event("read", "/users/image.png", "alice", len(read_content2))
        
        # Write to files
        print("\n✏️ Writing to files...")
        append_content = b"\nAppended content from demo."
        self.file_system.write_file("/users/sample.txt", append_content, AccessLevel.USER, append=True)
        print("✅ Appended content to text file")
        self._log_event("write", "/users/sample.txt", "alice", len(append_content))
        
        # Read updated content
        updated_content = self.file_system.read_file("/users/sample.txt", AccessLevel.USER)
        print(f"📄 Updated content: {updated_content.decode()}")
        
        # File information
        print("\n📊 File information:")
        file_info1 = self.file_system.get_file_info("/users/sample.txt")
        print(f"📄 {file_info1.name}: {file_info1.size} bytes, {file_info1.file_type.value}")
        print(f"   Created: {time.ctime(file_info1.created_time)}")
        print(f"   Modified: {time.ctime(file_info1.modified_time)}")
        
        # Delete a file
        print("\n🗑️ Deleting file...")
        self.file_system.delete_file("/users/image.png", AccessLevel.USER)
        print("✅ Deleted image file")
        self._log_event("delete", "/users/image.png", "alice", 0)
        
        # Verify deletion
        try:
            self.file_system.read_file("/users/image.png")
            print("❌ File should have been deleted!")
        except FileNotFoundError:
            print("✅ File successfully deleted")
            
    def demo_directory_management(self):
        """Demonstrate directory operations"""
        print("📁 DIRECTORY MANAGEMENT DEMONSTRATION")
        print("═" * 60)
        
        # Create directories
        print("🔄 Creating directory structure...")
        directories = [
            "/projects",
            "/projects/ai_research",
            "/projects/blockchain_dev",
            "/projects/ai_research/models",
            "/projects/ai_research/datasets",
            "/projects/blockchain_dev/contracts",
            "/projects/blockchain_dev/testing"
        ]
        
        for directory in directories:
            try:
                self.file_system.create_directory(directory, AccessLevel.USER)
                print(f"✅ Created: {directory}")
            except FileExistsError:
                print(f"ℹ️ Already exists: {directory}")
                
        # Create files in directories
        print("\n📄 Creating files in directories...")
        project_files = [
            ("/projects/ai_research/README.md", b"# AI Research Project\nThis directory contains AI research files.", FileType.REGULAR),
            ("/projects/ai_research/models/gpt_model.bin", b"fake model data" * 1000, FileType.AI_MODEL),
            ("/projects/ai_research/datasets/training_data.csv", b"id,data,label\n1,sample1,positive\n2,sample2,negative", FileType.AI_DATASET),
            ("/projects/blockchain_dev/whitepaper.pdf", b"fake PDF content for blockchain whitepaper", FileType.REGULAR),
            ("/projects/blockchain_dev/contracts/token.sol", b"contract Token { mapping(address => uint) balances; }", FileType.SMART_CONTRACT)
        ]
        
        for file_path, content, file_type in project_files:
            file_id = self.file_system.create_file(file_path, content, file_type, "alice", AccessLevel.USER)
            print(f"✅ Created {file_type.value}: {os.path.basename(file_path)}")
            self._log_event("create", file_path, "alice", len(content))
            
        # List directory contents
        print("\n📋 Directory listings:")
        for directory in ["/projects", "/projects/ai_research", "/projects/blockchain_dev"]:
            print(f"\n📁 {directory}:")
            try:
                entries = self.file_system.list_directory(directory)
                for entry in entries:
                    icon = "📁" if entry.is_directory else self._get_file_icon(entry.name)
                    size_info = f"({len(self.file_system.list_directory(f'{directory}/{entry.name}'))} items)" if entry.is_directory else f"({entry.size} bytes)"
                    print(f"  {icon} {entry.name} {size_info}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
                
    def demo_ai_blockchain_features(self):
        """Demonstrate AI and blockchain specific features"""
        print("🧠 AI & BLOCKCHAIN FILE FEATURES DEMONSTRATION")
        print("═" * 60)
        
        # Create AI model files
        print("🤖 Creating AI model files...")
        ai_models = [
            ("neural_network_v1.model", b"neural network weights and biases" * 200),
            ("transformer_model.bin", b"transformer architecture data" * 300),
            ("decision_tree.pkl", b"serialized decision tree model" * 100)
        ]
        
        for model_name, model_data in ai_models:
            file_id = self.file_system.create_file(
                f"/ai_models/{model_name}",
                model_data,
                FileType.AI_MODEL,
                "ai_engineer",
                AccessLevel.AI_ENGINEER
            )
            
            # Get model metadata
            model_info = self.file_system.get_file_info(f"/ai_models/{model_name}")
            print(f"🧠 {model_name}:")
            print(f"   Size: {model_info.size} bytes")
            print(f"   Version: {model_info.model_version}")
            print(f"   Accuracy: {model_info.ai_accuracy:.1%}")
            print(f"   Pinned in memory: {model_info.pin_in_memory}")
            
            self._log_event("create", f"/ai_models/{model_name}", "ai_engineer", len(model_data))
            
        # Create blockchain data files
        print("\n⛓️ Creating blockchain data files...")
        blockchain_data = [
            ("genesis_block.dat", b'{"index":0,"timestamp":1640995200,"transactions":[],"hash":"genesis"}'),
            ("block_001.dat", b'{"index":1,"prev_hash":"genesis","transactions":[{"from":"A","to":"B","amount":10}]}'),
            ("ledger.db", b"blockchain ledger database content" * 500)
        ]
        
        for data_name, data_content in blockchain_data:
            file_id = self.file_system.create_file(
                f"/blockchain/{data_name}",
                data_content,
                FileType.BLOCKCHAIN_DATA,
                "blockchain_dev",
                AccessLevel.BLOCKCHAIN_DEV
            )
            
            # Get blockchain metadata
            data_info = self.file_system.get_file_info(f"/blockchain/{data_name}")
            print(f"⛓️ {data_name}:")
            print(f"   Size: {data_info.size} bytes")
            print(f"   Hash: {data_info.blockchain_hash[:16]}...")
            print(f"   Pinned in memory: {data_info.pin_in_memory}")
            
            self._log_event("create", f"/blockchain/{data_name}", "blockchain_dev", len(data_content))
            
        # Create smart contracts
        print("\n📜 Creating smart contract files...")
        contracts = [
            ("ERC20Token.sol", b'pragma solidity ^0.8.0;\ncontract ERC20Token {\n  mapping(address => uint256) balances;\n}'),
            ("NFTContract.sol", b'pragma solidity ^0.8.0;\ncontract NFT {\n  mapping(uint256 => address) tokenOwner;\n}'),
            ("DeFiProtocol.sol", b'pragma solidity ^0.8.0;\ncontract DeFi {\n  function stake() external payable {}\n}')
        ]
        
        for contract_name, contract_code in contracts:
            file_id = self.file_system.create_file(
                f"/smart_contracts/{contract_name}",
                contract_code,
                FileType.SMART_CONTRACT,
                "blockchain_dev",
                AccessLevel.BLOCKCHAIN_DEV
            )
            
            contract_info = self.file_system.get_file_info(f"/smart_contracts/{contract_name}")
            print(f"📜 {contract_name}:")
            print(f"   Size: {contract_info.size} bytes")
            print(f"   Version: {contract_info.smart_contract_version}")
            
            self._log_event("create", f"/smart_contracts/{contract_name}", "blockchain_dev", len(contract_code))
            
        # Display file system statistics
        print("\n📊 File System Statistics:")
        stats = self.file_system.get_file_system_stats()
        print(f"📁 Total files: {stats['total_files']}")
        print(f"📂 Total directories: {stats['total_directories']}")
        print(f"💾 Storage utilization: {stats['storage_utilization']:.1f}%")
        print(f"🧠 AI models: {len([f for f in self.file_system.files.values() if f.file_type == FileType.AI_MODEL])}")
        print(f"⛓️ Blockchain files: {len([f for f in self.file_system.files.values() if f.file_type == FileType.BLOCKCHAIN_DATA])}")
        print(f"📜 Smart contracts: {len([f for f in self.file_system.files.values() if f.file_type == FileType.SMART_CONTRACT])}")
        
    def demo_encryption_security(self):
        """Demonstrate encryption and security features"""
        print("🔒 ENCRYPTION & SECURITY DEMONSTRATION")
        print("═" * 60)
        
        # Create files with different encryption levels
        print("🔐 Creating encrypted files...")
        
        sensitive_files = [
            ("confidential_report.txt", b"This is highly confidential information about our AI research.", EncryptionLevel.BASIC),
            ("financial_data.json", b'{"revenue": 1000000, "expenses": 800000, "profit": 200000}', EncryptionLevel.ADVANCED),
            ("military_ai_model.bin", b"top secret military AI model data" * 100, EncryptionLevel.MILITARY),
            ("public_info.txt", b"This is public information that doesn't need encryption.", EncryptionLevel.NONE)
        ]
        
        for filename, content, encryption_level in sensitive_files:
            # Create file
            file_id = self.file_system.create_file(
                f"/secure/{filename}",
                content,
                FileType.ENCRYPTED if encryption_level != EncryptionLevel.NONE else FileType.REGULAR,
                "admin",
                AccessLevel.ADMIN
            )
            
            # Generate encryption key
            if encryption_level != EncryptionLevel.NONE:
                key_id = self.encryption.generate_file_key(file_id, "admin", encryption_level)
                
                # Encrypt the content
                encrypted_content = self.encryption.encrypt_file_content(file_id, content, "admin")
                
                # Update file with encrypted content
                self.file_system.write_file(f"/secure/{filename}", encrypted_content, AccessLevel.ADMIN)
                
                print(f"🔒 {filename}: {encryption_level.value} (Key: {key_id[:12]}...)")
            else:
                print(f"📄 {filename}: No encryption")
                
            self._log_event("create", f"/secure/{filename}", "admin", len(content))
            
        # Test access control
        print("\n🛡️ Testing access control...")
        
        # Set access rules for a file
        test_file_id = list(self.file_system.files.keys())[0]
        self.encryption.set_file_access_rules(
            test_file_id,
            allowed_users=["admin", "alice"],
            time_restrictions=(9, 17),  # 9 AM to 5 PM
            max_accesses=10
        )
        print("✅ Set access rules: only admin and alice, 9 AM-5 PM, max 10 accesses")
        
        # Test encryption/decryption
        print("\n🔄 Testing encryption/decryption...")
        
        for filename, original_content, encryption_level in sensitive_files[:2]:  # Test first 2 files
            file_path = f"/secure/{filename}"
            
            try:
                # Read encrypted content
                encrypted_data = self.file_system.read_file(file_path, AccessLevel.ADMIN)
                
                if encryption_level != EncryptionLevel.NONE:
                    # Decrypt content
                    file_id = self.file_system.path_to_file_id[file_path]
                    decrypted_data = self.encryption.decrypt_file_content(file_id, encrypted_data, "admin")
                    
                    print(f"🔓 {filename}: Decryption successful")
                    print(f"   Original: {original_content[:30].decode()}...")
                    print(f"   Decrypted: {decrypted_data[:30].decode()}...")
                    print(f"   Match: {'✅' if original_content == decrypted_data else '❌'}")
                else:
                    print(f"📄 {filename}: No decryption needed")
                    
                self._log_event("read", file_path, "admin", len(encrypted_data))
                
            except Exception as e:
                print(f"❌ Error with {filename}: {e}")
                
        # Security statistics
        print("\n📊 Security Statistics:")
        security_stats = self.encryption.get_security_statistics()
        print(f"🔑 Encryption keys: {security_stats['total_encryption_keys']}")
        print(f"🔒 Encrypted files: {security_stats['encrypted_files']}")
        print(f"✅ Success rate: {security_stats['success_rate']:.1f}%")
        print(f"🚫 Blocked users: {security_stats['blocked_users']}")
        
        # Show recent security events
        print("\n🚨 Recent Security Events:")
        audit_log = self.encryption.get_audit_log(limit=5)
        for event in audit_log:
            status = "✅" if event.success else "❌"
            time_str = time.strftime('%H:%M:%S', time.localtime(event.timestamp))
            print(f"  {status} {time_str} - {event.event_type.value} by {event.user_id}")
            
    def demo_file_search(self):
        """Demonstrate file search and indexing"""
        print("🔍 FILE SEARCH & INDEXING DEMONSTRATION")
        print("═" * 60)
        
        # Create searchable files
        print("📝 Creating searchable content...")
        
        search_files = [
            ("research_paper.txt", b"Machine learning algorithms for blockchain consensus mechanisms in decentralized networks."),
            ("meeting_notes.md", b"# Meeting Notes\nDiscussed AI model deployment on blockchain infrastructure."),
            ("code_review.py", b"# Python code for neural network implementation\ndef train_model(data):\n    pass"),
            ("project_plan.doc", b"Project timeline for AI-powered smart contract development and testing."),
            ("technical_spec.pdf", b"Technical specifications for distributed artificial intelligence systems.")
        ]
        
        for filename, content in search_files:
            file_id = self.file_system.create_file(
                f"/documents/{filename}",
                content,
                FileType.REGULAR,
                "alice",
                AccessLevel.USER
            )
            print(f"📄 Created: {filename}")
            self._log_event("create", f"/documents/{filename}", "alice", len(content))
            
        # Perform searches
        print("\n🔍 Performing searches...")
        
        search_queries = [
            "machine learning",
            "blockchain",
            "neural network",
            "smart contract",
            "artificial intelligence",
            "python"
        ]
        
        for query in search_queries:
            results = self.file_system.search_files(query)
            print(f"\n🎯 Search: '{query}' - {len(results)} results")
            
            for file_path, metadata in results[:3]:  # Show top 3 results
                print(f"  📄 {os.path.basename(file_path)} ({metadata.file_type.value})")
                print(f"     Path: {file_path}")
                print(f"     Size: {metadata.size} bytes")
                print(f"     Modified: {time.ctime(metadata.modified_time)}")
                
        # Search statistics
        stats = self.file_system.get_file_system_stats()
        print(f"\n📊 Search Index Statistics:")
        print(f"🔤 Indexed words: {stats['indexed_words']}")
        print(f"📁 Searchable files: {stats['total_files']}")
        
    def demo_cache_performance(self):
        """Demonstrate cache performance"""
        print("💾 CACHE PERFORMANCE DEMONSTRATION")
        print("═" * 60)
        
        # Create test files for cache testing
        print("📄 Creating test files...")
        
        test_files = []
        for i in range(10):
            content = f"Test file content #{i+1} " * 100
            file_id = self.file_system.create_file(
                f"/cache_test/file_{i+1:02d}.txt",
                content.encode(),
                FileType.REGULAR,
                "alice"
            )
            test_files.append(f"/cache_test/file_{i+1:02d}.txt")
            
        print(f"✅ Created {len(test_files)} test files")
        
        # Test cache performance
        print("\n⚡ Testing cache performance...")
        
        # First read (cache miss)
        print("🔄 First read (cache miss):")
        start_time = time.time()
        for file_path in test_files:
            content = self.file_system.read_file(file_path, AccessLevel.USER)
            self._log_event("read", file_path, "alice", len(content))
        first_read_time = time.time() - start_time
        
        # Second read (cache hit)
        print("🔄 Second read (cache hit):")
        start_time = time.time()
        for file_path in test_files:
            content = self.file_system.read_file(file_path, AccessLevel.USER)
            self._log_event("read", file_path, "alice", len(content))
        second_read_time = time.time() - start_time
        
        # Performance comparison
        print(f"\n📊 Cache Performance Results:")
        print(f"⏱️ First read time: {first_read_time:.3f}s")
        print(f"⚡ Second read time: {second_read_time:.3f}s")
        print(f"🚀 Speedup: {first_read_time / max(second_read_time, 0.001):.1f}x")
        
        # Cache statistics
        stats = self.file_system.get_file_system_stats()
        print(f"\n💾 Cache Statistics:")
        print(f"✅ Cache hits: {stats['cache_hits']}")
        print(f"❌ Cache misses: {stats['cache_misses']}")
        print(f"📈 Hit rate: {stats['cache_hit_rate']:.1f}%")
        
    def demo_file_system_monitor(self):
        """Demonstrate real-time file system monitoring"""
        print("📊 REAL-TIME FILE SYSTEM MONITORING")
        print("═" * 60)
        
        print("🔄 Starting background file activity...")
        
        # Start background activity
        activity_thread = threading.Thread(target=self._background_file_activity, daemon=True)
        activity_thread.start()
        
        print("🖥️ Launching interactive monitor...")
        print("📝 Use number keys (1-6) to switch between different views")
        print("⌨️ Type 'q' to quit the monitor")
        
        try:
            # Start interactive monitoring
            self.interactive_monitor.start_interactive_mode()
        except KeyboardInterrupt:
            print("\n⏹️ Monitor stopped by user")
            
    def demo_multi_user_simulation(self):
        """Demonstrate multi-user file sharing simulation"""
        print("👥 MULTI-USER FILE SHARING SIMULATION")
        print("═" * 60)
        
        # Create shared workspace
        print("🔄 Setting up shared workspace...")
        shared_dirs = [
            "/shared/documents",
            "/shared/projects",
            "/shared/ai_models",
            "/shared/blockchain_data"
        ]
        
        for directory in shared_dirs:
            try:
                self.file_system.create_directory(directory, AccessLevel.ADMIN)
                print(f"✅ Created: {directory}")
            except FileExistsError:
                pass
                
        # Simulate multi-user activity
        print("\n👥 Simulating multi-user activity...")
        
        users = ["alice", "bob", "charlie", "david"]
        activities = []
        
        for i in range(20):
            user = random.choice(users)
            activity_type = random.choice(["create", "read", "write", "share"])
            
            if activity_type == "create":
                filename = f"document_{random.randint(1000, 9999)}.txt"
                content = f"Document created by {user} at {time.strftime('%H:%M:%S')}"
                
                try:
                    file_id = self.file_system.create_file(
                        f"/shared/documents/{filename}",
                        content.encode(),
                        FileType.REGULAR,
                        user,
                        AccessLevel.USER
                    )
                    print(f"📄 {user} created {filename}")
                    self._log_event("create", f"/shared/documents/{filename}", user, len(content))
                    activities.append(f"{user} created {filename}")
                except:
                    pass
                    
            elif activity_type == "read":
                # Try to read a random file
                try:
                    entries = self.file_system.list_directory("/shared/documents")
                    if entries:
                        file_entry = random.choice([e for e in entries if not e.is_directory])
                        content = self.file_system.read_file(f"/shared/documents/{file_entry.name}", AccessLevel.USER)
                        print(f"📖 {user} read {file_entry.name} ({len(content)} bytes)")
                        self._log_event("read", f"/shared/documents/{file_entry.name}", user, len(content))
                        activities.append(f"{user} read {file_entry.name}")
                except:
                    pass
                    
            elif activity_type == "write":
                # Try to modify a file
                try:
                    entries = self.file_system.list_directory("/shared/documents")
                    if entries:
                        file_entry = random.choice([e for e in entries if not e.is_directory])
                        additional_content = f"\n# Edited by {user} at {time.strftime('%H:%M:%S')}"
                        self.file_system.write_file(
                            f"/shared/documents/{file_entry.name}",
                            additional_content.encode(),
                            AccessLevel.USER,
                            append=True
                        )
                        print(f"✏️ {user} edited {file_entry.name}")
                        self._log_event("write", f"/shared/documents/{file_entry.name}", user, len(additional_content))
                        activities.append(f"{user} edited {file_entry.name}")
                except:
                    pass
                    
            # Small delay between activities
            time.sleep(0.1)
            
        # Show collaboration summary
        print(f"\n📊 Collaboration Summary:")
        print(f"👥 Active users: {len(set(user for activity in activities for user in [activity.split()[0]]))}")
        print(f"📄 Total activities: {len(activities)}")
        
        # User activity breakdown
        user_stats = {}
        for activity in activities:
            user = activity.split()[0]
            user_stats[user] = user_stats.get(user, 0) + 1
            
        print("\n👤 User Activity:")
        for user, count in sorted(user_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {user}: {count} operations")
            
    def demo_comprehensive_test(self):
        """Run comprehensive file system test"""
        print("🧪 COMPREHENSIVE FILE SYSTEM TEST")
        print("═" * 60)
        
        print("🔄 Running comprehensive test suite...")
        
        # Performance test
        print("\n⚡ Performance Test:")
        start_time = time.time()
        
        # Create many files
        for i in range(50):
            content = f"Performance test file #{i+1} content " * 50
            try:
                self.file_system.create_file(
                    f"/performance_test/file_{i+1:03d}.txt",
                    content.encode(),
                    FileType.REGULAR,
                    "test_user"
                )
            except:
                pass
                
        creation_time = time.time() - start_time
        print(f"📄 Created 50 files in {creation_time:.3f}s ({50/creation_time:.1f} files/sec)")
        
        # Read performance
        start_time = time.time()
        files_read = 0
        try:
            entries = self.file_system.list_directory("/performance_test")
            for entry in entries:
                if not entry.is_directory:
                    content = self.file_system.read_file(f"/performance_test/{entry.name}", AccessLevel.USER)
                    files_read += 1
        except:
            pass
            
        read_time = time.time() - start_time
        print(f"📖 Read {files_read} files in {read_time:.3f}s ({files_read/max(read_time, 0.001):.1f} files/sec)")
        
        # Final statistics
        print("\n📊 Final System Statistics:")
        stats = self.file_system.get_file_system_stats()
        
        print(f"📁 Total Files: {stats['total_files']}")
        print(f"📂 Total Directories: {stats['total_directories']}")
        print(f"💾 Storage Used: {stats['used_storage']/1024/1024:.2f} MB / {stats['total_storage']/1024/1024:.2f} MB")
        print(f"📈 Storage Utilization: {stats['storage_utilization']:.1f}%")
        print(f"📖 Read Operations: {stats['read_operations']}")
        print(f"✏️ Write Operations: {stats['write_operations']}")
        print(f"💾 Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
        print(f"⚡ Average I/O Time: {stats['avg_io_time']*1000:.2f}ms")
        
        if self.encryption:
            security_stats = self.encryption.get_security_statistics()
            print(f"🔑 Encryption Keys: {security_stats['total_encryption_keys']}")
            print(f"🔒 Encrypted Files: {security_stats['encrypted_files']}")
            print(f"🛡️ Security Success Rate: {security_stats['success_rate']:.1f}%")
            
        print("\n✅ Comprehensive test completed!")
        
    def _background_file_activity(self):
        """Generate background file activity for monitoring demo"""
        operations = ["create", "read", "write", "delete"]
        
        for i in range(100):
            try:
                operation = random.choice(operations)
                user = random.choice(self.demo_users)
                
                if operation == "create":
                    filename = f"bg_file_{random.randint(1000, 9999)}.txt"
                    content = f"Background file created at {time.time()}"
                    
                    try:
                        file_id = self.file_system.create_file(
                            f"/tmp/{filename}",
                            content.encode(),
                            random.choice(list(FileType)),
                            user
                        )
                        self._log_event("create", f"/tmp/{filename}", user, len(content))
                    except:
                        pass
                        
                elif operation == "read":
                    try:
                        entries = self.file_system.list_directory("/tmp")
                        if entries:
                            entry = random.choice([e for e in entries if not e.is_directory])
                            content = self.file_system.read_file(f"/tmp/{entry.name}", AccessLevel.USER)
                            self._log_event("read", f"/tmp/{entry.name}", user, len(content))
                    except:
                        pass
                        
                elif operation == "write":
                    try:
                        entries = self.file_system.list_directory("/tmp")
                        if entries:
                            entry = random.choice([e for e in entries if not e.is_directory])
                            new_content = f"\nModified by {user} at {time.time()}"
                            self.file_system.write_file(f"/tmp/{entry.name}", new_content.encode(), AccessLevel.USER, append=True)
                            self._log_event("write", f"/tmp/{entry.name}", user, len(new_content))
                    except:
                        pass
                        
                elif operation == "delete":
                    try:
                        entries = self.file_system.list_directory("/tmp")
                        if entries and len(entries) > 5:  # Keep some files
                            entry = random.choice([e for e in entries if not e.is_directory])
                            self.file_system.delete_file(f"/tmp/{entry.name}", AccessLevel.USER)
                            self._log_event("delete", f"/tmp/{entry.name}", user, 0)
                    except:
                        pass
                        
                time.sleep(random.uniform(0.1, 1.0))
                
            except Exception:
                pass  # Continue on errors
                
    def _log_event(self, event_type: str, file_path: str, user_id: str, file_size: int):
        """Log file system event"""
        event = FileSystemEvent(
            timestamp=time.time(),
            event_type=event_type,
            file_path=file_path,
            user_id=user_id,
            file_size=file_size,
            success=True
        )
        self.visualizer.add_event(event)
        
    def _get_file_icon(self, filename: str) -> str:
        """Get file icon based on extension"""
        ext = os.path.splitext(filename)[1].lower()
        icon_map = {
            '.txt': '📄', '.md': '📝', '.py': '🐍', '.sol': '📜',
            '.pdf': '📕', '.doc': '📘', '.json': '📋', '.csv': '📊',
            '.png': '🖼️', '.jpg': '🖼️', '.bin': '⚙️', '.model': '🧠'
        }
        return icon_map.get(ext, '📄')

def main():
    """Main demo entry point"""
    print("🎯 " + "DECENTRALIZED AI NODE OS - STEP 4 DEMO".center(80, "="))
    print("📁 File System Implementation with Encryption & Visualization")
    print("=" * 80)
    print()
    
    demo = Step4Demo()
    
    try:
        demo.run_comprehensive_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    finally:
        # Cleanup
        demo.visualizer.stop_monitoring()
        print("🧹 Demo cleanup completed")
        print("👋 Thank you for trying Step 4 of the Decentralized AI Node OS!")

if __name__ == "__main__":
    main() 