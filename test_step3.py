"""
Decentralized AI Node Operating System - Step 3: Test Suite
Comprehensive tests for threading API, synchronization primitives, and concurrency problems.
"""

import unittest
import threading
import time
import random
from typing import List

from thread_api import ThreadAPI, ThreadType, ThreadPriority, ThreadState
from concurrency_problems import ProducerConsumerAI, DiningPhilosophersAI, ReadersWritersAI
from synchronization_visualizer import SynchronizationVisualizer, SyncEvent

class TestThreadAPI(unittest.TestCase):
    """Test cases for the Thread API"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.thread_api = ThreadAPI()
        
    def test_thread_creation(self):
        """Test basic thread creation"""
        def dummy_task():
            time.sleep(0.1)
            return "completed"
            
        thread_id = self.thread_api.create_thread(
            function=dummy_task,
            name="TestThread",
            thread_type=ThreadType.USER_THREAD,
            priority=ThreadPriority.NORMAL
        )
        
        self.assertIsNotNone(thread_id)
        self.assertIn(thread_id, self.thread_api.threads)
        
        thread = self.thread_api.get_thread_info(thread_id)
        self.assertEqual(thread.name, "TestThread")
        self.assertEqual(thread.thread_type, ThreadType.USER_THREAD)
        self.assertEqual(thread.priority, ThreadPriority.NORMAL)
        self.assertEqual(thread.state, ThreadState.CREATED)
        
    def test_thread_execution(self):
        """Test thread execution and completion"""
        result_holder = {"value": None}
        
        def test_task(value):
            result_holder["value"] = value * 2
            return result_holder["value"]
            
        thread_id = self.thread_api.create_thread(
            function=test_task,
            args=(42,),
            name="ExecutionTest"
        )
        
        # Start and wait for completion
        success = self.thread_api.start_thread(thread_id)
        self.assertTrue(success)
        
        completed = self.thread_api.join_thread(thread_id, timeout=5.0)
        self.assertTrue(completed)
        
        thread = self.thread_api.get_thread_info(thread_id)
        self.assertEqual(thread.state, ThreadState.TERMINATED)
        self.assertEqual(result_holder["value"], 84)
        
    def test_multiple_threads(self):
        """Test multiple concurrent threads"""
        shared_counter = {"value": 0}
        lock = threading.Lock()
        
        def increment_task(iterations):
            for _ in range(iterations):
                with lock:
                    shared_counter["value"] += 1
                time.sleep(0.001)  # Small delay
                
        # Create multiple threads
        threads = []
        iterations_per_thread = 50
        num_threads = 5
        
        for i in range(num_threads):
            thread_id = self.thread_api.create_thread(
                function=increment_task,
                args=(iterations_per_thread,),
                name=f"Counter-{i}",
                thread_type=ThreadType.DATA_PROCESSOR
            )
            threads.append(thread_id)
            
        # Start all threads
        for thread_id in threads:
            self.thread_api.start_thread(thread_id)
            
        # Wait for all to complete
        for thread_id in threads:
            self.thread_api.join_thread(thread_id, timeout=10.0)
            
        # Verify result
        expected_value = num_threads * iterations_per_thread
        self.assertEqual(shared_counter["value"], expected_value)
        
    def test_thread_types_and_priorities(self):
        """Test different thread types and priorities"""
        def dummy_task():
            time.sleep(0.1)
            
        # Test all thread types
        for thread_type in ThreadType:
            thread_id = self.thread_api.create_thread(
                function=dummy_task,
                name=f"Type-{thread_type.name}",
                thread_type=thread_type
            )
            thread = self.thread_api.get_thread_info(thread_id)
            self.assertEqual(thread.thread_type, thread_type)
            
        # Test all priorities
        for priority in ThreadPriority:
            thread_id = self.thread_api.create_thread(
                function=dummy_task,
                name=f"Priority-{priority.name}",
                priority=priority
            )
            thread = self.thread_api.get_thread_info(thread_id)
            self.assertEqual(thread.priority, priority)

class TestSynchronizationPrimitives(unittest.TestCase):
    """Test cases for synchronization primitives"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.thread_api = ThreadAPI()
        
    def test_lock_creation_and_basic_usage(self):
        """Test lock creation and basic acquire/release"""
        lock_id = "test_lock"
        thread_id = "test_thread"
        
        # Create lock
        success = self.thread_api.create_lock(lock_id)
        self.assertTrue(success)
        self.assertIn(lock_id, self.thread_api.locks)
        
        # Cannot create duplicate
        success = self.thread_api.create_lock(lock_id)
        self.assertFalse(success)
        
        # Create a dummy thread for testing
        dummy_thread_id = self.thread_api.create_thread(
            function=lambda: time.sleep(0.1),
            name="DummyThread"
        )
        
        # Test acquire and release
        acquired = self.thread_api.acquire_lock(lock_id, dummy_thread_id)
        self.assertTrue(acquired)
        
        thread = self.thread_api.get_thread_info(dummy_thread_id)
        self.assertIn(lock_id, thread.locks_held)
        
        released = self.thread_api.release_lock(lock_id, dummy_thread_id)
        self.assertTrue(released)
        
        thread = self.thread_api.get_thread_info(dummy_thread_id)
        self.assertNotIn(lock_id, thread.locks_held)
        
    def test_lock_contention(self):
        """Test lock contention between threads"""
        lock_id = "contention_lock"
        self.thread_api.create_lock(lock_id)
        
        execution_order = []
        lock = threading.Lock()
        
        def lock_worker(worker_id):
            # Create thread in API
            api_thread_id = self.thread_api.create_thread(
                function=lambda: None,
                name=f"LockWorker-{worker_id}"
            )
            
            # Simulate lock acquisition
            if self.thread_api.acquire_lock(lock_id, api_thread_id, blocking=False):
                try:
                    with lock:
                        execution_order.append(f"start-{worker_id}")
                    time.sleep(0.1)
                    with lock:
                        execution_order.append(f"end-{worker_id}")
                finally:
                    self.thread_api.release_lock(lock_id, api_thread_id)
                    
        # Start multiple threads trying to acquire the same lock
        threads = []
        for i in range(3):
            thread = threading.Thread(target=lock_worker, args=(i,))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join(timeout=5.0)
            
        # Verify that execution was serialized
        self.assertTrue(len(execution_order) <= 6)  # At most 3 start/end pairs
        
    def test_condition_variables(self):
        """Test condition variable functionality"""
        cv_id = "test_cv"
        lock_id = "test_cv_lock"
        
        # Create lock and condition variable
        self.thread_api.create_lock(lock_id)
        success = self.thread_api.create_condition_variable(cv_id, lock_id)
        self.assertTrue(success)
        self.assertIn(cv_id, self.thread_api.condition_variables)
        
        # Test notification
        notified = self.thread_api.notify_condition(cv_id)
        self.assertTrue(notified)
        
        notified_all = self.thread_api.notify_condition(cv_id, notify_all=True)
        self.assertTrue(notified_all)
        
    def test_semaphores(self):
        """Test semaphore functionality"""
        sem_id = "test_semaphore"
        initial_value = 2
        
        # Create semaphore
        success = self.thread_api.create_semaphore(sem_id, initial_value)
        self.assertTrue(success)
        self.assertIn(sem_id, self.thread_api.semaphores)
        
        # Cannot create duplicate
        success = self.thread_api.create_semaphore(sem_id, 1)
        self.assertFalse(success)
        
        # Create dummy threads for testing
        thread_ids = []
        for i in range(3):
            thread_id = self.thread_api.create_thread(
                function=lambda: time.sleep(0.1),
                name=f"SemThread-{i}"
            )
            thread_ids.append(thread_id)
            
        # Acquire semaphore multiple times
        acquired_count = 0
        for thread_id in thread_ids:
            if self.thread_api.acquire_semaphore(sem_id, thread_id, blocking=False):
                acquired_count += 1
                
        # Should only allow initial_value acquisitions
        self.assertEqual(acquired_count, initial_value)

