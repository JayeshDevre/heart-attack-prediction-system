"""
SageMaker Configuration
Shared configuration settings for model training and deployment.
"""

# AWS Configuration
REGION = "us-east-1"  # Update if needed
BUCKET = "healthcare-project-data-jayesh-devre"  # Update with your bucket name

# S3 Keys
HIST_KEY = "raw/historical/heart_attack_prediction_dataset.csv"
TRAIN_KEY = "raw/historical/train/train.csv"
TEST_KEY = "raw/historical/test/test.csv"
FEATURE_LIST_KEY = "preprocess/feature_list.txt"

# Model Configuration
MODEL_OUTPUT_PATH = "models/xgboost"
XGBOOST_VERSION = "1.5-1"

# Training Configuration
INSTANCE_TYPE = "ml.m5.large"
INSTANCE_COUNT = 1
VOLUME_SIZE = 5

# Hyperparameters
HYPERPARAMETERS = {
    "objective": "binary:logistic",
    "num_round": 100,
    "eta": 0.1,
    "max_depth": 5,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "eval_metric": "auc"
}

# Train/Test Split
TEST_SIZE = 0.2
RANDOM_STATE = 42

