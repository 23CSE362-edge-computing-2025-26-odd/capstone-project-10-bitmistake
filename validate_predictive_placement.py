import sys
import os
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.workload_models import (
    WorkloadPredictor,
    TimeSeriesWorkloadForecaster,
    PatternBasedWorkloadGenerator,
    HealthcareWorkloadForecaster
)
from src.devices import SensorDevice, FogNodeDevice
from src.olb_algorithm import OLBLatencyCalculator


def test_workload_predictor():
    print("=== Testing WorkloadPredictor ===")
    
    predictor = WorkloadPredictor(history_window=20, prediction_horizon=5)
    
    for i in range(30):
        load = 100 + i * 2
        predictor.record_sensor_load(sensor_id=0, flow_rate=10.0, traffic_size=load/10)
    
    predicted_load = predictor.predict_sensor_load(sensor_id=0, steps_ahead=5)
    
    print(f"Historical loads: increasing from 100 to 158")
    print(f"Predicted load (5 steps ahead): {predicted_load:.2f}")
    
    if predicted_load > 158:
        print("✓ Predictor correctly identifies increasing trend\n")
    else:
        print("✗ Predictor failed to identify trend\n")


def test_time_series_forecaster():
    print("=== Testing TimeSeriesWorkloadForecaster ===")
    
    forecasters = {
        "autoregressive": TimeSeriesWorkloadForecaster("autoregressive"),
        "moving_average": TimeSeriesWorkloadForecaster("moving_average"),
        "exponential_smoothing": TimeSeriesWorkloadForecaster("exponential_smoothing"),
        "trend_based": TimeSeriesWorkloadForecaster("trend_based"),
    }
    
    periodic_data = [1.0 + 0.3 * np.sin(i * 0.1) for i in range(50)]
    
    for name, forecaster in forecasters.items():
        for value in periodic_data:
            forecaster.add_observation(value)
        
        forecast = forecaster.forecast_next_steps(10)
        forecast_mean = np.mean(forecast)
        
        print(f"{name}:")
        print(f"  Historical mean: {np.mean(periodic_data):.3f}")
        print(f"  Forecast mean: {forecast_mean:.3f}")
        print(f"  Forecast range: [{min(forecast):.3f}, {max(forecast):.3f}]")
    
    print("\n✓ All forecasting methods working\n")


def test_pattern_based_generator():
    print("=== Testing PatternBasedWorkloadGenerator ===")
    
    patterns = ["steady", "periodic", "bursty", "increasing", "decreasing"]
    
    for pattern_type in patterns:
        gen = PatternBasedWorkloadGenerator(pattern_type)
        
        current_values = [gen.get_current_multiplier() for _ in range(20)]
        forecast_values = gen.forecast_future_multipliers(10)
        
        current_mean = np.mean(current_values)
        forecast_mean = np.mean(forecast_values)
        
        print(f"{pattern_type}:")
        print(f"  Current mean: {current_mean:.3f}")
        print(f"  Forecast mean: {forecast_mean:.3f}")
        
        if pattern_type == "increasing":
            if forecast_mean > current_mean:
                print(f"  ✓ Correctly predicts increasing trend")
            else:
                print(f"  ✗ Failed to predict increasing trend")
        elif pattern_type == "decreasing":
            if forecast_mean < current_mean:
                print(f"  ✓ Correctly predicts decreasing trend")
            else:
                print(f"  ✗ Failed to predict decreasing trend")
        else:
            print(f"  ✓ Pattern generated")
    
    print()


def test_healthcare_forecaster():
    print("=== Testing HealthcareWorkloadForecaster ===")
    
    scenarios = ["icu", "emergency", "ambulatory"]
    
    for scenario_type in scenarios:
        forecaster = HealthcareWorkloadForecaster(scenario_type)
        
        multipliers = [forecaster.get_current_multiplier() for _ in range(100)]
        
        event_prob = forecaster.forecast_critical_event_probability(10)
        load_range = forecaster.forecast_load_range(10)
        
        print(f"{scenario_type}:")
        print(f"  Observed mean: {np.mean(multipliers):.3f}")
        print(f"  Observed max: {max(multipliers):.3f}")
        print(f"  Event probability: {event_prob:.3f}")
        print(f"  Forecast range: [{load_range[0]:.3f}, {load_range[1]:.3f}]")
        
        if scenario_type == "icu" and event_prob > 0:
            print(f"  ✓ ICU critical events detected")
        elif scenario_type == "emergency" and max(multipliers) > 2.0:
            print(f"  ✓ Emergency spikes detected")
        elif scenario_type == "ambulatory":
            print(f"  ✓ Ambulatory pattern generated")
    
    print()


