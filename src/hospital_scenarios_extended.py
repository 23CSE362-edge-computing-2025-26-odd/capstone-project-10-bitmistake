"""
Hospital Scenario Definitions for Comparison
Three distinct scenarios: ICU Monitoring, Patient Wards, Remote Patient Monitoring
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random


@dataclass
class SensorConfig:
    """Configuration for a sensor device"""
    sensor_id: str
    sensor_type: str  # ECG, SpO2, BP, TEMP, ENV, ACTIVITY
    data_rate: str    # high, medium, low
    criticality: str  # critical, important, routine
    data_size_bytes: int
    frequency_hz: float
    coordinates: Optional[tuple] = None  # (x, y) coordinates - generated if None


class HospitalScenario:
    """Base class for hospital scenarios"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.sensors: List[SensorConfig] = []
        self.fog_nodes = 4
        self.data_rates: Dict[str, int] = {}
        self.criticalities: Dict[str, int] = {}
        self.sensor_types: Dict[str, int] = {}
    
    def get_info(self) -> Dict:
        """Get scenario information"""
        return {
            "name": self.name,
            "description": self.description,
            "total_sensors": len(self.sensors),
            "fog_nodes": self.fog_nodes,
            "data_rates": self.data_rates,
            "criticalities": self.criticalities,
            "sensor_types": self.sensor_types,
            "avg_data_size": sum(s.data_size_bytes for s in self.sensors) / len(self.sensors) if self.sensors else 0,
            "avg_frequency": sum(s.frequency_hz for s in self.sensors) / len(self.sensors) if self.sensors else 0
        }


class ICUMonitoringScenario(HospitalScenario):
    """ICU Monitoring - Critical, concentrated deployment"""
    
    def __init__(self):
        super().__init__(
            name="ICU Monitoring",
            description="Intensive Care Unit with critical patient monitoring"
        )
        self.fog_nodes = 5
        self._create_sensors()
    
    def _create_sensors(self):
        """Create ICU sensors"""
        sensor_types_list = ["ECG", "SpO2", "BP", "TEMP"]
        criticalities_list = ["critical", "important", "routine"]
        data_rates_list = ["high", "medium", "low"]
        
        # 60 sensors total: 30 high, 15 medium, 15 low
        sensor_id = 0
        
        # High rate sensors (critical care)
        for i in range(30):
            sensor_type = sensor_types_list[i % len(sensor_types_list)]
            self.sensors.append(SensorConfig(
                sensor_id=f"ICU-{sensor_id}",
                sensor_type=sensor_type,
                data_rate="high",
                criticality="critical",
                data_size_bytes=256,
                frequency_hz=100.0
            ))
            sensor_id += 1
        
        # Medium rate sensors
        for i in range(15):
            sensor_type = sensor_types_list[i % len(sensor_types_list)]
            self.sensors.append(SensorConfig(
                sensor_id=f"ICU-{sensor_id}",
                sensor_type=sensor_type,
                data_rate="medium",
                criticality="important",
                data_size_bytes=128,
                frequency_hz=30.0
            ))
            sensor_id += 1
        
        # Low rate sensors
        for i in range(15):
            sensor_type = sensor_types_list[i % len(sensor_types_list)]
            self.sensors.append(SensorConfig(
                sensor_id=f"ICU-{sensor_id}",
                sensor_type=sensor_type,
                data_rate="low",
                criticality="routine",
                data_size_bytes=64,
                frequency_hz=10.0
            ))
            sensor_id += 1
        
        self._update_stats()
    
    def _update_stats(self):
        """Update scenario statistics"""
        self.data_rates = {"high": 30, "medium": 15, "low": 15}
        self.criticalities = {"critical": 30, "important": 15, "routine": 15}
        self.sensor_types = {"ECG": 15, "SpO2": 15, "BP": 15, "TEMP": 15}


