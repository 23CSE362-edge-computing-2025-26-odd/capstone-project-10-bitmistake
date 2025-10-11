# Quick Reference Card

## 🚀 One-Line Commands

```bash
# Interactive launcher
python run_pipeline.py

# Quick demo (5 min)
python pipeline_demo.py

# Full evaluation (10-15 min)
python run_complete_pipeline.py

# Research study (15-20 min)
cd experiments && python predictive_vs_reactive_comparison.py

# Validation
python validate_improvements.py
python validate_predictive_placement.py
```

## 📁 Key Files

| File | Purpose | Time |
|------|---------|------|
| `run_pipeline.py` | Interactive menu | - |
| `pipeline_demo.py` | Quick demo | 5 min |
| `run_complete_pipeline.py` | Full evaluation | 10-15 min |
| `experiments/predictive_vs_reactive_comparison.py` | Research study | 15-20 min |

## 🎯 Algorithms

| Algorithm | Type | Use When |
|-----------|------|----------|
| OLB (Reactive) | Baseline | Random workloads |
| Predictive Latency | Predictive | Trending workloads |
| Forecast-Based | Predictive | Known patterns |

## 📊 Expected Results

| Scenario | Improvement |
|----------|-------------|
| Periodic | 15-25% |
| Increasing | 20-30% |
| Bursty | -5-5% |
| ICU | 10-15% |
| Ambulatory | 25-35% |

## 📂 Output Locations

```
data/          → JSON results
reports/       → Text reports
plots/         → PNG visualizations
results/       → YAFS outputs
```

## 🔧 Quick Customization

### Change Environment Size
```python
environment = DigitalTwinEnvironment(5000, 3000)  # width, height
environment.initialize_sensors(30, seed=42)       # num_sensors
environment.initialize_fog_nodes(10, seed=42)     # num_fog_nodes
```

### Change Prediction Horizon
```python
placement = PredictiveLatencyPlacement(
    "Predictive",
    placement_json,
    environment,
    prediction_horizon=20  # default: 10
)
```

### Change Workload Pattern
```python
workload_gen = PatternBasedWorkloadGenerator("periodic")
# Options: steady, periodic, bursty, increasing, decreasing, random
```

## 📚 Documentation Quick Links

| Document | Purpose |
|----------|---------|
| `INDEX.md` | Complete index |
| `README_COMPLETE_SYSTEM.md` | System overview |
| `PIPELINE_GUIDE.md` | Pipeline details |
| `PREDICTIVE_PLACEMENT_GUIDE.md` | Technical guide |
| `SYSTEM_ARCHITECTURE.md` | Architecture diagrams |

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Import error | `pip install yafs numpy matplotlib pandas tensorflow` |
| Out of memory | Reduce sensor count or sim time |
| Slow execution | Run quick demo instead |
| Validation fails | Check dependencies |

## 📈 Metrics

| Metric | Unit | Description |
|--------|------|-------------|
| Overall Latency | ms | Total latency |
| Energy Consumption | W | Total energy |
| Load Balance Score | 0-1 | Balance quality |
| Network Usage | MB/s | Data transfer |

## 🔬 Validation Checklist

- [ ] Run `python validate_improvements.py`
- [ ] Run `python validate_predictive_placement.py`
- [ ] Both complete without errors
- [ ] Review validation output

## 🎓 Research Workflow

1. Run full evaluation: `python run_complete_pipeline.py`
2. Extract metrics from `data/complete_pipeline_*.json`
3. Use plots from `plots/` directory
4. Reference findings from `reports/complete_pipeline_*.txt`
5. Cite improvements and trade-offs

## 💡 Pro Tips

- Use `run_pipeline.py` for interactive menu
- Start with quick demo to understand workflow
- Run validation before experiments
- Check `plots/` for visualizations
- Read reports in `reports/` for analysis

## 🔑 Key Concepts

**Reactive**: Uses current state
**Predictive**: Forecasts future state
**Forecast-Based**: Uses pattern knowledge

**Prediction Horizon**: Steps to forecast ahead
**History Window**: Past observations to use
**Load Multiplier**: Workload scaling factor

## 📞 Quick Help

```bash
# View documentation
ls *.md

# Check output
ls data/
ls reports/
ls plots/

# Run validation
python validate_improvements.py

# Interactive menu
python run_pipeline.py
```

## ⚡ Performance

| Pipeline | Time | Algorithms | Scenarios |
|----------|------|------------|-----------|
| Quick Demo | 5 min | 3 | 1 |
| Complete | 10-15 min | 4 | 4 |
| Research | 15-20 min | 3 | 7 |

## 🎯 Success Criteria

✅ Validation passes
✅ Quick demo completes
✅ Plots generated
✅ Reports created
✅ Predictive shows improvement on periodic patterns

---

**Start Here**: `python run_pipeline.py`
**Documentation**: `INDEX.md`
**Help**: Read `PIPELINE_GUIDE.md`
