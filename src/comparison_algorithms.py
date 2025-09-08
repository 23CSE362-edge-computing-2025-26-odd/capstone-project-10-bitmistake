from yafs import Placement
import random
import math

class RandomPlacement(Placement):
    """Random placement algorithm for comparison"""
    def __init__(self, name, json_file, digital_twin):
        super().__init__(name, json_file)
        self.digital_twin = digital_twin
        self.module_assignments = {}
        self.activation_dist = None
    
    def initial_allocation(self, sim, app_name):
        app = sim.apps[app_name]
        modules_to_place = [m for m in app.modules if "Processing_Module" in m]
        
        print(f"Random: Placing {len(modules_to_place)} modules randomly...")
        
        for module_name in modules_to_place:
            fog_node_id = random.randint(0, len(self.digital_twin.fog_nodes) - 1)
            node_name = f"fog_{fog_node_id}"
            sim.deploy_module(app_name, module_name, [], [node_name])
            
            if fog_node_id not in self.module_assignments:
                self.module_assignments[fog_node_id] = []
            sensor_id = self._extract_sensor_id(module_name)
            sensor = self._find_sensor_by_id(sensor_id)
            if sensor:
                self.module_assignments[fog_node_id].append(sensor)
                print(f"Random: {module_name} -> fog_{fog_node_id}")
    
    def _extract_sensor_id(self, module_name):
        parts = module_name.split("_")
        for part in reversed(parts):
            if part.isdigit():
                return int(part)
        return 0
    
    def _find_sensor_by_id(self, sensor_id):
        for sensor in self.digital_twin.sensors:
            if sensor.device_id == sensor_id:
                return sensor
        return None

class DistancePlacement(Placement):
    """Distance-based placement for comparison"""
    def __init__(self, name, json_file, digital_twin):
        super().__init__(name, json_file)
        self.digital_twin = digital_twin
        self.module_assignments = {}
        self.activation_dist = None
    
    def initial_allocation(self, sim, app_name):
        app = sim.apps[app_name]
        modules_to_place = [m for m in app.modules if "Processing_Module" in m]
        
        print(f"Distance: Placing {len(modules_to_place)} modules by proximity...")
        
        for module_name in modules_to_place:
            sensor_id = self._extract_sensor_id(module_name)
            sensor = self._find_sensor_by_id(sensor_id)
            
            if sensor:
                min_distance = float('inf')
                closest_node_id = 0
                
                for i, fog_node in enumerate(self.digital_twin.fog_nodes):
                    distance = self._calculate_distance(sensor.coordinates, fog_node.coordinates)
                    if distance < min_distance:
                        min_distance = distance
                        closest_node_id = i
                
                node_name = f"fog_{closest_node_id}"
                sim.deploy_module(app_name, module_name, [], [node_name])
                
                if closest_node_id not in self.module_assignments:
                    self.module_assignments[closest_node_id] = []
                self.module_assignments[closest_node_id].append(sensor)
                print(f"Distance: {module_name} -> fog_{closest_node_id} (dist={min_distance:.1f})")
    
    def _extract_sensor_id(self, module_name):
        parts = module_name.split("_")
        for part in reversed(parts):
            if part.isdigit():
                return int(part)
        return 0
    
    def _find_sensor_by_id(self, sensor_id):
        for sensor in self.digital_twin.sensors:
            if sensor.device_id == sensor_id:
                return sensor
        return None
    
    def _calculate_distance(self, coord1, coord2):
        dx = coord1[0] - coord2[0]
        dy = coord1[1] - coord2[1]
        return math.sqrt(dx**2 + dy**2)

class LoadBalancedPlacement(Placement):
    """Simple load-balanced placement for comparison"""
    def __init__(self, name, json_file, digital_twin):
        super().__init__(name, json_file)
        self.digital_twin = digital_twin
        self.module_assignments = {}
        self.activation_dist = None
        self.node_loads = {i: 0 for i in range(len(digital_twin.fog_nodes))}
    
    def initial_allocation(self, sim, app_name):
        app = sim.apps[app_name]
        modules_to_place = [m for m in app.modules if "Processing_Module" in m]
        
        print(f"LoadBalanced: Placing {len(modules_to_place)} modules by load...")
        
        for module_name in modules_to_place:
            sensor_id = self._extract_sensor_id(module_name)
            sensor = self._find_sensor_by_id(sensor_id)
            
            if sensor:
                min_load_node = min(self.node_loads.keys(), key=lambda x: self.node_loads[x])
                
                node_name = f"fog_{min_load_node}"
                sim.deploy_module(app_name, module_name, [], [node_name])
                
                if min_load_node not in self.module_assignments:
                    self.module_assignments[min_load_node] = []
                self.module_assignments[min_load_node].append(sensor)
                
                self.node_loads[min_load_node] += 1
                print(f"LoadBalanced: {module_name} -> fog_{min_load_node} (load={self.node_loads[min_load_node]})")
    
    def _extract_sensor_id(self, module_name):
        parts = module_name.split("_")
        for part in reversed(parts):
            if part.isdigit():
                return int(part)
        return 0
    
    def _find_sensor_by_id(self, sensor_id):
        for sensor in self.digital_twin.sensors:
            if sensor.device_id == sensor_id:
                return sensor
        return None