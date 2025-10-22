# CI_Models/Workload/__init__.py
"""
Workload Prediction Module
Provides LSTM-based workload prediction for edge computing environments
"""

try:
    from .predict import WorkloadPredictor
    from .tflite_predictor import (
        EdgeWorkloadPredictor,
        PatternBasedWorkloadGenerator,
        HealthcareWorkloadForecaster,
        TimeSeriesWorkloadForecaster
    )
    
    __all__ = [
        'WorkloadPredictor',
        'EdgeWorkloadPredictor',
        'PatternBasedWorkloadGenerator',
        'HealthcareWorkloadForecaster',
        'TimeSeriesWorkloadForecaster'
    ]
except ImportError as e:
    # If imports fail, provide empty exports
    print(f"[WARNING] Workload module imports failed: {e}")
    __all__ = []
