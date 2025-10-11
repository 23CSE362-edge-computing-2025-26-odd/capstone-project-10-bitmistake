import sys
import os
import subprocess


def check_dependencies():
    print("="*80)
    print("CHECKING DEPENDENCIES")
    print("="*80 + "\n")
    
    required_packages = {
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'pandas': 'pandas',
        'yafs': 'yafs',
    }
    
    missing = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name} installed")
        except ImportError:
            print(f"✗ {package_name} NOT installed")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    print("\n✓ All dependencies installed\n")
    return True


def check_directories():
    print("="*80)
    print("CHECKING DIRECTORIES")
    print("="*80 + "\n")
    
    required_dirs = ['src', 'experiments', 'config']
    optional_dirs = ['results', 'data', 'reports', 'plots']
    
    all_good = True
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✓ {directory}/ exists")
        else:
            print(f"✗ {directory}/ NOT found")
            all_good = False
    
    print("\nCreating output directories...")
    for directory in optional_dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ {directory}/ ready")
    
    if not all_good:
        print("\n⚠ Some required directories missing")
        return False
    
    print("\n✓ All directories ready\n")
    return True


def check_source_files():
    print("="*80)
    print("CHECKING SOURCE FILES")
    print("="*80 + "\n")
    
    required_files = [
        'src/__init__.py',
        'src/olb_algorithm.py',
        'src/predictive_placement.py',
        'src/workload_models.py',
        'src/devices.py',
        'src/environment.py',
        'src/yafs_integration.py',
        'src/utils.py',
    ]
    
    all_good = True
    
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"✓ {filepath}")
        else:
            print(f"✗ {filepath} NOT found")
            all_good = False
    
    if not all_good:
        print("\n⚠ Some source files missing")
        return False
    
    print("\n✓ All source files present\n")
    return True


def check_imports():
    print("="*80)
    print("CHECKING IMPORTS")
    print("="*80 + "\n")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
        
        print("Importing core modules...")
        from src import (
            DigitalTwinEnvironment,
            OLBPlacement,
            PredictiveLatencyPlacement,
            ForecastBasedPlacement,
            PatternBasedWorkloadGenerator,
            PerformanceMetrics,
            SimulationVisualizer,
            create_placement_json,
            create_smart_healthcare_application,
            create_yafs_topology,
        )
        print("✓ All core imports successful\n")
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}\n")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}\n")
        return False


def run_quick_test():
    print("="*80)
    print("RUNNING QUICK TEST")
    print("="*80 + "\n")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
        
        from src import DigitalTwinEnvironment
        
        print("Creating test environment...")
        env = DigitalTwinEnvironment(1000, 1000)
        env.initialize_sensors(5, seed=42)
        env.initialize_fog_nodes(3, seed=42)
        
        print(f"✓ Created environment with {len(env.sensors)} sensors and {len(env.fog_nodes)} fog nodes")
        print("✓ Quick test passed\n")
        return True
        
    except Exception as e:
        print(f"✗ Quick test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def run_pipeline():
    print("="*80)
    print("RUNNING COMPLETE PIPELINE")
    print("="*80 + "\n")
    
    print("This will take 10-15 minutes...")
    print("Press Ctrl+C to cancel\n")
    
    try:
        import time
        time.sleep(2)
        
        result = subprocess.run(
            [sys.executable, "run_complete_pipeline.py"],
            check=True,
            capture_output=False
        )
        
        print("\n" + "="*80)
        print("✓ PIPELINE COMPLETED SUCCESSFULLY")
        print("="*80 + "\n")
        
        print("Check output in:")
        print("  - data/complete_pipeline_*.json")
        print("  - reports/complete_pipeline_*.txt")
        print("  - plots/scenario*_*.png")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Pipeline failed with exit code {e.returncode}")
        return False
    except KeyboardInterrupt:
        print("\n\n⚠ Pipeline cancelled by user")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*80)
    print("SAFE PIPELINE RUNNER")
    print("="*80 + "\n")
    
    print("This script will:")
    print("1. Check all dependencies")
    print("2. Verify directory structure")
    print("3. Check source files")
    print("4. Test imports")
    print("5. Run quick test")
    print("6. Execute complete pipeline\n")
    
    input("Press Enter to start pre-flight checks...")
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Source Files", check_source_files),
        ("Imports", check_imports),
        ("Quick Test", run_quick_test),
    ]
    
    for check_name, check_func in checks:
        if not check_func():
            print(f"\n✗ {check_name} check failed!")
            print("\nPlease fix the issues above and try again.")
            return False
    
    print("="*80)
    print("✓ ALL PRE-FLIGHT CHECKS PASSED")
    print("="*80 + "\n")
    
    response = input("Ready to run complete pipeline? (y/n): ").strip().lower()
    
    if response == 'y':
        return run_pipeline()
    else:
        print("\nCancelled. Run this script again when ready.")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
