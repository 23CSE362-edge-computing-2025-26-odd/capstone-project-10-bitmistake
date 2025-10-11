import sys
import os
import subprocess


def print_banner():
    print("\n" + "="*80)
    print("  PREDICTIVE PLACEMENT PIPELINE LAUNCHER")
    print("="*80 + "\n")


def print_menu():
    print("Available Pipelines:\n")
    
    print("1. Quick Demo Pipeline (5 minutes)")
    print("   - Basic demonstration of 3 algorithms")
    print("   - Single environment configuration")
    print("   - Generates plots and report")
    print("   - Best for: First-time users, quick overview\n")
    
    print("2. Complete Pipeline (10-15 minutes)")
    print("   - 4 comprehensive scenarios")
    print("   - Baseline, patterns, scalability, healthcare")
    print("   - Multiple algorithm comparisons")
    print("   - Best for: Full evaluation, research results\n")
    
    print("3. Predictive vs Reactive Study (15-20 minutes)")
    print("   - Detailed workload pattern analysis")
    print("   - Healthcare scenario evaluation")
    print("   - Comprehensive comparison report")
    print("   - Best for: Research papers, detailed analysis\n")
    
    print("4. Validation Tests")
    print("   - Validate all improvements")
    print("   - Test predictive placement components")
    print("   - Verify installation")
    print("   - Best for: Debugging, verification\n")
    
    print("5. View Documentation")
    print("   - Open pipeline guide")
    print("   - View predictive placement guide")
    print("   - Read technical summary\n")
    
    print("0. Exit\n")


def run_quick_demo():
    print("\n" + "="*80)
    print("  RUNNING QUICK DEMO PIPELINE")
    print("="*80 + "\n")
    
    try:
        subprocess.run([sys.executable, "pipeline_demo.py"], check=True)
        print("\n✓ Quick demo completed successfully!")
        print("  Check plots/ and reports/ directories for results")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Quick demo failed: {e}")
    except FileNotFoundError:
        print("\n✗ pipeline_demo.py not found")


def run_complete_pipeline():
    print("\n" + "="*80)
    print("  RUNNING COMPLETE PIPELINE")
    print("="*80 + "\n")
    
    print("This will take 10-15 minutes and run multiple scenarios.")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        return
    
    try:
        subprocess.run([sys.executable, "run_complete_pipeline.py"], check=True)
        print("\n✓ Complete pipeline finished successfully!")
        print("  Check data/ and reports/ directories for comprehensive results")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Complete pipeline failed: {e}")
    except FileNotFoundError:
        print("\n✗ run_complete_pipeline.py not found")


def run_predictive_study():
    print("\n" + "="*80)
    print("  RUNNING PREDICTIVE VS REACTIVE STUDY")
    print("="*80 + "\n")
    
    print("This will take 15-20 minutes and test multiple patterns.")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        return
    
    try:
        subprocess.run([
            sys.executable,
            os.path.join("experiments", "predictive_vs_reactive_comparison.py")
        ], check=True)
        print("\n✓ Predictive study completed successfully!")
        print("  Check data/ and reports/ directories for detailed analysis")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Predictive study failed: {e}")
    except FileNotFoundError:
        print("\n✗ experiments/predictive_vs_reactive_comparison.py not found")


def run_validation():
    print("\n" + "="*80)
    print("  RUNNING VALIDATION TESTS")
    print("="*80 + "\n")
    
    print("Running improvement validations...")
    try:
        subprocess.run([sys.executable, "validate_improvements.py"], check=True)
        print("\n✓ Improvement validations passed!")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Improvement validations failed: {e}")
    except FileNotFoundError:
        print("\n✗ validate_improvements.py not found")
    
    print("\nRunning predictive placement validations...")
    try:
        subprocess.run([sys.executable, "validate_predictive_placement.py"], check=True)
        print("\n✓ Predictive placement validations passed!")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Predictive placement validations failed: {e}")
    except FileNotFoundError:
        print("\n✗ validate_predictive_placement.py not found")


def view_documentation():
    print("\n" + "="*80)
    print("  DOCUMENTATION")
    print("="*80 + "\n")
    
    docs = [
        ("PIPELINE_GUIDE.md", "Complete pipeline guide"),
        ("PREDICTIVE_PLACEMENT_GUIDE.md", "Predictive placement detailed guide"),
        ("PREDICTIVE_PLACEMENT_SUMMARY.md", "Technical summary"),
        ("README_PREDICTIVE_PLACEMENT.md", "Quick start guide"),
        ("TECHNICAL_IMPROVEMENTS_SUMMARY.md", "Technical improvements"),
    ]
    
    print("Available documentation:\n")
    for i, (filename, description) in enumerate(docs, 1):
        exists = "✓" if os.path.exists(filename) else "✗"
        print(f"{i}. {exists} {filename}")
        print(f"   {description}\n")
    
    print("Open these files in your text editor or IDE to read.")
    input("\nPress Enter to continue...")


def main():
    while True:
        print_banner()
        print_menu()
        
        try:
            choice = input("Select option (0-5): ").strip()
            
            if choice == "0":
                print("\nExiting. Thank you!")
                break
            elif choice == "1":
                run_quick_demo()
            elif choice == "2":
                run_complete_pipeline()
            elif choice == "3":
                run_predictive_study()
            elif choice == "4":
                run_validation()
            elif choice == "5":
                view_documentation()
            else:
                print("\n✗ Invalid option. Please select 0-5.")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Exiting.")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
