import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src import (
    DigitalTwinEnvironment,
    OLBPlacement,
    PredictiveLatencyPlacement,
    ForecastBasedPlacement,
    PatternBasedWorkloadGenerator,
    HealthcareWorkloadForecaster,
    PerformanceMetrics,
    SimulationVisualizer,
    create_placement_json,
    create_smart_healthcare_application,
    create_yafs_topology,
)


class PipelineDemo:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {}
        self.visualizer = SimulationVisualizer()
        
        os.makedirs("results", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        os.makedirs("plots", exist_ok=True)
        os.makedirs("config", exist_ok=True)

    def print_header(self, text):
        print("\n" + "="*80)
        print(f"  {text}")
        print("="*80 + "\n")

    def print_step(self, step_num, text):
        print(f"\n[STEP {step_num}] {text}")
        print("-" * 80)

    def step1_create_environment(self):
        self.print_step(1, "Creating Digital Twin Environment")
        
        self.environment = DigitalTwinEnvironment(3000, 2000)
        self.environment.initialize_sensors(15, seed=42)
        self.environment.initialize_fog_nodes(6, seed=42)
        self.environment.initialize_cloud()
        
        print(f"[OK] Environment created: {self.environment.width}x{self.environment.height}")
        print(f"[OK] Sensors: {len(self.environment.sensors)}")
        print(f"[OK] Fog nodes: {len(self.environment.fog_nodes)}")
        print(f"[OK] Cloud node: {self.environment.cloud_node is not None}")
        
        summary = self.environment.get_summary()
        with open(f"data/environment_{self.timestamp}.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        return True

    def step2_generate_workload_patterns(self):
        self.print_step(2, "Generating Workload Patterns")
        
        self.workload_patterns = {
            "steady": PatternBasedWorkloadGenerator("steady"),
            "periodic": PatternBasedWorkloadGenerator("periodic"),
            "bursty": PatternBasedWorkloadGenerator("bursty"),
            "increasing": PatternBasedWorkloadGenerator("increasing"),
        }
        
        pattern_data = {}
        for name, generator in self.workload_patterns.items():
            history = [generator.get_current_multiplier() for _ in range(50)]
            forecast = generator.forecast_future_multipliers(10)
            
            pattern_data[name] = {
                "history": history,
                "forecast": forecast,
                "mean": sum(history) / len(history),
                "forecast_mean": sum(forecast) / len(forecast)
            }
            
            print(f"[OK] {name}: mean={pattern_data[name]['mean']:.2f}, forecast={pattern_data[name]['forecast_mean']:.2f}")
        
        with open(f"data/workload_patterns_{self.timestamp}.json", "w") as f:
            json.dump(pattern_data, f, indent=2, default=str)
        
        return True

    def step3_run_reactive_olb(self):
        self.print_step(3, "Running Reactive OLB (Baseline)")
        
        environment = DigitalTwinEnvironment(3000, 2000)
        environment.initialize_sensors(15, seed=42)
        environment.initialize_fog_nodes(6, seed=42)
        environment.initialize_cloud()
        
        app = create_smart_healthcare_application(environment)
        topology = create_yafs_topology(environment)
        placement_json = create_placement_json("config")
        
        placement = OLBPlacement("ReactiveOLB", placement_json, environment)
        
        try:
            from yafs.core import Sim
            from yafs.population import Population
            
            s = Sim(topology, default_results_path="results/")
            population = Population(name="ReactiveDemo")
            s.deploy_app(app, placement, population)
            s.run(until=500)
            
            metrics = PerformanceMetrics()
            metrics.collect_metrics(environment, placement, "ReactiveOLB")
            
            result = metrics.get_summary_dict()
            self.results["reactive_olb"] = result
            
            print(f"[OK] Latency: {result['overall_latency']:.4f} ms")
            print(f"[OK] Energy: {result['energy_consumption']:.4f} W")
            print(f"[OK] Load Balance: {result['load_balance_score']:.4f}")
            
            self.visualizer.plot_environment(
                environment, 
                placement, 
                "Reactive OLB",
                f"plots/reactive_olb_{self.timestamp}.png"
            )
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed: {e}")
            return False

    def step4_run_predictive_latency(self):
        self.print_step(4, "Running Predictive Latency Placement")
        
        environment = DigitalTwinEnvironment(3000, 2000)
        environment.initialize_sensors(15, seed=42)
        environment.initialize_fog_nodes(6, seed=42)
        environment.initialize_cloud()
        
        app = create_smart_healthcare_application(environment)
        topology = create_yafs_topology(environment)
        placement_json = create_placement_json("config")
        
        placement = PredictiveLatencyPlacement(
            "PredictiveOLB",
            placement_json,
            environment,
            prediction_horizon=10
        )
        
        try:
            from yafs.core import Sim
            from yafs.population import Population
            
            s = Sim(topology, default_results_path="results/")
            population = Population(name="PredictiveDemo")
            s.deploy_app(app, placement, population)
            s.run(until=500)
            
            metrics = PerformanceMetrics()
            metrics.collect_metrics(environment, placement, "PredictiveOLB")
            
            result = metrics.get_summary_dict()
            self.results["predictive_latency"] = result
            
            print(f"[OK] Latency: {result['overall_latency']:.4f} ms")
            print(f"[OK] Energy: {result['energy_consumption']:.4f} W")
            print(f"[OK] Load Balance: {result['load_balance_score']:.4f}")
            
            if "reactive_olb" in self.results:
                improvement = ((self.results["reactive_olb"]["overall_latency"] - result["overall_latency"]) / 
                              self.results["reactive_olb"]["overall_latency"]) * 100
                print(f"[OK] Improvement vs Reactive: {improvement:+.2f}%")
            
            self.visualizer.plot_environment(
                environment,
                placement,
                "Predictive Latency",
                f"plots/predictive_latency_{self.timestamp}.png"
            )
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed: {e}")
            return False

    def step5_run_forecast_based(self):
        self.print_step(5, "Running Forecast-Based Placement (Periodic Pattern)")
        
        environment = DigitalTwinEnvironment(3000, 2000)
        environment.initialize_sensors(15, seed=42)
        environment.initialize_fog_nodes(6, seed=42)
        environment.initialize_cloud()
        
        workload_gen = PatternBasedWorkloadGenerator("periodic")
        for _ in range(10):
            workload_gen.get_current_multiplier()
        
        app = create_smart_healthcare_application(environment)
        topology = create_yafs_topology(environment)
        placement_json = create_placement_json("config")
        
        placement = ForecastBasedPlacement(
            "ForecastOLB",
            placement_json,
            environment,
            workload_gen
        )
        
        try:
            from yafs.core import Sim
            from yafs.population import Population
            
            s = Sim(topology, default_results_path="results/")
            population = Population(name="ForecastDemo")
            s.deploy_app(app, placement, population)
            s.run(until=500)
            
            metrics = PerformanceMetrics()
            metrics.collect_metrics(environment, placement, "ForecastOLB")
            
            result = metrics.get_summary_dict()
            self.results["forecast_based"] = result
            
            print(f"[OK] Latency: {result['overall_latency']:.4f} ms")
            print(f"[OK] Energy: {result['energy_consumption']:.4f} W")
            print(f"[OK] Load Balance: {result['load_balance_score']:.4f}")
            
            if "reactive_olb" in self.results:
                improvement = ((self.results["reactive_olb"]["overall_latency"] - result["overall_latency"]) / 
                              self.results["reactive_olb"]["overall_latency"]) * 100
                print(f"[OK] Improvement vs Reactive: {improvement:+.2f}%")
            
            self.visualizer.plot_environment(
                environment,
                placement,
                "Forecast-Based",
                f"plots/forecast_based_{self.timestamp}.png"
            )
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed: {e}")
            return False

    def step6_compare_results(self):
        self.print_step(6, "Comparing All Algorithms")
        
        if len(self.results) < 2:
            print("[ERROR] Not enough results to compare")
            return False
        
        print("\nComparison Table:")
        print("-" * 80)
        print(f"{'Algorithm':<25} {'Latency (ms)':<15} {'Energy (W)':<15} {'Load Balance':<15}")
        print("-" * 80)
        
        for algo_name, result in self.results.items():
            print(f"{algo_name:<25} {result['overall_latency']:<15.4f} "
                  f"{result['energy_consumption']:<15.4f} {result['load_balance_score']:<15.4f}")
        
        print("-" * 80)
        
        if "reactive_olb" in self.results:
            baseline = self.results["reactive_olb"]["overall_latency"]
            print("\nImprovement vs Reactive OLB:")
            for algo_name, result in self.results.items():
                if algo_name != "reactive_olb":
                    improvement = ((baseline - result["overall_latency"]) / baseline) * 100
                    status = "[+]" if improvement > 0 else "[-]"
                    print(f"  {status} {algo_name}: {improvement:+.2f}%")
        
        try:
            self.visualizer.plot_performance_comparison(
                self.results,
                f"plots/comparison_{self.timestamp}.png"
            )
            print(f"\n[OK] Comparison plot saved: plots/comparison_{self.timestamp}.png")
        except Exception as e:
            print(f"[ERROR] Failed to create comparison plot: {e}")
        
        return True

    def step7_generate_report(self):
        self.print_step(7, "Generating Final Report")
        
        report_path = f"reports/pipeline_report_{self.timestamp}.txt"
        
        with open(report_path, "w") as f:
            f.write("="*80 + "\n")
            f.write("PREDICTIVE PLACEMENT PIPELINE DEMONSTRATION REPORT\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Timestamp: {self.timestamp}\n")
            f.write(f"Environment: {self.environment.width}x{self.environment.height}\n")
            f.write(f"Sensors: {len(self.environment.sensors)}\n")
            f.write(f"Fog Nodes: {len(self.environment.fog_nodes)}\n\n")
            
            f.write("="*80 + "\n")
            f.write("ALGORITHM RESULTS\n")
            f.write("="*80 + "\n\n")
            
            for algo_name, result in self.results.items():
                f.write(f"{algo_name.upper()}\n")
                f.write("-" * 80 + "\n")
                f.write(f"Overall Latency: {result['overall_latency']:.4f} ms\n")
                f.write(f"Energy Consumption: {result['energy_consumption']:.4f} W\n")
                f.write(f"Load Balance Score: {result['load_balance_score']:.4f}\n")
                f.write(f"Network Usage: {result['network_usage']:.4f} MB/s\n")
                f.write(f"Cost of Execution: {result['cost_of_execution']:.4f}\n\n")
            
            if "reactive_olb" in self.results:
                f.write("="*80 + "\n")
                f.write("IMPROVEMENT ANALYSIS\n")
                f.write("="*80 + "\n\n")
                
                baseline = self.results["reactive_olb"]["overall_latency"]
                
                for algo_name, result in self.results.items():
                    if algo_name != "reactive_olb":
                        improvement = ((baseline - result["overall_latency"]) / baseline) * 100
                        f.write(f"{algo_name}:\n")
                        f.write(f"  Latency Improvement: {improvement:+.2f}%\n")
                        
                        if improvement > 0:
                            f.write(f"  Status: BETTER than reactive\n")
                        else:
                            f.write(f"  Status: WORSE than reactive\n")
                        f.write("\n")
            
            f.write("="*80 + "\n")
            f.write("KEY FINDINGS\n")
            f.write("="*80 + "\n\n")
            
            f.write("1. PREDICTIVE PLACEMENT EFFECTIVENESS:\n")
            f.write("   - Predictive algorithms anticipate future workload changes\n")
            f.write("   - Most effective for trending and periodic patterns\n")
            f.write("   - Proactive placement reduces overload situations\n\n")
            
            f.write("2. LATENCY-BASED FORECASTING:\n")
            f.write("   - Uses historical trends to predict future latency\n")
            f.write("   - Considers both sensor load and fog utilization\n")
            f.write("   - Better load distribution across fog nodes\n\n")
            
            f.write("3. PATTERN-BASED FORECASTING:\n")
            f.write("   - Exploits known workload patterns\n")
            f.write("   - Effective for periodic and predictable workloads\n")
            f.write("   - Pattern-specific optimization strategies\n\n")
            
            f.write("="*80 + "\n")
            f.write("OUTPUT FILES\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Environment: data/environment_{self.timestamp}.json\n")
            f.write(f"Workload Patterns: data/workload_patterns_{self.timestamp}.json\n")
            f.write(f"Results: data/pipeline_results_{self.timestamp}.json\n")
            f.write(f"Report: {report_path}\n\n")
            
            f.write("Plots:\n")
            f.write(f"  - plots/reactive_olb_{self.timestamp}.png\n")
            f.write(f"  - plots/predictive_latency_{self.timestamp}.png\n")
            f.write(f"  - plots/forecast_based_{self.timestamp}.png\n")
            f.write(f"  - plots/comparison_{self.timestamp}.png\n\n")
        
        with open(f"data/pipeline_results_{self.timestamp}.json", "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"[OK] Report saved: {report_path}")
        print(f"[OK] Results saved: data/pipeline_results_{self.timestamp}.json")
        
        return True

    def run_pipeline(self):
        self.print_header("PREDICTIVE PLACEMENT PIPELINE DEMONSTRATION")
        
        print("This pipeline demonstrates the complete workflow:")
        print("1. Environment creation")
        print("2. Workload pattern generation")
        print("3. Reactive OLB (baseline)")
        print("4. Predictive Latency placement")
        print("5. Forecast-Based placement")
        print("6. Results comparison")
        print("7. Report generation")
        
        steps = [
            self.step1_create_environment,
            self.step2_generate_workload_patterns,
            self.step3_run_reactive_olb,
            self.step4_run_predictive_latency,
            self.step5_run_forecast_based,
            self.step6_compare_results,
            self.step7_generate_report,
        ]
        
        for step_func in steps:
            try:
                success = step_func()
                if not success:
                    print(f"\n[WARN] Step failed but continuing...")
            except Exception as e:
                print(f"\n[ERROR] Step failed with error: {e}")
                import traceback
                traceback.print_exc()
        
        self.print_header("PIPELINE COMPLETED")
        
        print("\nSummary:")
        print(f"  Algorithms tested: {len(self.results)}")
        print(f"  Timestamp: {self.timestamp}")
        print(f"\nOutput locations:")
        print(f"  Data: data/")
        print(f"  Reports: reports/")
        print(f"  Plots: plots/")
        
        if "reactive_olb" in self.results and "predictive_latency" in self.results:
            baseline = self.results["reactive_olb"]["overall_latency"]
            predictive = self.results["predictive_latency"]["overall_latency"]
            improvement = ((baseline - predictive) / baseline) * 100
            
            print(f"\nKey Result:")
            print(f"  Predictive Latency vs Reactive OLB: {improvement:+.2f}% latency change")
        
        print("\nNext steps:")
        print("  - Review plots in plots/ directory")
        print(f"  - Read report: reports/pipeline_report_{self.timestamp}.txt")
        print("  - Run full comparison: python experiments/predictive_vs_reactive_comparison.py")


if __name__ == "__main__":
    pipeline = PipelineDemo()
    pipeline.run_pipeline()
