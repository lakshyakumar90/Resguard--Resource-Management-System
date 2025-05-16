"""
Alerting System Module

This module provides functionality to monitor resource usage and generate
alerts when thresholds are exceeded.
"""

import time
import threading
import logging
import uuid
from typing import Dict, List, Any, Optional

from utils.config import Config
from utils.system_monitor import SystemMonitor
from core.resource_manager import ResourceManager


class AlertingSystem:
    """
    Monitors resource usage and generates alerts when thresholds are exceeded.
    
    This class implements a configurable alerting system with console notifications.
    """
    
    def __init__(self, resource_manager: ResourceManager, system_monitor: SystemMonitor, config: Config):
        """
        Initialize the alerting system.
        
        Args:
            resource_manager: Resource manager instance
            system_monitor: System monitor instance
            config: Configuration object
        """
        self.resource_manager = resource_manager
        self.system_monitor = system_monitor
        self.config = config
        
        # Thread management
        self.lock = threading.RLock()
        self.running = False
        self.alert_thread = None
        
        # Alert history
        self.alert_history = []
        
        # Last alert time for cooldown
        self.last_alert_time = {
            "cpu": 0,
            "memory": 0,
            "disk": 0,
            "network": 0
        }
        
        # Set up logging
        self.logger = logging.getLogger("alerting_system")
        self.logger.setLevel(logging.INFO)
        
        # Load configuration
        self.enabled = config.get("alerting", "enabled") if config.get("alerting", "enabled") is not None else True
        
        # Set default thresholds if not in config
        default_thresholds = {
            "cpu": {"warning": 70, "critical": 90},
            "memory": {"warning": 70, "critical": 90},
            "disk": {"warning": 70, "critical": 90},
            "network": {"warning": 70, "critical": 90}
        }
        self.thresholds = config.get("alerting", "thresholds") if config.get("alerting", "thresholds") is not None else default_thresholds
        
        # Set default cooldown period if not in config
        self.cooldown_period = config.get("alerting", "cooldown_period") if config.get("alerting", "cooldown_period") is not None else 300  # seconds
        
    def start(self):
        """Start the alerting system."""
        if not self.enabled:
            self.logger.info("Alerting system is disabled in configuration")
            return
            
        with self.lock:
            if self.running:
                return
                
            self.running = True
            self.alert_thread = threading.Thread(target=self._alert_loop, daemon=True)
            self.alert_thread.start()
            self.logger.info("Alerting system started")
            
    def stop(self):
        """Stop the alerting system."""
        with self.lock:
            self.running = False
            if self.alert_thread:
                self.alert_thread.join(timeout=1.0)
                self.alert_thread = None
            self.logger.info("Alerting system stopped")
            
    def get_alert_history(self) -> List[Dict]:
        """
        Get the alert history.
        
        Returns:
            List[Dict]: History of alerts
        """
        with self.lock:
            return self.alert_history.copy()
            
    def _alert_loop(self):
        """Background thread for checking alerts."""
        while self.running:
            try:
                self._check_alerts()
            except Exception as e:
                self.logger.error(f"Error checking alerts: {e}")
                
            # Sleep for a short time
            time.sleep(10)  # Check every 10 seconds
            
    def _check_alerts(self):
        """Check for alert conditions."""
        with self.lock:
            # Get current metrics
            metrics = self.system_monitor.get_metrics()
            current_time = time.time()
            
            # Check each resource type
            for resource in ["cpu", "memory", "disk"]:
                # Skip if in cooldown period
                if current_time - self.last_alert_time[resource] < self.cooldown_period:
                    continue
                    
                # Get current usage percentage
                usage_percent = metrics[resource]["percent"]
                
                # Check against thresholds
                if resource in self.thresholds:
                    # Check critical threshold
                    if "critical" in self.thresholds[resource] and usage_percent >= self.thresholds[resource]["critical"]:
                        self._generate_alert(resource, "critical", usage_percent, self.thresholds[resource]["critical"])
                        self.last_alert_time[resource] = current_time
                    # Check warning threshold
                    elif "warning" in self.thresholds[resource] and usage_percent >= self.thresholds[resource]["warning"]:
                        self._generate_alert(resource, "warning", usage_percent, self.thresholds[resource]["warning"])
                        self.last_alert_time[resource] = current_time
                        
    def _generate_alert(self, resource: str, severity: str, current_value: float, threshold: float):
        """
        Generate an alert.
        
        Args:
            resource: Resource type
            severity: Alert severity (warning, critical)
            current_value: Current resource usage
            threshold: Threshold that was exceeded
        """
        # Create alert
        alert = {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "resource": resource,
            "severity": severity,
            "current_value": current_value,
            "threshold": threshold,
            "message": f"{severity.upper()} alert: {resource} usage at {current_value:.1f}% (threshold: {threshold}%)"
        }
        
        # Add to history
        self.alert_history.append(alert)
        
        # Keep history limited to last 100 alerts
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
            
        # Log the alert
        self.logger.warning(f"Alert generated: {alert['message']}")
        
        # Send notification
        self._send_alert_notifications(alert)
        
    def _send_alert_notifications(self, alert: Dict):
        """
        Send notifications for an alert.
        
        Args:
            alert: Alert information
        """
        # Prepare alert message
        resource = alert["resource"]
        severity = alert["severity"]
        value = alert["current_value"]
        threshold = alert["threshold"]
        
        subject = f"ResGuard {severity.upper()} Alert: {resource} usage at {value:.1f}%"
        message = f"""
        ResGuard Alert
        --------------
        Resource: {resource}
        Severity: {severity.upper()}
        Current Value: {value:.1f}%
        Threshold: {threshold}%
        Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Send to console
        self._send_console_notification(subject, message)
        
    def _send_console_notification(self, subject: str, message: str):
        """
        Send a notification to the console.
        
        Args:
            subject: Alert subject
            message: Alert message
        """
        print("\n" + "=" * 80)
        print(f"ALERT: {subject}")
        print("-" * 80)
        print(message)
        print("=" * 80 + "\n")
