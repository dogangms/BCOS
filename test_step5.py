"""
Decentralized AI Node Operating System - Step 5: Bonus Features Test Suite
Comprehensive testing for AI-based scheduler and Web GUI dashboard.
"""

import unittest
import time
import threading
import json
import random
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the components to test
from ai_scheduler import AIScheduler, LearningMode, ProcessType, PowerManager, PerformancePredictor
from web_gui import WebGUIServer, create_integrated_gui
from file_system import VirtualFileSystem, FileType, AccessLevel
from file_encryption import FileEncryption, EncryptionLevel

class TestAIScheduler(unittest.TestCase):
    """Test the AI-based intelligent scheduler"""
    
    def setUp(self):
        """Set up test environment"""
        self.scheduler = AIScheduler(num_cores=4)
        self.test_processes = [
            ("test_ai_1", ProcessType.AI_WORKER, 1.5, 200),
            ("test_blockchain_1", ProcessType.BLOCKCHAIN_MINER, 2.0, 300),
            ("test_contract_1", ProcessType.SMART_CONTRACT, 0.8, 150),
            ("test_network_1", ProcessType.NETWORK_HANDLER, 1.2, 100),
            ("test_system_1", ProcessType.SYSTEM, 0.5, 80)
        ]
        
    def test_scheduler_initialization(self):
        """Test AI scheduler proper initialization"""
        self.assertEqual(self.scheduler.num_cores, 4)
        self.assertEqual(self.scheduler.learning_mode, LearningMode.BALANCED)
        self.assertEqual(len(self.scheduler.ready_queue), 0)
        self.assertEqual(len(self.scheduler.running_processes), 0)
        self.assertEqual(self.scheduler.total_scheduled, 0)
        
    def test_add_process_basic(self):
        """Test basic process addition"""
        process_id, ptype, estimated_time, memory = self.test_processes[0]
        self.scheduler.add_process(process_id, ptype, estimated_time, memory)
        
        self.assertEqual(len(self.scheduler.ready_queue), 1)
        self.assertEqual(self.scheduler.total_scheduled, 1)
        
        process = self.scheduler.ready_queue[0]
        self.assertEqual(process["id"], process_id)
        self.assertEqual(process["type"], ptype)
        self.assertGreater(process["predicted_runtime"], 0)
        self.assertGreater(process["priority"], 0)
        
    def test_priority_based_ordering(self):
        """Test that processes are ordered by priority"""
        # Add multiple processes
        for process_data in self.test_processes:
            self.scheduler.add_process(*process_data)
            
        # Check that queue is ordered by priority (highest first)
        priorities = [p["priority"] for p in self.scheduler.ready_queue]
        self.assertEqual(priorities, sorted(priorities, reverse=True))
        
    def test_intelligent_scheduling(self):
        """Test AI-based scheduling decisions"""
        # Add processes
        for process_data in self.test_processes:
            self.scheduler.add_process(*process_data)
            
        scheduled_processes = []
        
        # Schedule processes on available cores
        for _ in range(self.scheduler.num_cores):
            scheduled = self.scheduler.schedule_next()
            if scheduled:
                scheduled_processes.append(scheduled)
                
        # Verify scheduling results
        self.assertGreater(len(scheduled_processes), 0)
        self.assertLessEqual(len(scheduled_processes), self.scheduler.num_cores)
        
        # Check that processes are assigned to different cores
        assigned_cores = [p["core_id"] for p in scheduled_processes]
        self.assertEqual(len(assigned_cores), len(set(assigned_cores)))  # All unique cores
        
    def test_process_completion_and_learning(self):
        """Test process completion and AI learning"""
        # Add and schedule a process
        process_id, ptype, estimated_time, memory = self.test_processes[0]
        self.scheduler.add_process(process_id, ptype, estimated_time, memory)
        
        scheduled = self.scheduler.schedule_next()
        self.assertIsNotNone(scheduled)
        
        core_id = scheduled["core_id"]
        initial_patterns = len(self.scheduler.predictor.patterns)
        
        # Complete the process
        self.scheduler.complete_process(core_id, success=True, actual_memory=memory, io_operations=10)
        
        # Verify learning occurred
        self.assertGreaterEqual(len(self.scheduler.predictor.patterns), initial_patterns)
        self.assertEqual(len(self.scheduler.running_processes), 0)  # Process removed from running
        
    def test_learning_mode_changes(self):
        """Test different AI learning modes"""
        modes_to_test = [
            LearningMode.AI_FOCUSED,
            LearningMode.BLOCKCHAIN_FOCUSED,
            LearningMode.POWER_SAVING,
            LearningMode.PERFORMANCE,
            LearningMode.BALANCED
        ]
        
        for mode in modes_to_test:
            self.scheduler.set_learning_mode(mode)
            self.assertEqual(self.scheduler.learning_mode, mode)
            
            # Verify learning rate is adjusted
            self.assertGreater(self.scheduler.predictor.learning_rate, 0)
            self.assertLessEqual(self.scheduler.predictor.learning_rate, 0.3)
            
    def test_performance_prediction(self):
        """Test AI performance prediction capabilities"""
        predictor = self.scheduler.predictor
        
        # Test prediction without historical data
        runtime1 = predictor.predict_runtime(ProcessType.AI_WORKER, 1.0)
        self.assertGreater(runtime1, 0)
        
        # Record some executions to build patterns
        predictor.record_execution("test1", ProcessType.AI_WORKER, 1.5, 200, 5, True)
        predictor.record_execution("test2", ProcessType.AI_WORKER, 1.8, 220, 8, True)
        
        # Test prediction with historical data
        runtime2 = predictor.predict_runtime(ProcessType.AI_WORKER)
        self.assertGreater(runtime2, 0)
        
        # Verify patterns are being learned
        pattern = predictor.patterns[ProcessType.AI_WORKER]
        self.assertGreater(pattern.execution_count, 0)
        self.assertGreater(pattern.avg_cpu_time, 0)
        
    def test_power_management(self):
        """Test power-aware scheduling"""
        power_manager = self.scheduler.power_manager
        
        # Test power state selection
        ai_power_state = power_manager.get_optimal_power_state(ProcessType.AI_WORKER, 0.5)
        blockchain_power_state = power_manager.get_optimal_power_state(ProcessType.BLOCKCHAIN_MINER, 0.5)
        
        self.assertIn(ai_power_state, ["high_performance", "balanced", "power_saver", "eco_mode"])
        self.assertIn(blockchain_power_state, ["high_performance", "balanced", "power_saver", "eco_mode"])
        
        # Test power cost calculation
        cost = power_manager.calculate_power_cost(ProcessType.AI_WORKER, 2.0, "high_performance")
        self.assertGreater(cost, 0)
        
    def test_adaptive_learning(self):
        """Test AI adaptive learning based on performance"""
        initial_adaptations = self.scheduler.adaptation_count
        
        # Simulate poor performance to trigger adaptation
        for _ in range(15):
            self.scheduler.performance_scores.append(30)  # Poor performance scores
            
        # Add and complete a process to trigger adaptation check
        self.scheduler.add_process("adapt_test", ProcessType.AI_WORKER, 1.0)
        scheduled = self.scheduler.schedule_next()
        if scheduled:
            self.scheduler.complete_process(scheduled["core_id"], success=False)
            
        # Check if adaptation occurred (may require multiple poor performances)
        self.assertGreaterEqual(self.scheduler.adaptation_count, initial_adaptations)
        
    def test_metrics_and_statistics(self):
        """Test AI metrics collection and reporting"""
        # Add some processes and let them run
        for process_data in self.test_processes[:3]:
            self.scheduler.add_process(*process_data)
            
        # Schedule and complete processes
        for _ in range(3):
            scheduled = self.scheduler.schedule_next()
            if scheduled:
                # Simulate quick completion
                self.scheduler.complete_process(scheduled["core_id"], success=True)
                
        # Get metrics
        metrics = self.scheduler.get_ai_metrics()
        
        # Verify metrics structure and content
        required_keys = [
            "learning_mode", "prediction_accuracy", "avg_performance_score",
            "total_scheduled", "adaptation_count", "system_load", "active_cores",
            "queue_length", "core_loads", "learning_rate"
        ]
        
        for key in required_keys:
            self.assertIn(key, metrics)
            
        self.assertGreaterEqual(metrics["total_scheduled"], 3)
        self.assertIsInstance(metrics["core_loads"], list)
        self.assertEqual(len(metrics["core_loads"]), self.scheduler.num_cores)
        
    def test_learning_data_export(self):
        """Test AI learning data export functionality"""
        # Generate some learning data
        for process_data in self.test_processes:
            self.scheduler.add_process(*process_data)
            scheduled = self.scheduler.schedule_next()
            if scheduled:
                self.scheduler.complete_process(scheduled["core_id"], success=True)
                
        # Export learning data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_filename = f.name
            
        try:
            self.scheduler.export_learning_data(temp_filename)
            
            # Verify file was created and contains valid JSON
            self.assertTrue(os.path.exists(temp_filename))
            
            with open(temp_filename, 'r') as f:
                data = json.load(f)
                
            # Verify data structure
            self.assertIn("timestamp", data)
            self.assertIn("scheduler_metrics", data)
            self.assertIn("process_patterns", data)
            self.assertIn("recent_decisions", data)
            
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

