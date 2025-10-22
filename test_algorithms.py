"""
Quick Test Script for New Algorithms
Tests that LBS, LAB, MEC, and FNPA algorithms work correctly
"""

import sys
import os

# Setup path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all required modules can be imported"""
    print("=" * 70)
    print("TEST 1: Testing Imports")
    print("=" * 70)
    
    try:
        from src import (
            LBS, LAB, MEC, FNPA,
            DigitalTwinEnvironment,
            SimulationConfig,
            PREDICTIVE_AVAILABLE,
            WORKLOAD_PREDICTOR_AVAILABLE
        )
        print("✓ All core imports successful")
        print(f"  - LBS: {LBS}")
        print(f"  - LAB: {LAB}")
        print(f"  - MEC: {MEC}")
        print(f"  - FNPA: {FNPA}")
        print(f"  - Predictive Available: {PREDICTIVE_AVAILABLE}")
        print(f"  - Workload Predictor Available: {WORKLOAD_PREDICTOR_AVAILABLE}")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_environment_creation():
    """Test digital twin environment creation"""
    print("\n" + "=" * 70)
    print("TEST 2: Testing Environment Creation")
    print("=" * 70)
    
    try:
        from src import DigitalTwinEnvironment, SimulationConfig
        
        config = SimulationConfig()
        environment = DigitalTwinEnvironment(
            width=config.environment_width, 
            height=config.environment_height
        )
        environment.initialize_sensors(num_sensors=10, seed=42)
        environment.initialize_fog_nodes(num_fog_nodes=3, seed=42)
        
        print(f"✓ Environment created successfully")
        print(f"  - Sensors: {len(environment.sensors)}")
        print(f"  - Fog Nodes: {len(environment.fog_nodes)}")
        print(f"  - Cloud Node: {environment.cloud_node}")
        return True
    except Exception as e:
        print(f"✗ Environment creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_algorithm_initialization():
    """Test that algorithms can be initialized"""
    print("\n" + "=" * 70)
    print("TEST 3: Testing Algorithm Initialization")
    print("=" * 70)
    
    try:
        from src import LBS, LAB, MEC, FNPA, DigitalTwinEnvironment, SimulationConfig
        
        config = SimulationConfig()
        environment = DigitalTwinEnvironment(
            width=config.environment_width, 
            height=config.environment_height
        )
        environment.initialize_sensors(num_sensors=10, seed=42)
        environment.initialize_fog_nodes(num_fog_nodes=3, seed=42)
        
        # Create temporary placement config
        placement_config = "placement_config.json"
        
        algorithms = [
            ("LBS", LBS),
            ("LAB", LAB),
            ("MEC", MEC),
            ("FNPA", FNPA),
        ]
        
        for name, AlgoClass in algorithms:
            try:
                algo = AlgoClass(name, placement_config, environment)
                print(f"✓ {name} initialized successfully")
            except Exception as e:
                print(f"✗ {name} initialization failed: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Algorithm initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hospital_comparison():
    """Test hospital comparison framework"""
    print("\n" + "=" * 70)
    print("TEST 4: Testing Hospital Comparison Framework")
    print("=" * 70)
    
    try:
        from src.hospital_comparison import HospitalComparisonRunner
        
        runner = HospitalComparisonRunner()
        print(f"✓ HospitalComparisonRunner created")
        print(f"  - Algorithms to test: {len(runner.algorithms)}")
        print(f"  - Algorithm names: {runner.algorithms}")
        print(f"  - Scenarios: {len(runner.scenarios)}")
        return True
    except Exception as e:
        print(f"✗ Hospital comparison test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("ALGORITHM REFACTOR VALIDATION TESTS")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Import Test", test_imports()))
    results.append(("Environment Creation", test_environment_creation()))
    results.append(("Algorithm Initialization", test_algorithm_initialization()))
    results.append(("Hospital Comparison", test_hospital_comparison()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
        return 0
    else:
        print(f"\n✗✗✗ {total - passed} TEST(S) FAILED ✗✗✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())

