"""
Resource Usage Analyzer Module

This module provides functionality to analyze resource usage patterns
and predict future resource needs.
"""

import pandas as pd
import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple


class ResourceAnalyzer:
    """
    Analyzes resource usage patterns and predicts future needs.
    
    This class uses historical data to identify patterns in resource usage
    and make predictions about future resource requirements.
    """
    
    def __init__(self, history_size: int = 1000):
        """
        Initialize the resource analyzer.
        
        Args:
            history_size: Maximum number of historical data points to keep
        """
        self.history_size = history_size
        self.usage_history = pd.DataFrame(columns=[
            'timestamp', 'process_id', 'resource_type', 'amount', 'operation'
        ])
        
    def add_usage_event(self, process_id: str, resource_type: str, 
                       amount: int, operation: str) -> None:
        """
        Add a resource usage event to the history.
        
        Args:
            process_id: ID of the process
            resource_type: Type of resource
            amount: Amount of resource
            operation: Operation type (request, release)
        """
        event = pd.DataFrame({
            'timestamp': [time.time()],
            'process_id': [process_id],
            'resource_type': [resource_type],
            'amount': [amount],
            'operation': [operation]
        })
        
        self.usage_history = pd.concat([self.usage_history, event], ignore_index=True)
        
        # Trim history if needed
        if len(self.usage_history) > self.history_size:
            self.usage_history = self.usage_history.iloc[-self.history_size:]
            
    def add_usage_events(self, events: List[Dict[str, Any]]) -> None:
        """
        Add multiple resource usage events to the history.
        
        Args:
            events: List of event dictionaries
        """
        for event in events:
            self.add_usage_event(
                event['process_id'],
                event['resource_type'],
                event['amount'],
                event['operation']
            )
            
    def get_resource_usage_by_type(self) -> Dict[str, pd.DataFrame]:
        """
        Get resource usage statistics grouped by resource type.
        
        Returns:
            Dict: Resource usage statistics by type
        """
        if self.usage_history.empty:
            return {}
            
        result = {}
        for resource_type in self.usage_history['resource_type'].unique():
            resource_data = self.usage_history[
                self.usage_history['resource_type'] == resource_type
            ]
            
            # Calculate net usage (requests - releases)
            net_usage = resource_data.copy()
            net_usage.loc[net_usage['operation'] == 'release', 'amount'] *= -1
            
            # Group by timestamp (rounded to minute) and sum
            net_usage['minute'] = net_usage['timestamp'].apply(
                lambda x: int(x / 60) * 60
            )
            usage_by_minute = net_usage.groupby('minute')['amount'].sum().reset_index()
            
            result[resource_type] = usage_by_minute
            
        return result
        
    def get_process_resource_usage(self, process_id: str) -> pd.DataFrame:
        """
        Get resource usage for a specific process.
        
        Args:
            process_id: ID of the process
            
        Returns:
            DataFrame: Resource usage for the process
        """
        if self.usage_history.empty:
            return pd.DataFrame()
            
        process_data = self.usage_history[
            self.usage_history['process_id'] == process_id
        ]
        
        return process_data
        
    def predict_resource_needs(self, resource_type: str, 
                              time_horizon: int = 300) -> Dict[str, Any]:
        """
        Predict future resource needs for a specific resource type.
        
        Args:
            resource_type: Type of resource
            time_horizon: Time horizon for prediction in seconds
            
        Returns:
            Dict: Prediction results
        """
        if self.usage_history.empty:
            return {
                'resource_type': resource_type,
                'predicted_usage': 0,
                'confidence': 0.0
            }
            
        # Get usage data for the resource type
        resource_data = self.usage_history[
            self.usage_history['resource_type'] == resource_type
        ]
        
        if resource_data.empty:
            return {
                'resource_type': resource_type,
                'predicted_usage': 0,
                'confidence': 0.0
            }
            
        # Calculate net usage (requests - releases)
        net_usage = resource_data.copy()
        net_usage.loc[net_usage['operation'] == 'release', 'amount'] *= -1
        
        # Group by timestamp (rounded to minute) and sum
        net_usage['minute'] = net_usage['timestamp'].apply(
            lambda x: int(x / 60) * 60
        )
        usage_by_minute = net_usage.groupby('minute')['amount'].sum().reset_index()
        
        # If we don't have enough data, return a simple average
        if len(usage_by_minute) < 5:
            avg_usage = usage_by_minute['amount'].mean()
            return {
                'resource_type': resource_type,
                'predicted_usage': int(avg_usage) if not np.isnan(avg_usage) else 0,
                'confidence': 0.5
            }
            
        # Simple moving average prediction
        window_size = min(5, len(usage_by_minute))
        recent_usage = usage_by_minute['amount'].iloc[-window_size:].mean()
        
        # Calculate standard deviation for confidence
        std_dev = usage_by_minute['amount'].std()
        max_std = usage_by_minute['amount'].max() / 2 if usage_by_minute['amount'].max() > 0 else 1
        normalized_std = min(std_dev / max_std, 1) if not np.isnan(std_dev) else 0.5
        confidence = 1.0 - normalized_std
        
        return {
            'resource_type': resource_type,
            'predicted_usage': int(recent_usage) if not np.isnan(recent_usage) else 0,
            'confidence': confidence
        }
        
    def get_usage_patterns(self) -> Dict[str, Any]:
        """
        Identify usage patterns in the historical data.
        
        Returns:
            Dict: Usage patterns
        """
        if self.usage_history.empty:
            return {'patterns': []}
            
        patterns = []
        
        # Analyze by resource type
        for resource_type in self.usage_history['resource_type'].unique():
            resource_data = self.usage_history[
                self.usage_history['resource_type'] == resource_type
            ]
            
            # Calculate request frequency
            requests = resource_data[resource_data['operation'] == 'request']
            if len(requests) > 1:
                # Calculate time differences between requests
                requests = requests.sort_values('timestamp')
                time_diffs = requests['timestamp'].diff().dropna()
                
                if not time_diffs.empty:
                    avg_interval = time_diffs.mean()
                    
                    patterns.append({
                        'resource_type': resource_type,
                        'avg_request_interval': avg_interval,
                        'avg_request_size': requests['amount'].mean(),
                        'request_count': len(requests)
                    })
                    
        return {'patterns': patterns}
        
    def recommend_allocation(self) -> Dict[str, Dict[str, int]]:
        """
        Recommend resource allocation based on historical data.
        
        Returns:
            Dict: Recommended allocations by resource type
        """
        recommendations = {}
        
        for resource_type in self.usage_history['resource_type'].unique():
            prediction = self.predict_resource_needs(resource_type)
            
            # Add a safety margin based on confidence
            safety_margin = 1.0 + (1.0 - prediction['confidence'])
            recommended = int(prediction['predicted_usage'] * safety_margin)
            
            recommendations[resource_type] = {
                'recommended': recommended,
                'predicted': prediction['predicted_usage'],
                'confidence': prediction['confidence']
            }
            
        return recommendations
