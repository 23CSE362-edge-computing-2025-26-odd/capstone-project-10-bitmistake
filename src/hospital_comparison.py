import json
import time
import statistics
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
try:
    from . import PREDICTIVE_AVAILABLE
except ImportError:
    PREDICTIVE_AVAILABLE = False

from .environment import DigitalTwinEnvironment
from .hospital_scenarios_extended import ScenarioManager
from .yafs_integration import create_smart_healthcare_application, create_yafs_topology
from .metrics import PerformanceMetrics
from .utils import create_placement_json

# Import placement algorithms
from .olb_algorithm import OLBPlacement
from .comparison_algorithms import LBS, LAB, MEC, FNPA


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
    
    def __init__(self, simulation_time: int = 100):
        # Base algorithms always available
        self.algorithms = ["OLB", "LBS", "LAB", "MEC", "FNPA"]
        
        # Add Predictive only if available AND properly configured
        if PREDICTIVE_AVAILABLE:
            try:
                # Test if Predictive can actually be instantiated
                from .predictive_placement import PredictiveLatencyPlacement
                # Check if TFLite models exist
                import os
                model_dir = os.path.join(os.path.dirname(__file__), '..', 'CI_Models', 'Workload', 'models')
                if os.path.exists(model_dir) and os.listdir(model_dir):
                    self.algorithms.append("Predictive")
                    print("[INFO] Predictive algorithm enabled with LSTM models")
                else:
                    print("[WARNING] Predictive algorithm disabled - LSTM models not found")
                    print(f"[INFO] Expected model directory: {model_dir}")
            except Exception as e:
                print(f"[WARNING] Predictive algorithm disabled - initialization failed: {e}")
        else:
            print("[INFO] Predictive algorithm unavailable - skipping from comparison")
        
        self.scenarios = ["ICU Monitoring", "Patient Wards", "Remote Patient Monitoring"]
        self.iterations = 3
        self.simulation_time = simulation_time
        self.metrics: List[MetricPoint] = []
        self.start_time = None
        
        # Initialize components for real simulation
        self.scenario_manager = ScenarioManager()
        self.placement_config = None
    
    def run_comparison(self) -> Dict:
        """Run complete comparison with REAL YAFS simulations"""
        self.start_time = time.time()
        print("=" * 70)
        print("HOSPITAL SCENARIO COMPARISON START (REAL SIMULATIONS)")
        print("=" * 70)
        print(f"Algorithms: {len(self.algorithms)}")
        print(f"Scenarios: {len(self.scenarios)}")
        print(f"Iterations per combo: {self.iterations}")
        print(f"Total simulations: {len(self.algorithms) * len(self.scenarios) * self.iterations}")
        print(f"Simulation time per run: {self.simulation_time} time units")
        print("=" * 70)
        
        # Create placement config once
        self.placement_config = create_placement_json("config")
        
        # Get all hospital scenarios
        all_scenarios = self.scenario_manager.get_all_scenarios()
        scenario_map = {s.name: s for s in all_scenarios}
        
        total_runs = 0
        
        # Run comparisons with error handling
        for scenario_idx, scenario_name in enumerate(self.scenarios):
            print(f"\n[SCENARIO {scenario_idx + 1}/{len(self.scenarios)}] {scenario_name}")
            print("=" * 70)
            
            # Get scenario object
            scenario = scenario_map.get(scenario_name)
            if not scenario:
                print(f"ERROR: Scenario '{scenario_name}' not found!")
                continue
            
            for algo_idx, algorithm in enumerate(self.algorithms):
                print(f"\nTesting: {algorithm}")
                
                for iteration in range(self.iterations):
                    try:
                        # Run REAL simulation
                        metric = self._run_real_simulation(algorithm, scenario, iteration)
                        
                        if metric:
                            self.metrics.append(metric)
                            print(f"  [OK] Iteration {iteration + 1}/{self.iterations} "
                                  f"(latency: {metric.latency_avg:.2f}ms, "
                                  f"energy: {metric.energy_consumption:.2f}J, "
                                  f"load_balance: {metric.load_balance_score:.3f})")
                            total_runs += 1
                        else:
                            print(f"  [FAIL] Iteration {iteration + 1}/{self.iterations} returned None")
                            print(f"  [INFO] Check if algorithm {algorithm} is properly implemented")
                    except ValueError as e:
                        # Catch placement failures specifically
                        print(f"  [ERROR] Iteration {iteration + 1}/{self.iterations} - Placement failed: {e}")
                        print(f"  [INFO] Algorithm {algorithm} may not be compatible with scenario {scenario_name}")
                    except Exception as e:
                        print(f"  [ERROR] Iteration {iteration + 1}/{self.iterations} crashed: {e}")
                        import traceback
                        traceback.print_exc()
                        # Continue with next iteration instead of crashing entire comparison
        
        # Calculate statistics
        duration = time.time() - self.start_time
        
        print("\n" + "=" * 70)
        print(f"COMPARISON COMPLETED in {duration:.2f} seconds")
        print(f"Total successful runs: {total_runs}")
        print("=" * 70)
        
        # Print summary statistics
        self._print_comparison_summary()
        
        return self._create_results(duration, total_runs)
    
    def _print_comparison_summary(self):
        """Print detailed comparison summary"""
        print("\n" + "=" * 70)
        print("COMPARISON SUMMARY")
        print("=" * 70)
        
        for scenario in self.scenarios:
            scenario_metrics = [m for m in self.metrics if m.scenario_name == scenario]
            if not scenario_metrics:
                print(f"\n{scenario}: NO DATA")
                continue
            
            print(f"\n{scenario}:")
            print(f"{'Algorithm':<15} {'Latency (ms)':<15} {'Energy (J)':<15} {'Load Balance':<15}")
            print("-" * 70)
            
            for algorithm in self.algorithms:
                algo_metrics = [m for m in scenario_metrics if m.algorithm_name == algorithm]
                if algo_metrics:
                    avg_latency = statistics.mean([m.latency_avg for m in algo_metrics])
                    avg_energy = statistics.mean([m.energy_consumption for m in algo_metrics])
                    avg_load = statistics.mean([m.load_balance_score for m in algo_metrics])
                    print(f"{algorithm:<15} {avg_latency:<15.2f} {avg_energy:<15.2f} {avg_load:<15.3f}")
                else:
                    print(f"{algorithm:<15} {'NO DATA':<15} {'NO DATA':<15} {'NO DATA':<15}")
        
        print("\n" + "=" * 70)
    
    def _run_real_simulation(
        self, 
        algorithm_name: str, 
        scenario, 
        iteration: int
    ) -> Optional[MetricPoint]:
        """
        Run REAL YAFS simulation for given algorithm and scenario.
        Replaces synthetic metric generation.
        """
        try:
            placement_start = time.time()
            
            # 1. Convert scenario to environment
            environment = DigitalTwinEnvironment.from_scenario(scenario)
            
            # 2. Create YAFS application and topology
            app = create_smart_healthcare_application(environment)
            topology = create_yafs_topology(environment)
            
            # 3. Get placement algorithm instance
            placement_class = self._get_placement_class(algorithm_name)
            if not placement_class:
                print(f"ERROR: Unknown algorithm: {algorithm_name}")
                return None
            
            placement = placement_class(
                name=f"{algorithm_name}_{scenario.name}_{iteration}",
                json_file=self.placement_config,
                digital_twin=environment
            )
            
            # 4. Run YAFS simulation
            try:
                from yafs.core import Sim
                from yafs.population import Population
                
                sim = Sim(topology, default_results_path="results/")
                population = Population(name=f"Hospital_{scenario.name}")
                
                # Deploy and run
                sim.deploy_app(app, placement, population)
                sim.run(until=self.simulation_time)
                
                placement_time = (time.time() - placement_start) * 1000  # Convert to ms
                
                # 5. Collect real metrics
                metrics_collector = PerformanceMetrics()
                metrics_collector.collect_metrics(environment, placement, algorithm_name)
                
                # 6. Extract metrics from collector
                summary = metrics_collector.get_summary_dict()
                
                # 7. Create MetricPoint from real data
                # Extract per-task latencies for proper averaging
                per_task_latencies = summary.get("per_task_latencies", [])
                
                if per_task_latencies:
                    # Use actual per-task latencies for accurate metrics
                    import statistics
                    avg_latency = statistics.mean(per_task_latencies)
                    min_latency = min(per_task_latencies)
                    max_latency = max(per_task_latencies)
                    sorted_latencies = sorted(per_task_latencies)
                    p99_index = int(len(sorted_latencies) * 0.99)
                    p99_latency = sorted_latencies[p99_index] if p99_index < len(sorted_latencies) else sorted_latencies[-1]
                else:
                    # Fallback to summary metrics if per-task data unavailable
                    num_assignments = summary.get("num_assignments", 1)
                    avg_latency = summary.get("overall_latency", 0.0) / max(num_assignments, 1)
                    min_latency = summary.get("latency_min", 0.0)
                    max_latency = summary.get("latency_max", 0.0)
                    p99_latency = summary.get("latency_p99", max_latency)
                
                metric = MetricPoint(
                    algorithm_name=algorithm_name,
                    scenario_name=scenario.name,
                    iteration=iteration,
                    latency_min=min_latency,
                    latency_max=max_latency,
                    latency_avg=avg_latency,  # Use true average per task
                    latency_p99=p99_latency,
                    energy_consumption=summary.get("energy_consumption", 0.0),
                    load_balance_score=summary.get("load_balance_score", 0.0),
                    sla_compliance_percent=summary.get("sla_compliance_percent", 100.0),
                    placement_time_ms=placement_time,
                    network_bandwidth_mbps=summary.get("network_usage", 0.0),
                    cpu_utilization_percent=summary.get("cpu_utilization", 0.0),
                    memory_utilization_percent=summary.get("memory_utilization", 0.0)
                )
                
                return metric

            except ImportError as e:
                print(f"ERROR: YAFS not available: {e}")
                return None
            except Exception as e:
                print(f"ERROR: Simulation failed: {e}")
                import traceback
                traceback.print_exc()
                return None
        
        except Exception as e:
            print(f"ERROR: Failed to run simulation for {algorithm_name}/{scenario.name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_placement_class(self, algorithm_name: str):
        """Get placement algorithm class by name"""
        algorithm_map = {
            "OLB": OLBPlacement,
            "LBS": LBS,
            "LAB": LAB,
            "MEC": MEC,
            "FNPA": FNPA,
        }
        
        # Add predictive if available
        if PREDICTIVE_AVAILABLE and algorithm_name == "Predictive":
            try:
                from .predictive_placement import PredictiveLatencyPlacement
                return PredictiveLatencyPlacement
            except ImportError:
                return None
        
        return algorithm_map.get(algorithm_name)
    
    def _create_results(self, duration: float, total_runs: int) -> Dict:
        """Create results structure"""
        scenarios_data = []
        
        # Debug: Log all collected metrics
        print("\n" + "=" * 70)
        print("DEBUG: Collected Metrics Summary")
        print("=" * 70)
        for metric in self.metrics:
            print(f"  {metric.algorithm_name:15} | {metric.scenario_name:25} | "
                  f"Iter {metric.iteration} | Latency: {metric.latency_avg:8.2f}ms")
        
        # Debug: Count metrics by algorithm
        algo_counts = {}
        for metric in self.metrics:
            algo_counts[metric.algorithm_name] = algo_counts.get(metric.algorithm_name, 0) + 1
        print("\nMetrics per Algorithm:")
        for algo in self.algorithms:
            count = algo_counts.get(algo, 0)
            print(f"  {algo}: {count} metrics")
        print("=" * 70 + "\n")
        
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
                else:
                    print(f"[WARNING] No metrics found for {algorithm} in {scenario}")
            
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
        print(f"Results exported to: {filename}")
    
    def export_html(self, results: Dict, filename: str):
        """Export results to HTML"""
        html_content = self._generate_html_report(results)
        with open(filename, 'w') as f:
            f.write(html_content)
        print(f"Report exported to: {filename}")
    
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