# Quick Start Guide - Refactored Algorithms

## ✅ What's New

### Removed (Legacy)
- ❌ RandomPlacement
- ❌ DistancePlacement  
- ❌ LoadBalancedPlacement
- ❌ FNPAPlacement (old version)

### Added (Real Implementations)
- ✅ **LBS** - Location-Based Selection (distance optimization)
- ✅ **LAB** - Load-Aware Balancing (load + distance weighted)
- ✅ **MEC** - Multi-Edge Coordination (latency + energy optimization)
- ✅ **FNPA** - Fog Node Proximity Algorithm (resource-aware with cloud fallback)

---

## 🚀 Quick Usage

### Import Algorithms
```python
from src import LBS, LAB, MEC, FNPA, OLBPlacement
```

### Check Model Availability
```python
from src import PREDICTIVE_AVAILABLE, WORKLOAD_PREDICTOR_AVAILABLE

print(f"Predictive algorithms: {PREDICTIVE_AVAILABLE}")
print(f"Workload predictor: {WORKLOAD_PREDICTOR_AVAILABLE}")
```

### Run Simulation
```bash
# Main simulation (LSTM optional)
python main.py

# Hospital comparison
python main_hospital_workflow.py

# Run tests
python test_algorithms.py
```

---

## 🔧 LSTM Model Handling

### ✨ New Feature: Optional LSTM Models

The workflow now **gracefully handles missing LSTM models**:

#### ✅ If Models Available
- Loads pretrained models from `CI_Models/Workload/models/`
- Runs workload predictions
- Adjusts fog node capacities
- Logs: `"✓ LSTM predictions completed for X nodes"`

#### ✅ If Models Unavailable
- Skips LSTM prediction stage
- Uses default fog node capacities
- Continues simulation normally
- Logs: `"SKIPPING CI Model - WorkloadPredictor not available"`

#### ✅ Benefits
- No training during execution
- No crashes if models missing
- Clear status logging
- Simulation always runs

---

## 📊 Algorithm Comparison

| Algorithm | Best For | Load Aware | Energy Aware | Cloud Fallback |
|-----------|----------|------------|--------------|----------------|
| **LBS** | Latency-critical | ❌ | ❌ | ❌ |
| **LAB** | Balanced load | ✅ | ❌ | ❌ |
| **MEC** | Energy efficiency | ✅ | ✅ | ❌ |
| **FNPA** | Resource-limited | ✅ | ❌ | ✅ |
| **OLB** | Overall optimization | ✅ | ✅ | ❌ |

---

## ✅ Validation

All tests passing:
```
✓ Import Test
✓ Environment Creation  
✓ Algorithm Initialization
✓ Hospital Comparison

Total: 4/4 tests passed
```

Run validation: `python test_algorithms.py`

---

## 📁 Key Files

- `src/comparison_algorithms.py` - New algorithm implementations (586 lines)
- `src/__init__.py` - Optional imports and availability flags
- `main.py` - Enhanced with optional LSTM handling
- `test_algorithms.py` - Comprehensive test suite
- `REFACTOR_SUMMARY.md` - Complete documentation

---

## 🎯 Quick Algorithm Selection Guide

### Choose LBS when:
- Latency is critical
- Simple deployment needed
- Network proximity matters most

### Choose LAB when:
- Need balanced resource usage
- Want to prevent overload
- Have varying workload patterns

### Choose MEC when:
- Energy efficiency is priority
- Multi-objective optimization needed
- Both latency and power matter

### Choose FNPA when:
- Resource constraints exist
- Cloud fallback needed
- Bandwidth is limited

### Choose OLB when:
- Need comprehensive optimization
- Have complex latency requirements
- Want mathematical guarantees

---

## 🔍 Troubleshooting

### ImportError: tflite_predictor
**Solution**: This is normal! LSTM models are optional.
```python
# Check availability
from src import WORKLOAD_PREDICTOR_AVAILABLE
print(f"Models available: {WORKLOAD_PREDICTOR_AVAILABLE}")
```

### Algorithm not working
**Check**:
1. Environment initialized? `environment.initialize_sensors()` and `initialize_fog_nodes()`
2. Placement config exists? `placement_config.json`
3. YAFS simulation created? `Sim(topology, ...)`

### Need to add new algorithm
**Steps**:
1. Create class inheriting from `Placement`
2. Implement `initial_allocation(self, sim, app_name)`
3. Add helper methods (`_extract_sensor_id`, `_find_sensor_by_id`)
4. Update `src/__init__.py` to export it
5. Add to algorithm list in `main.py`

---

## 📞 Support

- See `REFACTOR_SUMMARY.md` for detailed documentation
- Run `test_algorithms.py` to validate installation
- Check logs in `logs/` directory for debugging

---

**Status**: ✅ Production Ready  
**Last Updated**: October 22, 2025  
**Tests**: 4/4 Passing

