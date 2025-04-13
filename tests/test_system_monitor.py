"""
Tests for the System Monitor implementation.
"""

import unittest
import time
from utils.system_monitor import SystemMonitor


class TestSystemMonitor(unittest.TestCase):
    """Test cases for the System Monitor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = SystemMonitor(update_interval=0.1)
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.monitor.shutdown()
        
    def test_get_metrics(self):
        """Test getting system metrics."""
        # Wait for initial metrics to be collected
        time.sleep(0.2)
        
        # Get metrics
        metrics = self.monitor.get_metrics()
        
        # Check metrics structure
        self.assertIn("cpu", metrics)
        self.assertIn("memory", metrics)
        self.assertIn("disk", metrics)
        self.assertIn("network", metrics)
        self.assertIn("timestamp", metrics)
        
        # Check CPU metrics
        self.assertIn("percent", metrics["cpu"])
        self.assertIn("per_cpu", metrics["cpu"])
        self.assertIn("count", metrics["cpu"])
        
        # Check memory metrics
        self.assertIn("total", metrics["memory"])
        self.assertIn("available", metrics["memory"])
        self.assertIn("percent", metrics["memory"])
        self.assertIn("used", metrics["memory"])
        
        # Check disk metrics
        self.assertIn("total", metrics["disk"])
        self.assertIn("used", metrics["disk"])
        self.assertIn("free", metrics["disk"])
        self.assertIn("percent", metrics["disk"])
        
        # Check network metrics
        self.assertIn("bytes_sent", metrics["network"])
        self.assertIn("bytes_recv", metrics["network"])
        self.assertIn("packets_sent", metrics["network"])
        self.assertIn("packets_recv", metrics["network"])
        
    def test_get_history(self):
        """Test getting metrics history."""
        # Wait for history to be collected
        time.sleep(0.5)
        
        # Get history
        history = self.monitor.get_history()
        
        # Check history structure
        self.assertIn("cpu", history)
        self.assertIn("memory", history)
        self.assertIn("disk", history)
        self.assertIn("network", history)
        self.assertIn("timestamps", history)
        
        # Check history has data
        self.assertGreater(len(history["timestamps"]), 0)
        self.assertEqual(len(history["cpu"]), len(history["timestamps"]))
        self.assertEqual(len(history["memory"]), len(history["timestamps"]))
        self.assertEqual(len(history["disk"]), len(history["timestamps"]))
        self.assertEqual(len(history["network"]), len(history["timestamps"]))
        
    def test_get_processes(self):
        """Test getting process information."""
        # Get processes
        processes = self.monitor.get_processes()
        
        # Check processes structure
        self.assertGreater(len(processes), 0)
        
        # Check first process
        process = processes[0]
        self.assertIn("pid", process)
        self.assertIn("name", process)
        self.assertIn("username", process)
        self.assertIn("cpu_percent", process)
        self.assertIn("memory_percent", process)
        
        # Check sorting
        cpu_sorted = self.monitor.get_processes(sort_by="cpu")
        if len(cpu_sorted) > 1:
            self.assertGreaterEqual(cpu_sorted[0]["cpu_percent"], cpu_sorted[1]["cpu_percent"])
            
        memory_sorted = self.monitor.get_processes(sort_by="memory")
        if len(memory_sorted) > 1:
            self.assertGreaterEqual(memory_sorted[0]["memory_percent"], memory_sorted[1]["memory_percent"])
            
    def test_history_limit(self):
        """Test history size limit."""
        # Set a small max_history
        self.monitor.max_history = 5
        
        # Wait for more than max_history updates
        time.sleep(1.0)
        
        # Get history
        history = self.monitor.get_history()
        
        # Check history size is limited
        self.assertLessEqual(len(history["timestamps"]), 5)
        self.assertLessEqual(len(history["cpu"]), 5)
        self.assertLessEqual(len(history["memory"]), 5)
        self.assertLessEqual(len(history["disk"]), 5)
        self.assertLessEqual(len(history["network"]), 5)


if __name__ == "__main__":
    unittest.main()
