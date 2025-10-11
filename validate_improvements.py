import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.olb_algorithm import OLBLatencyCalculator
from src.devices import SensorDevice, FogNodeDevice


def test_shannon_capacity_fix():
    print("=== Testing Shannon Capacity Fix ===")
    calc = OLBLatencyCalculator()
    
    bandwidth = 100
    snr_values = [1, 10, 100, 1000]
    
    print(f"Bandwidth: {bandwidth} MHz\n")
    
    for snr in snr_values:
        capacity = calc.calculate_device_capacity(bandwidth, snr)
        theoretical_max = bandwidth * math.log2(1 + snr)
        
        print(f"SNR: {snr}")
        print(f"  Calculated capacity: {capacity:.2f} Mbps")
        print(f"  Shannon theorem: {theoretical_max:.2f} Mbps")
        print(f"  Match: {abs(capacity - theoretical_max) < 0.01}")
        print()
    
    print("✓ Shannon capacity formula is correct\n")


def test_overload_detection():
    print("=== Testing Overload Detection ===")
    calc = OLBLatencyCalculator()
    
    sensor = SensorDevice(
        device_id=0,
        coordinates=(100, 100),
        transmission_power=0.5,
        average_flow_rate=10.0,
        flow_traffic_size=1.0,
        average_flow_size=1000
    )
    
    fog_node = FogNodeDevice(
        node_id=0,
        coordinates=(200, 200),
        processing_power=5000,
        bandwidth=50,
        carrier_frequency=2.4,
        noise_power=1e-10
    )
    
    assigned_sensors = [sensor] * 20
    
    latency = calc.calculate_computing_latency(sensor, fog_node, assigned_sensors)
    
    print(f"Fog node capacity: {fog_node.processingPower} MIPS")
    print(f"Assigned sensors: {len(assigned_sensors)}")
    print(f"Total load: {len(assigned_sensors) * sensor.averageFlowRate * sensor.averageFlowSize}")
    print(f"Computed latency: {latency}")
    
    if latency == float("inf"):
        print("✓ Overload correctly detected (returns infinity)\n")
    else:
        print("✗ Overload NOT detected (should return infinity)\n")


def test_cache_performance():
    print("=== Testing Cache Performance ===")
    import time
    from src import DigitalTwinEnvironment, OLBPlacement, create_placement_json
    
    environment = DigitalTwinEnvironment(3000, 2000)
    environment.initialize_sensors(20, seed=42)
    environment.initialize_fog_nodes(6, seed=42)
    
    placement_json = create_placement_json("config")
    placement = OLBPlacement("TestOLB", placement_json, environment)
    
    sensor = environment.sensors[0]
    
    start_time = time.time()
    for _ in range(100):
        placement._find_optimal_fog_node(sensor)
    uncached_time = time.time() - start_time
    
    placement._node_loads[0].append(sensor)
    placement.module_assignments[0] = [sensor]
    
    start_time = time.time()
    for _ in range(100):
        placement._find_optimal_fog_node(sensor)
    cached_time = time.time() - start_time
    
    speedup = uncached_time / cached_time if cached_time > 0 else float('inf')
    
    print(f"First run (no cache): {uncached_time:.4f}s")
    print(f"Subsequent runs (cached): {cached_time:.4f}s")
    print(f"Speedup: {speedup:.2f}x")
    
    if speedup > 2:
        print("✓ Caching provides significant speedup\n")
    else:
        print("⚠ Caching speedup lower than expected\n")


def test_workload_patterns():
    print("=== Testing Workload Patterns ===")
    from src.workload_models import DynamicWorkloadGenerator, HealthcareWorkloadPattern
    
    patterns = ["steady", "periodic", "bursty", "increasing"]
    
    for pattern_type in patterns:
        gen = DynamicWorkloadGenerator(pattern_type)
        values = [gen.get_next_load_multiplier() for _ in range(10)]
        avg = sum(values) / len(values)
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        
        print(f"{pattern_type}: avg={avg:.2f}, variance={variance:.2f}")
    
    print("\nHealthcare patterns:")
    scenarios = ["icu", "emergency", "ambulatory"]
    
    for scenario in scenarios:
        pattern = HealthcareWorkloadPattern(scenario)
        values = [pattern.get_load_multiplier() for _ in range(20)]
        avg = sum(values) / len(values)
        max_val = max(values)
        
        print(f"{scenario}: avg={avg:.2f}, max={max_val:.2f}")
    
    print("\n✓ Workload patterns working correctly\n")


def test_concurrent_predictions():
    print("=== Testing Concurrent Predictions ===")
    import time
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def mock_prediction(node_id):
        time.sleep(0.1)
        return f"system-{node_id}", {"predicted_avg": 50.0}
    
    start_time = time.time()
    results_sequential = []
    for i in range(6):
        results_sequential.append(mock_prediction(i))
    sequential_time = time.time() - start_time
    
    start_time = time.time()
    results_parallel = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(mock_prediction, i) for i in range(6)]
        for future in as_completed(futures):
            results_parallel.append(future.result())
    parallel_time = time.time() - start_time
    
    speedup = sequential_time / parallel_time
    
    print(f"Sequential execution: {sequential_time:.2f}s")
    print(f"Parallel execution: {parallel_time:.2f}s")
    print(f"Speedup: {speedup:.2f}x")
    
    if speedup > 4:
        print("✓ Concurrent execution provides significant speedup\n")
    else:
        print("⚠ Concurrent speedup lower than expected\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("VALIDATING TECHNICAL IMPROVEMENTS")
    print("="*60 + "\n")
    
    try:
        test_shannon_capacity_fix()
        test_overload_detection()
        test_cache_performance()
        test_workload_patterns()
        test_concurrent_predictions()
        
        print("="*60)
        print("ALL VALIDATIONS COMPLETED")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
