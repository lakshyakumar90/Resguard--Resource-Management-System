"""
Tests for the Resource Manager implementation.
"""

import unittest
import os
import json
import time
from core.resource_manager import ResourceManager


class TestResourceManager(unittest.TestCase):
    """Test cases for the Resource Manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize with available resources
        self.available_resources = {
            "cpu": 10,
            "memory": 10,
            "disk": 10,
            "network": 10
        }
        
        # Use a test state file
        self.state_file = "test_state.json"
        
        # Remove test state file if it exists
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
            
        self.resource_manager = ResourceManager(self.available_resources, self.state_file)
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Shutdown resource manager
        self.resource_manager.shutdown()
        
        # Remove test state file
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
            
    def test_register_process(self):
        """Test process registration."""
        # Register a process
        result = self.resource_manager.register_process("p1", {
            "cpu": 5,
            "memory": 5,
            "disk": 5,
            "network": 5
        })
        
        self.assertTrue(result)
        
        # Check process info
        state = self.resource_manager.get_system_state()
        self.assertIn("p1", state["process_info"])
        self.assertEqual(state["process_info"]["p1"]["status"], "registered")
        
    def test_request_resources(self):
        """Test resource request."""
        # Register a process
        self.resource_manager.register_process("p1", {
            "cpu": 5,
            "memory": 5,
            "disk": 5,
            "network": 5
        })
        
        # Request resources
        result = self.resource_manager.request_resources("p1", {
            "cpu": 3,
            "memory": 3,
            "disk": 3,
            "network": 3
        })
        
        self.assertTrue(result)
        
        # Check allocation
        state = self.resource_manager.get_system_state()
        self.assertEqual(state["allocation"]["p1"]["cpu"], 3)
        self.assertEqual(state["allocation"]["p1"]["memory"], 3)
        self.assertEqual(state["allocation"]["p1"]["disk"], 3)
        self.assertEqual(state["allocation"]["p1"]["network"], 3)
        
        # Check process status
        self.assertEqual(state["process_info"]["p1"]["status"], "running")
        
    def test_release_resources(self):
        """Test resource release."""
        # Register a process
        self.resource_manager.register_process("p1", {
            "cpu": 5,
            "memory": 5,
            "disk": 5,
            "network": 5
        })
        
        # Request resources
        self.resource_manager.request_resources("p1", {
            "cpu": 3,
            "memory": 3,
            "disk": 3,
            "network": 3
        })
        
        # Release resources
        result = self.resource_manager.release_resources("p1", {
            "cpu": 2,
            "memory": 2,
            "disk": 2,
            "network": 2
        })
        
        self.assertTrue(result)
        
        # Check allocation
        state = self.resource_manager.get_system_state()
        self.assertEqual(state["allocation"]["p1"]["cpu"], 1)
        self.assertEqual(state["allocation"]["p1"]["memory"], 1)
        self.assertEqual(state["allocation"]["p1"]["disk"], 1)
        self.assertEqual(state["allocation"]["p1"]["network"], 1)
        
    def test_remove_process(self):
        """Test process removal."""
        # Register a process
        self.resource_manager.register_process("p1", {
            "cpu": 5,
            "memory": 5,
            "disk": 5,
            "network": 5
        })
        
        # Request resources
        self.resource_manager.request_resources("p1", {
            "cpu": 3,
            "memory": 3,
            "disk": 3,
            "network": 3
        })
        
        # Remove process
        result = self.resource_manager.remove_process("p1")
        
        self.assertTrue(result)
        
        # Check process is removed
        state = self.resource_manager.get_system_state()
        self.assertNotIn("p1", state["allocation"])
        self.assertNotIn("p1", state["process_info"])
        
        # Check available resources
        self.assertEqual(state["available"]["cpu"], 10)
        self.assertEqual(state["available"]["memory"], 10)
        self.assertEqual(state["available"]["disk"], 10)
        self.assertEqual(state["available"]["network"], 10)
        
    def test_save_load_state(self):
        """Test state persistence."""
        # Register a process
        self.resource_manager.register_process("p1", {
            "cpu": 5,
            "memory": 5,
            "disk": 5,
            "network": 5
        })
        
        # Request resources
        self.resource_manager.request_resources("p1", {
            "cpu": 3,
            "memory": 3,
            "disk": 3,
            "network": 3
        })
        
        # Save state
        self.resource_manager.save_state()
        
        # Create a new resource manager
        new_manager = ResourceManager(self.available_resources, self.state_file)
        
        # Load state
        new_manager.load_state()
        
        # Check state is loaded correctly
        state = new_manager.get_system_state()
        self.assertIn("p1", state["allocation"])
        self.assertEqual(state["allocation"]["p1"]["cpu"], 3)
        self.assertEqual(state["allocation"]["p1"]["memory"], 3)
        self.assertEqual(state["allocation"]["p1"]["disk"], 3)
        self.assertEqual(state["allocation"]["p1"]["network"], 3)
        
        # Shutdown new manager
        new_manager.shutdown()
        
    def test_request_history(self):
        """Test request history logging."""
        # Register a process
        self.resource_manager.register_process("p1", {
            "cpu": 5,
            "memory": 5,
            "disk": 5,
            "network": 5
        })
        
        # Request resources
        self.resource_manager.request_resources("p1", {
            "cpu": 3,
            "memory": 3,
            "disk": 3,
            "network": 3
        })
        
        # Release resources
        self.resource_manager.release_resources("p1", {
            "cpu": 1,
            "memory": 1,
            "disk": 1,
            "network": 1
        })
        
        # Check request history
        state = self.resource_manager.get_system_state()
        history = state["request_history"]
        
        self.assertEqual(len(history), 3)  # register, request, release
        
        # Check register event
        self.assertEqual(history[0]["type"], "register")
        self.assertEqual(history[0]["process_id"], "p1")
        
        # Check request event
        self.assertEqual(history[1]["type"], "request")
        self.assertEqual(history[1]["process_id"], "p1")
        self.assertEqual(history[1]["resources"]["cpu"], 3)
        
        # Check release event
        self.assertEqual(history[2]["type"], "release")
        self.assertEqual(history[2]["process_id"], "p1")
        self.assertEqual(history[2]["resources"]["cpu"], 1)


if __name__ == "__main__":
    unittest.main()
