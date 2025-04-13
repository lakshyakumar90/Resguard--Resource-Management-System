"""
Resource Manager Module

This module implements the central resource management logic for the ResGuard system.
It coordinates resource allocation using the Banker's Algorithm and manages
process registration, resource requests, and releases.
"""

import json
import time
import threading
from typing import Dict, List, Optional, Tuple, Any

from core.banker_algorithm import BankerAlgorithm


class ResourceManager:
    """
    Central resource manager for the ResGuard system.

    This class manages resource allocation, process registration, and
    coordinates with the Banker's Algorithm to ensure safe allocation.
    """

    def __init__(self, available_resources: Dict[str, int], state_file: str = "system_state.json", reset_on_load: bool = False, debug_mode: bool = True, reset_allocations: bool = True):
        """
        Initialize the resource manager.

        Args:
            available_resources: Dictionary mapping resource names to quantities
            state_file: Path to the file for state persistence
            reset_on_load: Whether to reset resources to initial values when loading state
            debug_mode: Whether to print debug information
            reset_allocations: Whether to reset all allocations to 0 on startup
        """
        self.initial_resources = available_resources.copy()  # Store initial resources
        self.debug_mode = debug_mode  # Whether to print debug information
        self.banker = BankerAlgorithm(available_resources, debug_mode=debug_mode)
        self.state_file = state_file
        self.lock = threading.RLock()
        self.process_info = {}  # Additional process information
        self.request_history = []  # History of resource requests
        self.last_saved = 0  # Timestamp of last state save
        self.save_interval = 60  # Save state every 60 seconds
        self.reset_on_load = reset_on_load  # Whether to reset resources on load
        self.reset_allocations = reset_allocations  # Whether to reset allocations on startup

        if self.debug_mode:
            print(f"Resource Manager initialized with resources: {available_resources}")
            if self.reset_allocations:
                print("All allocations will be reset to 0 on startup")

        # Start background thread for periodic state saving
        self.running = True
        self.save_thread = threading.Thread(target=self._periodic_save, daemon=True)
        self.save_thread.start()

    def register_process(self, process_id: str, max_resources: Dict[str, int],
                         metadata: Dict[str, Any] = None) -> bool:
        """
        Register a new process with the resource manager.

        Args:
            process_id: Unique identifier for the process
            max_resources: Maximum resources the process may claim
            metadata: Additional process information

        Returns:
            bool: True if process was registered successfully, False otherwise
        """
        with self.lock:
            if self.banker.register_process(process_id, max_resources):
                self.process_info[process_id] = {
                    "registered_at": time.time(),
                    "metadata": metadata or {},
                    "status": "registered"
                }
                self._log_event("register", process_id, max_resources)
                return True
            return False

    def request_resources(self, process_id: str, request: Dict[str, int]) -> bool:
        """
        Process a resource request from a process.

        Args:
            process_id: Unique identifier for the process
            request: Dictionary of resources being requested

        Returns:
            bool: True if resources were allocated, False otherwise
        """
        with self.lock:
            result = self.banker.request_resources(process_id, request)
            if result:
                self.process_info[process_id]["status"] = "running"
                self._log_event("request", process_id, request, success=True)
            else:
                self._log_event("request", process_id, request, success=False)
            return result

    def release_resources(self, process_id: str, release: Dict[str, int]) -> bool:
        """
        Process a resource release from a process.

        Args:
            process_id: Unique identifier for the process
            release: Dictionary of resources being released

        Returns:
            bool: True if resources were released successfully, False otherwise
        """
        with self.lock:
            result = self.banker.release_resources(process_id, release)
            if result:
                self._log_event("release", process_id, release)
            return result

    def remove_process(self, process_id: str) -> bool:
        """
        Remove a process and release all its resources.

        Args:
            process_id: Unique identifier for the process

        Returns:
            bool: True if process was removed successfully, False otherwise
        """
        with self.lock:
            result = self.banker.remove_process(process_id)
            if result:
                self.process_info.pop(process_id, None)
                self._log_event("remove", process_id, {})
            return result

    def get_system_state(self) -> Dict:
        """
        Get the current state of the system.

        Returns:
            Dict: Current state including available resources, allocations, and process info
        """
        with self.lock:
            state = self.banker.get_state()
            state["process_info"] = self.process_info
            state["request_history"] = self.request_history[-100:]  # Last 100 requests
            return state

    def save_state(self) -> bool:
        """
        Save the current system state to a file.

        Returns:
            bool: True if state was saved successfully, False otherwise
        """
        try:
            with self.lock:
                state = self.get_system_state()
                with open(self.state_file, 'w') as f:
                    json.dump(state, f, indent=2)
                self.last_saved = time.time()
                return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False

    def load_state(self) -> bool:
        """
        Load system state from a file.

        Returns:
            bool: True if state was loaded successfully, False otherwise
        """
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            with self.lock:
                # Determine which resources to use
                if self.reset_on_load:
                    # Use initial resources if resetting
                    available_resources = self.initial_resources.copy()
                    if self.debug_mode:
                        print("Using initial resources instead of saved resources")
                        print(f"Initial resources: {available_resources}")
                else:
                    # Use saved resources
                    available_resources = state["available"]
                    if self.debug_mode:
                        print(f"Loaded resources from state: {available_resources}")

                # Recreate banker with appropriate resources
                self.banker = BankerAlgorithm(available_resources, debug_mode=self.debug_mode)

                # Restore processes
                for pid, max_claim in state["max_claim"].items():
                    self.banker.register_process(pid, max_claim)

                # Restore allocations only if not resetting them
                if not self.reset_allocations:
                    if self.debug_mode:
                        print("Restoring previous allocations from state")
                    for pid, allocation in state["allocation"].items():
                        for resource, amount in allocation.items():
                            if amount > 0:
                                self.banker.request_resources(pid, {resource: amount})
                else:
                    if self.debug_mode:
                        print("Resetting all allocations to 0 as requested")

                # Restore process info
                self.process_info = state.get("process_info", {})
                self.request_history = state.get("request_history", [])

                return True
        except Exception as e:
            print(f"Error loading state: {e}")
            return False

    def _log_event(self, event_type: str, process_id: str, resources: Dict[str, int],
                  success: bool = True) -> None:
        """
        Log a resource management event.

        Args:
            event_type: Type of event (register, request, release, remove)
            process_id: Unique identifier for the process
            resources: Resources involved in the event
            success: Whether the event was successful
        """
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "process_id": process_id,
            "resources": resources,
            "success": success
        }
        self.request_history.append(event)

        # If we have too many events, trim the history
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]

    def _periodic_save(self) -> None:
        """Background thread for periodic state saving."""
        while self.running:
            time.sleep(5)  # Check every 5 seconds

            current_time = time.time()
            if current_time - self.last_saved >= self.save_interval:
                self.save_state()

    def shutdown(self) -> None:
        """Shutdown the resource manager and save final state."""
        self.running = False
        if self.save_thread.is_alive():
            self.save_thread.join(timeout=2)
        self.save_state()

    def reset_resources(self) -> bool:
        """
        Reset resources to their initial values and clear all allocations.

        Returns:
            bool: True if resources were reset successfully, False otherwise
        """
        with self.lock:
            try:
                # Create a new banker with initial resources
                self.banker = BankerAlgorithm(self.initial_resources.copy(), debug_mode=self.debug_mode)

                # Clear all processes and allocations
                old_process_count = len(self.process_info)
                self.process_info = {}
                self.request_history = []

                if self.debug_mode:
                    print("Resources reset to initial values:")
                    for resource, amount in self.initial_resources.items():
                        print(f"  {resource}: {amount}")
                    print(f"Cleared {old_process_count} processes and all their allocations")
                else:
                    print("Resources and allocations reset successfully")

                return True
            except Exception as e:
                print(f"Error resetting resources: {e}")
                return False
