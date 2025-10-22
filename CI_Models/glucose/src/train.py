from model import Model
from data_loader import prepare_real_data, data_quality_report
from utils import get_labelled_sequences
import pandas as pd
import os 
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src directory
DATA_DIRECTORY = os.path.join(BASE_DIR, "data")  
FREQ_MINUTES = 5  # Sampling frequency in minutes

# Model parameters
TIME_WORN_THRESHOLD = 0.3  # Minimum percentage of time device must be worn
GLUCOSE_THRESHOLD = 54  # Hypoglycemia threshold in mg/dL
EVENT_DURATION_THRESHOLD = 15  # Minimum hypoglycemic event duration in minutes

def save_model_properly(model, base_name="model_real_data"):
    """
    Save the model properly by handling the directory structure correctly
    """
    try:
        # Create directory for the model
        save_dir = f"{base_name}_dir"
        os.makedirs(save_dir, exist_ok=True)
        
        # Save the Keras model with proper extension inside the directory
        keras_model_path = os.path.join(save_dir, "model.keras")
        model.classifier.model.save(keras_model_path)
        
        # Save the parameters (this is what your original save method does)
        parameters_path = os.path.join(save_dir, "parameters.json")
        with open(parameters_path, 'w') as f:
            json.dump({
                'loc': model.classifier.loc.tolist(),
                'scale': model.classifier.scale.tolist(),
                'threshold': model.classifier.threshold,
                'parameters': [model.transformer.parameters[i].tolist() for i in range(len(model.transformer.parameters))]
            }, f)
        
        print(f"✓ Model saved successfully to: {save_dir}")
        print(f"  - Keras model: {keras_model_path}")
        print(f"  - Parameters: {parameters_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to save model: {e}")
        return False

def main():
    print("Loading real CGM data...")
    
    # Load and prepare real data
    try:
        data = prepare_real_data(
            data_directory=DATA_DIRECTORY,
            freq_minutes=FREQ_MINUTES,
            file_pattern="*.csv"  # Adjust pattern if needed
        )
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Please check the DATA_DIRECTORY path and ensure CSV files are present.")
        return
    
    print(f"\nLoaded data for {len(data.columns)} patients")
    print(f"Date range: {data.index.min()} to {data.index.max()}")
    print(f"Total time points: {len(data)}")
    
    # Generate data quality report
    print("\nGenerating data quality report...")
    quality_report = data_quality_report(data)
    print(quality_report[['patient', 'valid_readings', 'missing_percentage', 'mean_glucose']].head(10))
    
    # Filter patients with sufficient data
    min_readings_required = int(7 * 24 * 60 / FREQ_MINUTES * 2)  # At least 2 weeks of data
    valid_patients = quality_report[
        (quality_report['valid_readings'] >= min_readings_required) & 
        (quality_report['missing_percentage'] < 90)
    ]['patient'].tolist()
    
    print(f"\nFound {len(valid_patients)} patients with sufficient data quality")
    
    if len(valid_patients) == 0:
        print("No patients meet the minimum data requirements. Consider:")
        print("- Reducing time_worn_threshold")
        print("- Reducing minimum readings required")
        print("- Checking data quality")
        return
    
    # Filter data to valid patients only
    data_filtered = data[valid_patients].copy()
    
    # Split the dataset into sequences
    print("\nCreating labeled sequences...")
    sequences = get_labelled_sequences(
        data=data_filtered,
        time_worn_threshold=TIME_WORN_THRESHOLD,
        glucose_threshold=GLUCOSE_THRESHOLD,
        event_duration_threshold=EVENT_DURATION_THRESHOLD,
    )
    
    print(f"Created {len(sequences)} sequences")
    
    if len(sequences) == 0:
        print("No valid sequences created. Consider:")
        print("- Reducing time_worn_threshold")
        print("- Adjusting glucose_threshold or event_duration_threshold")
        print("- Checking if patients have sufficient continuous data")
        return
    
    # Check class distribution
    labels = [s['Y'] for s in sequences]
    positive_count = sum(labels)
    negative_count = len(labels) - positive_count
    
    print(f"Class distribution:")
    print(f"- Negative (no hypoglycemia): {negative_count} ({negative_count/len(labels)*100:.1f}%)")
    print(f"- Positive (hypoglycemia): {positive_count} ({positive_count/len(labels)*100:.1f}%)")
    
    if positive_count == 0:
        print("Warning: No positive cases found. Consider:")
        print(f"- Adjusting glucose_threshold (current: {GLUCOSE_THRESHOLD} mg/dL)")
        print(f"- Reducing event_duration_threshold (current: {EVENT_DURATION_THRESHOLD} minutes)")
        return
    
    # Calculate sequence length (1 week in time points)
    sequence_length = int(7 * 24 * 60 / FREQ_MINUTES)
    print(f"Using sequence length: {sequence_length} time points (1 week)")
    
    # Train the model
    print("\nTraining model...")
    model = Model()
    
    try:
        model.fit(
            sequences=sequences,
            sequence_length=sequence_length,
            l1_penalty=0.005,
            l2_penalty=0.05,
            learning_rate=0.00001,
            batch_size=32,
            epochs=1000,
            seed=42,
            verbose=1
        )
        
        print("Model training completed successfully!")
        
        # Save the model using our fixed method
        print("\nSaving model...")
        save_success = save_model_properly(model, "model_real_data")
        
        if save_success:
            print("\n✓ Model saved successfully!")
            
            # Test loading the model to make sure it works
            print("\nTesting model loading...")
            test_model = Model()
            test_model.load("model_real_data_dir")
            print("✓ Model loaded successfully - save/load cycle works!")
            
        else:
            print("\n⚠️  Model training completed but saving failed.")
        
        # Quick evaluation on training data (for validation, use separate test set)
        print("\nEvaluating model on training data...")
        metrics = model.evaluate(sequences=sequences)
        
        print("Training metrics:")
        for metric, value in metrics.items():
            print(f"- {metric}: {value:.4f}")
            
    except Exception as e:
        print(f"Error during model training or saving: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()