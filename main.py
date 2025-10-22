"""
Unified Main Entry Point for OLB Simulation System
Supports multiple workflows via subcommands
"""

import argparse
import os
import sys
import time
import json

# --- PATH SETUP ---
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "CI_Models"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Workload"))

# --- SRC IMPORTS ---
from src import (
    DigitalTwinEnvironment,
    OLBPlacement,
    PerformanceMetrics,
    SimulationConfig,
    create_placement_json,
    create_smart_healthcare_application,
    create_yafs_topology,
    save_results,
    HospitalVisualizationEngine,
)
from src.orchestrator import get_project_root
from src.hospital_comparison import HospitalComparisonRunner
from src.hospital_scenarios_extended import ScenarioManager
from src.mqtt_simulator import MQTTSimulationEnvironment
from src.algorithm_registry import get_registry, initialize_default_registry

# --- CI MODEL IMPORT (OPTIONAL) ---
try:
    from Workload.predict import WorkloadPredictor
    WORKLOAD_PREDICTOR_AVAILABLE = True
except ImportError:
    WORKLOAD_PREDICTOR_AVAILABLE = False


# Module-level cache for LSTM predictor
_cached_workload_predictor = None

def get_or_create_workload_predictor(model_dir: str = "CI_Models/Workload/models"):
    """Get cached WorkloadPredictor or create new one."""
    global _cached_workload_predictor
    
    if _cached_workload_predictor is not None:
        return _cached_workload_predictor
    
    _cached_workload_predictor = WorkloadPredictor(model_dir=model_dir)
    return _cached_workload_predictor

def clear_workload_predictor_cache():
    """Clear the workload predictor cache to prevent memory leaks."""
    global _cached_workload_predictor
    if _cached_workload_predictor is not None:
        _cached_workload_predictor = None
        print("[INFO] Workload predictor cache cleared")
        
        import gc
        gc.collect()
        print("[INFO] Garbage collection completed")


def setup_directories():
    """Create output directories"""
    dirs = ["results", "data", "reports", "plots"]
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)


