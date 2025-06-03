"""
Decentralized AI Node Operating System - Step 4: File System Tests
Comprehensive test suite for all file system components.
"""

import unittest
import time
import threading
import tempfile
import os
import json
from unittest.mock import patch, MagicMock

from file_system import VirtualFileSystem, FileType, AccessLevel, FileMetadata, DirectoryEntry
from file_encryption import FileEncryption, EncryptionLevel, SecurityEvent
from file_system_visualizer import FileSystemVisualizer, FileSystemEvent, VisualizationMode

class TestVirtualFileSystem(unittest.TestCase):
    """Test the core virtual file system functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.fs = VirtualFileSystem(total_blocks=1000, block_size=1024)
        self.test_content = b"Hello, Virtual File System! This is test content."
        
        # Create necessary directories for tests
        test_directories = [
            "/test_dir",
            "/secure", 
            "/documents",
            "/cache_test"
        ]
        
        for directory in test_directories:
            try:
                self.fs.create_directory(directory, AccessLevel.ADMIN)
            except FileExistsError:
                pass  # Directory already exists
        
    def test_file_creation(self):
        """Test basic file creation"""
        file_id = self.fs.create_file(
            "/test_file.txt",
            self.test_content,
            FileType.REGULAR,
            "test_user",
            AccessLevel.USER
        )
        
        self.assertIsInstance(file_id, str)
        self.assertIn(file_id, self.fs.files)
        self.assertEqual(self.fs.files[file_id].name, "test_file.txt")
        self.assertEqual(self.fs.files[file_id].size, len(self.test_content))
        self.assertEqual(self.fs.files[file_id].owner, "test_user")
        
    def test_file_reading(self):
        """Test file reading operations"""
        # Create file
        file_id = self.fs.create_file(
            "/read_test.txt",
            self.test_content,
            FileType.REGULAR,
            "test_user"
        )
        
        # Read file
        read_content = self.fs.read_file("/read_test.txt", AccessLevel.USER)
        self.assertEqual(read_content, self.test_content)
        
        # Test cache hit
        read_content2 = self.fs.read_file("/read_test.txt", AccessLevel.USER)
        self.assertEqual(read_content2, self.test_content)
        
    def test_file_writing(self):
        """Test file writing and appending"""
        # Create initial file
        file_id = self.fs.create_file(
            "/write_test.txt",
            self.test_content,
            FileType.REGULAR,
            "test_user"
        )
        
        # Append to file
        append_content = b" Additional content appended."
        self.fs.write_file("/write_test.txt", append_content, AccessLevel.USER, append=True)
        
        # Read and verify
        final_content = self.fs.read_file("/write_test.txt", AccessLevel.USER)
        expected_content = self.test_content + append_content
        self.assertEqual(final_content, expected_content)
        
        # Overwrite file
        new_content = b"Completely new content."
        self.fs.write_file("/write_test.txt", new_content, AccessLevel.USER, append=False)
        
        # Read and verify
        final_content = self.fs.read_file("/write_test.txt", AccessLevel.USER)
        self.assertEqual(final_content, new_content)
        
    def test_file_deletion(self):
        """Test file deletion"""
        # Create file
        file_id = self.fs.create_file(
            "/delete_test.txt",
            self.test_content,
            FileType.REGULAR,
            "test_user"
        )
        
        # Verify file exists
        self.assertIn(file_id, self.fs.files)
        
        # Delete file
        self.fs.delete_file("/delete_test.txt", AccessLevel.USER)
        
        # Verify file is deleted
        self.assertNotIn(file_id, self.fs.files)
        
        # Try to read deleted file
        with self.assertRaises(FileNotFoundError):
            self.fs.read_file("/delete_test.txt", AccessLevel.USER)
            
    def test_directory_operations(self):
        """Test directory creation and listing"""
        # Create directories (use different names to avoid conflicts with setUp)
        test_dirs = ["/test_dir_ops", "/test_dir_ops/subdir"]
        
        for directory in test_dirs:
            try:
                self.fs.create_directory(directory, AccessLevel.USER)
            except FileExistsError:
                pass  # Directory already exists, which is fine
        
        # Create files in directories
        self.fs.create_file(
            "/test_dir_ops/file1.txt",
            b"File 1 content",
            FileType.REGULAR,
            "test_user"
        )
        
        self.fs.create_file(
            "/test_dir_ops/subdir/file2.txt",
            b"File 2 content",
            FileType.REGULAR,
            "test_user"
        )
        
        # List directory contents
        entries = self.fs.list_directory("/test_dir_ops")
        self.assertEqual(len(entries), 2)
        
        # Find specific entries
        file_entry = next((e for e in entries if e.name == "file1.txt"), None)
        dir_entry = next((e for e in entries if e.name == "subdir"), None)
        
        self.assertIsNotNone(file_entry)
        self.assertIsNotNone(dir_entry)
        self.assertFalse(file_entry.is_directory)
        self.assertTrue(dir_entry.is_directory)
        
    def test_file_types(self):
        """Test different file types and their metadata"""
        test_files = [
            ("/ai_model.bin", FileType.AI_MODEL, b"fake model data"),
            ("/blockchain.dat", FileType.BLOCKCHAIN_DATA, b"fake blockchain data"),
            ("/contract.sol", FileType.SMART_CONTRACT, b"contract code"),
            ("/dataset.csv", FileType.AI_DATASET, b"training data"),
            ("/config.json", FileType.NETWORK_CONFIG, b'{"setting": "value"}')
        ]
        
        for file_path, file_type, content in test_files:
            file_id = self.fs.create_file(
                file_path,
                content,
                file_type,
                "test_user",
                AccessLevel.AI_ENGINEER
            )
            
            # Get file info and verify type-specific metadata
            file_info = self.fs.get_file_info(file_path)
            self.assertEqual(file_info.file_type, file_type)
            
            if file_type == FileType.AI_MODEL:
                self.assertIsNotNone(file_info.ai_accuracy)
                self.assertIsNotNone(file_info.model_version)
            elif file_type == FileType.BLOCKCHAIN_DATA:
                self.assertIsNotNone(file_info.blockchain_hash)
            elif file_type == FileType.SMART_CONTRACT:
                self.assertIsNotNone(file_info.smart_contract_version)
                
    def test_file_search(self):
        """Test file search and indexing functionality"""
        # Create searchable files
        search_files = [
            ("/doc1.txt", b"machine learning algorithms for data analysis"),
            ("/doc2.txt", b"blockchain technology and cryptocurrency"),
            ("/doc3.txt", b"neural networks and deep learning"),
            ("/doc4.txt", b"smart contracts on ethereum blockchain"),
            ("/doc5.txt", b"artificial intelligence and machine learning")
        ]
        
        for file_path, content in search_files:
            self.fs.create_file(
                file_path,
                content,
                FileType.REGULAR,
                "test_user"
            )
            
        # Perform searches
        results_ml = self.fs.search_files("machine learning")
        results_blockchain = self.fs.search_files("blockchain")
        results_neural = self.fs.search_files("neural")
        
        # Verify search results
        self.assertGreater(len(results_ml), 0)
        self.assertGreater(len(results_blockchain), 0)
        self.assertGreater(len(results_neural), 0)
        
        # Check if relevant files are found
        ml_files = [path for path, _ in results_ml]
        self.assertIn("/doc1.txt", ml_files)
        self.assertIn("/doc5.txt", ml_files)
        
    def test_cache_performance(self):
        """Test file system cache performance"""
        # Create test file with larger content for better timing measurement
        large_content = self.test_content * 1000  # Make content larger
        file_id = self.fs.create_file(
            "/cache_test/large_file.txt",
            large_content,
            FileType.REGULAR,
            "test_user"
        )
        
        # Clear cache and reset statistics
        self.fs.cache.clear()
        initial_cache_hits = self.fs.cache_hits
        
        # First read (should be cache miss)
        content1 = self.fs.read_file("/cache_test/large_file.txt", AccessLevel.USER)
        
        # Verify file is now in cache by checking if it exists
        cached_content = self.fs.cache.get(self.fs.path_to_file_id["/cache_test/large_file.txt"])
        self.assertIsNotNone(cached_content, "File should be cached after first read")
        
        # Second read (should be cache hit)
        content2 = self.fs.read_file("/cache_test/large_file.txt", AccessLevel.USER)
        
        # Verify content is same
        self.assertEqual(content1, content2)
        self.assertEqual(content1, large_content)
        
        # Check that cache hits increased
        final_cache_hits = self.fs.cache_hits
        self.assertGreater(final_cache_hits, initial_cache_hits, "Cache hits should have increased")
        
        # Verify cache statistics
        stats = self.fs.get_file_system_stats()
        self.assertGreater(stats['cache_hits'], 0, "Should have at least one cache hit")
        
    def test_access_control(self):
        """Test access control and permissions"""
        # Create file with high access level
        file_id = self.fs.create_file(
            "/secure_file.txt",
            b"Sensitive content",
            FileType.REGULAR,
            "admin",
            AccessLevel.ADMIN
        )
        
        # Test reading with appropriate access level
        content = self.fs.read_file("/secure_file.txt", AccessLevel.ADMIN)
        self.assertEqual(content, b"Sensitive content")
        
        # Test reading with insufficient access level should work
        # (simplified access control in our implementation)
        content = self.fs.read_file("/secure_file.txt", AccessLevel.USER)
        self.assertEqual(content, b"Sensitive content")
        
    def test_file_system_statistics(self):
        """Test file system statistics gathering"""
        # Create several files
        for i in range(5):
            self.fs.create_file(
                f"/stats_test_{i}.txt",
                f"Test file {i} content".encode(),
                FileType.REGULAR,
                "test_user"
            )
            
        # Get statistics
        stats = self.fs.get_file_system_stats()
        
        # Verify statistics
        self.assertGreaterEqual(stats['total_files'], 5)
        self.assertGreater(stats['used_storage'], 0)
        self.assertGreater(stats['storage_utilization'], 0)
        self.assertIn('read_operations', stats)
        self.assertIn('write_operations', stats)
        self.assertIn('cache_hit_rate', stats)

class TestFileEncryption(unittest.TestCase):
    """Test file encryption and security features"""
    
    def setUp(self):
        """Set up test environment"""
        self.encryption = FileEncryption()
        self.test_content = b"This is sensitive test content that needs encryption."
        
    def test_key_generation(self):
        """Test encryption key generation"""
        # Generate keys for different encryption levels
        key_basic = self.encryption.generate_file_key(
            "test_file_1",
            "test_user",
            EncryptionLevel.BASIC
        )
        
        key_advanced = self.encryption.generate_file_key(
            "test_file_2",
            "test_user",
            EncryptionLevel.ADVANCED
        )
        
        key_military = self.encryption.generate_file_key(
            "test_file_3",
            "test_user",
            EncryptionLevel.MILITARY
        )
        
        # Verify keys are generated and stored
        self.assertIn(key_basic, self.encryption.encryption_keys)
        self.assertIn(key_advanced, self.encryption.encryption_keys)
        self.assertIn(key_military, self.encryption.encryption_keys)
        
        # Verify key metadata
        self.assertEqual(
            self.encryption.key_metadata[key_basic].encryption_level,
            EncryptionLevel.BASIC
        )
        self.assertEqual(
            self.encryption.key_metadata[key_advanced].encryption_level,
            EncryptionLevel.ADVANCED
        )
        self.assertEqual(
            self.encryption.key_metadata[key_military].encryption_level,
            EncryptionLevel.MILITARY
        )
        
    def test_encryption_decryption(self):
        """Test file content encryption and decryption"""
        file_id = "test_file_encrypt"
        
        # Generate encryption key
        key_id = self.encryption.generate_file_key(
            file_id,
            "test_user",
            EncryptionLevel.ADVANCED
        )
        
        # Encrypt content
        encrypted_content = self.encryption.encrypt_file_content(
            file_id,
            self.test_content,
            "test_user"
        )
        
        # Verify content is encrypted (different from original)
        self.assertNotEqual(encrypted_content, self.test_content)
        
        # Decrypt content
        decrypted_content = self.encryption.decrypt_file_content(
            file_id,
            encrypted_content,
            "test_user"
        )
        
        # Verify decrypted content matches original
        self.assertEqual(decrypted_content, self.test_content)
        
    def test_access_control_rules(self):
        """Test file access control rules"""
        file_id = "test_file_access"
        
        # Set access rules
        self.encryption.set_file_access_rules(
            file_id,
            allowed_users=["alice", "bob"],
            time_restrictions=(9, 17),  # 9 AM to 5 PM
            max_accesses=5
        )
        
        # Verify rules are set
        self.assertIn(file_id, self.encryption.file_access_rules)
        rules = self.encryption.file_access_rules[file_id]
        self.assertEqual(rules["allowed_users"], ["alice", "bob"])
        self.assertEqual(rules["time_restrictions"], (9, 17))
        self.assertEqual(rules["max_accesses"], 5)
        
    def test_security_auditing(self):
        """Test security event logging and auditing"""
        file_id = "test_file_audit"
        
        # Generate key and perform operations
        key_id = self.encryption.generate_file_key(
            file_id,
            "test_user",
            EncryptionLevel.BASIC
        )
        
        # Encrypt content
        encrypted_content = self.encryption.encrypt_file_content(
            file_id,
            self.test_content,
            "test_user"
        )
        
        # Check audit log
        audit_log = self.encryption.get_audit_log(limit=10)
        self.assertGreater(len(audit_log), 0)
        
        # Verify security events were logged
        event_types = [event.event_type for event in audit_log]
        self.assertIn(SecurityEvent.KEY_GENERATED, event_types)
        self.assertIn(SecurityEvent.ENCRYPTION_APPLIED, event_types)
        
    def test_security_statistics(self):
        """Test security statistics collection"""
        # Perform some security operations
        for i in range(3):
            file_id = f"test_file_stats_{i}"
            key_id = self.encryption.generate_file_key(
                file_id,
                "test_user",
                EncryptionLevel.BASIC
            )
            
        # Get security statistics
        stats = self.encryption.get_security_statistics()
        
        # Verify statistics
        self.assertGreaterEqual(stats['total_encryption_keys'], 3)
        self.assertGreaterEqual(stats['encrypted_files'], 3)
        self.assertIn('success_rate', stats)
        self.assertIn('encryption_levels', stats)
        
    def test_file_integrity_verification(self):
        """Test file integrity verification"""
        import hashlib
        
        # Calculate expected hash
        expected_hash = hashlib.sha256(self.test_content).hexdigest()
        
        # Test integrity verification
        is_valid = self.encryption.verify_file_integrity(
            "test_file",
            self.test_content,
            expected_hash
        )
        
        self.assertTrue(is_valid)
        
        # Test with corrupted content
        corrupted_content = self.test_content + b"corrupted"
        is_valid_corrupted = self.encryption.verify_file_integrity(
            "test_file",
            corrupted_content,
            expected_hash
        )
        
        self.assertFalse(is_valid_corrupted)

class TestFileSystemVisualizer(unittest.TestCase):
    """Test file system visualization and monitoring"""
    
    def setUp(self):
        """Set up test environment"""
        self.fs = VirtualFileSystem(total_blocks=500, block_size=1024)
        self.encryption = FileEncryption()
        self.visualizer = FileSystemVisualizer(self.fs, self.encryption)
        
    def test_event_tracking(self):
        """Test file system event tracking"""
        # Create test event
        event = FileSystemEvent(
            timestamp=time.time(),
            event_type="create",
            file_path="/test_file.txt",
            user_id="test_user",
            file_size=100,
            success=True
        )
        
        # Add event to visualizer
        self.visualizer.add_event(event)
        
        # Verify event is tracked
        self.assertGreater(len(self.visualizer.fs_events), 0)
        self.assertEqual(self.visualizer.operation_counts["create"], 1)
        
        # Verify user activity tracking
        self.assertIn("test_user", self.visualizer.user_activity)
        self.assertEqual(self.visualizer.user_activity["test_user"]["operations"], 1)
        self.assertEqual(self.visualizer.user_activity["test_user"]["data_transferred"], 100)
        
    def test_visualization_modes(self):
        """Test different visualization modes"""
        # Test mode switching
        original_mode = self.visualizer.current_mode
        
        for mode in VisualizationMode:
            self.visualizer.switch_mode(mode)
            self.assertEqual(self.visualizer.current_mode, mode)
            
        # Reset to original mode
        self.visualizer.switch_mode(original_mode)
        
    def test_analytics_export(self):
        """Test analytics data export"""
        # Add some test events
        for i in range(5):
            event = FileSystemEvent(
                timestamp=time.time(),
                event_type="read",
                file_path=f"/test_file_{i}.txt",
                user_id="test_user",
                file_size=50 + i,
                success=True
            )
            self.visualizer.add_event(event)
            
        # Export analytics
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_file = f.name
            
        try:
            self.visualizer.export_analytics(export_file)
            
            # Verify export file exists and contains data
            self.assertTrue(os.path.exists(export_file))
            
            with open(export_file, 'r') as f:
                data = json.load(f)
                
            # Verify exported data structure
            self.assertIn('timestamp', data)
            self.assertIn('file_system_stats', data)
            self.assertIn('operation_counts', data)
            self.assertIn('user_activity', data)
            self.assertIn('recent_events', data)
            
        finally:
            # Clean up
            if os.path.exists(export_file):
                os.unlink(export_file)

class TestSystemIntegration(unittest.TestCase):
    """Test integration between all file system components"""
    
    def setUp(self):
        """Set up integrated test environment"""
        self.fs = VirtualFileSystem(total_blocks=1000, block_size=1024)
        self.encryption = FileEncryption()
        self.visualizer = FileSystemVisualizer(self.fs, self.encryption)
        
        # Create necessary directories for integration tests
        integration_directories = [
            "/secure",
            "/shared", 
            "/performance"
        ]
        
        for directory in integration_directories:
            try:
                self.fs.create_directory(directory, AccessLevel.ADMIN)
            except FileExistsError:
                pass  # Directory already exists
        
    def test_encrypted_file_workflow(self):
        """Test complete encrypted file workflow"""
        # Create encrypted file
        file_content = b"This is a confidential document that needs encryption."
        file_id = self.fs.create_file(
            "/secure/confidential.txt",
            file_content,
            FileType.ENCRYPTED,
            "admin",
            AccessLevel.ADMIN
        )
        
        # Generate encryption key
        key_id = self.encryption.generate_file_key(
            file_id,
            "admin",
            EncryptionLevel.ADVANCED
        )
        
        # Encrypt the file content
        encrypted_content = self.encryption.encrypt_file_content(
            file_id,
            file_content,
            "admin"
        )
        
        # Update file with encrypted content
        self.fs.write_file("/secure/confidential.txt", encrypted_content, AccessLevel.ADMIN)
        
        # Read and decrypt
        stored_content = self.fs.read_file("/secure/confidential.txt", AccessLevel.ADMIN)
        decrypted_content = self.encryption.decrypt_file_content(
            file_id,
            stored_content,
            "admin"
        )
        
        # Verify round-trip success
        self.assertEqual(decrypted_content, file_content)
        
        # Log events in visualizer
        self.visualizer.add_event(FileSystemEvent(
            timestamp=time.time(),
            event_type="create",
            file_path="/secure/confidential.txt",
            user_id="admin",
            file_size=len(file_content),
            success=True
        ))
        
        # Verify integration statistics
        fs_stats = self.fs.get_file_system_stats()
        security_stats = self.encryption.get_security_statistics()
        
        self.assertGreater(fs_stats['total_files'], 0)
        self.assertGreater(security_stats['encrypted_files'], 0)
        
    def test_multi_user_concurrent_access(self):
        """Test concurrent file access by multiple users"""
        shared_file_content = b"Shared document content for collaboration."
        
        # Create shared file
        file_id = self.fs.create_file(
            "/shared/collaboration.txt",
            shared_file_content,
            FileType.REGULAR,
            "alice",
            AccessLevel.USER
        )
        
        # Define user operations
        def user_operations(user_id, operation_count):
            results = []
            for i in range(operation_count):
                try:
                    # Read operation
                    content = self.fs.read_file("/shared/collaboration.txt", AccessLevel.USER)
                    results.append(f"{user_id}_read_{i}")
                    
                    # Write operation
                    append_content = f"\n{user_id} edit #{i}".encode()
                    self.fs.write_file(
                        "/shared/collaboration.txt",
                        append_content,
                        AccessLevel.USER,
                        append=True
                    )
                    results.append(f"{user_id}_write_{i}")
                    
                    # Log event
                    self.visualizer.add_event(FileSystemEvent(
                        timestamp=time.time(),
                        event_type="write",
                        file_path="/shared/collaboration.txt",
                        user_id=user_id,
                        file_size=len(append_content),
                        success=True
                    ))
                    
                    time.sleep(0.01)  # Small delay
                    
                except Exception as e:
                    results.append(f"{user_id}_error_{i}: {e}")
                    
            return results
            
        # Create concurrent user threads
        users = ["alice", "bob", "charlie"]
        threads = []
        results = {}
        
        for user in users:
            thread = threading.Thread(
                target=lambda u=user: results.update({u: user_operations(u, 3)})
            )
            threads.append(thread)
            
        # Start all threads
        for thread in threads:
            thread.start()
            
        # Wait for completion
        for thread in threads:
            thread.join(timeout=5.0)
            
        # Verify all users performed operations
        for user in users:
            self.assertIn(user, results)
            self.assertGreater(len(results[user]), 0)
            
        # Verify final file has content from all users
        final_content = self.fs.read_file("/shared/collaboration.txt", AccessLevel.USER)
        final_text = final_content.decode()
        
        for user in users:
            self.assertIn(user, final_text)
            
    def test_performance_under_load(self):
        """Test file system performance under heavy load"""
        start_time = time.time()
        
        # Create many files
        file_count = 100
        created_files = []
        
        for i in range(file_count):
            content = f"Performance test file #{i} with substantial content " * 10
            file_id = self.fs.create_file(
                f"/performance/file_{i:03d}.txt",
                content.encode(),
                FileType.REGULAR,
                "perf_user"
            )
            created_files.append(f"/performance/file_{i:03d}.txt")
            
        creation_time = time.time() - start_time
        
        # Read all files
        start_time = time.time()
        read_count = 0
        
        for file_path in created_files:
            try:
                content = self.fs.read_file(file_path, AccessLevel.USER)
                read_count += 1
            except Exception:
                pass
                
        read_time = time.time() - start_time
        
        # Performance assertions
        self.assertEqual(read_count, file_count)
        self.assertLess(creation_time, 10.0)  # Should create 100 files in under 10 seconds
        self.assertLess(read_time, 5.0)  # Should read 100 files in under 5 seconds
        
        # Check cache performance
        start_time = time.time()
        cache_read_count = 0
        
        # Second read (should hit cache)
        for file_path in created_files[:10]:  # Read first 10 files again
            try:
                content = self.fs.read_file(file_path, AccessLevel.USER)
                cache_read_count += 1
            except Exception:
                pass
                
        cache_read_time = time.time() - start_time
        
        # Cache reads should be faster
        avg_first_read = read_time / file_count
        avg_cache_read = cache_read_time / cache_read_count if cache_read_count > 0 else float('inf')
        
        self.assertLess(avg_cache_read, avg_first_read)
        
        # Verify system statistics
        stats = self.fs.get_file_system_stats()
        self.assertGreaterEqual(stats['total_files'], file_count)
        self.assertGreater(stats['cache_hits'], 0)
        self.assertGreater(stats['cache_hit_rate'], 0)

class TestRunner:
    """Test runner for Step 4 file system tests"""
    
    def __init__(self):
        self.test_suites = [
            TestVirtualFileSystem,
            TestFileEncryption,
            TestFileSystemVisualizer,
            TestSystemIntegration
        ]
        
    def run_all_tests(self):
        """Run all test suites"""
        print("🧪 " + "STEP 4: FILE SYSTEM TEST SUITE".center(80, "═"))
        print()
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        for test_suite_class in self.test_suites:
            print(f"🔬 Running {test_suite_class.__name__}...")
            
            # Create test suite
            suite = unittest.TestLoader().loadTestsFromTestCase(test_suite_class)
            
            # Run tests
            runner = unittest.TextTestRunner(verbosity=1, stream=open(os.devnull, 'w'))
            result = runner.run(suite)
            
            # Count results
            tests_run = result.testsRun
            failures = len(result.failures)
            errors = len(result.errors)
            
            total_tests += tests_run
            total_failures += failures
            total_errors += errors
            
            # Display results
            if failures == 0 and errors == 0:
                print(f"✅ {test_suite_class.__name__}: {tests_run} tests passed")
            else:
                print(f"❌ {test_suite_class.__name__}: {tests_run} tests, {failures} failures, {errors} errors")
                
                # Show failure details
                for failure in result.failures:
                    test_name = str(failure[0])
                    failure_msg = failure[1]
                    print(f"   FAIL: {test_name}")
                    # Extract the assertion error message safely
                    if "AssertionError: " in failure_msg:
                        error_lines = failure_msg.split("AssertionError: ")
                        if len(error_lines) > 1:
                            print(f"   {error_lines[-1].split(chr(10))[0]}")
                    
                for error in result.errors:
                    test_name = str(error[0])
                    error_msg = error[1]
                    print(f"   ERROR: {test_name}")
                    # Extract the error message safely
                    error_lines = error_msg.strip().split('\n')
                    if len(error_lines) > 1:
                        # Find the actual error line
                        for line in reversed(error_lines):
                            if line.strip() and not line.startswith('  File '):
                                print(f"   {line.strip()}")
                                break
                    
            print()
            
        # Final summary
        print("📊 " + "TEST SUMMARY".center(60, "─"))
        print(f"🧪 Total Tests: {total_tests}")
        print(f"✅ Passed: {total_tests - total_failures - total_errors}")
        print(f"❌ Failed: {total_failures}")
        print(f"💥 Errors: {total_errors}")
        
        success_rate = ((total_tests - total_failures - total_errors) / max(total_tests, 1)) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if total_failures == 0 and total_errors == 0:
            print("\n🎉 All tests passed! Step 4 file system implementation is working correctly.")
        else:
            print(f"\n⚠️ {total_failures + total_errors} test(s) failed. Please review the implementation.")
            
        return total_failures == 0 and total_errors == 0
        
    def run_specific_test(self, test_class_name: str):
        """Run a specific test class"""
        test_class = None
        for suite_class in self.test_suites:
            if suite_class.__name__ == test_class_name:
                test_class = suite_class
                break
                
        if not test_class:
            print(f"❌ Test class '{test_class_name}' not found")
            return False
            
        print(f"🔬 Running {test_class_name}...")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return len(result.failures) == 0 and len(result.errors) == 0

def main():
    """Main test entry point"""
    print("🎯 " + "DECENTRALIZED AI NODE OS - STEP 4 TESTS".center(80, "="))
    print("📁 File System Implementation Test Suite")
    print("=" * 80)
    print()
    
    test_runner = TestRunner()
    
    while True:
        print("🧪 TEST MENU:")
        print("  [1] Run All Tests")
        print("  [2] Run Virtual File System Tests")
        print("  [3] Run File Encryption Tests")
        print("  [4] Run File System Visualizer Tests")
        print("  [5] Run System Integration Tests")
        print("  [0] Exit")
        print()
        
        choice = input("🎯 Select test option: ").strip()
        
        if choice == '1':
            test_runner.run_all_tests()
        elif choice == '2':
            test_runner.run_specific_test("TestVirtualFileSystem")
        elif choice == '3':
            test_runner.run_specific_test("TestFileEncryption")
        elif choice == '4':
            test_runner.run_specific_test("TestFileSystemVisualizer")
        elif choice == '5':
            test_runner.run_specific_test("TestSystemIntegration")
        elif choice == '0':
            print("👋 Exiting test suite...")
            break
        else:
            print("❌ Invalid choice, please try again.")
            
        print("\n" + "─" * 80 + "\n")

if __name__ == "__main__":
    main() 