"""
Unified Simulation Orchestrator
Resolves Major Issue #9 - Consolidates duplicate entry point logic
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any


def setup_directories(required_dirs: Optional[List[str]] = None) -> None:
    """
    Create required directories if they don't exist.
    Resolves Major Issue #13 - Duplicate directory creation logic.
    
    Args:
        required_dirs: List of directory paths to create. Defaults to standard set.
    """
    if required_dirs is None:
        required_dirs = ["logs", "data", "results", "plots", "reports"]
    
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)


def load_config(
    config_path: str,
    config_type: str = "json"
) -> Dict[str, Any]:
    """
    Load configuration file with validation.
    Resolves Major Issue #16 - Duplicate config loading.
    
    Args:
        config_path: Path to configuration file
        config_type: Configuration file type (json, yaml, etc.)
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    if config_type == "json":
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        raise ValueError(f"Unsupported config type: {config_type}")
    
    # Basic validation
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary")
    
    return config


class SimulationOrchestrator:
    """
    Unified orchestrator for all simulation workflows.
    Eliminates duplicate logic between main.py and main_hospital_workflow.py.
    """
    
    def __init__(
        self,
        simulation_name: str,
        log_file: str = "logs/simulation.log",
        config_file: Optional[str] = None
    ):
        """
        Initialize orchestrator.
        
        Args:
            simulation_name: Name of the simulation
            log_file: Path to log file
            config_file: Optional configuration file path
        """
        self.simulation_name = simulation_name
        self.start_time = time.time()
        
        # Setup directories
        setup_directories()
        
        print(f"Initializing {simulation_name} Simulation")
        
        # Load config if provided
        self.config = None
        if config_file and os.path.exists(config_file):
            self.config = load_config(config_file)
            print(f"Loaded configuration from {config_file}")
    
    def log_phase(self, phase_number: int, phase_name: str):
        """Print simulation phase header"""
        print("")
        print("=" * 80)
        print(f"PHASE {phase_number}: {phase_name}")
        print("=" * 80)
    
    def log_success(self, message: str, duration: Optional[float] = None):
        """Print success message with optional duration"""
        if duration is not None:
            print(f"[OK] {message} ({duration:.2f}s)")
        else:
            print(f"[OK] {message}")
    
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Print error message with optional exception"""
        print(f"[ERROR] {message}")
        if exception:
            import traceback
            traceback.print_exc()
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since orchestrator initialization"""
        return time.time() - self.start_time
    
    def finalize(self):
        """Finalize simulation and print summary"""
        total_time = self.get_elapsed_time()
        print("")
        print("=" * 80)
        print("SIMULATION COMPLETE")
        print("=" * 80)
        print(f"Total execution time: {total_time:.2f}s")
        print(f"Simulation: {self.simulation_name}")


class OLBSimulationOrchestrator(SimulationOrchestrator):
    """Orchestrator for OLB (main.py) simulations"""
    
    def __init__(self):
        super().__init__(
            simulation_name="OLB Placement",
            log_file="logs/olb_simulation.log"
        )
    
    def run(self):
        """Execute OLB simulation workflow"""
        print("Starting OLB simulation workflow...")
        # Main workflow logic would go here
        # This is a template - actual implementation in main.py


class HospitalSimulationOrchestrator(SimulationOrchestrator):
    """Orchestrator for Hospital (main_hospital_workflow.py) simulations"""
    
    def __init__(self):
        super().__init__(
            simulation_name="Hospital Comparison",
            log_file="logs/hospital_comparison.log"
        )
    
    def run(self):
        """Execute hospital comparison workflow"""
        print("Starting hospital comparison workflow...")
        # Main workflow logic would go here
        # This is a template - actual implementation in main_hospital_workflow.py


def get_project_root() -> Path:
    """
    Get project root directory.
    Resolves Major Issue #28 - Hardcoded paths.
    
    Returns:
        Path object for project root
    """
    return Path(__file__).parent.parent


def get_absolute_path(relative_path: str) -> Path:
    """
    Convert relative path to absolute path from project root.
    
    Args:
        relative_path: Path relative to project root
        
    Returns:
        Absolute Path object
    """
    return get_project_root() / relative_path


# Export helper functions
__all__ = [
    "setup_directories",
    "load_config",
    "SimulationOrchestrator",
    "OLBSimulationOrchestrator", 
    "HospitalSimulationOrchestrator",
    "get_project_root",
    "get_absolute_path"
]

