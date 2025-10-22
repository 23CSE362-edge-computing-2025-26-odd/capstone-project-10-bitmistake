from .comparison_algorithms import (LBS, LAB, MEC, FNPA)
from .devices import EdgeNodeDevice, SensorDevice
from .environment import DigitalTwinEnvironment
from .metrics import PerformanceMetrics, MetricsDefinitions
from .olb_algorithm import OLBLatencyCalculator, OLBPlacement
from .scenario_adapter import ScenarioToEnvironmentAdapter
from .utils import SimulationConfig, create_placement_json, save_results
from .visualization import SimulationVisualizer, HospitalVisualizationEngine
from .common_utils import (
    extract_sensor_id,
    calculate_euclidean_distance,
    SensorLookupIndex,
    DistanceCache,
    PlacementConstants,
    validate_coordinates,
    validate_simulation_config,
    profile_execution
)
from .orchestrator import (
    setup_directories,
    load_config,
    SimulationOrchestrator,
    get_project_root,
    get_absolute_path
)
from .algorithm_registry import (
    AlgorithmRegistry,
    get_registry,
    register_algorithm,
    get_algorithm,
    initialize_default_registry
)

# Try to import predictive placement algorithms - optional dependency
try:
    from .predictive_placement import PredictiveLatencyPlacement, ForecastBasedPlacement
    PREDICTIVE_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Predictive placement unavailable (LSTM models not loaded): {e}")
    print(f"[INFO] To enable predictive algorithms, ensure LSTM models are trained and tflite_predictor is available")
    PREDICTIVE_AVAILABLE = False
    
    # Create stub classes with clear error messages
    class PredictiveLatencyPlacement:
        """Stub class for unavailable PredictiveLatencyPlacement"""
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "PredictiveLatencyPlacement is not available. "
                "Please ensure LSTM models are trained and tflite_predictor module is accessible. "
                f"Original error: {e}"
            )
    
    class ForecastBasedPlacement:
        """Stub class for unavailable ForecastBasedPlacement"""
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "ForecastBasedPlacement is not available. "
                "Please ensure LSTM models are trained and tflite_predictor module is accessible. "
                f"Original error: {e}"
            )

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
    print(f"[INFO] To enable workload prediction, ensure CI_Models/Workload/tflite_predictor.py is accessible")
    WORKLOAD_PREDICTOR_AVAILABLE = False
    
    # Create stub classes with clear error messages
    class WorkloadPredictor:
        """Stub class for unavailable WorkloadPredictor"""
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "WorkloadPredictor is not available. "
                "Please ensure CI_Models/Workload directory is accessible. "
                f"Original error: {e}"
            )
    
    class PatternBasedWorkloadGenerator:
        """Stub class for unavailable PatternBasedWorkloadGenerator"""
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "PatternBasedWorkloadGenerator is not available. "
                f"Original error: {e}"
            )
    
    class HealthcareWorkloadForecaster:
        """Stub class for unavailable HealthcareWorkloadForecaster"""
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "HealthcareWorkloadForecaster is not available. "
                f"Original error: {e}"
            )
    
    class TimeSeriesWorkloadForecaster:
        """Stub class for unavailable TimeSeriesWorkloadForecaster"""
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "TimeSeriesWorkloadForecaster is not available. "
                f"Original error: {e}"
            )
from .yafs_integration import (create_smart_healthcare_application,
                               create_yafs_topology)

# Initialize algorithm registry with all available algorithms
initialize_default_registry()

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
    "HospitalVisualizationEngine",
    "LBS",
    "LAB",
    "MEC",
    "FNPA",
    "MetricsDefinitions",
    "ScenarioToEnvironmentAdapter",
    "PREDICTIVE_AVAILABLE",
    "WORKLOAD_PREDICTOR_AVAILABLE",
    # Common utilities
    "extract_sensor_id",
    "calculate_euclidean_distance",
    "SensorLookupIndex",
    "DistanceCache",
    "PlacementConstants",
    "validate_coordinates",
    "validate_simulation_config",
    "profile_execution",
    # Orchestrator
    "setup_directories",
    "load_config",
    "SimulationOrchestrator",
    "get_project_root",
    "get_absolute_path",
    # Algorithm Registry
    "AlgorithmRegistry",
    "get_registry",
    "register_algorithm",
    "get_algorithm",
    "initialize_default_registry",
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
