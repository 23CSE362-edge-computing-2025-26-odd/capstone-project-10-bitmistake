import random
from typing import List, Tuple

from .devices import CloudNodeDevice, EdgeNodeDevice, SensorDevice


class DigitalTwinEnvironment:
    """
    Phase 1: Environment Construction - The Digital Twin
    Manages the 2D coordinate system and all physical entities
    """

    def __init__(self, width=3000, height=2000):
        self.width = width
        self.height = height
        self.sensors = []
        self.edge_nodes = []
        self.cloud_node = None
        self.proxy_node = None

    def add_sensor(self, sensor):
        """Add sensor to the environment"""
        if (
            0 <= sensor.coordinates[0] <= self.width
            and 0 <= sensor.coordinates[1] <= self.height
        ):
            self.sensors.append(sensor)
        else:
            raise ValueError(
                f"Sensor coordinates {sensor.coordinates} outside environment bounds"
            )

    def add_edge_node(self, edge_node):
        """Add edge node to the environment"""
        if (
            0 <= edge_node.coordinates[0] <= self.width
            and 0 <= edge_node.coordinates[1] <= self.height
        ):
            self.edge_nodes.append(edge_node)
        else:
            raise ValueError(
                f"edge node coordinates {edge_node.coordinates} outside environment bounds"
            )

    def initialize_sensors(self, num_sensors=10, seed=None):
        """
        Task 1.2: Model Tier 1 - IoT Layer Entities
        Initialize sensors with random parameters
        """
        # Use a separate Random instance to avoid affecting global random state
        rng = random.Random(seed) if seed is not None else random.Random()
        print(
            f"[DEBUG] Initializing {num_sensors} sensors in environment of size ({self.width}, {self.height})"
        )
        # Initializing sensors silently
        for i in range(num_sensors):
            coordinates = (
                rng.uniform(0, self.width),
                rng.uniform(0, self.height),
            )
            transmission_power = rng.uniform(0.1, 1.0)  # Watts
            average_flow_rate = rng.uniform(0.5, 2.0)  # Hz
            flow_traffic_size = rng.uniform(0.1, 1.0)  # MB
            average_flow_size = rng.uniform(100, 1000)  # MI

            sensor = SensorDevice(
                device_id=i,
                coordinates=coordinates,
                transmission_power=transmission_power,
                average_flow_rate=average_flow_rate,
                flow_traffic_size=flow_traffic_size,
                average_flow_size=average_flow_size,
            )
            self.add_sensor(sensor)

            print(f"[INFO] Sensor {i} added at {coordinates}")

    def initialize_edge_nodes(self, num_edge_nodes=6, seed=None):
        # Use a separate Random instance to avoid affecting global random state
        rng = random.Random(seed + 100) if seed is not None else random.Random()
        print(f"[DEBUG] Initializing {num_edge_nodes} edge nodes")
        for i in range(num_edge_nodes):
            max_x = min(2500, self.width - 100)
            max_y = min(1500, self.height - 100)
            coordinates = (rng.uniform(100, max_x), rng.uniform(100, max_y))
            processing_power = rng.uniform(1000, 5000)
            bandwidth = rng.uniform(10, 100)
            carrier_frequency = rng.uniform(2.4, 5.0)
            noise_power = rng.uniform(1e-12, 1e-10)

            edge_node = EdgeNodeDevice(
                node_id=i,
                coordinates=coordinates,
                processing_power=processing_power,
                bandwidth=bandwidth,
                carrier_frequency=carrier_frequency,
                noise_power=noise_power,
            )
            self.add_edge_node(edge_node)

            print(
                f"[INFO] edgeNode {i} created at {coordinates} with {processing_power:.2f} MIPS"
            )

    def initialize_cloud(self):
        """Initialize the cloud node"""
        self.cloud_node = CloudNodeDevice(
            node_id="cloud", coordinates=(self.width / 2, self.height + 500)
        )
        print(
            "[INFO] Cloud node initialized at coordinates",
            (self.width / 2, self.height + 500),
        )

    def get_summary(self):
        """Get summary of the environment"""
        print(
            "[SUMMARY] Environment contains "
            f"{len(self.sensors)} sensors, {len(self.edge_nodes)} edge nodes, "
            f"Cloud exists: {self.cloud_node is not None}"
        )
        return {
            "environment_size": (self.width, self.height),
            "num_sensors": len(self.sensors),
            "num_edge_nodes": len(self.edge_nodes),
            "sensor_positions": [s.coordinates for s in self.sensors],
            "edge_node_positions": [f.coordinates for f in self.edge_nodes],
            "cloud_node": {
                "exists": self.cloud_node is not None,
                "coordinates": getattr(self.cloud_node, "coordinates", None),
                "processing_power": getattr(self.cloud_node, "processing_power", None),
                "bandwidth": getattr(self.cloud_node, "bandwidth", None),
            },
        }
    
    @classmethod
    def from_scenario(cls, scenario, environment_width=3000, environment_height=2000):
        """
        Create a DigitalTwinEnvironment from a HospitalScenario.
        
        Converts hospital scenario configurations into YAFS simulation entities.
        This method replaces the ScenarioToEnvironmentAdapter functionality.
        
        Args:
            scenario: HospitalScenario object with sensor configurations
            environment_width: Width of the simulation environment
            environment_height: Height of the simulation environment
            
        Returns:
            Initialized DigitalTwinEnvironment with sensors and edge nodes
        """
        from .hospital_scenarios_extended import SensorConfig, HospitalScenario
        
        print(f"Converting scenario '{scenario.name}' to environment")
        print(f"  Scenario has {len(scenario.sensors)} sensors, {scenario.edge_nodes} edge nodes")
        
        # Create environment
        environment = cls(width=environment_width, height=environment_height)
        
        # Convert sensors
        sensors = cls._convert_sensors_from_configs(scenario.sensors)
        environment.sensors = sensors
        
        # Create edge nodes based on scenario requirements
        cls._create_edge_nodes_for_scenario(environment, scenario)
        
        print(f"Converted scenario to environment:")
        print(f"  - {len(environment.sensors)} sensors")
        print(f"  - {len(environment.edge_nodes)} edge nodes")
        
        return environment
    
    @staticmethod
    def _convert_sensors_from_configs(sensor_configs) -> List[SensorDevice]:
        """
        Convert SensorConfig objects to SensorDevice objects.
        
        Args:
            sensor_configs: List of SensorConfig dataclass instances
            
        Returns:
            List of SensorDevice objects ready for simulation
        """
        from .hospital_scenarios_extended import SensorConfig
        
        sensors = []
        
        for config in sensor_configs:
            try:
                sensor = DigitalTwinEnvironment._config_to_sensor_device(config)
                sensors.append(sensor)
            except Exception as e:
                print(f"Warning: Failed to convert sensor {config.sensor_id}: {e}")
        
        return sensors
    
    @staticmethod
    def _config_to_sensor_device(config) -> SensorDevice:
        """
        Convert a single SensorConfig to SensorDevice.
        
        Maps scenario-specific parameters to simulation device parameters.
        """
        # Map data rate to flow parameters
        flow_rate, traffic_size, flow_size = DigitalTwinEnvironment._map_data_rate(
            config.data_rate, config.frequency_hz
        )
        
        # Map criticality to transmission power
        transmission_power = DigitalTwinEnvironment._map_criticality_to_power(config.criticality)
        
        # Generate coordinates if not provided
        coordinates = config.coordinates
        if coordinates is None:
            # Generate random coordinates within environment bounds
            # Use sensor_id hash for reproducibility
            import hashlib
            seed_value = int(hashlib.md5(str(config.sensor_id).encode()).hexdigest(), 16) % (2**32)
            rng = random.Random(seed_value)
            coordinates = (rng.uniform(0, 3000), rng.uniform(0, 2000))
        
        # Create sensor device
        sensor = SensorDevice(
            device_id=config.sensor_id,
            coordinates=coordinates,
            transmission_power=transmission_power,
            average_flow_rate=flow_rate,
            flow_traffic_size=traffic_size,
            average_flow_size=flow_size
        )
        
        return sensor
    
    @staticmethod
    def _map_data_rate(data_rate: str, frequency_hz: float) -> Tuple[float, float, float]:
        """
        Map scenario data rate specification to sensor flow parameters.
        
        Args:
            data_rate: "high", "medium", or "low"
            frequency_hz: Sensor sampling frequency
            
        Returns:
            Tuple of (average_flow_rate, flow_traffic_size, average_flow_size)
        """
        # Base parameters by data rate
        rate_mappings = {
            "high": {"traffic": 2.0, "size": 500.0},      # High throughput
            "medium": {"traffic": 1.0, "size": 300.0},    # Medium throughput
            "low": {"traffic": 0.5, "size": 100.0}        # Low throughput
        }
        
        params = rate_mappings.get(data_rate.lower(), rate_mappings["medium"])
        
        # Calculate flow parameters
        average_flow_rate = frequency_hz  # Hz (samples per second)
        flow_traffic_size = params["traffic"]  # Megabits per message
        average_flow_size = params["size"]  # Million Instructions per message
        
        return average_flow_rate, flow_traffic_size, average_flow_size
    
    @staticmethod
    def _map_criticality_to_power(criticality: str) -> float:
        """
        Map criticality level to transmission power.
        
        Critical sensors get higher power for better signal quality.
        
        Args:
            criticality: "critical", "important", or "routine"
            
        Returns:
            Transmission power in Watts
        """
        power_mappings = {
            "critical": 0.8,    # High power for critical sensors
            "important": 0.5,   # Medium power for important sensors
            "routine": 0.3      # Lower power for routine sensors
        }
        
        return power_mappings.get(criticality.lower(), 0.5)
    
    @staticmethod
    def _create_edge_nodes_for_scenario(environment, scenario):
        """
        Create edge nodes appropriate for the scenario.
        
        Distributes edge nodes across the environment based on sensor locations.
        
        Args:
            environment: DigitalTwinEnvironment to populate
            scenario: HospitalScenario defining requirements
        """
        num_edge_nodes = scenario.edge_nodes
        
        # Get sensor locations to inform edge node placement
        sensor_locations = [s.coordinates for s in environment.sensors]
        
        # Calculate edge node positions to minimize average distance to sensors
        edge_positions = DigitalTwinEnvironment._calculate_optimal_edge_positions(
            sensor_locations,
            num_edge_nodes,
            environment.width,
            environment.height
        )
        
        # Create edge nodes with appropriate capacities
        edge_nodes = []
        for i, position in enumerate(edge_positions):
            # Adjust capacity based on scenario requirements
            base_capacity = DigitalTwinEnvironment._estimate_required_capacity(scenario, num_edge_nodes)
            
            edge_node = EdgeNodeDevice(
                node_id=i,
                coordinates=position,
                processing_power=base_capacity,
                bandwidth=DigitalTwinEnvironment._estimate_required_bandwidth(scenario),
                carrier_frequency=2.4,  # GHz
                noise_power=1e-10  # Watts
            )
            edge_nodes.append(edge_node)
        
        environment.edge_nodes = edge_nodes
        
        print(f"Created {len(edge_nodes)} edge nodes for scenario")
    
    @staticmethod
    def _calculate_optimal_edge_positions(
        sensor_locations: List[Tuple[float, float]],
        num_edge_nodes: int,
        width: int,
        height: int
    ) -> List[Tuple[float, float]]:
        """
        Calculate optimal edge node positions using k-means-like clustering.
        
        Args:
            sensor_locations: List of (x, y) sensor coordinates
            num_edge_nodes: Number of edge nodes to place
            width: Environment width
            height: Environment height
            
        Returns:
            List of (x, y) positions for edge nodes
        """
        import math
        
        if not sensor_locations:
            # Fallback: distribute evenly if no sensors
            positions = []
            for i in range(num_edge_nodes):
                x = (i + 1) * width / (num_edge_nodes + 1)
                y = height / 2
                positions.append((x, y))
            return positions
        
        # Simple clustering: divide sensors into groups and place edge node at centroid
        random.seed(42)  # Reproducible placement
        
        # Initialize edge positions randomly
        positions = [
            (random.uniform(width * 0.2, width * 0.8), 
             random.uniform(height * 0.2, height * 0.8))
            for _ in range(num_edge_nodes)
        ]
        
        # Run simple k-means for a few iterations
        for iteration in range(10):
            # Assign sensors to nearest edge node
            clusters = [[] for _ in range(num_edge_nodes)]
            for sensor_loc in sensor_locations:
                nearest_edge = min(
                    range(num_edge_nodes),
                    key=lambda i: DigitalTwinEnvironment._distance(sensor_loc, positions[i])
                )
                clusters[nearest_edge].append(sensor_loc)
            
            # Update edge positions to cluster centroids
            new_positions = []
            for i, cluster in enumerate(clusters):
                if cluster:
                    avg_x = sum(loc[0] for loc in cluster) / len(cluster)
                    avg_y = sum(loc[1] for loc in cluster) / len(cluster)
                    new_positions.append((avg_x, avg_y))
                else:
                    new_positions.append(positions[i])  # Keep old position if no sensors
            
            positions = new_positions
        
        return positions
    
    @staticmethod
    def _distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        import math
        dx = coord1[0] - coord2[0]
        dy = coord1[1] - coord2[1]
        return math.sqrt(dx**2 + dy**2)
    
    @staticmethod
    def _estimate_required_capacity(scenario, num_edge_nodes: int) -> float:
        """
        Estimate required edge node processing capacity for scenario.
        
        Args:
            scenario: HospitalScenario
            num_edge_nodes: Number of edge nodes to distribute load across
            
        Returns:
            Processing power in MIPS per edge node
        """
        # Calculate total workload from sensors
        total_workload = 0.0
        for sensor_config in scenario.sensors:
            # Estimate workload based on data rate and frequency
            if sensor_config.data_rate.lower() == "high":
                total_workload += sensor_config.frequency_hz * 500
            elif sensor_config.data_rate.lower() == "medium":
                total_workload += sensor_config.frequency_hz * 300
            else:
                total_workload += sensor_config.frequency_hz * 100
        
        # Distribute across edge nodes with safety margin
        capacity_per_node = (total_workload / num_edge_nodes) * 1.5  # 50% safety margin
        
        # Ensure minimum capacity
        return max(1000.0, capacity_per_node)
    
    @staticmethod
    def _estimate_required_bandwidth(scenario) -> float:
        """
        Estimate required bandwidth for scenario.
        
        Returns bandwidth in MHz
        """
        # Base bandwidth plus scaling for high-data-rate sensors
        high_rate_sensors = sum(
            1 for s in scenario.sensors 
            if s.data_rate.lower() == "high"
        )
        
        base_bandwidth = 50.0  # MHz
        additional = high_rate_sensors * 5.0  # 5 MHz per high-rate sensor
        
        return base_bandwidth + additional
