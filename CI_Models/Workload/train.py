# lstm_workload_train.py
import pandas as pd
import numpy as np
import glob
import os
import pickle
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential, clone_model
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt
from datetime import datetime

# Suppress TensorFlow warnings
import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)

print("Starting LSTM Workload Predictor Training...")
print(f"TensorFlow version: {tf.__version__}")
print(f"Training started at: {datetime.now()}")

# -----------------
# Parameters
# -----------------
DATA_DIR = "data"
MODEL_DIR = "models"
SEQ_LENGTH = 50
FUTURE_STEPS = 200
FEATURES = ["load-1m", "cpu-user", "cpu-system", "sys-mem-free"]
EPOCHS_GLOBAL = 4
EPOCHS_FINE_TUNE = 5

# Create directories if they don't exist
os.makedirs(MODEL_DIR, exist_ok=True)

# -----------------
# 1. Load all systems into one dataset (for global training)
# -----------------
print("\n📊 Loading and preprocessing data...")
all_data = []
file_count = 0

for file in glob.glob(os.path.join(DATA_DIR, "system-*.csv")):
    try:
        df = pd.read_csv(file)
        print(f"  ✓ Loaded {os.path.basename(file)}: {len(df)} rows")
        
        # Check if all required features exist
        missing_features = [f for f in FEATURES if f not in df.columns]
        if missing_features:
            print(f"  ⚠️  Warning: Missing features in {file}: {missing_features}")
            continue
            
        all_data.append(df[FEATURES].values)
        file_count += 1
    except Exception as e:
        print(f"  ❌ Error loading {file}: {e}")
        continue

if not all_data:
    raise ValueError("No valid data files found! Please check your data directory and file format.")

print(f"Successfully loaded {file_count} system files")

# Stack all data
all_data = np.vstack(all_data)
print(f"Total data points: {len(all_data)}")
print(f"Features: {FEATURES}")

# Normalize globally
print("\n🔧 Normalizing data globally...")
scaler = MinMaxScaler()
scaled_all = scaler.fit_transform(all_data)

# Save the scaler for later use
scaler_path = os.path.join(MODEL_DIR, 'scaler.pkl')
with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)
print(f"  ✓ Scaler saved to {scaler_path}")

# Sequence builder with better error handling
def prepare_sequences(data, seq_length, target_col=0):
    """Prepare sequences for LSTM training"""
    X, y = [], []
    if len(data) <= seq_length:
        raise ValueError(f"Data length ({len(data)}) must be greater than sequence length ({seq_length})")
    
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, target_col])
    
    return np.array(X), np.array(y)

print(f"\n🔄 Preparing sequences (length={SEQ_LENGTH})...")
X_global, y_global = prepare_sequences(scaled_all, SEQ_LENGTH)
print(f"  ✓ Created {len(X_global)} training sequences")
print(f"  ✓ Input shape: {X_global.shape}, Output shape: {y_global.shape}")

# -----------------
# 2. Build base model with improved architecture
# -----------------
def build_model(seq_length, n_features):
    """Build LSTM model with dropout for regularization"""
    model = Sequential([
        LSTM(64, activation='tanh', return_sequences=True, 
             input_shape=(seq_length, n_features), dropout=0.2, recurrent_dropout=0.2),
        LSTM(32, activation='tanh', dropout=0.2, recurrent_dropout=0.2),
        Dense(16, activation='relu'),
        Dense(1)
    ])
    
    # Use Adam optimizer with learning rate scheduling
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss="mse", metrics=['mae'])
    return model

# Train global model
print(f"\n🚀 Training global model ({EPOCHS_GLOBAL} epochs)...")
global_model = build_model(SEQ_LENGTH, len(FEATURES))

# Add callbacks for better training
callbacks = [
    tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(patience=2, factor=0.5, min_lr=1e-6)
]

