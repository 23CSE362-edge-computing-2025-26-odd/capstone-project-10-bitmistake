import os
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib

# ========================
# CONFIGURATION
# ========================

# Get the absolute path of this script (so paths always resolve correctly)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

SEQ_LENGTH = 30
EPOCHS = 1
BATCH_SIZE = 16

os.makedirs(MODEL_DIR, exist_ok=True)

# ========================
# TRAINING FUNCTION
# ========================
def train_patient_model(csv_path, model_save_path, scaler_save_path):
    print(f"\n🩸 Training model for: {os.path.basename(csv_path)}")

    df = pd.read_csv(csv_path)
    if "Glucose" not in df.columns:
        print(f"⚠️ Skipping {csv_path} — no 'Glucose' column found.")
        return

    df = df.dropna(subset=["Glucose"])
    df["Glucose"] = pd.to_numeric(df["Glucose"], errors="coerce")
    df = df.dropna()

    if len(df) < SEQ_LENGTH + 10:
        print(f"⚠️ Skipping {csv_path} — insufficient data ({len(df)} points).")
        return

    glucose_values = df["Glucose"].values.reshape(-1, 1)

    # Scale data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(glucose_values)
    joblib.dump(scaler, scaler_save_path)

    # Create sequences
    X, y = [], []
    for i in range(len(scaled_data) - SEQ_LENGTH):
        X.append(scaled_data[i:i + SEQ_LENGTH])
        y.append(scaled_data[i + SEQ_LENGTH])
    X, y = np.array(X), np.array(y)

    # Train-test split
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Build LSTM model
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(SEQ_LENGTH, 1)),
        Dropout(0.2),
        LSTM(32),
        Dense(16, activation="relu"),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")

    # Train
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        verbose=1
    )

    # Save model
    model.save(model_save_path)
    print(f"✅ Saved model to {model_save_path}")
    print(f"✅ Saved scaler to {scaler_save_path}")

# ========================
# MAIN LOOP
# ========================

if not os.path.exists(DATA_DIR):
    print(f"❌ Data directory not found: {DATA_DIR}")
    exit(1)

csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

if not csv_files:
    print(f"❌ No CSV files found in {DATA_DIR}")
else:
    for csv_file in csv_files:
        patient_name = os.path.splitext(csv_file)[0]
        csv_path = os.path.join(DATA_DIR, csv_file)
        model_save_path = os.path.join(MODEL_DIR, f"{patient_name}.h5")
        scaler_save_path = os.path.join(MODEL_DIR, f"{patient_name}_scaler.pkl")

        train_patient_model(csv_path, model_save_path, scaler_save_path)

print("\n🎯 All available patient models trained successfully!")
