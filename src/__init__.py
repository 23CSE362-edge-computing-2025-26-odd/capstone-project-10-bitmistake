from .comparison_algorithms import (LBS, LAB, MEC, FNPA)
from .devices import EdgeNodeDevice, SensorDevice
from .environment import DigitalTwinEnvironment
from .healthcare_scenarios import HealthcareScenarios
from .metrics import PerformanceMetrics
from .metrics_definitions import MetricsDefinitions
from .olb_algorithm import OLBLatencyCalculator, OLBPlacement
from .utils import SimulationConfig, create_placement_json, save_results
from .visualization import SimulationVisualizer

# Try to import predictive placement algorithms - optional dependency
try:
    from .predictive_placement import PredictiveLatencyPlacement, ForecastBasedPlacement
    PREDICTIVE_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Predictive placement unavailable (LSTM models not loaded): {e}")
    PredictiveLatencyPlacement = None
    ForecastBasedPlacement = None
    PREDICTIVE_AVAILABLE = False

# Try to import CI_Models/Workload for edge deployment - optional
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'CI_Models', 'Workload'))
    
    from tflite_predictor import EdgeWorkloadPredictor as WorkloadPredictor
    from tflite_predictor import PatternBasedWorkloadGenerator, HealthcareWorkloadForecaster
    from tflite_predictor import TimeSeriesWorkloadForecaster
    WORKLOAD_PREDICTOR_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Workload predictor unavailable (CI models not loaded): {e}")
    WorkloadPredictor = None
    PatternBasedWorkloadGenerator = None
    HealthcareWorkloadForecaster = None
    TimeSeriesWorkloadForecaster = None
    WORKLOAD_PREDICTOR_AVAILABLE = False
from .yafs_integration import (create_smart_healthcare_application,
                               create_yafs_topology)

__all__ = [
    "SensorDevice",
    "EdgeNodeDevice",
    "DigitalTwinEnvironment",
    "OLBPlacement",
    "OLBLatencyCalculator",
    "create_smart_healthcare_application",
    "create_yafs_topology",
    "PerformanceMetrics",
    "SimulationConfig",
    "create_placement_json",
    "save_results",
    "SimulationVisualizer",
    "HealthcareScenarios",
    "LBS",
    "LAB",
    "MEC",
    "FNPA",
    "MetricsDefinitions",
    "PREDICTIVE_AVAILABLE",
    "WORKLOAD_PREDICTOR_AVAILABLE",
]

# Add optional imports to __all__ if available
if PREDICTIVE_AVAILABLE:
    __all__.extend(["PredictiveLatencyPlacement", "ForecastBasedPlacement"])
if WORKLOAD_PREDICTOR_AVAILABLE:
    __all__.extend([
        "WorkloadPredictor",
        "TimeSeriesWorkloadForecaster",
        "PatternBasedWorkloadGenerator",
        "HealthcareWorkloadForecaster"
    ])
