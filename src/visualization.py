import json
import os
import statistics

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import Dict, List, Any


class SimulationVisualizer:
    """Visualization tools for OLB simulation results"""

    def __init__(self):
        self.colors = ["red", "blue", "green", "orange", "purple", "brown"]

    def plot_environment(
        self, digital_twin, placement, algorithm_name="OLB", save_path=None
    ):
        """Plot the digital twin environment with assignments"""
        if save_path is None:
            save_path = f"environment_{algorithm_name.lower()}.png"

        plt.figure(figsize=(12, 8))

        # Plot edge nodes
        for i, edge_node in enumerate(digital_twin.edge_nodes):
            plt.scatter(
                edge_node.coordinates[0],
                edge_node.coordinates[1],
                c=self.colors[i % len(self.colors)],
                s=200,
                marker="s",
                label=f"edge Node {i}",
                alpha=0.7,
                edgecolors="black",
            )

        # Plot sensors with assignment colors
        for node_id, sensors in placement.module_assignments.items():
            for sensor in sensors:
                plt.scatter(
                    sensor.coordinates[0],
                    sensor.coordinates[1],
                    c=self.colors[node_id % len(self.colors)],
                    s=100,
                    marker="o",
                    alpha=0.8,
                )
                # Draw connection line
                edge_node = digital_twin.edge_nodes[node_id]
                plt.plot(
                    [sensor.coordinates[0], edge_node.coordinates[0]],
                    [sensor.coordinates[1], edge_node.coordinates[1]],
                    c=self.colors[node_id % len(self.colors)],
                    alpha=0.3,
                    linewidth=1,
                )

        plt.xlabel("X Coordinate (units)")
        plt.ylabel("Y Coordinate (units)")
        plt.title(f"{algorithm_name} Algorithm - Sensor-edge Node Assignments")
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Environment plot saved: {save_path}")
        return save_path

    def plot_performance_comparison(
        self, results_dict, save_path="performance_comparison.png"
    ):
        """Compare performance metrics across algorithms"""
        # Define clean labels mapping
        label_mapping = {
            "OLB": "OLB",
            "LBS": "Location-Based",
            "LAB": "Load-Aware",
            "MEC": "Multi-Edge",
            "FNPA": "FNPA",
        }

        algorithms = list(results_dict.keys())
        clean_labels = [label_mapping.get(algo, algo) for algo in algorithms]
        metrics = ["overall_latency", "energy_consumption", "load_balance_score"]
        metric_labels = [
            "Overall Latency (ms)",
            "Energy Consumption (W)",
            "Load Balance Score",
        ]

        # Print debugging information
        print("\nPlotting metrics for algorithms:", clean_labels)
        print("Looking for metrics:", metrics)

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

        for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
            values = [results_dict[alg][metric] for alg in algorithms]
            bars = axes[i].bar(clean_labels, values, color=colors[: len(algorithms)])
            axes[i].set_title(label)
            axes[i].set_ylabel("Value")
            axes[i].tick_params(axis="x", rotation=45)

            # Add value labels on bars
            for bar, value in zip(bars, values):
                axes[i].text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(values) * 0.01,
                    f"{value:.3f}",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                )

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Performance comparison saved: {save_path}")
        return save_path

    def plot_latency_distribution(self, metrics, save_path="latency_distribution.png"):
        assignments = metrics.detailed_assignments

        if not assignments:
            print("No assignments to plot")
            return save_path

        comm_latencies = [a["comm_latency"] for a in assignments]
        comp_latencies = [a["comp_latency"] for a in assignments]

        plt.figure(figsize=(10, 6))
        x = range(len(assignments))
        width = 0.35

        plt.bar(
            [i - width / 2 for i in x],
            comm_latencies,
            width,
            label="Communication Latency",
            alpha=0.8,
        )
        plt.bar(
            [i + width / 2 for i in x],
            comp_latencies,
            width,
            label="Computing Latency",
            alpha=0.8,
        )

        plt.xlabel("Sensor ID")
        plt.ylabel("Latency")
        plt.title("Latency Distribution Across Sensors")
        plt.legend()
        plt.xticks(x, [f"S{a['sensor_id']}" for a in assignments])
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Latency distribution plot saved: {save_path}")
        return save_path


