"""
Dash Dashboard Module

This module provides the Dash application for the ResGuard web dashboard.
"""

import dash
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import time
from typing import Dict, Any, List

from core.resource_manager import ResourceManager
from utils.system_monitor import SystemMonitor
from utils.config import Config


def create_dashboard(server, resource_manager: ResourceManager,
                    system_monitor: SystemMonitor, config: Config) -> dash.Dash:
    """
    Create and configure the Dash application.

    Args:
        server: Flask server
        resource_manager: Resource manager instance
        system_monitor: System monitor instance
        config: Configuration object

    Returns:
        dash.Dash: Configured Dash application
    """
    # Create Dash app
    app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname="/dashboard/",
        external_stylesheets=[
            "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"
        ]
    )

    # Define layout
    app.layout = html.Div([
        # Header
        html.Div([
            html.H1("ResGuard Dashboard", className="display-4"),
            html.P("Dynamic Resource Management System", className="lead"),
            html.Hr()
        ], className="jumbotron py-4"),

        # Main content
        html.Div([
            # Refresh interval
            dcc.Interval(
                id="interval-component",
                interval=config.get("web_dashboard", "refresh_interval") * 1000,  # milliseconds
                n_intervals=0
            ),

            # System metrics
            html.Div([
                html.H2("System Metrics"),
                html.Div([
                    # CPU usage
                    html.Div([
                        html.H4("CPU Usage"),
                        dcc.Graph(id="cpu-gauge")
                    ], className="col-md-6"),

                    # Memory usage
                    html.Div([
                        html.H4("Memory Usage"),
                        dcc.Graph(id="memory-gauge")
                    ], className="col-md-6")
                ], className="row"),

                html.Div([
                    # Disk usage
                    html.Div([
                        html.H4("Disk Usage"),
                        dcc.Graph(id="disk-gauge")
                    ], className="col-md-6"),

                    # Network usage
                    html.Div([
                        html.H4("Network Usage"),
                        dcc.Graph(id="network-chart")
                    ], className="col-md-6")
                ], className="row"),

                # Usage history
                html.Div([
                    html.H4("Resource Usage History"),
                    dcc.Graph(id="history-chart")
                ], className="mt-4")
            ], className="mt-4"),

            # Resource allocation
            html.Div([
                html.H2("Resource Allocation"),

                # Resource status
                html.Div([
                    html.Div([
                        html.H4("Resource Status", className="d-inline-block mr-2"),
                        html.Button(
                            "Reset Resources",
                            id="reset-resources-button",
                            className="btn btn-sm btn-warning",
                            title="Reset all resources to initial values"
                        )
                    ], className="d-flex justify-content-between align-items-center"),
                    html.Div(id="resource-status")
                ], className="mt-3"),

                # Process allocations
                html.Div([
                    html.H4("Process Allocations"),
                    html.Div(id="process-allocations")
                ], className="mt-3"),

                # Resource request form
                html.Div([
                    html.H4("Request Resources"),
                    html.Div([
                        # Process ID
                        html.Div([
                            html.Label("Process ID"),
                            dcc.Input(
                                id="process-id-input",
                                type="text",
                                placeholder="Enter process ID",
                                className="form-control"
                            )
                        ], className="form-group"),

                        # Resource amounts
                        html.Div([
                            html.Div([
                                html.Label("CPU"),
                                dcc.Input(
                                    id="cpu-input",
                                    type="number",
                                    min=0,
                                    placeholder="CPU units",
                                    className="form-control"
                                )
                            ], className="col-md-3"),

                            html.Div([
                                html.Label("Memory"),
                                dcc.Input(
                                    id="memory-input",
                                    type="number",
                                    min=0,
                                    placeholder="Memory units",
                                    className="form-control"
                                )
                            ], className="col-md-3"),

                            html.Div([
                                html.Label("Disk"),
                                dcc.Input(
                                    id="disk-input",
                                    type="number",
                                    min=0,
                                    placeholder="Disk units",
                                    className="form-control"
                                )
                            ], className="col-md-3"),

                            html.Div([
                                html.Label("Network"),
                                dcc.Input(
                                    id="network-input",
                                    type="number",
                                    min=0,
                                    placeholder="Network units",
                                    className="form-control"
                                )
                            ], className="col-md-3")
                        ], className="form-row"),

                        # Buttons
                        html.Div([
                            html.Button(
                                "Request",
                                id="request-button",
                                className="btn btn-primary mr-2"
                            ),
                            html.Button(
                                "Release",
                                id="release-button",
                                className="btn btn-warning mr-2"
                            ),
                            html.Button(
                                "Remove",
                                id="remove-button",
                                className="btn btn-danger"
                            )
                        ], className="mt-3"),

                        # Status message
                        html.Div(id="request-status", className="mt-2")
                    ], className="card card-body")
                ], className="mt-3")
            ], className="mt-4")
        ], className="container")
    ])

    # Define callbacks
    @app.callback(
        Output("cpu-gauge", "figure"),
        Input("interval-component", "n_intervals")
    )
    def update_cpu_gauge(n):
        """Update CPU gauge chart."""
        metrics = system_monitor.get_metrics()
        cpu_percent = metrics["cpu"]["percent"]

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=cpu_percent,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "CPU Usage"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 50], "color": "lightgreen"},
                    {"range": [50, 80], "color": "orange"},
                    {"range": [80, 100], "color": "red"}
                ]
            }
        ))

        fig.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
        return fig

    @app.callback(
        Output("memory-gauge", "figure"),
        Input("interval-component", "n_intervals")
    )
    def update_memory_gauge(n):
        """Update memory gauge chart."""
        metrics = system_monitor.get_metrics()
        memory_percent = metrics["memory"]["percent"]

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=memory_percent,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Memory Usage"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 50], "color": "lightgreen"},
                    {"range": [50, 80], "color": "orange"},
                    {"range": [80, 100], "color": "red"}
                ]
            }
        ))

        fig.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
        return fig

    @app.callback(
        Output("disk-gauge", "figure"),
        Input("interval-component", "n_intervals")
    )
    def update_disk_gauge(n):
        """Update disk gauge chart."""
        metrics = system_monitor.get_metrics()
        disk_percent = metrics["disk"]["percent"]

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=disk_percent,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Disk Usage"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 50], "color": "lightgreen"},
                    {"range": [50, 80], "color": "orange"},
                    {"range": [80, 100], "color": "red"}
                ]
            }
        ))

        fig.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
        return fig

    @app.callback(
        Output("network-chart", "figure"),
        Input("interval-component", "n_intervals")
    )
    def update_network_chart(n):
        """Update network usage chart."""
        history = system_monitor.get_history()

        if len(history["network"]) < 2:
            # Not enough data yet
            return go.Figure()

        # Calculate network speeds
        recv_speeds = []
        sent_speeds = []
        timestamps = []

        for i in range(1, len(history["network"])):
            last = history["network"][i]
            prev = history["network"][i-1]
            last_time = history["timestamps"][i]
            prev_time = history["timestamps"][i-1]

            time_diff = last_time - prev_time
            if time_diff > 0:
                recv_speed = (last["recv"] - prev["recv"]) / time_diff / 1024  # KB/s
                sent_speed = (last["sent"] - prev["sent"]) / time_diff / 1024  # KB/s

                recv_speeds.append(recv_speed)
                sent_speeds.append(sent_speed)
                timestamps.append(time.strftime("%H:%M:%S", time.localtime(last_time)))

        # Create figure
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=recv_speeds,
            mode="lines",
            name="Download (KB/s)"
        ))

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=sent_speeds,
            mode="lines",
            name="Upload (KB/s)"
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=50, b=10),
            xaxis_title="Time",
            yaxis_title="Speed (KB/s)"
        )

        return fig

    @app.callback(
        Output("history-chart", "figure"),
        Input("interval-component", "n_intervals")
    )
    def update_history_chart(n):
        """Update resource usage history chart."""
        history = system_monitor.get_history()

        if not history["timestamps"]:
            # No data yet
            return go.Figure()

        # Convert timestamps to readable format
        timestamps = [time.strftime("%H:%M:%S", time.localtime(ts)) for ts in history["timestamps"]]

        # Create figure
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=history["cpu"],
            mode="lines",
            name="CPU %"
        ))

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=history["memory"],
            mode="lines",
            name="Memory %"
        ))

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=history["disk"],
            mode="lines",
            name="Disk %"
        ))

        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Time",
            yaxis_title="Usage %",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return fig

    @app.callback(
        Output("resource-status", "children"),
        Input("interval-component", "n_intervals")
    )
    def update_resource_status(n):
        """Update resource status display."""
        state = resource_manager.get_system_state()
        available = state["available"]
        total_resources = config.get("resources")

        # Create table
        table = html.Table([
            # Header
            html.Thead(html.Tr([
                html.Th("Resource"),
                html.Th("Used"),
                html.Th("Available"),
                html.Th("Total"),
                html.Th("Usage %")
            ])),

            # Body
            html.Tbody([
                # CPU
                html.Tr([
                    html.Td("CPU"),
                    html.Td(f"{total_resources['cpu'] - available['cpu']}"),
                    html.Td(f"{available['cpu']}"),
                    html.Td(f"{total_resources['cpu']}"),
                    html.Td(f"{((total_resources['cpu'] - available['cpu']) / total_resources['cpu'] * 100):.1f}%")
                ]),

                # Memory
                html.Tr([
                    html.Td("Memory"),
                    html.Td(f"{total_resources['memory'] - available['memory']}"),
                    html.Td(f"{available['memory']}"),
                    html.Td(f"{total_resources['memory']}"),
                    html.Td(f"{((total_resources['memory'] - available['memory']) / total_resources['memory'] * 100):.1f}%")
                ]),

                # Disk
                html.Tr([
                    html.Td("Disk"),
                    html.Td(f"{total_resources['disk'] - available['disk']}"),
                    html.Td(f"{available['disk']}"),
                    html.Td(f"{total_resources['disk']}"),
                    html.Td(f"{((total_resources['disk'] - available['disk']) / total_resources['disk'] * 100):.1f}%")
                ]),

                # Network
                html.Tr([
                    html.Td("Network"),
                    html.Td(f"{total_resources['network'] - available['network']}"),
                    html.Td(f"{available['network']}"),
                    html.Td(f"{total_resources['network']}"),
                    html.Td(f"{((total_resources['network'] - available['network']) / total_resources['network'] * 100):.1f}%")
                ])
            ])
        ], className="table table-striped")

        return table

    @app.callback(
        Output("process-allocations", "children"),
        Input("interval-component", "n_intervals")
    )
    def update_process_allocations(n):
        """Update process allocations display."""
        state = resource_manager.get_system_state()

        if not state["allocation"]:
            return html.P("No processes registered")

        # Create table
        table = html.Table([
            # Header
            html.Thead(html.Tr([
                html.Th("Process ID"),
                html.Th("CPU"),
                html.Th("Memory"),
                html.Th("Disk"),
                html.Th("Network"),
                html.Th("Status")
            ])),

            # Body
            html.Tbody([
                html.Tr([
                    html.Td(pid),
                    html.Td(f"{allocation['cpu']}"),
                    html.Td(f"{allocation['memory']}"),
                    html.Td(f"{allocation['disk']}"),
                    html.Td(f"{allocation['network']}"),
                    html.Td(state["process_info"].get(pid, {}).get("status", "unknown"))
                ]) for pid, allocation in state["allocation"].items()
            ])
        ], className="table table-striped")

        return table

    @app.callback(
        Output("request-status", "children"),
        [
            Input("request-button", "n_clicks"),
            Input("release-button", "n_clicks"),
            Input("remove-button", "n_clicks"),
            Input("reset-resources-button", "n_clicks")
        ],
        [
            State("process-id-input", "value"),
            State("cpu-input", "value"),
            State("memory-input", "value"),
            State("disk-input", "value"),
            State("network-input", "value")
        ]
    )
    def handle_resource_actions(request_clicks, release_clicks, remove_clicks, reset_clicks,
                              process_id, cpu, memory, disk, network):
        """Handle resource action button clicks."""
        ctx = dash.callback_context

        if not ctx.triggered:
            return ""

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if not process_id:
            return html.Div("Please enter a Process ID", className="alert alert-danger")

        if button_id == "request-button":
            return handle_request(process_id, cpu, memory, disk, network)
        elif button_id == "release-button":
            return handle_release(process_id, cpu, memory, disk, network)
        elif button_id == "remove-button":
            return handle_remove(process_id)
        elif button_id == "reset-resources-button":
            return handle_reset_resources()

        return ""

    def handle_request(process_id, cpu, memory, disk, network):
        """Handle resource request."""
        resources = {}

        if cpu is not None:
            resources["cpu"] = int(cpu)
        if memory is not None:
            resources["memory"] = int(memory)
        if disk is not None:
            resources["disk"] = int(disk)
        if network is not None:
            resources["network"] = int(network)

        if not resources:
            return html.Div("Please enter at least one resource amount", className="alert alert-danger")

        # Check if process exists
        state = resource_manager.get_system_state()
        if process_id not in state["allocation"]:
            # Register process with maximum resources
            max_resources = {r: config.get("resources")[r] for r in resources.keys()}
            if not resource_manager.register_process(process_id, max_resources):
                return html.Div("Failed to register process", className="alert alert-danger")

        # Request resources
        if resource_manager.request_resources(process_id, resources):
            return html.Div("Resources allocated successfully", className="alert alert-success")
        else:
            return html.Div("Resource allocation would cause deadlock", className="alert alert-danger")

    def handle_release(process_id, cpu, memory, disk, network):
        """Handle resource release."""
        resources = {}

        if cpu is not None:
            resources["cpu"] = int(cpu)
        if memory is not None:
            resources["memory"] = int(memory)
        if disk is not None:
            resources["disk"] = int(disk)
        if network is not None:
            resources["network"] = int(network)

        if not resources:
            return html.Div("Please enter at least one resource amount", className="alert alert-danger")

        # Release resources
        if resource_manager.release_resources(process_id, resources):
            return html.Div("Resources released successfully", className="alert alert-success")
        else:
            return html.Div("Failed to release resources", className="alert alert-danger")

    def handle_remove(process_id):
        """Handle process removal."""
        if resource_manager.remove_process(process_id):
            return html.Div("Process removed successfully", className="alert alert-success")
        else:
            return html.Div("Failed to remove process", className="alert alert-danger")

    def handle_reset_resources():
        """Handle resources reset."""
        # Call the API endpoint to reset resources
        if resource_manager.reset_resources():
            return html.Div("Resources reset to initial values successfully", className="alert alert-success")
        else:
            return html.Div("Failed to reset resources", className="alert alert-danger")

    return app
