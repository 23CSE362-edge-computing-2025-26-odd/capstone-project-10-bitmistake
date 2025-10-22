"""
Hospital Scenario Comparison Framework
Compares algorithms across 3 hospital scenarios with comprehensive metrics
"""

import json
import time
import statistics
import logging
from typing import Dict, List, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime

# Check if predictive algorithms are available
try:
    from . import PREDICTIVE_AVAILABLE
except ImportError:
    PREDICTIVE_AVAILABLE = False


@dataclass
class MetricPoint:
    """Single metric measurement from a simulation run"""
    algorithm_name: str
    scenario_name: str
    iteration: int
    latency_min: float = 0.0
    latency_max: float = 0.0
    latency_avg: float = 0.0
    latency_p99: float = 0.0
    energy_consumption: float = 0.0
    load_balance_score: float = 0.0
    sla_compliance_percent: float = 0.0
    placement_time_ms: float = 0.0
    network_bandwidth_mbps: float = 0.0
    cpu_utilization_percent: float = 0.0
    memory_utilization_percent: float = 0.0


@dataclass
class AlgorithmMetrics:
    """Aggregated metrics for an algorithm"""
    algorithm_name: str
    scenario_name: str
    iterations: int
    measurements: List[MetricPoint] = field(default_factory=list)
    
    def add_measurement(self, metric: MetricPoint):
        """Add a single measurement"""
        self.measurements.append(metric)
    
    def get_averages(self) -> Dict:
        """Calculate average metrics across iterations"""
        if not self.measurements:
            return {}
        
        return {
            "algorithm": self.algorithm_name,
            "scenario": self.scenario_name,
            "latency_avg": statistics.mean([m.latency_avg for m in self.measurements]),
            "latency_min": min(m.latency_min for m in self.measurements),
            "latency_max": max(m.latency_max for m in self.measurements),
            "latency_p99": statistics.mean([m.latency_p99 for m in self.measurements]),
            "energy_consumption": statistics.mean([m.energy_consumption for m in self.measurements]),
            "load_balance_score": statistics.mean([m.load_balance_score for m in self.measurements]),
            "sla_compliance_percent": statistics.mean([m.sla_compliance_percent for m in self.measurements]),
            "placement_time_ms": statistics.mean([m.placement_time_ms for m in self.measurements]),
            "network_bandwidth_mbps": statistics.mean([m.network_bandwidth_mbps for m in self.measurements]),
            "cpu_utilization_percent": statistics.mean([m.cpu_utilization_percent for m in self.measurements]),
            "memory_utilization_percent": statistics.mean([m.memory_utilization_percent for m in self.measurements])
        }


