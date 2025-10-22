# Configuration file for CGM hypoglycemia prediction system

# Data paths and loading settings
DATA_DIRECTORY = "./data"  # UPDATE THIS PATH TO YOUR DATA
FREQ_MINUTES = 5  # CGM sampling frequency in minutes
FILE_PATTERN = "*.csv"  # Pattern to match CSV files

# Data quality thresholds
TIME_WORN_THRESHOLD = 0.7  # Minimum percentage of time device must be worn (70%)
MIN_MISSING_DATA_THRESHOLD = 50  # Maximum percentage of missing data allowed (50%)

# Clinical thresholds
GLUCOSE_THRESHOLD = 54  # Hypoglycemia threshold in mg/dL (ADA standard)
EVENT_DURATION_THRESHOLD = 15  # Minimum hypoglycemic event duration in minutes

# Model training parameters
MODEL_PARAMS = {
    'l1_penalty': 0.005,
    'l2_penalty': 0.05,
    'learning_rate': 0.00001,
    'batch_size': 32,
    'epochs': 1000,
    'seed': 42,
}

# Cross-validation settings
CV_FOLDS = 5  # Number of folds for cross-validation
CV_MIN_SAMPLES_PER_CLASS = 3  # Minimum samples per class for CV

# Model directories
MODEL_DIR = 'model_real_data'  # Directory to save/load trained models

# Output files
PREDICTIONS_FILE = 'hypoglycemia_predictions.csv'
EVALUATION_FILE = 'evaluation_results.csv'
CV_RESULTS_FILE = 'cross_validation_results.csv'
CV_DETAILS_FILE = 'cross_validation_fold_details.csv'
DATA_QUALITY_FILE = 'data_quality_report.csv'

# Logging settings
VERBOSE_TRAINING = 1  # 0 for quiet, 1 for progress bars, 2 for detailed logs

# Clinical alert settings
HIGH_RISK_THRESHOLD = 0.5  # Probability threshold for high-risk alerts
ALERT_ENABLED = True  # Whether to show clinical alerts