from .olb_algorithm import OLBLatencyCalculator
import logging
import os
from datetime import datetime


class MetricsDefinitions:
    """
    Standardized metrics definitions for fair algorithm comparison
    """

    @staticmethod
    def get_metrics_documentation():
        return {
            "latency_metrics": {
                "overall_latency": "Sum of communication and computing latencies across all sensors (ms)",
                "communication_latency": "Network transmission delays based on distance and SNR (ms)",
                "computing_latency": "Processing delays based on edge node CPU utilization (ms)",
                "average_latency": "Mean latency per sensor assignment (ms)",
            },
            "energy_metrics": {
                "total_energy": "Sum of transmission and processing energy consumption (W)",
                "transmission_energy": "Energy used for wireless communication (W)",
                "processing_energy": "Energy used for computation at edge nodes (W)",
            },
            "cost_metrics": {
                "execution_cost": "Weighted combination of latency, energy, and network usage",
                "network_usage": "Total data transmission volume (MB/s)",
                "resource_utilization": "Average edge node CPU/memory utilization (%)",
            },
            "load_balance_metrics": {
                "load_variance": "Variance in edge node utilization levels",
                "max_utilization": "Highest edge node utilization percentage",
                "assignment_distribution": "Number of sensors per edge node",
            },
        }

    @staticmethod
    def calculate_energy_consumption(sensor, edge_node, distance):
        """Calculate energy consumption for sensor-edge assignment"""
        # Transmission energy: P_tx * t_tx
        transmission_time = sensor.flowTrafficSize / (
            edge_node.bandwidth * 1e-3
        )  # Convert MB to seconds
        transmission_energy = sensor.transmissionPower * transmission_time

        # Processing energy: P_cpu * t_proc
        processing_time = (
            sensor.averageFlowSize / edge_node.processingPower * 1e-3
        )  # Convert MI to seconds
        processing_energy = (
            edge_node.processingPower * 1e-6 * processing_time
        )  # Assume 1W per 1000 MIPS

        print(
            f"[DEBUG] EnergyCalc -> Sensor {sensor.device_id} | edge {edge_node.node_id} | "
            f"TxEnergy={transmission_energy:.4f}, ProcEnergy={processing_energy:.4f}"
        )

        return transmission_energy + processing_energy

    @staticmethod
    def calculate_load_balance_score(assignments):
        """Calculate load balance quality score"""
        if not assignments:
            return 0

        loads = [len(sensors) for sensors in assignments.values()]
        if len(loads) <= 1:
            return 1.0

        mean_load = sum(loads) / len(loads)
        variance = sum((load - mean_load) ** 2 for load in loads) / len(loads)

        print(f"[DEBUG] LoadBalance -> mean={mean_load:.2f}, variance={variance:.2f}")

        # Lower variance = better balance (normalize to 0-1 scale)
        return 1.0 / (1.0 + variance)