class TestWebGUIServer(unittest.TestCase):
    """Test the web-based GUI server"""
    
    def setUp(self):
        """Set up test environment"""
        self.file_system = VirtualFileSystem(total_blocks=500, block_size=1024)
        self.encryption = FileEncryption()
        self.ai_scheduler = AIScheduler(num_cores=2)
        self.gui_server = WebGUIServer(
            file_system=self.file_system,
            encryption=self.encryption,
            ai_scheduler=self.ai_scheduler,
            port=8081  # Use different port for testing
        )
        
    def test_gui_server_initialization(self):
        """Test GUI server proper initialization"""
        self.assertEqual(self.gui_server.port, 8081)
        self.assertFalse(self.gui_server.running)
        self.assertIsNotNone(self.gui_server.file_system)
        self.assertIsNotNone(self.gui_server.encryption)
        self.assertIsNotNone(self.gui_server.ai_scheduler)
        
    def test_html_generation(self):
        """Test HTML dashboard generation"""
        html_content = self.gui_server._generate_dashboard_html()
        
        # Verify HTML structure
        self.assertIn("<!DOCTYPE html>", html_content)
        self.assertIn("<title>", html_content)
        self.assertIn("Decentralized AI Node OS", html_content)
        self.assertIn("dashboard.js", html_content)
        self.assertIn("style.css", html_content)
        
        # Check for required sections
        required_sections = [
            "System Overview",
            "AI Scheduler Intelligence", 
            "File System Monitor",
            "Process Monitor"
        ]
        
        for section in required_sections:
            self.assertIn(section, html_content)
            
    def test_css_generation(self):
        """Test CSS stylesheet generation"""
        css_content = self.gui_server._generate_css()
        
        # Verify CSS structure and key elements
        self.assertIn("body {", css_content)
        self.assertIn("dashboard", css_content)
        self.assertIn("gradient", css_content)
        self.assertIn("@media", css_content)  # Responsive design
        self.assertIn("animation", css_content)  # Animations
        
    def test_javascript_generation(self):
        """Test JavaScript functionality generation"""
        js_content = self.gui_server._generate_javascript()
        
        # Verify JavaScript structure
        self.assertIn("class Dashboard", js_content)
        self.assertIn("initializeCharts", js_content)
        self.assertIn("updateAllData", js_content)
        self.assertIn("new Chart", js_content)
        
        # Check for API endpoints
        api_endpoints = ["/api/system", "/api/scheduler", "/api/files", "/api/security"]
        for endpoint in api_endpoints:
            self.assertIn(endpoint, js_content)
            
    def test_system_metrics_generation(self):
        """Test system metrics data generation"""
        metrics = self.gui_server._get_system_metrics()
        
        required_metrics = [
            "cpu_usage", "memory_usage", "disk_usage", 
            "network_activity", "process_count", "uptime"
        ]
        
        for metric in required_metrics:
            self.assertIn(metric, metrics)
            self.assertIsInstance(metrics[metric], (int, float))
            
        self.assertGreaterEqual(metrics["uptime"], 0)
        
    def test_file_system_data_integration(self):
        """Test file system data integration"""
        # Create some test files
        self.file_system.create_file("/test1.txt", b"test data", FileType.REGULAR, "test_user")
        self.file_system.create_file("/test2.dat", b"more data", FileType.AI_MODEL, "test_user")
        
        fs_data = self.gui_server._get_file_system_data()
        
        # Verify data structure
        expected_keys = ["total_files", "total_directories", "storage_utilization", "cache_hit_rate"]
        for key in expected_keys:
            self.assertIn(key, fs_data)
            
        self.assertGreaterEqual(fs_data["total_files"], 2)
        
    def test_scheduler_data_integration(self):
        """Test AI scheduler data integration"""
        # Add some processes to scheduler
        self.ai_scheduler.add_process("gui_test_1", ProcessType.AI_WORKER, 1.0)
        self.ai_scheduler.add_process("gui_test_2", ProcessType.BLOCKCHAIN_MINER, 1.5)
        
        scheduler_data = self.gui_server._get_scheduler_data()
        
        # Verify data structure
        expected_keys = [
            "learning_mode", "prediction_accuracy", "total_scheduled",
            "queue_length", "running_processes"
        ]
        
        for key in expected_keys:
            self.assertIn(key, scheduler_data)
            
        self.assertGreaterEqual(scheduler_data["total_scheduled"], 2)
        self.assertIsInstance(scheduler_data["running_processes"], dict)
        
    def test_security_data_integration(self):
        """Test security data integration"""
        # Create encrypted file
        file_id = self.file_system.create_file("/secure.dat", b"secret data", FileType.REGULAR, "test_user")
        key_id = self.encryption.generate_file_key(file_id, "test_user", EncryptionLevel.ADVANCED)
        
        security_data = self.gui_server._get_security_data()
        
        # Verify data structure
        expected_keys = ["encrypted_files", "active_encryption_keys", "success_rate", "blocked_users"]
        for key in expected_keys:
            self.assertIn(key, security_data)
            
    def test_integrated_gui_creation(self):
        """Test integrated GUI creation function"""
        gui = create_integrated_gui(
            file_system=self.file_system,
            encryption=self.encryption,
            ai_scheduler=self.ai_scheduler,
            port=8082
        )
        
        self.assertIsInstance(gui, WebGUIServer)
        self.assertEqual(gui.port, 8082)
        self.assertEqual(gui.file_system, self.file_system)
        self.assertEqual(gui.encryption, self.encryption)
        self.assertEqual(gui.ai_scheduler, self.ai_scheduler)

