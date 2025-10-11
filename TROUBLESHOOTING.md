# Troubleshooting Guide

## Quick Diagnosis

Run this command to diagnose issues:
```bash
conda activate tensorflow_gpu_env
python run_pipeline_safe.py
```

This will check everything and tell you exactly what's wrong.

## Common Errors and Solutions

### 1. ModuleNotFoundError: No module named 'yafs'

**Error**:
```
ModuleNotFoundError: No module named 'yafs'
```

**Solution**:
```bash
conda activate tensorflow_gpu_env
pip install yafs
```

**Verify**:
```bash
python -c "import yafs; print('YAFS installed:', yafs.__version__)"
```

---

### 2. ModuleNotFoundError: No module named 'src'

**Error**:
```
ModuleNotFoundError: No module named 'src'
```

**Cause**: Running from wrong directory

**Solution**:
```bash
# Navigate to project root
cd /path/to/your/project

# Verify you're in the right place
ls src/

# Run pipeline
python run_complete_pipeline.py
```

---

### 3. ImportError: cannot import name 'PredictiveLatencyPlacement'

**Error**:
```
ImportError: cannot import name 'PredictiveLatencyPlacement' from 'src'
```

**Cause**: Auto-formatting may have changed imports

**Solution**:
```bash
# Check if file exists
ls src/predictive_placement.py

# Test import
python -c "from src.predictive_placement import PredictiveLatencyPlacement; print('OK')"

# If fails, check src/__init__.py
cat src/__init__.py | grep PredictiveLatencyPlacement
```

**Fix**: Ensure `src/__init__.py` contains:
```python
from .predictive_placement import PredictiveLatencyPlacement, ForecastBasedPlacement
```

---

### 4. ImportError: cannot import name 'WorkloadPredictor'

**Error**:
```
ImportError: cannot import name 'WorkloadPredictor' from 'src.workload_models'
```

**Solution**:
```bash
# Check file
cat src/workload_models.py | grep "class WorkloadPredictor"

# Test import
python -c "from src.workload_models import WorkloadPredictor; print('OK')"
```

**Fix**: Ensure `src/__init__.py` contains:
```python
from .workload_models import (WorkloadPredictor, TimeSeriesWorkloadForecaster,
                              PatternBasedWorkloadGenerator, HealthcareWorkloadForecaster)
```

---

### 5. FileNotFoundError: placement_config.json

**Error**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'config/placement_config.json'
```

**Solution**:
```bash
# Create config directory
mkdir -p config

# Run pipeline again
python run_complete_pipeline.py
```

The pipeline will create the file automatically.

---

### 6. AttributeError: module 'src' has no attribute 'PerformanceMetrics'

**Error**:
```
AttributeError: module 'src' has no attribute 'PerformanceMetrics'
```

**Cause**: Missing metrics.py or incorrect import

**Solution**:
```bash
# Check if metrics.py exists
ls src/metrics.py

# If missing, check what's available
python -c "import src; print(dir(src))"
```

**Workaround**: Comment out PerformanceMetrics usage temporarily:
```python
# metrics = PerformanceMetrics()
# metrics.collect_metrics(environment, placement, algo_name)
```

---

### 7. MemoryError or System Hangs

**Error**:
```
MemoryError: Unable to allocate array
```
or system becomes unresponsive

**Solution**: Reduce problem size

Edit `run_complete_pipeline.py`:
```python
environment_config = {
    "width": 2000,           # Reduce from 3000
    "height": 1500,          # Reduce from 2000
    "num_sensors": 10,       # Reduce from 15
    "num_fog_nodes": 4,      # Reduce from 6
    "seed": 42,
    "sim_time": 300          # Reduce from 500
}
```

---

### 8. YAFS Simulation Hangs

**Symptom**: Pipeline runs but gets stuck during simulation

**Solution 1**: Reduce simulation time
```python
s.run(until=300)  # Instead of 500
```

**Solution 2**: Add timeout
```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Simulation timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)  # 60 second timeout

try:
    s.run(until=500)
finally:
    signal.alarm(0)
```

---

### 9. Matplotlib Backend Error

**Error**:
```
ImportError: Cannot load backend 'TkAgg'
```

**Solution**:
```bash
# Install tkinter
conda install tk

# Or use different backend
export MPLBACKEND=Agg
python run_complete_pipeline.py
```

**Or** add to script:
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
```

---

### 10. NumPy Version Conflict

**Error**:
```
ValueError: numpy.ndarray size changed
```

**Solution**:
```bash
conda activate tensorflow_gpu_env
pip install --upgrade numpy
pip install --force-reinstall numpy
```

---

## Validation Failures

### validate_improvements.py fails

