"""
Desktop Application Module

This module provides the main desktop application for the ResGuard system.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import webbrowser
import os
from typing import Dict, Any

from core.resource_manager import ResourceManager
from core.thread_manager import ThreadManager
from utils.system_monitor import SystemMonitor
from utils.config import Config
from desktop_app.login import LoginScreen
from desktop_app.dashboard import Dashboard
from desktop_app.settings_dialog import SettingsDialog




class DesktopApp:
    """
    Main desktop application for the ResGuard system.

    This class provides the main window and coordinates the different
    components of the desktop application.
    """

    def __init__(self, resource_manager: ResourceManager, thread_manager: ThreadManager,
                system_monitor: SystemMonitor, config: Config):
        """
        Initialize the desktop application.

        Args:
            resource_manager: Resource manager instance
            thread_manager: Thread manager instance
            system_monitor: System monitor instance
            config: Configuration object
        """
        self.resource_manager = resource_manager
        self.thread_manager = thread_manager
        self.system_monitor = system_monitor
        self.config = config

        # Create root window
        self.root = tk.Tk()
        self.root.title(config.get("desktop_app", "title"))
        self.root.geometry(f"{config.get('desktop_app', 'width')}x{config.get('desktop_app', 'height')}")

        # Set window icon
        # self.root.iconbitmap("icon.ico")  # Uncomment if you have an icon

        # Configure style
        self._configure_style()

        # Show login screen if authentication is enabled
        if config.get("security", "enable_authentication"):
            self.root.withdraw()  # Hide main window
            login = LoginScreen(self.root, config, self._on_login_success)
        else:
            self._initialize_ui()

    def _configure_style(self):
        """Configure the application style."""
        style = ttk.Style()

        # Use system theme
        style.theme_use("clam")  # Use a theme that works on most platforms

        # Configure colors
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
        style.configure("TButton", padding=5)
        style.configure("TProgressbar", thickness=8)

    def _on_login_success(self, username: str):
        """
        Handle successful login.

        Args:
            username: Username of the logged-in user
        """
        self.username = username
        self.root.deiconify()  # Show main window
        self._initialize_ui()

    def _initialize_ui(self):
        """Initialize the main UI after login."""
        # Configure root window
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Create menu
        self._create_menu()

        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create dashboard
        self.dashboard = Dashboard(main_frame, self.resource_manager,
                                 self.system_monitor, self.config)
        self.dashboard.pack(fill=tk.BOTH, expand=True)

        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_menu(self):
        """Create the application menu."""
        menubar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save State", command=self._save_state)
        file_menu.add_command(label="Load State", command=self._load_state)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Web Dashboard", command=self._open_web_dashboard)
        view_menu.add_command(label="Refresh", command=self._refresh)
        menubar.add_cascade(label="View", menu=view_menu)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Create Snapshot", command=self._create_snapshot)
        tools_menu.add_command(label="Load Snapshot", command=self._load_snapshot)
        tools_menu.add_separator()
        tools_menu.add_command(label="Reset Resources", command=self._reset_resources)
        tools_menu.add_separator()
        tools_menu.add_command(label="Settings", command=self._open_settings)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Help", command=self._show_help)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def _save_state(self):
        """Save the current system state."""
        if self.resource_manager.save_state():
            self.status_var.set("State saved successfully")
            messagebox.showinfo("Success", "System state saved successfully")
        else:
            self.status_var.set("Error saving state")
            messagebox.showerror("Error", "Failed to save system state")

    def _load_state(self):
        """Load system state from file."""
        if self.resource_manager.load_state():
            self.status_var.set("State loaded successfully")
            messagebox.showinfo("Success", "System state loaded successfully")
            self._refresh()
        else:
            self.status_var.set("Error loading state")
            messagebox.showerror("Error", "Failed to load system state")

    def _create_snapshot(self):
        """Create a system state snapshot."""
        # This would typically open a dialog to name the snapshot
        # For simplicity, we'll just use a timestamp
        if self.resource_manager.save_state():
            self.status_var.set("Snapshot created successfully")
            messagebox.showinfo("Success", "System snapshot created successfully")
        else:
            self.status_var.set("Error creating snapshot")
            messagebox.showerror("Error", "Failed to create system snapshot")

    def _load_snapshot(self):
        """Load a system state snapshot."""
        # This would typically open a dialog to select a snapshot
        # For simplicity, we'll just load the current state
        if self.resource_manager.load_state():
            self.status_var.set("Snapshot loaded successfully")
            messagebox.showinfo("Success", "System snapshot loaded successfully")
            self._refresh()
        else:
            self.status_var.set("Error loading snapshot")
            messagebox.showerror("Error", "Failed to load system snapshot")

    def _reset_resources(self):
        """Reset resources to initial values."""
        if messagebox.askyesno("Reset Resources", "Are you sure you want to reset all resources to their initial values? This will remove all processes and allocations."):
            if self.resource_manager.reset_resources():
                self.status_var.set("Resources reset successfully")
                messagebox.showinfo("Success", "Resources have been reset to their initial values")
                self._refresh()
            else:
                self.status_var.set("Error resetting resources")
                messagebox.showerror("Error", "Failed to reset resources")

    def _open_web_dashboard(self):
        """Open the web dashboard in a browser."""
        host = self.config.get("web_dashboard", "host")
        port = self.config.get("web_dashboard", "port")
        url = f"http://{host}:{port}"

        try:
            webbrowser.open(url)
            self.status_var.set(f"Web dashboard opened at {url}")
        except Exception as e:
            self.status_var.set("Error opening web dashboard")
            messagebox.showerror("Error", f"Failed to open web dashboard: {e}")

    def _open_settings(self):
        """Open the settings dialog."""
        # Create settings dialog
        settings_dialog = SettingsDialog(self.root, self.config, self._on_settings_saved)

    def _refresh(self):
        """Refresh the dashboard."""
        self.dashboard._refresh_data()
        self.status_var.set("Dashboard refreshed")

    def _on_settings_saved(self):
        """Handle settings saved event."""
        # Update window title and size
        self.root.title(self.config.get("desktop_app", "title"))
        self.root.geometry(f"{self.config.get('desktop_app', 'width')}x{self.config.get('desktop_app', 'height')}")

        # Refresh dashboard
        self._refresh()

        # Update status
        self.status_var.set("Settings saved successfully")

    def _show_about(self):
        """Show the about dialog."""
        about_text = """
        ResGuard: Dynamic Resource Management System

        Version: 1.0.0

        A software project to dynamically allocate computing resources
        using the Banker's Algorithm to prevent deadlocks, optimize
        utilization, and provide real-time monitoring.

        © 2024 Your Name
        """

        messagebox.showinfo("About ResGuard", about_text)

    def _show_help(self):
        """Show the help dialog."""
        help_text = """
        ResGuard Help

        Resource Requests:
        1. Enter a Process ID
        2. Enter resource amounts
        3. Click "Request"

        Resource Releases:
        1. Enter a Process ID
        2. Enter resource amounts
        3. Click "Release"

        Remove Process:
        1. Enter a Process ID
        2. Click "Remove"

        Double-click on a process in the allocation table
        to fill the request form.
        """

        messagebox.showinfo("ResGuard Help", help_text)

    def _on_close(self):
        """Handle application close."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            # Save state before exit
            self.resource_manager.save_state()

            # Shutdown components
            self.system_monitor.shutdown()
            self.resource_manager.shutdown()

            # Close window
            self.root.destroy()

    def run(self):
        """Run the application."""
        self.root.mainloop()