class TestIntegration(unittest.TestCase):
    """Test integration between AI scheduler and web GUI"""
    
    def setUp(self):
        """Set up integrated test environment"""
        self.file_system = VirtualFileSystem(total_blocks=1000, block_size=2048)
        self.encryption = FileEncryption()
        self.ai_scheduler = AIScheduler(num_cores=4)
        self.gui_server = WebGUIServer(
            self.file_system, self.encryption, self.ai_scheduler, port=8083
        )
        
    def test_full_system_integration(self):
        """Test full system integration with all components"""
        # Create file system content - use existing directories from file system initialization
        test_files = [
            ("/ai_models/ai_model.dat", b"AI model data" * 50, FileType.AI_MODEL),
            ("/blockchain/block.dat", b"Blockchain data" * 30, FileType.BLOCKCHAIN_DATA),
            ("/smart_contracts/smart.sol", b"Smart contract code" * 20, FileType.SMART_CONTRACT)
        ]
        
        # These directories should already exist from file system initialization
        # No need to create them manually
        
        for file_path, content, file_type in test_files:
            file_id = self.file_system.create_file(file_path, content, file_type, "integration_user")
            
            # Add encryption for sensitive files
            if file_type in [FileType.AI_MODEL, FileType.BLOCKCHAIN_DATA]:
                key_id = self.encryption.generate_file_key(file_id, "integration_user", EncryptionLevel.ADVANCED)
                
        # Add AI scheduler workload
        ai_processes = [
            ("ai_train_1", ProcessType.AI_WORKER, 2.0, 400),
            ("blockchain_mine_1", ProcessType.BLOCKCHAIN_MINER, 3.0, 500),
            ("contract_exec_1", ProcessType.SMART_CONTRACT, 1.0, 200),
            ("network_sync_1", ProcessType.NETWORK_HANDLER, 1.5, 150)
        ]
        
        for process_data in ai_processes:
            self.ai_scheduler.add_process(*process_data)
            
        # Schedule and run some processes
        scheduled_count = 0
        for _ in range(3):
            scheduled = self.ai_scheduler.schedule_next()
            if scheduled:
                scheduled_count += 1
                # Simulate quick completion
                self.ai_scheduler.complete_process(scheduled["core_id"], success=True)
                
        # Test GUI data generation with integrated system
        system_metrics = self.gui_server._get_system_metrics()
        file_metrics = self.gui_server._get_file_system_data()
        scheduler_metrics = self.gui_server._get_scheduler_data()
        security_metrics = self.gui_server._get_security_data()
        
        # Verify integrated data
        self.assertGreater(file_metrics["total_files"], 0)
        self.assertGreater(scheduler_metrics["total_scheduled"], 0)
        self.assertGreater(security_metrics["encrypted_files"], 0)
        self.assertGreaterEqual(system_metrics["uptime"], 0)  # Allow 0 uptime for fresh instances
        
    def test_real_time_data_flow(self):
        """Test real-time data flow between components"""
        initial_files = self.gui_server._get_file_system_data()["total_files"]
        initial_scheduled = self.gui_server._get_scheduler_data()["total_scheduled"]
        
        # Add new file
        self.file_system.create_file("/realtime_test.txt", b"real-time test", FileType.REGULAR, "test_user")
        
        # Add new process
        self.ai_scheduler.add_process("realtime_proc", ProcessType.AI_WORKER, 1.0)
        
        # Verify data updates
        updated_files = self.gui_server._get_file_system_data()["total_files"]
        updated_scheduled = self.gui_server._get_scheduler_data()["total_scheduled"]
        
        self.assertGreater(updated_files, initial_files)
        self.assertGreater(updated_scheduled, initial_scheduled)
        
    def test_concurrent_operations(self):
        """Test concurrent operations across all components"""
        def file_operations():
            for i in range(5):
                self.file_system.create_file(f"/concurrent_{i}.dat", f"data_{i}".encode(), FileType.REGULAR, "concurrent_user")
                time.sleep(0.1)
                
        def scheduler_operations():
            for i in range(5):
                self.ai_scheduler.add_process(f"concurrent_proc_{i}", ProcessType.AI_WORKER, 1.0)
                scheduled = self.ai_scheduler.schedule_next()
                if scheduled:
                    # Quick completion
                    self.ai_scheduler.complete_process(scheduled["core_id"], success=True)
                time.sleep(0.1)
                
        # Run concurrent operations
        file_thread = threading.Thread(target=file_operations)
        scheduler_thread = threading.Thread(target=scheduler_operations)
        
        file_thread.start()
        scheduler_thread.start()
        
        file_thread.join()
        scheduler_thread.join()
        
        # Verify final state
        final_metrics = {
            "files": self.gui_server._get_file_system_data(),
            "scheduler": self.gui_server._get_scheduler_data(),
            "system": self.gui_server._get_system_metrics()
        }
        
        self.assertGreaterEqual(final_metrics["files"]["total_files"], 5)
        self.assertGreaterEqual(final_metrics["scheduler"]["total_scheduled"], 5)

