"""
Tests for the Configuration Manager.
"""

import unittest
import os
import json
from utils.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for the Configuration Manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a test config file
        self.config_file = "test_config.json"
        
        # Remove test config file if it exists
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
            
        # Create config manager
        self.config = Config(self.config_file)
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove test config file
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
            
    def test_default_config(self):
        """Test default configuration."""
        # Check default values
        self.assertEqual(self.config.get("system", "state_dir"), "states")
        self.assertEqual(self.config.get("resources", "cpu"), 100)
        self.assertEqual(self.config.get("desktop_app", "title"), "ResGuard Resource Manager")
        self.assertEqual(self.config.get("web_dashboard", "port"), 5000)
        self.assertEqual(self.config.get("security", "enable_authentication"), True)
        self.assertEqual(self.config.get("logging", "level"), "INFO")
        
    def test_set_get(self):
        """Test setting and getting configuration values."""
        # Set values
        self.config.set("system", "state_dir", "custom_states")
        self.config.set("resources", "cpu", 200)
        self.config.set("desktop_app", "title", "Custom Title")
        self.config.set("web_dashboard", "port", 8080)
        self.config.set("security", "enable_authentication", False)
        self.config.set("logging", "level", "DEBUG")
        
        # Check values
        self.assertEqual(self.config.get("system", "state_dir"), "custom_states")
        self.assertEqual(self.config.get("resources", "cpu"), 200)
        self.assertEqual(self.config.get("desktop_app", "title"), "Custom Title")
        self.assertEqual(self.config.get("web_dashboard", "port"), 8080)
        self.assertEqual(self.config.get("security", "enable_authentication"), False)
        self.assertEqual(self.config.get("logging", "level"), "DEBUG")
        
    def test_save_load(self):
        """Test saving and loading configuration."""
        # Set values
        self.config.set("system", "state_dir", "custom_states")
        self.config.set("resources", "cpu", 200)
        
        # Save config
        self.assertTrue(self.config.save())
        
        # Create new config manager
        new_config = Config(self.config_file)
        
        # Check values
        self.assertEqual(new_config.get("system", "state_dir"), "custom_states")
        self.assertEqual(new_config.get("resources", "cpu"), 200)
        
    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults."""
        # Set values
        self.config.set("system", "state_dir", "custom_states")
        self.config.set("resources", "cpu", 200)
        
        # Reset to defaults
        self.assertTrue(self.config.reset_to_defaults())
        
        # Check values
        self.assertEqual(self.config.get("system", "state_dir"), "states")
        self.assertEqual(self.config.get("resources", "cpu"), 100)
        
    def test_reset_section(self):
        """Test resetting a section to defaults."""
        # Set values
        self.config.set("system", "state_dir", "custom_states")
        self.config.set("resources", "cpu", 200)
        
        # Reset system section
        self.assertTrue(self.config.reset_section("system"))
        
        # Check values
        self.assertEqual(self.config.get("system", "state_dir"), "states")
        self.assertEqual(self.config.get("resources", "cpu"), 200)
        
    def test_validate(self):
        """Test configuration validation."""
        # Set invalid values
        self.config.set("system", "state_save_interval", -1)
        self.config.set("resources", "cpu", 0)
        self.config.set("desktop_app", "width", -100)
        self.config.set("web_dashboard", "port", 70000)
        
        # Validate
        errors = self.config.validate()
        
        # Check errors
        self.assertEqual(len(errors), 4)
        self.assertIn("System state_save_interval must be a positive number", errors)
        self.assertIn("Resource cpu must be a positive number", errors)
        self.assertIn("Desktop app width must be a positive integer", errors)
        self.assertIn("Web dashboard port must be a valid port number (1-65535)", errors)
        
    def test_get_settings_metadata(self):
        """Test getting settings metadata."""
        metadata = self.config.get_settings_metadata()
        
        # Check metadata structure
        self.assertIn("system", metadata)
        self.assertIn("resources", metadata)
        self.assertIn("desktop_app", metadata)
        self.assertIn("web_dashboard", metadata)
        self.assertIn("security", metadata)
        self.assertIn("logging", metadata)
        
        # Check field metadata
        cpu_field = next((f for f in metadata["resources"] if f["name"] == "cpu"), None)
        self.assertIsNotNone(cpu_field)
        self.assertEqual(cpu_field["type"], "number")
        self.assertEqual(cpu_field["label"], "CPU Units")
        self.assertIn("description", cpu_field)


if __name__ == "__main__":
    unittest.main()
