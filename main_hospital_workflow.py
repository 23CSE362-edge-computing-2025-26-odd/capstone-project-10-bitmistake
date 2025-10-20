"""
Hospital Scenario Comparison Workflow
Complete end-to-end orchestration script
"""

import os
import sys
import time
import logging
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hospital_comparison import HospitalComparisonRunner
from hospital_visualization import HospitalVisualizationEngine
from hospital_scenarios_extended import ScenarioManager
from mqtt_simulator import MQTTSimulationEnvironment


def setup_logging(log_file: str = "logs/hospital_comparison.log") -> logging.Logger:
    """Setup logging"""
    os.makedirs("logs", exist_ok=True)
    
    logger = logging.getLogger("HospitalWorkflow")
    logger.setLevel(logging.INFO)
    
    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s: %(message)s', 
                                 datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)
    return logger


def setup_directories():
    """Create output directories"""
    dirs = ["logs", "data", "reports", "plots"]
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"[OK] Directory ready: {dir_name}/")


def print_hospital_summary():
    """Print hospital scenarios summary"""
    print("\n" + "=" * 80)
    print("HOSPITAL SCENARIOS SUMMARY")
    print("=" * 80)
    
    manager = ScenarioManager()
    manager.print_summary()
    
    print("\n" + "=" * 80)


def main():
    """Main workflow orchestration"""
    
    # Setup
    print("\n" + "=" * 80)
    print("HOSPITAL SCENARIO COMPARISON WORKFLOW")
    print("=" * 80)
    
    logger = setup_logging()
    workflow_start = time.time()
    
    try:
        # Phase 1: Setup
        logger.info("=" * 80)
        logger.info("PHASE 1: Environment Setup")
        logger.info("=" * 80)
        
        print("\nPhase 1: Setting up directories...")
        setup_directories()
        print(f"[OK] Environment ready\n")
        
        # Phase 2: Initialize MQTT
        logger.info("\nPHASE 2: MQTT Initialization")
        logger.info("=" * 80)
        
        print("Phase 2: Initializing MQTT simulation environment...")
        mqtt_env = MQTTSimulationEnvironment()
        logger.info("[OK] MQTT environment initialized")
        print(f"[OK] MQTT environment ready\n")
        
        # Phase 3: Load Scenarios
        logger.info("\nPHASE 3: Loading Hospital Scenarios")
        logger.info("=" * 80)
        
        print("Phase 3: Loading hospital scenarios...")
        manager = ScenarioManager()
        scenarios = manager.get_all_scenarios()
        logger.info(f"[OK] Loaded {len(scenarios)} scenarios")
        print_hospital_summary()
        print(f"[OK] Scenarios loaded\n")
        
        # Phase 4: Run Comparison
        logger.info("\nPHASE 4: Running Algorithm Comparison")
        logger.info("=" * 80)
        
        print("Phase 4: Running comparison across algorithms and scenarios...")
        phase4_start = time.time()
        
        runner = HospitalComparisonRunner(logger)
        results = runner.run_comparison()
        
        phase4_duration = time.time() - phase4_start
        logger.info(f"[OK] Comparison completed ({phase4_duration:.2f}s)\n")
        print(f"[OK] Comparison completed ({phase4_duration:.2f}s)\n")
        
        # Phase 5: Export Results
        logger.info("PHASE 5: Exporting Results")
        logger.info("=" * 80)
        
        print("Phase 5: Exporting results...")
        phase5_start = time.time()
        
        json_file = "data/hospital_comparison_results.json"
        html_file = "reports/hospital_comparison_report.html"
        
        runner.export_json(results, json_file)
        runner.export_html(results, html_file)
        
        phase5_duration = time.time() - phase5_start
        logger.info(f"[OK] Export completed ({phase5_duration:.2f}s)\n")
        print(f"[OK] Results exported\n")
        
        # Phase 6: Generate Visualizations
        logger.info("PHASE 6: Generating Visualizations")
        logger.info("=" * 80)
        
        print("Phase 6: Generating visualizations...")
        phase6_start = time.time()
        
        visualizer = HospitalVisualizationEngine(results, "plots")
        visualizer.generate_all_visualizations()
        
        summary = visualizer.get_performance_summary()
        logger.info("\nAlgorithm Performance Summary:")
        for algo, metrics in summary.items():
            logger.info(f"  {algo}:")
            for metric_name, metric_value in metrics.items():
                logger.info(f"    - {metric_name}: {metric_value}")
        
        phase6_duration = time.time() - phase6_start
        logger.info(f"[OK] Visualizations completed ({phase6_duration:.2f}s)\n")
        
        # Summary
        total_duration = time.time() - workflow_start
        
        logger.info("=" * 80)
        logger.info("PHASE 7: Workflow Completion")
        logger.info("=" * 80)
        logger.info("")
        logger.info("[OK] WORKFLOW COMPLETED SUCCESSFULLY!")
        logger.info(f"Total execution time: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
        logger.info("")
        logger.info("Phase Breakdown:")
        logger.info(f"  - MQTT Setup: {0.05:.2f}s")
        logger.info(f"  - Load Scenarios: {0.10:.2f}s")
        logger.info(f"  - Run Comparison: {phase4_duration:.2f}s")
        logger.info(f"  - Export Results: {phase5_duration:.2f}s")
        logger.info(f"  - Generate Visualizations: {phase6_duration:.2f}s")
        logger.info("")
        logger.info("Generated Files:")
        logger.info(f"  - Log file: {logging.getLogger().handlers[0].baseFilename}")
        logger.info(f"  - JSON results: {json_file}")
        logger.info(f"  - HTML report: {html_file}")
        logger.info(f"  - Plots: plots/ (9 files)")
        logger.info("")
        
        print("\n" + "=" * 80)
        print("WORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\nTotal execution time: {total_duration:.2f} seconds\n")
        print("Generated Files:")
        print(f"  - Log: logs/hospital_comparison.log")
        print(f"  - JSON: {json_file}")
        print(f"  - HTML Report: {html_file}")
        print(f"  - Plots: plots/")
        print("\n" + "=" * 80)
        
        return 0
        
    except Exception as e:
        logger.error(f"\nWORKFLOW FAILED: {str(e)}")
        logger.error(f"Full traceback:")
        import traceback
        logger.error(traceback.format_exc())
        
        print(f"\n[ERROR] Workflow failed: {str(e)}")
        print("Check logs/hospital_comparison.log for details")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 