def run_olb_simulation():
    """Run OLB simulation workflow"""
    print("\n" + "=" * 80)
    print("STARTING OLB SIMULATION WITH YAFS FRAMEWORK")
    print("=" * 80)

    config = SimulationConfig()
    
    # Validate configuration before running simulation
    from src.common_utils import validate_simulation_config
    validation_errors = validate_simulation_config(config)
    if validation_errors:
        print("[ERROR] Configuration validation failed:")
        for error in validation_errors:
            print(f"  - {error}")
        return 1

    # --- CREATE DIGITAL TWIN ENVIRONMENT ---
    print("Creating digital twin environment...")
    environment = DigitalTwinEnvironment(
        width=config.environment_width, height=config.environment_height
    )
    environment.initialize_sensors(
        num_sensors=config.num_sensors, seed=config.random_seed
    )
    environment.initialize_edge_nodes(
        num_edge_nodes=config.num_edge_nodes, seed=config.random_seed
    )

    # --- OPTIONAL: RUN CI MODEL (LSTM WORKLOAD PREDICTOR) ---
    workload_predictions = {}
    
    if WORKLOAD_PREDICTOR_AVAILABLE:
        print("=" * 70)
        print("Running CI Model (LSTM Workload Predictor)...")
        print("=" * 70)
        
        try:
            ci_model = get_or_create_workload_predictor("CI_Models/Workload/models")
            
            from concurrent.futures import ThreadPoolExecutor, as_completed

            def predict_single_node(node_index):
                node_name = f"system-{node_index+1}"
                try:
                    result = ci_model.predict_future(node_name, future_steps=200, plot=False, save_plot=False)
                    return node_name, result["stats"]
                except Exception as e:
                    return node_name, None

            with ThreadPoolExecutor(max_workers=min(6, len(environment.edge_nodes))) as executor:
                futures = [executor.submit(predict_single_node, i) for i in range(len(environment.edge_nodes))]
                for future in as_completed(futures):
                    node_name, stats = future.result()
                    if stats:
                        workload_predictions[node_name] = stats
            
            print(f"LSTM predictions completed for {len(workload_predictions)} nodes")
            
        except Exception as e:
            print(f"Warning: LSTM model initialization failed: {e}")
            print("Continuing without workload predictions")
            workload_predictions = {}
    else:
        print("=" * 70)
        print("SKIPPING CI Model - WorkloadPredictor not available")
        print("=" * 70)

    # --- ADJUST edge NODE CAPACITIES BASED ON PREDICTED WORKLOAD ---
    if workload_predictions:
        print("Adjusting edge node capacities based on predicted workloads...")
        
        # Import constants for capacity adjustment
        from src.common_utils import PlacementConstants
        CAPACITY_INCREASE_FACTOR = PlacementConstants.CAPACITY_INCREASE_FACTOR
        CAPACITY_DECREASE_BASE = PlacementConstants.CAPACITY_DECREASE_BASE
        MIN_ADJUSTMENT_FACTOR = PlacementConstants.MIN_CAPACITY_FACTOR
        MAX_ADJUSTMENT_FACTOR = PlacementConstants.MAX_CAPACITY_FACTOR
        DEFAULT_AVG_LOAD = PlacementConstants.DEFAULT_AVG_LOAD
        
        total_predicted_load = 0
        node_predictions = {}
        
        for i, edge_node in enumerate(environment.edge_nodes):
            node_name = f"system-{i+1}"
            if node_name in workload_predictions:
                predicted_load = workload_predictions[node_name]["predicted_avg"]
                node_predictions[i] = predicted_load
                total_predicted_load += predicted_load
        
        avg_predicted_load = total_predicted_load / len(node_predictions) if node_predictions else DEFAULT_AVG_LOAD
        
        for i, edge_node in enumerate(environment.edge_nodes):
            if i in node_predictions:
                predicted_load = node_predictions[i]
                
                if predicted_load > avg_predicted_load:
                    load_ratio = predicted_load / max(avg_predicted_load, 1.0)
                    adjustment_factor = 1.0 + (CAPACITY_INCREASE_FACTOR * (load_ratio - 1.0))
                else:
                    load_ratio = predicted_load / max(avg_predicted_load, 1.0)
                    adjustment_factor = CAPACITY_DECREASE_BASE + (CAPACITY_INCREASE_FACTOR * load_ratio)
                
                # Clamp adjustment factor to safe bounds
                adjustment_factor = max(MIN_ADJUSTMENT_FACTOR, min(MAX_ADJUSTMENT_FACTOR, adjustment_factor))
                edge_node.processingPower *= adjustment_factor
        
        print("edge node capacity adjustments completed")

    # --- SETUP YAFS APPLICATION AND TOPOLOGY ---
    print("Setting up YAFS application and topology...")
    app = create_smart_healthcare_application(environment)
    topology = create_yafs_topology(environment)

    placement_json = create_placement_json("config")
    olb_placement = OLBPlacement(
        name="OLB_Healthcare", json_file=placement_json, digital_twin=environment
    )

    # Initialize MQTT environment
    mqtt_env = MQTTSimulationEnvironment()
    mqtt_env.simulation_time = 0
    
    # Publish simulation start event
    mqtt_env.publish_simulation_start({
        "algorithm": "OLB",
        "num_sensors": len(environment.sensors),
        "num_edge_nodes": len(environment.edge_nodes),
        "simulation_time": config.simulation_time
    })

    try:
        from yafs.core import Sim
        from yafs.population import Population

        print("Starting YAFS simulation...")

        s = Sim(topology, default_results_path="results/")
        population = Population(name="HealthcareSensors")
        
        # Connect MQTT to YAFS
        mqtt_env.connect_to_yafs_simulation(s)
        
        s.deploy_app(app, olb_placement, population)
        
        # Publish placement decisions to MQTT
        mqtt_env.publish_placement_decisions(olb_placement, environment)
        
        s.run(until=config.simulation_time)
        
        # Advance MQTT simulation time
        mqtt_env.advance_time(config.simulation_time * 1000)

        print("Collecting simulation results...")
        metrics = PerformanceMetrics()
        metrics.collect_metrics(environment, olb_placement, "OLB")

        # Publish final metrics to MQTT
        mqtt_env.publish_simulation_end(metrics.get_summary_dict())
        
        # Export MQTT log
        mqtt_log_file = mqtt_env.export_mqtt_log("olb_mqtt_log.json")
        
        results = {
            "simulation_config": config.to_dict(),
            "ci_predictions": workload_predictions,
            "environment_info": {
                "num_sensors": len(environment.sensors),
                "num_edge_nodes": len(environment.edge_nodes),
                "sensor_coordinates": [s.coordinates for s in environment.sensors],
                "edge_node_coordinates": [f.coordinates for f in environment.edge_nodes],
            },
            "performance_metrics": metrics.get_summary_dict(),
            "mqtt_statistics": mqtt_env.get_statistics(),
            "mqtt_log_file": mqtt_log_file,
            "simulation_metadata": {
                "simulation_time": config.simulation_time,
                "framework": "YAFS 1.0",
                "algorithm": "Optimised Load Balancing (OLB)",
            },
        }

        # Use absolute path for results file
        results_filename = str(get_project_root() / "data" / "olb_simulation_results.json")
        with open(results_filename, "w") as f:
            json.dump(results, f, indent=2, default=str)

        save_results(metrics, olb_placement, str(get_project_root() / "reports" / "olb_simulation_report.txt"))

        print("\n" + "=" * 80)
        print("OLB SIMULATION COMPLETED SUCCESSFULLY!")
        print(f"Results saved to: {results_filename}")
        print("=" * 80)
        
        return 0

    except ImportError as e:
        print(f"ERROR: YAFS framework not properly installed: {e}")
        return 1
    except Exception as e:
        print(f"ERROR: Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Always clear cache to free memory
        if WORKLOAD_PREDICTOR_AVAILABLE:
            clear_workload_predictor_cache()


def run_algorithm_comparison():
    """Run algorithm comparison workflow"""
    print("\n" + "=" * 80)
    print("RUNNING ALGORITHM COMPARISON")
    print("=" * 80)

    config = SimulationConfig()
    
    # Validate configuration
    from src.common_utils import validate_simulation_config
    validation_errors = validate_simulation_config(config)
    if validation_errors:
        print("[ERROR] Configuration validation failed:")
        for error in validation_errors:
            print(f"  - {error}")
        return 1
    
    # Use algorithm registry for consistent algorithm access
    registry = get_registry()
    algorithm_names = ['LBS', 'LAB', 'MEC', 'FNPA']
    
    # Verify all algorithms are available
    missing_algorithms = [name for name in algorithm_names if not registry.exists(name)]
    if missing_algorithms:
        print(f"[ERROR] Missing algorithms: {', '.join(missing_algorithms)}")
        return 1

    placement_json = create_placement_json(str(get_project_root() / "config"))
    
    # Initialize MQTT environment for algorithm comparison
    mqtt_env = MQTTSimulationEnvironment()
    mqtt_env.simulation_time = 0

    for algo_name in algorithm_names:
        AlgoClass = registry.get(algo_name)
        if AlgoClass is None:
            print(f"[ERROR] Algorithm {algo_name} not found in registry")
            continue
        print(f"\n{'='*70}")
        print(f"Running {algo_name} Algorithm")
        print(f"{'='*70}")

        environment = DigitalTwinEnvironment(
            width=config.environment_width, height=config.environment_height
        )
        environment.initialize_sensors(
            num_sensors=config.num_sensors, seed=config.random_seed
        )
        environment.initialize_edge_nodes(
            num_edge_nodes=config.num_edge_nodes, seed=config.random_seed
        )

        app = create_smart_healthcare_application(environment)
        topology = create_yafs_topology(environment)

        try:
            from yafs.core import Sim
            from yafs.population import Population

            sim = Sim(topology, default_results_path="results/")
            population = Population(name="HealthcareSensors")

            placement = AlgoClass(algo_name, placement_json, environment)
            
            # Publish simulation start to MQTT
            mqtt_env.publish_simulation_start({
                "algorithm": algo_name,
                "num_sensors": len(environment.sensors),
                "num_edge_nodes": len(environment.edge_nodes)
            })
            
            sim.deploy_app(app, placement, population)
            
            # Connect MQTT to YAFS simulation and publish placement decisions
            mqtt_env.connect_to_yafs_simulation(sim)
            mqtt_env.publish_placement_decisions(placement, environment)
            
            sim.run(until=config.simulation_time)
            
            # Advance MQTT time
            mqtt_env.advance_time(config.simulation_time * 1000)

            metrics = PerformanceMetrics()
            metrics.collect_metrics(environment, placement, algo_name)
            
            # Publish final metrics to MQTT
            mqtt_env.publish_simulation_end(metrics.get_summary_dict())
            
            # Export MQTT log for this algorithm
            mqtt_log_file = mqtt_env.export_mqtt_log(f"{algo_name.lower()}_mqtt_log.json")

            results = {
                "simulation_config": config.to_dict(),
                "performance_metrics": metrics.get_summary_dict(),
                "mqtt_statistics": mqtt_env.get_statistics(),
                "mqtt_log_file": mqtt_log_file,
                "simulation_metadata": {
                    "algorithm": algo_name,
                    "framework": "YAFS 1.0",
                    "simulation_time": config.simulation_time,
                },
            }

            results_filename = str(get_project_root() / "data" / f"{algo_name.lower()}_results.json")
            with open(results_filename, "w") as f:
                json.dump(results, f, indent=2, default=str)

            save_results(metrics, placement, str(get_project_root() / "reports" / f"{algo_name.lower()}_report.txt"))

            print(f"{algo_name} completed, results saved to {results_filename}")
            print(f"MQTT log saved to {mqtt_log_file}")

        except Exception as e:
            print(f"ERROR running {algo_name}: {e}")
            continue

    print("\n" + "=" * 80)
    print("ALGORITHM COMPARISON COMPLETED")
    print("=" * 80)
    
    return 0


def run_hospital_comparison():
    """Run hospital scenario comparison workflow"""
    print("\n" + "=" * 80)
    print("HOSPITAL SCENARIO COMPARISON WORKFLOW")
    print("=" * 80)
    
    workflow_start = time.time()
    
    try:
        # Phase 1: Setup
        print("\n[PHASE 1] Environment Setup")
        print("-" * 80)
        
        # Phase 2: Initialize MQTT
        print("\n[PHASE 2] MQTT Initialization")
        print("-" * 80)
        
        mqtt_env = MQTTSimulationEnvironment()
        mqtt_env.simulation_time = 0
        print("MQTT environment ready")
        
        # Phase 3: Load Scenarios
        print("\n[PHASE 3] Loading Hospital Scenarios")
        print("-" * 80)
        
        manager = ScenarioManager()
        scenarios = manager.get_all_scenarios()
        print(f"Loaded {len(scenarios)} scenarios")
        manager.print_summary()
        
        # Phase 4: Run Comparison
        print("\n[PHASE 4] Running Algorithm Comparison (with MQTT)")
        print("-" * 80)
        
        phase4_start = time.time()
        runner = HospitalComparisonRunner()
        results = runner.run_comparison()
        phase4_duration = time.time() - phase4_start
        
        # Publish results to MQTT
        print("Publishing results to MQTT broker...")
        mqtt_env.advance_time(phase4_duration * 1000)
        
        for scenario_data in results.get("scenarios", []):
            for result in scenario_data.get("results", []):
                mqtt_env.publish_simulation_metrics({
                    "algorithm": result["algorithm_name"],
                    "scenario": scenario_data["scenario_name"],
                    "latency_avg": result["latency_avg"],
                    "energy_consumption": result["energy_consumption"],
                    "load_balance_score": result["load_balance_score"],
                    "sla_compliance": result["sla_compliance_percent"]
                })
        
        mqtt_stats = mqtt_env.get_statistics()
        print(f"MQTT published {mqtt_stats['messages_sent']} messages")
        print(f"Comparison completed ({phase4_duration:.2f}s)")
        
        # Phase 5: Export Results
        print("\n[PHASE 5] Exporting Results")
        print("-" * 80)
        
        json_file = str(get_project_root() / "data" / "hospital_comparison_results.json")
        html_file = str(get_project_root() / "reports" / "hospital_comparison_report.html")
        
        runner.export_json(results, json_file)
        runner.export_html(results, html_file)
        print("Results exported")
        
        # Phase 6: Generate Visualizations
        print("\n[PHASE 6] Generating Visualizations")
        print("-" * 80)
        
        visualizer = HospitalVisualizationEngine(results, str(get_project_root() / "plots"))
        visualizer.generate_all_visualizations()
        
        summary = visualizer.get_performance_summary()
        print("\nPerformance Summary:")
        for algo, metrics in summary.items():
            print(f"  {algo}:")
            for metric_name, metric_value in metrics.items():
                print(f"    - {metric_name}: {metric_value}")
        
        # Final Summary
        total_duration = time.time() - workflow_start
        
        print("\n" + "=" * 80)
        print("HOSPITAL WORKFLOW COMPLETED SUCCESSFULLY!")
        print(f"Total execution time: {total_duration:.2f}s ({total_duration/60:.2f}min)")
        print(f"JSON results: {json_file}")
        print(f"HTML report: {html_file}")
        print(f"Plots: plots/ directory")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: Workflow failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Always clear cache to free memory
        if WORKLOAD_PREDICTOR_AVAILABLE:
            clear_workload_predictor_cache()


def main():
    """Main entry point with argument parsing"""
    # Initialize algorithm registry
    initialize_default_registry()
    print(f"[INFO] Initialized algorithm registry with {len(get_registry())} algorithms")
    
    parser = argparse.ArgumentParser(
        description="OLB edge Computing Simulation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py olb           Run OLB simulation
  python main.py hospital      Run hospital scenario comparison
  python main.py compare       Run algorithm comparison
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # OLB simulation command
    parser_olb = subparsers.add_parser('olb', help='Run OLB simulation')
    
    # Hospital comparison command
    parser_hospital = subparsers.add_parser('hospital', help='Run hospital scenario comparison')
    
    # Algorithm comparison command
    parser_compare = subparsers.add_parser('compare', help='Run algorithm comparison')
    
    args = parser.parse_args()
    
    # Setup directories using orchestrator
    from src.orchestrator import setup_directories
    setup_directories()
    
    # Run appropriate workflow
    if args.command == 'olb':
        return run_olb_simulation()
    elif args.command == 'hospital':
        return run_hospital_comparison()
    elif args.command == 'compare':
        return run_algorithm_comparison()
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
