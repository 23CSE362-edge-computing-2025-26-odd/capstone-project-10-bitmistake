class ActuatorDevice:
    """
    Tier 1 - IoT Layer Entity representing an actuator device
    Actuators receive processed data or commands from edge/Cloud nodes
    Examples: insulin pump, alarm, display unit
    """

    def __init__(self, actuator_id, coordinates, action_type, power_consumption):
        self.actuator_id = actuator_id
        self.coordinates = coordinates  # (x, y) tuple
        self.actionType = action_type  # e.g., "insulin_delivery", "alert", "display"
        self.powerConsumption = power_consumption  # in Watts
        self.received_commands = []  # track commands received

        print(
            f"[INFO] Actuator {actuator_id} ({action_type}) created at {coordinates} "
            f"with Power {power_consumption}W"
        )

    def receive_command(self, command):
        """Receive a command from edge/cloud node"""
        self.received_commands.append(command)
        print(f"[ACTION] Actuator {self.actuator_id} executed command: {command}")

    def __str__(self):
        return f"Actuator_{self.actuator_id} ({self.actionType}) at {self.coordinates}"

    def __repr__(self):
        return self.__str__()


class SensorDevice:
    """
    Tier 1 - IoT Layer Entity representing a patient sensor
    Contains all attributes required by OLB equations
    """

    def __init__(
        self,
        device_id,
        coordinates,
        transmission_power,
        average_flow_rate,
        flow_traffic_size,
        average_flow_size,
    ):
        self.device_id = device_id
        self.coordinates = coordinates  # (x, y) tuple
        self.transmissionPower = transmission_power  # P(x) in Watts
        self.averageFlowRate = average_flow_rate  # fl(x) in Hz
        self.flowTrafficSize = flow_traffic_size  # l(x) in megabits
        self.averageFlowSize = average_flow_size  # ν(x) in MI
        print(
            f"[INFO] SensorDevice {device_id} created at {coordinates} with Tx Power {transmission_power}W"
        )

    def __str__(self):
        return f"Sensor_{self.device_id} at {self.coordinates}"

    def __repr__(self):
        return self.__str__()


class EdgeNodeDevice:
    """
    Tier 2 - edge Layer Entity representing edge computing nodes
    Contains all attributes required by OLB equations
    """

    def __init__(
        self,
        node_id,
        coordinates,
        processing_power,
        bandwidth,
        carrier_frequency,
        noise_power,
    ):
        self.node_id = node_id
        self.coordinates = coordinates  # (x, y) tuple
        self.processingPower = processing_power  # Cj in MIPS
        self.bandwidth = bandwidth  # BWj in MHz
        self.carrierFrequency = carrier_frequency  # in GHz
        self.noisePower = noise_power  # σ^2 in Watts
        self.assigned_modules = []  # Track assigned processing modules
        print(
            f"[INFO] edgeNode {node_id} created at {coordinates} with {processing_power} MIPS and BW {bandwidth} MHz"
        )

    # Note: Each edge node will store assigned modules in self.assigned_modules

    def __str__(self):
        return f"edgeNode_{self.node_id} at {self.coordinates}"

    def __repr__(self):
        return self.__str__()


class CloudNodeDevice(EdgeNodeDevice):
    """
    Tier 3 - Cloud Layer Entity representing the cloud data center
    Inherits EdgeNodeDevice but enforces large compute and bandwidth capacity.
    Treated as a single centralized node.
    """

    def __init__(
        self,
        node_id="cloud",
        coordinates=(0, 0),
        processing_power=1e6,
        bandwidth=1000,
        carrier_frequency=10.0,
        noise_power=1e-15,
    ):
        super().__init__(
            node_id=node_id,
            coordinates=coordinates,
            processing_power=processing_power,
            bandwidth=bandwidth,
            carrier_frequency=carrier_frequency,
            noise_power=noise_power,
        )
        print(
            f"[INFO] CloudNode initialized at {coordinates} with {processing_power} MIPS and BW {bandwidth} MHz"
        )

    def __str__(self):
        return f"CloudNode at {self.coordinates}"

    def __repr__(self):
        return self.__str__()