class PatientWardsScenario(HospitalScenario):
    """Patient Wards - Mixed criticality, distributed deployment"""
    
    def __init__(self):
        super().__init__(
            name="Patient Wards",
            description="Hospital ward with diverse patient monitoring"
        )
        self.fog_nodes = 4
        self._create_sensors()
    
    def _create_sensors(self):
        """Create ward sensors"""
        sensor_types_list = ["ECG", "SpO2", "TEMP", "ENV"]
        
        # 96 sensors: 48 medium, 48 low
        sensor_id = 0
        
        # Medium rate sensors
        for i in range(48):
            sensor_type = sensor_types_list[i % len(sensor_types_list)]
            self.sensors.append(SensorConfig(
                sensor_id=f"WARD-{sensor_id}",
                sensor_type=sensor_type,
                data_rate="medium",
                criticality="important",
                data_size_bytes=128,
                frequency_hz=20.0
            ))
            sensor_id += 1
        
        # Low rate sensors
        for i in range(48):
            sensor_type = sensor_types_list[i % len(sensor_types_list)]
            self.sensors.append(SensorConfig(
                sensor_id=f"WARD-{sensor_id}",
                sensor_type=sensor_type,
                data_rate="low",
                criticality="routine",
                data_size_bytes=64,
                frequency_hz=5.0
            ))
            sensor_id += 1
        
        self._update_stats()
    
    def _update_stats(self):
        """Update scenario statistics"""
        self.data_rates = {"medium": 48, "low": 48}
        self.criticalities = {"important": 48, "routine": 48}
        self.sensor_types = {"ECG": 24, "SpO2": 24, "TEMP": 24, "ENV": 24}


class RemotePatientMonitoringScenario(HospitalScenario):
    """Remote Patient Monitoring - Wide geographic spread"""
    
    def __init__(self):
        super().__init__(
            name="Remote Patient Monitoring",
            description="Home-based patient monitoring across geographic area"
        )
        self.fog_nodes = 4
        self._create_sensors()
    
    def _create_sensors(self):
        """Create remote monitoring sensors"""
        sensor_types_list = ["ECG", "BP", "TEMP", "ACTIVITY"]
        
        # 32 sensors: 5 high, 12 medium, 15 low
        sensor_id = 0
        
        # High rate critical sensors
        for i in range(5):
            sensor_type = sensor_types_list[i % len(sensor_types_list)]
            self.sensors.append(SensorConfig(
                sensor_id=f"REMOTE-{sensor_id}",
                sensor_type=sensor_type,
                data_rate="high",
                criticality="critical",
                data_size_bytes=256,
                frequency_hz=50.0
            ))
            sensor_id += 1
        
        # Medium rate sensors
        for i in range(12):
            sensor_type = sensor_types_list[i % len(sensor_types_list)]
            self.sensors.append(SensorConfig(
                sensor_id=f"REMOTE-{sensor_id}",
                sensor_type=sensor_type,
                data_rate="medium",
                criticality="important",
                data_size_bytes=128,
                frequency_hz=15.0
            ))
            sensor_id += 1
        
        # Low rate sensors
        for i in range(15):
            sensor_type = sensor_types_list[i % len(sensor_types_list)]
            self.sensors.append(SensorConfig(
                sensor_id=f"REMOTE-{sensor_id}",
                sensor_type=sensor_type,
                data_rate="low",
                criticality="routine",
                data_size_bytes=64,
                frequency_hz=2.0
            ))
            sensor_id += 1
        
        self._update_stats()
    
    def _update_stats(self):
        """Update scenario statistics"""
        self.data_rates = {"high": 5, "medium": 12, "low": 15}
        self.criticalities = {"critical": 10, "important": 14, "routine": 8}
        self.sensor_types = {"ECG": 5, "BP": 12, "TEMP": 7, "ACTIVITY": 8}


class ScenarioManager:
    """Manages all hospital scenarios"""
    
    def __init__(self):
        self.scenarios = {
            "icu": ICUMonitoringScenario(),
            "wards": PatientWardsScenario(),
            "remote": RemotePatientMonitoringScenario()
        }
    
    def get_scenario(self, scenario_name: str) -> HospitalScenario:
        """Get scenario by name"""
        return self.scenarios.get(scenario_name)
    
    def get_all_scenarios(self) -> List[HospitalScenario]:
        """Get all scenarios"""
        return list(self.scenarios.values())
    
    def print_summary(self):
        """Print scenario summary"""
        for scenario in self.get_all_scenarios():
            info = scenario.get_info()
            print(f"\n{info['name']}")
            print("-" * 60)
            print(f"  Description: {info['description']}")
            print(f"  Total Sensors: {info['total_sensors']}")
            print(f"  Fog Nodes: {info['fog_nodes']}")
            print(f"  Data Rates: {info['data_rates']}")
            print(f"  Criticalities: {info['criticalities']}")
            print(f"  Sensor Types: {info['sensor_types']}")
            print(f"  Avg Data Size: {info['avg_data_size']:.0f} bytes")
            print(f"  Avg Frequency: {info['avg_frequency']:.2f} Hz")

