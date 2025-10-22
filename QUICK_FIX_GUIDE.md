# Quick Fix Guide - Critical Issues

This guide provides immediate fixes for the 8 critical issues that need urgent attention.

---

## Issue #1: Missing CI Models __init__.py

**File:** `CI_Models/Workload/__init__.py`

**Current State:** Empty file

**Fix:**
```python
"""
CI Models Workload Package
LSTM-based workload prediction for edge deployment
"""

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

__version__ = '1.0.0'
```

---

## Issue #2: Inconsistent Path Handling

**Files:** Multiple

**Problem:** Mix of relative and absolute paths

**Fix:** Update all files to use centralized path resolution

### In `main.py`:
```python
# Replace line 214
from src.orchestrator import get_project_root, get_absolute_path

# Use:
results_filename = get_absolute_path("data/olb_simulation_results.json")
```

### In `web_ui/app.py`:
```python
# Add at top of file
from src.orchestrator import get_project_root, get_absolute_path

# Replace line 95
config_dir = get_absolute_path("config")
placement_json = create_placement_json(config_dir)
```

### In `CI_Models/Workload/predict.py`:
```python
# Replace lines 67-70
from pathlib import Path

def load_training_info(self) -> None:
    try:
        # Use absolute path from project root
        base_dir = Path(__file__).parent
        scaler_path = base_dir / 'models' / 'scaler.pkl'
        
        if not scaler_path.exists():
            raise FileNotFoundError(f"Scaler not found: {scaler_path}")
```

---

## Issue #3: YAFS Output Parser Not Integrated

**File:** `src/yafs_output_parser.py`

**Problem:** Parser expects CSV files that YAFS doesn't generate

**Fix Option 1 - Remove Parser (Recommended):**

1. Comment out parser import in `src/metrics.py` line 250:
```python
# Try to enhance metrics with YAFS output data
# try:
#     from .yafs_output_parser import parse_yafs_output
#     yafs_metrics = parse_yafs_output("results", algorithm_name.lower())
#     ...
# except ImportError:
#     print("[INFO] YAFS output parser not available, using calculated metrics")
```

2. Remove `src/yafs_output_parser.py` from `src/__init__.py` exports

**Fix Option 2 - Implement YAFS CSV Output:**

Add to `src/yafs_integration.py`:
```python
def configure_yafs_logging(sim, output_dir="results"):
    """Configure YAFS to output CSV files for parser"""
    # This requires YAFS framework modifications
    # Not recommended unless you control YAFS source
    pass
```

---

## Issue #4: Synthetic Workload Generation

**File:** `src/metrics.py` line 295

**Current Code:**
```python
if not placement.module_assignments or all(len(sensors) == 0 for sensors in placement.module_assignments.values()):
    self.logger.warning("[WARNING] NO ASSIGNMENTS FOUND! Generating synthetic workload...")
    self._generate_synthetic_workload(digital_twin, placement)
```

**Fix:**
```python
if not placement.module_assignments or all(len(sensors) == 0 for sensors in placement.module_assignments.values()):
    error_msg = f"Placement algorithm {algorithm_name} failed to assign any sensors!"
    self.logger.error(f"[ERROR] {error_msg}")
    raise ValueError(error_msg)
```

**Remove the `_generate_synthetic_workload` method entirely (lines 295-310)**

---

## Issue #5: Missing Model Files

**Directory:** `CI_Models/Workload/models/`

**Problem:** Empty directory, no trained models

**Fix Option 1 - Generate Models:**

```bash
# Navigate to CI_Models/Workload
cd CI_Models/Workload

# Ensure data files exist
ls data/  # Should show system-1.csv, system-2.csv, etc.

# Train models
python train_workload_model.py --epochs 50 --batch-size 32

# Convert to TFLite
python train_workload_model.py --convert-only --quantize
```

**Fix Option 2 - Disable Predictive Features:**

In `src/__init__.py`, ensure predictive algorithms are properly disabled:
```python
try:
    from .predictive_placement import PredictiveLatencyPlacement, ForecastBasedPlacement
    PREDICTIVE_AVAILABLE = True
except ImportError as e:
    print(f"[INFO] Predictive algorithms disabled: {e}")
    PREDICTIVE_AVAILABLE = False
    # Stub classes already defined
```

In `main.py`, skip predictive if unavailable:
```python
if WORKLOAD_PREDICTOR_AVAILABLE:
    # Run predictions
    pass
else:
    print("[INFO] Skipping workload predictions - models not available")
```

---

## Issue #6: Duplicate Entry Points

**Files:** `main.py` and potential `main_hospital_workflow.py`

**Fix:** Ensure only `main.py` is used

**Check for duplicate files:**
```bash
# Find all main*.py files
find . -name "main*.py" -type f
```

**If `main_hospital_workflow.py` exists, delete it:**
```bash
rm main_hospital_workflow.py
```

**Update README.md to show correct usage:**
```markdown
## Usage

Run simulations using main.py with subcommands:

```bash
# OLB simulation
python main.py olb

# Hospital comparison
python main.py hospital

