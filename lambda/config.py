"""
Lambda Configuration
Configuration constants for the heart attack prediction Lambda function.
"""

# SageMaker Endpoint
ENDPOINT_NAME = "xgb-heart-attack-endpoint-2025-11-24-01-04-04"

# S3 Configuration
BUCKET_NAME = "healthcare-project-data-jayesh-devre"
PROCESSED_PREFIX = "processed/final_health_dataset_csv/"
FEATURE_LIST_KEY = "preprocess/feature_list.txt"

# SNS Configuration
ALERT_TOPIC_ARN = "arn:aws:sns:us-east-1:381492296417:jayesh-devre-health-alerts"

# Prediction Configuration
ALERT_THRESHOLD = 0.45  # Risk score threshold for triggering alerts
MAX_ROWS_TO_PROCESS = 50  # Maximum number of rows to process per invocation