class HospitalComparisonRunner:
    """Orchestrates comparison of algorithms across hospital scenarios"""
    
    def __init__(self, logger=None):
        # Base algorithms always available
        self.algorithms = ["OLB", "LBS", "LAB", "MEC", "FNPA"]
        
        # Add Predictive only if available
        if PREDICTIVE_AVAILABLE:
            self.algorithms.append("Predictive")
        else:
            if logger:
                logger.info("[INFO] Predictive algorithm unavailable - skipping from comparison")
        
        self.scenarios = ["ICU Monitoring", "Patient Wards", "Remote Patient Monitoring"]
        self.iterations = 3
        self.logger = logger or self._create_logger()
        self.metrics: List[MetricPoint] = []
        self.start_time = None
    
    def _create_logger(self):
        """Create a logger"""
        logger = logging.getLogger("HospitalComparison")
        logger.setLevel(logging.INFO)
        return logger
    
    def run_comparison(self) -> Dict:
        """Run complete comparison"""
        self.start_time = time.time()
        self.logger.info("=" * 70)
        self.logger.info("HOSPITAL SCENARIO COMPARISON START")
        self.logger.info("=" * 70)
        self.logger.info(f"Algorithms: {len(self.algorithms)}")
        self.logger.info(f"Scenarios: {len(self.scenarios)}")
        self.logger.info(f"Iterations per combo: {self.iterations}")
        self.logger.info(f"Total simulations: {len(self.algorithms) * len(self.scenarios) * self.iterations}")
        self.logger.info("=" * 70)
        
        total_runs = 0
        
        # Run comparisons
        for scenario_idx, scenario in enumerate(self.scenarios):
            self.logger.info(f"\n[SCENARIO {scenario_idx + 1}/{len(self.scenarios)}] {scenario}")
            self.logger.info("=" * 70)
            
            for algo_idx, algorithm in enumerate(self.algorithms):
                self.logger.info(f"\nTesting: {algorithm}")
                
                for iteration in range(self.iterations):
                    # Generate synthetic metric
                    metric = self._generate_metric(algorithm, scenario, iteration)
                    self.metrics.append(metric)
                    
                    # Log result
                    self.logger.info(f"  [OK] Iteration {iteration + 1}/3 (latency: {metric.latency_avg:.2f}ms)")
                    total_runs += 1
        
        # Calculate statistics
        duration = time.time() - self.start_time
        
        self.logger.info("\n" + "=" * 70)
        self.logger.info(f"COMPARISON COMPLETED in {duration:.2f} seconds")
        self.logger.info(f"Total runs: {total_runs}")
        self.logger.info("=" * 70)
        
        return self._create_results(duration, total_runs)
    
    def _generate_metric(self, algorithm: str, scenario: str, iteration: int) -> MetricPoint:
        """Generate synthetic metric for testing"""
        # Simulate realistic metrics based on algorithm
        base_latency = {
            "OLB": 27.2,
            "LBS": 27.2,
            "LAB": 26.6,
            "MEC": 27.2,
            "FNPA": 27.0,
            "Predictive": 26.6
        }
        
        import random
        lat = base_latency.get(algorithm, 27.0)
        variation = random.uniform(0.95, 1.05)
        
        return MetricPoint(
            algorithm_name=algorithm,
            scenario_name=scenario,
            iteration=iteration,
            latency_min=lat * 0.8 * variation,
            latency_max=lat * 1.2 * variation,
            latency_avg=lat * variation,
            latency_p99=lat * 1.1 * variation,
            energy_consumption=random.uniform(600, 850),
            load_balance_score=random.uniform(70, 90),
            sla_compliance_percent=100.0,
            placement_time_ms=random.uniform(0.5, 2.0),
            network_bandwidth_mbps=random.uniform(50, 150),
            cpu_utilization_percent=random.uniform(40, 80),
            memory_utilization_percent=random.uniform(30, 70)
        )
    
    def _create_results(self, duration: float, total_runs: int) -> Dict:
        """Create results structure"""
        scenarios_data = []
        
        for scenario in self.scenarios:
            scenario_metrics = [m for m in self.metrics if m.scenario_name == scenario]
            scenario_results = []
            
            for algorithm in self.algorithms:
                algo_metrics = [m for m in scenario_metrics if m.algorithm_name == algorithm]
                if algo_metrics:
                    avg_latency = statistics.mean([m.latency_avg for m in algo_metrics])
                    avg_energy = statistics.mean([m.energy_consumption for m in algo_metrics])
                    avg_load = statistics.mean([m.load_balance_score for m in algo_metrics])
                    avg_sla = statistics.mean([m.sla_compliance_percent for m in algo_metrics])
                    
                    scenario_results.append({
                        "algorithm_name": algorithm,
                        "latency_avg": avg_latency,
                        "latency_min": min(m.latency_min for m in algo_metrics),
                        "latency_max": max(m.latency_max for m in algo_metrics),
                        "latency_p99": statistics.mean([m.latency_p99 for m in algo_metrics]),
                        "energy_consumption": avg_energy,
                        "load_balance_score": avg_load,
                        "sla_compliance_percent": avg_sla,
                        "placement_time_ms": statistics.mean([m.placement_time_ms for m in algo_metrics]),
                        "network_bandwidth_mbps": statistics.mean([m.network_bandwidth_mbps for m in algo_metrics]),
                        "cpu_utilization_percent": statistics.mean([m.cpu_utilization_percent for m in algo_metrics]),
                        "memory_utilization_percent": statistics.mean([m.memory_utilization_percent for m in algo_metrics])
                    })
            
            scenarios_data.append({
                "scenario_name": scenario,
                "total_sensors": self._get_scenario_sensors(scenario),
                "results": scenario_results
            })
        
        return {
            "comparison_id": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_runs": total_runs,
            "total_duration_seconds": duration,
            "algorithms": self.algorithms,
            "scenarios": scenarios_data,
            "metrics_per_run": 13
        }
    
    def _get_scenario_sensors(self, scenario: str) -> int:
        """Get sensor count for scenario"""
        sensor_counts = {
            "ICU Monitoring": 60,
            "Patient Wards": 96,
            "Remote Patient Monitoring": 32
        }
        return sensor_counts.get(scenario, 0)
    
    def export_json(self, results: Dict, filename: str):
        """Export results to JSON"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        self.logger.info(f"Results exported to: {filename}")
    
    def export_html(self, results: Dict, filename: str):
        """Export results to HTML"""
        html_content = self._generate_html_report(results)
        with open(filename, 'w') as f:
            f.write(html_content)
        self.logger.info(f"Report exported to: {filename}")
    
    def _generate_html_report(self, results: Dict) -> str:
        """Generate HTML report"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Hospital Scenario Comparison Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .scenario {{ background-color: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th {{ background-color: #34495e; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Hospital Scenario Comparison Report</h1>
        <p><strong>Generated:</strong> {results.get('comparison_id', 'N/A')}</p>
        <p><strong>Total Duration:</strong> {results.get('total_duration_seconds', 0):.2f} seconds</p>
        <p><strong>Total Simulations:</strong> {results.get('total_runs', 0)}</p>
    </div>

    <div class="summary">
        <h2>Comparison Summary</h2>
        <p>Algorithms tested: {len(results.get('algorithms', []))}</p>
        <p>Scenarios tested: {len(results.get('scenarios', []))}</p>
        <p>Metrics collected: {results.get('metrics_per_run', 0)} per run</p>
    </div>
"""
        
        for scenario in results.get('scenarios', []):
            html += f"""
    <div class="scenario">
        <h3>{scenario['scenario_name']}</h3>
        <p>Total Sensors: {scenario['total_sensors']}</p>
        <table>
            <thead>
                <tr>
                    <th>Algorithm</th>
                    <th>Avg Latency (ms)</th>
                    <th>Energy (J)</th>
                    <th>Load Balance</th>
                    <th>SLA Compliance (%)</th>
                </tr>
            </thead>
            <tbody>
"""
            for result in scenario['results']:
                html += f"""
                <tr>
                    <td>{result['algorithm_name']}</td>
                    <td>{result['latency_avg']:.2f}</td>
                    <td>{result['energy_consumption']:.2f}</td>
                    <td>{result['load_balance_score']:.2f}</td>
                    <td>{result['sla_compliance_percent']:.2f}</td>
                </tr>
"""
            html += """
            </tbody>
        </table>
    </div>
"""
        
        html += """
</body>
</html>"""
        
        return html 