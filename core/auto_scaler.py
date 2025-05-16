"""
Auto-Scaler Module

This module provides functionality to automatically adjust resource allocations
based on demand and configured policies.
"""

import time
import threading
import logging
from typing import Dict, List

from utils.config import Config
from utils.system_monitor import SystemMonitor
from core.resource_manager import ResourceManager


class AutoScaler:
    """
    Automatically adjusts resource allocations based on demand and policies.
    
    This class implements reactive scaling to optimize resource allocation
    by monitoring CPU and memory usage.
    """
    
    def __init__(self, resource_manager: ResourceManager, system_monitor: SystemMonitor, 
                predictive_analyzer=None, config: Config=None):
        """
        Initialize the auto-scaler.
        
        Args:
            resource_manager: Resource manager instance
            system_monitor: System monitor instance
            predictive_analyzer: Predictive analyzer instance (not used in this simplified version)
            config: Configuration object
        """
        # Core components
        self.resource_manager = resource_manager
        self.system_monitor = system_monitor
        self.config = config
        
        # Thread management
        self.lock = threading.RLock()
        self.running = False
        self.scaling_thread = None
        
        # Scaling history
        self.scaling_history = []
        
        # Last scaling time for cooldown
        self.last_scaling_time = {
            "cpu": 0,
            "memory": 0
        }
        
        # Set up logging
        self.logger = logging.getLogger("auto_scaler")
        self.logger.setLevel(logging.INFO)
        
        # Load configuration with defaults if not specified
        if self.config:
            self.enabled = config.get("auto_scaling", "enabled") if config.get("auto_scaling", "enabled") is not None else True
            self.check_interval = config.get("auto_scaling", "check_interval") if config.get("auto_scaling", "check_interval") is not None else 60  # seconds
            self.cooldown_period = config.get("auto_scaling", "cooldown_period") if config.get("auto_scaling", "cooldown_period") is not None else 300  # seconds
            self.scale_up_threshold = config.get("auto_scaling", "scale_up_threshold") if config.get("auto_scaling", "scale_up_threshold") is not None else 80  # percent
            self.scale_down_threshold = config.get("auto_scaling", "scale_down_threshold") if config.get("auto_scaling", "scale_down_threshold") is not None else 30  # percent
            self.scale_up_amount = config.get("auto_scaling", "scale_up_amount") if config.get("auto_scaling", "scale_up_amount") is not None else 10  # units
            self.scale_down_amount = config.get("auto_scaling", "scale_down_amount") if config.get("auto_scaling", "scale_down_amount") is not None else 5  # units
        else:
            # Default values if no config is provided
            self.enabled = True
            self.check_interval = 60  # seconds
            self.cooldown_period = 300  # seconds
            self.scale_up_threshold = 80  # percent
            self.scale_down_threshold = 30  # percent
            self.scale_up_amount = 10  # units
            self.scale_down_amount = 5  # units
            
        # This simplified version only supports reactive mode
        self.mode = "reactive"
        
    def start(self):
        """Start the auto-scaler."""
        if not self.enabled:
            self.logger.info("Auto-scaler is disabled in configuration")
            return
            
        with self.lock:
            if self.running:
                return
                
            self.running = True
            self.scaling_thread = threading.Thread(target=self._scaling_loop, daemon=True)
            self.scaling_thread.start()
            self.logger.info("Auto-scaler started in reactive mode")
            
    def stop(self):
        """Stop the auto-scaler."""
        with self.lock:
            self.running = False
            if self.scaling_thread:
                self.scaling_thread.join(timeout=1.0)
                self.scaling_thread = None
            self.logger.info("Auto-scaler stopped")
            
    def get_scaling_history(self) -> List[Dict]:
        """
        Get the scaling action history.
        
        Returns:
            List[Dict]: History of scaling actions
        """
        with self.lock:
            return self.scaling_history.copy()
            
    def _scaling_loop(self):
        """Background thread for scaling resources."""
        while self.running:
            try:
                # Perform reactive scaling based on current usage
                self._reactive_scaling()
            except Exception as e:
                self.logger.error(f"Error in scaling loop: {e}")
                
            # Sleep until next check
            time.sleep(self.check_interval)
            
    def _reactive_scaling(self):
        """Implement reactive scaling based on current usage."""
        with self.lock:
            # Get current system metrics
            metrics = self.system_monitor.get_metrics()
            
            # Check CPU and memory resources
            for resource in ["cpu", "memory"]:
                # Skip if in cooldown period
                current_time = time.time()
                if current_time - self.last_scaling_time[resource] < self.cooldown_period:
                    continue
                    
                # Get current usage percentage
                usage_percent = metrics[resource]["percent"]
                
                # Simple decision logic:
                # If usage is above threshold, scale up
                # If usage is below threshold, scale down
                if usage_percent > self.scale_up_threshold:
                    self._scale_up(resource, usage_percent)
                    self.last_scaling_time[resource] = current_time
                elif usage_percent < self.scale_down_threshold:
                    self._scale_down(resource, usage_percent)
                    self.last_scaling_time[resource] = current_time
                
    def _scale_up(self, resource: str, usage_percent: float = 0,
                 predictive: bool = False, scheduled: bool = False,
                 scale_amount: int = None):
        """
        Scale up a resource by a fixed amount.
        
        Args:
            resource: Resource type to scale (cpu or memory)
            usage_percent: Current usage percentage (not used in simplified version)
            predictive: Whether this is a predictive scaling action (not used)
            scheduled: Whether this is a scheduled scaling action (not used)
            scale_amount: Optional specific amount to scale by
        """
        # Get current total resource amount
        total_resource = 100  # Default value
        if self.config:
            config_resource = self.config.get("resources", resource)
            if config_resource is not None:
                total_resource = config_resource
        
        # Use provided scale amount or default
        amount_to_add = scale_amount if scale_amount is not None else self.scale_up_amount
        
        # Add amount
        new_total = total_resource + amount_to_add
        
        # Update configuration if config is available
        if self.config:
            self.config.set("resources", resource, new_total)
            self.config.save()
        
        # Log the scaling action
        action_type = "predictive" if predictive else ("scheduled" if scheduled else "reactive")
        self.logger.info(f"{action_type.capitalize()} scale up: {resource} +{amount_to_add} units (to {new_total})")
        
        # Record in history
        self.scaling_history.append({
            "timestamp": time.time(),
            "action": "scale_up",
            "resource": resource,
            "amount": amount_to_add,
            "type": action_type,
            "usage_percent": usage_percent,
            "new_total": new_total
        })
        
        # Keep history limited to last 50 actions
        if len(self.scaling_history) > 50:
            self.scaling_history = self.scaling_history[-50:]
            
    def _scale_down(self, resource: str, usage_percent: float = 0,
                   predictive: bool = False, scheduled: bool = False,
                   scale_amount: int = None):
        """
        Scale down a resource by a fixed amount.
        
        Args:
            resource: Resource type to scale (cpu or memory)
            usage_percent: Current usage percentage (not used in simplified version)
            predictive: Whether this is a predictive scaling action (not used)
            scheduled: Whether this is a scheduled scaling action (not used)
            scale_amount: Optional specific amount to scale by
        """
        # Get current total resource amount
        total_resource = 100  # Default value
        if self.config:
            config_resource = self.config.get("resources", resource)
            if config_resource is not None:
                total_resource = config_resource
        
        # Use provided scale amount or default
        amount_to_remove = scale_amount if scale_amount is not None else self.scale_down_amount
        
        # Calculate new total (ensure we don't go below minimum)
        min_resource = 10  # Minimum resource units
        new_total = max(min_resource, total_resource - amount_to_remove)
        
        # Skip if no change
        if new_total == total_resource:
            return
            
        # Update configuration if config is available
        if self.config:
            self.config.set("resources", resource, new_total)
            self.config.save()
        
        # Log the scaling action
        action_type = "predictive" if predictive else ("scheduled" if scheduled else "reactive")
        self.logger.info(f"{action_type.capitalize()} scale down: {resource} -{amount_to_remove} units (to {new_total})")
        
        # Record in history
        self.scaling_history.append({
            "timestamp": time.time(),
            "action": "scale_down",
            "resource": resource,
            "amount": amount_to_remove,
            "type": action_type,
            "usage_percent": usage_percent,
            "new_total": new_total
        })
        
        # Keep history limited to last 50 actions
        if len(self.scaling_history) > 50:
            self.scaling_history = self.scaling_history[-50:]
