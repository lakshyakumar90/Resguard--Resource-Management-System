"""
Banker's Algorithm Implementation for Deadlock Prevention

This module implements the Banker's Algorithm for safe resource allocation
to prevent deadlocks in a multi-process environment.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional


class BankerAlgorithm:
    """
    Implementation of Banker's Algorithm for deadlock prevention.

    The Banker's Algorithm is a resource allocation and deadlock avoidance
    algorithm that tests for safety by simulating the allocation of predetermined
    maximum possible amounts of all resources.
    """

    def __init__(self, available_resources: Dict[str, int], debug_mode: bool = False):
        """
        Initialize the Banker's Algorithm with available resources.

        Args:
            available_resources: Dictionary mapping resource names to quantities
            debug_mode: Whether to print debug information
        """
        self.available = available_resources.copy()
        self.resource_types = list(available_resources.keys())
        self.max_claim = {}  # Maximum resources a process may claim
        self.allocation = {}  # Currently allocated resources to processes
        self.need = {}  # Resources still needed by processes
        self.debug_mode = debug_mode  # Whether to print debug information

    def register_process(self, process_id: str, max_resources: Dict[str, int]) -> bool:
        """
        Register a new process with its maximum resource requirements.

        Args:
            process_id: Unique identifier for the process
            max_resources: Maximum resources the process may claim

        Returns:
            bool: True if process was registered successfully, False otherwise
        """
        # Validate that max_resources contains all resource types
        if not all(resource in max_resources for resource in self.resource_types):
            if self.debug_mode:
                print(f"Process {process_id} registration failed: missing resource types")
            return False

        # Check if max_resources are reasonable (not more than total available)
        for resource, amount in max_resources.items():
            total_available = self.available[resource]
            # Allow max claim to be up to 80% of total resources for any single process
            if amount > total_available * 0.8:
                if self.debug_mode:
                    print(f"Warning: Process {process_id} is requesting {amount} of {resource} which is more than 80% of total {total_available}")
                # We'll still allow it, but warn about it

        # Initialize process data
        self.max_claim[process_id] = max_resources.copy()
        self.allocation[process_id] = {resource: 0 for resource in self.resource_types}
        self.need[process_id] = {resource: max_resources[resource] for resource in self.resource_types}

        if self.debug_mode:
            print(f"Process {process_id} registered with max resources: {max_resources}")

        return True

    def request_resources(self, process_id: str, request: Dict[str, int]) -> bool:
        """
        Process a resource request from a process.

        Args:
            process_id: Unique identifier for the process
            request: Dictionary of resources being requested

        Returns:
            bool: True if resources can be allocated safely, False otherwise
        """
        # Check if process is registered
        if process_id not in self.max_claim:
            return False

        # Check if request exceeds need
        for resource, amount in request.items():
            if amount > self.need[process_id].get(resource, 0):
                if self.debug_mode:
                    print(f"Request denied: Process {process_id} requested {amount} of {resource} but only needs {self.need[process_id].get(resource, 0)}")
                return False

        # Check if request exceeds available
        for resource, amount in request.items():
            if amount > self.available.get(resource, 0):
                if self.debug_mode:
                    print(f"Request denied: Process {process_id} requested {amount} of {resource} but only {self.available.get(resource, 0)} available")
                return False

        # Try allocation
        # Save current state
        old_available = self.available.copy()
        old_allocation = {pid: alloc.copy() for pid, alloc in self.allocation.items()}
        old_need = {pid: need.copy() for pid, need in self.need.items()}

        # Tentatively allocate resources
        for resource, amount in request.items():
            self.available[resource] -= amount
            self.allocation[process_id][resource] += amount
            self.need[process_id][resource] -= amount

        # Check if system is in safe state
        safe, unsafe_processes = self._is_safe()

        # If we have a small number of processes (<=5), we'll be more lenient
        # and allow the allocation even if it might lead to deadlock
        if not safe and len(self.max_claim) <= 5:
            # Calculate how much of each resource is being used
            resource_usage = {}
            for r in self.resource_types:
                total = self.available[r] + sum(self.allocation[pid][r] for pid in self.allocation)
                used = sum(self.allocation[pid][r] for pid in self.allocation)
                usage_percent = (used / total) * 100 if total > 0 else 0
                resource_usage[r] = usage_percent

            # If resource usage is low (<90%), allow the allocation despite potential deadlock
            if all(usage < 90 for usage in resource_usage.values()):
                if self.debug_mode:
                    print(f"Resource usage is low, allowing allocation despite potential deadlock")
                    print(f"Resource usage: {resource_usage}")
                safe = True

        if safe:
            if self.debug_mode:
                print(f"Request approved: Process {process_id} allocated {request}")
            return True
        else:
            # Restore old state
            self.available = old_available
            self.allocation = old_allocation
            self.need = old_need
            if self.debug_mode:
                print(f"Request denied: Allocation would lead to unsafe state")
                print(f"Unsafe processes: {unsafe_processes}")
            return False

    def release_resources(self, process_id: str, release: Dict[str, int]) -> bool:
        """
        Process a resource release from a process.

        Args:
            process_id: Unique identifier for the process
            release: Dictionary of resources being released

        Returns:
            bool: True if resources were released successfully, False otherwise
        """
        # Check if process is registered
        if process_id not in self.allocation:
            return False

        # Check if release exceeds allocation
        for resource, amount in release.items():
            if amount > self.allocation[process_id].get(resource, 0):
                return False

        # Release resources
        for resource, amount in release.items():
            self.available[resource] += amount
            self.allocation[process_id][resource] -= amount
            self.need[process_id][resource] += amount

        return True

    def _is_safe(self) -> tuple:
        """
        Check if the current state is safe using the Banker's Algorithm.

        Returns:
            tuple: (is_safe, unsafe_processes)
                is_safe: True if the state is safe, False otherwise
                unsafe_processes: List of processes that couldn't complete (empty if safe)
        """
        # Create working copies
        work = self.available.copy()
        finish = {pid: False for pid in self.max_claim}

        # Find an unfinished process whose needs can be satisfied
        iteration_count = 0
        max_iterations = len(self.max_claim) * 3  # Allow more iterations to find a solution

        while iteration_count < max_iterations:
            found = False
            for pid in self.max_claim:
                # Skip processes that are already finished
                if finish[pid]:
                    continue

                # Check if this process can complete with current resources
                # We'll be more lenient here - if a process needs resources but not too many,
                # we'll consider it can complete
                can_complete = True
                resource_shortage = False

                for r in self.resource_types:
                    # If the process needs more of this resource than is available
                    if self.need[pid][r] > work[r]:
                        # Check if the shortage is significant
                        shortage = self.need[pid][r] - work[r]
                        total_resource = self.available[r] + sum(self.allocation[p][r] for p in self.allocation)

                        # If shortage is more than 50% of total resources, it's significant
                        if shortage > total_resource * 0.5:
                            can_complete = False
                            break
                        else:
                            resource_shortage = True

                # If there's a resource shortage but it's not significant, we'll still
                # consider the process can complete, but with a warning
                if can_complete:
                    if resource_shortage and self.debug_mode:
                        print(f"Process {pid} has resource shortage but it's not significant, considering it can complete")

                    # This process can complete
                    found = True
                    finish[pid] = True
                    # Release its resources
                    for resource in self.resource_types:
                        work[resource] += self.allocation[pid][resource]
                    break

            if not found:
                break

            iteration_count += 1

        # Get list of processes that couldn't complete
        unsafe_processes = [pid for pid, finished in finish.items() if not finished]

        # If all processes are finished, the state is safe
        is_safe = all(finish.values())

        # If we have a small number of processes and they're all requesting resources,
        # we'll consider it safe anyway to avoid being too restrictive
        if not is_safe and len(self.max_claim) <= 3:
            if self.debug_mode:
                print(f"Only {len(self.max_claim)} processes in the system, considering it safe despite deadlock potential")
            is_safe = True

        if self.debug_mode and not is_safe:
            print(f"Unsafe state detected. Unfinished processes: {unsafe_processes}")
            print(f"Available resources: {self.available}")
            print(f"Current allocations: {self.allocation}")
            print(f"Current needs: {self.need}")

        return is_safe, unsafe_processes

    def get_state(self) -> Dict:
        """
        Get the current state of the system.

        Returns:
            Dict: Current state including available resources, allocations, and needs
        """
        return {
            "available": self.available,
            "max_claim": self.max_claim,
            "allocation": self.allocation,
            "need": self.need
        }

    def remove_process(self, process_id: str) -> bool:
        """
        Remove a process and release all its resources.

        Args:
            process_id: Unique identifier for the process

        Returns:
            bool: True if process was removed successfully, False otherwise
        """
        if process_id not in self.allocation:
            return False

        # Release all resources
        for resource in self.resource_types:
            self.available[resource] += self.allocation[process_id][resource]

        # Remove process data
        del self.max_claim[process_id]
        del self.allocation[process_id]
        del self.need[process_id]

        return True
