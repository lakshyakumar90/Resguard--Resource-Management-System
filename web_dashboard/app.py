"""
Web Dashboard Application Module

This module provides the Flask application for the ResGuard web dashboard.
"""

import os
import json
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from functools import wraps
from typing import Dict, Any, Callable, List, Union

from core.resource_manager import ResourceManager
from utils.system_monitor import SystemMonitor
from utils.config import Config


def create_app(resource_manager: ResourceManager, system_monitor: SystemMonitor,
              config: Config) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        resource_manager: Resource manager instance
        system_monitor: System monitor instance
        config: Configuration object

    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    # Store components in app config
    app.config["RESOURCE_MANAGER"] = resource_manager
    app.config["SYSTEM_MONITOR"] = system_monitor
    app.config["APP_CONFIG"] = config

    # Authentication decorator
    def login_required(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if config.get("security", "enable_authentication") and "username" not in session:
                return redirect(url_for("login", next=request.url))
            return f(*args, **kwargs)
        return decorated_function

    # Routes
    @app.route("/")
    @login_required
    def index():
        """Render the main dashboard page."""
        return render_template("index.html")

    @app.route("/settings", methods=["GET", "POST"])
    @login_required
    def settings():
        """Handle settings page."""
        errors = []
        success = False

        # Handle reset requests
        if request.args.get("reset"):
            reset_type = request.args.get("reset")
            if reset_type == "all":
                config.reset_to_defaults()
                config.save()
                flash("All settings have been reset to defaults.")
                return redirect(url_for("settings"))
            elif reset_type in config.get_all():
                config.reset_section(reset_type)
                config.save()
                flash(f"{reset_type.replace('_', ' ').title()} settings have been reset to defaults.")
                return redirect(url_for("settings"))

        # Handle form submission
        if request.method == "POST":
            # Process form data
            for key, value in request.form.items():
                if "." in key:
                    section, setting = key.split(".", 1)

                    # Convert value based on type
                    metadata = config.get_settings_metadata()
                    field_meta = next((f for f in metadata.get(section, []) if f["name"] == setting), None)

                    if field_meta:
                        if field_meta["type"] == "number":
                            try:
                                if "." in value:
                                    value = float(value)
                                else:
                                    value = int(value)
                            except ValueError:
                                errors.append(f"Invalid number for {field_meta['label']}")
                                continue
                        elif field_meta["type"] == "boolean":
                            value = (value == "on")

                    # Update config
                    config.set(section, setting, value)

            # Validate config
            validation_errors = config.validate()
            if validation_errors:
                errors.extend(validation_errors)

            # Save config if no errors
            if not errors:
                if config.save():
                    success = True
                else:
                    errors.append("Failed to save configuration")

        # Prepare data for template
        metadata = config.get_settings_metadata()
        config_data = config.get_all()

        return render_template(
            "settings.html",
            metadata=metadata,
            config=config_data,
            errors=errors,
            success=success
        )

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Handle login requests."""
        if not config.get("security", "enable_authentication"):
            return redirect(url_for("index"))

        error = None
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            if (username == config.get("security", "default_username") and
                password == config.get("security", "default_password")):
                session["username"] = username
                return redirect(request.args.get("next") or url_for("index"))
            else:
                error = "Invalid username or password"

        return render_template("login.html", error=error)

    @app.route("/logout")
    def logout():
        """Handle logout requests."""
        session.pop("username", None)
        return redirect(url_for("login"))

    @app.route("/api/system")
    @login_required
    def api_system():
        """API endpoint for system metrics."""
        return jsonify(system_monitor.get_metrics())

    @app.route("/api/system/history")
    @login_required
    def api_system_history():
        """API endpoint for system metrics history."""
        return jsonify(system_monitor.get_history())

    @app.route("/api/system/processes")
    @login_required
    def api_processes():
        """API endpoint for process information."""
        sort_by = request.args.get("sort", "cpu")
        return jsonify(system_monitor.get_processes(sort_by=sort_by))

    @app.route("/api/resources")
    @login_required
    def api_resources():
        """API endpoint for resource allocation information."""
        return jsonify(resource_manager.get_system_state())

    @app.route("/api/resources/request", methods=["POST"])
    @login_required
    def api_request_resources():
        """API endpoint for requesting resources."""
        data = request.json

        if not data or "process_id" not in data or "resources" not in data:
            return jsonify({"success": False, "error": "Invalid request data"}), 400

        process_id = data["process_id"]
        resources = data["resources"]

        # Check if process exists
        state = resource_manager.get_system_state()
        if process_id not in state["allocation"]:
            # Register process with maximum resources
            max_resources = {r: config.get("resources")[r] for r in resources.keys()}
            if not resource_manager.register_process(process_id, max_resources):
                return jsonify({"success": False, "error": "Failed to register process"}), 400

        # Request resources
        if resource_manager.request_resources(process_id, resources):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Resource allocation would cause deadlock"}), 400

    @app.route("/api/resources/release", methods=["POST"])
    @login_required
    def api_release_resources():
        """API endpoint for releasing resources."""
        data = request.json

        if not data or "process_id" not in data or "resources" not in data:
            return jsonify({"success": False, "error": "Invalid request data"}), 400

        process_id = data["process_id"]
        resources = data["resources"]

        # Release resources
        if resource_manager.release_resources(process_id, resources):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Failed to release resources"}), 400

    @app.route("/api/resources/remove", methods=["POST"])
    @login_required
    def api_remove_process():
        """API endpoint for removing a process."""
        data = request.json

        if not data or "process_id" not in data:
            return jsonify({"success": False, "error": "Invalid request data"}), 400

        process_id = data["process_id"]

        # Remove process
        if resource_manager.remove_process(process_id):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Failed to remove process"}), 400

    @app.route("/api/resources/reset", methods=["POST"])
    @login_required
    def api_reset_resources():
        """API endpoint for resetting resources to initial values."""
        # Reset resources
        if resource_manager.reset_resources():
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Failed to reset resources"}), 400

    return app


def run_app(app: Flask, host: str = "127.0.0.1", port: int = 5000,
           debug: bool = False, threaded: bool = True) -> None:
    """
    Run the Flask application.

    Args:
        app: Flask application
        host: Host to bind to
        port: Port to bind to
        debug: Whether to run in debug mode
        threaded: Whether the app is running in a thread
    """
    # If running in a thread, we need to disable debug mode to avoid errors
    # with the reloader trying to use signals in a non-main thread
    if threaded:
        debug = False

    app.run(host=host, port=port, debug=debug, use_reloader=False)