class HospitalVisualizationEngine:
    """Generates visualizations from hospital comparison results"""
    
    def __init__(self, results: Dict, output_dir: str = "plots"):
        self.results = results
        self.output_dir = output_dir
        self.metrics = self._extract_metrics()
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def _extract_metrics(self) -> List[Dict]:
        """Extract all metrics from results"""
        metrics = []
        for scenario in self.results.get('scenarios', []):
            for result in scenario.get('results', []):
                metric = result.copy()
                metric['scenario_name'] = scenario['scenario_name']
                metrics.append(metric)
        return metrics
    
    def generate_all_visualizations(self):
        """Generate all visualization types"""
        self._create_algorithm_comparison_charts()
        self._create_scenario_timelines()
        self._create_distribution_boxplot()
        self._create_node_utilization_heatmap()
        print(f"[OK] All visualizations generated in {self.output_dir}/")
    
    def _create_algorithm_comparison_charts(self):
        """Create 4 algorithm comparison bar charts"""
        algorithms = self.results.get('algorithms', [])
        
        # Chart 1: Latency Comparison
        fig, ax = plt.subplots(figsize=(12, 6))
        latencies = [m['latency_avg'] for m in self.metrics if m['algorithm_name'] in algorithms]
        algo_names = [m['algorithm_name'] for m in self.metrics if m['algorithm_name'] in algorithms]
        
        bars = ax.bar(algorithms, 
                     [statistics.mean([m['latency_avg'] for m in self.metrics if m['algorithm_name'] == a]) 
                      for a in algorithms],
                     color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
        ax.set_ylabel('Latency (ms)', fontsize=12)
        ax.set_title('Algorithm Comparison: Average Latency', fontsize=14, fontweight='bold')
        ax.set_ylim(bottom=0)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}', ha='center', va='bottom', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'comparison_latency.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Chart 2: Energy Consumption
        fig, ax = plt.subplots(figsize=(12, 6))
        energies = [statistics.mean([m['energy_consumption'] for m in self.metrics if m['algorithm_name'] == a]) 
                   for a in algorithms]
        bars = ax.bar(algorithms, energies,
                     color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
        ax.set_ylabel('Energy (J)', fontsize=12)
        ax.set_title('Algorithm Comparison: Energy Consumption', fontsize=14, fontweight='bold')
        ax.set_ylim(bottom=0)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}', ha='center', va='bottom', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'comparison_energy.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Chart 3: Load Balance Score
        fig, ax = plt.subplots(figsize=(12, 6))
        loads = [statistics.mean([m['load_balance_score'] for m in self.metrics if m['algorithm_name'] == a]) 
                for a in algorithms]
        bars = ax.bar(algorithms, loads,
                     color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
        ax.set_ylabel('Load Balance Score', fontsize=12)
        ax.set_title('Algorithm Comparison: Load Balance', fontsize=14, fontweight='bold')
        ax.set_ylim(bottom=0)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}', ha='center', va='bottom', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'comparison_load_balance.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Chart 4: SLA Compliance
        fig, ax = plt.subplots(figsize=(12, 6))
        slas = [statistics.mean([m['sla_compliance_percent'] for m in self.metrics if m['algorithm_name'] == a]) 
               for a in algorithms]
        bars = ax.bar(algorithms, slas,
                     color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
        ax.set_ylabel('SLA Compliance (%)', fontsize=12)
        ax.set_title('Algorithm Comparison: SLA Compliance', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 105)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'comparison_sla_compliance.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_scenario_timelines(self):
        """Create line charts for each scenario"""
        scenarios_list = list(set([m['scenario_name'] for m in self.metrics]))
        algorithms = self.results.get('algorithms', [])
        
        for scenario in scenarios_list:
            fig, ax = plt.subplots(figsize=(12, 6))
            scenario_metrics = [m for m in self.metrics if m['scenario_name'] == scenario]
            
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            for i, algo in enumerate(algorithms):
                algo_latencies = [m['latency_avg'] for m in scenario_metrics if m['algorithm_name'] == algo]
                if algo_latencies:
                    ax.plot(range(len(algo_latencies)), algo_latencies, marker='o', label=algo, 
                           color=colors[i % len(colors)], linewidth=2, markersize=8)
            
            ax.set_xlabel('Iteration', fontsize=12)
            ax.set_ylabel('Latency (ms)', fontsize=12)
            ax.set_title(f'Latency Timeline: {scenario}', fontsize=14, fontweight='bold')
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            
            filename = f"hospital_{scenario.lower().replace(' ', '_')}_latency_timeline.png"
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')
            plt.close()
    
    def _create_distribution_boxplot(self):
        """Create box plot for latency distribution"""
        fig, ax = plt.subplots(figsize=(12, 6))
        algorithms = self.results.get('algorithms', [])
        
        data_by_algo = []
        for algo in algorithms:
            latencies = [m['latency_avg'] for m in self.metrics if m['algorithm_name'] == algo]
            data_by_algo.append(latencies)
        
        bp = ax.boxplot(data_by_algo, labels=algorithms, patch_artist=True)
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_ylabel('Latency (ms)', fontsize=12)
        ax.set_title('Latency Distribution by Algorithm', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'latency_distribution_boxplot.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_node_utilization_heatmap(self):
        """Create heatmap for node utilization"""
        fig, ax = plt.subplots(figsize=(12, 6))
        algorithms = self.results.get('algorithms', [])
        scenarios_list = list(set([m['scenario_name'] for m in self.metrics]))
        
        # Create matrix: algorithms x scenarios
        data = []
        for algo in algorithms:
            row = []
            for scenario in scenarios_list:
                cpu_util = statistics.mean([m['cpu_utilization_percent'] for m in self.metrics 
                                          if m['algorithm_name'] == algo and m['scenario_name'] == scenario])
                row.append(cpu_util)
            data.append(row)
        
        im = ax.imshow(data, cmap='YlOrRd', aspect='auto')
        ax.set_xticks(range(len(scenarios_list)))
        ax.set_yticks(range(len(algorithms)))
        ax.set_xticklabels(scenarios_list, rotation=45, ha='right')
        ax.set_yticklabels(algorithms)
        ax.set_title('Node Utilization Heatmap (CPU %)', fontsize=14, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('CPU Utilization (%)', rotation=270, labelpad=15)
        
        # Add text annotations
        for i in range(len(algorithms)):
            for j in range(len(scenarios_list)):
                text = ax.text(j, i, f'{data[i][j]:.1f}%',
                             ha="center", va="center", color="black", fontsize=10)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'node_utilization_heatmap.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def get_performance_summary(self) -> Dict:
        """Generate performance summary"""
        algorithms = self.results.get('algorithms', [])
        summary = {}
        
        for algo in algorithms:
            algo_metrics = [m for m in self.metrics if m['algorithm_name'] == algo]
            if algo_metrics:
                summary[algo] = {
                    "Avg Latency": f"{statistics.mean([m['latency_avg'] for m in algo_metrics]):.2f}ms",
                    "Energy": f"{statistics.mean([m['energy_consumption'] for m in algo_metrics]):.4f}J",
                    "Load Balance": f"{statistics.mean([m['load_balance_score'] for m in algo_metrics]):.1f}",
                    "SLA Compliance": f"{statistics.mean([m['sla_compliance_percent'] for m in algo_metrics]):.1f}%"
                }
        
        return summary
