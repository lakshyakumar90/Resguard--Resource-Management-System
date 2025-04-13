"""
State Manager Module

This module handles state persistence and recovery for the ResGuard system.
"""

import json
import os
import time
import threading
from typing import Dict, Any, Optional


class StateManager:
    """
    Manages state persistence and recovery for the ResGuard system.
    
    This class provides functionality to save and load system state,
    create snapshots, and recover from failures.
    """
    
    def __init__(self, state_dir: str = "states"):
        """
        Initialize the state manager.
        
        Args:
            state_dir: Directory to store state files
        """
        self.state_dir = state_dir
        self.current_state_file = os.path.join(state_dir, "current_state.json")
        self.lock = threading.RLock()
        
        # Create state directory if it doesn't exist
        os.makedirs(state_dir, exist_ok=True)
        
    def save_state(self, state: Dict[str, Any]) -> bool:
        """
        Save the current system state.
        
        Args:
            state: The state to save
            
        Returns:
            bool: True if state was saved successfully, False otherwise
        """
        with self.lock:
            try:
                # Add timestamp to state
                state["saved_at"] = time.time()
                
                # Save to current state file
                with open(self.current_state_file, 'w') as f:
                    json.dump(state, f, indent=2)
                    
                return True
            except Exception as e:
                print(f"Error saving state: {e}")
                return False
                
    def create_snapshot(self, state: Dict[str, Any], name: Optional[str] = None) -> str:
        """
        Create a named snapshot of the system state.
        
        Args:
            state: The state to save
            name: Optional name for the snapshot
            
        Returns:
            str: Path to the snapshot file, or None if failed
        """
        with self.lock:
            try:
                # Generate snapshot filename
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                if name:
                    filename = f"{timestamp}-{name}.json"
                else:
                    filename = f"{timestamp}-snapshot.json"
                    
                snapshot_path = os.path.join(self.state_dir, filename)
                
                # Add metadata to state
                state["snapshot_name"] = name or "snapshot"
                state["snapshot_time"] = time.time()
                
                # Save snapshot
                with open(snapshot_path, 'w') as f:
                    json.dump(state, f, indent=2)
                    
                return snapshot_path
            except Exception as e:
                print(f"Error creating snapshot: {e}")
                return None
                
    def load_state(self) -> Dict[str, Any]:
        """
        Load the current system state.
        
        Returns:
            Dict: The loaded state, or None if failed
        """
        with self.lock:
            try:
                if not os.path.exists(self.current_state_file):
                    return None
                    
                with open(self.current_state_file, 'r') as f:
                    state = json.load(f)
                    
                return state
            except Exception as e:
                print(f"Error loading state: {e}")
                return None
                
    def load_snapshot(self, snapshot_path: str) -> Dict[str, Any]:
        """
        Load a specific snapshot.
        
        Args:
            snapshot_path: Path to the snapshot file
            
        Returns:
            Dict: The loaded state, or None if failed
        """
        with self.lock:
            try:
                if not os.path.exists(snapshot_path):
                    return None
                    
                with open(snapshot_path, 'r') as f:
                    state = json.load(f)
                    
                return state
            except Exception as e:
                print(f"Error loading snapshot: {e}")
                return None
                
    def list_snapshots(self) -> Dict[str, str]:
        """
        List all available snapshots.
        
        Returns:
            Dict: Mapping of snapshot names to file paths
        """
        with self.lock:
            snapshots = {}
            
            try:
                for filename in os.listdir(self.state_dir):
                    if filename.endswith(".json") and filename != "current_state.json":
                        path = os.path.join(self.state_dir, filename)
                        try:
                            with open(path, 'r') as f:
                                state = json.load(f)
                                name = state.get("snapshot_name", filename)
                                snapshots[name] = path
                        except:
                            # If we can't read the snapshot, skip it
                            continue
                            
                return snapshots
            except Exception as e:
                print(f"Error listing snapshots: {e}")
                return {}
