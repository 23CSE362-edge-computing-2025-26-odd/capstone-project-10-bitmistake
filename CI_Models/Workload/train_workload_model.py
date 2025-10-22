"""
Workload Model Training Script for Edge Deployment
Trains LSTM models on system workload data and converts to TensorFlow Lite format
"""
import os
import sys
import pickle
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# TensorFlow imports
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')


class WorkloadModelTrainer:
    """Train LSTM models for workload prediction"""
    
    def __init__(self, data_dir: str = "data", model_dir: str = "models", seq_length: int = 50):
        """
        Initialize the trainer
        
        Args:
            data_dir: Directory containing CSV data files
            model_dir: Directory to save trained models
            seq_length: Sequence length for LSTM input
        """
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.seq_length = seq_length
        self.scaler = None
        self.features = None
        
        # Create model directory if it doesn't exist
        os.makedirs(self.model_dir, exist_ok=True)
        
        print(f"Trainer initialized: seq_length={seq_length}")
    
    def load_and_preprocess_data(self, csv_file: str) -> Tuple[pd.DataFrame, MinMaxScaler]:
        """
        Load and preprocess CSV data
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            Preprocessed dataframe and scaler
        """
        print(f"\nLoading data from {csv_file}...")
        
        # Load data
        df = pd.read_csv(csv_file)
        print(f"  Loaded {len(df)} samples")
        
        # Remove timestamp column if present
        if 'timestamp' in df.columns:
            df = df.drop('timestamp', axis=1)
        
        # Select numeric features (exclude non-numeric columns)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            raise ValueError(f"No numeric columns found in {csv_file}")
        
        # Use load-1m as primary feature if available, otherwise use first numeric column
        if 'load-1m' in numeric_cols:
            self.features = ['load-1m']
        else:
            self.features = numeric_cols[:1]
        
        df = df[self.features]
        
        # Remove any NaN or infinite values
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna()
        
        print(f"  Using features: {self.features}")
        print(f"  Data shape after cleaning: {df.shape}")
        print(f"  Data statistics:")
        print(f"    Mean: {df.iloc[:, 0].mean():.4f}")
        print(f"    Std: {df.iloc[:, 0].std():.4f}")
        print(f"    Min: {df.iloc[:, 0].min():.4f}")
        print(f"    Max: {df.iloc[:, 0].max():.4f}")
        
        # Scale data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(df[self.features])
        
        return pd.DataFrame(scaled_data, columns=self.features), scaler
    
    def create_sequences(self, data: np.ndarray, seq_length: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM training
        
        Args:
            data: Scaled data array
            seq_length: Length of sequences
            
        Returns:
            X and y arrays for training
        """
        X, y = [], []
        
        for i in range(len(data) - seq_length):
            X.append(data[i:i+seq_length])
            y.append(data[i+seq_length, 0])  # Predict first feature
        
        return np.array(X), np.array(y)
    
    def build_lstm_model(self, input_shape: Tuple[int, int], 
                        lstm_units: int = 64, dropout_rate: float = 0.2) -> tf.keras.Model:
        """
        Build LSTM model for workload prediction
        
        Args:
            input_shape: Shape of input (seq_length, num_features)
            lstm_units: Number of LSTM units
            dropout_rate: Dropout rate for regularization
            
        Returns:
            Compiled Keras model
        """
        model = Sequential([
            LSTM(lstm_units, activation='relu', input_shape=input_shape, return_sequences=True),
            Dropout(dropout_rate),
            LSTM(lstm_units // 2, activation='relu', return_sequences=False),
            Dropout(dropout_rate),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')  # Output in [0, 1] range for scaled predictions
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        print(f"\nLSTM Model Architecture:")
        model.summary()
        
        return model
    
    def train_model(self, csv_file: str, system_name: str, epochs: int = 100, 
                   batch_size: int = 32, validation_split: float = 0.2) -> Dict[str, Any]:
        """
        Train LSTM model on data from a single system
        
        Args:
            csv_file: Path to CSV file
            system_name: Name of the system (e.g., 'system-1')
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Validation split ratio
            
        Returns:
            Training history and model info
        """
        print(f"\n{'='*60}")
        print(f"Training model for {system_name}")
        print(f"{'='*60}")
        
        # Load and preprocess data
        scaled_df, scaler = self.load_and_preprocess_data(csv_file)
        
        # Create sequences
        X, y = self.create_sequences(scaled_df.values, self.seq_length)
        print(f"\nCreated sequences: X shape = {X.shape}, y shape = {y.shape}")
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )
        print(f"Training set: {X_train.shape[0]} samples")
        print(f"Validation set: {X_val.shape[0]} samples")
        
        # Build model
        model = self.build_lstm_model((self.seq_length, len(self.features)))
        
        # Train model
        print(f"\nTraining model...")
        early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6)
        
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop, reduce_lr],
            verbose=1
        )
        
        # Evaluate model
        train_loss, train_mae = model.evaluate(X_train, y_train, verbose=0)
        val_loss, val_mae = model.evaluate(X_val, y_val, verbose=0)
        
        print(f"\nTraining Results:")
        print(f"  Train Loss: {train_loss:.6f}, Train MAE: {train_mae:.6f}")
        print(f"  Val Loss: {val_loss:.6f}, Val MAE: {val_mae:.6f}")
        
        # Save model
        model_path = os.path.join(self.model_dir, f"{system_name}.h5")
        model.save(model_path)
        print(f"  Model saved: {model_path}")
        
        # Save scaler (only once, reuse for all models)
        if self.scaler is None:
            self.scaler = scaler
            scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
            print(f"  Scaler saved: {scaler_path}")
        
        # Save training summary (only once)
        summary_path = os.path.join(self.model_dir, 'training_summary.pkl')
        if not os.path.exists(summary_path):
            summary = {
                'seq_length': self.seq_length,
                'features': self.features,
                'timestamp': datetime.now().isoformat()
            }
            with open(summary_path, 'wb') as f:
                pickle.dump(summary, f)
            print(f"  Training summary saved: {summary_path}")
        
        return {
            'model': model,
            'history': history,
            'scaler': scaler,
            'train_loss': train_loss,
            'train_mae': train_mae,
            'val_loss': val_loss,
            'val_mae': val_mae,
            'model_path': model_path
        }
    
    def train_all_models(self, system_ids: Optional[List[str]] = None, 
                        epochs: int = 100, batch_size: int = 32) -> Dict[str, Dict]:
        """
        Train models for all available systems
        
        Args:
            system_ids: List of system IDs to train (e.g., ['system-1', 'system-2'])
            epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            Dictionary of training results
        """
        # Find all CSV files if system_ids not provided
        if system_ids is None:
            csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
            system_ids = [f.replace('.csv', '') for f in csv_files]
            system_ids = sorted(system_ids)
        
        print(f"\nTraining models for systems: {system_ids}")
        
        results = {}
        for system_id in system_ids:
            csv_file = os.path.join(self.data_dir, f"{system_id}.csv")
            
            if not os.path.exists(csv_file):
                print(f"WARNING: CSV file not found: {csv_file}")
                continue
            
            try:
                result = self.train_model(csv_file, system_id, epochs=epochs, batch_size=batch_size)
                results[system_id] = result
            except Exception as e:
                print(f"ERROR: Failed to train {system_id}: {e}")
                continue
        
        return results
    
    def convert_to_tflite(self, system_name: str, quantize: bool = True, 
                        target_spec: str = "float16") -> bool:
        """
        Convert H5 model to TensorFlow Lite format
        
        Args:
            system_name: Name of the system
            quantize: Whether to apply quantization
            target_spec: Quantization target ('float16', 'int8', or 'default')
            
        Returns:
            Success status
        """
        h5_path = os.path.join(self.model_dir, f"{system_name}.h5")
        tflite_path = os.path.join(self.model_dir, f"{system_name}.tflite")
        
        if not os.path.exists(h5_path):
            print(f"ERROR: H5 model not found: {h5_path}")
            return False
        
        try:
            print(f"\nConverting {system_name} to TFLite...")
            
            # Load the Keras model
            model = tf.keras.models.load_model(h5_path, compile=False)
            
            # Create converter
            converter = tf.lite.TFLiteConverter.from_keras_model(model)
            
            # Apply optimizations
            if quantize:
                converter.optimizations = [tf.lite.Optimize.DEFAULT]
                
                if target_spec == "float16":
                    converter.target_spec.supported_types = [tf.float16]
                    print("  Using float16 quantization")
                elif target_spec == "int8":
                    converter.target_spec.supported_types = [tf.int8]
                    converter.inference_input_type = tf.int8
                    converter.inference_output_type = tf.int8
                    print("  Using int8 quantization")
                else:
                    print("  Using default quantization")
            
            # Handle LSTM models with tensor list operations
            converter.target_spec.supported_ops = [
                tf.lite.OpsSet.TFLITE_BUILTINS,
                tf.lite.OpsSet.SELECT_TF_OPS
            ]
            converter._experimental_lower_tensor_list_ops = False
            print("  Using SELECT_TF_OPS for LSTM compatibility")
            
            # Convert
            tflite_model = converter.convert()
            
            # Save TFLite model
            with open(tflite_path, 'wb') as f:
                f.write(tflite_model)
            
            # Calculate size reduction
            h5_size = os.path.getsize(h5_path)
            tflite_size = os.path.getsize(tflite_path)
            reduction = ((h5_size - tflite_size) / h5_size) * 100
            
            print(f"  [OK] Conversion successful!")
            print(f"    Original (H5): {h5_size / 1024:.1f} KB")
            print(f"    TFLite: {tflite_size / 1024:.1f} KB")
            print(f"    Size reduction: {reduction:.1f}%")
            
            return True
            
        except Exception as e:
            print(f"  [FAIL] Conversion failed: {e}")
            return False
    
    def convert_all_to_tflite(self, system_ids: Optional[List[str]] = None,
                             quantize: bool = True, target_spec: str = "float16") -> None:
        """
        Convert all H5 models to TensorFlow Lite format
        
        Args:
            system_ids: List of system IDs to convert
            quantize: Whether to apply quantization
            target_spec: Quantization target
        """
        if system_ids is None:
            h5_files = [f for f in os.listdir(self.model_dir) if f.endswith('.h5')]
            system_ids = [f.replace('.h5', '') for f in h5_files if f != 'global_model.h5']
        
        print(f"\n{'='*60}")
        print(f"Converting {len(system_ids)} models to TensorFlow Lite")
        print(f"{'='*60}")
        
        success_count = 0
        for system_id in system_ids:
            if self.convert_to_tflite(system_id, quantize, target_spec):
                success_count += 1
        
        print(f"\n{'='*60}")
        print(f"Conversion Complete: {success_count}/{len(system_ids)} successful")
        print(f"{'='*60}")


def main():
    """Main function with command-line argument parsing"""
    parser = argparse.ArgumentParser(
        description='Train workload prediction models and convert to TensorFlow Lite'
    )
    parser.add_argument('--data-dir', type=str, default='data',
                       help='Directory containing CSV data files')
    parser.add_argument('--model-dir', type=str, default='models',
                       help='Directory to save models')
    parser.add_argument('--seq-length', type=int, default=50,
                       help='Sequence length for LSTM')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for training')
    parser.add_argument('--systems', type=str, nargs='+',
                       help='Specific systems to train (e.g., system-1 system-2)')
    parser.add_argument('--convert-only', action='store_true',
                       help='Only convert existing H5 models to TFLite (skip training)')
    parser.add_argument('--quantize', action='store_true', default=True,
                       help='Apply quantization during TFLite conversion')
    parser.add_argument('--target-spec', type=str, choices=['float16', 'int8', 'default'],
                       default='float16', help='Quantization target specification')
    parser.add_argument('--no-convert', action='store_true',
                       help='Train models but do not convert to TFLite')
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = WorkloadModelTrainer(
        data_dir=args.data_dir,
        model_dir=args.model_dir,
        seq_length=args.seq_length
    )
    
    try:
        if args.convert_only:
            # Only convert existing models
            print("Converting existing H5 models to TensorFlow Lite...")
            trainer.convert_all_to_tflite(
                system_ids=args.systems,
                quantize=args.quantize,
                target_spec=args.target_spec
            )
        else:
            # Train models
            print(f"Starting training with:")
            print(f"  Data directory: {args.data_dir}")
            print(f"  Model directory: {args.model_dir}")
            print(f"  Sequence length: {args.seq_length}")
            print(f"  Epochs: {args.epochs}")
            print(f"  Batch size: {args.batch_size}")
            
            results = trainer.train_all_models(
                system_ids=args.systems,
                epochs=args.epochs,
                batch_size=args.batch_size
            )
            
            if not results:
                print("ERROR: No models were trained successfully")
                sys.exit(1)
            
            print(f"\n{'='*60}")
            print(f"Training Summary")
            print(f"{'='*60}")
            for system_id, result in results.items():
                print(f"\n{system_id}:")
                print(f"  Model path: {result['model_path']}")
                print(f"  Train Loss: {result['train_loss']:.6f} (MAE: {result['train_mae']:.6f})")
                print(f"  Val Loss: {result['val_loss']:.6f} (MAE: {result['val_mae']:.6f})")
            
            # Convert to TFLite
            if not args.no_convert:
                print(f"\n{'='*60}")
                print("Converting to TensorFlow Lite...")
                print(f"{'='*60}")
                trainer.convert_all_to_tflite(
                    system_ids=list(results.keys()),
                    quantize=args.quantize,
                    target_spec=args.target_spec
                )
            
            print("\n[SUCCESS] Training and conversion completed successfully!")
    
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