# Algorithm comparison
python main.py compare
```
```

---

## Issue #7: Web UI Config Directory Bug

**File:** `web_ui/app.py` line 95

**Current Code:**
```python
placement_json = create_placement_json(config_dir)  # config_dir not defined!
```

**Fix:**
```python
# Add before line 95
config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
os.makedirs(config_dir, exist_ok=True)
placement_json = create_placement_json(config_dir)
```

**Better Fix - Use orchestrator:**
```python
# At top of file
from src.orchestrator import setup_directories, get_absolute_path

# In simulate() function, before line 95
setup_directories(["config", "results"])
config_dir = get_absolute_path("config")
placement_json = create_placement_json(config_dir)
```

---

## Issue #8: MQTT Simulator Not Connected

**File:** `src/mqtt_simulator.py`

**Problem:** MQTT environment created but never connected to YAFS

**Fix Option 1 - Remove MQTT (Recommended):**

1. Remove MQTT imports from `main.py`:
```python
# Remove line 33
# from src.mqtt_simulator import MQTTSimulationEnvironment
```

2. Remove MQTT initialization in `main.py` line 245:
```python
# Remove these lines
# mqtt_env = MQTTSimulationEnvironment()
# mqtt_env.simulation_time = 0
```

3. Remove MQTT connection in `main.py` line 285:
```python
# Remove
# mqtt_env.connect_to_yafs_simulation(sim)
```

**Fix Option 2 - Implement MQTT Integration:**

In `src/mqtt_simulator.py`, add actual YAFS callbacks:
```python
def connect_to_yafs_simulation(self, yafs_sim):
    """Connect MQTT environment to YAFS simulation"""
    self.yafs_sim = yafs_sim
    
    # Register callbacks with YAFS
    # Note: This requires YAFS framework support
    if hasattr(yafs_sim, 'register_message_callback'):
        yafs_sim.register_message_callback(self.on_yafs_message_created)
    
    if hasattr(yafs_sim, 'register_delivery_callback'):
        yafs_sim.register_delivery_callback(self.on_yafs_message_delivered)
    
    print("[INFO] MQTT environment connected to YAFS simulation")
```

---

## Verification Steps

After applying fixes, verify:

### 1. Check Imports
```bash
python -c "from src import *; print('Imports OK')"
python -c "from CI_Models.Workload import *; print('CI Models OK')"
```

### 2. Run Basic Simulation
```bash
python main.py olb
```

### 3. Test Web UI
```bash
cd web_ui
python app.py
# Open http://localhost:5000 and run a simulation
```

### 4. Check File Structure
```bash
# Verify all required files exist
ls CI_Models/Workload/__init__.py
ls config/placement_config.json
ls src/orchestrator.py
```

---

## Common Errors After Fixes

### Error: "No module named 'Workload'"
**Solution:** Ensure `CI_Models/Workload/__init__.py` is not empty

### Error: "FileNotFoundError: scaler.pkl"
**Solution:** Either train models or disable predictive features

### Error: "config_dir not defined"
**Solution:** Apply Issue #7 fix to web_ui/app.py

### Error: "Placement algorithm failed"
**Solution:** Check that Issue #4 fix was applied (no synthetic workload)

---

## Testing After Fixes

Run this test script to verify fixes:

```python
# test_critical_fixes.py
import sys
import os

def test_imports():
    """Test all critical imports"""
    try:
        from src import *
        print("✓ src imports OK")
    except Exception as e:
        print(f"✗ src imports FAILED: {e}")
        return False
    
    try:
        from CI_Models.Workload import WorkloadPredictor
        print("✓ CI Models imports OK")
    except Exception as e:
        print(f"✗ CI Models imports FAILED: {e}")
        return False
    
    return True

def test_paths():
    """Test path resolution"""
    try:
        from src.orchestrator import get_project_root, get_absolute_path
        root = get_project_root()
        config_path = get_absolute_path("config")
        print(f"✓ Path resolution OK: {root}")
        return True
    except Exception as e:
        print(f"✗ Path resolution FAILED: {e}")
        return False

def test_web_ui():
    """Test web UI imports"""
    try:
        sys.path.insert(0, 'web_ui')
        from app import app
        print("✓ Web UI imports OK")
        return True
    except Exception as e:
        print(f"✗ Web UI imports FAILED: {e}")
        return False

if __name__ == "__main__":
    print("Testing Critical Fixes...")
    print("=" * 50)
    
    results = [
        test_imports(),
        test_paths(),
        test_web_ui()
    ]
    
    print("=" * 50)
    if all(results):
        print("✓ All critical fixes verified!")
        sys.exit(0)
    else:
        print("✗ Some fixes failed - review errors above")
        sys.exit(1)
```

Run with:
```bash
python test_critical_fixes.py
```

---

## Next Steps

After fixing these 8 critical issues:

1. Review MAJOR ISSUES in `CODEBASE_ISSUES_ANALYSIS.md`
2. Implement unit tests
3. Add requirements.txt
4. Update documentation
5. Run full test suite

