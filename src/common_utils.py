import math
from typing import Tuple, Optional, Dict, List


def extract_sensor_id(module_name: str):
    """
    Extract sensor ID from module name.
    Handles both numeric IDs (0, 1, 2) and string IDs (ICU-0, REMOTE-5).
    Returns int for numeric IDs, str for prefixed IDs.
    """
    parts = module_name.split("_")
    for part in reversed(parts):
        if part.isdigit():
            return int(part)
        # Check if it's a hyphenated ID like "ICU-0" or "REMOTE-5"
        if "-" in part:
            return part
    return 0


def calculate_euclidean_distance(
    coord1: Tuple[float, float], 
    coord2: Tuple[float, float]
) -> float:
    dx = coord1[0] - coord2[0]
    dy = coord1[1] - coord2[1]
    return math.sqrt(dx**2 + dy**2)


class SensorLookupIndex:
    
    def __init__(self, sensors):
        
        self._index: Dict[int, object] = {
            sensor.device_id: sensor 
            for sensor in sensors
        }
    
    def find_by_id(self, sensor_id: int) -> Optional[object]:
        """
        Find sensor by ID in O(1) time.
        
        Args:
            sensor_id: Sensor device ID
            
        Returns:
            SensorDevice object or None if not found
        """
        return self._index.get(sensor_id)
    
    def __len__(self) -> int:
        """Return number of sensors in index"""
        return len(self._index)
    
    def __contains__(self, sensor_id: int) -> bool:
        """Check if sensor ID exists"""
        return sensor_id in self._index


