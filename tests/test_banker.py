"""
Tests for the Banker's Algorithm implementation.
"""

import unittest
from core.banker_algorithm import BankerAlgorithm


class TestBankerAlgorithm(unittest.TestCase):
    """Test cases for the Banker's Algorithm."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize with available resources
        self.available_resources = {
            "cpu": 10,
            "memory": 10,
            "disk": 10,
            "network": 10
        }
        
        self.banker = BankerAlgorithm(self.available_resources)
        
    def test_register_process(self):
        """Test process registration."""
        # Register a process
        result = self.banker.register_process("p1", {
            "cpu": 5,
            "memory": 5,
            "disk": 5,
            "network": 5
        })
        
        self.assertTrue(result)
        self.assertIn("p1", self.banker.max_claim)
        self.assertIn("p1", self.banker.allocation)
        self.assertIn("p1", self.banker.need)
        
        # Check initial allocation
        self.assertEqual(self.banker.allocation["p1"]["cpu"], 0)
        self.assertEqual(self.banker.allocation["p1"]["memory"], 0)
        self.assertEqual(self.banker.allocation["p1"]["disk"], 0)
        self.assertEqual(self.banker.allocation["p1"]["network"], 0)
        
        # Check need
        self.assertEqual(self.banker.need["p1"]["cpu"], 5)
        self.assertEqual(self.banker.need["p1"]["memory"], 5)
        self.assertEqual(self.banker.need["p1"]["disk"], 5)
        self.assertEqual(self.banker.need["p1"]["network"], 5)
        
    def test_request_resources(self):
        """Test resource request."""
        # Register a process
        self.banker.register_process("p1", {
            "cpu": 5,
            "memory": 5,
            "disk": 5,
            "network": 5
        })
        
        # Request resources
        result = self.banker.request_resources("p1", {
            "cpu": 3,
            "memory": 3,
            "disk": 3,
            "network": 3
        })
        
        self.assertTrue(result)
        
        # Check allocation
        self.assertEqual(self.banker.allocation["p1"]["cpu"], 3)
        self.assertEqual(self.banker.allocation["p1"]["memory"], 3)
        self.assertEqual(self.banker.allocation["p1"]["disk"], 3)
        self.assertEqual(self.banker.allocation["p1"]["network"], 3)
        
        # Check need
        self.assertEqual(self.banker.need["p1"]["cpu"], 2)
        self.assertEqual(self.banker.need["p1"]["memory"], 2)
        self.assertEqual(self.banker.need["p1"]["disk"], 2)
        self.assertEqual(self.banker.need["p1"]["network"], 2)
        
        # Check available
        self.assertEqual(self.banker.available["cpu"], 7)
        self.assertEqual(self.banker.available["memory"], 7)
        self.assertEqual(self.banker.available["disk"], 7)
        self.assertEqual(self.banker.available["network"], 7)
        
    def test_release_resources(self):
        """Test resource release."""
        # Register a process
        self.banker.register_process("p1", {
            "cpu": 5,
            "memory": 5,
            "disk": 5,
            "network": 5
        })
        
        # Request resources
        self.banker.request_resources("p1", {
            "cpu": 3,
            "memory": 3,
            "disk": 3,
            "network": 3
        })
        
        # Release resources
        result = self.banker.release_resources("p1", {
            "cpu": 2,
            "memory": 2,
            "disk": 2,
            "network": 2
        })
        
        self.assertTrue(result)
        
        # Check allocation
        self.assertEqual(self.banker.allocation["p1"]["cpu"], 1)
        self.assertEqual(self.banker.allocation["p1"]["memory"], 1)
        self.assertEqual(self.banker.allocation["p1"]["disk"], 1)
        self.assertEqual(self.banker.allocation["p1"]["network"], 1)
        
        # Check need
        self.assertEqual(self.banker.need["p1"]["cpu"], 4)
        self.assertEqual(self.banker.need["p1"]["memory"], 4)
        self.assertEqual(self.banker.need["p1"]["disk"], 4)
        self.assertEqual(self.banker.need["p1"]["network"], 4)
        
        # Check available
        self.assertEqual(self.banker.available["cpu"], 9)
        self.assertEqual(self.banker.available["memory"], 9)
        self.assertEqual(self.banker.available["disk"], 9)
        self.assertEqual(self.banker.available["network"], 9)
        
    def test_deadlock_prevention(self):
        """Test deadlock prevention."""
        # Register processes
        self.banker.register_process("p1", {
            "cpu": 7,
            "memory": 5,
            "disk": 3,
            "network": 5
        })
        
        self.banker.register_process("p2", {
            "cpu": 3,
            "memory": 2,
            "disk": 2,
            "network": 3
        })
        
        # Allocate resources to p1
        self.banker.request_resources("p1", {
            "cpu": 2,
            "memory": 1,
            "disk": 1,
            "network": 1
        })
        
        # Allocate resources to p2
        self.banker.request_resources("p2", {
            "cpu": 1,
            "memory": 1,
            "disk": 1,
            "network": 1
        })
        
        # Try to allocate more resources to p1
        result = self.banker.request_resources("p1", {
            "cpu": 5,
            "memory": 4,
            "disk": 2,
            "network": 4
        })
        
        # This should fail because it would lead to deadlock
        self.assertFalse(result)
        
        # Check that allocations haven't changed
        self.assertEqual(self.banker.allocation["p1"]["cpu"], 2)
        self.assertEqual(self.banker.allocation["p1"]["memory"], 1)
        self.assertEqual(self.banker.allocation["p1"]["disk"], 1)
        self.assertEqual(self.banker.allocation["p1"]["network"], 1)
        
        # Try a safe allocation to p2
        result = self.banker.request_resources("p2", {
            "cpu": 1,
            "memory": 1,
            "disk": 1,
            "network": 1
        })
        
        # This should succeed
        self.assertTrue(result)
        
        # Check updated allocations
        self.assertEqual(self.banker.allocation["p2"]["cpu"], 2)
        self.assertEqual(self.banker.allocation["p2"]["memory"], 2)
        self.assertEqual(self.banker.allocation["p2"]["disk"], 2)
        self.assertEqual(self.banker.allocation["p2"]["network"], 2)
        
    def test_remove_process(self):
        """Test process removal."""
        # Register a process
        self.banker.register_process("p1", {
            "cpu": 5,
            "memory": 5,
            "disk": 5,
            "network": 5
        })
        
        # Request resources
        self.banker.request_resources("p1", {
            "cpu": 3,
            "memory": 3,
            "disk": 3,
            "network": 3
        })
        
        # Remove process
        result = self.banker.remove_process("p1")
        
        self.assertTrue(result)
        self.assertNotIn("p1", self.banker.max_claim)
        self.assertNotIn("p1", self.banker.allocation)
        self.assertNotIn("p1", self.banker.need)
        
        # Check available resources
        self.assertEqual(self.banker.available["cpu"], 10)
        self.assertEqual(self.banker.available["memory"], 10)
        self.assertEqual(self.banker.available["disk"], 10)
        self.assertEqual(self.banker.available["network"], 10)


if __name__ == "__main__":
    unittest.main()
