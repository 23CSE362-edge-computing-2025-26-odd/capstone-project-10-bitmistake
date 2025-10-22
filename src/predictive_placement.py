import math
import sys
import os
from yafs import Placement
from .olb_algorithm import OLBLatencyCalculator
from .common_utils import extract_sensor_id, SensorLookupIndex

# Import from CI_Models/Workload for edge deployment with proper error handling
try:
    # Add to path only if not already present
    workload_path = os.path.join(os.path.dirname(__file__), '..', 'CI_Models', 'Workload')
    workload_path = os.path.abspath(workload_path)
    if workload_path not in sys.path:
        sys.path.insert(0, workload_path)
    
    from tflite_predictor import EdgeWorkloadPredictor as WorkloadPredictor
    WORKLOAD_PREDICTOR_AVAILABLE = True
except (ImportError, ModuleNotFoundError) as e:
    print(f"Warning: WorkloadPredictor not available: {e}")
    WORKLOAD_PREDICTOR_AVAILABLE = False
    # Create stub class
    class WorkloadPredictor:
        def __init__(self, *args, **kwargs):
            raise ImportError("WorkloadPredictor not available")


class PredictiveLatencyPlacement(Placement):
    def __init__(self, name, json_file, digital_twin, prediction_horizon=10):
        super().__init__(name, json_file)
        self.digital_twin = digital_twin
        self.calculator = OLBLatencyCalculator()
        self.sensor_lookup = SensorLookupIndex(digital_twin.sensors)
        self.workload_predictor = WorkloadPredictor(
            model_dir=os.path.join(os.path.dirname(__file__), '..', 'CI_Models', 'Workload', 'models'),
            use_tflite=True
        )
        self.module_assignments = {}
        self.activation_dist = None
        self.prediction_horizon = prediction_horizon
        self.placement_decisions = []

    def initial_allocation(self, sim, app_name):
        app = sim.apps[app_name]
        modules_to_place = [m for m in app.modules if "Processing_Module" in m]

        print(f"\n[PredictiveLatency] Placing {len(modules_to_place)} modules with workload forecasting...")

        for module_name in modules_to_place:
            sensor_id = extract_sensor_id(module_name)
            sensor = self.sensor_lookup.find_by_id(sensor_id)

            if sensor:
                self._record_current_loads()
                
                optimal_node_id = self._find_predictive_optimal_node(sensor)

                if optimal_node_id is not None:
                    node_name = f"edge_{optimal_node_id}"
                    sim.deploy_module(app_name, module_name, [], [node_name])

                    if optimal_node_id not in self.module_assignments:
                        self.module_assignments[optimal_node_id] = []
                    self.module_assignments[optimal_node_id].append(sensor)
                    
                    print(f"  Sensor {sensor_id} -> edge {optimal_node_id} (predictive)")
                else:
                    fallback_node = "edge_0"
                    sim.deploy_module(app_name, module_name, [], [fallback_node])
                    if 0 not in self.module_assignments:
                        self.module_assignments[0] = []
                    self.module_assignments[0].append(sensor)
                    print(f"  Sensor {sensor_id} -> edge 0 (fallback)")

    def _record_current_loads(self):
        for sensor in self.digital_twin.sensors:
            self.workload_predictor.record_sensor_load(
                sensor.device_id,
                sensor.averageFlowRate,
                sensor.flowTrafficSize
            )

        for i, edge_node in enumerate(self.digital_twin.edge_nodes):
            assigned_sensors = self.module_assignments.get(i, [])
            total_load = sum(s.averageFlowRate * s.averageFlowSize for s in assigned_sensors)
            self.workload_predictor.record_edge_node_load(i, total_load, edge_node.processingPower)

    def _find_predictive_optimal_node(self, sensor):
        min_predicted_latency = float("inf")
        optimal_node_id = None
        decision_info = {
            'sensor_id': sensor.device_id,
            'candidates': []
        }

        for i, edge_node in enumerate(self.digital_twin.edge_nodes):
            try:
                assigned_sensors = self.module_assignments.get(i, [])
                
                predicted_latency = self.workload_predictor.predict_future_latency(
                    sensor, edge_node, assigned_sensors, self.calculator
                )

                decision_info['candidates'].append({
                    'edge_node_id': i,
                    'predicted_latency': predicted_latency
                })

                if predicted_latency < min_predicted_latency:
                    min_predicted_latency = predicted_latency
                    optimal_node_id = i

            except (ZeroDivisionError, ValueError, OverflowError):
                continue

        decision_info['chosen_node'] = optimal_node_id
        decision_info['predicted_latency'] = min_predicted_latency
        self.placement_decisions.append(decision_info)

        return optimal_node_id


class ForecastBasedPlacement(Placement):
    def __init__(self, name, json_file, digital_twin, workload_forecaster):
        super().__init__(name, json_file)
        self.digital_twin = digital_twin
        self.calculator = OLBLatencyCalculator()
        self.sensor_lookup = SensorLookupIndex(digital_twin.sensors)
        self.workload_forecaster = workload_forecaster
        self.module_assignments = {}
        self.activation_dist = None
        self.forecast_horizon = 10

    def initial_allocation(self, sim, app_name):
        app = sim.apps[app_name]
        modules_to_place = [m for m in app.modules if "Processing_Module" in m]

        print(f"\n[ForecastBased] Placing {len(modules_to_place)} modules with pattern forecasting...")

        future_multipliers = self.workload_forecaster.forecast_future_multipliers(self.forecast_horizon)
        avg_future_load = sum(future_multipliers) / len(future_multipliers)

        print(f"  Forecasted avg load multiplier: {avg_future_load:.2f}")

        for module_name in modules_to_place:
            sensor_id = extract_sensor_id(module_name)
            sensor = self.sensor_lookup.find_by_id(sensor_id)

            if sensor:
                optimal_node_id = self._find_forecast_optimal_node(sensor, avg_future_load)

                if optimal_node_id is not None:
                    node_name = f"edge_{optimal_node_id}"
                    sim.deploy_module(app_name, module_name, [], [node_name])

                    if optimal_node_id not in self.module_assignments:
                        self.module_assignments[optimal_node_id] = []
                    self.module_assignments[optimal_node_id].append(sensor)
                    
                    print(f"  Sensor {sensor_id} -> edge {optimal_node_id}")
                else:
                    fallback_node = "edge_0"
                    sim.deploy_module(app_name, module_name, [], [fallback_node])
                    if 0 not in self.module_assignments:
                        self.module_assignments[0] = []
                    self.module_assignments[0].append(sensor)

    def _find_forecast_optimal_node(self, sensor, future_load_multiplier):
        min_latency = float("inf")
        optimal_node_id = None

        original_flow_rate = sensor.averageFlowRate
        sensor.averageFlowRate *= future_load_multiplier

        for i, edge_node in enumerate(self.digital_twin.edge_nodes):
            try:
                assigned_sensors = self.module_assignments.get(i, [])

                comm_latency = self.calculator.calculate_communication_latency(sensor, edge_node, assigned_sensors)
                comp_latency = self.calculator.calculate_computing_latency(sensor, edge_node, assigned_sensors)

                if comm_latency == float("inf") or comp_latency == float("inf"):
                    continue

                total_latency = comm_latency + comp_latency

                if total_latency < min_latency:
                    min_latency = total_latency
                    optimal_node_id = i

            except (ZeroDivisionError, ValueError, OverflowError):
                continue

        sensor.averageFlowRate = original_flow_rate

        return optimal_node_id
