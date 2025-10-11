"""
Healthcare scenario evaluation script
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import (DigitalTwinEnvironment, DistancePlacement, FNPAPlacement,
                 HealthcareScenarios, OLBPlacement, PerformanceMetrics,
                 RandomPlacement, SimulationVisualizer, create_placement_json,
                 create_smart_healthcare_application, create_yafs_topology)


def run_healthcare_scenarios():
    """Run OLB evaluation on realistic healthcare scenarios"""
    print("=== HEALTHCARE SCENARIOS EVALUATION ===\n")

    scenarios = {
        "ICU": lambda env: HealthcareScenarios.create_icu_scenario(env, 8),
        "Ambulatory": lambda env: HealthcareScenarios.create_ambulatory_scenario(
            env, 12
        ),
        "Emergency": lambda env: HealthcareScenarios.create_emergency_scenario(env, 4),
    }

    algorithms = {
        "OLB": OLBPlacement,
        "Random": RandomPlacement,
        "Distance": DistancePlacement,
        "FNPA": FNPAPlacement,
    }

    all_results = {}

    for scenario_name, scenario_func in scenarios.items():
        print(f"\\n{'='*50}")
        print(f"SCENARIO: {scenario_name}")
        print(f"{'='*50}")

        scenario_results = {}

        for alg_name, alg_class in algorithms.items():
            print(f"\\nRunning {alg_name} on {scenario_name} scenario...")

            # Create fresh environment
            environment = DigitalTwinEnvironment(3000, 2000)
            num_sensors = scenario_func(environment)
            environment.initialize_cloud()

            print(f"  Sensors: {num_sensors}, Fog Nodes: {len(environment.fog_nodes)}")

            try:
                # Create YAFS components
                app = create_smart_healthcare_application(environment)
                topology = create_yafs_topology(environment)
                placement_json = create_placement_json("config")
                placement = alg_class(
                    f"{alg_name}_{scenario_name}", placement_json, environment
                )

                # Run simulation
                from yafs.core import Sim
                from yafs.population import Population

                s = Sim(topology, default_results_path="../results/")
                population = Population(name=f"{scenario_name}Sensors")
                s.deploy_app(app, placement, population)
                s.run(until=500)  # Shorter simulation for scenarios

                # Collect metrics
                metrics = PerformanceMetrics()
                metrics.collect_metrics(
                    environment, placement, f"{alg_name}_{scenario_name}"
                )

                result = metrics.get_summary_dict()
                result["num_sensors"] = num_sensors
                result["num_fog_nodes"] = len(environment.fog_nodes)

                scenario_results[alg_name] = result
                print(f"  {alg_name}: Latency={result['overall_latency']:.2f}ms")

            except Exception as e:
                print(f"  {alg_name} failed: {e}")
                continue

        all_results[scenario_name] = scenario_results

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("plots", exist_ok=True)

    with open(f"data/healthcare_scenarios_.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    # Generate report
    generate_healthcare_report(all_results, timestamp)

    # Create visualizations
    create_healthcare_visualizations(all_results, timestamp)

    print(
        f"\\nHealthcare evaluation completed! Results saved with timestamp: "
    )
    return all_results


def generate_healthcare_report(results, timestamp):
    """Generate healthcare scenarios comparison report"""
    with open(f"reports/healthcare_report_.txt", "w") as f:
        f.write("=== HEALTHCARE SCENARIOS EVALUATION REPORT ===\\n\\n")

        # Scenario information
        scenario_info = HealthcareScenarios.get_scenario_info()

        for scenario_name, scenario_results in results.items():
            f.write(f"{scenario_name.upper()} SCENARIO\\n")
            f.write("-" * 40 + "\\n")

            if scenario_name.lower() in scenario_info:
                info = scenario_info[scenario_name.lower()]
                f.write(f"Description: {info['description']}\\n")
                f.write(f"Characteristics: {', '.join(info['characteristics'])}\\n\\n")

            # Algorithm comparison for this scenario
            if scenario_results:
                f.write("Algorithm Performance:\\n")
                for alg_name, metrics in scenario_results.items():
                    f.write(f"  {alg_name}:\\n")
                    f.write(
                        f"    Overall Latency: {metrics['overall_latency']:.4f} ms\\n"
                    )
                    f.write(
                        f"    Energy Consumption: {metrics['energy_consumption']:.4f} W\\n"
                    )
                    f.write(
                        f"    Load Balance Score: {metrics['load_balance_score']:.4f}\\n"
                    )
                    f.write(
                        f"    Sensors: {metrics['num_sensors']}, Fog Nodes: {metrics['num_fog_nodes']}\\n\\n"
                    )

                # Best performer
                best_alg = min(
                    scenario_results.items(), key=lambda x: x[1]["overall_latency"]
                )
                f.write(
                    f"Best Performer: {best_alg[0]} ({best_alg[1]['overall_latency']:.4f} ms)\\n\\n"
                )

            f.write("\\n")

        # Cross-scenario analysis
        f.write("CROSS-SCENARIO ANALYSIS\\n")
        f.write("=" * 40 + "\\n")

        olb_results = {
            scenario: results[scenario].get("OLB", {}) for scenario in results
        }
        olb_results = {k: v for k, v in olb_results.items() if v}

        if olb_results:
            f.write("OLB Performance Across Scenarios:\\n")
            for scenario, metrics in olb_results.items():
                f.write(f"  {scenario}: {metrics['overall_latency']:.4f} ms\\n")

            # Most challenging scenario
            most_challenging = max(
                olb_results.items(), key=lambda x: x[1]["overall_latency"]
            )
            f.write(f"\\nMost Challenging Scenario: {most_challenging[0]}\\n")
            f.write(
                f"Reason: Highest latency ({most_challenging[1]['overall_latency']:.4f} ms)\\n"
            )


def create_healthcare_visualizations(results, timestamp):
    """Create visualizations for healthcare scenarios"""
    viz = SimulationVisualizer()

    # Performance comparison across scenarios
    if results:
        # Extract OLB results for scenario comparison
        olb_scenario_results = {}
        for scenario, scenario_results in results.items():
            if "OLB" in scenario_results:
                olb_scenario_results[scenario] = scenario_results["OLB"]

        if olb_scenario_results:
            viz.plot_performance_comparison(
                olb_scenario_results,
                f"plots/healthcare_scenarios_comparison_.png",
            )

    print("Healthcare visualizations created!")


if __name__ == "__main__":
    run_healthcare_scenarios()
