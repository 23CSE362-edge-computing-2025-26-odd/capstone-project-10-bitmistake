"""
Simulated MQTT Protocol Layer for Hospital IoT Devices
Provides pub/sub messaging without external broker dependencies
"""

import json
import time
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MQTTMessage:
    """Represents a single MQTT message"""
    topic: str
    payload: str
    qos: int = 1
    retain: bool = False
    timestamp: float = field(default_factory=time.time)


@dataclass
class MQTTClient:
    """Represents an MQTT client (sensor or edge node)"""
    client_id: str
    is_publisher: bool = True
    is_subscriber: bool = False


class MQTTBroker:
    """Simulated MQTT Broker - manages pub/sub without external dependencies"""
    
    def __init__(self):
        self.subscriptions: Dict[str, List[Callable]] = {}
        self.message_history: Dict[str, List[MQTTMessage]] = {}
        self.retained_messages: Dict[str, MQTTMessage] = {}
        self.clients: Dict[str, MQTTClient] = {}
        self.stats = {"published": 0, "delivered": 0}
    
    def register_client(self, client_id: str, is_publisher: bool = True, is_subscriber: bool = False):
        """Register a new MQTT client"""
        self.clients[client_id] = MQTTClient(client_id, is_publisher, is_subscriber)
    
    def subscribe(self, client_id: str, topic: str, callback: Callable):
        """Subscribe client to topic with wildcard support"""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(callback)
    
    def publish(self, client_id: str, topic: str, payload: dict, qos: int = 1, retain: bool = False):
        """Publish message to topic"""
        message = MQTTMessage(
            topic=topic,
            payload=json.dumps(payload) if isinstance(payload, dict) else str(payload),
            qos=qos,
            retain=retain
        )
        
        # Store in history
        if topic not in self.message_history:
            self.message_history[topic] = []
        self.message_history[topic].append(message)
        
        # Handle retained messages
        if retain:
            self.retained_messages[topic] = message
        
        # Deliver to subscribers
        self._deliver_message(message)
        self.stats["published"] += 1
    
    def _deliver_message(self, message: MQTTMessage):
        """Deliver message to matching subscribers"""
        for topic_pattern in self.subscriptions:
            if self._topic_matches(message.topic, topic_pattern):
                for callback in self.subscriptions[topic_pattern]:
                    try:
                        callback(message)
                        self.stats["delivered"] += 1
                    except Exception as e:
                        print(f"Error delivering to subscriber: {e}")
    
    @staticmethod
    def _topic_matches(topic: str, pattern: str) -> bool:
        """Check if topic matches pattern with + and # wildcards"""
        topic_parts = topic.split('/')
        pattern_parts = pattern.split('/')
        
        for i, pattern_part in enumerate(pattern_parts):
            if pattern_part == '#':
                return True
            if pattern_part == '+':
                if i >= len(topic_parts):
                    return False
                continue
            if i >= len(topic_parts) or topic_parts[i] != pattern_part:
                return False
        
        return len(topic_parts) == len(pattern_parts)
    
    def get_retained_message(self, topic: str) -> Optional[MQTTMessage]:
        """Get last retained message for topic"""
        return self.retained_messages.get(topic)
    
    def get_message_history(self, topic: str) -> List[MQTTMessage]:
        """Get message history for topic"""
        return self.message_history.get(topic, [])
    
    def get_stats(self) -> Dict:
        """Get broker statistics"""
        return {
            "published": self.stats["published"],
            "delivered": self.stats["delivered"],
            "subscriptions": len(self.subscriptions),
            "retained_messages": len(self.retained_messages),
            "clients": len(self.clients)
        }


