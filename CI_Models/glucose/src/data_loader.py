import os
import pandas as pd
import numpy as np
from pathlib import Path

def load_patient_data(file_path):
    """
    Load a single patient's CGM data from CSV file.
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file containing patient data
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with columns ['id', 'ts', 'gl']
    """
    # Extract patient ID from filename (e.g., 'g1_Patient_15_1' -> 'Patient_15_1')
    patient_id = Path(file_path).stem.split('_', 1)[1]
    
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Convert DeviceDtTm to datetime
    df['DeviceDtTm'] = pd.to_datetime(df['DeviceDtTm'])
    
    # Rename columns to match expected format
    df_processed = pd.DataFrame({
        'id': patient_id,
        'ts': df['DeviceDtTm'],
        'gl': df['Glucose'].astype(float)
    })
    
    # Sort by timestamp
    df_processed = df_processed.sort_values('ts').reset_index(drop=True)
    
    return df_processed

def load_multiple_patients(data_directory, file_pattern="*.csv"):
    """
    Load multiple patients' CGM data from a directory.
    
    Parameters:
    -----------
    data_directory : str
        Path to directory containing CSV files
    file_pattern : str
        Pattern to match CSV files (default: "*.csv")
        
    Returns:
    --------
    pd.DataFrame
        Combined DataFrame with all patients' data
    """
    data_path = Path(data_directory)
    csv_files = list(data_path.glob(file_pattern))
    
    if not csv_files:
        raise ValueError(f"No CSV files found in {data_directory} matching pattern {file_pattern}")
    
    all_data = []
    
    for file_path in csv_files:
        try:
            patient_data = load_patient_data(file_path)
            all_data.append(patient_data)
            print(f"Loaded {len(patient_data)} records for patient {patient_data['id'].iloc[0]}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue
    
    if not all_data:
        raise ValueError("No valid data files could be loaded")
    
    # Combine all patient data
    combined_data = pd.concat(all_data, axis=0, ignore_index=True)
    
    print(f"Total loaded: {len(combined_data)} records from {len(all_data)} patients")
    
    return combined_data

def resample_patient_data(data, freq_minutes=5):
    """
    Resample patient data to consistent frequency and handle missing values.
    
    Parameters:
    -----------
    data : pd.DataFrame
        DataFrame with columns ['id', 'ts', 'gl']
    freq_minutes : int
        Desired frequency in minutes (default: 5)
        
    Returns:
    --------
    pd.DataFrame
        Resampled data in wide format (timestamps as index, patients as columns)
    """
    # Create frequency string for pandas
    freq_str = f'{freq_minutes}T'
    
    # Group by patient and resample
    resampled_data = []
    
    for patient_id in data['id'].unique():
        patient_data = data[data['id'] == patient_id].copy()
        
        # Set timestamp as index
        patient_data = patient_data.set_index('ts')['gl']
        
        # Resample to consistent frequency
        
        freq_str = f"{freq_minutes}min"  
        patient_resampled = patient_data.resample(freq_str).mean()

        
        # Create DataFrame with patient ID as column
        patient_df = pd.DataFrame({patient_id: patient_resampled})
        
        resampled_data.append(patient_df)
    
    # Combine all patients
    if len(resampled_data) == 1:
        result = resampled_data[0]
    else:
        result = pd.concat(resampled_data, axis=1)
    
    # Sort by timestamp
    result = result.sort_index()
    
    print(f"Resampled data shape: {result.shape}")
    print(f"Date range: {result.index.min()} to {result.index.max()}")
    print(f"Missing data percentage: {result.isnull().sum().sum() / (result.shape[0] * result.shape[1]) * 100:.2f}%")
    
    return result

def prepare_real_data(data_directory, freq_minutes=5, file_pattern="*.csv"):
    """
    Complete pipeline to load and prepare real CGM data.
    
    Parameters:
    -----------
    data_directory : str
        Path to directory containing CSV files
    freq_minutes : int
        Desired frequency in minutes (default: 5)
    file_pattern : str
        Pattern to match CSV files (default: "*.csv")
        
    Returns:
    --------
    pd.DataFrame
        Processed data ready for model training/prediction
    """
    # Load all patient data
    raw_data = load_multiple_patients(data_directory, file_pattern)
    
    # Resample to consistent frequency
    processed_data = resample_patient_data(raw_data, freq_minutes)
    
    return processed_data

# Utility function to inspect data quality
def data_quality_report(data):
    report = []
    
    for patient in data.columns:
        patient_data = data[patient].dropna()
        
        if len(patient_data) > 0:
            report.append({
                'patient': patient,
                'total_readings': len(data[patient]),
                'valid_readings': len(patient_data),
                'missing_percentage': (len(data[patient]) - len(patient_data)) / len(data[patient]) * 100,
                'mean_glucose': patient_data.mean(),
                'std_glucose': patient_data.std(),
                'min_glucose': patient_data.min(),
                'max_glucose': patient_data.max(),
                'hypoglycemic_readings': (patient_data < 54).sum(),
                'hyperglycemic_readings': (patient_data > 180).sum(),
                'first_reading': data[patient].first_valid_index(),
                'last_reading': data[patient].last_valid_index()
            })
    
    return pd.DataFrame(report)
