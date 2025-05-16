"""
Settings Dialog Module

This module provides a dialog for editing application settings.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from typing import Dict, Any, List, Optional, Callable

from utils.config import Config


class SettingsDialog(tk.Toplevel):
    """
    Dialog for editing application settings.

    This class provides a UI for viewing and editing all configuration
    options, with validation and the ability to reset to defaults.
    """

    def __init__(self, parent, config: Config, on_save: Optional[Callable] = None):
        """
        Initialize the settings dialog.

        Args:
            parent: Parent widget
            config: Configuration object
            on_save: Callback function to call when settings are saved
        """
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.on_save = on_save

        # Store original config for cancel
        self.original_config = json.dumps(config.get_all())

        # Configure window
        self.title("ResGuard Settings")
        self.geometry("800x600")
        self.minsize(600, 400)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Create widgets
        self._create_widgets()

        # Initialize settings fields
        self._initialize_settings()

    def _create_widgets(self):
        """Create and arrange widgets for the settings dialog."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook for settings categories
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs for security settings only
        self.tabs = {}
        self.settings_frames = {}

        # Get settings metadata
        self.metadata = {}
        full_metadata = self.config.get_settings_metadata()

        # Only include security, reports, auto_scaling, and alerting sections
        if "security" in full_metadata:
            self.metadata["security"] = full_metadata["security"]

        if "reports" in full_metadata:
            self.metadata["reports"] = full_metadata["reports"]

        if "auto_scaling" in full_metadata:
            self.metadata["auto_scaling"] = full_metadata["auto_scaling"]

        if "alerting" in full_metadata:
            self.metadata["alerting"] = full_metadata["alerting"]

        # Create tabs for each settings category
        for section in self.metadata:
            # Create scrollable frame for section
            frame = ttk.Frame(self.notebook)

            # Set appropriate tab title
            tab_title = "Authentication" if section == "security" else section.replace("_", " ").title()
            self.notebook.add(frame, text=tab_title)

            # Add scrollbar
            canvas = tk.Canvas(frame)
            scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e, canvas=canvas: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Store frame reference
            self.tabs[section] = frame
            self.settings_frames[section] = scrollable_frame

            # Add reset button for section
            reset_button = ttk.Button(
                scrollable_frame,
                text=f"Reset {section.replace('_', ' ').title()} Settings",
                command=lambda s=section: self._reset_section(s)
            )
            reset_button.pack(pady=(10, 20), padx=10, anchor=tk.W)

        # Add buttons at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Save button
        save_button = ttk.Button(
            button_frame,
            text="Save",
            command=self.on_save_settings
        )
        save_button.pack(side=tk.RIGHT, padx=5)

        # Cancel button
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self.on_cancel
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)

        # Reset all button
        reset_all_button = ttk.Button(
            button_frame,
            text="Reset All",
            command=self._reset_all
        )
        reset_all_button.pack(side=tk.LEFT, padx=5)

    def _initialize_settings(self):
        """Initialize settings fields with current values."""
        self.setting_widgets = {}

        for section, fields in self.metadata.items():
            frame = self.settings_frames[section]
            section_widgets = {}

            for i, field in enumerate(fields):
                # Create frame for this setting
                field_frame = ttk.Frame(frame)
                field_frame.pack(fill=tk.X, pady=5, padx=10)

                # Label with tooltip
                label = ttk.Label(
                    field_frame,
                    text=field["label"],
                    width=20,
                    anchor=tk.W
                )
                label.pack(side=tk.LEFT, padx=(0, 10))

                # Create tooltip
                self._create_tooltip(label, field["description"])

                # Create appropriate widget based on type
                widget = None
                var = None

                if field["type"] == "string":
                    var = tk.StringVar()
                    widget = ttk.Entry(field_frame, textvariable=var)
                    widget.pack(side=tk.LEFT, fill=tk.X, expand=True)

                    # Set current value
                    current_value = self.config.get(section, field["name"]) or ""
                    var.set(current_value)

                elif field["type"] == "password":
                    var = tk.StringVar()
                    widget = ttk.Entry(field_frame, textvariable=var, show="*")
                    widget.pack(side=tk.LEFT, fill=tk.X, expand=True)

                    # Set current value
                    current_value = self.config.get(section, field["name"]) or ""
                    var.set(current_value)

                elif field["type"] == "number":
                    var = tk.StringVar()  # Use StringVar for validation

                    # Create spinbox with validation
                    min_val = field.get("min", 0)
                    max_val = field.get("max", 1000000)
                    step = field.get("step", 1)

                    widget = ttk.Spinbox(
                        field_frame,
                        from_=min_val,
                        to=max_val,
                        increment=step,
                        textvariable=var
                    )
                    widget.pack(side=tk.LEFT, fill=tk.X, expand=True)

                    # Set current value
                    current_value = self.config.get(section, field["name"])
                    if current_value is not None:
                        var.set(str(current_value))

                elif field["type"] == "boolean":
                    var = tk.BooleanVar()
                    widget = ttk.Checkbutton(field_frame, variable=var)
                    widget.pack(side=tk.LEFT)

                    # Set current value
                    current_value = self.config.get(section, field["name"])
                    if current_value is not None:
                        var.set(current_value)

                elif field["type"] == "select":
                    var = tk.StringVar()
                    widget = ttk.Combobox(
                        field_frame,
                        textvariable=var,
                        values=field["options"],
                        state="readonly"
                    )
                    widget.pack(side=tk.LEFT, fill=tk.X, expand=True)

                    # Set current value
                    current_value = self.config.get(section, field["name"])
                    if current_value in field["options"]:
                        var.set(current_value)
                    elif field["options"]:
                        var.set(field["options"][0])

                # Store widget and variable
                if widget and var:
                    section_widgets[field["name"]] = {
                        "widget": widget,
                        "var": var,
                        "metadata": field
                    }

            # Store section widgets
            self.setting_widgets[section] = section_widgets

    def _create_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25

            # Create tooltip window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")

            label = ttk.Label(
                self.tooltip,
                text=text,
                background="#ffffe0",
                relief="solid",
                borderwidth=1,
                wraplength=250,
                justify="left",
                padding=5
            )
            label.pack()

        def leave(event):
            if hasattr(self, "tooltip"):
                self.tooltip.destroy()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def _reset_section(self, section):
        """Reset a section to default values."""
        if messagebox.askyesno(
            "Reset Section",
            f"Are you sure you want to reset the {section.replace('_', ' ').title()} settings to defaults?"
        ):
            # Reset section in config
            self.config.reset_section(section)

            # Update UI
            section_widgets = self.setting_widgets[section]
            for name, item in section_widgets.items():
                var = item["var"]
                field = item["metadata"]

                # Get default value
                default_value = self.config.get(section, name)

                # Update widget
                if field["type"] == "boolean":
                    var.set(default_value)
                elif field["type"] in ["string", "password", "select"]:
                    var.set(default_value or "")
                elif field["type"] == "number":
                    var.set(str(default_value) if default_value is not None else "0")

    def _reset_all(self):
        """Reset all settings to defaults."""
        if messagebox.askyesno(
            "Reset All Settings",
            "Are you sure you want to reset all settings to defaults?"
        ):
            # Reset config
            self.config.reset_to_defaults()

            # Reinitialize settings
            self._initialize_settings()

    def on_save_settings(self):
        """Save settings and close dialog."""
        # Collect values from widgets
        for section, section_widgets in self.setting_widgets.items():
            for name, item in section_widgets.items():
                var = item["var"]
                field = item["metadata"]

                # Get value from widget
                value = var.get()

                # Convert value based on type
                if field["type"] == "number":
                    try:
                        # Convert to int or float
                        if "." in value:
                            value = float(value)
                        else:
                            value = int(value)

                        # Validate min/max
                        min_val = field.get("min")
                        max_val = field.get("max")

                        if min_val is not None and value < min_val:
                            messagebox.showerror(
                                "Validation Error",
                                f"{field['label']} must be at least {min_val}"
                            )
                            return

                        if max_val is not None and value > max_val:
                            messagebox.showerror(
                                "Validation Error",
                                f"{field['label']} must be at most {max_val}"
                            )
                            return
                    except ValueError:
                        messagebox.showerror(
                            "Validation Error",
                            f"{field['label']} must be a number"
                        )
                        return

                # Update config
                self.config.set(section, name, value)

        # Validate config
        errors = self.config.validate()
        if errors:
            messagebox.showerror(
                "Validation Error",
                "The following errors were found:\n\n" + "\n".join(errors)
            )
            return

        # Save config
        if not self.config.save():
            messagebox.showerror(
                "Save Error",
                "Failed to save configuration"
            )
            return

        # Call callback if provided
        if self.on_save:
            self.on_save()

        # Close dialog
        self.destroy()

    def on_cancel(self):
        """Cancel changes and close dialog."""
        # Restore original config
        original = json.loads(self.original_config)
        for section, values in original.items():
            for key, value in values.items():
                self.config.set(section, key, value)

        # Close dialog
        self.destroy()
