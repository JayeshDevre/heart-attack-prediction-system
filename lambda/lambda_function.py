"""
AWS Lambda Function for Heart Attack Prediction
Processes health monitoring data from S3, makes predictions using SageMaker endpoint,
and sends alerts for high-risk patients via SNS.
"""

import boto3
import csv
import io
import pandas as pd
import json
from datetime import datetime

from config import (
    ENDPOINT_NAME,
    BUCKET_NAME,
    PROCESSED_PREFIX,
    FEATURE_LIST_KEY,
    ALERT_TOPIC_ARN,
    ALERT_THRESHOLD,
    MAX_ROWS_TO_PROCESS
)

# Initialize AWS clients
runtime = boto3.client("sagemaker-runtime")
s3 = boto3.client("s3")
sns = boto3.client("sns")


def load_feature_list():
    """
    Load expected feature list from S3.
    
    This ensures the preprocessing aligns with the features used during training.
    
    Returns:
        list: List of expected feature names in the correct order
    """
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=FEATURE_LIST_KEY)
    features = obj["Body"].read().decode("utf-8").splitlines()
    features = [f.strip() for f in features if f.strip()]
    
    # Remove target variable if present
    if "Heart Attack Risk" in features:
        features.remove("Heart Attack Risk")
    
    return features


def preprocess_row(df_row, expected_features):
    """
    Preprocess one row and align with training feature set.
    
    Steps:
    1. Split Blood Pressure into systolic and diastolic
    2. Drop non-feature columns (Patient ID, Country, etc.)
    3. Manual one-hot encoding for categorical variables (Sex, Diet)
    4. Convert to numeric and fill missing values
    5. Align columns with expected features from training
    
    Args:
        df_row (dict): Raw patient data row
        expected_features (list): List of feature names from training
        
    Returns:
        pd.DataFrame: Preprocessed dataframe with features aligned to training set
    """
    df = pd.DataFrame([df_row])
    
    # Split Blood Pressure
    if "Blood Pressure" in df.columns:
        bp = df["Blood Pressure"].astype(str).str.split("/", n=1, expand=True)
        df["BP_Systolic"] = pd.to_numeric(bp[0], errors="coerce")
        df["BP_Diastolic"] = pd.to_numeric(bp[1], errors="coerce")
        df.drop(columns=["Blood Pressure"], inplace=True)
    
    # Drop non-feature columns
    df = df.drop(columns=["Patient ID", "Country", "Continent", "Hemisphere"], errors="ignore")
    
    # Manual encoding for categorical columns
    df["Sex_Male"] = (df["Sex"].astype(str).str.lower() == "male").astype(int)
    df["Diet_Healthy"] = (df["Diet"].astype(str).str.lower() == "healthy").astype(int)
    df["Diet_Unhealthy"] = (df["Diet"].astype(str).str.lower() == "unhealthy").astype(int)
    
    # Drop originals
    df = df.drop(columns=["Sex", "Diet"], errors="ignore")
    
    # Convert numeric & fill missing
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)
    
    # Align with expected features
    for col in expected_features:
        if col not in df.columns:
            df[col] = 0
    
    df = df[expected_features]
    
    return df


def lambda_handler(event, context):
    """
    Lambda handler function for processing health monitoring data.
    
    Workflow:
    1. Load expected feature list from S3
    2. Get latest processed CSV file from S3
    3. Process each row (up to MAX_ROWS_TO_PROCESS)
    4. Make predictions using SageMaker endpoint
    5. Save predictions to S3
    6. Send SNS alerts for high-risk patients
    
    Args:
        event (dict): Lambda event (can be empty for scheduled invocations)
        context (LambdaContext): Lambda context object
        
    Returns:
        dict: Response with status code and processing results
    """
    print("Lambda invoked. Checking for processed CSV file in S3...")
    
    # Load expected features from training
    expected_features = load_feature_list()
    print(f"Loaded {len(expected_features)} expected features from training.")
    
    # Get latest processed CSV
    objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PROCESSED_PREFIX)
    csv_files = [obj["Key"] for obj in objects.get("Contents", []) if obj["Key"].endswith(".csv")]
    
    if not csv_files:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "No CSV file found."})
        }
    
    csv_key = csv_files[0]
    print(f"Using file: {csv_key}")
    
    # Read CSV
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=csv_key)
    data = obj["Body"].read().decode("utf-8").splitlines()
    reader = csv.DictReader(data)
    rows = list(reader)
    
    print(f"Columns detected ({len(reader.fieldnames)}): {reader.fieldnames}")
    
    results, alerts, alert_details = [], 0, []
    predictions = []
    
    # Process rows (limit to avoid timeout)
    for i, row in enumerate(rows[:MAX_ROWS_TO_PROCESS]):
        patient_id = row.get("Patient ID", f"Row{i+1}")
        
        # Preprocess row to match training features
        df_row = preprocess_row(row, expected_features)
        
        # Convert to CSV format for SageMaker
        csv_payload = df_row.to_csv(index=False, header=False)
        
        # Invoke SageMaker endpoint
        response = runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="text/csv",
            Body=csv_payload
        )
        
        raw_result = response["Body"].read().decode("utf-8").strip()
        
        if raw_result:
            score = float(raw_result)
            results.append(score)
            print(f"Risk score for {patient_id}: {score:.3f}")
            
            predictions.append({
                "Patient ID": patient_id,
                "Heart Attack Risk": round(score, 6),
                "Risk_Status": "HIGH_RISK" if score > ALERT_THRESHOLD else "LOW_RISK",
                "ScoredAt": datetime.utcnow().isoformat() + "Z"
            })
            
            # Check for high-risk alerts
            if score > ALERT_THRESHOLD:
                alerts += 1
                alert_details.append({
                    "patient_id": patient_id,
                    "risk_score": round(score, 3),
                    "status": "HIGH_RISK"
                })
                print(f"High-risk alert triggered for {patient_id} (score={score:.3f})")
    
    # Save predictions summary to S3
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    pred_key = f"predictions/heart_attack_predictions_{timestamp}.csv"
    
    if predictions:
        df_pred = pd.DataFrame(predictions)
        csv_buf = io.StringIO()
        df_pred.to_csv(csv_buf, index=False)
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=pred_key,
            Body=csv_buf.getvalue().encode("utf-8")
        )
        print(f"Predictions saved to s3://{BUCKET_NAME}/{pred_key}")
    
    # Send SNS notification for high-risk patients
    if alerts > 0:
        try:
            msg = "\n".join([f"{a['patient_id']}: {a['risk_score']}" for a in alert_details])
            sns.publish(
                TopicArn=ALERT_TOPIC_ARN,
                Message=f"{alerts} High-Risk Patients Detected:\n{msg}",
                Subject="Heart Health Alert Triggered"
            )
            print("SNS notification sent.")
        except Exception as e:
            print(f"SNS notification failed: {e}")
    
    print(f"Processed {len(rows)} rows, triggered {alerts} alerts.")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "processed_rows": len(rows),
            "alerts_triggered": alerts,
            "alert_details": alert_details,
            "all_scores": results
        })
    }
