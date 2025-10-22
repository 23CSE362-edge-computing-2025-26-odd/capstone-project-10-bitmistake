"""
Centralized Algorithm Registry
Resolves Major Issue #17 - Single source of truth for all placement algorithms
"""

from typing import Dict, Type, List, Optional, Callable


class AlgorithmRegistry:
    """
    Central registry for all placement algorithms.
    Provides single source of truth, avoiding scattered algorithm imports.
    """
    
    def __init__(self):
        """Initialize algorithm registry"""
        self._algorithms: Dict[str, Type] = {}
        self._metadata: Dict[str, dict] = {}
    
    def register(
        self,
        name: str,
        algorithm_class: Type,
        description: str = "",
        category: str = "general",
        requires_ml: bool = False
    ) -> None:
        """
        Register an algorithm.
        
        Args:
            name: Algorithm identifier (e.g., 'OLB', 'LBS')
            algorithm_class: The placement class
            description: Human-readable description
            category: Algorithm category (e.g., 'distance', 'load', 'hybrid')
            requires_ml: Whether algorithm requires ML models
        """
        self._algorithms[name] = algorithm_class
        self._metadata[name] = {
            'description': description,
            'category': category,
            'requires_ml': requires_ml,
            'class_name': algorithm_class.__name__
        }
    
    def get(self, name: str) -> Optional[Type]:
        """
        Get algorithm class by name.
        
        Args:
            name: Algorithm identifier
            
        Returns:
            Algorithm class or None if not found
        """
        return self._algorithms.get(name)
    
    def get_all(self) -> Dict[str, Type]:
        """Get all registered algorithms"""
        return self._algorithms.copy()
    
    def get_names(self) -> List[str]:
        """Get list of all registered algorithm names"""
        return list(self._algorithms.keys())
    
    def get_by_category(self, category: str) -> Dict[str, Type]:
        """Get algorithms filtered by category"""
        return {
            name: cls
            for name, cls in self._algorithms.items()
            if self._metadata[name]['category'] == category
        }
    
    def get_metadata(self, name: str) -> Optional[dict]:
        """Get algorithm metadata"""
        return self._metadata.get(name)
    
    def exists(self, name: str) -> bool:
        """Check if algorithm is registered"""
        return name in self._algorithms
    
    def unregister(self, name: str) -> bool:
        """
        Unregister an algorithm.
        
        Args:
            name: Algorithm identifier
            
        Returns:
            True if unregistered, False if not found
        """
        if name in self._algorithms:
            del self._algorithms[name]
            del self._metadata[name]
            return True
        return False
    
    def get_available_algorithms(self, include_ml: bool = True) -> List[str]:
        """
        Get list of available algorithms based on requirements.
        
        Args:
            include_ml: Whether to include ML-dependent algorithms
            
        Returns:
            List of available algorithm names
        """
        if include_ml:
            return self.get_names()
        
        return [
            name
            for name, meta in self._metadata.items()
            if not meta['requires_ml']
        ]
    
    def __len__(self) -> int:
        """Return number of registered algorithms"""
        return len(self._algorithms)
    
    def __contains__(self, name: str) -> bool:
        """Check if algorithm is registered using 'in' operator"""
        return name in self._algorithms
    
    def __repr__(self) -> str:
        """String representation"""
        return f"AlgorithmRegistry({len(self)} algorithms: {', '.join(self.get_names())})"


# Global registry instance
_global_registry = AlgorithmRegistry()


def get_registry() -> AlgorithmRegistry:
    """Get the global algorithm registry instance"""
    return _global_registry


def register_algorithm(
    name: str,
    algorithm_class: Type,
    description: str = "",
    category: str = "general",
    requires_ml: bool = False
) -> None:
    """
    Convenience function to register algorithm in global registry.
    
    Args:
        name: Algorithm identifier
        algorithm_class: The placement class
        description: Human-readable description
        category: Algorithm category
        requires_ml: Whether algorithm requires ML models
    """
    _global_registry.register(name, algorithm_class, description, category, requires_ml)


def get_algorithm(name: str) -> Optional[Type]:
    """
    Convenience function to get algorithm from global registry.
    
    Args:
        name: Algorithm identifier
        
    Returns:
        Algorithm class or None
    """
    return _global_registry.get(name)


def initialize_default_registry():
    """
    Initialize registry with all available algorithms.
    Called during package initialization.
    """
    from .olb_algorithm import OLBPlacement
    from .comparison_algorithms import LBS, LAB, MEC, FNPA
    
    # Register core algorithms
    register_algorithm(
        'OLB',
        OLBPlacement,
        description='Optimized Load Balancing with latency optimization',
        category='hybrid',
        requires_ml=False
    )
    
    register_algorithm(
        'LBS',
        LBS,
        description='Location-Based Selection - minimizes distance',
        category='distance',
        requires_ml=False
    )
    
    register_algorithm(
        'LAB',
        LAB,
        description='Load-Aware Balancing - dynamic load distribution',
        category='load',
        requires_ml=False
    )
    
    register_algorithm(
        'MEC',
        MEC,
        description='Multi-Edge Coordination - latency+energy optimization',
        category='hybrid',
        requires_ml=False
    )
    
    register_algorithm(
        'FNPA',
        FNPA,
        description='edge Node Proximity Algorithm with resource awareness',
        category='hybrid',
        requires_ml=False
    )
    
    # Try to register ML-based algorithms if available
    try:
        from .predictive_placement import PredictiveLatencyPlacement, ForecastBasedPlacement
        
        register_algorithm(
            'Predictive',
            PredictiveLatencyPlacement,
            description='LSTM-based predictive latency placement',
            category='ml',
            requires_ml=True
        )
        
        register_algorithm(
            'Forecast',
            ForecastBasedPlacement,
            description='Time-series forecast-based placement',
            category='ml',
            requires_ml=True
        )
    except ImportError:
        pass  # ML algorithms not available


# Export public API
__all__ = [
    'AlgorithmRegistry',
    'get_registry',
    'register_algorithm',
    'get_algorithm',
    'initialize_default_registry'
]

