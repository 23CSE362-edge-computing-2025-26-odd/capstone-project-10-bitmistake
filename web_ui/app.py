from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import sys
import os
import json
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import (
    DigitalTwinEnvironment,
    create_placement_json,
    create_smart_healthcare_application,
    create_yafs_topology,
    PerformanceMetrics,
    SimulationVisualizer,
    PREDICTIVE_AVAILABLE,
)
from src.algorithm_registry import get_registry, initialize_default_registry
from src.orchestrator import setup_directories

# Initialize algorithm registry on module load
initialize_default_registry()
print(f"[INFO] Web UI: Initialized algorithm registry with {len(get_registry())} algorithms")

app = Flask(__name__)
CORS(app)

simulation_cache = {}
comparison_results = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate', methods=['POST'])
def simulate():
    try:
        data = request.json
        
        # Input validation
        num_sensors = data.get('numSensors', 10)
        num_edge_nodes = data.get('numedgeNodes', 4)
        algorithm = data.get('algorithm', 'reactive')
        
        # Validate sensor count
        if not isinstance(num_sensors, int) or num_sensors < 1:
            return jsonify({
                'success': False,
                'error': 'Number of sensors must be a positive integer'
            }), 400
        if num_sensors > 100:
            return jsonify({
                'success': False,
                'error': 'Number of sensors cannot exceed 100'
            }), 400
        
        # Validate edge node count
        if not isinstance(num_edge_nodes, int) or num_edge_nodes < 1:
            return jsonify({
                'success': False,
                'error': 'Number of edge nodes must be a positive integer'
            }), 400
        if num_edge_nodes > 20:
            return jsonify({
                'success': False,
                'error': 'Number of edge nodes cannot exceed 20'
            }), 400
        
        # Validate algorithm
        valid_algorithms = ['olb', 'lbs', 'lab', 'mec', 'fnpa']
        if PREDICTIVE_AVAILABLE:
            valid_algorithms.append('predictive')
        
        if algorithm not in valid_algorithms:
            return jsonify({
                'success': False,
                'error': f'Invalid algorithm. Must be one of: {", ".join(valid_algorithms)}'
            }), 400
        
        # Check if predictive is requested but not available
        if algorithm == 'predictive' and not PREDICTIVE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Predictive algorithm is not available. Please install required dependencies.'
            }), 400
        
        print(f"[INFO] Starting simulation: {num_sensors} sensors, {num_edge_nodes} edge nodes, {algorithm}")
        
        environment = DigitalTwinEnvironment(3000, 2000)
        environment.initialize_sensors(num_sensors, seed=42)
        environment.initialize_edge_nodes(num_edge_nodes, seed=42)
        environment.initialize_cloud()
        
        print(f"[INFO] Environment initialized with {len(environment.sensors)} sensors and {len(environment.edge_nodes)} edge nodes")
        
        # Initialize MQTT environment
        from src.mqtt_simulator import MQTTSimulationEnvironment
        mqtt_env = MQTTSimulationEnvironment()
        mqtt_env.publish_simulation_start({
            "algorithm": algorithm,
            "num_sensors": num_sensors,
            "num_edge_nodes": num_edge_nodes,
            "source": "web_ui"
        })
        
        app_obj = create_smart_healthcare_application(environment)
        topology = create_yafs_topology(environment)
        
        # Setup directories using orchestrator
        setup_directories(["config", "results"])
        
        config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
        placement_json = create_placement_json(config_dir)
        
        # Create placement algorithm using registry
        registry = get_registry()
        algorithm_class = registry.get(algorithm.upper())
        
        if algorithm_class is None:
            return jsonify({
                'success': False,
                'error': f'Unknown algorithm: {algorithm}'
            }), 400
        
        # Special handling for predictive algorithm
        if algorithm == 'predictive':
            if not PREDICTIVE_AVAILABLE:
                return jsonify({
                    'success': False,
                    'error': 'Predictive algorithm is not available'
                }), 400
            placement = algorithm_class("Predictive", placement_json, environment, prediction_horizon=10)
        else:
            placement = algorithm_class(algorithm.upper(), placement_json, environment)
        
        from yafs.core import Sim
        from yafs.population import Population
        
        # Results directory already created by setup_directories
        results_dir = os.path.join(os.path.dirname(__file__), "..", "results")
        
        # Use constant for simulation time
        from src.common_utils import PlacementConstants
        
        s = Sim(topology, default_results_path=os.path.join(results_dir, f"sim_{algorithm}"))
        population = Population(name="WebUI")
        
        # Connect MQTT and publish placement decisions
        mqtt_env.connect_to_yafs_simulation(s)
        
        s.deploy_app(app_obj, placement, population)
        
        # Publish placement decisions to MQTT
        mqtt_env.publish_placement_decisions(placement, environment)
        
        s.run(until=PlacementConstants.DEFAULT_SIMULATION_TIME)
        
        # Advance MQTT time
        mqtt_env.advance_time(PlacementConstants.DEFAULT_SIMULATION_TIME * 1000)
        
        print(f"[INFO] Simulation completed, collecting metrics...")
        
        metrics = PerformanceMetrics()
        metrics.collect_metrics(environment, placement, algorithm)
        
        # Publish final metrics to MQTT
        mqtt_env.publish_simulation_end(metrics.get_summary_dict())
        
        result = metrics.get_summary_dict()
        result['mqtt_statistics'] = mqtt_env.get_statistics()
        
        print(f"[INFO] Metrics collected: {result}")
        
        sensors_data = [
            {
                'id': sensor.device_id,
                'x': sensor.coordinates[0],
                'y': sensor.coordinates[1],
                'power': sensor.transmissionPower
            }
            for sensor in environment.sensors
        ]
        
        edge_nodes_data = [
            {
                'id': edge.node_id,
                'x': edge.coordinates[0],
                'y': edge.coordinates[1],
                'capacity': edge.processingPower
            }
            for edge in environment.edge_nodes
        ]
        
        assignments = []
        for edge_id, sensors in placement.module_assignments.items():
            for sensor in sensors:
                assignments.append({
                    'sensorId': sensor.device_id,
                    'edgeId': edge_id
                })
        
        print(f"[INFO] Returning {len(sensors_data)} sensors, {len(edge_nodes_data)} edge nodes, {len(assignments)} assignments")
        
        simulation_cache[algorithm] = {
            'metrics': result,
            'sensors': sensors_data,
            'edgeNodes': edge_nodes_data,
            'assignments': assignments
        }
        
        return jsonify({
            'success': True,
            'metrics': result,
            'sensors': sensors_data,
            'edgeNodes': edge_nodes_data,
            'assignments': assignments
        })
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_msg = traceback.format_exc()
        print(f"[ERROR] Simulation failed: {error_msg}")
        print(f"[ERROR] Traceback:\n{traceback_msg}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/api/compare', methods=['POST'])
def compare_algorithms():
    try:
        data = request.json
        num_sensors = data.get('numSensors', 10)
        num_edge_nodes = data.get('numedgeNodes', 4)
        algorithms_to_compare = data.get('algorithms', ['olb', 'predictive', 'random', 'distance'])
        
        # Input validation
        if not isinstance(num_sensors, int) or num_sensors < 1 or num_sensors > 100:
            return jsonify({
                'success': False,
                'error': 'Number of sensors must be between 1 and 100'
            }), 400
        
        if not isinstance(num_edge_nodes, int) or num_edge_nodes < 1 or num_edge_nodes > 20:
            return jsonify({
                'success': False,
                'error': 'Number of edge nodes must be between 1 and 20'
            }), 400
        
        if not isinstance(algorithms_to_compare, list) or len(algorithms_to_compare) < 1:
            return jsonify({
                'success': False,
                'error': 'Must specify at least one algorithm to compare'
            }), 400
        
        valid_algorithms = ['olb', 'lbs', 'lab', 'mec', 'fnpa']
        if PREDICTIVE_AVAILABLE:
            valid_algorithms.append('predictive')
        
        invalid_algos = [a for a in algorithms_to_compare if a not in valid_algorithms]
        if invalid_algos:
            return jsonify({
                'success': False,
                'error': f'Invalid algorithms: {", ".join(invalid_algos)}'
            }), 400
        
        # Check if predictive is requested but not available
        if 'predictive' in algorithms_to_compare and not PREDICTIVE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Predictive algorithm is not available. Please install required dependencies.'
            }), 400
        
        print(f"[INFO] Starting comparison with {num_sensors} sensors and {num_edge_nodes} edge nodes")
        print(f"[INFO] Comparing algorithms: {algorithms_to_compare}")
        
        # Initialize MQTT environment for comparison
        from src.mqtt_simulator import MQTTSimulationEnvironment
        mqtt_env = MQTTSimulationEnvironment()
        mqtt_env.publish_simulation_start({
            "type": "comparison",
            "algorithms": algorithms_to_compare,
            "num_sensors": num_sensors,
            "num_edge_nodes": num_edge_nodes,
            "source": "web_ui"
        })
        
        results = {}
        
        # Create ONE environment that all algorithms will use (same seed for fair comparison)
        base_environment = DigitalTwinEnvironment(3000, 2000)
        base_environment.initialize_sensors(num_sensors, seed=42)
        base_environment.initialize_edge_nodes(num_edge_nodes, seed=42)
        base_environment.initialize_cloud()
        
        for algorithm in algorithms_to_compare:
            print(f"[INFO] Running {algorithm} algorithm...")
            
            # Create a fresh environment with same configuration
            environment = DigitalTwinEnvironment(3000, 2000)
            environment.initialize_sensors(num_sensors, seed=42)
            environment.initialize_edge_nodes(num_edge_nodes, seed=42)
            environment.initialize_cloud()
            
            app_obj = create_smart_healthcare_application(environment)
            topology = create_yafs_topology(environment)
            
            # Setup directories using orchestrator (only once per comparison)
            if algorithm == algorithms_to_compare[0]:
                setup_directories(["config", "results"])
            
            config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
            placement_json = create_placement_json(config_dir)
            
            # Use registry to get algorithm class
            print(f"[DEBUG] Creating placement algorithm: {algorithm}")
            registry = get_registry()
            algorithm_class = registry.get(algorithm.upper())
            
            if algorithm_class is None:
                print(f"[ERROR] Unknown algorithm: {algorithm}")
                continue
            
            # Special handling for predictive algorithm
            if algorithm == 'predictive':
                if not PREDICTIVE_AVAILABLE:
                    print(f"[ERROR] Predictive algorithm not available")
                    continue
                placement = algorithm_class("Predictive", placement_json, environment, prediction_horizon=10)
            else:
                placement = algorithm_class(algorithm.upper(), placement_json, environment)
            
            print(f"[DEBUG] Placement class: {placement.__class__.__name__}")
            
            from yafs.core import Sim
            from yafs.population import Population
            
            # Results directory already created by setup_directories
            results_dir = os.path.join(os.path.dirname(__file__), "..", "results")
            
            s = Sim(topology, default_results_path=os.path.join(results_dir, f"compare_{algorithm}"))
            population = Population(name=f"Compare_{algorithm}")
            
            # Connect MQTT
            mqtt_env.connect_to_yafs_simulation(s)
            
            print(f"[DEBUG] Deploying app for {algorithm}...")
            s.deploy_app(app_obj, placement, population)
            
            # Publish placement decisions
            mqtt_env.publish_placement_decisions(placement, environment)
            
            print(f"[DEBUG] Running simulation for {algorithm}...")
            s.run(until=PlacementConstants.DEFAULT_SIMULATION_TIME)
            
            # Advance MQTT time
            mqtt_env.advance_time(PlacementConstants.DEFAULT_SIMULATION_TIME * 1000)
            
            print(f"[DEBUG] Collecting metrics for {algorithm}...")
            print(f"[DEBUG] Placement has {len(placement.module_assignments)} edge nodes with assignments")
            
            # Verify assignments are different
            assignment_summary = {}
            for edge_id, sensors in placement.module_assignments.items():
                assignment_summary[edge_id] = len(sensors)
            print(f"[DEBUG] {algorithm} assignment distribution: {assignment_summary}")
            
            metrics = PerformanceMetrics()
            metrics.collect_metrics(environment, placement, algorithm)
            result = metrics.get_summary_dict()
            
            print(f"[DEBUG] {algorithm} results: Latency={result.get('overall_latency', 0):.2f}ms, "
                  f"Energy={result.get('energy_consumption', 0):.2f}W, "
                  f"Balance={result.get('load_balance_score', 0):.3f}, "
                  f"Assignments={len(result.get('detailed_assignments', []))}")
            
            sensors_data = [
                {
                    'id': sensor.device_id,
                    'x': sensor.coordinates[0],
                    'y': sensor.coordinates[1],
                    'power': sensor.transmissionPower
                }
                for sensor in environment.sensors
            ]
            
            edge_nodes_data = [
                {
                    'id': edge.node_id,
                    'x': edge.coordinates[0],
                    'y': edge.coordinates[1],
                    'capacity': edge.processingPower
                }
                for edge in environment.edge_nodes
            ]
            
            # Get assignments - check both module_assignments and direct sensor assignments
            assignments = []
            print(f"[DEBUG] Module assignments for {algorithm}: {placement.module_assignments}")
            
            # Try to get sensor-to-edge assignments
            if hasattr(placement, 'module_assignments') and placement.module_assignments:
                for edge_id, sensors in placement.module_assignments.items():
                    for sensor in sensors:
                        assignments.append({
                            'sensorId': sensor.device_id,
                            'edgeId': edge_id
                        })
            
            # If no assignments found, return error instead of creating fake data
            if not assignments:
                print(f"[ERROR] No assignments found for {algorithm} - placement may have failed")
                result['error'] = f"No placement assignments generated for {algorithm}"
                result['assignments_available'] = False
            else:
                result['assignments_available'] = True
            
            print(f"[DEBUG] Total assignments for {algorithm}: {len(assignments)}")
            
            results[algorithm] = {
                'metrics': result,
                'sensors': sensors_data,
                'edgeNodes': edge_nodes_data,
                'assignments': assignments
            }
            
            print(f"[INFO] {algorithm} completed: latency={result['overall_latency']:.2f}ms, energy={result['energy_consumption']:.2f}W")
        
        # Calculate best algorithm
        best_algorithm = min(results.keys(), key=lambda k: results[k]['metrics']['overall_latency'])
        worst_algorithm = max(results.keys(), key=lambda k: results[k]['metrics']['overall_latency'])
        
        improvement = 0
        if results[worst_algorithm]['metrics']['overall_latency'] > 0:
            improvement = ((results[worst_algorithm]['metrics']['overall_latency'] - 
                          results[best_algorithm]['metrics']['overall_latency']) / 
                         results[worst_algorithm]['metrics']['overall_latency']) * 100
        
        # Publish comparison summary to MQTT
        comparison_summary = {
            "best_algorithm": best_algorithm,
            "worst_algorithm": worst_algorithm,
            "improvement_percent": improvement,
            "algorithms_compared": list(results.keys())
        }
        mqtt_env.publish_simulation_end(comparison_summary)
        
        comparison_results.update(results)
        
        print(f"[INFO] Comparison complete. Best: {best_algorithm}, Worst: {worst_algorithm}, Improvement: {improvement:.2f}%")
        
        return jsonify({
            'success': True,
            'results': results,
            'improvement': improvement,
            'best_algorithm': best_algorithm,
            'worst_algorithm': worst_algorithm,
            'mqtt_statistics': mqtt_env.get_statistics()
        })
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"[ERROR] Comparison failed: {error_msg}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/api/generate-chart', methods=['POST'])
def generate_chart():
    try:
        if len(comparison_results) < 1:
            return jsonify({
                'success': False,
                'error': 'Run comparison first'
            }), 400
        
        print("[INFO] Generating comparison chart...")
        
        # Prepare data
        algorithm_names = []
        algorithm_display_names = {
            'olb': 'OLB',
            'predictive': 'Predictive',
            'lbs': 'Location-Based',
            'lab': 'Load-Aware',
            'mec': 'Multi-Edge',
            'fnpa': 'FNPA'
        }
        
        latencies = []
        energies = []
        load_balances = []
        network_usage = []
        
        for alg_key in comparison_results.keys():
            algorithm_names.append(algorithm_display_names.get(alg_key, alg_key.title()))
            metrics = comparison_results[alg_key]['metrics']
            latencies.append(metrics['overall_latency'])
            energies.append(metrics['energy_consumption'])
            load_balances.append(metrics['load_balance_score'])
            network_usage.append(metrics['network_usage'])
        
        # Serene elegant color palette
        colors = ['#f0ce9e', '#d4a574', '#c89b6d', '#e6b88a', '#b8956f', '#a8856a']
        colors = colors[:len(algorithm_names)]  # Use only as many colors as needed
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 11))
        fig.patch.set_facecolor('#24181c')
        
        # Latency comparison
        bars1 = ax1.bar(algorithm_names, latencies, color=colors, alpha=0.85, edgecolor='#f0ce9e', linewidth=1.5)
        ax1.set_title(' Overall Latency (ms)', color='#f0ce9e', fontsize=15, fontweight='normal', pad=18)
        ax1.set_facecolor('#2d2126')
        ax1.tick_params(colors='#c4a07a', labelsize=9)
        ax1.spines['bottom'].set_color('#4a3d42')
        ax1.spines['left'].set_color('#4a3d42')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.grid(axis='y', alpha=0.1, color='#f0ce9e', linestyle='-', linewidth=0.5)
        ax1.set_ylabel('Latency (ms)', color='#c4a07a', fontsize=10)
        for bar, val in zip(bars1, latencies):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f}', ha='center', va='bottom', color='#f0ce9e', fontsize=9)
        
        # Energy comparison
        bars2 = ax2.bar(algorithm_names, energies, color=colors, alpha=0.85, edgecolor='#f0ce9e', linewidth=1.5)
        ax2.set_title(' Energy Consumption (W)', color='#f0ce9e', fontsize=15, fontweight='normal', pad=18)
        ax2.set_facecolor('#2d2126')
        ax2.tick_params(colors='#c4a07a', labelsize=9)
        ax2.spines['bottom'].set_color('#4a3d42')
        ax2.spines['left'].set_color('#4a3d42')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.grid(axis='y', alpha=0.1, color='#f0ce9e', linestyle='-', linewidth=0.5)
        ax2.set_ylabel('Energy (W)', color='#c4a07a', fontsize=10)
        for bar, val in zip(bars2, energies):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f}', ha='center', va='bottom', color='#f0ce9e', fontsize=9)
        
        # Load balance comparison
        bars3 = ax3.bar(algorithm_names, load_balances, color=colors, alpha=0.85, edgecolor='#f0ce9e', linewidth=1.5)
        ax3.set_title(' Load Balance Score', color='#f0ce9e', fontsize=15, fontweight='normal', pad=18)
        ax3.set_facecolor('#2d2126')
        ax3.tick_params(colors='#c4a07a', labelsize=9)
        ax3.spines['bottom'].set_color('#4a3d42')
        ax3.spines['left'].set_color('#4a3d42')
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)
        ax3.grid(axis='y', alpha=0.1, color='#f0ce9e', linestyle='-', linewidth=0.5)
        ax3.set_ylabel('Balance Score', color='#c4a07a', fontsize=10)
        for bar, val in zip(bars3, load_balances):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.3f}', ha='center', va='bottom', color='#f0ce9e', fontsize=9)
        
        # Network usage comparison
        bars4 = ax4.bar(algorithm_names, network_usage, color=colors, alpha=0.85, edgecolor='#f0ce9e', linewidth=1.5)
        ax4.set_title(' Network Usage (MB/s)', color='#f0ce9e', fontsize=15, fontweight='normal', pad=18)
        ax4.set_facecolor('#2d2126')
        ax4.tick_params(colors='#c4a07a', labelsize=9)
        ax4.spines['bottom'].set_color('#4a3d42')
        ax4.spines['left'].set_color('#4a3d42')
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        ax4.grid(axis='y', alpha=0.1, color='#f0ce9e', linestyle='-', linewidth=0.5)
        ax4.set_ylabel('Network (MB/s)', color='#c4a07a', fontsize=10)
        for bar, val in zip(bars4, network_usage):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f}', ha='center', va='bottom', color='#f0ce9e', fontsize=9)
        
        plt.tight_layout(pad=3.0)
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', facecolor='#24181c', dpi=130, bbox_inches='tight')
        img_buffer.seek(0)
        
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        print("[INFO] Chart generated successfully")
        
        return jsonify({
            'success': True,
            'chart': f'data:image/png;base64,{img_base64}'
        })
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"[ERROR] Chart generation failed: {error_msg}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/api/environment-info')
def environment_info():
    algorithms = ['olb', 'lbs', 'lab', 'mec', 'fnpa']
    if PREDICTIVE_AVAILABLE:
        algorithms.insert(1, 'predictive')  # Insert after 'olb'
    
    return jsonify({
        'defaultSensors': 10,
        'defaultedgeNodes': 4,
        'maxSensors': 30,
        'maxedgeNodes': 10,
        'algorithms': algorithms,
        'predictiveAvailable': PREDICTIVE_AVAILABLE
    })

