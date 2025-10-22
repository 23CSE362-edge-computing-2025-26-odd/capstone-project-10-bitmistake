import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model
import joblib
import matplotlib.pyplot as plt

# ===============================
# 📂 Directory Configuration
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

# 🧠 Choose the patient data file (change as needed)
PATIENT_FILE = "g1_Patient_15_1.csv"

# ===============================
# 🔍 Resolve Model + Scaler Paths
# ===============================
CSV_PATH = os.path.join(DATA_DIR, PATIENT_FILE)

# Try both .h5 and .keras formats for flexibility
model_base_name = os.path.splitext(PATIENT_FILE)[0]
MODEL_PATH_H5 = os.path.join(MODEL_DIR, f"{model_base_name}.h5")
MODEL_PATH_KERAS = os.path.join(MODEL_DIR, f"{model_base_name}.keras")
SCALER_PATH = os.path.join(MODEL_DIR, f"{model_base_name}_scaler.pkl")

# ===============================
# ⚙️ Validate Paths
# ===============================
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"❌ Data file not found: {CSV_PATH}")

if os.path.exists(MODEL_PATH_H5):
    MODEL_PATH = MODEL_PATH_H5
elif os.path.exists(MODEL_PATH_KERAS):
    MODEL_PATH = MODEL_PATH_KERAS
else:
    raise FileNotFoundError(f"❌ No model file found for {PATIENT_FILE} in 'models/'")

if not os.path.exists(SCALER_PATH):
    raise FileNotFoundError(f"❌ Scaler file not found: {SCALER_PATH}")

print(f"✅ Loaded model and scaler for {PATIENT_FILE}")

# ===============================
# 🧩 Load Data
# ===============================
df = pd.read_csv(CSV_PATH)

# Ensure the dataset has the expected 'Glucose' column
if "Glucose" not in df.columns:
    raise ValueError("❌ The CSV file must contain a 'Glucose' column.")

df = df.dropna(subset=["Glucose"])
if len(df) < 25:
    raise ValueError("❌ Not enough data points to make a prediction (need >25 readings).")

glucose = df["Glucose"].values.reshape(-1, 1)

# ===============================
# 🧮 Load Scaler + Model
# ===============================
scaler = joblib.load(SCALER_PATH)

# 🧠 FIX: disable compilation to avoid deserialization errors
model = load_model(MODEL_PATH, compile=False)

# ===============================
# 🔢 Prepare Input Sequence
# ===============================
glucose_scaled = scaler.transform(glucose)

SEQ_LEN = 20  # same as training
X_input = glucose_scaled[-SEQ_LEN:].reshape(1, SEQ_LEN, 1)

# ===============================
# 🔮 Predict Future Glucose Levels
# ===============================
future_preds = []
current_seq = X_input.copy()

for _ in range(50):  # predict 50 steps ahead
    pred = model.predict(current_seq, verbose=0)[0][0]
    future_preds.append(pred)
    # slide the window and append new prediction
    current_seq = np.append(current_seq[:, 1:, :], [[[pred]]], axis=1)

# Inverse transform predictions to real glucose values
future_glucose = scaler.inverse_transform(np.array(future_preds).reshape(-1, 1))

# ===============================
# 📊 Visualization
# ===============================
past = glucose[-100:]  # last 100 readings
future_index = np.arange(len(past), len(past) + len(future_glucose))

plt.figure(figsize=(10, 5))
plt.plot(range(len(past)), past, label="Past Glucose", color='blue', linewidth=2)
plt.plot(future_index, future_glucose, label="Predicted Future Glucose", color='red', linewidth=2)
plt.title(f"Glucose Prediction for {PATIENT_FILE}")
plt.xlabel("Time Steps")
plt.ylabel("Glucose Level (mg/dL)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ===============================
# 🧾 Print Summary Stats
# ===============================
print("\n📊 Prediction Summary:")
print(f"Current avg (last 50 readings): {np.mean(past[-50:]):.2f}")
print(f"Predicted avg (next 50 readings): {np.mean(future_glucose):.2f}")
print(f"Predicted range: {np.min(future_glucose):.2f} - {np.max(future_glucose):.2f}")
