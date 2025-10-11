import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "CI_Models"))

from src import (
    DigitalTwinEnvironment,
    OLBPlacement,
    PerformanceMetrics,
    SimulationConfig,
    create_placement_json,
    create_smart_healthcare_application,
    create_yafs_topology,
)
from src.workload_models import DynamicWorkloadGenerator, HealthcareWorkloadPattern

try:
    from Workload.predict import WorkloadPredictor
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False
    print("LSTM predictor not available, skipping LSTM-based tests")


class WorkloadAwareOLBPlacement(OLBPlacement):
    def __init__(self, name, json_file, digital_twin, workload_generator=None):
        super().__init__(name, json_file, digital_twin)
        self.workload_generator = workload_generator
        self.workload_history = []

    def initial_allocation(self, sim, app_name):
        if self.workload_generator:
            for sensor in self.digital_twin.sensors:
                multiplier = self.workload_generator.apply_to_sensor(sensor)
                self.workload_history.append({
                    'sensor_id': sensor.device_id,
                    'multiplier': multiplier,
                    'new_flow_rate': sensor.averageFlowRate
                })
        
        super().initial_allocation(sim, app_name)


class LSTMPredictiveOLBPlacement(OLBPlacement):
    def __init__(self, name, json_file, digital_twin, workload_predictions):
        super().__init__(name, json_file, digital_twin)
        self.workload_predictions = workload_predictions
        self._apply_predictions_to_fog_nodes()

    def _apply_predictions_to_fog_nodes(self):
        for i, fog_node in enumerate(self.digital_twin.fog_nodes):
            node_name = f"system-{i+1}"
            if node_name in self.workload_predictions:
                predicted_load = self.workload_predictions[node_name]['predicted_avg']
                adjustment_factor = max(0.3, 1.0 - (predicted_load / 100.0))
                fog_node.processingPower *= adjustment_factor
                print(f"Adjusted {node_name}: capacity={fog_node.processingPower:.2f}, factor={adjustment_factor:.2f}")


def run_workload_pattern_comparison():
    print("=== WORKLOAD PATTERN COMPARISON STUDY ===\n")
    
    config = SimulationConfig()
    workload_patterns = {
        "steady": DynamicWorkloadGenerator("steady"),
        "periodic": DynamicWorkloadGenerator("periodic"),
        "bursty": DynamicWorkloadGenerator("bursty"),
        "increasing": DynamicWorkloadGenerator("increasing"),
    }
    
    results = {}
    
    for pattern_name, workload_gen in workload_patterns.items():
        print(f"\nRunning OLB with {pattern_name} workload pattern...")
        
        environment = DigitalTwinEnvironment(config.environment_width, config.environment_height)
        environment.initialize_sensors(config.num_sensors, config.random_seed)
        environment.initialize_fog_nodes(config.num_fog_nodes, config.random_seed)
        environment.initialize_cloud()
        
        app = create_smart_healthcare_application(environment)
        topology = create_yafs_topology(environment)
        placement_json = create_placement_json("config")
        
        placement = WorkloadAwareOLBPlacement(
            f"OLB_{pattern_name}",
            placement_json,
            environment,
            workload_gen
        )
        
        try:
            from yafs.core import Sim
            from yafs.population import Population
            
            s = Sim(topology, default_results_path="../results/")
            population = Population(name=f"{pattern_name}Sensors")
            s.deploy_app(app, placement, population)
            s.run(until=config.simulation_time)
            
            metrics = PerformanceMetrics()
            metrics.collect_metrics(environment, placement, f"OLB_{pattern_name}")
            
            result = metrics.get_summary_dict()
            result['workload_pattern'] = pattern_name
            result['workload_history'] = placement.workload_history[:10]
            
            results[pattern_name] = result
            print(f"  Latency: {result['overall_latency']:.2f}ms")
            print(f"  Energy: {result['energy_consumption']:.2f}W")
            
        except Exception as e:
            print(f"  Failed: {e}")
            continue
    
    return results


