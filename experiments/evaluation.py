import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import (DigitalTwinEnvironment, DistancePlacement, FNPAPlacement,
                 LoadBalancedPlacement, OLBPlacement, PerformanceMetrics,
                 RandomPlacement, SimulationConfig, SimulationVisualizer,
                 create_placement_json, create_smart_healthcare_application,
                 create_yafs_topology)


def run_algorithm_comparison():
    """Run comprehensive algorithm comparison"""
    print("=== OLB ALGORITHM EVALUATION ===\n")

    config = SimulationConfig()
    algorithms = {
        "OLB": OLBPlacement,
        "Random": RandomPlacement,
        "Distance": DistancePlacement,
        "LoadBalanced": LoadBalancedPlacement,
        "FNPA": FNPAPlacement,
    }

    results = {}

    for alg_name, alg_class in algorithms.items():
        print(f"Running {alg_name} algorithm...")

        # Create fresh environment for each test
        environment = DigitalTwinEnvironment(
            config.environment_width, config.environment_height
        )
        environment.initialize_sensors(config.num_sensors, config.random_seed)
        environment.initialize_fog_nodes(config.num_fog_nodes, config.random_seed)
        environment.initialize_cloud()

        # Create application and topology
        app = create_smart_healthcare_application(environment)
        topology = create_yafs_topology(environment)

        # Initialize algorithm
        placement_json = create_placement_json("config")
        placement = alg_class(f"{alg_name}_Healthcare", placement_json, environment)

        try:
            from yafs.core import Sim
            from yafs.population import Population

            s = Sim(topology, default_results_path="../results/")
            population = Population(name=f"{alg_name}Sensors")
            s.deploy_app(app, placement, population)
            s.run(until=config.simulation_time)

            # Collect metrics
            metrics = PerformanceMetrics()
            metrics.collect_metrics(environment, placement, alg_name)

            results[alg_name] = metrics.get_summary_dict()
            print(f"{alg_name} completed\n")

        except Exception as e:
            print(f"{alg_name} failed: {e}\n")
            continue

    # Generate comparison report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save detailed results
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("plots", exist_ok=True)

    with open(f"data/algorithm_comparison_.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    # Generate comparison report
    with open(f"reports/comparison_report_.txt", "w") as f:
        f.write("=== ALGORITHM COMPARISON REPORT ===\n\n")

        for alg_name, metrics in results.items():
            f.write(f"{alg_name} Algorithm Results:\n")
            f.write(f"  Overall Latency: {metrics['overall_latency']:.4f}\n")
            f.write(f"  Energy Consumption: {metrics['energy_consumption']:.4f} W\n")
            f.write(f"  Network Usage: {metrics['network_usage']:.4f} MB/s\n")
            f.write(f"  Cost of Execution: {metrics['cost_of_execution']:.4f}\n\n")

        # Performance ranking
        f.write("PERFORMANCE RANKING:\n")
        sorted_by_latency = sorted(
            results.items(), key=lambda x: x[1]["overall_latency"]
        )
        for i, (alg_name, _) in enumerate(sorted_by_latency, 1):
            f.write(f"{i}. {alg_name} (Lowest Latency)\n")

    # Create visualizations
    visualizer = SimulationVisualizer()
    if results:
        visualizer.plot_performance_comparison(
            results, f"plots/performance_comparison_.png"
        )

    print(f"Evaluation completed! Results saved with timestamp: ")
    return results


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    run_algorithm_comparison()
