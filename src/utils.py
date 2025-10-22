import json
import os


def create_placement_json(output_dir="."):
    """Create JSON file for YAFS placement (required by YAFS)"""
    placement_config = {
        "name": "OLB_Placement",
        "algorithm": "custom_olb",
        "description": "Optimised Load Balancing for IoT-enabled Smart Healthcare",
    }

    json_path = os.path.join(output_dir, "placement_config.json")
    with open(json_path, "w") as f:
        json.dump(placement_config, f, indent=2)

    return json_path


def save_results(metrics, placement, output_file):
    """Save simulation results to file"""
    try:
        report = metrics.generate_report()

        with open(output_file, "w") as f:
            f.write(report)

            # Add detailed module assignment summary
            f.write("\nMODULE ASSIGNMENT SUMMARY:\n")
            for node_id, sensors in placement.module_assignments.items():
                f.write(f"edge Node {node_id}: {len(sensors)} sensors assigned\n")
                for sensor in sensors:
                    f.write(
                        f"  - Sensor {sensor.device_id} at coordinates {sensor.coordinates}\n"
                    )

        print(f"Results saved to {output_file}")
        return True

    except Exception as e:
        print(f"Warning: Could not save results: {e}")
        return False


class SimulationConfig:
    """Configuration class for simulation parameters"""

    def __init__(self):
        # Environment parameters
        self.environment_width = 3000
        self.environment_height = 2000

        # Device parameters
        self.num_sensors = 10
        self.num_edge_nodes = 6

        # Simulation parameters
        self.simulation_time = 1000
        self.random_seed = 42

        # Output parameters
        self.output_dir = "."
        self.results_file = "yafs_olb_results.txt"

    def to_dict(self):
        """Convert configuration to dictionary"""
        return {
            "environment": {
                "width": self.environment_width,
                "height": self.environment_height,
            },
            "devices": {
                "num_sensors": self.num_sensors,
                "num_edge_nodes": self.num_edge_nodes,
            },
            "simulation": {"time": self.simulation_time, "seed": self.random_seed},
            "output": {"dir": self.output_dir, "results_file": self.results_file},
        }

    def save_config(self, filename):
        """Save configuration to JSON file"""
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_config(cls, filename):
        """Load configuration from JSON file"""
        config = cls()
        with open(filename, "r") as f:
            data = json.load(f)

        # Update configuration from loaded data
        if "environment" in data:
            config.environment_width = data["environment"].get(
                "width", config.environment_width
            )
            config.environment_height = data["environment"].get(
                "height", config.environment_height
            )

        if "devices" in data:
            config.num_sensors = data["devices"].get("num_sensors", config.num_sensors)
            config.num_edge_nodes = data["devices"].get(
                "num_edge_nodes", config.num_edge_nodes
            )

        if "simulation" in data:
            config.simulation_time = data["simulation"].get(
                "time", config.simulation_time
            )
            config.random_seed = data["simulation"].get("seed", config.random_seed)

        if "output" in data:
            config.output_dir = data["output"].get("dir", config.output_dir)
            config.results_file = data["output"].get(
                "results_file", config.results_file
            )

        return config
