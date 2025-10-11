# 🚀 START HERE

## Quickest Way to Run

### Windows
**Double-click**: `run_pipeline.bat`

### Command Line (All Platforms)
```bash
conda activate tensorflow_gpu_env
python run_pipeline_safe.py
```

That's it! The script will check everything and run the pipeline.

---

## What This Does

Runs a **complete evaluation** of predictive placement algorithms:
- 4 scenarios
- Multiple algorithms
- Generates plots and reports
- Takes 10-15 minutes

---

## Three Options

### 1. Safe Runner (Recommended)
```bash
python run_pipeline_safe.py
```
- ✅ Checks everything first
- ✅ Tells you if something is wrong
- ✅ Then runs complete pipeline
- ⏱️ 10-15 minutes

### 2. Quick Demo
```bash
python pipeline_demo.py
```
- ✅ Fast demonstration
- ✅ 3 algorithms
- ✅ Generates plots
- ⏱️ 5 minutes

### 3. Direct Execution
```bash
python run_complete_pipeline.py
```
- ✅ Full evaluation
- ✅ 4 scenarios
- ✅ Comprehensive results
- ⏱️ 10-15 minutes

---

## Prerequisites

### 1. Activate Environment
```bash
conda activate tensorflow_gpu_env
```

### 2. Install Dependencies (if needed)
```bash
pip install yafs numpy matplotlib pandas
```

### 3. Verify
```bash
python -c "import yafs; print('Ready to go!')"
```

---

## Expected Output

### Console
```
================================================================================
  COMPLETE PREDICTIVE PLACEMENT PIPELINE
================================================================================

Running Scenario 1: Baseline...
  Running Reactive_OLB... ✓ (12.34s)
  Running Predictive_Latency... ✓ (15.67s)
  ...

PIPELINE COMPLETED
Results saved to data/ and reports/
```

### Files Created
```
data/complete_pipeline_*.json       ← All metrics
reports/complete_pipeline_*.txt     ← Analysis report
plots/scenario*_*.png               ← Visualizations
```

---

## If Something Goes Wrong

### Quick Fix
```bash
python run_pipeline_safe.py
```
This will diagnose and tell you what's wrong.

### Common Issues

**Can't find yafs?**
```bash
pip install yafs
```

**Wrong directory?**
```bash
cd /path/to/your/project
```

**Too slow?**
```bash
python pipeline_demo.py  # Faster version
```

---

## After It Runs

### View Results
```bash
# Read report
cat reports/complete_pipeline_*.txt

# View plots
# Open plots/*.png in image viewer
```

### What to Look For
- ✅ Comparison tables
- ✅ Improvement percentages
- ✅ Algorithm performance
- ✅ Visualizations

---

## Documentation

| File | Purpose |
|------|---------|
| `README_EXECUTION.md` | Detailed execution guide |
| `TROUBLESHOOTING.md` | Solutions to problems |
| `QUICK_REFERENCE.md` | Quick commands |
| `EXECUTION_GUIDE.md` | Step-by-step guide |

---

## Need Help?

1. Run: `python run_pipeline_safe.py`
2. Check: `TROUBLESHOOTING.md`
3. Try: `python pipeline_demo.py`

---

## Summary

**Just want it to work?**
```bash
conda activate tensorflow_gpu_env
python run_pipeline_safe.py
```

**In a hurry?**
```bash
conda activate tensorflow_gpu_env
python pipeline_demo.py
```

**Ready for full evaluation?**
```bash
conda activate tensorflow_gpu_env
python run_complete_pipeline.py
```

---

## ✨ That's It!

The system will:
1. Check everything is ready
2. Run the algorithms
3. Generate results
4. Save plots and reports

**Time**: 5-15 minutes depending on option chosen

**Output**: JSON data, text reports, PNG plots

**Next**: Review results in `reports/` and `plots/`

---

**Questions?** Check `README_EXECUTION.md` or `TROUBLESHOOTING.md`
