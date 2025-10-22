from model import Model
from data_loader import prepare_real_data, data_quality_report
from utils import get_unlabelled_sequences
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src directory
DATA_DIRECTORY = os.path.join(BASE_DIR, "data")  
FREQ_MINUTES = 5  # Sampling frequency in minutes

# Model parameters - RELAXED THRESHOLDS FOR PREDICTION
TIME_WORN_THRESHOLD = 0.15  # Reduced from 0.3 - minimum percentage of time device must be worn

def main():
    print("Loading real CGM data for prediction...")
    
    # Load and prepare real data
    try:
        data = prepare_real_data(
            data_directory=DATA_DIRECTORY,
            freq_minutes=FREQ_MINUTES,
            file_pattern="*.csv"
        )
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Please check the DATA_DIRECTORY path and ensure CSV files are present.")
        return
    
    print(f"\nLoaded data for {len(data.columns)} patients")
    print(f"Date range: {data.index.min()} to {data.index.max()}")
    
    # Generate data quality report
    quality_report = data_quality_report(data)
    print("\nData quality summary:")
    print(quality_report[['patient', 'valid_readings', 'missing_percentage', 'mean_glucose']].head())
    
    # RELAXED REQUIREMENTS: Filter patients with at least 3 days of data instead of 1 week
    min_readings_required = int(3 * 24 * 60 / FREQ_MINUTES)  # 3 days instead of 7 days
    valid_patients = quality_report[
        (quality_report['valid_readings'] >= min_readings_required) & 
        (quality_report['missing_percentage'] < 95)  # Increased from 90% to 95%
    ]['patient'].tolist()
    
    print(f"\nFound {len(valid_patients)} patients with sufficient data for prediction")
    print(f"(Minimum required: {min_readings_required} readings over 3 days)")
    
    if len(valid_patients) == 0:
        print("No patients meet the minimum data requirements for prediction.")
        print("Current requirements:")
        print(f"- At least {min_readings_required} valid readings (3 days)")
        print("- Less than 95% missing data")
        return
    
    # Filter data to valid patients only
    data_filtered = data[valid_patients].copy()
    
    # Create unlabeled sequences (using most recent available data)
    print("\nCreating prediction sequences...")
    sequences = get_unlabelled_sequences(
        data=data_filtered,
        time_worn_threshold=TIME_WORN_THRESHOLD,
    )
    
    print(f"Created {len(sequences)} prediction sequences")
    
    if len(sequences) == 0:
        print("No valid sequences created for prediction.")
        print(f"Consider reducing time_worn_threshold (current: {TIME_WORN_THRESHOLD})")
        return
    
    # FIXED MODEL LOADING PATH
    print("\nLoading trained model...")
    try:
        model = Model()
        # Use the correct directory name from the training script
        model.load(directory='model_real_data_dir')  # Fixed: added '_dir' suffix
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Make sure you have trained the model first using train.py")
        print("Expected model directory: 'model_real_data_dir'")
        
        # Check if model directory exists
        if not os.path.exists('model_real_data_dir'):
            print("Model directory 'model_real_data_dir' not found.")
            print("Please run the training script first.")
        else:
            print("Model directory exists but failed to load.")
            print("Contents:", os.listdir('model_real_data_dir'))
        return
    
    # Generate predictions
    print("\nGenerating predictions...")
    try:
        predictions = model.predict(sequences=sequences)
        print(f"Generated predictions for {len(predictions)} sequences")
        
        # Display results
        print("\nPrediction Results:")
        print("="*60)
        
        # Summary statistics
        total_predictions = len(predictions)
        high_risk_predictions = (predictions['predicted_label'] == 1).sum()
        
        print(f"Total patients predicted: {total_predictions}")
        print(f"High-risk predictions: {high_risk_predictions} ({high_risk_predictions/total_predictions*100:.1f}%)")
        print(f"Low-risk predictions: {total_predictions - high_risk_predictions} ({(total_predictions - high_risk_predictions)/total_predictions*100:.1f}%)")
        
        print(f"\nAverage predicted probability: {predictions['predicted_probability'].mean():.3f}")
        print(f"Decision threshold: {predictions['decision_threshold'].iloc[0]:.3f}")
        
        # Show individual predictions
        print("\nIndividual Predictions:")
        print("-"*60)
        
        # Sort by probability (highest risk first)
        predictions_sorted = predictions.sort_values('predicted_probability', ascending=False)
        
        for idx, row in predictions_sorted.iterrows():
            risk_level = "HIGH RISK" if row['predicted_label'] == 1 else "Low Risk"
            print(f"Patient {row['patient']}: {risk_level}")
            print(f"  Probability: {row['predicted_probability']:.3f}")
            print(f"  Prediction period: {row['start']} to {row['end']}")
            print()
        
        # Save predictions to file
        output_file = 'hypoglycemia_predictions.csv'
        predictions.to_csv(output_file, index=False)
        print(f"Predictions saved to {output_file}")
        
        # High-risk patient alert
        if high_risk_predictions > 0:
            print("\n⚠️  HIGH-RISK PATIENTS IDENTIFIED:")
            high_risk_patients = predictions[predictions['predicted_label'] == 1]['patient'].tolist()
            print(f"Patients requiring attention: {', '.join(high_risk_patients)}")
        else:
            print("\n✅ No high-risk patients identified in this prediction cycle.")
        
    except Exception as e:
        print(f"Error generating predictions: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()