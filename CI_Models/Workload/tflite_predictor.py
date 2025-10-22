"""
TFLite-Compatible Workload Predictor for Edge Deployment
Optimized for low memory footprint and edge device inference
"""
import os
import sys
import pickle
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from collections import deque

# TensorFlow imports
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')

class EdgeWorkloadPredictor:
    """Edge-optimized workload predictor using TFLite models"""
    
    def __init__(self, model_dir: str = "models", use_tflite: bool = True) -> None:
        self.model_dir = model_dir
        self.use_tflite = use_tflite
        self.scaler: Optional[Any] = None
        self.features: Optional[List[str]] = None
        self.seq_length: Optional[int] = None
        self.tflite_interpreter: Optional[tf.lite.Interpreter] = None
        self.input_details: Optional[List[Dict]] = None
        self.output_details: Optional[List[Dict]] = None
        
        # Runtime history for real-time predictions
        self.sensor_history: Dict[str, deque] = {}
        self.edge_node_history: Dict[str, deque] = {}
        self.history_window = 50
        self.prediction_horizon = 10
        
        self.load_training_info()
        if use_tflite:
            self._initialize_tflite_model()
    
    def load_training_info(self) -> None:
        """Load scaler and training parameters"""
        try:
            # Load scaler
            scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
            if not os.path.exists(scaler_path):
                # Try relative path from current working directory
                scaler_path = os.path.join(os.path.dirname(__file__), 'models', 'scaler.pkl')
            
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            
            # Load training summary
            summary_path = os.path.join(self.model_dir, 'training_summary.pkl')
            if not os.path.exists(summary_path):
                summary_path = os.path.join(os.path.dirname(__file__), 'models', 'training_summary.pkl')
                
            with open(summary_path, 'rb') as f:
                summary = pickle.load(f)
                self.seq_length = summary['seq_length']
                self.features = summary['features']
                
        except FileNotFoundError as e:
            print(f"Warning: Training artifacts not found. Using fallback mode. Error: {e}")
            # Set defaults for fallback mode
            self.seq_length = 10
            self.features = ['workload']
    
    def _initialize_tflite_model(self, node_name: str = "system-1") -> None:
        """Initialize TFLite interpreter for edge deployment"""
        try:
            tflite_path = os.path.join(self.model_dir, f"{node_name}.tflite")
            
            # If TFLite model doesn't exist, try to convert from H5
            if not os.path.exists(tflite_path):
                h5_path = os.path.join(self.model_dir, f"{node_name}.h5")
                if os.path.exists(h5_path):
                    self._convert_to_tflite(h5_path, tflite_path)
                else:
                    print(f"Warning: No model found for {node_name}, using fallback prediction")
                    return
            
            # Load TFLite model
            self.tflite_interpreter = tf.lite.Interpreter(model_path=tflite_path)
            self.tflite_interpreter.allocate_tensors()
            
            # Get input and output details
            self.input_details = self.tflite_interpreter.get_input_details()
            self.output_details = self.tflite_interpreter.get_output_details()
            
            print(f"TFLite model loaded successfully for {node_name}")
            
        except Exception as e:
            print(f"Warning: Failed to load TFLite model: {e}")
            self.use_tflite = False
    
    def _convert_to_tflite(self, h5_path: str, tflite_path: str, quantize: bool = True) -> None:
        """Convert H5 model to TFLite with quantization for edge deployment"""
        try:
            # Load the original model
            model = tf.keras.models.load_model(h5_path, compile=False)
            
            # Convert to TFLite
            converter = tf.lite.TFLiteConverter.from_keras_model(model)
            
            if quantize:
                # Enable quantization for smaller model size
                converter.optimizations = [tf.lite.Optimize.DEFAULT]
                converter.target_spec.supported_types = [tf.float16]  # Use float16 for edge
            
            # Convert
            tflite_model = converter.convert()
            
            # Save TFLite model
            with open(tflite_path, 'wb') as f:
                f.write(tflite_model)
            
            print(f"Model converted to TFLite: {tflite_path}")
            
        except Exception as e:
            print(f"Warning: Failed to convert model to TFLite: {e}")
    
    def record_sensor_load(self, sensor_id: str, flow_rate: float, traffic_size: float) -> None:
        """Record sensor load for real-time prediction"""
        if sensor_id not in self.sensor_history:
            self.sensor_history[sensor_id] = deque(maxlen=self.history_window)
        
        load = flow_rate * traffic_size
        self.sensor_history[sensor_id].append(load)
    
    def record_edge_node_load(self, edge_node_id: str, total_load: float, capacity: float) -> None:
        """Record edge node load for real-time prediction"""
        if edge_node_id not in self.edge_node_history:
            self.edge_node_history[edge_node_id] = deque(maxlen=self.history_window)
        
        utilization = total_load / capacity if capacity > 0 else 0
        self.edge_node_history[edge_node_id].append(utilization)
    
    def predict_sensor_load(self, sensor_id: str, steps_ahead: int = 10) -> float:
        """Predict sensor load using TFLite model or fallback"""
        if sensor_id not in self.sensor_history or len(self.sensor_history[sensor_id]) < 3:
            return 1.0  # Default fallback
        
        history = list(self.sensor_history[sensor_id])
        
        if self.use_tflite and self.tflite_interpreter is not None:
            return self._predict_with_tflite(history, steps_ahead)
        else:
            return self._predict_with_fallback(history, steps_ahead)
    
    def predict_edge_node_utilization(self, edge_node_id: str, steps_ahead: int = 10) -> float:
        """Predict edge node utilization"""
        if edge_node_id not in self.edge_node_history or len(self.edge_node_history[edge_node_id]) < 3:
            return 0.5  # Default fallback
        
        history = list(self.edge_node_history[edge_node_id])
        
        if self.use_tflite and self.tflite_interpreter is not None:
            predicted = self._predict_with_tflite(history, steps_ahead)
            return np.clip(predicted, 0, 1)
        else:
            return self._predict_with_fallback(history, steps_ahead)
    
    def _predict_with_tflite(self, history: List[float], steps_ahead: int) -> float:
        """Make prediction using TFLite interpreter"""
        try:
            # Prepare input sequence
            if len(history) < self.seq_length:
                # Pad with last value if insufficient history
                padded_history = [history[-1]] * (self.seq_length - len(history)) + history
            else:
                padded_history = history[-self.seq_length:]
            
            # Scale the input if scaler is available
            if self.scaler is not None:
                input_data = np.array(padded_history).reshape(1, self.seq_length, 1)
                scaled_input = self.scaler.transform(input_data.reshape(-1, 1)).reshape(1, self.seq_length, 1)
            else:
                scaled_input = np.array(padded_history).reshape(1, self.seq_length, 1).astype(np.float32)
            
            # Set input tensor
            self.tflite_interpreter.set_tensor(self.input_details[0]['index'], scaled_input)
            
            # Run inference
            self.tflite_interpreter.invoke()
            
            # Get output
            output = self.tflite_interpreter.get_tensor(self.output_details[0]['index'])
            prediction = float(output[0, 0])
            
            # Inverse transform if scaler is available
            if self.scaler is not None:
                dummy_features = np.zeros((1, len(self.features)))
                dummy_features[0, 0] = prediction
                prediction = self.scaler.inverse_transform(dummy_features)[0, 0]
            
            return max(0, prediction)
            
        except Exception as e:
            print(f"TFLite prediction failed: {e}")
            return self._predict_with_fallback(history, steps_ahead)
    
    def _predict_with_fallback(self, history: List[float], steps_ahead: int) -> float:
        """Fallback prediction using simple linear trend"""
        if len(history) < 3:
            return history[-1] if history else 1.0
        
        # Simple linear trend prediction
        x = np.arange(len(history))
        coeffs = np.polyfit(x, history, deg=1)
        predicted = coeffs[0] * (len(history) + steps_ahead) + coeffs[1]
        
        return max(0, predicted)
    
    def predict_future_latency(self, sensor, edge_node, current_assignments, calculator) -> float:
        """Predict future latency for placement decisions"""
        sensor_id = sensor.device_id
        edge_node_id = edge_node.node_id
        
        predicted_sensor_load = self.predict_sensor_load(sensor_id, self.prediction_horizon)
        predicted_edge_util = self.predict_edge_node_utilization(edge_node_id, self.prediction_horizon)
        
        current_comm_latency = calculator.calculate_communication_latency(sensor, edge_node, current_assignments)
        current_comp_latency = calculator.calculate_computing_latency(sensor, edge_node, current_assignments)
        
        if current_comm_latency == float("inf") or current_comp_latency == float("inf"):
            return float("inf")
        
        # Calculate load increase factor
        current_load = sensor.averageFlowRate * sensor.flowTrafficSize
        load_increase_factor = predicted_sensor_load / current_load if current_load > 0 else 1.0
        
        # Apply utilization penalty
        utilization_penalty = 1.0 + (predicted_edge_util * 2.0)
        
        predicted_latency = (current_comm_latency + current_comp_latency) * load_increase_factor * utilization_penalty
        
        return predicted_latency
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage statistics for edge deployment monitoring"""
        memory_stats = {
            'history_memory_mb': 0,
            'model_memory_mb': 0,
            'total_memory_mb': 0
        }
        
        # Calculate history memory
        total_history_points = sum(len(hist) for hist in self.sensor_history.values()) + \
                              sum(len(hist) for hist in self.edge_node_history.values())
        memory_stats['history_memory_mb'] = (total_history_points * 8) / (1024 * 1024)  # 8 bytes per float64
        
        # Calculate model memory
        if self.use_tflite and self.tflite_interpreter:
            try:
                tflite_path = os.path.join(self.model_dir, "system-1.tflite")
                if os.path.exists(tflite_path):
                    model_size = os.path.getsize(tflite_path)
                    memory_stats['model_memory_mb'] = model_size / (1024 * 1024)
            except:
                pass
        
        memory_stats['total_memory_mb'] = memory_stats['history_memory_mb'] + memory_stats['model_memory_mb']
        
        return memory_stats


class PatternBasedWorkloadGenerator:
    """Lightweight workload pattern generator for edge deployment"""
    
    def __init__(self, pattern_type: str = "steady"):
        self.pattern_type = pattern_type
        self.time_step = 0
        self.history = deque(maxlen=50)  # Reduced memory footprint
    
    def get_current_multiplier(self) -> float:
        """Get current workload multiplier"""
        self.time_step += 1
        
        if self.pattern_type == "steady":
            multiplier = 1.0
        elif self.pattern_type == "periodic":
            multiplier = 1.0 + 0.3 * np.sin(self.time_step * 0.1)
        elif self.pattern_type == "bursty":
            multiplier = 3.0 if np.random.random() < 0.1 else 0.5
        elif self.pattern_type == "random":
            multiplier = np.random.uniform(0.5, 1.5)
        elif self.pattern_type == "increasing":
            multiplier = 1.0 + (self.time_step * 0.01)
        elif self.pattern_type == "decreasing":
            multiplier = max(0.3, 1.0 - (self.time_step * 0.01))
        else:
            multiplier = 1.0
        
        self.history.append(multiplier)
        return multiplier
    
    def forecast_future_multipliers(self, steps: int = 10) -> List[float]:
        """Forecast future multipliers"""
        if len(self.history) < 3:
            return [1.0] * steps
        
        # Simple moving average forecast
        recent_avg = np.mean(list(self.history)[-5:])
        return [recent_avg] * steps


class HealthcareWorkloadForecaster:
    """Healthcare-specific workload forecaster optimized for edge deployment"""
    
    def __init__(self, scenario_type: str = "icu"):
        self.scenario_type = scenario_type
        self.time_step = 0
        self.critical_event_active = False
        self.event_duration = 0
        self.event_history = deque(maxlen=50)  # Reduced memory
        self.load_history = deque(maxlen=50)
    
    def get_current_multiplier(self) -> float:
        """Get current healthcare workload multiplier"""
        self.time_step += 1
        
        if self.scenario_type == "icu":
            if np.random.random() < 0.05:
                self.critical_event_active = True
                self.event_duration = np.random.randint(10, 30)
                self.event_history.append(self.time_step)
            
            if self.critical_event_active:
                self.event_duration -= 1
                if self.event_duration <= 0:
                    self.critical_event_active = False
                multiplier = np.random.uniform(2.0, 4.0)
            else:
                multiplier = 1.0 + np.random.uniform(-0.1, 0.1)
        
        elif self.scenario_type == "emergency":
            if np.random.random() < 0.15:
                multiplier = np.random.uniform(2.5, 5.0)
                self.event_history.append(self.time_step)
            else:
                multiplier = np.random.uniform(0.8, 1.5)
        
        elif self.scenario_type == "ambulatory":
            hour_of_day = (self.time_step % 288) / 12
            if 8 <= hour_of_day <= 18:
                multiplier = 1.0 + 0.5 * np.sin((hour_of_day - 8) * np.pi / 10)
            else:
                multiplier = 0.3
        else:
            multiplier = 1.0
        
        self.load_history.append(multiplier)
        return multiplier
    
    def forecast_critical_event_probability(self, steps_ahead: int = 10) -> float:
        """Forecast probability of critical events"""
        if len(self.event_history) < 2:
            return 0.05 if self.scenario_type == "icu" else 0.15
        
        recent_events = [t for t in self.event_history if self.time_step - t < 50]
        event_rate = len(recent_events) / 50.0
        
        return min(0.5, event_rate * 1.5)
    
    def forecast_load_range(self, steps_ahead: int = 10) -> Tuple[float, float]:
        """Forecast load range"""
        if len(self.load_history) < 10:
            return (0.8, 1.5)
        
        recent_loads = list(self.load_history)[-20:]
        mean_load = np.mean(recent_loads)
        std_load = np.std(recent_loads)
        
        min_expected = max(0.3, mean_load - 2 * std_load)
        max_expected = mean_load + 2 * std_load
        
        return (min_expected, max_expected)


class TimeSeriesWorkloadForecaster:
    """Lightweight time series forecaster for edge deployment"""
    
    def __init__(self, pattern_type: str = "autoregressive"):
        self.pattern_type = pattern_type
        self.history = deque(maxlen=50)  # Reduced memory footprint
        self.time_step = 0

    def add_observation(self, value: float) -> None:
        """Add observation to history"""
        self.history.append(value)
        self.time_step += 1

    def forecast_next_steps(self, steps: int = 10) -> List[float]:
        """Forecast next steps using lightweight methods"""
        if len(self.history) < 3:
            return [1.0] * steps
        
        history_array = np.array(list(self.history))
        
        if self.pattern_type == "autoregressive":
            return self._ar_forecast(history_array, steps)
        elif self.pattern_type == "moving_average":
            return self._ma_forecast(history_array, steps)
        elif self.pattern_type == "exponential_smoothing":
            return self._exp_smoothing_forecast(history_array, steps)
        elif self.pattern_type == "trend_based":
            return self._trend_forecast(history_array, steps)
        
        return [np.mean(history_array)] * steps

    def _ar_forecast(self, history: np.ndarray, steps: int) -> List[float]:
        """Autoregressive forecast with reduced complexity"""
        if len(history) < 3:
            return [history[-1]] * steps
        
        lag = min(2, len(history) - 1)  # Reduced lag for edge deployment
        X = np.array([history[i-lag:i] for i in range(lag, len(history))])
        y = history[lag:]
        
        if len(X) == 0:
            return [history[-1]] * steps
        
        try:
            coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
        except:
            return [history[-1]] * steps
        
        forecast = []
        current_window = list(history[-lag:])
        
        for _ in range(steps):
            next_val = np.dot(coeffs, current_window)
            forecast.append(max(0, next_val))
            current_window = current_window[1:] + [next_val]
        
        return forecast

    def _ma_forecast(self, history: np.ndarray, steps: int) -> List[float]:
        """Moving average forecast"""
        window_size = min(5, len(history))  # Reduced window for edge deployment
        ma = np.mean(history[-window_size:])
        return [ma] * steps

    def _exp_smoothing_forecast(self, history: np.ndarray, steps: int) -> List[float]:
        """Exponential smoothing forecast"""
        alpha = 0.3
        smoothed = history[0]
        
        for val in history[1:]:
            smoothed = alpha * val + (1 - alpha) * smoothed
        
        return [smoothed] * steps

    def _trend_forecast(self, history: np.ndarray, steps: int) -> List[float]:
        """Trend-based forecast"""
        if len(history) < 2:
            return [history[-1]] * steps
            
        x = np.arange(len(history))
        try:
            coeffs = np.polyfit(x, history, deg=1)
        except:
            return [history[-1]] * steps
        
        forecast = []
        for i in range(steps):
            next_x = len(history) + i
            next_val = coeffs[0] * next_x + coeffs[1]
            forecast.append(max(0, next_val))
        
        return forecast