class PerformanceMetrics:
    """
    Performance metrics collection with standardized definitions
    """

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
        self.algorithm_name = "Unknown"
        # Statistical latency metrics
        self.latency_min = 0
        self.latency_max = 0
        self.latency_p99 = 0
        # Resource utilization metrics
        self.cpu_utilization = 0
        self.memory_utilization = 0
        
        # Task tracking
        self.tasks_generated = 0
        self.tasks_completed = 0
        self.per_node_loads = {}
        self.per_task_latencies = []

        # Setup logging to file
        self._setup_logging()
        print("[DEBUG] MetricsCollector initialized")
    
    def _setup_logging(self):
        """Setup logging to file for metrics tracking"""
        os.makedirs("logs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"logs/metrics_.log"
        
        # Create logger
        self.logger = logging.getLogger(f"MetricsCollector_{id(self)}")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        
        self.logger.info(f"Metrics logging initialized - Log file: {log_file}")

    def collect_metrics(self, digital_twin, placement, algorithm_name="Unknown"):
        """
        Collects metrics for a given placement in the OLB algorithm
        """

        self.logger.info(f"="*80)
        self.logger.info(f"Collecting metrics for algorithm: {algorithm_name}")
        self.logger.info(f"="*80)
        self.algorithm_name = algorithm_name
        calculator = OLBLatencyCalculator()

        # Log initial state
        self.logger.info(f"Total sensors in environment: {len(digital_twin.sensors)}")
        self.logger.info(f"Total edge nodes in environment: {len(digital_twin.edge_nodes)}")
        self.logger.info(f"Module assignments: {len(placement.module_assignments)} nodes have assignments")
        
        # Check if assignments are empty - raise error instead of generating synthetic data
        if not placement.module_assignments or all(len(sensors) == 0 for sensors in placement.module_assignments.values()):
            self.logger.error(f"[ERROR] Placement algorithm {algorithm_name} failed to assign any sensors!")
            raise ValueError(f"Placement algorithm {algorithm_name} failed to assign any sensors!")
        
        # Count total assignments
        total_assignments = sum(len(sensors) for sensors in placement.module_assignments.values())
        self.logger.info(f"Total sensor assignments: {total_assignments}")
        self.tasks_generated = total_assignments
        
        if total_assignments == 0:
            raise ValueError(f"ERROR: Zero assignments after placement! Algorithm {algorithm_name} failed to place any sensors.")

        total_comm_latency = 0
        total_comp_latency = 0
        total_energy = 0
        node_utilizations = []
        self.per_node_loads = {}

        for node_id, assigned_sensors in placement.module_assignments.items():
            if node_id >= len(digital_twin.edge_nodes):
                continue

            edge_node = digital_twin.edge_nodes[node_id]
            node_load = len(assigned_sensors)
            node_utilizations.append(node_load)
            self.per_node_loads[node_id] = node_load
            
            self.logger.info(f"Processing Node {node_id}: {node_load} sensors assigned")

            for sensor in assigned_sensors:
                self.tasks_completed += 1
                other_sensors = [s for s in assigned_sensors if s != sensor]
                comm_lat = calculator.calculate_communication_latency(
                    sensor, edge_node, other_sensors
                )
                comp_lat = calculator.calculate_computing_latency(
                    sensor, edge_node, other_sensors
                )

                if comm_lat == float("inf") or comp_lat == float("inf"):
                    comm_lat = 1000
                    comp_lat = 1000

                distance = calculator.calculate_distance(
                    sensor.coordinates, edge_node.coordinates
                )
                energy = MetricsDefinitions.calculate_energy_consumption(
                    sensor, edge_node, distance
                )

                print(
                    f"[TRACE] Sensor {sensor.device_id} -> edge {edge_node.node_id}, "
                    f"CommLat={comm_lat:.4f}, CompLat={comp_lat:.4f}, Energy={energy:.4f}"
                )

                total_latency = comm_lat + comp_lat
                total_comm_latency += comm_lat
                total_comp_latency += comp_lat
                total_energy += energy
                self.per_task_latencies.append(total_latency)

                self.detailed_assignments.append(
                    {
                        "sensor_id": sensor.device_id,
                        "edge_node_id": edge_node.node_id,
                        "comm_latency": comm_lat,
                        "comp_latency": comp_lat,
                        "total_latency": total_latency,
                        "energy": energy,
                        "distance": distance,
                        "sensor_coordinates": sensor.coordinates,
                        "edge_node_coordinates": edge_node.coordinates,
                    }
                )
                
                self.logger.debug(f"Task {self.tasks_completed}: Sensor {sensor.device_id} -> Node {edge_node.node_id}, "
                                f"Latency={total_latency:.4f}ms, Energy={energy:.4f}J")

        self.overall_latency = total_comm_latency + total_comp_latency
        self.communication_latency = total_comm_latency
        self.computing_latency = total_comp_latency
        self.energy_consumption = total_energy

        self.network_usage = sum(
            sensor.averageFlowRate * sensor.flowTrafficSize
            for sensor in digital_twin.sensors
        )
        self.execution_time = (
            self.overall_latency / len(digital_twin.sensors)
            if digital_twin.sensors
            else 0
        )

        self.load_balance_score = MetricsDefinitions.calculate_load_balance_score(
            placement.module_assignments
        )
        self.max_utilization = max(node_utilizations) if node_utilizations else 0

        # Cost calculation with named constants
        LATENCY_WEIGHT = 0.1
        NETWORK_WEIGHT = 0.05
        ENERGY_WEIGHT = 0.02
        
        self.cost_of_execution = (
            self.overall_latency * LATENCY_WEIGHT
            + self.network_usage * NETWORK_WEIGHT
            + self.energy_consumption * ENERGY_WEIGHT
        )
        
        # Log comprehensive metrics summary
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"METRICS SUMMARY FOR {algorithm_name}")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"[TASK TRACKING]")
        self.logger.info(f"   - Tasks Generated: {self.tasks_generated}")
        self.logger.info(f"   - Tasks Completed: {self.tasks_completed}")
        self.logger.info(f"   - Completion Rate: {(self.tasks_completed/self.tasks_generated*100) if self.tasks_generated > 0 else 0:.2f}%")
        self.logger.info(f"\n[PERFORMANCE METRICS]")
        self.logger.info(f"   - Overall Latency: {self.overall_latency:.4f} ms")
        self.logger.info(f"   - Communication Latency: {self.communication_latency:.4f} ms")
        self.logger.info(f"   - Computing Latency: {self.computing_latency:.4f} ms")
        self.logger.info(f"   - Energy Consumption: {self.energy_consumption:.4f} J")
        self.logger.info(f"   - Load Balance Score: {self.load_balance_score:.4f}")
        self.logger.info(f"\n[PER-NODE LOAD DISTRIBUTION]")
        for node_id, load in self.per_node_loads.items():
            self.logger.info(f"   - Node {node_id}: {load} tasks")
        self.logger.info(f"\n[PER-TASK LATENCY VALUES] (first 10):")
        for i, latency in enumerate(self.per_task_latencies[:10]):
            self.logger.info(f"   - Task {i+1}: {latency:.4f} ms")
        if len(self.per_task_latencies) > 10:
            self.logger.info(f"   - ... and {len(self.per_task_latencies)-10} more tasks")
        self.logger.info(f"{'='*80}\n")
        
        # Validate metrics - throw error if still zero
        if self.overall_latency == 0 and total_assignments > 0:
            raise ValueError(f"[ERROR] Overall latency is 0.00 but {total_assignments} assignments exist!")
        if self.energy_consumption == 0 and total_assignments > 0:
            raise ValueError(f"[ERROR] Energy consumption is 0.00 but {total_assignments} assignments exist!")
        if self.load_balance_score == 0 and len(placement.module_assignments) > 1:
            raise ValueError(f"[ERROR] Load balance score is 0.00 but {len(placement.module_assignments)} nodes have assignments!")
        
        # Calculate statistical latency metrics
        if self.detailed_assignments:
            latencies = [a["total_latency"] for a in self.detailed_assignments]
            self.latency_min = min(latencies)
            self.latency_max = max(latencies)
            # Calculate 99th percentile
            sorted_latencies = sorted(latencies)
            p99_index = int(len(sorted_latencies) * 0.99)
            self.latency_p99 = sorted_latencies[p99_index] if p99_index < len(sorted_latencies) else sorted_latencies[-1]
        
        # Try to enhance metrics with YAFS output data if available
        try:
            from .yafs_output_parser import parse_yafs_output
            yafs_metrics = parse_yafs_output("results", algorithm_name.lower())
            
            # Use actual YAFS metrics only if data was found
            if yafs_metrics["total_messages_processed"] > 0:
                self.latency_min = yafs_metrics["actual_latency_min"]
                self.latency_max = yafs_metrics["actual_latency_max"]
                self.latency_p99 = yafs_metrics["actual_latency_p99"]
                self.overall_latency = yafs_metrics["actual_latency_avg"]
                self.logger.info(f"Enhanced metrics with YAFS output data: {yafs_metrics['total_messages_processed']} messages processed")
            else:
                self.logger.info("YAFS output files not found, using calculated metrics (this is normal)")
        except ImportError:
            self.logger.info("YAFS output parser not available, using calculated metrics")
        except Exception as e:
            self.logger.debug(f"Could not parse YAFS output (using calculated metrics): {e}")
        
        # Calculate CPU and memory utilization
        if digital_twin.edge_nodes:
            total_capacity = sum(edge.processingPower for edge in digital_twin.edge_nodes)
            total_load = sum(
                len(sensors) * sum(s.averageFlowSize for s in sensors) 
                for sensors in placement.module_assignments.values()
            )
            self.cpu_utilization = min(100.0, (total_load / total_capacity * 100)) if total_capacity > 0 else 0
            # Memory utilization estimate (based on number of assignments)
            total_assignments = sum(len(sensors) for sensors in placement.module_assignments.values())
            self.memory_utilization = min(100.0, (total_assignments / len(digital_twin.sensors) * 80)) if digital_twin.sensors else 0
        


    def generate_report(self):
        """Generate comprehensive performance report"""
        print("[INFO] Generating performance report...")
        report = f""" YAFS OLB SIMULATION PERFORMANCE REPORT 

KEY PERFORMANCE INDICATORS (KPIs):
Overall Latency (L): {self.overall_latency:.4f}
  - Communication Latency: {self.communication_latency:.4f}
  - Computing Latency: {self.computing_latency:.4f}
Network Usage (Nusage): {self.network_usage:.4f} MB/s
Execution Time (Te): {self.execution_time:.4f} ms
Energy Consumption (Etotal): {self.energy_consumption:.4f} W
Cost of Execution (Ce): {self.cost_of_execution:.4f}

DETAILED ASSIGNMENT ANALYSIS:
"""

        # Group assignments by edge node
        node_assignments = {}
        for assignment in self.detailed_assignments:
            node_id = assignment["edge_node_id"]
            if node_id not in node_assignments:
                node_assignments[node_id] = []
            node_assignments[node_id].append(assignment)

        for node_id, assignments in node_assignments.items():
            report += f"\nedge Node {node_id}: {len(assignments)} sensors assigned\n"
            for assignment in assignments:
                report += f"  Sensor {assignment['sensor_id']}: Total Latency = {assignment['total_latency']:.4f}\n"
                report += (
                    f"    - Communication Latency: {assignment['comm_latency']:.4f}\n"
                )
                report += f"    - Computing Latency: {assignment['comp_latency']:.4f}\n"
                report += f"    - Sensor Position: {assignment['sensor_coordinates']}\n"
                report += (
                    f"    - edge Node Position: {assignment['edge_node_coordinates']}\n"
                )

        report += "\n=\n"
        return report


    
    def calculate_sla_compliance(self, sla_threshold_ms: float = 100.0) -> float:
        """
        Calculate SLA compliance percentage based on latency threshold.
        
        Args:
            sla_threshold_ms: Maximum acceptable latency in milliseconds
            
        Returns:
            Percentage of tasks meeting SLA (0-100)
        """
        if not self.per_task_latencies:
            return 100.0
        
        compliant_tasks = sum(1 for latency in self.per_task_latencies if latency <= sla_threshold_ms)
        compliance_percent = (compliant_tasks / len(self.per_task_latencies)) * 100
        
        self.logger.info(f"SLA Compliance: {compliant_tasks}/{len(self.per_task_latencies)} tasks under {sla_threshold_ms}ms = {compliance_percent:.2f}%")
        
        return compliance_percent
    
    def get_summary_dict(self):
        """Get comprehensive metrics as dictionary"""
        # Calculate SLA compliance
        sla_compliance_percent = self.calculate_sla_compliance()
        
        return {
            "algorithm": self.algorithm_name,
            "overall_latency": self.overall_latency,
            "communication_latency": self.communication_latency,
            "computing_latency": self.computing_latency,
            "latency_min": self.latency_min,
            "latency_max": self.latency_max,
            "latency_p99": self.latency_p99,
            "network_usage": self.network_usage,
            "execution_time": self.execution_time,
            "energy_consumption": self.energy_consumption,
            "cost_of_execution": self.cost_of_execution,
            "load_balance_score": self.load_balance_score,
            "max_utilization": self.max_utilization,
            "cpu_utilization": self.cpu_utilization,
            "memory_utilization": self.memory_utilization,
            "sla_compliance_percent": sla_compliance_percent,
            "num_assignments": len(self.detailed_assignments),
            "detailed_assignments": self.detailed_assignments,
            "tasks_generated": self.tasks_generated,
            "tasks_completed": self.tasks_completed,
            "per_node_loads": self.per_node_loads,
            "per_task_latencies": self.per_task_latencies,
        }
