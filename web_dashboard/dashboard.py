"""
Dash Dashboard Module

This module provides the Dash application for the ResGuard web dashboard.
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import time
from typing import Dict, Any, List


from utils.system_monitor import SystemMonitor
from utils.config import Config


def create_dashboard(server, system_monitor: SystemMonitor, config: Config) -> dash.Dash:
    """
    Create and configure the Dash application.

    Args:
        server: Flask server
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



    return app