@app.route('/api/mqtt/status', methods=['GET'])
def mqtt_status():
    """Get MQTT broker status and statistics"""
    try:
        from src.mqtt_simulator import MQTTSimulationEnvironment
        
        # Create temporary MQTT environment to show capabilities
        mqtt_env = MQTTSimulationEnvironment()
        
        return jsonify({
            'success': True,
            'mqtt_enabled': True,
            'broker_info': {
                'type': 'Simulated MQTT Broker',
                'features': [
                    'Pub/Sub messaging',
                    'Topic wildcards (+ and #)',
                    'QoS levels (0, 1, 2)',
                    'Retained messages',
                    'Message history'
                ],
                'topics': [
                    'sensor/{sensor_id}/reading',
                    'placement/{algorithm}/summary',
                    'placement/sensor_{id}/assignment',
                    'simulation/lifecycle/start',
                    'simulation/lifecycle/end',
                    'simulation/metrics'
                ]
            },
            'statistics': mqtt_env.get_statistics()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mqtt/messages', methods=['GET'])
def mqtt_messages():
    """Get recent MQTT messages from last simulation"""
    try:
        import os
        import json
        from pathlib import Path
        
        # Try to read the most recent MQTT log
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return jsonify({
                'success': True,
                'messages': [],
                'note': 'No MQTT logs found. Run a simulation first.'
            })
        
        # Find most recent MQTT log file
        mqtt_logs = list(logs_dir.glob("*_mqtt_log.json"))
        if not mqtt_logs:
            return jsonify({
                'success': True,
                'messages': [],
                'note': 'No MQTT logs found. Run a simulation first.'
            })
        
        # Get most recent log
        latest_log = max(mqtt_logs, key=lambda p: p.stat().st_mtime)
        
        with open(latest_log, 'r') as f:
            log_data = json.load(f)
        
        # Return last 50 messages
        messages = log_data.get('messages', [])[-50:]
        
        return jsonify({
            'success': True,
            'log_file': str(latest_log),
            'total_messages': log_data.get('total_messages', 0),
            'simulation_time': log_data.get('simulation_time', 0),
            'broker_stats': log_data.get('broker_stats', {}),
            'recent_messages': messages
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test-algorithms', methods=['GET'])
def test_algorithms():
    """Test endpoint to verify algorithms produce different results"""
    try:
        print("[TEST] Testing algorithm differences...")
        
        # Create a simple test environment
        env = DigitalTwinEnvironment(3000, 2000)
        env.initialize_sensors(5, seed=42)
        env.initialize_edge_nodes(2, seed=42)
        env.initialize_cloud()
        
        app_obj = create_smart_healthcare_application(env)
        topology = create_yafs_topology(env)
        
        # Setup directories using orchestrator
        setup_directories(["config", "results"])
        config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
        placement_json = create_placement_json(config_dir)
        
        test_results = {}
        
        registry = get_registry()
        test_algorithms = ['OLB', 'LBS']
        if PREDICTIVE_AVAILABLE:
            test_algorithms.insert(1, 'Predictive')
        
        for alg_name in test_algorithms:
            alg_class = registry.get(alg_name)
            if alg_class is None:
                continue
            # Create fresh environment
            test_env = DigitalTwinEnvironment(3000, 2000)
            test_env.initialize_sensors(5, seed=42)
            test_env.initialize_edge_nodes(2, seed=42)
            test_env.initialize_cloud()
            
            test_app = create_smart_healthcare_application(test_env)
            test_topo = create_yafs_topology(test_env)
            
            if alg_name == 'Predictive':
                placement = alg_class(alg_name, placement_json, test_env, prediction_horizon=10)
            else:
                placement = alg_class(alg_name, placement_json, test_env)
            
            from yafs.core import Sim
            from yafs.population import Population
            
            # Results directory already created by setup_directories
            results_dir = os.path.join(os.path.dirname(__file__), "..", "results")
            
            s = Sim(test_topo, default_results_path=os.path.join(results_dir, f"test_{alg_name}"))
            pop = Population(name=f"Test_{alg_name}")
            s.deploy_app(test_app, placement, pop)
            s.run(until=PlacementConstants.DEFAULT_SIMULATION_TIME // 2)  # Half time for testing
            
            # Get assignment distribution
            distribution = {}
            for edge_id, sensors in placement.module_assignments.items():
                distribution[f"edge_{edge_id}"] = len(sensors)
            
            test_results[alg_name] = {
                'distribution': distribution,
                'total_assignments': sum(distribution.values())
            }
        
        return jsonify({
            'success': True,
            'test_results': test_results,
            'message': 'Check if distributions are different'
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
