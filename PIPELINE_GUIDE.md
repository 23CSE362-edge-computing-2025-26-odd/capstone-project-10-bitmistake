# Complete Pipeline Guide

## Overview

Three pipeline scripts demonstrate the entire predictive placement system from basic demo to comprehensive evaluation.

## Pipeline Options

### 1. Quick Demo Pipeline (5 minutes)
**File**: `pipeline_demo.py`

**What it does**:
- Creates environment
- Generates workload patterns
- Runs 3 algorithms (Reactive, Predictive, Forecast)
- Compares results
- Generates report and plots

**Run**:
```bash
python pipeline_demo.py
```

**Output**:
- `data/environment_*.json` - Environment configuration
- `data/workload_patterns_*.json` - Generated patterns
- `data/pipeline_results_*.json` - Algorithm results
- `reports/pipeline_report_*.txt` - Detailed report
- `plots/reactive_olb_*.png` - Reactive placement visualization
- `plots/predictive_latency_*.png` - Predictive placement visualization
- `plots/forecast_based_*.png` - Forecast placement visualization
- `plots/comparison_*.png` - Performance comparison chart

**Best for**: Quick demonstration, understanding the workflow

---

### 2. Complete Pipeline (10-15 minutes)
**File**: `run_complete_pipeline.py`

**What it does**:
- **Scenario 1**: Baseline comparison (4 algorithms)
- **Scenario 2**: Workload patterns (4 patterns × 3 algorithms)
- **Scenario 3**: Scalability (3 scales × 2 algorithms)
- **Scenario 4**: Healthcare scenarios (3 scenarios × 2 algorithms)

**Run**:
```bash
python run_complete_pipeline.py
```

**Output**:
- `data/complete_pipeline_*.json` - All scenario results
- `reports/complete_pipeline_*.txt` - Comprehensive report
- `plots/scenario1_*_*.png` - Baseline visualizations
- `plots/scenario1_comparison_*.png` - Baseline comparison

**Best for**: Comprehensive evaluation, research paper results

---

### 3. Predictive vs Reactive Study (15-20 minutes)
**File**: `experiments/predictive_vs_reactive_comparison.py`

**What it does**:
- Tests 4 workload patterns (steady, periodic, bursty, increasing)
- Tests 3 healthcare scenarios (ICU, emergency, ambulatory)
- Compares Reactive vs Predictive vs Forecast-based
- Generates detailed analysis

**Run**:
```bash
cd experiments
python predictive_vs_reactive_comparison.py
```

**Output**:
- `data/predictive_comparison_*.json` - Detailed results
- `reports/predictive_comparison_*.txt` - Analysis report

**Best for**: Research comparison, pattern analysis

---

## Pipeline Workflow

### Quick Demo Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Create Environment                                  │
│  - Initialize 15 sensors, 6 fog nodes                       │
│  - Save environment configuration                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Generate Workload Patterns                          │
│  - Create 4 patterns (steady, periodic, bursty, increasing) │
│  - Generate history and forecasts                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Run Reactive OLB (Baseline)                         │
│  - Standard OLB placement                                   │
│  - Collect metrics                                          │
│  - Generate visualization                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Run Predictive Latency Placement                    │
│  - Forecast-based placement                                 │
│  - Compare with baseline                                    │
│  - Generate visualization                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Run Forecast-Based Placement                        │
│  - Pattern-aware placement                                  │
│  - Compare with baseline                                    │
│  - Generate visualization                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: Compare Results                                     │
│  - Generate comparison table                                │
│  - Calculate improvements                                   │
│  - Create comparison plot                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: Generate Report                                     │
│  - Comprehensive text report                                │
│  - JSON data export                                         │
│  - Summary statistics                                       │
└─────────────────────────────────────────────────────────────┘
```

### Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│ SCENARIO 1: Baseline Comparison                             │
│  - Reactive OLB                                             │
│  - Random Placement                                         │
│  - Distance Placement                                       │
│  - Predictive Latency                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ SCENARIO 2: Workload Patterns                               │
│  For each pattern (steady, periodic, bursty, increasing):   │
│    - Reactive OLB                                           │
│    - Predictive Latency                                     │
│    - Forecast-Based                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ SCENARIO 3: Scalability                                     │
│  For each scale (10, 20, 30 sensors):                       │
│    - Reactive OLB                                           │
│    - Predictive Latency                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ SCENARIO 4: Healthcare Scenarios                            │
│  For each scenario (ICU, emergency, ambulatory):            │
│    - Reactive OLB                                           │
│    - Predictive Latency                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Generate Comprehensive Report                               │
│  - All scenario results                                     │
│  - Cross-scenario analysis                                  │
│  - Key findings                                             │
└─────────────────────────────────────────────────────────────┘
```

## Output Structure