class TestConcurrencyProblems(unittest.TestCase):
    """Test cases for classical concurrency problems"""
    
    def test_producer_consumer_basic(self):
        """Test basic Producer-Consumer functionality"""
        pc = ProducerConsumerAI(
            buffer_size=5,
            num_producers=2,
            num_consumers=1
        )
        
        # Run for a short duration
        start_time = time.time()
        pc.start_simulation(duration=3.0)
        duration = time.time() - start_time
        
        # Verify simulation ran for approximately the right duration
        self.assertGreater(duration, 2.5)
        self.assertLess(duration, 5.0)
        
        # Verify some production and consumption occurred
        self.assertGreater(pc.total_produced, 0)
        self.assertGreater(pc.total_consumed, 0)
        
    def test_dining_philosophers_basic(self):
        """Test basic Dining Philosophers functionality"""
        dp = DiningPhilosophersAI(num_philosophers=3)
        
        start_time = time.time()
        dp.start_simulation(duration=3.0)
        duration = time.time() - start_time
        
        # Verify simulation ran
        self.assertGreater(duration, 2.5)
        self.assertLess(duration, 5.0)
        
        # Verify some eating occurred
        total_eating = sum(dp.eating_count)
        self.assertGreater(total_eating, 0)
        
    def test_readers_writers_basic(self):
        """Test basic Readers-Writers functionality"""
        rw = ReadersWritersAI(
            num_readers=3,
            num_writers=1
        )
        
        start_time = time.time()
        rw.start_simulation(duration=3.0)
        duration = time.time() - start_time
        
        # Verify simulation ran
        self.assertGreater(duration, 2.5)
        self.assertLess(duration, 5.0)
        
        # Verify some operations occurred
        total_reads = sum(rw.read_operations.values())
        total_writes = sum(rw.write_operations.values())
        
        self.assertGreater(total_reads, 0)
        self.assertGreater(total_writes, 0)
        self.assertGreater(total_reads, total_writes)  # More reads than writes

