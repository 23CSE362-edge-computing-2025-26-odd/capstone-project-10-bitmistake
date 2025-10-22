import json
import logging
import os
import sys
from datetime import datetime

# --- PATH SETUP ---
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "CI_Models"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Workload"))

# --- SRC IMPORTS ---
from src.comparison_algorithms import (
    DistancePlacement,
    FNPAPlacement,
    LoadBalancedPlacement,
    RandomPlacement,
)
from src import (
    DigitalTwinEnvironment,
    OLBPlacement,
    PerformanceMetrics,
    SimulationConfig,
    create_placement_json,
    create_smart_healthcare_application,
    create_yafs_topology,
    save_results,
)

# --- CI MODEL IMPORT ---
from Workload.predict import WorkloadPredictor

# --- ALGORITHMS FOR EXPERIMENT COMPARISON ---
algorithms = [
    ("RandomPlacement", RandomPlacement),
    ("DistancePlacement", DistancePlacement),
    ("LoadBalancedPlacement", LoadBalancedPlacement),
    ("FNPAPlacement", FNPAPlacement),
]

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/olb_simulation.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting OLB Simulation with YAFS Framework")

    config = SimulationConfig()

    # --- CREATE DIGITAL TWIN ENVIRONMENT ---
    logger.info("Creating digital twin environment...")
    environment = DigitalTwinEnvironment(
        width=config.environment_width, height=config.environment_height
    )
    environment.initialize_sensors(
        num_sensors=config.num_sensors, seed=config.random_seed
    )
    environment.initialize_fog_nodes(
        num_fog_nodes=config.num_fog_nodes, seed=config.random_seed
    )

    # --- CI MODEL INTEGRATION (Workload Predictor) ---
    logger.info("Running CI Model (LSTM Workload Predictor)...")
    ci_model = WorkloadPredictor(model_dir="CI_Models/Workload/models")
    workload_predictions = {}

    for i, fog_node in enumerate(environment.fog_nodes):
        node_name = f"system-{i+1}"
        try:
            result = ci_model.predict_future(
                node_name, future_steps=200, plot=False, save_plot=False
            )
            workload_predictions[node_name] = result["stats"]
            logger.info(f"Predicted workload for {node_name}: {result['stats']}")
        except Exception as e:
            logger.warning(f"Workload prediction failed for {node_name}: {e}")

    # --- ADJUST FOG NODE CAPACITIES BASED ON PREDICTED WORKLOAD ---
    logger.info("Adjusting fog node capacities based on predicted workloads...")
    for i, fog_node in enumerate(environment.fog_nodes):
        node_name = f"system-{i+1}"
        if node_name in workload_predictions:
            predicted_load = workload_predictions[node_name]["predicted_avg"]
            adjustment_factor = max(0.5, 1.0 - (predicted_load / 100.0))
            fog_node.processingPower *= adjustment_factor
            logger.info(
                f"FogNode {i} adjusted: Power={fog_node.processingPower:.2f}, "
                f"AdjFactor={adjustment_factor:.2f}"
            )

    # --- SETUP YAFS APPLICATION AND TOPOLOGY ---
    logger.info("Setting up YAFS application and topology...")
    app = create_smart_healthcare_application(environment)
    topology = create_yafs_topology(environment)

    logger.info("Creating placement configuration...")
    placement_json = create_placement_json("config")

    logger.info("Initializing OLB placement algorithm...")
    olb_placement = OLBPlacement(
        name="OLB_Healthcare", json_file=placement_json, digital_twin=environment
    )

    try:
        from yafs.core import Sim
        from yafs.population import Population

        logger.info("Starting YAFS simulation...")

        s = Sim(topology, default_results_path="results/")
        population = Population(name="HealthcareSensors")
        s.deploy_app(app, olb_placement, population)
        s.run(until=config.simulation_time)

        logger.info("Collecting simulation results...")
        metrics = PerformanceMetrics()
        metrics.collect_metrics(environment, olb_placement, "OLB")

        # --- INCLUDE CI MODEL RESULTS IN OUTPUT ---
        results = {
            "simulation_config": config.to_dict(),
            "ci_predictions": workload_predictions,  # ← Added CI data
            "environment_info": {
                "num_sensors": len(environment.sensors),
                "num_fog_nodes": len(environment.fog_nodes),
                "sensor_coordinates": [s.coordinates for s in environment.sensors],
                "fog_node_coordinates": [f.coordinates for f in environment.fog_nodes],
            },
            "performance_metrics": metrics.get_summary_dict(),
            "simulation_metadata": {
                "simulation_time": config.simulation_time,
                "framework": "YAFS 1.0",
                "algorithm": "Optimised Load Balancing (OLB)",
            },
        }

        results_filename = f"data/olb_simulation_results.json"
        with open(results_filename, "w") as f:
            json.dump(results, f, indent=2, default=str)

        save_results(metrics, olb_placement, f"reports/olb_simulation_report.txt")

        logger.info("Simulation completed successfully!")
        logger.info(f"Results saved to: {results_filename}")

        return s, app.name, placement_json, environment, results

    except ImportError as e:
        logger.error(f"YAFS framework not properly installed: {e}")
        logger.error("Please install YAFS using: pip install yafs")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)


def run_experiments(placement_json, config):
    import json
    from yafs.core import Sim
    from yafs.population import Population

    for algo_name, AlgoClass in algorithms:
        print(f"\n==== Running {algo_name} ====\n")

        environment = DigitalTwinEnvironment(
            width=config.environment_width, height=config.environment_height
        )
        environment.initialize_sensors(
            num_sensors=config.num_sensors, seed=config.random_seed
        )
        environment.initialize_fog_nodes(
            num_fog_nodes=config.num_fog_nodes, seed=config.random_seed
        )

        app = create_smart_healthcare_application(environment)
        topology = create_yafs_topology(environment)
        sim = Sim(topology, default_results_path="results/")
        population = Population(name="HealthcareSensors")

        placement = AlgoClass(algo_name, placement_json, environment)
        sim.deploy_app(app, placement, population)
        sim.run(until=config.simulation_time)

        metrics = PerformanceMetrics()
        metrics.collect_metrics(environment, placement, algo_name)

        results = {
            "simulation_config": config.to_dict(),
            "performance_metrics": metrics.get_summary_dict(),
            "simulation_metadata": {
                "algorithm": algo_name,
                "framework": "YAFS 1.0",
                "simulation_time": config.simulation_time,
            },
        }

        results_filename = f"data/{algo_name.lower()}_results.json"
        with open(results_filename, "w") as f:
            json.dump(results, f, indent=2, default=str)

        save_results(metrics, placement, f"reports/{algo_name.lower()}_report.txt")

        print(f"==== Finished {algo_name}, results saved to {results_filename} ====\n")


if __name__ == "__main__":
    # --- CREATE DIRECTORIES ---
    os.makedirs("results", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # --- RUN MAIN SIMULATION ---
    sim, app_name, placement_json, environment, results = main()

    # --- RUN COMPARISON EXPERIMENTS ---
    config = SimulationConfig()
    run_experiments(placement_json, config)