def run_healthcare_workload_comparison():
    print("\n=== HEALTHCARE SCENARIO WORKLOAD COMPARISON ===\n")
    
    config = SimulationConfig()
    healthcare_patterns = {
        "icu": HealthcareWorkloadPattern("icu"),
        "emergency": HealthcareWorkloadPattern("emergency"),
        "ambulatory": HealthcareWorkloadPattern("ambulatory"),
    }
    
    results = {}
    
    for scenario_name, workload_pattern in healthcare_patterns.items():
        print(f"\nRunning OLB with {scenario_name} healthcare pattern...")
        
        environment = DigitalTwinEnvironment(config.environment_width, config.environment_height)
        environment.initialize_sensors(config.num_sensors, config.random_seed)
        environment.initialize_fog_nodes(config.num_fog_nodes, config.random_seed)
        environment.initialize_cloud()
        
        app = create_smart_healthcare_application(environment)
        topology = create_yafs_topology(environment)
        placement_json = create_placement_json("config")
        
        placement = WorkloadAwareOLBPlacement(
            f"OLB_{scenario_name}",
            placement_json,
            environment,
            workload_pattern
        )
        
        try:
            from yafs.core import Sim
            from yafs.population import Population
            
            s = Sim(topology, default_results_path="../results/")
            population = Population(name=f"{scenario_name}Sensors")
            s.deploy_app(app, placement, population)
            s.run(until=config.simulation_time)
            
            metrics = PerformanceMetrics()
            metrics.collect_metrics(environment, placement, f"OLB_{scenario_name}")
            
            result = metrics.get_summary_dict()
            result['scenario_type'] = scenario_name
            
            results[scenario_name] = result
            print(f"  Latency: {result['overall_latency']:.2f}ms")
            print(f"  Energy: {result['energy_consumption']:.2f}W")
            
        except Exception as e:
            print(f"  Failed: {e}")
            continue
    
    return results


def run_lstm_vs_static_comparison():
    if not LSTM_AVAILABLE:
        print("\n=== LSTM predictor not available, skipping ===\n")
        return {}
    
    print("\n=== LSTM PREDICTIVE vs STATIC OLB COMPARISON ===\n")
    
    config = SimulationConfig()
    
    try:
        ci_model = WorkloadPredictor(model_dir="CI_Models/Workload/models")
        workload_predictions = {}
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def predict_node(node_index):
            node_name = f"system-{node_index+1}"
            try:
                result = ci_model.predict_future(node_name, future_steps=200, plot=False, save_plot=False)
                return node_name, result["stats"]
            except Exception as e:
                print(f"  Prediction failed for {node_name}: {e}")
                return node_name, None
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(predict_node, i) for i in range(6)]
            for future in as_completed(futures):
                node_name, stats = future.result()
                if stats:
                    workload_predictions[node_name] = stats
        
        print(f"Collected predictions for {len(workload_predictions)} nodes\n")
        
    except Exception as e:
        print(f"LSTM prediction failed: {e}")
        return {}
    
    results = {}
    
    for test_name, use_lstm in [("static_olb", False), ("lstm_predictive_olb", True)]:
        print(f"\nRunning {test_name}...")
        
        environment = DigitalTwinEnvironment(config.environment_width, config.environment_height)
        environment.initialize_sensors(config.num_sensors, config.random_seed)
        environment.initialize_fog_nodes(config.num_fog_nodes, config.random_seed)
        environment.initialize_cloud()
        
        app = create_smart_healthcare_application(environment)
        topology = create_yafs_topology(environment)
        placement_json = create_placement_json("config")
        
        if use_lstm:
            placement = LSTMPredictiveOLBPlacement(
                "OLB_LSTM",
                placement_json,
                environment,
                workload_predictions
            )
        else:
            placement = OLBPlacement("OLB_Static", placement_json, environment)
        
        try:
            from yafs.core import Sim
            from yafs.population import Population
            
            s = Sim(topology, default_results_path="../results/")
            population = Population(name=f"{test_name}Sensors")
            s.deploy_app(app, placement, population)
            s.run(until=config.simulation_time)
            
            metrics = PerformanceMetrics()
            metrics.collect_metrics(environment, placement, test_name)
            
            result = metrics.get_summary_dict()
            result['uses_lstm'] = use_lstm
            
            results[test_name] = result
            print(f"  Latency: {result['overall_latency']:.2f}ms")
            print(f"  Energy: {result['energy_consumption']:.2f}W")
            
        except Exception as e:
            print(f"  Failed: {e}")
            continue
    
    return results


