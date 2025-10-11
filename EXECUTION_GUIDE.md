# Complete Pipeline Execution Guide

## Prerequisites

### 1. Activate Conda Environment
```bash
conda activate tensorflow_gpu_env
```

### 2. Verify Python Version
```bash
python --version
```
Should be Python 3.7 or higher

### 3. Install Dependencies
```bash
pip install yafs numpy matplotlib pandas
```

## Execution Methods

### Method 1: Safe Runner (Recommended)

This method checks everything before running:

```bash
conda activate tensorflow_gpu_env
python run_pipeline_safe.py
```

**What it does**:
1. ✅ Checks all dependencies
2. ✅ Verifies directory structure
3. ✅ Checks source files
4. ✅ Tests imports
5. ✅ Runs quick test
6. ✅ Executes complete pipeline

**If any check fails**, it will tell you exactly what to fix.

### Method 2: Direct Execution

If you're confident everything is set up:

```bash
conda activate tensorflow_gpu_env
python run_complete_pipeline.py
```

### Method 3: Step-by-Step Manual

If you want to run each step manually:

```bash
# 1. Activate environment
conda activate tensorflow_gpu_env

# 2. Check dependencies
python -c "import yafs, numpy, matplotlib, pandas; print('All dependencies OK')"

# 3. Create directories
mkdir -p results data reports plots config

# 4. Run pipeline
python run_complete_pipeline.py
```

## Common Issues and Solutions

### Issue 1: ModuleNotFoundError: No module named 'yafs'

**Solution**:
```bash
conda activate tensorflow_gpu_env
pip install yafs
```

### Issue 2: ModuleNotFoundError: No module named 'src'

**Solution**: Make sure you're in the project root directory
```bash
cd /path/to/your/project
python run_complete_pipeline.py
```

### Issue 3: ImportError: cannot import name 'PredictiveLatencyPlacement'

**Solution**: The files were auto-formatted. Re-read them:
```bash
python -c "from src import PredictiveLatencyPlacement; print('Import OK')"
```

If this fails, check `src/__init__.py` has the correct imports.

### Issue 4: FileNotFoundError: placement_config.json

**Solution**: Create config directory
```bash
mkdir -p config
python run_complete_pipeline.py
```

### Issue 5: MemoryError or Out of Memory

**Solution**: Reduce sensor count in the pipeline
Edit `run_complete_pipeline.py` and change:
```python
"num_sensors": 10,  # Reduce from 15
```

### Issue 6: YAFS simulation hangs

**Solution**: Reduce simulation time
Edit `run_complete_pipeline.py` and change:
```python
"sim_time": 300  # Reduce from 500
```

## Troubleshooting Workflow

### Step 1: Check Environment
```bash
conda activate tensorflow_gpu_env
python --version
which python
```

### Step 2: Check Dependencies
```bash
python -c "import yafs; print('YAFS:', yafs.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import matplotlib; print('Matplotlib:', matplotlib.__version__)"
python -c "import pandas; print('Pandas:', pandas.__version__)"
```

### Step 3: Check Source Files
```bash
ls src/__init__.py
ls src/olb_algorithm.py
ls src/predictive_placement.py
ls src/workload_models.py
```

### Step 4: Test Imports
```bash
python -c "from src import DigitalTwinEnvironment; print('Import OK')"
python -c "from src import OLBPlacement; print('Import OK')"
python -c "from src import PredictiveLatencyPlacement; print('Import OK')"
```

### Step 5: Run Quick Test
```bash
python -c "
from src import DigitalTwinEnvironment
env = DigitalTwinEnvironment(1000, 1000)
env.initialize_sensors(5, seed=42)
print(f'Test OK: {len(env.sensors)} sensors created')
"
```

### Step 6: Run Safe Pipeline
```bash
python run_pipeline_safe.py
```

## Expected Output