**Check each test**:
```bash
python -c "
from src.olb_algorithm import OLBLatencyCalculator
calc = OLBLatencyCalculator()
capacity = calc.calculate_device_capacity(100, 10)
print(f'Shannon capacity test: {capacity:.2f}')
"
```

### validate_predictive_placement.py fails

**Check workload models**:
```bash
python -c "
from src.workload_models import WorkloadPredictor
predictor = WorkloadPredictor()
print('WorkloadPredictor OK')
"
```

---

## Performance Issues

### Pipeline is too slow

**Solutions**:
1. Reduce sensor count
2. Reduce simulation time
3. Skip some scenarios
4. Run quick demo instead

```bash
python pipeline_demo.py  # Much faster
```

### High memory usage

**Solutions**:
1. Close other applications
2. Reduce problem size
3. Run scenarios separately

---

## Import Issues Checklist

Run these checks in order:

```bash
# 1. Check Python version
python --version

# 2. Check environment
conda env list
which python

# 3. Check dependencies
pip list | grep yafs
pip list | grep numpy
pip list | grep matplotlib

# 4. Check directory
pwd
ls src/

# 5. Check imports
python -c "import sys; print(sys.path)"
python -c "from src import DigitalTwinEnvironment; print('OK')"

# 6. Check specific modules
python -c "from src import OLBPlacement; print('OK')"
python -c "from src import PredictiveLatencyPlacement; print('OK')"
python -c "from src import WorkloadPredictor; print('OK')"
```

---

## File Structure Issues

### Missing files

**Check required files**:
```bash
ls src/__init__.py
ls src/olb_algorithm.py
ls src/predictive_placement.py
ls src/workload_models.py
ls src/devices.py
ls src/environment.py
ls src/yafs_integration.py
ls src/utils.py
```

### Missing directories

**Create all directories**:
```bash
mkdir -p src experiments config results data reports plots logs
```

---

## YAFS-Specific Issues

### YAFS not found

```bash
pip install yafs
```

### YAFS version issues

```bash
pip install --upgrade yafs
```

### YAFS import error

```bash
python -c "import yafs; print(yafs.__file__)"
```

---

## Quick Fixes

### Reset everything

```bash
# Clean output
rm -rf data/*.json reports/*.txt plots/*.png results/*

# Reinstall dependencies
pip install --force-reinstall yafs numpy matplotlib pandas

# Run safe pipeline
python run_pipeline_safe.py
```

### Run minimal test

```bash
python -c "
from src import DigitalTwinEnvironment, OLBPlacement
from src import create_smart_healthcare_application, create_yafs_topology, create_placement_json

env = DigitalTwinEnvironment(1000, 1000)
env.initialize_sensors(5, seed=42)
env.initialize_fog_nodes(3, seed=42)

app = create_smart_healthcare_application(env)
topology = create_yafs_topology(env)
placement_json = create_placement_json('config')

placement = OLBPlacement('Test', placement_json, env)

print('Minimal test passed!')
"
```

---

## Getting Help

### 1. Run diagnostics
```bash
python run_pipeline_safe.py
```

### 2. Check logs
```bash
cat logs/olb_simulation.log
```

### 3. Run validation
```bash
python validate_improvements.py
python validate_predictive_placement.py
```

### 4. Try quick demo
```bash
python pipeline_demo.py
```

### 5. Check documentation
- `EXECUTION_GUIDE.md` - Step-by-step execution
- `PIPELINE_GUIDE.md` - Pipeline details
- `INDEX.md` - Complete navigation

---

## Emergency Procedures

### Pipeline won't start

```bash
# 1. Check environment
conda activate tensorflow_gpu_env

# 2. Check dependencies
pip install yafs numpy matplotlib pandas

# 3. Check directory
cd /path/to/project
ls src/

# 4. Run safe pipeline
python run_pipeline_safe.py
```

### Pipeline crashes mid-execution

```bash
# 1. Check partial results
ls data/
ls reports/
ls plots/

# 2. Check error message
# Look at last lines of output

# 3. Reduce problem size
# Edit run_complete_pipeline.py
# Reduce num_sensors, sim_time

# 4. Run quick demo instead
python pipeline_demo.py
```

### Can't fix the issue

```bash
# Run quick demo as alternative
python pipeline_demo.py

# Or run single scenario
python -c "
from run_complete_pipeline import CompletePipeline
pipeline = CompletePipeline()
pipeline.scenario1_baseline_comparison()
"
```

---

## Contact Support

If none of these solutions work:

1. Note the exact error message
2. Note your Python version: `python --version`
3. Note your OS: `uname -a` (Linux/Mac) or `ver` (Windows)
4. List installed packages: `pip list`
5. Provide the output of: `python run_pipeline_safe.py`

Include all this information when seeking help.
