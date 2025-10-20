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
    """Represents an MQTT client (sensor or fog node)"""
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
    
    def advance_time(self, delta_ms: float):
        """Advance simulation time"""
        self.simulation_time += delta_ms
    
    def publish_sensor_reading(self, sensor_id: str, fog_id: str, reading: dict):
        """Publish sensor reading to MQTT topic"""
        topic = f"sensor/{sensor_id}/reading"
        payload = {
            "sensor_id": sensor_id,
            "fog_node": fog_id,
            "timestamp": self.simulation_time,
            "reading": reading
        }
        self.broker.publish(sensor_id, topic, payload, qos=2, retain=False)
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