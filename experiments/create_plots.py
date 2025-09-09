import json
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.visualization import SimulationVisualizer
from src.environment import DigitalTwinEnvironment
from src.utils import SimulationConfig

# Load results
with open('../data/algorithm_comparison_20250907_184119.json', 'r') as f:
    results = json.load(f)

# Create visualizer
viz = SimulationVisualizer()

# Create performance comparison plot
viz.plot_performance_comparison(results, "../plots/algorithm_comparison_chart.png")

# Create environment plot for OLB
config = SimulationConfig()
environment = DigitalTwinEnvironment(config.environment_width, config.environment_height)
environment.initialize_sensors(config.num_sensors, config.random_seed)
environment.initialize_fog_nodes(config.num_fog_nodes, config.random_seed)

# Mock placement for visualization
class MockPlacement:
    def __init__(self, assignments):
        self.module_assignments = assignments

# Extract OLB assignments
olb_assignments = {}
for assignment in results['OLB']['detailed_assignments']:
    node_id = assignment['fog_node_id']
    sensor_id = assignment['sensor_id']
    
    if node_id not in olb_assignments:
        olb_assignments[node_id] = []
    
    sensor = next(s for s in environment.sensors if s.device_id == sensor_id)
    olb_assignments[node_id].append(sensor)

olb_placement = MockPlacement(olb_assignments)
viz.plot_environment(environment, olb_placement, "OLB", "../plots/olb_environment.png")

print("Plots created successfully!")
print("- algorithm_comparison_chart.png")
print("- olb_environment.png")