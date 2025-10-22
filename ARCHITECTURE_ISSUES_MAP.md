# 🏗️ ARCHITECTURE & ISSUES MAP
## Visual Guide to Codebase Structure and Problems

---

## 📐 SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   main.py    │  │  web_ui/     │  │   CLI        │         │
│  │  (Unified)   │  │  app.py      │  │  Scripts     │         │
│  │              │  │              │  │              │         │
│  │ ✅ Working   │  │ ⚠️ Needs     │  │ ✅ Working   │         │
│  │              │  │   Validation │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │  Orchestrator    │  │  Algorithm       │                    │
│  │                  │  │  Registry        │                    │
│  │ ✅ Implemented   │  │                  │                    │
│  │ ⚠️ Not Used      │  │ ✅ Implemented   │                    │
│  │   Everywhere     │  │ ⚠️ Not Used      │                    │
│  └──────────────────┘  └──────────────────┘                    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Hospital Comparison Runner                      │  │
│  │                                                            │  │
│  │  ✅ Real YAFS Simulations                                 │  │
│  │  🔴 Missing Metrics (min/max/p99)                         │  │
│  │  🔴 No Error Handling                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DOMAIN LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Digital Twin Environment                               │    │
│  │                                                          │    │
│  │  ✅ Sensor/edge Node Management                          │    │
│  │  ✅ Spatial Coordinates                                 │    │
│  │  🔴 Hospital Scenario Conversion BROKEN                 │    │
│  │     (expects coordinates that don't exist)              │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ OLB          │  │ Predictive   │  │ Comparison   │         │
│  │ Algorithm    │  │ Placement    │  │ Algorithms   │         │
│  │              │  │              │  │              │         │
│  │ ✅ Working   │  │ ⚠️ Fragile   │  │ ✅ Working   │         │
│  │ ⚠️ Duplicate │  │   Imports    │  │ ⚠️ Wrong     │         │
│  │   Distance   │  │              │  │   Names      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Performance Metrics                                    │    │
│  │                                                          │    │
│  │  ✅ Latency, Energy, Load Balance                       │    │
│  │  🔴 Missing: min/max/p99 latency                        │    │
│  │  🔴 Missing: CPU/memory utilization                     │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Hospital Scenarios                                     │    │
│  │                                                          │    │
│  │  ✅ 3 Scenarios Defined (ICU, Wards, Remote)           │    │
│  │  🔴 SensorConfig MISSING coordinates field              │    │
│  │  ⚠️ Hardcoded sensor counts                             │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  MQTT Simulator                                         │    │
│  │                                                          │    │
│  │  ✅ Broker Implementation                               │    │
│  │  ✅ Pub/Sub Pattern                                     │    │
│  │  🔴 COMPLETELY DISCONNECTED from YAFS                   │    │
│  │  🔴 publish_sensor_reading() NEVER CALLED               │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ YAFS         │  │ TensorFlow/  │  │ NetworkX     │         │
│  │ Framework    │  │ TFLite       │  │              │         │
│  │              │  │              │  │              │         │
│  │ ✅ Working   │  │ ⚠️ Optional  │  │ ✅ Working   │         │
│  │ ⚠️ Output    │  │   Fragile    │  │              │         │
│  │   Ignored    │  │   Imports    │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔴 CRITICAL ISSUE LOCATIONS

```
main.py
├── Line 40-50: 🔴 Workload predictor cache never cleared (memory leak)
├── Line 120-145: 🟠 Unclear capacity adjustment (magic numbers)
└── Line 295-310: 🔴 MQTT initialized but never integrated

src/environment.py
├── Line 200-250: 🔴 from_scenario() expects coordinates that don't exist
└── Line 280-320: 🟠 Magic numbers in edge node placement

src/hospital_scenarios_extended.py
├── Line 15-25: 🔴 SensorConfig MISSING coordinates field
└── Line 50-150: ⚠️ Hardcoded sensor counts

src/metrics.py
├── Line 140-160: 🔴 get_summary_dict() missing latency_min/max/p99
└── Line 180-200: 🔴 Missing CPU/memory utilization calculations

src/hospital_comparison.py
├── Line 150-180: 🔴 No error handling in simulation loop
├── Line 200-220: 🔴 Expects metrics that don't exist
└── Line 250-280: ⚠️ Metrics from formulas, not YAFS output

src/mqtt_simulator.py
├── Line 1-200: 🔴 Entire file disconnected from YAFS
└── Line 150-170: 🔴 publish_sensor_reading() never called

src/predictive_placement.py
├── Line 7-10: 🔴 Fragile sys.path manipulation
└── Line 50-80: ⚠️ Fallback too silent

web_ui/app.py
├── Line 14-26: 🔴 Unconditional predictive import
├── Line 40-60: 🔴 No input validation
└── Line 200-400: ⚠️ Long functions, no error handling

src/olb_algorithm.py
└── Line 20-30: 🟠 Duplicate distance calculation

src/comparison_algorithms.py
└── Line 1-450: 🟠 Inconsistent algorithm naming
```

---

## 🔌 DATA FLOW & INTEGRATION GAPS

### Current Flow (What Works)

```
User Input
    │
    ▼
main.py / web_ui
    │
    ├─► Create Environment ✅
    │       │
    │       ├─► Initialize Sensors ✅
    │       └─► Initialize edge Nodes ✅
    │
    ├─► Create YAFS Application ✅
    │       │
    │       └─► Define Modules & Messages ✅
    │
    ├─► Create Topology ✅
    │       │
    │       └─► Network Graph ✅
    │
    ├─► Select Algorithm ✅
    │       │
    │       ├─► OLB ✅
    │       ├─► Predictive ⚠️
    │       └─► Comparison (LBS/LAB/MEC/FNPA) ✅
    │
    ├─► Run YAFS Simulation ✅
    │       │
    │       ├─► Deploy Modules ✅
    │       ├─► Route Messages ✅
    │       └─► Generate CSV Files ✅ (but ignored!)
    │
    └─► Collect Metrics ⚠️
            │
            ├─► Calculate Latency ✅
            ├─► Calculate Energy ✅
            ├─► Calculate Load Balance ✅
            └─► Missing: min/max/p99, CPU/mem 🔴
```

### Broken Flow (What Doesn't Work)

```
Hospital Scenarios 🔴
    │
    ├─► SensorConfig (NO coordinates) 🔴
    │       │
    │       └─► from_scenario() expects coordinates 🔴
    │               │
    │               └─► CRASH: AttributeError 🔴

MQTT Simulator 🔴
    │
    ├─► Broker Created ✅
    ├─► Topics Defined ✅
    └─► NEVER CONNECTED TO YAFS 🔴
            │
            ├─► No sensor readings published 🔴
            ├─► No real-time messages 🔴
            └─► Only final results (after sim) 🔴

YAFS Output Files 🟠
    │
    ├─► CSV Files Generated ✅
    │       │
    │       ├─► Message delays ✅
    │       ├─► Queue lengths ✅
    │       └─► Resource usage ✅
    │
    └─► NEVER READ BACK 🟠
            │
            └─► Metrics from formulas instead 🟠
```

---

## 🎯 ISSUE SEVERITY MAP

### By Module

```
┌─────────────────────────────────────────────────────────────┐
│ Module                    │ 🔴 │ 🟠 │ 🟢 │ Total │ Status │
├─────────────────────────────────────────────────────────────┤
│ hospital_scenarios        │ 2  │ 1  │ 0  │  3    │ 🔴     │
│ mqtt_simulator            │ 2  │ 0  │ 0  │  2    │ 🔴     │
│ metrics                   │ 2  │ 0  │ 1  │  3    │ 🔴     │
│ environment               │ 1  │ 1  │ 1  │  3    │ 🔴     │
│ web_ui/app                │ 1  │ 2  │ 2  │  5    │ 🔴     │
│ main                      │ 1  │ 1  │ 1  │  3    │ 🔴     │
│ hospital_comparison       │ 1  │ 1  │ 0  │  2    │ 🔴     │
│ predictive_placement      │ 1  │ 1  │ 0  │  2    │ 🔴     │
│ comparison_algorithms     │ 0  │ 2  │ 1  │  3    │ 🟠     │
│ olb_algorithm             │ 0  │ 1  │ 1  │  2    │ 🟠     │
│ visualization             │ 0  │ 1  │ 2  │  3    │ 🟠     │
│ orchestrator              │ 0  │ 1  │ 0  │  1    │ 🟠     │
│ algorithm_registry        │ 0  │ 1  │ 0  │  1    │ 🟠     │
│ yafs_integration          │ 0  │ 0  │ 0  │  0    │ ✅     │
│ devices                   │ 0  │ 0  │ 0  │  0    │ ✅     │
│ common_utils              │ 0  │ 0  │ 0  │  0    │ ✅     │
│ utils                     │ 0  │ 0  │ 1  │  1    │ ✅     │
├─────────────────────────────────────────────────────────────┤
│ TOTAL                     │ 8  │ 15 │ 12 │ 35    │ ⚠️     │
└─────────────────────────────────────────────────────────────┘
```

### By Category

```
┌──────────────────────────────────────────────────────────┐
│ Category              │ Count │ % of Total │ Priority  │
├──────────────────────────────────────────────────────────┤
│ Integration Gaps      │   5   │    14%     │ 🔴 HIGH   │
│ Missing Features      │   6   │    17%     │ 🔴 HIGH   │
│ Data Flow Issues      │   4   │    11%     │ 🔴 HIGH   │
│ Code Quality          │   8   │    23%     │ 🟠 MED    │
│ Architecture          │   5   │    14%     │ 🟠 MED    │
│ Error Handling        │   3   │     9%     │ 🟠 MED    │
│ Documentation         │   2   │     6%     │ 🟢 LOW    │
│ Style/Cleanup         │   2   │     6%     │ 🟢 LOW    │
└──────────────────────────────────────────────────────────┘
```

---

## 🔄 REDUNDANCY MAP

### Duplicate Logic Instances

```
1. Sensor Lookup (RESOLVED ✅)
   ├─ OLBPlacement → Uses SensorLookupIndex ✅
   ├─ PredictiveLatencyPlacement → Uses SensorLookupIndex ✅
   └─ Comparison Algorithms → Uses SensorLookupIndex ✅

2. Distance Calculation (PARTIAL ⚠️)
   ├─ OLBLatencyCalculator.calculate_distance() 🔴
   ├─ common_utils.calculate_euclidean_distance() ✅
   └─ Comparison Algorithms → Use common_utils ✅

3. Directory Creation (PARTIAL ⚠️)
   ├─ orchestrator.setup_directories() ✅
   ├─ main.py → Uses setup_directories() ✅
   ├─ web_ui/app.py → os.makedirs() directly 🔴
   └─ hospital_comparison.py → os.makedirs() directly 🔴

4. Config Loading (RESOLVED ✅)
   ├─ orchestrator.load_config() ✅
   └─ utils.SimulationConfig.load_config() ✅

5. Placement JSON Creation (RESOLVED ✅)
   ├─ utils.create_placement_json() ✅
   └─ Used consistently everywhere ✅

6. YAFS Simulation Setup (DUPLICATED 🔴)
   ├─ main.py lines 150-200
   ├─ web_ui/app.py lines 50-100
   ├─ hospital_comparison.py lines 200-250
   └─ Pattern: Create env → app → topology → sim
       (Could be extracted to orchestrator)

7. Metrics Collection (CONSISTENT ✅)
   └─ PerformanceMetrics used everywhere ✅
```

---

## 🎨 LEGEND

### Status Indicators
- ✅ **Working** - Functional, no major issues
- ⚠️ **Partial** - Works but has issues
- 🔴 **Broken** - Critical issues, may crash
- 🟠 **Needs Work** - Major issues, needs attention
- 🟢 **Minor** - Small issues, low priority

### Issue Severity
- 🔴 **Critical** - Breaks functionality, fix immediately
- 🟠 **Major** - Significant issues, fix soon
- 🟢 **Minor** - Small issues, cleanup

### Integration Status
- ✅ **Connected** - Properly integrated
- ⚠️ **Partial** - Partially integrated
- 🔴 **Disconnected** - Not integrated
- ❌ **Missing** - Component missing

---

## 📍 QUICK NAVIGATION

**Critical Issues:** See lines marked with 🔴  
**Integration Gaps:** See "Data Flow & Integration Gaps" section  
**Redundancy:** See "Redundancy Map" section  
**Module Status:** See "Issue Severity Map" table  

**Full Details:** See `CODEBASE_DIAGNOSTIC_REPORT.md`  
**Quick Summary:** See `DIAGNOSTIC_SUMMARY.md`

---

**Generated:** 2025-10-22  
**Analyzer:** Kiro AI Code Analysis System
