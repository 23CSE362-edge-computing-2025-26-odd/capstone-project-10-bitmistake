# Predictive Workload-Aware Placement Guide

## Overview

This implements **latency-based predictive placement** algorithms that forecast future workload and make proactive placement decisions, unlike OLB's reactive approach.

## Key Difference from OLB

### OLB (Reactive)
- Uses **current state** to calculate latency
- Minimizes latency at placement time
- No consideration of future workload changes

### Predictive Placement (Proactive)
- **Forecasts future workload** trends
- Predicts future latency based on historical patterns
- Places sensors to minimize **expected future latency**

## Three Predictive Approaches

### 1. PredictiveLatencyPlacement

**Method**: Time-series forecasting of sensor load and fog utilization

**How it works**:
1. Records historical sensor flow rates and fog node utilization
2. Uses linear regression to predict future trends
3. Calculates predicted latency = current_latency × load_increase × utilization_penalty
4. Places sensor on fog node with lowest predicted latency

**Best for**: Workloads with clear trends (increasing, decreasing, periodic)

**Example**:
```python
from src import PredictiveLatencyPlacement

placement = PredictiveLatencyPlacement(
    "Predictive_OLB",
    placement_json,
    environment,
    prediction_horizon=10
)
```

### 2. ForecastBasedPlacement

**Method**: Pattern-based workload forecasting

**How it works**:
1. Uses TimeSeriesWorkloadForecaster to predict load multipliers
2. Applies forecasted multiplier to sensor flow rates
3. Calculates latency with adjusted flow rates
4. Places sensor based on forecasted conditions

**Best for**: Known workload patterns (periodic, bursty, steady)

**Example**:
```python
from src import ForecastBasedPlacement, PatternBasedWorkloadGenerator

workload_gen = PatternBasedWorkloadGenerator("periodic")
placement = ForecastBasedPlacement(
    "Forecast_OLB",
    placement_json,
    environment,
    workload_gen
)
```

### 3. AdaptivePredictivePlacement (Future Work)

**Method**: Switches between predictive and reactive based on prediction accuracy

**How it works**:
1. Tracks prediction errors over time
2. Uses predictive mode when errors are low
3. Falls back to reactive mode when predictions are unreliable
4. Adapts to workload pattern changes

## Workload Forecasting Models

### WorkloadPredictor
Records and predicts sensor/fog node loads using linear regression

**Methods**:
- `record_sensor_load()`: Track sensor flow rate history
- `record_fog_node_load()`: Track fog utilization history
- `predict_sensor_load()`: Forecast future sensor load
- `predict_fog_node_utilization()`: Forecast future fog utilization
- `predict_future_latency()`: Combine predictions to estimate latency

### TimeSeriesWorkloadForecaster
Provides multiple forecasting algorithms

**Algorithms**:
- **autoregressive**: AR(3) model using last 3 observations
- **moving_average**: Simple moving average
- **exponential_smoothing**: Exponential weighted average (α=0.3)
- **trend_based**: Linear trend extrapolation

**Usage**:
```python
forecaster = TimeSeriesWorkloadForecaster("autoregressive")
forecaster.add_observation(1.2)
forecaster.add_observation(1.5)
future_values = forecaster.forecast_next_steps(10)
```

### PatternBasedWorkloadGenerator
Generates and forecasts workload patterns

**Patterns**:
- steady: Constant 1.0x
- periodic: Sinusoidal variation
- bursty: Random 3x spikes
- increasing: Linear growth
- decreasing: Linear decay
- random: Uniform random

**Usage**:
```python
gen = PatternBasedWorkloadGenerator("periodic")
current = gen.get_current_multiplier()
future = gen.forecast_future_multipliers(10)
```

### HealthcareWorkloadForecaster
Healthcare-specific workload patterns with forecasting

**Scenarios**:
- **icu**: 5% critical event probability, 2-4x load spikes
- **emergency**: 15% emergency probability, 2.5-5x spikes
- **ambulatory**: Daily cycle (8am-6pm peaks)

**Methods**:
- `get_current_multiplier()`: Current load multiplier
- `forecast_critical_event_probability()`: Predict event likelihood
- `forecast_load_range()`: Predict min/max load range

## Running the Comparison Study

```bash
cd experiments
python predictive_vs_reactive_comparison.py
```

### What it Tests

**Part 1: Workload Pattern Comparison**
- Tests on: steady, periodic, bursty, increasing patterns
- Compares: Reactive OLB vs Predictive vs Forecast-based
- Measures: Latency, energy, load balance

**Part 2: Healthcare Scenario Comparison**
- Tests on: ICU, Emergency, Ambulatory scenarios
- Compares: Reactive OLB vs Predictive
- Measures: Real-world applicability