def generate_comparison_report(pattern_results, healthcare_results, lstm_results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    all_results = {
        'workload_patterns': pattern_results,
        'healthcare_scenarios': healthcare_results,
        'lstm_comparison': lstm_results,
        'timestamp': timestamp
    }
    
    with open(f"data/workload_comparison_{timestamp}.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    with open(f"reports/workload_comparison_{timestamp}.txt", "w") as f:
        f.write("=== WORKLOAD MODEL COMPARISON STUDY ===\n\n")
        
        if pattern_results:
            f.write("1. WORKLOAD PATTERN COMPARISON\n")
            f.write("-" * 50 + "\n")
            for pattern, metrics in pattern_results.items():
                f.write(f"\n{pattern.upper()} Pattern:\n")
                f.write(f"  Overall Latency: {metrics['overall_latency']:.4f} ms\n")
                f.write(f"  Energy Consumption: {metrics['energy_consumption']:.4f} W\n")
                f.write(f"  Load Balance Score: {metrics['load_balance_score']:.4f}\n")
            
            best_pattern = min(pattern_results.items(), key=lambda x: x[1]['overall_latency'])
            f.write(f"\nBest Pattern: {best_pattern[0]} ({best_pattern[1]['overall_latency']:.2f}ms)\n\n")
        
        if healthcare_results:
            f.write("\n2. HEALTHCARE SCENARIO COMPARISON\n")
            f.write("-" * 50 + "\n")
            for scenario, metrics in healthcare_results.items():
                f.write(f"\n{scenario.upper()} Scenario:\n")
                f.write(f"  Overall Latency: {metrics['overall_latency']:.4f} ms\n")
                f.write(f"  Energy Consumption: {metrics['energy_consumption']:.4f} W\n")
                f.write(f"  Load Balance Score: {metrics['load_balance_score']:.4f}\n")
            
            best_scenario = min(healthcare_results.items(), key=lambda x: x[1]['overall_latency'])
            f.write(f"\nBest Scenario: {best_scenario[0]} ({best_scenario[1]['overall_latency']:.2f}ms)\n\n")
        
        if lstm_results:
            f.write("\n3. LSTM PREDICTIVE vs STATIC OLB\n")
            f.write("-" * 50 + "\n")
            for test_name, metrics in lstm_results.items():
                f.write(f"\n{test_name.upper()}:\n")
                f.write(f"  Overall Latency: {metrics['overall_latency']:.4f} ms\n")
                f.write(f"  Energy Consumption: {metrics['energy_consumption']:.4f} W\n")
                f.write(f"  Load Balance Score: {metrics['load_balance_score']:.4f}\n")
            
            if 'static_olb' in lstm_results and 'lstm_predictive_olb' in lstm_results:
                static_latency = lstm_results['static_olb']['overall_latency']
                lstm_latency = lstm_results['lstm_predictive_olb']['overall_latency']
                improvement = ((static_latency - lstm_latency) / static_latency) * 100
                f.write(f"\nLSTM Improvement: {improvement:+.2f}%\n")
        
        f.write("\n" + "=" * 50 + "\n")
        f.write("CONCLUSION:\n")
        f.write("This study demonstrates how different workload patterns affect OLB performance.\n")
        f.write("LSTM-based prediction can proactively adjust fog node capacities.\n")
    
    print(f"\nComparison report saved: reports/workload_comparison_{timestamp}.txt")


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    
    pattern_results = run_workload_pattern_comparison()
    healthcare_results = run_healthcare_workload_comparison()
    lstm_results = run_lstm_vs_static_comparison()
    
    generate_comparison_report(pattern_results, healthcare_results, lstm_results)
    
    print("\n=== WORKLOAD COMPARISON STUDY COMPLETED ===")
