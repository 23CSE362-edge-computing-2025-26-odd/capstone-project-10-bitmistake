import math

from yafs import Placement
from .common_utils import extract_sensor_id, SensorLookupIndex, calculate_euclidean_distance


class OLBLatencyCalculator:
    """
    Core OLB mathematical model implementation
    Implements all latency calculation formulas
    """

    def __init__(self):
        self.speed_of_light = 299792458  # m/s

    def calculate_distance(self, sensor_coords, edge_coords):
        """
        Calculate Euclidean distance between sensor and edge node.
        Uses common_utils implementation to avoid duplication.
        """
        return calculate_euclidean_distance(sensor_coords, edge_coords)

    def calculate_channel_gain(self, distance, carrier_frequency):
        """Calculate Channel Gain (g(x))"""
        if distance == 0:
            distance = 1  # Avoid division by zero

        wavelength = self.speed_of_light / (carrier_frequency * 1e9)
        channel_gain = 10 * math.log10(wavelength**2 / (4 * math.pi * distance) ** 2)
        return channel_gain

    def calculate_snr(self, transmission_power, channel_gain, noise_power):
        """Calculate Signal-to-Noise Ratio (SNR(x))"""
        linear_gain = 10 ** (channel_gain / 10)
        return (transmission_power * linear_gain) / noise_power

    def calculate_device_capacity(self, bandwidth, snr):
        """Calculate Device Capacity (cj(x))"""
        if snr <= 0:
            return 0.001
        return bandwidth * math.log2(1 + snr)

    def calculate_individual_traffic_load(
        self, flow_rate, traffic_size, device_capacity
    ):
        """Calculate Individual Traffic Load (eaj(x))"""
        if device_capacity == 0:
            return 1.0
        return (flow_rate * traffic_size) / device_capacity

    def calculate_individual_computing_load(
        self, flow_rate, flow_size, processing_power
    ):
        """Calculate Individual Computing Load (ebj(x))"""
        if processing_power == 0:
            return 1.0
        return (flow_rate * flow_size) / processing_power

    def calculate_communication_latency(self, sensor, edge_node, assigned_sensors):
        """
        Task 3.1.1: Communication Latency Analysis (L_m(j))
        """
        try:
            # Calculate Distance (d)
            distance = self.calculate_distance(sensor.coordinates, edge_node.coordinates)

            # Calculate wavelength λ
            wavelength = self.speed_of_light / (edge_node.carrierFrequency * 1e9)

            # Calculate Channel Gain (g(x))
            channel_gain = 10 * math.log10(
                wavelength**2 / (4 * math.pi * distance) ** 2
            )

            # Calculate Signal-to-Noise Ratio (SNR(x))
            linear_gain = 10 ** (channel_gain / 10)
            snr = (sensor.transmissionPower * linear_gain) / edge_node.noisePower

            # Calculate Device Capacity (cj(x))
            device_capacity = self.calculate_device_capacity(edge_node.bandwidth, snr)
            
            if device_capacity <= 0:
                return float("inf")

            # Calculate Individual Traffic Load (eaj(x))
            individual_traffic_load = (
                sensor.averageFlowRate * sensor.flowTrafficSize
            ) / device_capacity

            # Calculate Total Traffic Load (TLj)
            total_traffic_load = individual_traffic_load
            for assigned_sensor in assigned_sensors:
                assigned_load = (
                    assigned_sensor.averageFlowRate * assigned_sensor.flowTrafficSize
                ) / device_capacity
                total_traffic_load += assigned_load

            # System is overloaded - assignment is infeasible
            if total_traffic_load >= 1.0:
                return float("inf")

            # Calculate Communication Latency Score (L_m(j))
            comm_latency = total_traffic_load / (1 - total_traffic_load)

            return comm_latency

        except (ZeroDivisionError, ValueError, OverflowError):
            return float("inf")

    def calculate_computing_latency(self, sensor, edge_node, assigned_sensors):
        """
        Task 3.1.2: Computing Latency Analysis (L_p(j))
        """
        try:
            # Calculate Individual Computing Load (ebj(x))
            individual_computing_load = (
                sensor.averageFlowRate * sensor.averageFlowSize
            ) / edge_node.processingPower

            # Calculate Total Computing Load (CLj)
            total_computing_load = individual_computing_load
            for assigned_sensor in assigned_sensors:
                assigned_comp_load = (
                    assigned_sensor.averageFlowRate * assigned_sensor.averageFlowSize
                ) / edge_node.processingPower
                total_computing_load += assigned_comp_load

            # System is overloaded - assignment is infeasible
            if total_computing_load >= 1.0:
                return float("inf")

            # Calculate Computing Latency Score (L_p(j))
            comp_latency = total_computing_load / (1 - total_computing_load)

            return comp_latency

        except (ZeroDivisionError, ValueError, OverflowError):
            return float("inf")


