import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src import (
    DigitalTwinEnvironment,
    OLBPlacement,
    PredictiveLatencyPlacement,
    ForecastBasedPlacement,
    PatternBasedWorkloadGenerator,
    PerformanceMetrics,
    create_placement_json,
    create_smart_healthcare_application,
    create_yafs_topology,
)


def run_quick_demo():
    print("\n" + "="*70)
    print("PREDICTIVE PLACEMENT QUICK DEMO")
    print("="*70 + "\n")
    
    print("Setting up environment...")
    environment = DigitalTwinEnvironment(3000, 2000)
    environment.initialize_sensors(10, seed=42)
    environment.initialize_fog_nodes(6, seed=42)
    environment.initialize_cloud()
    
    print(f"Created: {len(environment.sensors)} sensors, {len(environment.fog_nodes)} fog nodes\n")
    
    workload_gen = PatternBasedWorkloadGenerator("periodic")
    print("Generating periodic workload pattern...")
    for _ in range(10):
        multiplier = workload_gen.get_current_multiplier()
    print(f"Current load multiplier: {multiplier:.2f}\n")
    
    future_forecast = workload_gen.forecast_future_multipliers(10)
    print(f"Forecasted next 10 steps: {[f'{x:.2f}' for x in future_forecast[:5]]}...\n")
    
    app = create_smart_healthcare_application(environment)
    topology = create_yafs_topology(environment)
    placement_json = create_placement_json("config")
    
    algorithms = [
        ("Reactive OLB", OLBPlacement("ReactiveOLB", placement_json, environment)),
        ("Predictive Latency", PredictiveLatencyPlacement("PredictiveOLB", placement_json, environment, prediction_horizon=10)),
        ("Forecast Based", ForecastBasedPlacement("ForecastOLB", placement_json, environment, workload_gen)),
    ]
    
    results = {}
    
    for algo_name, placement in algorithms:
        print(f"\n{'='*70}")
        print(f"Running: {algo_name}")
        print(f"{'='*70}")
        
        try:
            from yafs.core import Sim
            from yafs.population import Population
            
            s = Sim(topology, default_results_path="results/")
            population = Population(name=f"{algo_name}Demo")
            s.deploy_app(app, placement, population)
            s.run(until=500)
            
            metrics = PerformanceMetrics()
            metrics.collect_metrics(environment, placement, algo_name)
            
            result = metrics.get_summary_dict()
            results[algo_name] = result
            
            print(f"\nResults:")
            print(f"  Overall Latency: {result['overall_latency']:.4f} ms")
            print(f"  Energy Consumption: {result['energy_consumption']:.4f} W")
            print(f"  Load Balance Score: {result['load_balance_score']:.4f}")
            print(f"  Network Usage: {result['network_usage']:.4f} MB/s")
            
        except Exception as e:
            print(f"Failed: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n\n{'='*70}")
    print("COMPARISON SUMMARY")
    print(f"{'='*70}\n")
    
    if len(results) >= 2:
        reactive_latency = results.get("Reactive OLB", {}).get("overall_latency", 0)
        
        for algo_name, result in results.items():
            if algo_name != "Reactive OLB" and reactive_latency > 0:
                improvement = ((reactive_latency - result['overall_latency']) / reactive_latency) * 100
                print(f"{algo_name}:")
                print(f"  Latency: {result['overall_latency']:.4f} ms")
                print(f"  Improvement vs Reactive: {improvement:+.2f}%")
                
                if improvement > 0:
                    print(f"  ✓ {algo_name} is {improvement:.1f}% better")
                else:
                    print(f"  ✗ Reactive is {abs(improvement):.1f}% better")
                print()
    
    print(f"{'='*70}")
    print("DEMO COMPLETED")
    print(f"{'='*70}\n")
    
    print("Next steps:")
    print("1. Run full comparison: python experiments/predictive_vs_reactive_comparison.py")
    print("2. Validate implementation: python validate_predictive_placement.py")
    print("3. Read guide: PREDICTIVE_PLACEMENT_GUIDE.md")


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    run_quick_demo()