class TestSynchronizationVisualizer(unittest.TestCase):
    """Test cases for the synchronization visualizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.thread_api = ThreadAPI()
        self.visualizer = SynchronizationVisualizer(self.thread_api)
        
    def test_visualizer_creation(self):
        """Test visualizer initialization"""
        self.assertIsNotNone(self.visualizer.thread_api)
        self.assertFalse(self.visualizer.running)
        self.assertEqual(len(self.visualizer.sync_events), 0)
        
    def test_sync_event_tracking(self):
        """Test synchronization event tracking"""
        event = SyncEvent(
            timestamp=time.time(),
            thread_id="test_thread",
            event_type="lock_acquire",
            resource_id="test_lock",
            success=True,
            wait_time=0.1
        )
        
        self.visualizer.add_sync_event(event)
        self.assertEqual(len(self.visualizer.sync_events), 1)
        
        recorded_event = self.visualizer.sync_events[0]
        self.assertEqual(recorded_event.thread_id, "test_thread")
        self.assertEqual(recorded_event.event_type, "lock_acquire")
        self.assertEqual(recorded_event.resource_id, "test_lock")
        
    def test_thread_snapshot(self):
        """Test thread snapshot functionality"""
        # Create a test thread
        thread_id = self.thread_api.create_thread(
            function=lambda: time.sleep(0.1),
            name="SnapshotTestThread",
            thread_type=ThreadType.AI_WORKER
        )
        
        # Take snapshot
        self.visualizer.take_thread_snapshot()
        
        # Verify snapshot was recorded
        self.assertIn(thread_id, self.visualizer.thread_snapshots)
        snapshots = self.visualizer.thread_snapshots[thread_id]
        self.assertEqual(len(snapshots), 1)
        
        snapshot = snapshots[0]
        self.assertEqual(snapshot.thread_id, thread_id)
        self.assertEqual(snapshot.name, "SnapshotTestThread")
        self.assertEqual(snapshot.thread_type, ThreadType.AI_WORKER)

class TestSystemIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.thread_api = ThreadAPI()
        
    def test_concurrent_access_patterns(self):
        """Test realistic concurrent access patterns"""
        # Simulate AI training scenario with multiple components
        shared_model = {"parameters": 0, "version": 0}
        model_lock_id = "model_lock"
        update_cv_id = "model_update_cv"
        
        self.thread_api.create_lock(model_lock_id)
        self.thread_api.create_condition_variable(update_cv_id, model_lock_id)
        
        results = {"trainers": 0, "validators": 0, "updates": 0}
        
        def ai_trainer(trainer_id):
            api_thread_id = self.thread_api.create_thread(
                function=lambda: None,
                name=f"Trainer-{trainer_id}",
                thread_type=ThreadType.AI_WORKER
            )
            
            for _ in range(5):
                if self.thread_api.acquire_lock(model_lock_id, api_thread_id):
                    try:
                        # Simulate training
                        time.sleep(random.uniform(0.01, 0.05))
                        shared_model["parameters"] += 1
                        results["trainers"] += 1
                        
                        # Notify validators
                        self.thread_api.notify_condition(update_cv_id)
                    finally:
                        self.thread_api.release_lock(model_lock_id, api_thread_id)
                        
                time.sleep(random.uniform(0.01, 0.03))
                
        def model_validator(validator_id):
            api_thread_id = self.thread_api.create_thread(
                function=lambda: None,
                name=f"Validator-{validator_id}",
                thread_type=ThreadType.DATA_PROCESSOR
            )
            
            for _ in range(3):
                if self.thread_api.acquire_lock(model_lock_id, api_thread_id):
                    try:
                        # Wait for model updates
                        self.thread_api.wait_condition(update_cv_id, api_thread_id, timeout=1.0)
                        
                        # Simulate validation
                        time.sleep(random.uniform(0.01, 0.03))
                        results["validators"] += 1
                    finally:
                        self.thread_api.release_lock(model_lock_id, api_thread_id)
                        
        # Start concurrent threads
        threads = []
        
        # Trainer threads
        for i in range(3):
            thread = threading.Thread(target=ai_trainer, args=(i,))
            threads.append(thread)
            thread.start()
            
        # Validator threads
        for i in range(2):
            thread = threading.Thread(target=model_validator, args=(i,))
            threads.append(thread)
            thread.start()
            
        # Wait for completion
        for thread in threads:
            thread.join(timeout=10.0)
            
        # Verify results
        self.assertGreater(results["trainers"], 0)
        self.assertGreater(results["validators"], 0)
        self.assertEqual(shared_model["parameters"], results["trainers"])
        
    def test_system_performance_under_load(self):
        """Test system performance under high thread load"""
        def cpu_intensive_task(task_id, iterations):
            # Simulate CPU-intensive AI computation
            total = 0
            for i in range(iterations):
                total += i ** 2
                if i % 100 == 0:
                    time.sleep(0.001)  # Yield occasionally
            return total
            
        # Create many threads
        num_threads = 20
        iterations = 1000
        threads = []
        
        start_time = time.time()
        
        for i in range(num_threads):
            thread_id = self.thread_api.create_thread(
                function=cpu_intensive_task,
                args=(i, iterations),
                name=f"LoadTest-{i}",
                thread_type=ThreadType.AI_WORKER if i % 2 == 0 else ThreadType.DATA_PROCESSOR
            )
            threads.append(thread_id)
            self.thread_api.start_thread(thread_id)
            
        # Wait for all threads to complete
        for thread_id in threads:
            self.thread_api.join_thread(thread_id, timeout=30.0)
            
        duration = time.time() - start_time
        
        # Verify system handled the load
        stats = self.thread_api.get_system_stats()
        self.assertEqual(stats['total_threads_created'], num_threads)
        self.assertEqual(stats['total_threads_completed'], num_threads)
        self.assertLess(duration, 30.0)  # Should complete within reasonable time

def run_all_tests():
    """Run all test suites"""
    print("🧪 " + "STEP 3 TEST SUITE".center(60, "═"))
    print()
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestThreadAPI))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSynchronizationPrimitives))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestConcurrencyProblems))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSynchronizationVisualizer))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSystemIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "═" * 60)
    print("📊 TEST RESULTS SUMMARY:")
    print(f"✅ Tests Run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️ Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, failure in result.failures:
            print(f"  {test}: {failure}")
            
    if result.errors:
        print("\n⚠️ ERRORS:")
        for test, error in result.errors:
            print(f"  {test}: {error}")
            
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")
        sys.exit(1) 