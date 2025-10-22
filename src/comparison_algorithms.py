"""
Real Implementation of Placement Algorithms for Fog Computing
Includes LBS, LAB, MEC, and FNPA algorithms with proper algorithmic logic
"""

import math
from typing import Dict, List, Optional, Tuple
from yafs import Placement


class LBS(Placement):
    """
    Location-Based Selection (LBS) Algorithm
    
    Strategy: Select placement nodes by minimizing average Euclidean distance 
    between sensors and fog nodes. Prioritizes nearest nodes first.
    
    Key Features:
    - Pure distance-based optimization
    - No load consideration
    - Greedy assignment to closest available node
    """
    
    def __init__(self, name: str, json_file: str, digital_twin):
        super().__init__(name, json_file)
        self.digital_twin = digital_twin
        self.module_assignments: Dict[int, List] = {}
        self.activation_dist = None
        
    def initial_allocation(self, sim, app_name: str):
        """Deploy modules using location-based selection"""
        app = sim.apps[app_name]
        modules_to_place = [m for m in app.modules if "Processing_Module" in m]
        
        print(f"\n{'='*70}")
        print(f"LBS Algorithm: Placing {len(modules_to_place)} modules by location")
        print(f"{'='*70}")
        
        placement_count = 0
        total_distance = 0.0
        
        for module_name in modules_to_place:
            sensor_id = self._extract_sensor_id(module_name)
            sensor = self._find_sensor_by_id(sensor_id)
            
            if sensor:
                # Find nearest fog node
                optimal_node_id, distance = self._find_nearest_fog_node(sensor)
                
                if optimal_node_id is not None:
                    node_name = f"fog_{optimal_node_id}"
                    sim.deploy_module(app_name, module_name, [], [node_name])
                    
                    # Track assignment
                    if optimal_node_id not in self.module_assignments:
                        self.module_assignments[optimal_node_id] = []
                    self.module_assignments[optimal_node_id].append(sensor)
                    
                    placement_count += 1
                    total_distance += distance
                    
                    print(f"  [LBS] Sensor {sensor_id} -> fog_{optimal_node_id} "
                          f"(distance: {distance:.2f}m)")
        
        avg_distance = total_distance / placement_count if placement_count > 0 else 0
        print(f"\n[LBS] Placement Complete: {placement_count} modules placed")
        print(f"[LBS] Average Distance: {avg_distance:.2f}m")
        print(f"{'='*70}\n")
    
    def _find_nearest_fog_node(self, sensor) -> Tuple[Optional[int], float]:
        """Find the nearest fog node to the sensor"""
        min_distance = float("inf")
        nearest_node_id = None
        
        for i, fog_node in enumerate(self.digital_twin.fog_nodes):
            distance = self._calculate_distance(sensor.coordinates, fog_node.coordinates)
            
            if distance < min_distance:
                min_distance = distance
                nearest_node_id = i
        
        return nearest_node_id, min_distance
    
    def _calculate_distance(self, coord1: Tuple[float, float], 
                           coord2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two coordinates"""
        dx = coord1[0] - coord2[0]
        dy = coord1[1] - coord2[1]
        return math.sqrt(dx**2 + dy**2)
    
    def _extract_sensor_id(self, module_name: str) -> int:
        """Extract sensor ID from module name"""
        parts = module_name.split("_")
        for part in reversed(parts):
            if part.isdigit():
                return int(part)
        return 0
    
    def _find_sensor_by_id(self, sensor_id: int):
        """Find sensor device by ID"""
        for sensor in self.digital_twin.sensors:
            if sensor.device_id == sensor_id:
                return sensor
        return None


class LAB(Placement):
    """
    Load-Aware Balancing (LAB) Algorithm
    
    Strategy: Dynamically assign placement based on node capacity and current load.
    Uses weighted scoring: score = α·(1/load) + β·(1/distance)
    
    Key Features:
    - Balances load across fog nodes
    - Considers both distance and current utilization
    - Adaptive weighting based on system state
    """
    
    def __init__(self, name: str, json_file: str, digital_twin, 
                 alpha: float = 0.6, beta: float = 0.4):
        super().__init__(name, json_file)
        self.digital_twin = digital_twin
        self.module_assignments: Dict[int, List] = {}
        self.activation_dist = None
        
        # Weighting factors
        self.alpha = alpha  # Weight for load consideration
        self.beta = beta    # Weight for distance consideration
        
        # Track node loads
        self.node_loads: Dict[int, float] = {
            i: 0.0 for i in range(len(digital_twin.fog_nodes))
        }
        self.node_capacities: Dict[int, float] = {
            i: fog_node.processingPower 
            for i, fog_node in enumerate(digital_twin.fog_nodes)
        }
    
    def initial_allocation(self, sim, app_name: str):
        """Deploy modules using load-aware balancing"""
        app = sim.apps[app_name]
        modules_to_place = [m for m in app.modules if "Processing_Module" in m]
        
        print(f"\n{'='*70}")
        print(f"LAB Algorithm: Placing {len(modules_to_place)} modules with load awareness")
        print(f"LAB Parameters: α={self.alpha}, β={self.beta}")
        print(f"{'='*70}")
        
        placement_count = 0
        
        for module_name in modules_to_place:
            sensor_id = self._extract_sensor_id(module_name)
            sensor = self._find_sensor_by_id(sensor_id)
            
            if sensor:
                # Find optimal node based on load and distance
                optimal_node_id, score = self._find_optimal_node(sensor)
                
                if optimal_node_id is not None:
                    node_name = f"fog_{optimal_node_id}"
                    sim.deploy_module(app_name, module_name, [], [node_name])
                    
                    # Track assignment
                    if optimal_node_id not in self.module_assignments:
                        self.module_assignments[optimal_node_id] = []
                    self.module_assignments[optimal_node_id].append(sensor)
                    
                    # Update load tracking
                    workload = sensor.averageFlowSize * sensor.averageFlowRate
                    self.node_loads[optimal_node_id] += workload
                    
                    utilization = (self.node_loads[optimal_node_id] / 
                                 self.node_capacities[optimal_node_id] * 100)
                    
                    placement_count += 1
                    print(f"  [LAB] Sensor {sensor_id} -> fog_{optimal_node_id} "
                          f"(score: {score:.4f}, util: {utilization:.1f}%)")
        
        print(f"\n[LAB] Placement Complete: {placement_count} modules placed")
        self._print_load_distribution()
        print(f"{'='*70}\n")
    
    def _find_optimal_node(self, sensor) -> Tuple[Optional[int], float]:
        """Find optimal node using weighted scoring"""
        best_score = float("-inf")
        best_node_id = None
        
        # Normalize factors for scoring
        max_distance = self._get_max_distance()
        
        for i, fog_node in enumerate(self.digital_twin.fog_nodes):
            # Calculate distance component
            distance = self._calculate_distance(sensor.coordinates, fog_node.coordinates)
            normalized_distance = distance / max_distance if max_distance > 0 else 0
            
            # Calculate load component
            current_utilization = self.node_loads[i] / self.node_capacities[i]
            
            # Avoid overloaded nodes (utilization > 95%)
            if current_utilization > 0.95:
                continue
            
            # Calculate weighted score (higher is better)
            # score = α·(1 - utilization) + β·(1 - normalized_distance)
            load_score = 1.0 - current_utilization
            distance_score = 1.0 - normalized_distance
            
            total_score = self.alpha * load_score + self.beta * distance_score
            
            if total_score > best_score:
                best_score = total_score
                best_node_id = i
        
        return best_node_id, best_score
    
    def _get_max_distance(self) -> float:
        """Calculate maximum possible distance in environment"""
        width = self.digital_twin.width
        height = self.digital_twin.height
        return math.sqrt(width**2 + height**2)
    
    def _calculate_distance(self, coord1: Tuple[float, float], 
                           coord2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance"""
        dx = coord1[0] - coord2[0]
        dy = coord1[1] - coord2[1]
        return math.sqrt(dx**2 + dy**2)
    
    def _print_load_distribution(self):
        """Print load distribution across nodes"""
        print(f"\n[LAB] Load Distribution:")
        for i in range(len(self.digital_twin.fog_nodes)):
            utilization = (self.node_loads[i] / self.node_capacities[i] * 100)
            assignments = len(self.module_assignments.get(i, []))
            print(f"  fog_{i}: {assignments} sensors, {utilization:.1f}% utilized")
    
    def _extract_sensor_id(self, module_name: str) -> int:
        """Extract sensor ID from module name"""
        parts = module_name.split("_")
        for part in reversed(parts):
            if part.isdigit():
                return int(part)
        return 0
    
    def _find_sensor_by_id(self, sensor_id: int):
        """Find sensor device by ID"""
        for sensor in self.digital_twin.sensors:
            if sensor.device_id == sensor_id:
                return sensor
        return None


class MEC(Placement):
    """
    Multi-Edge Coordination (MEC) Algorithm
    
    Strategy: Distribute tasks across edge servers collaboratively using greedy 
    balancing that considers both latency and energy cost.
    
    Key Features:
    - Multi-objective optimization (latency + energy)
    - Collaborative edge resource management
    - Energy-aware placement decisions
    """
    
    def __init__(self, name: str, json_file: str, digital_twin, 
                 latency_weight: float = 0.5, energy_weight: float = 0.5):
        super().__init__(name, json_file)
        self.digital_twin = digital_twin
        self.module_assignments: Dict[int, List] = {}
        self.activation_dist = None
        
        # Multi-objective weights
        self.latency_weight = latency_weight
        self.energy_weight = energy_weight
        
        # Track node states
        self.node_loads: Dict[int, float] = {
            i: 0.0 for i in range(len(digital_twin.fog_nodes))
        }
        self.node_energy_consumption: Dict[int, float] = {
            i: 0.0 for i in range(len(digital_twin.fog_nodes))
        }
    
    def initial_allocation(self, sim, app_name: str):
        """Deploy modules using multi-edge coordination"""
        app = sim.apps[app_name]
        modules_to_place = [m for m in app.modules if "Processing_Module" in m]
        
        print(f"\n{'='*70}")
        print(f"MEC Algorithm: Placing {len(modules_to_place)} modules with coordination")
        print(f"MEC Weights: latency={self.latency_weight}, energy={self.energy_weight}")
        print(f"{'='*70}")
        
        placement_count = 0
        total_energy = 0.0
        
        for module_name in modules_to_place:
            sensor_id = self._extract_sensor_id(module_name)
            sensor = self._find_sensor_by_id(sensor_id)
            
            if sensor:
                # Find optimal node considering latency and energy
                optimal_node_id, latency_cost, energy_cost = self._find_optimal_edge(sensor)
                
                if optimal_node_id is not None:
                    node_name = f"fog_{optimal_node_id}"
                    sim.deploy_module(app_name, module_name, [], [node_name])
                    
                    # Track assignment
                    if optimal_node_id not in self.module_assignments:
                        self.module_assignments[optimal_node_id] = []
                    self.module_assignments[optimal_node_id].append(sensor)
                    
                    # Update resource tracking
                    self.node_loads[optimal_node_id] += 1
                    self.node_energy_consumption[optimal_node_id] += energy_cost
                    total_energy += energy_cost
                    
                    placement_count += 1
                    print(f"  [MEC] Sensor {sensor_id} -> fog_{optimal_node_id} "
                          f"(latency: {latency_cost:.2f}ms, energy: {energy_cost:.2f}J)")
        
        avg_energy = total_energy / placement_count if placement_count > 0 else 0
        print(f"\n[MEC] Placement Complete: {placement_count} modules placed")
        print(f"[MEC] Total Energy Consumption: {total_energy:.2f}J")
        print(f"[MEC] Average Energy per Task: {avg_energy:.2f}J")
        self._print_edge_coordination_status()
        print(f"{'='*70}\n")
    
    def _find_optimal_edge(self, sensor) -> Tuple[Optional[int], float, float]:
        """Find optimal edge node considering latency and energy"""
        best_cost = float("inf")
        best_node_id = None
        best_latency = 0.0
        best_energy = 0.0
        
        for i, fog_node in enumerate(self.digital_twin.fog_nodes):
            # Calculate latency cost (communication + computation)
            latency_cost = self._estimate_latency(sensor, fog_node, i)
            
            # Calculate energy cost
            energy_cost = self._estimate_energy(sensor, fog_node, i)
            
            # Normalize costs (0-1 range)
            normalized_latency = latency_cost / 100.0  # Assume max latency ~100ms
            normalized_energy = energy_cost / 10.0     # Assume max energy ~10J
            
            # Calculate combined cost
            total_cost = (self.latency_weight * normalized_latency + 
                         self.energy_weight * normalized_energy)
            
            if total_cost < best_cost:
                best_cost = total_cost
                best_node_id = i
                best_latency = latency_cost
                best_energy = energy_cost
        
        return best_node_id, best_latency, best_energy
    
    def _estimate_latency(self, sensor, fog_node, node_id: int) -> float:
        """Estimate latency for assignment"""
        # Distance-based communication latency
        distance = self._calculate_distance(sensor.coordinates, fog_node.coordinates)
        comm_latency = distance / 1000.0  # Simple model: 1ms per km
        
        # Load-based computation latency
        current_load = self.node_loads[node_id]
        capacity = fog_node.processingPower
        comp_latency = (current_load + 1) / capacity * 10.0  # Simple model
        
        return comm_latency + comp_latency
    
    def _estimate_energy(self, sensor, fog_node, node_id: int) -> float:
        """Estimate energy consumption for assignment"""
        # Distance-based transmission energy
        distance = self._calculate_distance(sensor.coordinates, fog_node.coordinates)
        transmission_energy = sensor.transmissionPower * (distance / 1000.0) * 0.001
        
        # Computation energy (based on workload)
        workload = sensor.averageFlowSize * sensor.averageFlowRate
        computation_energy = workload / fog_node.processingPower * 0.5
        
        # Load factor (higher load = higher energy per task)
        load_factor = 1.0 + (self.node_loads[node_id] / 10.0)
        
        return (transmission_energy + computation_energy) * load_factor
    
    def _calculate_distance(self, coord1: Tuple[float, float], 
                           coord2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance"""
        dx = coord1[0] - coord2[0]
        dy = coord1[1] - coord2[1]
        return math.sqrt(dx**2 + dy**2)
    
    def _print_edge_coordination_status(self):
        """Print coordination status across edges"""
        print(f"\n[MEC] Edge Coordination Status:")
        for i in range(len(self.digital_twin.fog_nodes)):
            load = self.node_loads[i]
            energy = self.node_energy_consumption[i]
            assignments = len(self.module_assignments.get(i, []))
            print(f"  fog_{i}: {assignments} sensors, load={load:.1f}, energy={energy:.2f}J")
    
    def _extract_sensor_id(self, module_name: str) -> int:
        """Extract sensor ID from module name"""
        parts = module_name.split("_")
        for part in reversed(parts):
            if part.isdigit():
                return int(part)
        return 0
    
    def _find_sensor_by_id(self, sensor_id: int):
        """Find sensor device by ID"""
        for sensor in self.digital_twin.sensors:
            if sensor.device_id == sensor_id:
                return sensor
        return None


class FNPA(Placement):
    """
    Fog Node Proximity Algorithm (FNPA)
    
    Strategy: Choose fog nodes nearest to sensors with resource awareness.
    Falls back to cloud if all fog nodes are saturated.
    Prioritizes minimal hop distance and bandwidth availability.
    
    Key Features:
    - Proximity-based with resource checks
    - Bandwidth-aware assignment
    - Cloud fallback for overload scenarios
    - Hop distance optimization
    """
    
    def __init__(self, name: str, json_file: str, digital_twin, 
                 resource_threshold: float = 0.85, bandwidth_threshold: float = 0.8):
        super().__init__(name, json_file)
        self.digital_twin = digital_twin
        self.module_assignments: Dict[int, List] = {}
        self.activation_dist = None
        
        # Resource management thresholds
        self.resource_threshold = resource_threshold  # Max 85% utilization
        self.bandwidth_threshold = bandwidth_threshold  # Max 80% bandwidth usage
        
        # Track node states
        self.node_loads: Dict[int, float] = {
            i: 0.0 for i in range(len(digital_twin.fog_nodes))
        }
        self.node_capacities: Dict[int, float] = {
            i: fog_node.processingPower 
            for i, fog_node in enumerate(digital_twin.fog_nodes)
        }
        self.node_bandwidth_usage: Dict[int, float] = {
            i: 0.0 for i in range(len(digital_twin.fog_nodes))
        }
        self.cloud_assignments = 0
    
    def initial_allocation(self, sim, app_name: str):
        """Deploy modules using fog node proximity algorithm"""
        app = sim.apps[app_name]
        modules_to_place = [m for m in app.modules if "Processing_Module" in m]
        
        print(f"\n{'='*70}")
        print(f"FNPA Algorithm: Placing {len(modules_to_place)} modules by proximity")
        print(f"FNPA Thresholds: resource={self.resource_threshold*100}%, "
              f"bandwidth={self.bandwidth_threshold*100}%")
        print(f"{'='*70}")
        
        placement_count = 0
        fog_count = 0
        cloud_count = 0
        
        for module_name in modules_to_place:
            sensor_id = self._extract_sensor_id(module_name)
            sensor = self._find_sensor_by_id(sensor_id)
            
            if sensor:
                # Try to find suitable fog node
                optimal_node_id = self._find_suitable_fog_node(sensor)
                
                if optimal_node_id is not None:
                    # Assign to fog node
                    node_name = f"fog_{optimal_node_id}"
                    sim.deploy_module(app_name, module_name, [], [node_name])
                    
                    if optimal_node_id not in self.module_assignments:
                        self.module_assignments[optimal_node_id] = []
                    self.module_assignments[optimal_node_id].append(sensor)
                    
                    # Update resource tracking
                    workload = sensor.averageFlowSize * sensor.averageFlowRate
                    self.node_loads[optimal_node_id] += workload
                    
                    bandwidth_demand = sensor.flowTrafficSize * sensor.averageFlowRate
                    fog_node = self.digital_twin.fog_nodes[optimal_node_id]
                    self.node_bandwidth_usage[optimal_node_id] += bandwidth_demand / fog_node.bandwidth
                    
                    fog_count += 1
                    utilization = (self.node_loads[optimal_node_id] / 
                                 self.node_capacities[optimal_node_id] * 100)
                    
                    print(f"  [FNPA] Sensor {sensor_id} -> fog_{optimal_node_id} "
                          f"(util: {utilization:.1f}%)")
                else:
                    # Fallback to cloud
                    node_name = "cloud"
                    sim.deploy_module(app_name, module_name, [], [node_name])
                    self.cloud_assignments += 1
                    cloud_count += 1
                    
                    print(f"  [FNPA] Sensor {sensor_id} -> CLOUD (fog nodes saturated)")
                
                placement_count += 1
        
        print(f"\n[FNPA] Placement Complete: {placement_count} modules placed")
        print(f"[FNPA] Fog Placements: {fog_count}, Cloud Fallbacks: {cloud_count}")
        self._print_resource_status()
        print(f"{'='*70}\n")
    
    def _find_suitable_fog_node(self, sensor) -> Optional[int]:
        """Find nearest fog node with available resources"""
        # Create list of (distance, node_id) pairs
        candidates = []
        
        for i, fog_node in enumerate(self.digital_twin.fog_nodes):
            # Check resource availability
            utilization = self.node_loads[i] / self.node_capacities[i]
            bandwidth_util = self.node_bandwidth_usage[i]
            
            # Skip overloaded nodes
            if utilization >= self.resource_threshold:
                continue
            if bandwidth_util >= self.bandwidth_threshold:
                continue
            
            # Calculate distance (hop distance approximated by Euclidean distance)
            distance = self._calculate_distance(sensor.coordinates, fog_node.coordinates)
            
            candidates.append((distance, i))
        
        # No suitable fog node found
        if not candidates:
            return None
        
        # Sort by distance and select nearest
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]
    
    def _calculate_distance(self, coord1: Tuple[float, float], 
                           coord2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance (approximates hop distance)"""
        dx = coord1[0] - coord2[0]
        dy = coord1[1] - coord2[1]
        return math.sqrt(dx**2 + dy**2)
    
    def _print_resource_status(self):
        """Print resource utilization status"""
        print(f"\n[FNPA] Resource Utilization:")
        for i in range(len(self.digital_twin.fog_nodes)):
            utilization = (self.node_loads[i] / self.node_capacities[i] * 100)
            bandwidth_util = self.node_bandwidth_usage[i] * 100
            assignments = len(self.module_assignments.get(i, []))
            status = "SATURATED" if utilization >= self.resource_threshold * 100 else "AVAILABLE"
            print(f"  fog_{i}: {assignments} sensors, CPU={utilization:.1f}%, "
                  f"BW={bandwidth_util:.1f}% [{status}]")
        if self.cloud_assignments > 0:
            print(f"  cloud: {self.cloud_assignments} sensors (fallback)")
    
    def _extract_sensor_id(self, module_name: str) -> int:
        """Extract sensor ID from module name"""
        parts = module_name.split("_")
        for part in reversed(parts):
            if part.isdigit():
                return int(part)
        return 0
    
    def _find_sensor_by_id(self, sensor_id: int):
        """Find sensor device by ID"""
        for sensor in self.digital_twin.sensors:
            if sensor.device_id == sensor_id:
                return sensor
        return None
