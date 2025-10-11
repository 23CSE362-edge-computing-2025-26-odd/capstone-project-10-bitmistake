# How to Run the Complete Pipeline

## 🚀 Quick Start (Recommended)

### Windows Users

**Double-click** `run_pipeline.bat` or run in Command Prompt:
```cmd
run_pipeline.bat
```

This will:
1. Activate your conda environment
2. Show you a menu
3. Let you choose what to run

### All Users (Command Line)

```bash
# 1. Activate environment
conda activate tensorflow_gpu_env

# 2. Run safe pipeline (checks everything first)
python run_pipeline_safe.py
```

## 📋 Step-by-Step Instructions

### Step 1: Activate Environment
```bash
conda activate tensorflow_gpu_env
```

**Verify**:
```bash
python --version
# Should show Python 3.7+
```

### Step 2: Install Dependencies (if needed)
```bash
pip install yafs numpy matplotlib pandas
```

**Verify**:
```bash
python -c "import yafs, numpy, matplotlib, pandas; print('All dependencies OK')"
```

### Step 3: Choose Execution Method

#### Option A: Safe Runner (Recommended for first time)
```bash
python run_pipeline_safe.py
```

**What it does**:
- ✅ Checks all dependencies
- ✅ Verifies files exist
- ✅ Tests imports
- ✅ Runs quick test
- ✅ Then runs complete pipeline

**Time**: 10-15 minutes

#### Option B: Direct Execution (if you're confident)
```bash
python run_complete_pipeline.py
```

**Time**: 10-15 minutes

#### Option C: Quick Demo (fastest)
```bash
python pipeline_demo.py
```

**Time**: 5 minutes

## 📊 What to Expect

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
  Running Distance_Placement... ✓ (11.45s)
     Latency: 0.1567 ms
  Running Predictive_Latency... ✓ (15.67s)
     Latency: 0.1123 ms

[... continues for all scenarios ...]

================================================================================
PIPELINE COMPLETED
================================================================================

Total execution time: 645.23 seconds (10.8 minutes)

Results saved:
  - Data: data/complete_pipeline_20241011_143022.json
  - Report: reports/complete_pipeline_20241011_143022.txt
  - Plots: plots/scenario*_20241011_143022.png

Scenarios completed: 4
Total algorithm runs: 15
```

### Output Files

After completion, you'll have:

```
data/
└── complete_pipeline_YYYYMMDD_HHMMSS.json

reports/
└── complete_pipeline_YYYYMMDD_HHMMSS.txt

plots/
├── scenario1_reactive_olb_YYYYMMDD_HHMMSS.png
├── scenario1_random_placement_YYYYMMDD_HHMMSS.png
├── scenario1_distance_placement_YYYYMMDD_HHMMSS.png
├── scenario1_predictive_latency_YYYYMMDD_HHMMSS.png
└── scenario1_comparison_YYYYMMDD_HHMMSS.png
```

## ⏱️ Execution Time

| Scenario | Time |
|----------|------|
| Scenario 1: Baseline | 2-3 min |
| Scenario 2: Patterns | 3-5 min |
| Scenario 3: Scalability | 2-3 min |
| Scenario 4: Healthcare | 2-3 min |
| **Total** | **10-15 min** |

## ✅ Success Indicators

You'll know it worked if you see:

1. ✅ All scenarios complete without errors
2. ✅ "PIPELINE COMPLETED" message
3. ✅ Files created in `data/`, `reports/`, `plots/`
4. ✅ No error messages in console
5. ✅ Latency values printed for each algorithm

## ❌ If Something Goes Wrong

### Quick Diagnosis
```bash
python run_pipeline_safe.py
```

This will tell you exactly what's wrong.

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'yafs'`
```bash
pip install yafs
```

**Issue**: `ModuleNotFoundError: No module named 'src'`
```bash
# Make sure you're in project root
cd /path/to/your/project
python run_complete_pipeline.py
```

**Issue**: Pipeline hangs or is too slow
```bash
# Run quick demo instead
python pipeline_demo.py
```

**Issue**: Out of memory
Edit `run_complete_pipeline.py` and reduce:
- `num_sensors` from 15 to 10
- `sim_time` from 500 to 300

### Full Troubleshooting
See `TROUBLESHOOTING.md` for complete solutions.

## 📖 After Execution

### View Results

**Text Report**:
```bash
# Windows
type reports\complete_pipeline_*.txt

# Linux/Mac
cat reports/complete_pipeline_*.txt
```

**JSON Data**:
```bash
python -c "import json; print(json.dumps(json.load(open('data/complete_pipeline_*.json')), indent=2))"
```

**Plots**:
Open PNG files in `plots/` directory with any image viewer.

### Analyze Results

1. **Open report** in text editor
2. **Review comparison tables** - see which algorithm performed best
3. **Check improvement percentages** - see predictive vs reactive gains
4. **Examine plots** - visual comparison of algorithms

## 🔄 Running Again

### Clean Previous Results
```bash
# Windows
del /Q data\*.json reports\*.txt plots\*.png

# Linux/Mac
rm -f data/*.json reports/*.txt plots/*.png
```

### Run Again
```bash
python run_complete_pipeline.py
```

## 🎯 Alternative Workflows

### Just Want to See It Work?
```bash
python pipeline_demo.py
```
5 minutes, generates plots and report.

### Want Detailed Research Results?
```bash
cd experiments
python predictive_vs_reactive_comparison.py
```
15-20 minutes, comprehensive analysis.

### Want to Validate Everything?
```bash
python validate_improvements.py
python validate_predictive_placement.py
```
2 minutes, checks all components.

## 📚 Documentation

- `EXECUTION_GUIDE.md` - Detailed execution guide
- `TROUBLESHOOTING.md` - Solutions to common issues
- `PIPELINE_GUIDE.md` - Pipeline documentation
- `QUICK_REFERENCE.md` - Quick command reference

## 💡 Pro Tips

1. **First time?** Use `python run_pipeline_safe.py`
2. **In a hurry?** Use `python pipeline_demo.py`
3. **Having issues?** Check `TROUBLESHOOTING.md`
4. **Want to customize?** Edit environment config in pipeline file
5. **Need help?** Run `python run_pipeline_safe.py` for diagnostics

## 🆘 Getting Help

If you're stuck:

1. Run `python run_pipeline_safe.py` - it will diagnose issues
2. Check `TROUBLESHOOTING.md` - solutions to common problems
3. Run validation: `python validate_improvements.py`
4. Try quick demo: `python pipeline_demo.py`

## ✨ Summary

**Easiest way to run**:
```bash
conda activate tensorflow_gpu_env
python run_pipeline_safe.py
```

**Fastest way to see results**:
```bash
conda activate tensorflow_gpu_env
python pipeline_demo.py
```

**Most comprehensive**:
```bash
conda activate tensorflow_gpu_env
python run_complete_pipeline.py
```

Choose based on your needs and available time!
