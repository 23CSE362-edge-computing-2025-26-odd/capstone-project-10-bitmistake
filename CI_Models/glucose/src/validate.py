import pandas as pd
from sklearn.model_selection import StratifiedKFold
import numpy as np

from model import Model
from data_loader import prepare_real_data, data_quality_report
from utils import get_labelled_sequences

# Data loading parameters
DATA_DIRECTORY = "path/to/your/csv/files"  # Update this path
FREQ_MINUTES = 5

# Model parameters
TIME_WORN_THRESHOLD = 0.7
GLUCOSE_THRESHOLD = 54
EVENT_DURATION_THRESHOLD = 15

# Cross-validation parameters
N_SPLITS = 5  # Reduced from 10 due to potentially smaller real dataset

def main():
    print("Loading real CGM data for cross-validation...")
    
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
    
    # Filter patients with sufficient data (need enough for multiple weeks)
    min_readings_required = int(21 * 24 * 60 / FREQ_MINUTES)  # At least 3 weeks
    valid_patients = quality_report[
        (quality_report['valid_readings'] >= min_readings_required) & 
        (quality_report['missing_percentage'] < 60)  # Allow slightly more missing data
    ]['patient'].tolist()
    
    print(f"Found {len(valid_patients)} patients suitable for cross-validation")
    
    if len(valid_patients) < N_SPLITS:
        print(f"Warning: Only {len(valid_patients)} patients available, but need at least {N_SPLITS} for {N_SPLITS}-fold CV")
        N_SPLITS = max(2, len(valid_patients) // 2)
        print(f"Reducing to {N_SPLITS}-fold cross-validation")
    
    if len(valid_patients) < 2:
        print("Not enough patients for cross-validation.")
        return
    
    # Filter data
    data_filtered = data[valid_patients].copy()
    
    # Create labeled sequences
    print("\nCreating labeled sequences...")
    sequences = get_labelled_sequences(
        data=data_filtered,
        time_worn_threshold=TIME_WORN_THRESHOLD,
        glucose_threshold=GLUCOSE_THRESHOLD,
        event_duration_threshold=EVENT_DURATION_THRESHOLD,
    )
    
    print(f"Created {len(sequences)} labeled sequences")
    
    if len(sequences) < N_SPLITS:
        print(f"Not enough sequences ({len(sequences)}) for {N_SPLITS}-fold cross-validation")
        return
    
    # Check class distribution
    labels = [s['Y'] for s in sequences]
    positive_count = sum(labels)
    negative_count = len(labels) - positive_count
    
    print(f"\nDataset statistics:")
    print(f"- Total sequences: {len(sequences)}")
    print(f"- Negative cases: {negative_count} ({negative_count/len(labels)*100:.1f}%)")
    print(f"- Positive cases: {positive_count} ({positive_count/len(labels)*100:.1f}%)")
    
    if positive_count == 0:
        print("Error: No positive cases found. Cannot perform meaningful validation.")
        return
    
    if positive_count < N_SPLITS or negative_count < N_SPLITS:
        print(f"Warning: Limited samples in one class. Results may be unstable.")
        print(f"Consider adjusting parameters or collecting more data.")
    
    # Calculate sequence length
    sequence_length = int(7 * 24 * 60 / FREQ_MINUTES)
    
    # Perform stratified k-fold cross-validation
    print(f"\nPerforming {N_SPLITS}-fold cross-validation...")
    
    try:
        skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=42)
        
        # Create lists for storing results
        results = []
        fold_details = []
        
        # Loop across the folds
        for fold_idx, (train_index, test_index) in enumerate(skf.split(
            X=[s['X'] for s in sequences], 
            y=[s['Y'] for s in sequences]
        )):
            
            print(f"\nTraining fold {fold_idx + 1}/{N_SPLITS}...")
            
            # Split sequences
            train_sequences = [sequences[i] for i in train_index]
            test_sequences = [sequences[i] for i in test_index]
            
            # Check fold distribution
            train_labels = [s['Y'] for s in train_sequences]
            test_labels = [s['Y'] for s in test_sequences]
            
            fold_info = {
                'fold': fold_idx + 1,
                'train_total': len(train_sequences),
                'train_positive': sum(train_labels),
                'test_total': len(test_sequences),
                'test_positive': sum(test_labels)
            }
            fold_details.append(fold_info)
            
            print(f"  Train: {len(train_sequences)} sequences ({sum(train_labels)} positive)")
            print(f"  Test: {len(test_sequences)} sequences ({sum(test_labels)} positive)")
            
            # Skip fold if no positive cases in training or test
            if sum(train_labels) == 0:
                print("  Skipping fold: No positive cases in training set")
                continue
            if sum(test_labels) == 0:
                print("  Warning: No positive cases in test set for this fold")
            
            # Train model for this fold
            model = Model()
            
            try:
                model.fit(
                    sequences=train_sequences,
                    sequence_length=sequence_length,
                    l1_penalty=0.005,
                    l2_penalty=0.05,
                    learning_rate=0.00001,
                    batch_size=32,
                    epochs=1000,
                    seed=42,
                    verbose=0  # Quiet training for cross-validation
                )
                
                # Evaluate model on test set
                if sum(test_labels) > 0:  # Only evaluate if we have positive cases
                    metrics = model.evaluate(sequences=test_sequences)
                    metrics['fold'] = fold_idx + 1
                    results.append(metrics)
                    
                    print(f"  Fold {fold_idx + 1} results: AUC={metrics['auc']:.3f}, F1={metrics['f1']:.3f}")
                else:
                    print(f"  Fold {fold_idx + 1}: Cannot calculate metrics (no positive test cases)")
                
            except Exception as e:
                print(f"  Error in fold {fold_idx + 1}: {e}")
                continue
        
        # Analyze results
        if not results:
            print("\nNo valid results obtained from cross-validation.")
            print("This may be due to:")
            print("- Insufficient positive cases")
            print("- Data quality issues")
            print("- Model training failures")
            return
        
        print(f"\nCross-validation completed with {len(results)} successful folds")
        
        # Calculate summary statistics
        results_df = pd.DataFrame(results)
        
        print("\n" + "="*60)
        print("CROSS-VALIDATION RESULTS")
        print("="*60)
        
        # Display mean and std for each metric
        summary_stats = results_df.describe()
        
        for metric in ['accuracy', 'balanced_accuracy', 'precision', 'sensitivity', 'specificity', 'f1', 'auc']:
            if metric in results_df.columns:
                mean_val = results_df[metric].mean()
                std_val = results_df[metric].std()
                print(f"{metric.upper():>20}: {mean_val:.4f} (±{std_val:.4f})")
        
        # Clinical interpretation
        print("\n" + "-"*60)
        print("CLINICAL PERFORMANCE SUMMARY")
        print("-"*60)
        
        mean_sensitivity = results_df['sensitivity'].mean()
        mean_specificity = results_df['specificity'].mean()
        mean_auc = results_df['auc'].mean()
        
        print(f"Average sensitivity: {mean_sensitivity:.1%} (detects hypoglycemia cases)")
        print(f"Average specificity: {mean_specificity:.1%} (avoids false alarms)")
        print(f"Average AUC: {mean_auc:.3f} (overall discrimination)")
        
        # Performance assessment
        print(f"\nPerformance Assessment:")
        if mean_auc >= 0.8:
            print("✓ Excellent discrimination capability")
        elif mean_auc >= 0.7:
            print("✓ Good discrimination capability")
        elif mean_auc >= 0.6:
            print("⚠ Fair discrimination capability")
        else:
            print("⚠ Poor discrimination capability - consider model improvements")
        
        if mean_sensitivity >= 0.8:
            print("✓ High sensitivity - good at detecting hypoglycemia")
        elif mean_sensitivity >= 0.6:
            print("⚠ Moderate sensitivity - may miss some cases")
        else:
            print("⚠ Low sensitivity - missing too many hypoglycemia cases")
        
        if mean_specificity >= 0.7:
            print("✓ Good specificity - reasonable false alarm rate")
        elif mean_specificity >= 0.5:
            print("⚠ Moderate specificity - some false alarms expected")
        else:
            print("⚠ Low specificity - high false alarm rate")
        
        # Save detailed results
        results_df.to_csv('cross_validation_results.csv', index=False)
        
        fold_details_df = pd.DataFrame(fold_details)
        fold_details_df.to_csv('cross_validation_fold_details.csv', index=False)
        
        print(f"\nDetailed results saved to:")
        print(f"- cross_validation_results.csv")
        print(f"- cross_validation_fold_details.csv")
        
        # Stability assessment
        print(f"\nModel Stability Assessment:")
        auc_std = results_df['auc'].std()
        if auc_std < 0.05:
            print("✓ Very stable performance across folds")
        elif auc_std < 0.1:
            print("✓ Stable performance across folds")
        else:
            print("⚠ Variable performance across folds - may need more data or different approach")
        
    except Exception as e:
        print(f"Error during cross-validation: {e}")
        return

if __name__ == "__main__":
    main()