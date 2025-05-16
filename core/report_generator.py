"""
Report Generator Module

This module provides functionality to generate reports on resource utilization
and system performance.
"""

import os
import time
import threading
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
from jinja2 import Template

from utils.config import Config
from utils.system_monitor import SystemMonitor
from core.resource_manager import ResourceManager


class ReportGenerator:
    """
    Generates reports on resource utilization and system performance.
    
    This class implements automated report generation with configurable
    formats and metrics.
    """
    
    def __init__(self, resource_manager: ResourceManager, system_monitor: SystemMonitor, config: Config):
        """
        Initialize the report generator.
        
        Args:
            resource_manager: Resource manager instance
            system_monitor: System monitor instance
            config: Configuration object
        """
        self.resource_manager = resource_manager
        self.system_monitor = system_monitor
        self.config = config
        self.lock = threading.RLock()
        self.running = False
        self.report_thread = None
        
        # Report history
        self.report_history = []
        
        # Set up logging
        self.logger = logging.getLogger("report_generator")
        self.logger.setLevel(logging.INFO)
        
        # Load configuration
        self.enabled = config.get("reports", "enabled")
        self.generation_interval = config.get("reports", "generation_interval")
        self.retention_period = config.get("reports", "retention_period")
        self.include_metrics = config.get("reports", "include_metrics")
        self.report_format = config.get("reports", "format")
        self.output_dir = config.get("reports", "output_dir")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def start(self):
        """Start the report generator."""
        if not self.enabled:
            self.logger.info("Report generator is disabled in configuration")
            return
            
        with self.lock:
            if self.running:
                return
                
            self.running = True
            self.report_thread = threading.Thread(target=self._report_loop, daemon=True)
            self.report_thread.start()
            self.logger.info("Report generator started")
            
    def stop(self):
        """Stop the report generator."""
        with self.lock:
            self.running = False
            if self.report_thread:
                self.report_thread.join(timeout=1.0)
                self.report_thread = None
            self.logger.info("Report generator stopped")
            
    def get_report_history(self) -> List[Dict]:
        """
        Get the report generation history.
        
        Returns:
            List[Dict]: History of generated reports
        """
        with self.lock:
            return self.report_history.copy()
            
    def generate_report(self, report_type: str = "daily") -> Optional[str]:
        """
        Generate a report on demand.
        
        Args:
            report_type: Type of report to generate (daily, weekly, monthly)
            
        Returns:
            Optional[str]: Path to the generated report, or None if generation failed
        """
        with self.lock:
            try:
                # Determine time range based on report type
                end_time = time.time()
                if report_type == "daily":
                    start_time = end_time - 86400  # 1 day
                    title = "Daily Resource Utilization Report"
                elif report_type == "weekly":
                    start_time = end_time - 604800  # 7 days
                    title = "Weekly Resource Utilization Report"
                elif report_type == "monthly":
                    start_time = end_time - 2592000  # 30 days
                    title = "Monthly Resource Utilization Report"
                else:
                    # Default to daily
                    start_time = end_time - 86400
                    title = "Resource Utilization Report"
                    
                # Generate report
                report_path = self._generate_report_file(start_time, end_time, title, report_type)
                
                if report_path:
                    # Add to history
                    self.report_history.append({
                        "type": report_type,
                        "path": report_path,
                        "generated_at": time.time(),
                        "start_time": start_time,
                        "end_time": end_time
                    })
                    
                    # Keep history limited to last 100 reports
                    if len(self.report_history) > 100:
                        self.report_history = self.report_history[-100:]
                        
                    self.logger.info(f"Generated {report_type} report: {report_path}")
                    
                return report_path
            except Exception as e:
                self.logger.error(f"Error generating report: {e}")
                return None
                
    def _report_loop(self):
        """Background thread for generating periodic reports."""
        # Wait a bit before generating the first report
        time.sleep(60)
        
        while self.running:
            try:
                # Generate daily report
                self.generate_report("daily")
                
                # Check if we should generate weekly report (on Sundays)
                now = datetime.now()
                if now.weekday() == 6:  # Sunday
                    self.generate_report("weekly")
                    
                # Check if we should generate monthly report (on 1st of month)
                if now.day == 1:
                    self.generate_report("monthly")
                    
                # Clean up old reports
                self._cleanup_old_reports()
            except Exception as e:
                self.logger.error(f"Error in report loop: {e}")
                
            # Sleep until next generation time
            time.sleep(self.generation_interval)
            
    def _generate_report_file(self, start_time: float, end_time: float, 
                             title: str, report_type: str) -> Optional[str]:
        """
        Generate a report file.
        
        Args:
            start_time: Start time for report data
            end_time: End time for report data
            title: Report title
            report_type: Type of report
            
        Returns:
            Optional[str]: Path to the generated report, or None if generation failed
        """
        # Create report filename
        timestamp = datetime.fromtimestamp(end_time).strftime("%Y%m%d-%H%M%S")
        filename = f"{report_type}_{timestamp}"
        
        # Generate report based on format
        if self.report_format == "html":
            return self._generate_html_report(start_time, end_time, title, filename)
        elif self.report_format == "json":
            return self._generate_json_report(start_time, end_time, title, filename)
        elif self.report_format == "pdf":
            return self._generate_pdf_report(start_time, end_time, title, filename)
        else:
            # Default to HTML
            return self._generate_html_report(start_time, end_time, title, filename)
            
    def _generate_html_report(self, start_time: float, end_time: float, 
                             title: str, filename: str) -> Optional[str]:
        """
        Generate an HTML report.
        
        Args:
            start_time: Start time for report data
            end_time: End time for report data
            title: Report title
            filename: Base filename
            
        Returns:
            Optional[str]: Path to the generated report, or None if generation failed
        """
        try:
            # Collect report data
            report_data = self._collect_report_data(start_time, end_time)
            
            # Generate charts
            chart_paths = self._generate_charts(report_data, filename)
            
            # Create HTML template
            template_str = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>{{ title }}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #333; }
                    .section { margin-bottom: 30px; }
                    .chart { margin-bottom: 20px; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    tr:nth-child(even) { background-color: #f9f9f9; }
                </style>
            </head>
            <body>
                <h1>{{ title }}</h1>
                <p>Generated: {{ generated_at }}</p>
                <p>Period: {{ start_time }} to {{ end_time }}</p>
                
                <div class="section">
                    <h2>Resource Utilization Summary</h2>
                    <table>
                        <tr>
                            <th>Resource</th>
                            <th>Average</th>
                            <th>Maximum</th>
                            <th>Minimum</th>
                        </tr>
                        {% for resource in summary %}
                        <tr>
                            <td>{{ resource.name }}</td>
                            <td>{{ resource.avg }}%</td>
                            <td>{{ resource.max }}%</td>
                            <td>{{ resource.min }}%</td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
                
                <div class="section">
                    <h2>Resource Usage Charts</h2>
                    {% for chart in charts %}
                    <div class="chart">
                        <h3>{{ chart.title }}</h3>
                        <img src="{{ chart.path }}" alt="{{ chart.title }}" width="800">
                    </div>
                    {% endfor %}
                </div>
                
                <div class="section">
                    <h2>Process Allocation Summary</h2>
                    <table>
                        <tr>
                            <th>Process ID</th>
                            <th>CPU</th>
                            <th>Memory</th>
                            <th>Disk</th>
                            <th>Network</th>
                            <th>Status</th>
                        </tr>
                        {% for process in processes %}
                        <tr>
                            <td>{{ process.id }}</td>
                            <td>{{ process.cpu }}</td>
                            <td>{{ process.memory }}</td>
                            <td>{{ process.disk }}</td>
                            <td>{{ process.network }}</td>
                            <td>{{ process.status }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
                
                <div class="section">
                    <h2>Efficiency Metrics</h2>
                    <table>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                        {% for metric in efficiency %}
                        <tr>
                            <td>{{ metric.name }}</td>
                            <td>{{ metric.value }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
            </body>
            </html>
            """
            
            # Create template
            template = Template(template_str)
            
            # Prepare template data
            template_data = {
                "title": title,
                "generated_at": datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S"),
                "start_time": datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"),
                "summary": report_data["summary"],
                "charts": [
                    {"title": "CPU Usage", "path": chart_paths["cpu"]},
                    {"title": "Memory Usage", "path": chart_paths["memory"]},
                    {"title": "Disk Usage", "path": chart_paths["disk"]},
                    {"title": "Network Usage", "path": chart_paths["network"]}
                ],
                "processes": report_data["processes"],
                "efficiency": report_data["efficiency"]
            }
            
            # Render template
            html_content = template.render(**template_data)
            
            # Write to file
            report_path = os.path.join(self.output_dir, f"{filename}.html")
            with open(report_path, "w") as f:
                f.write(html_content)
                
            return report_path
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {e}")
            return None
            
    def _generate_json_report(self, start_time: float, end_time: float, 
                             title: str, filename: str) -> Optional[str]:
        """
        Generate a JSON report.
        
        Args:
            start_time: Start time for report data
            end_time: End time for report data
            title: Report title
            filename: Base filename
            
        Returns:
            Optional[str]: Path to the generated report, or None if generation failed
        """
        try:
            # Collect report data
            report_data = self._collect_report_data(start_time, end_time)
            
            # Create JSON structure
            json_data = {
                "title": title,
                "generated_at": time.time(),
                "start_time": start_time,
                "end_time": end_time,
                "data": report_data
            }
            
            # Write to file
            report_path = os.path.join(self.output_dir, f"{filename}.json")
            with open(report_path, "w") as f:
                json.dump(json_data, f, indent=2)
                
            return report_path
        except Exception as e:
            self.logger.error(f"Error generating JSON report: {e}")
            return None
            
    def _generate_pdf_report(self, start_time: float, end_time: float, 
                            title: str, filename: str) -> Optional[str]:
        """
        Generate a PDF report.
        
        Args:
            start_time: Start time for report data
            end_time: End time for report data
            title: Report title
            filename: Base filename
            
        Returns:
            Optional[str]: Path to the generated report, or None if generation failed
        """
        # This is a placeholder for PDF generation
        # In a real implementation, we would use a library like ReportLab or WeasyPrint
        
        # For now, generate an HTML report instead
        self.logger.warning("PDF generation not implemented, falling back to HTML")
        return self._generate_html_report(start_time, end_time, title, filename)
            
    def _collect_report_data(self, start_time: float, end_time: float) -> Dict:
        """
        Collect data for the report.
        
        Args:
            start_time: Start time for report data
            end_time: End time for report data
            
        Returns:
            Dict: Report data
        """
        # Get system history
        history = self.system_monitor.get_history()
        
        # Filter history by time range
        filtered_timestamps = []
        filtered_cpu = []
        filtered_memory = []
        filtered_disk = []
        filtered_network = []
        
        for i, ts in enumerate(history["timestamps"]):
            if start_time <= ts <= end_time:
                filtered_timestamps.append(ts)
                filtered_cpu.append(history["cpu"][i])
                filtered_memory.append(history["memory"][i])
                filtered_disk.append(history["disk"][i])
                
                # Network is special - calculate total bytes
                if i < len(history["network"]):
                    net = history["network"][i]
                    total_bytes = net.get("bytes_sent", 0) + net.get("bytes_recv", 0)
                    filtered_network.append(total_bytes)
                else:
                    filtered_network.append(0)
                    
        # Calculate summary statistics
        summary = [
            {
                "name": "CPU",
                "avg": round(np.mean(filtered_cpu) if filtered_cpu else 0, 1),
                "max": round(np.max(filtered_cpu) if filtered_cpu else 0, 1),
                "min": round(np.min(filtered_cpu) if filtered_cpu else 0, 1)
            },
            {
                "name": "Memory",
                "avg": round(np.mean(filtered_memory) if filtered_memory else 0, 1),
                "max": round(np.max(filtered_memory) if filtered_memory else 0, 1),
                "min": round(np.min(filtered_memory) if filtered_memory else 0, 1)
            },
            {
                "name": "Disk",
                "avg": round(np.mean(filtered_disk) if filtered_disk else 0, 1),
                "max": round(np.max(filtered_disk) if filtered_disk else 0, 1),
                "min": round(np.min(filtered_disk) if filtered_disk else 0, 1)
            }
        ]
        
        # Get current process allocations
        state = self.resource_manager.get_system_state()
        processes = []
        
        for pid, allocation in state["allocation"].items():
            processes.append({
                "id": pid,
                "cpu": allocation["cpu"],
                "memory": allocation["memory"],
                "disk": allocation["disk"],
                "network": allocation["network"],
                "status": state["process_info"].get(pid, {}).get("status", "unknown")
            })
            
        # Calculate efficiency metrics
        efficiency = [
            {
                "name": "Resource Utilization",
                "value": f"{round(np.mean(filtered_cpu) if filtered_cpu else 0, 1)}%"
            },
            {
                "name": "Memory Efficiency",
                "value": f"{round(np.mean(filtered_memory) if filtered_memory else 0, 1)}%"
            },
            {
                "name": "Disk Efficiency",
                "value": f"{round(np.mean(filtered_disk) if filtered_disk else 0, 1)}%"
            }
        ]
        
        # Return collected data
        return {
            "timestamps": filtered_timestamps,
            "cpu": filtered_cpu,
            "memory": filtered_memory,
            "disk": filtered_disk,
            "network": filtered_network,
            "summary": summary,
            "processes": processes,
            "efficiency": efficiency
        }
        
    def _generate_charts(self, report_data: Dict, filename: str) -> Dict[str, str]:
        """
        Generate charts for the report.
        
        Args:
            report_data: Report data
            filename: Base filename
            
        Returns:
            Dict[str, str]: Paths to generated chart images
        """
        chart_paths = {}
        
        # Convert timestamps to datetime for better x-axis labels
        timestamps = [datetime.fromtimestamp(ts) for ts in report_data["timestamps"]]
        
        # Generate CPU chart
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, report_data["cpu"], 'b-')
        plt.title("CPU Usage")
        plt.xlabel("Time")
        plt.ylabel("Usage (%)")
        plt.grid(True)
        plt.tight_layout()
        cpu_path = os.path.join(self.output_dir, f"{filename}_cpu.png")
        plt.savefig(cpu_path)
        plt.close()
        chart_paths["cpu"] = os.path.basename(cpu_path)
        
        # Generate Memory chart
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, report_data["memory"], 'g-')
        plt.title("Memory Usage")
        plt.xlabel("Time")
        plt.ylabel("Usage (%)")
        plt.grid(True)
        plt.tight_layout()
        memory_path = os.path.join(self.output_dir, f"{filename}_memory.png")
        plt.savefig(memory_path)
        plt.close()
        chart_paths["memory"] = os.path.basename(memory_path)
        
        # Generate Disk chart
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, report_data["disk"], 'r-')
        plt.title("Disk Usage")
        plt.xlabel("Time")
        plt.ylabel("Usage (%)")
        plt.grid(True)
        plt.tight_layout()
        disk_path = os.path.join(self.output_dir, f"{filename}_disk.png")
        plt.savefig(disk_path)
        plt.close()
        chart_paths["disk"] = os.path.basename(disk_path)
        
        # Generate Network chart
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, report_data["network"], 'y-')
        plt.title("Network Usage")
        plt.xlabel("Time")
        plt.ylabel("Bytes")
        plt.grid(True)
        plt.tight_layout()
        network_path = os.path.join(self.output_dir, f"{filename}_network.png")
        plt.savefig(network_path)
        plt.close()
        chart_paths["network"] = os.path.basename(network_path)
        
        return chart_paths
        
    def _cleanup_old_reports(self):
        """Clean up old reports based on retention period."""
        try:
            # Calculate cutoff time
            cutoff_time = time.time() - (self.retention_period * 86400)  # Convert days to seconds
            
            # Get list of report files
            report_files = [f for f in os.listdir(self.output_dir) 
                          if os.path.isfile(os.path.join(self.output_dir, f))]
            
            # Check each file
            for file in report_files:
                file_path = os.path.join(self.output_dir, file)
                file_time = os.path.getmtime(file_path)
                
                if file_time < cutoff_time:
                    # Delete old file
                    os.remove(file_path)
                    self.logger.info(f"Deleted old report: {file}")
        except Exception as e:
            self.logger.error(f"Error cleaning up old reports: {e}")