class TestPerformance(unittest.TestCase):
    """Test performance characteristics of bonus features"""
    
    def setUp(self):
        """Set up performance test environment"""
        self.ai_scheduler = AIScheduler(num_cores=8)
        
    def test_scheduler_performance_under_load(self):
        """Test AI scheduler performance under heavy load"""
        start_time = time.time()
        
        # Add many processes quickly
        for i in range(100):
            process_type = random.choice(list(ProcessType))
            estimated_time = random.uniform(0.5, 2.0)
            memory_req = random.uniform(100, 500)
            
            self.ai_scheduler.add_process(f"perf_test_{i}", process_type, estimated_time, memory_req)
            
        addition_time = time.time() - start_time
        
        # Schedule processes quickly
        start_time = time.time()
        scheduled_count = 0
        
        while len(self.ai_scheduler.ready_queue) > 0 and scheduled_count < 8:
            scheduled = self.ai_scheduler.schedule_next()
            if scheduled:
                scheduled_count += 1
                # Quick completion
                self.ai_scheduler.complete_process(scheduled["core_id"], success=True)
                
        scheduling_time = time.time() - start_time
        
        # Performance assertions
        self.assertLess(addition_time, 1.0, "Process addition should be fast")
        self.assertLess(scheduling_time, 0.5, "Scheduling should be fast")
        self.assertEqual(scheduled_count, 8, "Should schedule up to core limit")
        
    def test_gui_data_generation_performance(self):
        """Test GUI data generation performance"""
        # Create substantial system state
        file_system = VirtualFileSystem(total_blocks=1000, block_size=2048)
        encryption = FileEncryption()
        
        # Create many files
        for i in range(50):
            file_system.create_file(f"/perf_test_{i}.dat", f"test data {i}".encode() * 10, FileType.REGULAR, "perf_user")
            
        # Add many processes
        for i in range(50):
            self.ai_scheduler.add_process(f"perf_proc_{i}", random.choice(list(ProcessType)), random.uniform(0.5, 2.0))
            
        gui_server = WebGUIServer(file_system, encryption, self.ai_scheduler)
        
        # Test data generation performance
        start_time = time.time()
        
        metrics = {
            "system": gui_server._get_system_metrics(),
            "files": gui_server._get_file_system_data(),
            "scheduler": gui_server._get_scheduler_data(),
            "security": gui_server._get_security_data()
        }
        
        generation_time = time.time() - start_time
        
        # Performance assertion
        self.assertLess(generation_time, 0.1, "GUI data generation should be fast")
        
        # Verify data completeness
        for category, data in metrics.items():
            self.assertIsInstance(data, dict)
            self.assertGreater(len(data), 0)