class DistanceCache:
    """
    Cache for distance calculations between sensors and edge nodes.
    
    Avoids repeated distance calculations (O(1) lookup vs O(1) computation).
    Resolves Minor Issue #42.
    """
    
    def __init__(self):
        """Initialize empty distance cache"""
        self._cache: Dict[Tuple[int, int], float] = {}
        self._hits = 0
        self._misses = 0
    
    def get_distance(
        self, 
        sensor_coords: Tuple[float, float],
        edge_coords: Tuple[float, float],
        sensor_id: int,
        edge_id: int
    ) -> float:
        """
        Get cached distance or calculate and cache it.
        
        Args:
            sensor_coords: Sensor (x, y) coordinates
            edge_coords: edge node (x, y) coordinates  
            sensor_id: Sensor device ID
            edge_id: edge node ID
            
        Returns:
            Distance between sensor and edge node
        """
        cache_key = (sensor_id, edge_id)
        
        if cache_key in self._cache:
            self._hits += 1
            return self._cache[cache_key]
        
        # Calculate and cache
        distance = calculate_euclidean_distance(sensor_coords, edge_coords)
        self._cache[cache_key] = distance
        self._misses += 1
        return distance
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache performance statistics"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate_percent": hit_rate,
            "cached_entries": len(self._cache)
        }
    
    def clear(self):
        """Clear cache and reset statistics"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0


def create_sensor_lookup_index(digital_twin) -> SensorLookupIndex:
    """
    Create optimized sensor lookup index from digital twin environment.
    
    Args:
        digital_twin: DigitalTwinEnvironment instance
        
    Returns:
        SensorLookupIndex for O(1) sensor lookups
    """
    return SensorLookupIndex(digital_twin.sensors)


def create_distance_cache() -> DistanceCache:
    """
    Create distance cache for placement algorithms.
    
    Returns:
        DistanceCache instance
    """
    return DistanceCache()


class PlacementConstants:
    """Named constants for placement algorithms"""
    
    # Utilization thresholds
    MAX_UTILIZATION = 0.95  # 95% max utilization
    CRITICAL_UTILIZATION = 0.85  # 85% triggers load balancing
    SAFE_UTILIZATION = 0.70  # 70% safe operating range
    
    # Capacity adjustment bounds
    MIN_CAPACITY_FACTOR = 0.6  # Minimum 60% of original
    MAX_CAPACITY_FACTOR = 1.5  # Maximum 150% of original
    
    # FNPA thresholds
    FNPA_RESOURCE_THRESHOLD = 0.85  # 85% CPU threshold
    FNPA_BANDWIDTH_THRESHOLD = 0.80  # 80% bandwidth threshold
    
    # Timeout values (seconds)
    SIMULATION_TIMEOUT = 300  # 5 minutes
    PREDICTION_TIMEOUT = 60   # 1 minute
    
    # Batch sizes
    DEFAULT_BATCH_SIZE = 10
    MAX_BATCH_SIZE = 100
    
    # Workload prediction constants (from main.py)
    CAPACITY_INCREASE_FACTOR = 0.3  # 30% increase for high-load nodes
    CAPACITY_DECREASE_BASE = 0.7    # 70% base for low-load nodes
    DEFAULT_AVG_LOAD = 50.0         # Default average load if no predictions
    
    # Simulation defaults
    DEFAULT_SIMULATION_TIME = 200  # Default simulation time in time units
    DEFAULT_ENVIRONMENT_WIDTH = 3000
    DEFAULT_ENVIRONMENT_HEIGHT = 2000
    
    # SLA thresholds
    DEFAULT_SLA_LATENCY_MS = 100.0  # Default SLA latency threshold
    
    # File extensions
    JSON_EXT = '.json'
    CSV_EXT = '.csv'
    H5_EXT = '.h5'
    TFLITE_EXT = '.tflite'
    PKL_EXT = '.pkl'


def validate_coordinates(coordinates: Tuple[float, float], width: float, height: float) -> bool:
    """
    Validate that coordinates are within environment bounds.
    
    Resolves part of Major Issue #23.
    
    Args:
        coordinates: (x, y) coordinate tuple
        width: Environment width
        height: Environment height
        
    Returns:
        True if coordinates are valid
    """
    x, y = coordinates
    return 0 <= x <= width and 0 <= y <= height


def validate_simulation_config(config) -> List[str]:
    """
    Validate simulation configuration parameters.
    
    Resolves Major Issue #23.
    
    Args:
        config: SimulationConfig object
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Validate environment dimensions
    if config.environment_width <= 0:
        errors.append(f"Invalid environment width: {config.environment_width}")
    if config.environment_height <= 0:
        errors.append(f"Invalid environment height: {config.environment_height}")
    
    # Validate sensor/edge node counts
    if config.num_sensors <= 0:
        errors.append(f"Invalid number of sensors: {config.num_sensors}")
    if config.num_edge_nodes <= 0:
        errors.append(f"Invalid number of edge nodes: {config.num_edge_nodes}")
    
    # Validate simulation time
    if config.simulation_time <= 0:
        errors.append(f"Invalid simulation time: {config.simulation_time}")
    
    # Check reasonable ratios
    if config.num_sensors < config.num_edge_nodes:
        errors.append(
            f"Warning: More edge nodes ({config.num_edge_nodes}) than sensors ({config.num_sensors})"
        )
    
    return errors


# Timing decorator for performance profiling (resolves Major Issue #25)
import time
import functools
from typing import Callable

def profile_execution(func: Callable) -> Callable:
    """
    Decorator to profile function execution time.
    
    Args:
        func: Function to profile
        
    Returns:
        Wrapped function with timing
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        # Log timing info
        print(f"[PROFILE] {func.__name__} completed in {duration:.4f}s")
        
        return result
    
    return wrapper


def cleanup_temporary_files(directories: List[str] = None) -> int:
    """
    Clean up temporary files and caches.
    
    Resolves Minor Issue #44.
    
    Args:
        directories: List of directories to clean (defaults to temp directories)
        
    Returns:
        Number of files deleted
    """
    import os
    import shutil
    
    if directories is None:
        directories = ["__pycache__", ".pytest_cache"]
    
    files_deleted = 0
    
    for directory in directories:
        if directory.startswith("*"):
            # Handle wildcard patterns
            import glob
            for file_path in glob.glob(f"**/{directory}", recursive=True):
                try:
                    os.remove(file_path)
                    files_deleted += 1
                except Exception as e:
                    print(f"[WARNING] Could not delete {file_path}: {e}")
        else:
            # Handle directories
            if os.path.exists(directory):
                try:
                    shutil.rmtree(directory)
                    files_deleted += 1
                    print(f"[INFO] Cleaned up directory: {directory}")
                except Exception as e:
                    print(f"[WARNING] Could not clean {directory}: {e}")
    
    return files_deleted
