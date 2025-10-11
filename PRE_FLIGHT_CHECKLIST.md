# Pre-Flight Checklist

Run through this checklist before executing the pipeline.

## ✅ Environment Setup

- [ ] Conda environment activated
  ```bash
  conda activate tensorflow_gpu_env
  ```

- [ ] Python version 3.7+
  ```bash
  python --version
  ```

- [ ] In correct directory
  ```bash
  pwd  # Should show project root
  ls src/  # Should list source files
  ```

## ✅ Dependencies

- [ ] YAFS installed
  ```bash
  python -c "import yafs; print('✓ YAFS OK')"
  ```

- [ ] NumPy installed
  ```bash
  python -c "import numpy; print('✓ NumPy OK')"
  ```

- [ ] Matplotlib installed
  ```bash
  python -c "import matplotlib; print('✓ Matplotlib OK')"
  ```

- [ ] Pandas installed
  ```bash
  python -c "import pandas; print('✓ Pandas OK')"
  ```

**Install all at once**:
```bash
pip install yafs numpy matplotlib pandas
```

## ✅ File Structure

- [ ] Source files exist
  ```bash
  ls src/__init__.py
  ls src/olb_algorithm.py
  ls src/predictive_placement.py
  ls src/workload_models.py
  ```

- [ ] Pipeline files exist
  ```bash
  ls run_pipeline_safe.py
  ls run_complete_pipeline.py
  ls pipeline_demo.py
  ```

- [ ] Output directories created
  ```bash
  mkdir -p results data reports plots config logs
  ```

## ✅ Imports

- [ ] Core imports work
  ```bash
  python -c "from src import DigitalTwinEnvironment; print('✓ Environment OK')"
  ```

- [ ] Algorithm imports work
  ```bash
  python -c "from src import OLBPlacement; print('✓ OLB OK')"
  python -c "from src import PredictiveLatencyPlacement; print('✓ Predictive OK')"
  ```

- [ ] Workload imports work
  ```bash
  python -c "from src import PatternBasedWorkloadGenerator; print('✓ Workload OK')"
  ```

## ✅ Quick Test

- [ ] Can create environment
  ```bash
  python -c "
  from src import DigitalTwinEnvironment
  env = DigitalTwinEnvironment(1000, 1000)
  env.initialize_sensors(5, seed=42)
  print(f'✓ Created {len(env.sensors)} sensors')
  "
  ```

- [ ] Can create placement
  ```bash
  python -c "
  from src import DigitalTwinEnvironment, OLBPlacement, create_placement_json
  env = DigitalTwinEnvironment(1000, 1000)
  env.initialize_sensors(5, seed=42)
  env.initialize_fog_nodes(3, seed=42)
  placement_json = create_placement_json('config')
  placement = OLBPlacement('Test', placement_json, env)
  print('✓ Placement created')
  "
  ```

## ✅ System Resources

- [ ] Sufficient disk space (at least 100MB free)
  ```bash
  df -h .  # Linux/Mac
  # or check in File Explorer (Windows)
  ```

- [ ] Sufficient memory (at least 2GB free)
  ```bash
  free -h  # Linux
  # or check Task Manager (Windows)
  ```

- [ ] No other heavy processes running
  - Close unnecessary applications
  - Check CPU usage is low

## ✅ Ready to Run

If all checks pass, you're ready!

### Option 1: Safe Runner (Recommended)
```bash
python run_pipeline_safe.py
```

### Option 2: Quick Demo
```bash
python pipeline_demo.py
```

### Option 3: Direct Execution
```bash
python run_complete_pipeline.py
```

## ❌ If Any Check Fails

### Dependencies Missing
```bash
pip install yafs numpy matplotlib pandas
```

### Import Errors
```bash
# Check you're in project root
cd /path/to/project

# Verify src/ exists
ls src/

# Try imports again
python -c "from src import DigitalTwinEnvironment; print('OK')"
```

### File Not Found
```bash
# Check files exist
ls run_pipeline_safe.py
ls src/__init__.py

# If missing, you may need to re-download
```

### System Resources Low
- Close other applications
- Free up disk space
- Restart computer if needed

## 🔧 Automated Check

Run this to check everything automatically:
```bash
python run_pipeline_safe.py
```

This script will:
1. ✅ Check all dependencies
2. ✅ Verify file structure
3. ✅ Test imports
4. ✅ Run quick test
5. ✅ Then ask if you want to run pipeline

## 📋 Manual Verification

If automated check doesn't work, run these manually:

```bash
# 1. Environment
conda activate tensorflow_gpu_env
python --version

# 2. Dependencies
python -c "import yafs, numpy, matplotlib, pandas; print('All OK')"

# 3. Directory
pwd
ls src/

# 4. Imports
python -c "from src import DigitalTwinEnvironment, OLBPlacement; print('OK')"

# 5. Quick test
python -c "
from src import DigitalTwinEnvironment
env = DigitalTwinEnvironment(1000, 1000)
env.initialize_sensors(5, seed=42)
print('Test passed')
"
```

## ✅ Final Check

Before running, ensure:
- [x] All checkboxes above are checked
- [x] No error messages from tests
- [x] You have 10-15 minutes available
- [x] You're ready to review results

## 🚀 Execute

Once all checks pass:
```bash
python run_pipeline_safe.py
```

Or for quick demo:
```bash
python pipeline_demo.py
```

## 📊 Expected Timeline

- Pre-flight checks: 2-3 minutes
- Pipeline execution: 10-15 minutes
- Results review: 5-10 minutes
- **Total**: 20-30 minutes

## 🎯 Success Criteria

You'll know it worked when:
- ✅ No error messages
- ✅ "PIPELINE COMPLETED" message
- ✅ Files in data/, reports/, plots/
- ✅ Plots show algorithm comparisons
- ✅ Report contains metrics

## 📞 If You Need Help

1. Check `TROUBLESHOOTING.md`
2. Run `python run_pipeline_safe.py` for diagnostics
3. Try `python pipeline_demo.py` as alternative
4. Review error messages carefully

---

**Ready?** Run: `python run_pipeline_safe.py`