history = global_model.fit(
    X_global, y_global, 
    epochs=EPOCHS_GLOBAL, 
    batch_size=64, 
    validation_split=0.2, 
    shuffle=False, 
    verbose=1,
    callbacks=callbacks
)

# Save global model
global_model_path = os.path.join(MODEL_DIR, 'global_model.h5')
global_model.save(global_model_path)
print(f"  ✓ Global model saved to {global_model_path}")

# -----------------
# 3. Fine-tune for each node
# -----------------
print(f"\n🎯 Fine-tuning models for individual nodes ({EPOCHS_FINE_TUNE} epochs each)...")
node_models = {}
fine_tune_results = {}

for file in glob.glob(os.path.join(DATA_DIR, "system-*.csv")):
    node_name = os.path.basename(file).replace(".csv", "")
    print(f"\n  🔧 Processing {node_name}...")

    try:
        df_node = pd.read_csv(file)
        
        # Check data quality
        if len(df_node) <= SEQ_LENGTH:
            print(f"    ⚠️  Skipping {node_name}: insufficient data ({len(df_node)} rows)")
            continue
            
        scaled_node = scaler.transform(df_node[FEATURES])
        X_node, y_node = prepare_sequences(scaled_node, SEQ_LENGTH)
        
        print(f"    📊 Node data: {len(X_node)} sequences")

        # Clone global model
        node_model = clone_model(global_model)
        node_model.build((None, SEQ_LENGTH, len(FEATURES)))
        node_model.set_weights(global_model.get_weights())

        # Fine-tune with lower learning rate
        node_model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4), 
            loss="mse", 
            metrics=[tf.keras.metrics.MeanAbsoluteError()]
        )
        
        # Fine-tune
        fine_tune_history = node_model.fit(
            X_node, y_node, 
            epochs=EPOCHS_FINE_TUNE, 
            batch_size=32, 
            validation_split=0.2, 
            shuffle=False, 
            verbose=0
        )

        # Save model
        save_path = os.path.join(MODEL_DIR, f"{node_name}.h5")
        node_model.save(save_path)
        node_models[node_name] = node_model
        
        # Store training metrics
        final_loss = fine_tune_history.history['loss'][-1]
        final_val_loss = fine_tune_history.history['val_loss'][-1]
        fine_tune_results[node_name] = {
            'final_loss': final_loss,
            'final_val_loss': final_val_loss,
            'data_points': len(df_node)
        }
        
        print(f"    ✓ Model saved to {save_path}")
        print(f"    📈 Final loss: {final_loss:.6f}, Val loss: {final_val_loss:.6f}")
        
    except Exception as e:
        print(f"    ❌ Error processing {node_name}: {e}")
        continue

# -----------------
# 4. Summary and save training info
# -----------------
print(f"\n✅ Training completed!")
print(f"🎯 Global model trained on {len(X_global)} sequences")
print(f"🔧 Fine-tuned {len(node_models)} individual node models")

# Save training summary
summary = {
    'global_model_path': global_model_path,
    'scaler_path': scaler_path,
    'seq_length': SEQ_LENGTH,
    'features': FEATURES,
    'fine_tune_results': fine_tune_results,
    'training_date': datetime.now().isoformat()
}

summary_path = os.path.join(MODEL_DIR, 'training_summary.pkl')
with open(summary_path, 'wb') as f:
    pickle.dump(summary, f)

print(f"📋 Training summary saved to {summary_path}")
print(f"🎉 All models saved in {MODEL_DIR}/")

# Print final results table
if fine_tune_results:
    print(f"\n📊 Fine-tuning Results Summary:")
    print("-" * 70)
    print(f"{'Node':<15} {'Data Points':<12} {'Final Loss':<12} {'Val Loss':<12}")
    print("-" * 70)
    for node, results in fine_tune_results.items():
        print(f"{node:<15} {results['data_points']:<12} {results['final_loss']:<12.6f} {results['final_val_loss']:<12.6f}")
    print("-" * 70)