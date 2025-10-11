class PerformanceMetrics:
    def __init__(self):
        self.overall_latency = 0.0
        self.communication_latency = 0.0
        self.computing_latency = 0.0
        self.energy_consumption = 0.0
        self.network_usage = 0.0
        self.cost_of_execution = 0.0
        self.load_balance_score = 0.0
        self.detailed_assignments = []

    def collect_metrics(self, environment, placement, algorithm_name):
        total_comm_latency = 0.0
        total_comp_latency = 0.0
        total_energy = 0.0
        
        from .olb_algorithm import OLBLatencyCalculator
        calculator = OLBLatencyCalculator()
        
        for fog_node_id, sensors in placement.module_assignments.items():
            fog_node = environment.fog_nodes[fog_node_id]
            
            for sensor in sensors:
                assigned_sensors = [s for s in sensors if s != sensor]
                
                comm_latency = calculator.calculate_communication_latency(sensor, fog_node, assigned_sensors)
                comp_latency = calculator.calculate_computing_latency(sensor, fog_node, assigned_sensors)
                
                if comm_latency != float("inf") and comp_latency != float("inf"):
                    total_comm_latency += comm_latency
                    total_comp_latency += comp_latency
                    
                    energy = sensor.transmissionPower * sensor.flowTrafficSize
                    total_energy += energy
                    
                    self.detailed_assignments.append({
                        'sensor_id': sensor.device_id,
                        'fog_node_id': fog_node_id,
                        'comm_latency': comm_latency,
                        'comp_latency': comp_latency,
                        'total_latency': comm_latency + comp_latency,
                        'energy': energy
                    })
        
        self.overall_latency = total_comm_latency + total_comp_latency
        self.communication_latency = total_comm_latency
        self.computing_latency = total_comp_latency
        self.energy_consumption = total_energy
        
        total_sensors = sum(len(sensors) for sensors in placement.module_assignments.values())
        if total_sensors > 0:
            self.network_usage = total_energy / total_sensors
        
        loads = [len(sensors) for sensors in placement.module_assignments.values()]
        if len(loads) > 1:
            mean_load = sum(loads) / len(loads)
            variance = sum((load - mean_load) ** 2 for load in loads) / len(loads)
            self.load_balance_score = 1.0 / (1.0 + variance)
        else:
            self.load_balance_score = 1.0
        
        self.cost_of_execution = self.overall_latency + self.energy_consumption + self.network_usage

    def get_summary_dict(self):
        return {
            'overall_latency': self.overall_latency,
            'communication_latency': self.communication_latency,
            'computing_latency': self.computing_latency,
            'energy_consumption': self.energy_consumption,
            'network_usage': self.network_usage,
            'cost_of_execution': self.cost_of_execution,
            'load_balance_score': self.load_balance_score,
            'detailed_assignments': self.detailed_assignments
        }

    def generate_report(self):
        report = []
        report.append("="*80)
        report.append("PERFORMANCE METRICS REPORT")
        report.append("="*80)
        report.append("")
        report.append(f"Overall Latency: {self.overall_latency:.4f} ms")
        report.append(f"  Communication Latency: {self.communication_latency:.4f} ms")
        report.append(f"  Computing Latency: {self.computing_latency:.4f} ms")
        report.append("")
        report.append(f"Energy Consumption: {self.energy_consumption:.4f} W")
        report.append(f"Network Usage: {self.network_usage:.4f} MB/s")
        report.append(f"Cost of Execution: {self.cost_of_execution:.4f}")
        report.append(f"Load Balance Score: {self.load_balance_score:.4f}")
        report.append("")
        report.append(f"Total Assignments: {len(self.detailed_assignments)}")
        report.append("")
        return "\n".join(report)