### Expected Results

**Periodic Workload**:
- Predictive: 15-25% better than reactive
- Reason: Can anticipate load cycles

**Bursty Workload**:
- Predictive: Similar or worse than reactive
- Reason: Unpredictable spikes hard to forecast

**Increasing Workload**:
- Predictive: 20-30% better than reactive
- Reason: Trend detection prevents overload

**ICU Scenario**:
- Predictive: 10-15% better
- Reason: Critical events have patterns

**Emergency Scenario**:
- Predictive: 5-10% better
- Reason: High unpredictability limits benefit

**Ambulatory Scenario**:
- Predictive: 25-35% better
- Reason: Strong daily cycle pattern

## Implementation Details

### Prediction Horizon
Number of time steps to forecast ahead (default: 10)

**Trade-off**:
- Short horizon (5): More accurate, less proactive
- Long horizon (20): Less accurate, more proactive

### History Window
Number of past observations to use (default: 50)

**Trade-off**:
- Small window (20): Adapts quickly, less stable
- Large window (100): More stable, slower adaptation

### Load Increase Factor
```python
load_increase_factor = predicted_load / current_load
```
Multiplier applied to current latency based on predicted load change

### Utilization Penalty
```python
utilization_penalty = 1.0 + (predicted_utilization * 2.0)
```
Penalty factor for high fog node utilization (0-100% → 1.0-3.0x)

## When to Use Each Approach

### Use Reactive OLB When:
- Workload is completely random
- No historical data available
- Simplicity is priority
- Prediction overhead not acceptable

### Use PredictiveLatencyPlacement When:
- Workload has trends (increasing/decreasing)
- Historical data available
- Willing to trade computation for accuracy
- Proactive placement valuable

### Use ForecastBasedPlacement When:
- Workload pattern is known (periodic, bursty)
- Pattern-specific optimization needed
- Can characterize workload type
- Want pattern-aware placement

## Integration Example

```python
from src import (
    DigitalTwinEnvironment,
    PredictiveLatencyPlacement,
    PatternBasedWorkloadGenerator,
    create_smart_healthcare_application,
    create_yafs_topology,
    create_placement_json
)

environment = DigitalTwinEnvironment(3000, 2000)
environment.initialize_sensors(20, seed=42)
environment.initialize_fog_nodes(6, seed=42)

workload_gen = PatternBasedWorkloadGenerator("periodic")

for _ in range(10):
    workload_gen.get_current_multiplier()

app = create_smart_healthcare_application(environment)
topology = create_yafs_topology(environment)
placement_json = create_placement_json("config")

placement = PredictiveLatencyPlacement(
    "Predictive_Healthcare",
    placement_json,
    environment,
    prediction_horizon=10
)

from yafs.core import Sim
from yafs.population import Population

s = Sim(topology, default_results_path="results/")
population = Population(name="PredictiveSensors")
s.deploy_app(app, placement, population)
s.run(until=1000)
```

## Output Files

```
data/predictive_comparison_YYYYMMDD_HHMMSS.json
reports/predictive_comparison_YYYYMMDD_HHMMSS.txt
```

## Key Metrics

### Prediction Accuracy
How well forecasts match actual workload

### Latency Improvement
Percentage reduction vs reactive OLB

### Placement Stability
How often sensors need reassignment

### Overhead
Computation time for prediction vs placement

## Research Contributions

1. **Novel approach**: Latency-based workload prediction for fog placement
2. **Multiple forecasting methods**: AR, MA, exponential smoothing, trend
3. **Healthcare-specific patterns**: ICU, emergency, ambulatory
4. **Comprehensive comparison**: Reactive vs predictive across patterns
5. **Practical insights**: When prediction helps vs hurts

## Future Enhancements

1. **Machine learning forecasting**: LSTM, GRU for complex patterns
2. **Multi-step ahead prediction**: Optimize for entire horizon
3. **Confidence intervals**: Quantify prediction uncertainty
4. **Online learning**: Update models during simulation
5. **Hybrid approaches**: Combine multiple forecasting methods
6. **Reinforcement learning**: Learn optimal prediction strategy

## Limitations

1. **Cold start**: Needs historical data to predict
2. **Pattern changes**: Slow to adapt to new patterns
3. **Computational overhead**: Prediction adds latency
4. **Accuracy dependency**: Poor predictions hurt performance
5. **Horizon selection**: No automatic tuning

## Validation

Run validation script:
```bash
python validate_predictive_placement.py
```

Checks:
- Forecasting accuracy on known patterns
- Prediction overhead measurement
- Latency improvement verification
- Edge case handling
