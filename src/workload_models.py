import math
import random
import numpy as np
from collections import deque


class WorkloadPredictor:
    def __init__(self, history_window=50, prediction_horizon=10):
        self.history_window = history_window
        self.prediction_horizon = prediction_horizon
        self.sensor_history = {}
        self.fog_node_history = {}

    def record_sensor_load(self, sensor_id, flow_rate, traffic_size):
        if sensor_id not in self.sensor_history:
            self.sensor_history[sensor_id] = deque(maxlen=self.history_window)
        
        load = flow_rate * traffic_size
        self.sensor_history[sensor_id].append(load)

    def record_fog_node_load(self, fog_node_id, total_load, capacity):
        if fog_node_id not in self.fog_node_history:
            self.fog_node_history[fog_node_id] = deque(maxlen=self.history_window)
        
        utilization = total_load / capacity if capacity > 0 else 0
        self.fog_node_history[fog_node_id].append(utilization)

    def predict_sensor_load(self, sensor_id, steps_ahead=10):
        if sensor_id not in self.sensor_history or len(self.sensor_history[sensor_id]) < 3:
            return None
        
        history = list(self.sensor_history[sensor_id])
        
        if len(history) < 10:
            return np.mean(history)
        
        recent_trend = np.polyfit(range(len(history)), history, deg=1)
        predicted_load = recent_trend[0] * (len(history) + steps_ahead) + recent_trend[1]
        
        return max(0, predicted_load)

    def predict_fog_node_utilization(self, fog_node_id, steps_ahead=10):
        if fog_node_id not in self.fog_node_history or len(self.fog_node_history[fog_node_id]) < 3:
            return 0.5
        
        history = list(self.fog_node_history[fog_node_id])
        
        if len(history) < 10:
            return np.mean(history)
        
        recent_trend = np.polyfit(range(len(history)), history, deg=1)
        predicted_util = recent_trend[0] * (len(history) + steps_ahead) + recent_trend[1]
        
        return np.clip(predicted_util, 0, 1)

    def predict_future_latency(self, sensor, fog_node, current_assignments, calculator):
        sensor_id = sensor.device_id
        fog_node_id = fog_node.node_id
        
        predicted_sensor_load = self.predict_sensor_load(sensor_id, self.prediction_horizon)
        if predicted_sensor_load is None:
            predicted_sensor_load = sensor.averageFlowRate * sensor.flowTrafficSize
        
        predicted_fog_util = self.predict_fog_node_utilization(fog_node_id, self.prediction_horizon)
        
        current_comm_latency = calculator.calculate_communication_latency(sensor, fog_node, current_assignments)
        current_comp_latency = calculator.calculate_computing_latency(sensor, fog_node, current_assignments)
        
        if current_comm_latency == float("inf") or current_comp_latency == float("inf"):
            return float("inf")
        
        load_increase_factor = predicted_sensor_load / (sensor.averageFlowRate * sensor.flowTrafficSize) if sensor.averageFlowRate * sensor.flowTrafficSize > 0 else 1.0
        utilization_penalty = 1.0 + (predicted_fog_util * 2.0)
        
        predicted_latency = (current_comm_latency + current_comp_latency) * load_increase_factor * utilization_penalty
        
        return predicted_latency


class TimeSeriesWorkloadForecaster:
    def __init__(self, pattern_type="autoregressive"):
        self.pattern_type = pattern_type
        self.history = deque(maxlen=100)
        self.time_step = 0

    def add_observation(self, value):
        self.history.append(value)
        self.time_step += 1

    def forecast_next_steps(self, steps=10):
        if len(self.history) < 5:
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

    def _ar_forecast(self, history, steps):
        if len(history) < 3:
            return [history[-1]] * steps
        
        lag = min(3, len(history) - 1)
        X = np.array([history[i-lag:i] for i in range(lag, len(history))])
        y = history[lag:]
        
        if len(X) == 0:
            return [history[-1]] * steps
        
        coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
        
        forecast = []
        current_window = list(history[-lag:])
        
        for _ in range(steps):
            next_val = np.dot(coeffs, current_window)
            forecast.append(max(0, next_val))
            current_window = current_window[1:] + [next_val]
        
        return forecast

    def _ma_forecast(self, history, steps):
        window_size = min(10, len(history))
        ma = np.mean(history[-window_size:])
        return [ma] * steps

    def _exp_smoothing_forecast(self, history, steps):
        alpha = 0.3
        smoothed = history[0]
        
        for val in history[1:]:
            smoothed = alpha * val + (1 - alpha) * smoothed
        
        return [smoothed] * steps

    def _trend_forecast(self, history, steps):
        x = np.arange(len(history))
        coeffs = np.polyfit(x, history, deg=1)
        
        forecast = []
        for i in range(steps):
            next_x = len(history) + i
            next_val = coeffs[0] * next_x + coeffs[1]
            forecast.append(max(0, next_val))
        
        return forecast