```
project/
├── data/
│   ├── environment_TIMESTAMP.json
│   ├── workload_patterns_TIMESTAMP.json
│   ├── pipeline_results_TIMESTAMP.json
│   └── complete_pipeline_TIMESTAMP.json
│
├── reports/
│   ├── pipeline_report_TIMESTAMP.txt
│   └── complete_pipeline_TIMESTAMP.txt
│
├── plots/
│   ├── reactive_olb_TIMESTAMP.png
│   ├── predictive_latency_TIMESTAMP.png
│   ├── forecast_based_TIMESTAMP.png
│   ├── comparison_TIMESTAMP.png
│   ├── scenario1_*_TIMESTAMP.png
│   └── scenario1_comparison_TIMESTAMP.png
│
└── results/
    └── (YAFS simulation outputs)
```

## Metrics Collected

Each algorithm run collects:

1. **Latency Metrics**:
   - Overall latency (ms)
   - Communication latency
   - Computing latency
   - Average latency per sensor

2. **Energy Metrics**:
   - Total energy consumption (W)
   - Transmission energy
   - Processing energy

3. **Load Balance Metrics**:
   - Load balance score (0-1)
   - Load variance
   - Max utilization

4. **Performance Metrics**:
   - Network usage (MB/s)
   - Cost of execution
   - Execution time (s)

## Interpreting Results

### Latency Improvement
```
Improvement = (Baseline_Latency - Algorithm_Latency) / Baseline_Latency × 100%
```

**Positive**: Algorithm is better than baseline
**Negative**: Baseline is better than algorithm

### Load Balance Score
```
Score = 1.0 / (1.0 + variance)
```

**Higher is better** (1.0 = perfect balance, 0.0 = poor balance)

### Expected Results

| Scenario | Expected Improvement |
|----------|---------------------|
| Steady workload | 0-5% |
| Periodic workload | 15-25% |
| Bursty workload | -5-5% |
| Increasing workload | 20-30% |
| ICU scenario | 10-15% |
| Emergency scenario | 5-10% |
| Ambulatory scenario | 25-35% |

## Customization

### Modify Environment Size
```python
environment_config = {
    "width": 5000,        # Change from 3000
    "height": 3000,       # Change from 2000
    "num_sensors": 30,    # Change from 15
    "num_fog_nodes": 10,  # Change from 6
    "seed": 42,
    "sim_time": 1000      # Change from 500
}
```

### Add New Algorithm
```python
algorithms = [
    ("My_Algorithm", MyAlgorithmClass, None, {"param": value}),
]
```

### Change Workload Pattern
```python
workload_gen = PatternBasedWorkloadGenerator("periodic")  # or "bursty", "increasing"
```

### Adjust Prediction Horizon
```python
placement = PredictiveLatencyPlacement(
    "Predictive",
    placement_json,
    environment,
    prediction_horizon=20  # Change from 10
)
```

## Troubleshooting

### Issue: YAFS import error
**Solution**: Install YAFS
```bash
pip install yafs
```

### Issue: NumPy error
**Solution**: Install NumPy
```bash
pip install numpy
```

### Issue: Matplotlib error
**Solution**: Install Matplotlib
```bash
pip install matplotlib
```

### Issue: Out of memory
**Solution**: Reduce sensor count or simulation time
```python
environment_config["num_sensors"] = 10  # Reduce from 15
environment_config["sim_time"] = 300    # Reduce from 500
```

### Issue: Slow execution
**Solution**: Run quick demo instead of complete pipeline
```bash
python pipeline_demo.py  # Instead of run_complete_pipeline.py
```

## Validation

Before running pipelines, validate installation:
```bash
python validate_improvements.py
python validate_predictive_placement.py
```

Both should complete without errors.

## Next Steps

1. **Run quick demo**: `python pipeline_demo.py`
2. **Review plots**: Check `plots/` directory
3. **Read report**: Open `reports/pipeline_report_*.txt`
4. **Run complete pipeline**: `python run_complete_pipeline.py`
5. **Analyze results**: Compare metrics across scenarios

## Research Usage

For research papers:

1. Run complete pipeline for comprehensive results
2. Use plots from `plots/` directory
3. Extract metrics from `data/*.json` files
4. Reference report findings from `reports/*.txt`
5. Cite key improvements and trade-offs

## Performance Benchmarks

**Quick Demo Pipeline**:
- Time: ~5 minutes
- Algorithms: 3
- Scenarios: 1
- Output files: 8

**Complete Pipeline**:
- Time: ~10-15 minutes
- Algorithms: 4
- Scenarios: 4
- Output files: 20+

**Predictive vs Reactive Study**:
- Time: ~15-20 minutes
- Algorithms: 3
- Scenarios: 7
- Output files: 2

## Citation

If you use these pipelines in research:
```
Predictive Workload-Aware Placement for Fog Computing
Latency-Based Forecasting Pipeline for IoT Healthcare Systems
```
