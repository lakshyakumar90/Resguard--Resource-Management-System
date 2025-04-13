"""
Login Screen Module

This module provides the login screen for the ResGuard desktop application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any


class LoginScreen(tk.Toplevel):
    """
    Login screen for the ResGuard desktop application.
    
    This class provides a login form with username and password fields,
    and handles authentication.
    """
    
    def __init__(self, parent, config, on_login_success: Callable):
        """
        Initialize the login screen.
        
        Args:
            parent: Parent widget
            config: Configuration object
            on_login_success: Callback function for successful login
        """
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.on_login_success = on_login_success
        
        # Configure window
        self.title("ResGuard Login")
        self.geometry("400x300")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create widgets
        self._create_widgets()
        
        # Set focus to username entry
        self.username_entry.focus()
        
    def _create_widgets(self):
        """Create and arrange widgets for the login screen."""
        # Main frame
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="ResGuard Resource Manager",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Username
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=5)
        
        username_label = ttk.Label(username_frame, text="Username:", width=10)
        username_label.pack(side=tk.LEFT, padx=5)
        
        self.username_entry = ttk.Entry(username_frame)
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Password
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=5)
        
        password_label = ttk.Label(password_frame, text="Password:", width=10)
        password_label.pack(side=tk.LEFT, padx=5)
        
        self.password_entry = ttk.Entry(password_frame, show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Login button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        login_button = ttk.Button(
            button_frame, 
            text="Login",
            command=self.login
        )
        login_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(
            button_frame, 
            text="Cancel",
            command=self.on_close
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key to login
        self.bind("<Return>", lambda event: self.login())
        
    def login(self):
        """Handle login button click."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Login Error", "Please enter username and password")
            return
            
        # Check credentials
        if self._check_credentials(username, password):
            self.on_login_success(username)
            self.destroy()
        else:
            messagebox.showerror("Login Error", "Invalid username or password")
            
    def _check_credentials(self, username: str, password: str) -> bool:
        """
        Check if credentials are valid.
        
        Args:
            username: Username to check
            password: Password to check
            
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        # Get credentials from config
        enable_auth = self.config.get("security", "enable_authentication")
        
        if not enable_auth:
            return True
            
        default_username = self.config.get("security", "default_username")
        default_password = self.config.get("security", "default_password")
        
        return username == default_username and password == default_password
        
    def on_close(self):
        """Handle window close."""
        self.parent.destroy()