class MQTTSimulationEnvironment:
    """MQTT environment for simulation timeline (not real-time)"""
    
    def __init__(self):
        self.broker = MQTTBroker()
        self.simulation_time = 0
        self.messages_sent = []
        self.yafs_sim = None  # Reference to YAFS simulation for event callbacks
    
    def advance_time(self, delta_ms: float):
        """Advance simulation time"""
        self.simulation_time += delta_ms
    
    def publish_sensor_reading(self, sensor_id: str, edge_id: str, reading: dict):
        """Publish sensor reading to MQTT topic"""
        topic = f"sensor/{sensor_id}/reading"
        payload = {
            "sensor_id": sensor_id,
            "edge_node": edge_id,
            "timestamp": self.simulation_time,
            "reading": reading
        }
        self.broker.publish(sensor_id, topic, payload, qos=2, retain=False)
        self.messages_sent.append({
            "topic": topic,
            "time": self.simulation_time,
            "payload": payload
        })
    
    def publish_placement_assignment(self, sensor_id: int, edge_id: int, assignment_info: dict):
        """
        Publish placement assignment decision to MQTT.
        Connects MQTT with simulation placement decisions.
        """
        topic = f"placement/sensor_{sensor_id}/assignment"
        payload = {
            "sensor_id": sensor_id,
            "assigned_edge_node": edge_id,
            "timestamp": self.simulation_time,
            "assignment_info": assignment_info
        }
        self.broker.publish(f"sensor_{sensor_id}", topic, payload, qos=1, retain=True)
        self.messages_sent.append({
            "topic": topic,
            "time": self.simulation_time,
            "payload": payload
        })
    
    def publish_simulation_metrics(self, metrics: dict):
        """Publish simulation metrics to MQTT"""
        topic = "simulation/metrics"
        payload = {
            "timestamp": self.simulation_time,
            "metrics": metrics
        }
        self.broker.publish("simulation", topic, payload, qos=1, retain=True)
        self.messages_sent.append({
            "topic": topic,
            "time": self.simulation_time,
            "payload": payload
        })
    
    def get_statistics(self) -> Dict:
        """Get simulation statistics"""
        return {
            "simulation_time": self.simulation_time,
            "messages_sent": len(self.messages_sent),
            "broker_stats": self.broker.get_stats()
        }
    
    def connect_to_yafs_simulation(self, yafs_sim):
        """Connect MQTT environment to YAFS simulation for real-time event publishing"""
        self.yafs_sim = yafs_sim
        print("[INFO] MQTT environment connected to YAFS simulation")
    
    def publish_placement_decisions(self, placement, digital_twin):
        """
        Publish all placement decisions to MQTT after placement algorithm runs.
        This is the main integration point between placement and MQTT.
        """
        print("[INFO] Publishing placement decisions to MQTT...")
        
        # Publish each sensor-to-edge assignment
        for edge_id, sensors in placement.module_assignments.items():
            edge_node = digital_twin.edge_nodes[edge_id] if edge_id < len(digital_twin.edge_nodes) else None
            
            for sensor in sensors:
                assignment_info = {
                    "algorithm": placement.name,
                    "edge_node_id": edge_id,
                    "edge_node_coordinates": edge_node.coordinates if edge_node else None,
                    "sensor_coordinates": sensor.coordinates,
                    "distance": self._calculate_distance(sensor.coordinates, edge_node.coordinates) if edge_node else None,
                    "sensor_power": sensor.transmissionPower,
                    "edge_capacity": edge_node.processingPower if edge_node else None
                }
                
                self.publish_placement_assignment(sensor.device_id, edge_id, assignment_info)
        
        # Publish summary statistics
        total_assignments = sum(len(sensors) for sensors in placement.module_assignments.values())
        summary = {
            "algorithm": placement.name,
            "total_sensors": len(digital_twin.sensors),
            "total_edge_nodes": len(digital_twin.edge_nodes),
            "total_assignments": total_assignments,
            "assignments_per_node": {
                edge_id: len(sensors) 
                for edge_id, sensors in placement.module_assignments.items()
            }
        }
        
        topic = f"placement/{placement.name}/summary"
        self.broker.publish("placement_system", topic, summary, qos=1, retain=True)
        self.messages_sent.append({
            "topic": topic,
            "time": self.simulation_time,
            "payload": summary
        })
        
        print(f"[INFO] Published {total_assignments} placement assignments to MQTT")
    
    def publish_simulation_start(self, config: dict):
        """Publish simulation start event"""
        topic = "simulation/lifecycle/start"
        payload = {
            "timestamp": self.simulation_time,
            "config": config,
            "event": "simulation_started"
        }
        self.broker.publish("simulation", topic, payload, qos=1, retain=False)
        self.messages_sent.append({
            "topic": topic,
            "time": self.simulation_time,
            "payload": payload
        })
    
    def publish_simulation_end(self, metrics: dict):
        """Publish simulation end event with final metrics"""
        topic = "simulation/lifecycle/end"
        payload = {
            "timestamp": self.simulation_time,
            "metrics": metrics,
            "event": "simulation_completed"
        }
        self.broker.publish("simulation", topic, payload, qos=1, retain=False)
        self.messages_sent.append({
            "topic": topic,
            "time": self.simulation_time,
            "payload": payload
        })
    
    def subscribe_to_sensor_readings(self, callback: Callable):
        """Subscribe to all sensor readings"""
        self.broker.subscribe("subscriber", "sensor/+/reading", callback)
    
    def subscribe_to_placement_updates(self, callback: Callable):
        """Subscribe to placement assignment updates"""
        self.broker.subscribe("subscriber", "placement/#", callback)
    
    def subscribe_to_simulation_events(self, callback: Callable):
        """Subscribe to simulation lifecycle events"""
        self.broker.subscribe("subscriber", "simulation/#", callback)
    
    @staticmethod
    def _calculate_distance(coord1, coord2):
        """Calculate Euclidean distance between two coordinates"""
        import math
        return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)
    
    def export_mqtt_log(self, filename: str = "mqtt_messages.json"):
        """Export all MQTT messages to JSON file"""
        import json
        from pathlib import Path
        
        log_data = {
            "simulation_time": self.simulation_time,
            "total_messages": len(self.messages_sent),
            "broker_stats": self.broker.get_stats(),
            "messages": self.messages_sent
        }
        
        # Ensure logs directory exists
        Path("logs").mkdir(exist_ok=True)
        filepath = Path("logs") / filename
        
        with open(filepath, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"[INFO] MQTT log exported to {filepath}")
        return str(filepath) 