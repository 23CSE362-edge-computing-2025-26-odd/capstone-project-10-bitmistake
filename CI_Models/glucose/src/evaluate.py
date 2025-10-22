from model import Model
from data_loader import prepare_real_data, data_quality_report
from utils import get_labelled_sequences
import pandas as pd
import numpy as np

# Data loading parameters
DATA_DIRECTORY = "path/to/your/csv/files"  # Update this path
FREQ_MINUTES = 5

# Model parameters
TIME_WORN_THRESHOLD = 0.7
GLUCOSE_THRESHOLD = 54
EVENT_DURATION_THRESHOLD = 15

def main():
    print("Loading real CGM data for evaluation...")
    
    # Load and prepare real data
    try:
        data = prepare_real_data(
            data_directory=DATA_DIRECTORY,
            freq_minutes=FREQ_MINUTES,
            file_pattern="*.csv"
        )
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    print(f"\nLoaded data for {len(data.columns)} patients")
    
    # Generate data quality report
    quality_report = data_quality_report(data)
    
    # Filter patients with sufficient data for evaluation
    min_readings_required = int(14 * 24 * 60 / FREQ_MINUTES)  # At least 2 weeks for proper evaluation
    valid_patients = quality_report[
        (quality_report['valid_readings'] >= min_readings_required) & 
        (quality_report['missing_percentage'] < 50)
    ]['patient'].tolist()
    
    print(f"Found {len(valid_patients)} patients suitable for evaluation")
    
    if len(valid_patients) == 0:
        print("No patients meet the minimum data requirements for evaluation.")
        return
    
    # Filter data
    data_filtered = data[valid_patients].copy()
    
    # Create labeled sequences
    print("\nCreating evaluation sequences...")
    sequences = get_labelled_sequences(
        data=data_filtered,
        time_worn_threshold=TIME_WORN_THRESHOLD,
        glucose_threshold=GLUCOSE_THRESHOLD,
        event_duration_threshold=EVENT_DURATION_THRESHOLD,
    )
    
    print(f"Created {len(sequences)} labeled sequences for evaluation")
    
    if len(sequences) == 0:
        print("No valid sequences created for evaluation.")
        return
    
    # Check class distribution
    labels = [s['Y'] for s in sequences]
    positive_count = sum(labels)
    negative_count = len(labels) - positive_count
    
    print(f"\nEvaluation dataset statistics:")
    print(f"- Total sequences: {len(sequences)}")
    print(f"- Negative cases: {negative_count} ({negative_count/len(labels)*100:.1f}%)")
    print(f"- Positive cases: {positive_count} ({positive_count/len(labels)*100:.1f}%)")
    
    if positive_count == 0:
        print("Warning: No positive cases in evaluation set.")
        return
    
    # Load the trained model
    print("\nLoading trained model...")
    try:
        model = Model()
        model.load(directory='model_real_data')
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Make sure you have trained the model first using train_real_data.py")
        return
    
    # Evaluate the model
    print("\nEvaluating model performance...")
    try:
        metrics = model.evaluate(sequences=sequences)
        
        print("\n" + "="*50)
        print("MODEL EVALUATION RESULTS")
        print("="*50)
        
        # Display metrics
        for metric, value in metrics.items():
            print(f"{metric.upper():>20}: {value:.4f}")
        
        # Additional analysis
        print("\n" + "-"*50)
        print("PERFORMANCE ANALYSIS")
        print("-"*50)
        
        # Clinical interpretation
        sensitivity = metrics['sensitivity']
        specificity = metrics['specificity']
        
        print(f"Clinical Interpretation:")
        print(f"- Sensitivity (True Positive Rate): {sensitivity:.1%}")
        print(f"  → Can identify {sensitivity:.1%} of patients who will have hypoglycemia")
        
        print(f"- Specificity (True Negative Rate): {specificity:.1%}")
        print(f"  → Correctly identifies {specificity:.1%} of patients who won't have hypoglycemia")
        
        if metrics['precision'] > 0:
            print(f"- Precision (Positive Predictive Value): {metrics['precision']:.1%}")
            print(f"  → When model predicts hypoglycemia, it's correct {metrics['precision']:.1%} of the time")
        
        # Risk assessment
        print(f"\nRisk Assessment:")
        if sensitivity >= 0.8 and specificity >= 0.7:
            print("✓ Model shows good clinical performance")
        elif sensitivity >= 0.7:
            print("⚠ Model has acceptable sensitivity but may have false positives")
        elif sensitivity < 0.7:
            print("⚠ Model may miss too many high-risk patients (low sensitivity)")
        
        if specificity < 0.5:
            print("⚠ Model has too many false alarms (low specificity)")
        
        # Save detailed results
        results_summary = {
            'evaluation_date': pd.Timestamp.now(),
            'total_sequences': len(sequences),
            'positive_cases': positive_count,
            'negative_cases': negative_count,
            'class_balance': positive_count / len(sequences),
            **metrics
        }
        
        results_df = pd.DataFrame([results_summary])
        results_df.to_csv('evaluation_results.csv', index=False)
        print(f"\nDetailed results saved to evaluation_results.csv")
        
    except Exception as e:
        print(f"Error during model evaluation: {e}")
        return

if __name__ == "__main__":
    main()