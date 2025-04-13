"""
Dashboard Module

This module provides the main dashboard for the ResGuard desktop application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from typing import Dict, Any, List, Optional

from core.resource_manager import ResourceManager
from utils.system_monitor import SystemMonitor


class Dashboard(ttk.Frame):
    """
    Main dashboard for the ResGuard desktop application.
    
    This class provides a UI for monitoring resource usage and
    managing resource allocations.
    """
    
    def __init__(self, parent, resource_manager: ResourceManager, 
                system_monitor: SystemMonitor, config: Any):
        """
        Initialize the dashboard.
        
        Args:
            parent: Parent widget
            resource_manager: Resource manager instance
            system_monitor: System monitor instance
            config: Configuration object
        """
        super().__init__(parent)
        self.parent = parent
        self.resource_manager = resource_manager
        self.system_monitor = system_monitor
        self.config = config
        
        # Refresh interval
        self.refresh_interval = config.get("desktop_app", "refresh_interval")
        
        # Create widgets
        self._create_widgets()
        
        # Start refresh timer
        self.after(int(self.refresh_interval * 1000), self._refresh_data)
        
    def _create_widgets(self):
        """Create and arrange widgets for the dashboard."""
        # Main container with two columns
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)
        
        # Left panel - System resources
        left_frame = ttk.LabelFrame(self, text="System Resources")
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Create system resource widgets
        self._create_system_resources(left_frame)
        
        # Right panel - Resource allocation
        right_frame = ttk.LabelFrame(self, text="Resource Allocation")
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Create resource allocation widgets
        self._create_resource_allocation(right_frame)
        
    def _create_system_resources(self, parent):
        """Create system resource monitoring widgets."""
        # Configure grid
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=0)  # CPU
        parent.rowconfigure(1, weight=0)  # Memory
        parent.rowconfigure(2, weight=0)  # Disk
        parent.rowconfigure(3, weight=0)  # Network
        parent.rowconfigure(4, weight=1)  # Process list
        
        # CPU usage
        cpu_frame = ttk.Frame(parent)
        cpu_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Label(cpu_frame, text="CPU Usage:").pack(side=tk.LEFT, padx=5)
        self.cpu_progress = ttk.Progressbar(cpu_frame, length=200, mode="determinate")
        self.cpu_progress.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.cpu_label = ttk.Label(cpu_frame, text="0%", width=5)
        self.cpu_label.pack(side=tk.LEFT, padx=5)
        
        # Memory usage
        mem_frame = ttk.Frame(parent)
        mem_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Label(mem_frame, text="Memory:").pack(side=tk.LEFT, padx=5)
        self.mem_progress = ttk.Progressbar(mem_frame, length=200, mode="determinate")
        self.mem_progress.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.mem_label = ttk.Label(mem_frame, text="0%", width=5)
        self.mem_label.pack(side=tk.LEFT, padx=5)
        
        # Disk usage
        disk_frame = ttk.Frame(parent)
        disk_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Label(disk_frame, text="Disk:").pack(side=tk.LEFT, padx=5)
        self.disk_progress = ttk.Progressbar(disk_frame, length=200, mode="determinate")
        self.disk_progress.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.disk_label = ttk.Label(disk_frame, text="0%", width=5)
        self.disk_label.pack(side=tk.LEFT, padx=5)
        
        # Network usage
        net_frame = ttk.Frame(parent)
        net_frame.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Label(net_frame, text="Network:").pack(side=tk.LEFT, padx=5)
        self.net_recv_label = ttk.Label(net_frame, text="↓ 0 KB/s")
        self.net_recv_label.pack(side=tk.LEFT, padx=5)
        self.net_sent_label = ttk.Label(net_frame, text="↑ 0 KB/s")
        self.net_sent_label.pack(side=tk.LEFT, padx=5)
        
        # Process list
        proc_frame = ttk.Frame(parent)
        proc_frame.grid(row=4, column=0, padx=5, pady=5, sticky="nsew")
        proc_frame.columnconfigure(0, weight=1)
        proc_frame.rowconfigure(0, weight=0)
        proc_frame.rowconfigure(1, weight=1)
        
        ttk.Label(proc_frame, text="Top Processes:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        # Create treeview for processes
        columns = ("pid", "name", "cpu", "memory")
        self.process_tree = ttk.Treeview(proc_frame, columns=columns, show="headings", height=10)
        
        # Define headings
        self.process_tree.heading("pid", text="PID")
        self.process_tree.heading("name", text="Name")
        self.process_tree.heading("cpu", text="CPU %")
        self.process_tree.heading("memory", text="Memory %")
        
        # Define columns
        self.process_tree.column("pid", width=50)
        self.process_tree.column("name", width=150)
        self.process_tree.column("cpu", width=60)
        self.process_tree.column("memory", width=60)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(proc_frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscroll=scrollbar.set)
        
        # Place widgets
        self.process_tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=5)
        
    def _create_resource_allocation(self, parent):
        """Create resource allocation widgets."""
        # Configure grid
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=0)  # Resource status
        parent.rowconfigure(1, weight=0)  # Request form
        parent.rowconfigure(2, weight=1)  # Allocation table
        
        # Resource status
        status_frame = ttk.LabelFrame(parent, text="Resource Status")
        status_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Create grid for resource status
        status_frame.columnconfigure(0, weight=0)
        status_frame.columnconfigure(1, weight=1)
        status_frame.columnconfigure(2, weight=0)
        
        # Resource labels
        resources = ["CPU", "Memory", "Disk", "Network"]
        self.resource_bars = {}
        self.resource_labels = {}
        
        for i, resource in enumerate(resources):
            ttk.Label(status_frame, text=f"{resource}:").grid(row=i, column=0, padx=5, pady=2, sticky="w")
            
            progress = ttk.Progressbar(status_frame, length=200, mode="determinate")
            progress.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            
            label = ttk.Label(status_frame, text="0/0", width=10)
            label.grid(row=i, column=2, padx=5, pady=2, sticky="e")
            
            self.resource_bars[resource.lower()] = progress
            self.resource_labels[resource.lower()] = label
            
        # Request form
        request_frame = ttk.LabelFrame(parent, text="Request Resources")
        request_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Process ID
        pid_frame = ttk.Frame(request_frame)
        pid_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(pid_frame, text="Process ID:").pack(side=tk.LEFT, padx=5)
        self.pid_entry = ttk.Entry(pid_frame)
        self.pid_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Resource entries
        resource_frame = ttk.Frame(request_frame)
        resource_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create grid for resource entries
        resource_frame.columnconfigure(0, weight=0)
        resource_frame.columnconfigure(1, weight=1)
        resource_frame.columnconfigure(2, weight=0)
        resource_frame.columnconfigure(3, weight=1)
        
        # CPU
        ttk.Label(resource_frame, text="CPU:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.cpu_entry = ttk.Entry(resource_frame, width=8)
        self.cpu_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        # Memory
        ttk.Label(resource_frame, text="Memory:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.memory_entry = ttk.Entry(resource_frame, width=8)
        self.memory_entry.grid(row=0, column=3, padx=5, pady=2, sticky="ew")
        
        # Disk
        ttk.Label(resource_frame, text="Disk:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.disk_entry = ttk.Entry(resource_frame, width=8)
        self.disk_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        # Network
        ttk.Label(resource_frame, text="Network:").grid(row=1, column=2, padx=5, pady=2, sticky="w")
        self.network_entry = ttk.Entry(resource_frame, width=8)
        self.network_entry.grid(row=1, column=3, padx=5, pady=2, sticky="ew")
        
        # Buttons
        button_frame = ttk.Frame(request_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Request", command=self._request_resources).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Release", command=self._release_resources).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove", command=self._remove_process).pack(side=tk.LEFT, padx=5)
        
        # Allocation table
        alloc_frame = ttk.LabelFrame(parent, text="Current Allocations")
        alloc_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        
        # Create treeview for allocations
        columns = ("process", "cpu", "memory", "disk", "network", "status")
        self.alloc_tree = ttk.Treeview(alloc_frame, columns=columns, show="headings")
        
        # Define headings
        self.alloc_tree.heading("process", text="Process ID")
        self.alloc_tree.heading("cpu", text="CPU")
        self.alloc_tree.heading("memory", text="Memory")
        self.alloc_tree.heading("disk", text="Disk")
        self.alloc_tree.heading("network", text="Network")
        self.alloc_tree.heading("status", text="Status")
        
        # Define columns
        self.alloc_tree.column("process", width=150)
        self.alloc_tree.column("cpu", width=60)
        self.alloc_tree.column("memory", width=60)
        self.alloc_tree.column("disk", width=60)
        self.alloc_tree.column("network", width=60)
        self.alloc_tree.column("status", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(alloc_frame, orient=tk.VERTICAL, command=self.alloc_tree.yview)
        self.alloc_tree.configure(yscroll=scrollbar.set)
        
        # Place widgets
        self.alloc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Bind double-click to fill request form
        self.alloc_tree.bind("<Double-1>", self._on_allocation_select)
        
    def _refresh_data(self):
        """Refresh dashboard data."""
        try:
            # Update system metrics
            self._update_system_metrics()
            
            # Update resource allocation
            self._update_resource_allocation()
            
            # Update process list
            self._update_process_list()
            
            # Schedule next refresh
            self.after(int(self.refresh_interval * 1000), self._refresh_data)
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing data: {e}")
            
    def _update_system_metrics(self):
        """Update system metrics display."""
        metrics = self.system_monitor.get_metrics()
        
        # Update CPU
        cpu_percent = metrics["cpu"]["percent"]
        self.cpu_progress["value"] = cpu_percent
        self.cpu_label["text"] = f"{cpu_percent:.1f}%"
        
        # Update Memory
        mem_percent = metrics["memory"]["percent"]
        self.mem_progress["value"] = mem_percent
        self.mem_label["text"] = f"{mem_percent:.1f}%"
        
        # Update Disk
        disk_percent = metrics["disk"]["percent"]
        self.disk_progress["value"] = disk_percent
        self.disk_label["text"] = f"{disk_percent:.1f}%"
        
        # Update Network
        # Calculate network speed (bytes per second)
        history = self.system_monitor.get_history()
        if len(history["network"]) >= 2:
            last = history["network"][-1]
            prev = history["network"][-2]
            last_time = history["timestamps"][-1]
            prev_time = history["timestamps"][-2]
            
            time_diff = last_time - prev_time
            if time_diff > 0:
                recv_speed = (last["recv"] - prev["recv"]) / time_diff / 1024  # KB/s
                sent_speed = (last["sent"] - prev["sent"]) / time_diff / 1024  # KB/s
                
                self.net_recv_label["text"] = f"↓ {recv_speed:.1f} KB/s"
                self.net_sent_label["text"] = f"↑ {sent_speed:.1f} KB/s"
                
    def _update_resource_allocation(self):
        """Update resource allocation display."""
        state = self.resource_manager.get_system_state()
        
        # Update resource status
        available = state["available"]
        total_resources = self.config.get("resources")
        
        for resource in ["cpu", "memory", "disk", "network"]:
            total = total_resources[resource]
            used = total - available[resource]
            percent = (used / total) * 100 if total > 0 else 0
            
            self.resource_bars[resource]["value"] = percent
            self.resource_labels[resource]["text"] = f"{used}/{total}"
            
        # Update allocation table
        self.alloc_tree.delete(*self.alloc_tree.get_children())
        
        for pid, allocation in state["allocation"].items():
            process_info = state["process_info"].get(pid, {})
            status = process_info.get("status", "unknown")
            
            self.alloc_tree.insert("", "end", values=(
                pid,
                allocation["cpu"],
                allocation["memory"],
                allocation["disk"],
                allocation["network"],
                status
            ))
            
    def _update_process_list(self):
        """Update process list display."""
        processes = self.system_monitor.get_processes(sort_by="cpu")
        
        # Clear current items
        self.process_tree.delete(*self.process_tree.get_children())
        
        # Add processes
        for proc in processes[:10]:  # Show top 10 processes
            self.process_tree.insert("", "end", values=(
                proc["pid"],
                proc["name"],
                f"{proc['cpu_percent']:.1f}",
                f"{proc['memory_percent']:.1f}"
            ))
            
    def _request_resources(self):
        """Handle resource request button click."""
        try:
            # Get process ID
            pid = self.pid_entry.get().strip()
            if not pid:
                messagebox.showerror("Error", "Please enter a Process ID")
                return
                
            # Get resource amounts
            resources = {}
            
            cpu = self.cpu_entry.get().strip()
            if cpu:
                resources["cpu"] = int(cpu)
                
            memory = self.memory_entry.get().strip()
            if memory:
                resources["memory"] = int(memory)
                
            disk = self.disk_entry.get().strip()
            if disk:
                resources["disk"] = int(disk)
                
            network = self.network_entry.get().strip()
            if network:
                resources["network"] = int(network)
                
            if not resources:
                messagebox.showerror("Error", "Please enter at least one resource amount")
                return
                
            # Check if process exists
            state = self.resource_manager.get_system_state()
            if pid not in state["allocation"]:
                # Register process with maximum resources
                max_resources = {r: self.config.get("resources")[r] for r in resources.keys()}
                if not self.resource_manager.register_process(pid, max_resources):
                    messagebox.showerror("Error", "Failed to register process")
                    return
                    
            # Request resources
            if self.resource_manager.request_resources(pid, resources):
                messagebox.showinfo("Success", "Resources allocated successfully")
                self._update_resource_allocation()
            else:
                messagebox.showerror("Error", "Resource allocation would cause deadlock")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for resource amounts")
        except Exception as e:
            messagebox.showerror("Error", f"Error requesting resources: {e}")
            
    def _release_resources(self):
        """Handle resource release button click."""
        try:
            # Get process ID
            pid = self.pid_entry.get().strip()
            if not pid:
                messagebox.showerror("Error", "Please enter a Process ID")
                return
                
            # Get resource amounts
            resources = {}
            
            cpu = self.cpu_entry.get().strip()
            if cpu:
                resources["cpu"] = int(cpu)
                
            memory = self.memory_entry.get().strip()
            if memory:
                resources["memory"] = int(memory)
                
            disk = self.disk_entry.get().strip()
            if disk:
                resources["disk"] = int(disk)
                
            network = self.network_entry.get().strip()
            if network:
                resources["network"] = int(network)
                
            if not resources:
                messagebox.showerror("Error", "Please enter at least one resource amount")
                return
                
            # Release resources
            if self.resource_manager.release_resources(pid, resources):
                messagebox.showinfo("Success", "Resources released successfully")
                self._update_resource_allocation()
            else:
                messagebox.showerror("Error", "Failed to release resources")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for resource amounts")
        except Exception as e:
            messagebox.showerror("Error", f"Error releasing resources: {e}")
            
    def _remove_process(self):
        """Handle remove process button click."""
        try:
            # Get process ID
            pid = self.pid_entry.get().strip()
            if not pid:
                messagebox.showerror("Error", "Please enter a Process ID")
                return
                
            # Remove process
            if self.resource_manager.remove_process(pid):
                messagebox.showinfo("Success", "Process removed successfully")
                self._update_resource_allocation()
            else:
                messagebox.showerror("Error", "Failed to remove process")
        except Exception as e:
            messagebox.showerror("Error", f"Error removing process: {e}")
            
    def _on_allocation_select(self, event):
        """Handle allocation table row selection."""
        # Get selected item
        selection = self.alloc_tree.selection()
        if not selection:
            return
            
        # Get values
        values = self.alloc_tree.item(selection[0], "values")
        if not values:
            return
            
        # Fill form
        self.pid_entry.delete(0, tk.END)
        self.pid_entry.insert(0, values[0])
        
        self.cpu_entry.delete(0, tk.END)
        self.cpu_entry.insert(0, values[1])
        
        self.memory_entry.delete(0, tk.END)
        self.memory_entry.insert(0, values[2])
        
        self.disk_entry.delete(0, tk.END)
        self.disk_entry.insert(0, values[3])
        
        self.network_entry.delete(0, tk.END)
        self.network_entry.insert(0, values[4])
