import json
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import DigitalTwinEnvironment, SimulationConfig, SimulationVisualizer

# Load results from all algorithm runs
results = {}
import os


def load_latest_file(pattern):
    files = [
        f
        for f in os.listdir("../data")
        if f.startswith(pattern) and f.endswith(".json")
    ]
    if not files:
        print(f"No files found matching pattern: {pattern}")
        return None
    latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join("../data", x)))
    print(f"Loading {latest_file}")
    return latest_file


# Load OLB results
olb_file = load_latest_file("olb_simulation_results")
if olb_file:
    with open(f"../data/{olb_file}", "r") as f:
        olb_results = json.load(f)
        results["OLB"] = olb_results.get("performance_metrics", {})

# Load comparison algorithm results
algorithms = ["random", "distance", "loadbalanced", "fnpa"]
for algo in algorithms:
    result_file = load_latest_file(f"{algo}placement_results")
    if result_file:
        with open(f"../data/{result_file}", "r") as f:
            algo_results = json.load(f)
            results[algo.upper() + "Placement"] = algo_results.get(
                "performance_metrics", {}
            )

# Create visualizer
viz = SimulationVisualizer()

# Create performance comparison plot
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Print the results for debugging
print("\nResults for visualization:")
for algo, metrics in results.items():
    print(f"\n{algo}:")
    print(metrics)

# Create the plot
output_path = f"../plots/performance_comparison_.png"
viz.plot_performance_comparison(results, output_path)
print(f"\nPlot saved to: {output_path}")

# Create environment plot for OLB
config = SimulationConfig()
environment = DigitalTwinEnvironment(
    config.environment_width, config.environment_height
)
environment.initialize_sensors(config.num_sensors, config.random_seed)
environment.initialize_fog_nodes(config.num_fog_nodes, config.random_seed)


# Mock placement for visualization
class MockPlacement:
    def __init__(self, assignments):
        self.module_assignments = assignments


# Extract OLB assignments
olb_assignments = {}
for assignment in results["OLB"]["detailed_assignments"]:
    node_id = assignment["fog_node_id"]
    sensor_id = assignment["sensor_id"]

    if node_id not in olb_assignments:
        olb_assignments[node_id] = []

    sensor = next(s for s in environment.sensors if s.device_id == sensor_id)
    olb_assignments[node_id].append(sensor)

olb_placement = MockPlacement(olb_assignments)
viz.plot_environment(environment, olb_placement, "OLB", "../plots/olb_environment.png")

print("Plots created successfully!")
print("- algorithm_comparison_chart.png")
print("- olb_environment.png")