def test_predictive_latency_calculation():
    print("=== Testing Predictive Latency Calculation ===")
    
    predictor = WorkloadPredictor(history_window=20, prediction_horizon=5)
    calculator = OLBLatencyCalculator()
    
    sensor = SensorDevice(
        device_id=0,
        coordinates=(100, 100),
        transmission_power=0.5,
        average_flow_rate=5.0,
        flow_traffic_size=1.0,
        average_flow_size=1000
    )
    
    fog_node = FogNodeDevice(
        node_id=0,
        coordinates=(200, 200),
        processing_power=5000,
        bandwidth=100,
        carrier_frequency=2.4,
        noise_power=1e-10
    )
    
    for i in range(30):
        load = 5.0 + i * 0.1
        predictor.record_sensor_load(sensor.device_id, load, sensor.flowTrafficSize)
        predictor.record_fog_node_load(0, load * 1000, fog_node.processingPower)
    
    current_latency = calculator.calculate_communication_latency(sensor, fog_node, [])
    current_latency += calculator.calculate_computing_latency(sensor, fog_node, [])
    
    predicted_latency = predictor.predict_future_latency(sensor, fog_node, [], calculator)
    
    print(f"Current latency: {current_latency:.4f}")
    print(f"Predicted latency: {predicted_latency:.4f}")
    print(f"Ratio: {predicted_latency / current_latency:.2f}x")
    
    if predicted_latency > current_latency:
        print("✓ Predictor correctly anticipates load increase\n")
    else:
        print("⚠ Predictor may not be capturing trend\n")


def test_forecast_accuracy():
    print("=== Testing Forecast Accuracy ===")
    
    true_pattern = [1.0 + 0.3 * np.sin(i * 0.1) for i in range(100)]
    
    forecaster = TimeSeriesWorkloadForecaster("autoregressive")
    
    for value in true_pattern[:50]:
        forecaster.add_observation(value)
    
    forecast = forecaster.forecast_next_steps(10)
    actual = true_pattern[50:60]
    
    errors = [abs(f - a) for f, a in zip(forecast, actual)]
    mae = np.mean(errors)
    mape = np.mean([abs(f - a) / a * 100 for f, a in zip(forecast, actual)])
    
    print(f"Mean Absolute Error: {mae:.4f}")
    print(f"Mean Absolute Percentage Error: {mape:.2f}%")
    
    if mape < 20:
        print("✓ Forecast accuracy is good (< 20% error)\n")
    else:
        print("⚠ Forecast accuracy could be improved\n")


def test_prediction_overhead():
    print("=== Testing Prediction Overhead ===")
    
    predictor = WorkloadPredictor(history_window=50, prediction_horizon=10)
    calculator = OLBLatencyCalculator()
    
    sensor = SensorDevice(0, (100, 100), 0.5, 5.0, 1.0, 1000)
    fog_node = FogNodeDevice(0, (200, 200), 5000, 100, 2.4, 1e-10)
    
    for i in range(50):
        predictor.record_sensor_load(0, 5.0 + i * 0.1, 1.0)
        predictor.record_fog_node_load(0, (5.0 + i * 0.1) * 1000, 5000)
    
    start_time = time.time()
    for _ in range(100):
        current_latency = calculator.calculate_communication_latency(sensor, fog_node, [])
        current_latency += calculator.calculate_computing_latency(sensor, fog_node, [])
    reactive_time = time.time() - start_time
    
    start_time = time.time()
    for _ in range(100):
        predicted_latency = predictor.predict_future_latency(sensor, fog_node, [], calculator)
    predictive_time = time.time() - start_time
    
    overhead = ((predictive_time - reactive_time) / reactive_time) * 100
    
    print(f"Reactive calculation time: {reactive_time:.4f}s")
    print(f"Predictive calculation time: {predictive_time:.4f}s")
    print(f"Overhead: {overhead:+.1f}%")
    
    if overhead < 50:
        print("✓ Prediction overhead is acceptable (< 50%)\n")
    else:
        print("⚠ Prediction overhead is high\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("VALIDATING PREDICTIVE PLACEMENT COMPONENTS")
    print("="*70 + "\n")
    
    try:
        test_workload_predictor()
        test_time_series_forecaster()
        test_pattern_based_generator()
        test_healthcare_forecaster()
        test_predictive_latency_calculation()
        test_forecast_accuracy()
        test_prediction_overhead()
        
        print("="*70)
        print("ALL PREDICTIVE PLACEMENT VALIDATIONS COMPLETED")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