class PatternBasedWorkloadGenerator:
    def __init__(self, pattern_type="steady"):
        self.pattern_type = pattern_type
        self.time_step = 0
        self.forecaster = TimeSeriesWorkloadForecaster(pattern_type)

    def get_current_multiplier(self):
        self.time_step += 1
        
        if self.pattern_type == "steady":
            multiplier = 1.0
        elif self.pattern_type == "periodic":
            multiplier = 1.0 + 0.3 * math.sin(self.time_step * 0.1)
        elif self.pattern_type == "bursty":
            multiplier = 3.0 if random.random() < 0.1 else 0.5
        elif self.pattern_type == "random":
            multiplier = random.uniform(0.5, 1.5)
        elif self.pattern_type == "increasing":
            multiplier = 1.0 + (self.time_step * 0.01)
        elif self.pattern_type == "decreasing":
            multiplier = max(0.3, 1.0 - (self.time_step * 0.01))
        else:
            multiplier = 1.0
        
        self.forecaster.add_observation(multiplier)
        return multiplier

    def forecast_future_multipliers(self, steps=10):
        return self.forecaster.forecast_next_steps(steps)

    def apply_to_sensor(self, sensor):
        multiplier = self.get_current_multiplier()
        sensor.averageFlowRate *= multiplier
        return multiplier


class HealthcareWorkloadForecaster:
    def __init__(self, scenario_type="icu"):
        self.scenario_type = scenario_type
        self.time_step = 0
        self.critical_event_active = False
        self.event_duration = 0
        self.event_history = deque(maxlen=100)
        self.load_history = deque(maxlen=100)

    def get_current_multiplier(self):
        self.time_step += 1
        
        if self.scenario_type == "icu":
            if random.random() < 0.05:
                self.critical_event_active = True
                self.event_duration = random.randint(10, 30)
                self.event_history.append(self.time_step)
            
            if self.critical_event_active:
                self.event_duration -= 1
                if self.event_duration <= 0:
                    self.critical_event_active = False
                multiplier = random.uniform(2.0, 4.0)
            else:
                multiplier = 1.0 + random.uniform(-0.1, 0.1)
        
        elif self.scenario_type == "emergency":
            if random.random() < 0.15:
                multiplier = random.uniform(2.5, 5.0)
                self.event_history.append(self.time_step)
            else:
                multiplier = random.uniform(0.8, 1.5)
        
        elif self.scenario_type == "ambulatory":
            hour_of_day = (self.time_step % 288) / 12
            if 8 <= hour_of_day <= 18:
                multiplier = 1.0 + 0.5 * math.sin((hour_of_day - 8) * math.pi / 10)
            else:
                multiplier = 0.3
        else:
            multiplier = 1.0
        
        self.load_history.append(multiplier)
        return multiplier

    def forecast_critical_event_probability(self, steps_ahead=10):
        if len(self.event_history) < 2:
            return 0.05 if self.scenario_type == "icu" else 0.15
        
        recent_events = [t for t in self.event_history if self.time_step - t < 50]
        event_rate = len(recent_events) / 50.0
        
        return min(0.5, event_rate * 1.5)

    def forecast_load_range(self, steps_ahead=10):
        if len(self.load_history) < 10:
            return (0.8, 1.5)
        
        recent_loads = list(self.load_history)[-20:]
        mean_load = np.mean(recent_loads)
        std_load = np.std(recent_loads)
        
        min_expected = max(0.3, mean_load - 2 * std_load)
        max_expected = mean_load + 2 * std_load
        
        return (min_expected, max_expected)

    def apply_to_sensors(self, sensors):
        multiplier = self.get_current_multiplier()
        for sensor in sensors:
            sensor.averageFlowRate *= multiplier
        return multiplier