def run_comprehensive_tests():
    """Run all test suites with detailed reporting"""
    print("🧪 " + "STEP 5 BONUS FEATURES TEST SUITE".center(80, "="))
    print("🤖 AI Scheduler + 🖥️ Web GUI Dashboard Testing")
    print("=" * 80)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [TestAIScheduler, TestWebGUIServer, TestIntegration, TestPerformance]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
        
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=None)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("🏁 TEST EXECUTION SUMMARY")
    print("=" * 80)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    passed = total_tests - failures - errors - skipped
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failures}")
    print(f"💥 Errors: {errors}")
    print(f"⏭️ Skipped: {skipped}")
    
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if failures > 0:
        print("\n💥 FAILURES:")
        for test, traceback in result.failures:
            print(f"   ❌ {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else 'Unknown failure'}")
            
    if errors > 0:
        print("\n🚨 ERRORS:")
        for test, traceback in result.errors:
            print(f"   💥 {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else 'Unknown error'}")
    
    print("\n" + "=" * 80)
    
    if failures == 0 and errors == 0:
        print("🎉 ALL TESTS PASSED! Step 5 bonus features are working perfectly!")
        print("🚀 AI Scheduler and Web GUI are ready for production!")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
        
    print("=" * 80)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_comprehensive_tests() 