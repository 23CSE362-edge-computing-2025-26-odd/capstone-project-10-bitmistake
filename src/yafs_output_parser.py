"""
YAFS Output Parser
Parses YAFS simulation output CSV files to extract actual simulation metrics
"""

import os
import pandas as pd
import glob
from typing import Dict, List, Optional, Tuple
import statistics


class YAFSOutputParser:
    """Parse YAFS simulation output files for enhanced metrics"""
    
    def __init__(self, results_dir: str = "results"):
        self.results_dir = results_dir
        self.message_delays = []
        self.queue_lengths = []
        self.resource_usage = []
    
    def parse_simulation_results(self, simulation_prefix: str = "") -> Dict:
        """
        Parse YAFS simulation output files
        
        Args:
            simulation_prefix: Prefix to filter specific simulation files
            
        Returns:
            Dictionary containing parsed metrics
        """
        metrics = {
            "message_delays": self._parse_message_delays(simulation_prefix),
            "queue_lengths": self._parse_queue_lengths(simulation_prefix),
            "resource_usage": self._parse_resource_usage(simulation_prefix),
            "statistics": {}
        }
        
        # Calculate statistics from parsed data
        if metrics["message_delays"]:
            delays = [item["delay"] for item in metrics["message_delays"]]
            metrics["statistics"] = {
                "avg_delay": statistics.mean(delays),
                "min_delay": min(delays),
                "max_delay": max(delays),
                "p95_delay": self._calculate_percentile(delays, 95),
                "p99_delay": self._calculate_percentile(delays, 99),
                "total_messages": len(delays)
            }
        
        return metrics
    
    def _parse_message_delays(self, prefix: str = "") -> List[Dict]:
        """Parse message delay CSV files"""
        delays = []
        
        # Look for message delay files
        pattern = os.path.join(self.results_dir, f"{prefix}*message_delays*.csv")
        files = glob.glob(pattern)
        
        for file_path in files:
            try:
                df = pd.read_csv(file_path)
                for _, row in df.iterrows():
                    delays.append({
                        "message_id": row.get("message_id", ""),
                        "delay": row.get("delay", 0.0),
                        "source": row.get("source", ""),
                        "destination": row.get("destination", ""),
                        "timestamp": row.get("timestamp", 0.0)
                    })
            except Exception as e:
                print(f"[WARNING] Could not parse message delays from {file_path}: {e}")
        
        return delays
    
    def _parse_queue_lengths(self, prefix: str = "") -> List[Dict]:
        """Parse queue length CSV files"""
        queue_lengths = []
        
        # Look for queue length files
        pattern = os.path.join(self.results_dir, f"{prefix}*queue_lengths*.csv")
        files = glob.glob(pattern)
        
        for file_path in files:
            try:
                df = pd.read_csv(file_path)
                for _, row in df.iterrows():
                    queue_lengths.append({
                        "node_id": row.get("node_id", ""),
                        "queue_length": row.get("queue_length", 0),
                        "timestamp": row.get("timestamp", 0.0)
                    })
            except Exception as e:
                print(f"[WARNING] Could not parse queue lengths from {file_path}: {e}")
        
        return queue_lengths
    
    def _parse_resource_usage(self, prefix: str = "") -> List[Dict]:
        """Parse resource usage CSV files"""
        resource_usage = []
        
        # Look for resource usage files
        pattern = os.path.join(self.results_dir, f"{prefix}*resource_usage*.csv")
        files = glob.glob(pattern)
        
        for file_path in files:
            try:
                df = pd.read_csv(file_path)
                for _, row in df.iterrows():
                    resource_usage.append({
                        "node_id": row.get("node_id", ""),
                        "cpu_usage": row.get("cpu_usage", 0.0),
                        "memory_usage": row.get("memory_usage", 0.0),
                        "timestamp": row.get("timestamp", 0.0)
                    })
            except Exception as e:
                print(f"[WARNING] Could not parse resource usage from {file_path}: {e}")
        
        return resource_usage
    
    def _calculate_percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        index = min(index, len(sorted_data) - 1)
        return sorted_data[index]
    
    def get_enhanced_metrics(self, simulation_prefix: str = "") -> Dict:
        """
        Get enhanced metrics from YAFS output files
        
        Args:
            simulation_prefix: Prefix to filter specific simulation files
            
        Returns:
            Dictionary with enhanced metrics
        """
        parsed_data = self.parse_simulation_results(simulation_prefix)
        
        enhanced_metrics = {
            "actual_latency_avg": parsed_data["statistics"].get("avg_delay", 0.0),
            "actual_latency_min": parsed_data["statistics"].get("min_delay", 0.0),
            "actual_latency_max": parsed_data["statistics"].get("max_delay", 0.0),
            "actual_latency_p95": parsed_data["statistics"].get("p95_delay", 0.0),
            "actual_latency_p99": parsed_data["statistics"].get("p99_delay", 0.0),
            "total_messages_processed": parsed_data["statistics"].get("total_messages", 0),
            "message_delays": parsed_data["message_delays"],
            "queue_lengths": parsed_data["queue_lengths"],
            "resource_usage": parsed_data["resource_usage"]
        }
        
        return enhanced_metrics


def parse_yafs_output(results_dir: str = "results", simulation_prefix: str = "") -> Dict:
    """
    Convenience function to parse YAFS output files
    
    Args:
        results_dir: Directory containing YAFS output files
        simulation_prefix: Prefix to filter specific simulation files
        
    Returns:
        Dictionary with parsed metrics
    """
    parser = YAFSOutputParser(results_dir)
    return parser.get_enhanced_metrics(simulation_prefix)