class OLBPlacement(Placement):
    """
    Phase 3: OLB Algorithm Implementation
    Custom YAFS Placement policy implementing the core OLB algorithm
    """

    def __init__(self, name, json_file, digital_twin):
        super(OLBPlacement, self).__init__(name, json_file)
        self.digital_twin = digital_twin
        self.calculator = OLBLatencyCalculator()
        self.module_assignments = {}  # Track which modules are assigned to which nodes
        self.sensor_lookup = SensorLookupIndex(digital_twin.sensors)

        # Set activation distribution to None to avoid the error
        self.activation_dist = None
        
        self._latency_cache = {}
        self._node_loads = {i: [] for i in range(len(digital_twin.edge_nodes))}

    def initial_allocation(self, sim, app_name):
        app = sim.apps[app_name]

        modules_to_place = [m for m in app.modules if "Processing_Module" in m]

        for module_name in modules_to_place:
            sensor_id = extract_sensor_id(module_name)
            sensor = self.sensor_lookup.find_by_id(sensor_id)

            if sensor:
                optimal_node_id = self._find_optimal_edge_node(sensor)

                if optimal_node_id is not None:
                    node_name = f"edge_{optimal_node_id}"
                    sim.deploy_module(app_name, module_name, [], [node_name])

                    if optimal_node_id not in self.module_assignments:
                        self.module_assignments[optimal_node_id] = []
                    self.module_assignments[optimal_node_id].append(sensor)
                    self._node_loads[optimal_node_id].append(sensor)
                else:
                    fallback_node = "edge_0"
                    sim.deploy_module(app_name, module_name, [], [fallback_node])
                    if 0 not in self.module_assignments:
                        self.module_assignments[0] = []
                    self.module_assignments[0].append(sensor)
                    self._node_loads[0].append(sensor)

    def _find_optimal_edge_node(self, sensor):
        min_latency = float("inf")
        optimal_node_id = None

        for i, edge_node in enumerate(self.digital_twin.edge_nodes):
            try:
                current_load_count = len(self._node_loads[i])
                cache_key = (sensor.device_id, i, current_load_count)
                
                if cache_key in self._latency_cache:
                    total_latency = self._latency_cache[cache_key]
                else:
                    assigned_sensors = self.module_assignments.get(i, [])
                    comm_latency = self.calculator.calculate_communication_latency(sensor, edge_node, assigned_sensors)
                    comp_latency = self.calculator.calculate_computing_latency(sensor, edge_node, assigned_sensors)

                    if comm_latency == float("inf") or comp_latency == float("inf"):
                        total_latency = float("inf")
                    else:
                        total_latency = comm_latency + comp_latency
                    
                    self._latency_cache[cache_key] = total_latency

                if total_latency < min_latency:
                    min_latency = total_latency
                    optimal_node_id = i

            except (ZeroDivisionError, ValueError, OverflowError):
                continue

        return optimal_node_id
