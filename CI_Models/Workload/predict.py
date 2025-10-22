"""
LSTM Workload Predictor - Clean Version
Fixes all import and type issues
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
# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')

class WorkloadPredictor:
    """LSTM-based workload predictor with proper type hints"""
    
    def __init__(self, model_dir: str = "models") -> None:
        self.model_dir = model_dir
        self.scaler: Optional[Any] = None
        self.features: Optional[List[str]] = None
        self.seq_length: Optional[int] = None
        self.load_training_info()
    
    def load_training_info(self) -> None:
        """Load scaler and training parameters"""
        try:
            # Load scaler
            scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            print(f"✓ Loaded scaler from {scaler_path}")
            
            # Load training summary
            summary_path = os.path.join(self.model_dir, 'training_summary.pkl')
            with open(summary_path, 'rb') as f:
                summary = pickle.load(f)
                self.seq_length = summary['seq_length']
                self.features = summary['features']
            print(f"✓ Loaded parameters: seq_length={self.seq_length}, features={len(self.features)}")
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Training artifacts not found. Run training script first. Error: {e}")
    
    def prepare_sequences(self, data: np.ndarray, seq_length: int, target_col: int = 0) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Prepare sequences for prediction"""
        X: List[np.ndarray] = []
        y: List[float] = []
        
        for i in range(len(data) - seq_length):
            X.append(data[i:i+seq_length])
            if i + seq_length < len(data):
                y.append(data[i+seq_length, target_col])
        
        return np.array(X), np.array(y) if y else None
    
    def predict_future(self, node_name: str, future_steps: int = 200, 
                      plot: bool = True, save_plot: bool = True) -> Dict[str, Any]:
        """Predict future workload for a specific node"""
        print(f"\n🔮 Predicting future workload for {node_name}...")
        
        # Load node model
        model_path = os.path.join(self.model_dir, f"{node_name}.h5")
        if not os.path.exists(model_path):
            available_models = [f.replace('.h5', '') for f in os.listdir(self.model_dir) 
                              if f.endswith('.h5') and f != 'global_model.h5']
            raise FileNotFoundError(f"Model for {node_name} not found. Available: {available_models}")
        
        # Load model with error handling
        try:
            node_model = tf.keras.models.load_model(model_path)
        except Exception as e:
            print(f"  ⚠️  Loading with compatibility mode...")
            try:
                # Try loading without compilation
                node_model = tf.keras.models.load_model(model_path, compile=False)
                # Recompile manually
                node_model.compile(
                    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
                    loss='mse',
                    metrics=[tf.keras.metrics.MeanAbsoluteError()]
                )
            except Exception as e2:
                raise RuntimeError(f"Failed to load model: {e2}")
        
        print(f"✓ Loaded model from {model_path}")
        
        # Load node data
        data_path = os.path.join("data", f"{node_name}.csv")
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        df_node = pd.read_csv(data_path)
        print(f"✓ Loaded data: {len(df_node)} historical points")
        
        # Validate features
        if not self.features:
            raise ValueError("Features not loaded")
            
        missing_features = [f for f in self.features if f not in df_node.columns]
        if missing_features:
            raise ValueError(f"Missing features in data: {missing_features}")
        
        # Scale data
        if not self.scaler:
            raise ValueError("Scaler not loaded")
            
        scaled_node = self.scaler.transform(df_node[self.features])
        
        # Prepare sequences
        if not self.seq_length:
            raise ValueError("Sequence length not loaded")
            
        X_node, _ = self.prepare_sequences(scaled_node, self.seq_length)
        if len(X_node) == 0:
            raise ValueError(f"Insufficient data. Need at least {self.seq_length} points.")
        
        # Generate predictions
        print(f"🚀 Generating {future_steps} predictions...")
        input_seq = X_node[-1].copy()
        predictions: List[float] = []
        
        for step in range(future_steps):
            # Predict next value
            pred_input = input_seq.reshape(1, self.seq_length, len(self.features))
            pred = node_model.predict(pred_input, verbose=0)
            pred_value = float(pred[0, 0])
            predictions.append(pred_value)
            
            # Update sequence
            new_point = input_seq[-1].copy()
            new_point[0] = pred_value
            input_seq = np.vstack([input_seq[1:], new_point])
        
        # Rescale predictions
        predictions_array = np.array(predictions).reshape(-1, 1)
        dummy_features = np.zeros((len(predictions), len(self.features)))
        dummy_features[:, 0] = predictions_array.flatten()
        
        predictions_rescaled = self.scaler.inverse_transform(dummy_features)[:, 0]
        
        # Calculate statistics
        feature_name = self.features[0]
        current_data = df_node[feature_name].tail(50)
        current_avg = float(current_data.mean())
        predicted_avg = float(predictions_rescaled.mean())
        predicted_max = float(predictions_rescaled.max())
        predicted_min = float(predictions_rescaled.min())
        
        print(f"📊 Prediction Statistics:")
        print(f"  Current avg (last 50): {current_avg:.2f}")
        print(f"  Predicted avg: {predicted_avg:.2f}")
        print(f"  Predicted range: {predicted_min:.2f} - {predicted_max:.2f}")
        
        if plot:
            self.plot_predictions(df_node, predictions_rescaled, node_name, future_steps, save_plot)
        
        return {
            'historical_data': df_node[feature_name].values,
            'predictions': predictions_rescaled,
            'stats': {
                'current_avg': current_avg,
                'predicted_avg': predicted_avg,
                'predicted_max': predicted_max,
                'predicted_min': predicted_min
            }
        }
    
    def plot_predictions(self, df_historical: pd.DataFrame, predictions: np.ndarray, 
                        node_name: str, future_steps: int, save_plot: bool = True) -> None:
        """Create visualization of predictions"""
        if not self.features:
            return
            
        plt.figure(figsize=(15, 8))
        
        feature_name = self.features[0]
        historical_values = df_historical[feature_name].values
        historical_indices = list(range(len(historical_values)))
        future_indices = list(range(len(historical_values), len(historical_values) + future_steps))
        
        # Plot data
        plt.plot(historical_indices, historical_values, 
                label=f'Historical {feature_name}', 
                color='#2E86C1', linewidth=2, alpha=0.8)
        
        plt.plot(future_indices, predictions, 
                label=f'Predicted {feature_name}', 
                color='#E74C3C', linewidth=2, linestyle='--')
        
        # Styling
        plt.axvline(x=len(historical_values)-1, color='gray', linestyle=':', alpha=0.7, 
                   label='Prediction Start')
        
        plt.title(f'Workload Prediction for {node_name}', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Time Steps', fontsize=12)
        plt.ylabel(f'{feature_name} Value', fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Statistics
        current_avg = float(historical_values[-50:].mean() if len(historical_values) >= 50 
                           else historical_values.mean())
        predicted_avg = float(predictions.mean())
        change_pct = ((predicted_avg/current_avg - 1) * 100) if current_avg > 0 else 0
        
        stats_text = f'Current Avg: {current_avg:.2f}\nPredicted Avg: {predicted_avg:.2f}\nChange: {change_pct:+.1f}%'
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        if save_plot:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_path = f'prediction_{node_name}_{timestamp}.png'
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            print(f"📈 Plot saved as {plot_path}")
        
        plt.show()
    
    def list_available_nodes(self) -> List[str]:
        """List all available trained models"""
        models: List[str] = []
        if os.path.exists(self.model_dir):
            for file in os.listdir(self.model_dir):
                if file.endswith('.h5') and file != 'global_model.h5':
                    models.append(file.replace('.h5', ''))
        return sorted(models)

def main() -> None:
    """Main function with proper argument parsing"""
    parser = argparse.ArgumentParser(description='LSTM Workload Predictor')
    parser.add_argument('--node', type=str, help='Node name to predict (e.g., system-1)')
    parser.add_argument('--steps', type=int, default=200, help='Number of future steps')
    parser.add_argument('--all', action='store_true', help='Predict for all nodes')
    parser.add_argument('--list', action='store_true', help='List available models')
    
    args = parser.parse_args()
    
    try:
        predictor = WorkloadPredictor()
        
        if args.list:
            nodes = predictor.list_available_nodes()
            print(f"Available trained models: {nodes}")
            return
        
        if args.node:
            predictor.predict_future(args.node, args.steps)
        elif args.all:
            nodes = predictor.list_available_nodes()
            for node in nodes:
                try:
                    predictor.predict_future(node, args.steps, plot=False, save_plot=False)
                except Exception as e:
                    print(f"❌ Failed to predict {node}: {e}")
        else:
            # Interactive mode
            nodes = predictor.list_available_nodes()
            if not nodes:
                print("No trained models found. Run training script first.")
                return
            
            print(f"Available nodes: {nodes}")
            node_choice = input("Enter node name: ").strip()
            
            if node_choice not in nodes:
                print(f"Invalid node. Choose from: {nodes}")
                return
            
            steps_input = input("Future steps (default 200): ").strip()
            steps = int(steps_input) if steps_input.isdigit() else 200
            
            predictor.predict_future(node_choice, steps)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()