### Console Output
```
================================================================================
  COMPLETE PREDICTIVE PLACEMENT PIPELINE
================================================================================

This pipeline runs 4 comprehensive scenarios:
  1. Baseline algorithm comparison
  2. Workload pattern analysis
  3. Scalability testing
  4. Healthcare scenario evaluation

Estimated time: 5-10 minutes

Press Enter to start...

================================================================================
SCENARIO 1: BASELINE ALGORITHM COMPARISON
================================================================================

Testing all algorithms on standard environment:
  - 15 sensors, 6 fog nodes
  - No workload patterns
  - 500 time steps

  Running Reactive_OLB... ✓ (12.34s)
     Latency: 0.1234 ms
  Running Random_Placement... ✓ (10.23s)
     Latency: 0.2345 ms
  ...
```

### Output Files

After successful completion, you'll have:

```
data/
├── complete_pipeline_YYYYMMDD_HHMMSS.json

reports/
├── complete_pipeline_YYYYMMDD_HHMMSS.txt

plots/
├── scenario1_reactive_olb_YYYYMMDD_HHMMSS.png
├── scenario1_random_placement_YYYYMMDD_HHMMSS.png
├── scenario1_distance_placement_YYYYMMDD_HHMMSS.png
├── scenario1_predictive_latency_YYYYMMDD_HHMMSS.png
└── scenario1_comparison_YYYYMMDD_HHMMSS.png
```

## Execution Time

| Scenario | Expected Time |
|----------|---------------|
| Scenario 1: Baseline | 2-3 minutes |
| Scenario 2: Patterns | 3-5 minutes |
| Scenario 3: Scalability | 2-3 minutes |
| Scenario 4: Healthcare | 2-3 minutes |
| **Total** | **10-15 minutes** |

## Monitoring Progress

The pipeline prints progress for each step:
- ✓ = Success
- ✗ = Failure
- ⚠ = Warning

Watch for:
- Algorithm execution times
- Latency values
- Error messages

## If Pipeline Fails

### 1. Check the error message
Look for the last error printed before failure

### 2. Check log files
```bash
cat logs/olb_simulation.log
```

### 3. Run validation
```bash
python validate_improvements.py
python validate_predictive_placement.py
```

### 4. Run quick demo instead
```bash
python pipeline_demo.py
```

### 5. Get help
- Check `TROUBLESHOOTING.md`
- Review error in console
- Check `PIPELINE_GUIDE.md`

## Success Indicators

✅ All scenarios complete
✅ No error messages
✅ Output files created
✅ Plots generated
✅ Report contains results

## Post-Execution

### View Results
```bash
# View report
cat reports/complete_pipeline_*.txt

# View data
python -c "import json; print(json.dumps(json.load(open('data/complete_pipeline_*.json')), indent=2))"

# View plots
# Open plots/*.png in image viewer
```

### Analyze Results
1. Open report in text editor
2. Review comparison tables
3. Check improvement percentages
4. Examine plots for visual analysis

## Next Steps

After successful execution:

1. **Review Results**: Read the generated report
2. **Analyze Plots**: Check visualizations in `plots/`
3. **Extract Data**: Use JSON files for further analysis
4. **Run Variations**: Modify parameters and re-run
5. **Research Study**: Run `experiments/predictive_vs_reactive_comparison.py`

## Quick Commands Reference

```bash
# Activate environment
conda activate tensorflow_gpu_env

# Safe execution (recommended)
python run_pipeline_safe.py

# Direct execution
python run_complete_pipeline.py

# Quick demo (5 min)
python pipeline_demo.py

# Validation
python validate_improvements.py

# Check dependencies
python -c "import yafs, numpy, matplotlib, pandas; print('OK')"

# View results
ls -lh data/
ls -lh reports/
ls -lh plots/
```

## Emergency Stop

If you need to stop the pipeline:
- Press `Ctrl+C` once
- Wait for graceful shutdown
- Check partial results in output directories

## Cleanup

To clean output before re-running:
```bash
rm -rf data/*.json
rm -rf reports/*.txt
rm -rf plots/*.png
rm -rf results/*
```

## Support

If you encounter issues:
1. Run `python run_pipeline_safe.py` for diagnostics
2. Check `TROUBLESHOOTING.md`
3. Review error messages carefully
4. Verify all dependencies installed
5. Ensure correct directory structure
