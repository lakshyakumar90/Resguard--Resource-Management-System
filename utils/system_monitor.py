"""
System Monitor Module

This module provides functionality to monitor system resources
using psutil and provides real-time metrics.
"""

import psutil
import time
import threading
from typing import Dict, List, Callable, Any, Optional


class SystemMonitor:
    """
    Monitors system resources and provides real-time metrics.
    
    This class uses psutil to collect information about CPU, memory,
    disk, and network usage, and provides methods to access this data.
    """
    
    def __init__(self, update_interval: float = 1.0):
        """
        Initialize the system monitor.
        
        Args:
            update_interval: Time between updates in seconds
        """
        self.update_interval = update_interval
        self.lock = threading.RLock()
        self.running = True
        
        # Initialize metrics
        self.metrics = {
            "cpu": {
                "percent": 0.0,
                "per_cpu": [],
                "count": psutil.cpu_count()
            },
            "memory": {
                "total": 0,
                "available": 0,
                "percent": 0.0,
                "used": 0
            },
            "disk": {
                "total": 0,
                "used": 0,
                "free": 0,
                "percent": 0.0
            },
            "network": {
                "bytes_sent": 0,
                "bytes_recv": 0,
                "packets_sent": 0,
                "packets_recv": 0
            },
            "timestamp": 0
        }
        
        # History of metrics
        self.history = {
            "cpu": [],
            "memory": [],
            "disk": [],
            "network": [],
            "timestamps": []
        }
        
        # Maximum history length
        self.max_history = 60  # 1 minute at 1 second intervals
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def _monitor_loop(self) -> None:
        """Background thread for continuous monitoring."""
        while self.running:
            self._update_metrics()
            time.sleep(self.update_interval)
            
    def _update_metrics(self) -> None:
        """Update all system metrics."""
        with self.lock:
            # Update CPU metrics
            self.metrics["cpu"]["percent"] = psutil.cpu_percent()
            self.metrics["cpu"]["per_cpu"] = psutil.cpu_percent(percpu=True)
            
            # Update memory metrics
            mem = psutil.virtual_memory()
            self.metrics["memory"]["total"] = mem.total
            self.metrics["memory"]["available"] = mem.available
            self.metrics["memory"]["used"] = mem.used
            self.metrics["memory"]["percent"] = mem.percent
            
            # Update disk metrics
            disk = psutil.disk_usage('/')
            self.metrics["disk"]["total"] = disk.total
            self.metrics["disk"]["used"] = disk.used
            self.metrics["disk"]["free"] = disk.free
            self.metrics["disk"]["percent"] = disk.percent
            
            # Update network metrics
            net = psutil.net_io_counters()
            self.metrics["network"]["bytes_sent"] = net.bytes_sent
            self.metrics["network"]["bytes_recv"] = net.bytes_recv
            self.metrics["network"]["packets_sent"] = net.packets_sent
            self.metrics["network"]["packets_recv"] = net.packets_recv
            
            # Update timestamp
            self.metrics["timestamp"] = time.time()
            
            # Update history
            self.history["cpu"].append(self.metrics["cpu"]["percent"])
            self.history["memory"].append(self.metrics["memory"]["percent"])
            self.history["disk"].append(self.metrics["disk"]["percent"])
            self.history["network"].append({
                "sent": self.metrics["network"]["bytes_sent"],
                "recv": self.metrics["network"]["bytes_recv"]
            })
            self.history["timestamps"].append(self.metrics["timestamp"])
            
            # Trim history if needed
            if len(self.history["timestamps"]) > self.max_history:
                self.history["cpu"] = self.history["cpu"][-self.max_history:]
                self.history["memory"] = self.history["memory"][-self.max_history:]
                self.history["disk"] = self.history["disk"][-self.max_history:]
                self.history["network"] = self.history["network"][-self.max_history:]
                self.history["timestamps"] = self.history["timestamps"][-self.max_history:]
                
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get the current system metrics.
        
        Returns:
            Dict: Current system metrics
        """
        with self.lock:
            return self.metrics.copy()
            
    def get_history(self) -> Dict[str, List]:
        """
        Get the history of system metrics.
        
        Returns:
            Dict: History of system metrics
        """
        with self.lock:
            return self.history.copy()
            
    def get_processes(self, sort_by: str = "cpu") -> List[Dict[str, Any]]:
        """
        Get information about running processes.
        
        Args:
            sort_by: Field to sort by (cpu, memory)
            
        Returns:
            List[Dict]: List of process information
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                processes.append({
                    "pid": pinfo["pid"],
                    "name": pinfo["name"],
                    "username": pinfo["username"],
                    "cpu_percent": pinfo["cpu_percent"] or 0.0,
                    "memory_percent": pinfo["memory_percent"] or 0.0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        # Sort processes
        if sort_by == "cpu":
            processes.sort(key=lambda p: p["cpu_percent"], reverse=True)
        elif sort_by == "memory":
            processes.sort(key=lambda p: p["memory_percent"], reverse=True)
            
        return processes[:50]  # Return top 50 processes
        
    def shutdown(self) -> None:
        """Shutdown the system monitor."""
        self.running = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
