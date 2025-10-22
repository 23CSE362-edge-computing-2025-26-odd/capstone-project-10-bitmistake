# Optimised Load Balancing (OLB) Simulation for Smart Healthcare IoT

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![Framework](https://img.shields.io/badge/framework-YAFS-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![ML Models](https://img.shields.io/badge/ML-LSTM%20%7C%20TFLite-purple.svg)
![Web UI](https://img.shields.io/badge/Web%20UI-Flask-green.svg)

A comprehensive, modularized simulation platform for **Optimised Load Balancing (OLB)** algorithms in IoT-enabled smart healthcare systems, featuring predictive placement strategies, machine learning workload forecasting, and interactive web visualization.

This project provides a complete digital twin ecosystem with advanced capabilities including:
- **Predictive Load Balancing**: ML-powered workload prediction and proactive placement
- **Edge Deployment**: TensorFlow Lite models for resource-constrained environments  
- **Interactive Web Interface**: Real-time simulation and algorithm comparison
- **Comprehensive Evaluation**: Multi-scenario testing and performance analysis

---

## Table of Contents

- [About The Project](#about-the-project)
- [Key Features](#key-features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Basic Simulation](#basic-simulation)
  - [Predictive Placement Demo](#predictive-placement-demo)
  - [Complete Pipeline](#complete-pipeline)
  - [Web Interface](#web-interface)
- [Project Structure](#project-structure)
- [Algorithms](#algorithms)
  - [Core OLB Algorithm](#core-olb-algorithm)
  - [Predictive Placement](#predictive-placement)
  - [Comparison Algorithms](#comparison-algorithms)
- [CI/ML Models](#ciml-models)
- [Web Interface](#web-interface)
- [Simulation Output](#simulation-output)
- [Contributing](#contributing)
- [License](#license)

---

## About The Project

This simulation platform implements advanced load balancing algorithms for IoT-enabled smart healthcare systems, featuring both reactive and predictive placement strategies. Built on the YAFS framework, it provides a comprehensive digital twin environment for evaluating load balancing performance across various scenarios.

The platform has evolved from a basic OLB implementation to a sophisticated ecosystem supporting:
- **Multiple Algorithm Types**: Reactive OLB, predictive placement, forecast-based strategies
- **Machine Learning Integration**: LSTM-based workload prediction with TensorFlow Lite edge deployment
- **Real-time Visualization**: Interactive web interface for simulation control and results analysis
- **Comprehensive Testing**: Multi-scenario evaluation including healthcare-specific workloads

**Built With:**
*   [Python 3.8+](https://www.python.org/)
*   [YAFS (Yet Another edge Simulator)](https://yafs.readthedocs.io/)
*   [TensorFlow/TensorFlow Lite](https://www.tensorflow.org/)
*   [Flask](https://flask.palletsprojects.com/)
*   [NetworkX](https://networkx.org/)
*   [NumPy](https://numpy.org/)
*   [Matplotlib](https://matplotlib.org/)

---

## Key Features

###  **Predictive Load Balancing**
- **LSTM-based Workload Prediction**: Forecasts future computational demands using historical data
- **Proactive Placement**: Anticipates workload changes and optimizes resource allocation
- **Pattern Recognition**: Handles steady, periodic, bursty, and increasing workload patterns

###  **Edge Deployment Support**
- **TensorFlow Lite Models**: Optimized models for resource-constrained edge devices
- **Real-time Inference**: Low-latency workload prediction on edge nodes
- **Model Conversion**: Automatic conversion from full TensorFlow to TFLite format

###  **Interactive Web Interface**
- **Real-time Simulation**: Run simulations through a modern web interface
- **Algorithm Comparison**: Side-by-side performance analysis of different algorithms
- **Visual Results**: Interactive charts and environment visualizations
- **RESTful API**: Programmatic access to simulation capabilities

###  **Comprehensive Evaluation**
- **Multi-scenario Testing**: Baseline comparison, workload patterns, scalability, healthcare scenarios
- **Performance Metrics**: Latency, energy consumption, load balancing, network usage
- **Statistical Analysis**: Detailed performance reports and comparative studies

---

## Getting Started

Follow these steps to get the simulation running on your local machine.

### Prerequisites

Ensure you have Python 3.8 or higher installed. You can check your version with:
```sh
python --version
```
### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/23CSE362-edge-computing-2025-26-odd/capstone-project-10-bitmistake.git
    cd capstone-project-10-bitmistake
    ```

2.  **Install core dependencies:**
    ```sh
    pip install yafs networkx numpy matplotlib
    ```

3.  **Install ML dependencies (for predictive features):**
    ```sh
    pip install tensorflow flask flask-cors pandas scikit-learn
    ```

4.  **Install TensorFlow Lite (for edge deployment):**
    ```sh
    pip install tflite-runtime
    ```

5.  **Verify installation:**
    ```sh
    python -c "import yafs, tensorflow, flask; print('All dependencies installed successfully!')"
    ```
---

## Usage

The platform offers multiple ways to run simulations, from basic OLB to comprehensive predictive analysis.

### Basic Simulation

Run the standard OLB simulation with CI model integration:

```sh
python main.py
```

This will:
1. Initialize the digital twin environment
2. Run LSTM workload predictions for edge nodes
3. Adjust edge node capacities based on predictions
4. Execute OLB placement algorithm
5. Generate performance reports

### Predictive Placement Demo

Experience the power of predictive placement algorithms:

```sh
python run_predictive_demo.py
```

This demo compares:
- **Reactive OLB**: Traditional reactive placement
- **Predictive Latency**: ML-powered proactive placement
- **Forecast Based**: Pattern-aware workload forecasting

### Complete Pipeline

Run comprehensive multi-scenario evaluation:

```sh
python run_complete_pipeline.py
```

This executes 4 comprehensive scenarios:
1. **Baseline Comparison**: All algorithms on standard environment
2. **Workload Patterns**: Testing on different workload types
3. **Scalability Analysis**: Performance with varying sensor counts
4. **Healthcare Scenarios**: ICU, Emergency, and Ambulatory workloads

### Web Interface

Launch the interactive web interface:

```sh
cd web_ui
python app.py
```

Then open `http://localhost:5000` in your browser to:
- Run simulations with custom parameters
- Compare algorithms in real-time
- Visualize results with interactive charts
- Export performance data

**Configuration:**
You can modify simulation parameters in the `src/utils.py` file within the `SimulationConfig` class.

---

## Project Structure

```
.
├── main.py                     # Main simulation entry point with CI integration
├── run_complete_pipeline.py    # Comprehensive multi-scenario evaluation
├── run_predictive_demo.py      # Predictive placement demonstration
├── pipeline_demo.py            # Pipeline demonstration script
├── test_edge_deployment.py     # Edge deployment testing
├── emoji_remover.py           # Utility for text processing
├── 
├── CI_Models/                  # Machine Learning Models
│   └── Workload/              # LSTM workload prediction models
│       ├── models/            # Trained TensorFlow/TFLite models
│       ├── predict.py          # Workload prediction interface
│       ├── tflite_predictor.py # Edge deployment predictor
│       └── convert_to_tflite.py # Model conversion utilities
│
├── config/                     # Configuration files
│   ├── experiment_config.json  # Experiment parameters
│   └── placement_config.json  # Placement algorithm settings
│
├── data/                       # Simulation results (JSON format)
├── docs/                       # Project documentation
├── experiments/               # Evaluation and analysis scripts
│   ├── create_plots.py        # Visualization generation
│   ├── evaluation.py          # Performance evaluation
│   ├── healthcare_evaluation.py # Healthcare-specific analysis
│   ├── predictive_vs_reactive_comparison.py # Algorithm comparison
│   └── workload_comparison_study.py # Workload pattern analysis
│
├── logs/                       # Simulation logs
├── plots/                      # Generated visualizations
├── reports/                    # Formatted simulation reports
├── results/                    # YAFS simulation outputs
├── 
├── src/                        # Core source code
│   ├── __init__.py            # Package exports
│   ├── comparison_algorithms.py # Alternative placement algorithms
│   ├── devices.py             # Sensor and edge Node models
│   ├── environment.py         # Digital Twin Environment
│   ├── healthcare_scenarios.py # Healthcare-specific scenarios
│   ├── metrics.py             # Performance metrics collection
│   ├── metrics_definitions.py # Custom metrics definitions
│   ├── olb_algorithm.py       # Core OLB implementation
│   ├── predictive_placement.py # Predictive placement algorithms
│   ├── utils.py               # Configuration and utilities
│   ├── visualization.py       # Plotting and visualization
│   └── yafs_integration.py    # YAFS framework integration
│
├── web_ui/                     # Interactive Web Interface
│   ├── app.py                 # Flask web application
│   ├── start_server.bat      # Windows server startup
│   ├── static/                # Web assets
│   │   ├── css/style.css     # Styling
│   │   └── js/app.js         # Frontend JavaScript
│   └── templates/             # HTML templates
│       └── index.html        # Main interface
│
└── README.md                   # This file
```

---

## Architecture

The OLB simulation platform follows a modular, layered architecture designed for scalability, maintainability, and extensibility. The architecture integrates multiple components working together to provide comprehensive load balancing simulation capabilities.

### System Overview

The platform implements a **three-tier architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  Web Interface (Flask)  │  CLI Scripts  │  API Endpoints     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  Simulation Orchestrator  │  Algorithm Engine  │  Metrics   │
│  Pipeline Manager         │  Placement Policies │  Collector│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  Digital Twin Environment  │  Device Models  │  ML Models   │
│  YAFS Integration         │  OLB Calculator │  Predictors │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                     │
├─────────────────────────────────────────────────────────────┤
│  YAFS Framework  │  TensorFlow/TFLite  │  NetworkX  │ Files│
└─────────────────────────────────────────────────────────────┘
```

### Core Architecture Components

#### 1. **Digital Twin Environment** (`src/environment.py`)

The **DigitalTwinEnvironment** class serves as the central orchestrator for the simulation world:

```python
class DigitalTwinEnvironment:
    def __init__(self, width=3000, height=2000):
        self.width = width                    # Environment dimensions
        self.height = height
        self.sensors = []                     # Tier 1: IoT sensors
        self.edge_nodes = []                   # Tier 2: edge computing nodes
        self.cloud_node = None               # Tier 3: Cloud data center
        self.proxy_node = None               # Network proxy
```

**Key Responsibilities:**
- **Spatial Management**: Maintains 2D coordinate system (3000x2000 units)
- **Device Lifecycle**: Creates, initializes, and manages all physical entities
- **Environment Validation**: Ensures devices are within spatial bounds
- **Configuration Management**: Handles random seed-based reproducible initialization

#### 2. **Device Models** (`src/devices.py`)

The platform implements a **hierarchical device model** representing the three-tier architecture:

##### Tier 1: IoT Layer
```python
class SensorDevice:
    def __init__(self, device_id, coordinates, transmission_power, 
                 average_flow_rate, flow_traffic_size, average_flow_size):
        self.device_id = device_id
        self.coordinates = coordinates          # (x, y) position
        self.transmissionPower = transmission_power    # P(x) in Watts
        self.averageFlowRate = average_flow_rate       # fl(x) in Hz
        self.flowTrafficSize = flow_traffic_size       # l(x) in megabits
        self.averageFlowSize = average_flow_size       # ν(x) in MI
```

##### Tier 2: edge Layer
```python
class EdgeNodeDevice:
    def __init__(self, node_id, coordinates, processing_power,
                 bandwidth, carrier_frequency, noise_power):
        self.node_id = node_id
        self.coordinates = coordinates          # (x, y) position
        self.processingPower = processing_power # Cj in MIPS
        self.bandwidth = bandwidth             # BWj in MHz
        self.carrierFrequency = carrier_frequency # in GHz
        self.noisePower = noise_power          # σ² in Watts
        self.assigned_modules = []             # Track assignments
```

##### Tier 3: Cloud Layer
```python
class CloudNodeDevice(EdgeNodeDevice):
    def __init__(self, node_id="cloud", coordinates=(0, 0),
                 processing_power=1e6, bandwidth=1000, ...):
        # Inherits from EdgeNodeDevice with cloud-scale parameters
```

#### 3. **OLB Algorithm Engine** (`src/olb_algorithm.py`)

The **OLBLatencyCalculator** implements the mathematical foundation:

```python
class OLBLatencyCalculator:
    def calculate_communication_latency(self, sensor, edge_node, assigned_sensors):
        # Implements L_m(j) calculation:
        # 1. Distance calculation (Euclidean)
        # 2. Channel gain: g(x) = 10 * log10(λ²/(4πd)²)
        # 3. SNR: SNR(x) = (P(x) * g(x))/σ²
        # 4. Device capacity: cj(x) = BWj * log2(1 + SNR(x))
        # 5. Traffic load: eaj(x) = (fl(x) * l(x))/cj(x)
        # 6. Communication latency: L_m(j) = TLj/(1 - TLj)
    
    def calculate_computing_latency(self, sensor, edge_node, assigned_sensors):
        # Implements L_p(j) calculation:
        # 1. Computing load: ebj(x) = (fl(x) * ν(x))/Cj
        # 2. Total computing load: CLj = Σ ebj(x)
        # 3. Computing latency: L_p(j) = CLj/(1 - CLj)
```

The **OLBPlacement** class integrates with YAFS framework:

```python
class OLBPlacement(Placement):
    def __init__(self, name, json_file, digital_twin):
        super().__init__(name, json_file)
        self.digital_twin = digital_twin
        self.calculator = OLBLatencyCalculator()
        self.module_assignments = {}    # Track assignments
        self._latency_cache = {}        # Performance optimization
        self._node_loads = {}          # Load tracking
```

#### 4. **Predictive Placement Engine** (`src/predictive_placement.py`)

Advanced algorithms extending the core OLB:

##### Predictive Latency Placement
```python
class PredictiveLatencyPlacement(Placement):
    def __init__(self, name, json_file, digital_twin, prediction_horizon=10):
        super().__init__(name, json_file)
        self.workload_predictor = WorkloadPredictor(use_tflite=True)
        self.prediction_horizon = prediction_horizon
        self.placement_decisions = []  # Decision tracking
    
    def _find_predictive_optimal_node(self, sensor):
        # Uses ML models to predict future workload patterns
        # Considers predicted latency over multiple time horizons
        # Makes proactive placement decisions
```

##### Forecast-Based Placement
```python
class ForecastBasedPlacement(Placement):
    def __init__(self, name, json_file, digital_twin, workload_forecaster):
        super().__init__(name, json_file)
        self.workload_forecaster = workload_forecaster
        self.forecast_horizon = 10
    
    def _find_forecast_optimal_node(self, sensor, future_load_multiplier):
        # Uses pattern-based workload forecasting
        # Adjusts sensor parameters based on predicted patterns
        # Optimizes for anticipated workload changes
```

#### 5. **YAFS Integration Layer** (`src/yafs_integration.py`)

Bridges the domain model with the YAFS simulation framework:

##### Application Definition
```python
def create_smart_healthcare_application(digital_twin):
    app = Application(name="SmartHealthcare")
    
    # Create modules for each sensor
    for sensor in digital_twin.sensors:
        client_module = f"Client_Module_Sensor_{sensor.device_id}"
        processing_module = f"Processing_Module_Sensor_{sensor.device_id}"
        
        # Define module types and resource requirements
        modules.append({client_module: {"Type": Application.TYPE_SOURCE, "RAM": 10, "IPT": 1000}})
        modules.append({processing_module: {"Type": Application.TYPE_MODULE, "RAM": 50, "IPT": int(sensor.averageFlowSize)}})
    
    # Define message flows: Sensor → Processing → Storage
    for sensor in digital_twin.sensors:
        msg = Message(name=f"sensor_msg_{sensor.device_id}",
                     src=client_module, dst=processing_module,
                     instructions=int(sensor.averageFlowSize),
                     bytes=int(sensor.flowTrafficSize * 1000000))
        app.add_source_messages(msg)
```

##### Topology Creation
```python
def create_yafs_topology(digital_twin):
    G = nx.Graph()
    
    # Create network topology: edge Nodes ↔ Proxy ↔ Cloud
    edge_node_names = [f"edge_{i}" for i in range(len(digital_twin.edge_nodes))]
    all_nodes = edge_node_names + ["proxy", "cloud"]
    G.add_nodes_from(all_nodes)
    
    # Define network connections
    for i in range(len(digital_twin.edge_nodes)):
        G.add_edge(f"edge_{i}", "proxy")
    G.add_edge("proxy", "cloud")
    
    # Configure node resources based on device models
    for i, edge_node in enumerate(digital_twin.edge_nodes):
        topology.G.nodes[f"edge_{i}"]["IPT"] = int(edge_node.processingPower)
        topology.G.nodes[f"edge_{i}"]["RAM"] = 1000
        topology.G.nodes[f"edge_{i}"]["STORAGE"] = 10000
```

#### 6. **Machine Learning Integration** (`CI_Models/Workload/`)

The ML subsystem provides intelligent workload prediction:

##### Edge Workload Predictor
```python
class EdgeWorkloadPredictor:
    def __init__(self, model_dir: str = "models", use_tflite: bool = True):
        self.model_dir = model_dir
        self.use_tflite = use_tflite
        self.tflite_interpreter = None
        self.sensor_history = {}      # Runtime history tracking
        self.edge_node_history = {}   # Node load history
        self.history_window = 50     # Sliding window size
        self.prediction_horizon = 10 # Future prediction steps
    
    def predict_future_latency(self, sensor, edge_node, assigned_sensors, calculator):
        # Combines ML predictions with OLB calculations
        # Uses historical patterns to forecast future workload
        # Returns predicted latency for proactive placement
```

##### Pattern-Based Workload Generator
```python
class PatternBasedWorkloadGenerator:
    def __init__(self, pattern_type: str):
        self.pattern_type = pattern_type  # steady, periodic, bursty, increasing
        self.current_step = 0
        self.pattern_parameters = self._initialize_pattern()
    
    def get_current_multiplier(self) -> float:
        # Generates workload multipliers based on pattern type
        # Supports various healthcare workload patterns
    
    def forecast_future_multipliers(self, horizon: int) -> List[float]:
        # Generates future workload predictions
        # Used by forecast-based placement algorithms
```

#### 7. **Performance Metrics System** (`src/metrics.py`)

Comprehensive performance evaluation and reporting:

```python
class PerformanceMetrics:
    def __init__(self):
        self.overall_latency = 0
        self.network_usage = 0
        self.execution_time = 0
        self.energy_consumption = 0
        self.cost_of_execution = 0
        self.communication_latency = 0
        self.computing_latency = 0
        self.detailed_assignments = []
        self.load_balance_score = 0
        self.max_utilization = 0
    
    def collect_metrics(self, digital_twin, placement, algorithm_name):
        # Collects comprehensive performance metrics
        # Calculates latency, energy, load balancing scores
        # Generates detailed assignment analysis
    
    def get_summary_dict(self):
        # Returns structured metrics for API consumption
        # Supports both human-readable reports and machine-readable data
```

#### 8. **Web Interface Architecture** (`web_ui/`)

Modern web-based simulation interface:

##### Backend (Flask)
```python
# web_ui/app.py
@app.route('/api/simulate', methods=['POST'])
def simulate():
    # Handles single algorithm simulation requests
    # Returns real-time results and visualizations

@app.route('/api/compare', methods=['POST'])
def compare_algorithms():
    # Executes multiple algorithms for comparison
    # Provides side-by-side performance analysis

@app.route('/api/generate-chart', methods=['POST'])
def generate_chart():
    # Creates interactive performance visualizations
    # Returns base64-encoded chart images
```

##### Frontend Architecture
```
web_ui/
├── static/
│   ├── css/style.css          # Modern dark theme styling
│   └── js/app.js             # Interactive simulation controls
├── templates/
│   └── index.html            # Main interface template
└── app.py                    # Flask application server
```

### Data Flow Architecture

The platform implements a **multi-stage data processing pipeline**:

```
1. ENVIRONMENT INITIALIZATION
   DigitalTwinEnvironment → Device Models → YAFS Topology

2. WORKLOAD PREDICTION (Optional)
   ML Models → Workload Predictors → Pattern Generators

3. PLACEMENT DECISION
   Placement Algorithms → OLB Calculator → Assignment Logic

4. SIMULATION EXECUTION
   YAFS Framework → Message Routing → Resource Allocation

5. METRICS COLLECTION
   Performance Metrics → Data Aggregation → Report Generation

6. VISUALIZATION & OUTPUT
   Charts → Reports → API Responses → Web Interface
```

### Integration Patterns

#### 1. **Strategy Pattern** - Algorithm Selection
Different placement algorithms implement a common interface, allowing runtime selection:
```python
# All placement classes inherit from YAFS Placement
class OLBPlacement(Placement): ...
class PredictiveLatencyPlacement(Placement): ...
class ForecastBasedPlacement(Placement): ...
```

#### 2. **Observer Pattern** - Metrics Collection
The metrics system observes placement decisions and simulation events:
```python
# Metrics collector observes placement changes
metrics.collect_metrics(environment, placement, algorithm_name)
```

#### 3. **Factory Pattern** - Device Creation
Device models are created through factory methods in the environment:
```python
# Environment creates devices based on configuration
environment.initialize_sensors(num_sensors, seed)
environment.initialize_edge_nodes(num_edge_nodes, seed)
```

#### 4. **Adapter Pattern** - YAFS Integration
The integration layer adapts domain models to YAFS framework requirements:
```python
# Domain models adapted to YAFS Application and Topology
app = create_smart_healthcare_application(environment)
topology = create_yafs_topology(environment)
```

### Scalability Considerations

#### Horizontal Scaling
- **Parallel Simulations**: Multiple independent simulation instances
- **Distributed ML**: Separate ML inference services
- **Load Balancing**: Web interface supports multiple concurrent users

#### Vertical Scaling
- **Memory Optimization**: Efficient data structures and caching
- **CPU Optimization**: Vectorized calculations and parallel processing
- **Storage Optimization**: Compressed model storage and efficient I/O

#### Edge Deployment
- **TFLite Models**: Optimized for resource-constrained devices
- **Minimal Dependencies**: Reduced runtime requirements
- **Real-time Inference**: Low-latency prediction capabilities

This architecture provides a robust foundation for comprehensive load balancing simulation while maintaining flexibility for future enhancements and extensions.

---

## Algorithms

The platform implements multiple placement algorithms for comprehensive evaluation and comparison.

### Core OLB Algorithm

The **Optimised Load Balancing (OLB)** algorithm dynamically assigns sensor workloads to the most optimal edge node by calculating a total latency score. The node with the minimum score is selected.

#### Communication Latency Analysis (L_m(j))

This measures the time it takes to transmit data from a sensor to a edge node:

1. **Distance**: Euclidean distance between the sensor and the edge node
2. **Channel Gain & SNR**: Signal strength and quality over the wireless channel
3. **Device Capacity**: The maximum data rate the edge node can handle from the sensor
4. **Total Traffic Load**: The cumulative traffic from all sensors assigned to the node

#### Computing Latency Analysis (L_p(j))

This measures the time it takes for a edge node to process the received data:

1. **Individual Computing Load**: The computational demand of a single sensor's workload
2. **Total Computing Load**: The cumulative computational demand from all sensors assigned to the node

The final placement decision is made by selecting the edge node `j` that minimizes `Total Latency = L_m(j) + L_p(j)`.

### Predictive Placement

#### Predictive Latency Placement
- **LSTM-based Prediction**: Uses trained LSTM models to forecast future workload patterns
- **Proactive Optimization**: Anticipates workload changes and adjusts placement accordingly
- **Horizon-based Planning**: Considers multiple future time steps for better decisions

#### Forecast-Based Placement
- **Pattern Recognition**: Identifies workload patterns (steady, periodic, bursty, increasing)
- **Workload Forecasting**: Generates future workload predictions based on identified patterns
- **Adaptive Strategies**: Adjusts placement strategy based on predicted workload characteristics

### Comparison Algorithms

The platform includes several baseline algorithms for comparison:

- **Random Placement**: Assigns sensors to edge nodes randomly
- **Distance Placement**: Assigns sensors to the nearest edge node
- **Load Balanced Placement**: Distributes sensors evenly across edge nodes
- **FNPA Placement**: edge Node Proximity Algorithm for geographic optimization

---

## CI/ML Models

The platform integrates machine learning models for intelligent workload prediction and edge deployment.

### LSTM Workload Predictor

**Location**: `CI_Models/Workload/`

The LSTM-based workload predictor provides intelligent forecasting capabilities:

#### Features
- **Multi-node Prediction**: Individual models for each edge node (system-1 to system-6)
- **Edge Deployment**: TensorFlow Lite models for resource-constrained environments
- **Pattern Recognition**: Handles various workload patterns (steady, periodic, bursty, increasing)
- **Real-time Inference**: Low-latency prediction suitable for real-time placement decisions

#### Model Architecture
- **Input**: Historical workload data (sequence length: 10-20 time steps)
- **Architecture**: LSTM layers with dropout for regularization
- **Output**: Future workload predictions (configurable horizon)
- **Training**: Separate models trained on node-specific workload patterns

#### Usage
```python
from CI_Models.Workload.predict import WorkloadPredictor

# Initialize predictor
predictor = WorkloadPredictor(model_dir="CI_Models/Workload/models")

# Predict future workload for a specific node
predictions = predictor.predict_future("system-1", future_steps=10)
```

### Edge Deployment Support

#### TensorFlow Lite Integration
- **Model Conversion**: Automatic conversion from TensorFlow to TFLite format
- **Optimized Inference**: Reduced memory footprint and faster execution
- **Cross-platform**: Compatible with various edge devices and architectures

#### Edge Predictor Class
```python
from CI_Models.Workload.tflite_predictor import EdgeWorkloadPredictor

# Initialize edge predictor
edge_predictor = EdgeWorkloadPredictor(model_dir="models", use_tflite=True)

# Real-time prediction
prediction = edge_predictor.predict_current_load("system-1")
```

### Workload Pattern Generators

#### Pattern-Based Generator
- **Steady**: Constant workload levels
- **Periodic**: Cyclical workload patterns (daily, weekly)
- **Bursty**: Random spikes with normal baseline
- **Increasing**: Gradually increasing workload over time

#### Healthcare-Specific Patterns
- **ICU**: Critical events with 5% probability
- **Emergency**: High-frequency emergency scenarios
- **Ambulatory**: Daily cycle patterns with peak hours

---

## Web Interface

The platform includes a modern web interface for interactive simulation and analysis.

### Features

#### Real-time Simulation
- **Parameter Configuration**: Adjust sensor count, edge nodes, algorithm selection
- **Live Results**: Real-time performance metrics and visualizations
- **Interactive Charts**: Dynamic performance comparisons

#### Algorithm Comparison
- **Side-by-side Analysis**: Compare multiple algorithms simultaneously
- **Performance Metrics**: Latency, energy consumption, load balancing scores
- **Visual Assignments**: See sensor-to-edge node assignments on interactive map

#### API Endpoints

**Simulation API**
- `POST /api/simulate`: Run single algorithm simulation
- `POST /api/compare`: Compare multiple algorithms
- `POST /api/generate-chart`: Generate performance comparison charts

**Configuration API**
- `GET /api/environment-info`: Get default configuration parameters
- `GET /api/test-algorithms`: Test algorithm functionality

### Usage

1. **Start the Web Server**:
   ```sh
   cd web_ui
   python app.py
   ```

2. **Access the Interface**:
   Open `http://localhost:5000` in your browser

3. **Run Simulations**:
   - Configure simulation parameters
   - Select algorithms to compare
   - View real-time results and visualizations

### Web Interface Components

#### Frontend (`web_ui/static/`)
- **CSS**: Modern, responsive styling with dark theme
- **JavaScript**: Interactive simulation controls and chart generation
- **Templates**: HTML templates for the web interface

#### Backend (`web_ui/app.py`)
- **Flask Application**: RESTful API for simulation control
- **Real-time Processing**: Concurrent simulation execution
- **Chart Generation**: Matplotlib-based performance visualizations

---

## Simulation Output

The platform generates comprehensive output across multiple formats and locations:

### Data Files (`data/`)
- **`olb_simulation_results.json`**: Complete simulation results with CI predictions
- **`complete_pipeline_*.json`**: Multi-scenario evaluation results
- **`predictive_comparison_*.json`**: Predictive vs reactive algorithm comparison
- **`workload_comparison_*.json`**: Workload pattern analysis results
- **`algorithm_comparison_*.json`**: Cross-algorithm performance comparison

### Reports (`reports/`)
- **`olb_simulation_report.txt`**: Human-readable performance summary
- **`complete_pipeline_*.txt`**: Comprehensive multi-scenario analysis
- **`comparison_report_*.txt`**: Algorithm comparison analysis

### Visualizations (`plots/`)
- **Performance Charts**: Bar charts comparing algorithm metrics
- **Environment Maps**: Sensor and edge node placement visualizations
- **Workload Patterns**: Time series plots of workload predictions
- **Comparison Plots**: Side-by-side algorithm performance analysis

### YAFS Results (`results/`)
- **CSV Files**: Detailed simulation metrics in tabular format
- **Link Files**: Network topology and message flow data
- **Diagnostic Files**: Simulation execution diagnostics

### Web Interface Output
- **Real-time Charts**: Interactive performance visualizations
- **JSON API Responses**: Structured data for frontend consumption
- **Base64 Images**: Generated charts embedded in web responses

---

## Contributing

We welcome contributions to improve the OLB simulation platform! Here's how you can contribute:

### Development Setup

1. **Fork the repository** and clone your fork
2. **Create a virtual environment**:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
4. **Run tests** to ensure everything works:
   ```sh
   python -m pytest tests/
   ```

### Areas for Contribution

#### Algorithm Development
- **New Placement Algorithms**: Implement additional load balancing strategies
- **Predictive Models**: Develop new ML models for workload prediction
- **Optimization Techniques**: Improve existing algorithm performance

#### Platform Enhancement
- **Web Interface**: Improve UI/UX, add new visualizations
- **API Development**: Extend REST API with new endpoints
- **Edge Deployment**: Optimize models for different edge platforms

#### Testing & Documentation
- **Unit Tests**: Add comprehensive test coverage
- **Integration Tests**: Test end-to-end workflows
- **Documentation**: Improve code documentation and user guides

#### Performance Optimization
- **Simulation Speed**: Optimize YAFS simulation performance
- **Memory Usage**: Reduce memory footprint for large-scale simulations
- **Parallel Processing**: Implement concurrent simulation execution

### Submission Process

1. **Create a feature branch**: `git checkout -b feature/your-feature-name`
2. **Make your changes** with appropriate tests and documentation
3. **Run the test suite**: Ensure all tests pass
4. **Update documentation**: Update README and code comments as needed
5. **Submit a pull request** with a clear description of your changes

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for all public functions and classes
- Include type hints where appropriate
- Write comprehensive tests for new functionality

---

## License

Distributed under the MIT License.
