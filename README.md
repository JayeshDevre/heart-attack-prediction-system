# Intelligent Health Monitoring & Heart Attack Prediction System

An Intelligent Health Monitoring & Heart Attack Prediction System Using AWS EMR, SageMaker, Lambda, Athena, and SNS

## Project Overview

This project implements an end-to-end machine learning pipeline for predicting heart attack risk in patients using their vital signs and demographic data. The system processes patient data through multiple AWS services, trains a machine learning model, and provides real-time predictions with automated alerting for high-risk patients.

## Architecture

The system follows a data pipeline architecture with the following flow:

```
Data Generation → EMR Processing → SageMaker Training → Lambda Prediction → Athena Analytics
                                                              ↓
                                                           SNS Alerts
```

### Component Overview

1. **Data Generation** (`phase1_sim/`): Generates simulated patient vital signs data
2. **EMR Processing** (`emr/`): Aggregates and processes data using PySpark
3. **Model Training** (`sagemaker/`): Trains XGBoost model and deploys endpoint
4. **Real-time Prediction** (`lambda/`): Processes new data and makes predictions
5. **Analytics** (`athena/`): SQL queries for data analysis
6. **Alerting**: SNS notifications for high-risk patients

## System Components

### 1. Data Generation (`phase1_sim/`)

**Purpose**: Generate simulated vital signs data for testing and development.

**Files**:
- `gen_simulated_vitals.py`: Generates 7 days of vital signs for 20 patients
- `simulated_vitals.csv`: Output file with simulated data

**Features**:
- Heart Rate (60-110 bpm)
- Blood Pressure (Systolic: 100-170, Diastolic: 60-120)
- Sleep Hours Per Day (3-9 hours)
- Physical Activity Per Day (0-1)

### 2. EMR Data Processing (`emr/`)

**Purpose**: Process and aggregate patient data using AWS EMR (Elastic MapReduce).

**Files**:
- `main.py`: PySpark script for data processing

**Process**:
1. Loads historical patient data from S3
2. Loads simulated vital signs data
3. Aggregates 7-day vitals into weekly averages per patient:
   - Average Heart Rate
   - Average Blood Pressure (Systolic/Diastolic)
   - Average Sleep Hours
   - Total Physical Activity Days
4. Joins aggregated vitals with historical demographics
5. Outputs processed CSV to S3: `s3://bucket/processed/final_health_dataset_csv/`

**Dependencies**: PySpark 3.5.0+

### 3. Model Training (`sagemaker/`)

**Purpose**: Train and deploy XGBoost model for heart attack risk prediction.

**Files**:
- `train_model.ipynb`: Jupyter notebook for model training
- `preprocess.py`: Data preprocessing utilities
- `config.py`: Configuration settings

**Training Process**:
1. Loads processed data from S3
2. Preprocessing:
   - Splits Blood Pressure into Systolic/Diastolic
   - Drops identifier columns (Patient ID, Country, Continent, Hemisphere)
   - One-hot encodes categorical variables (Sex, Diet)
   - Handles missing values
3. Splits data into train/test (80/20) with stratification
4. Trains XGBoost binary classifier with hyperparameters:
   - Objective: binary:logistic
   - Evaluation metric: AUC
   - 100 rounds with learning rate 0.1
5. Deploys model as SageMaker endpoint
6. Saves feature list to S3 for Lambda preprocessing alignment

**Configuration** (`config.py`):
- S3 bucket and key paths
- Model hyperparameters
- Training instance configuration
- Train/test split parameters

### 4. Real-time Prediction (`lambda/`)

**Purpose**: Process new patient data and generate heart attack risk predictions.

**Files**:
- `lambda_function.py`: Main Lambda handler
- `config.py`: Lambda configuration

**Workflow**:
1. Loads expected feature list from S3 (ensures preprocessing alignment)
2. Retrieves latest processed CSV from S3
3. For each patient row:
   - Preprocesses data to match training features
   - Invokes SageMaker endpoint for prediction
   - Records risk score
4. Saves predictions to S3: `s3://bucket/predictions/`
5. Sends SNS alerts for high-risk patients (risk > 0.45)

**Configuration** (`config.py`):
- SageMaker endpoint name
- S3 bucket and prefixes
- SNS topic ARN for alerts
- Alert threshold (default: 0.45)
- Max rows to process per invocation (default: 50)

### 5. Analytics (`athena/`)

**Purpose**: SQL-based analytics on processed data and predictions.

**Files**:
- `ddl.sql`: Creates external tables in Athena
- `analysis.sql`: Analytics queries

**Tables Created**:
1. `heart_attack_processed_data`: EMR output (patient vitals + demographics)
2. `heart_attack_predictions`: Lambda prediction outputs

**Analytics Queries**:
- Highest-risk patients with demographics
- Count of high-risk patients (>0.45 threshold)
- Average risk by age group
- Sleep duration vs. risk correlation
- Physical activity vs. heart rate vs. risk

## Data Flow

1. **Historical Data**: `heart_attack_prediction_dataset.csv` uploaded to S3
2. **Simulated Vitals**: Generated locally, uploaded to S3
3. **EMR Processing**: Aggregates vitals and joins with historical data
4. **SageMaker Training**: Trains model on processed data, deploys endpoint
5. **Lambda Processing**: Processes new data, generates predictions
6. **Athena Analytics**: Queries processed data and predictions
7. **SNS Alerts**: Notifications for high-risk patients

## S3 Bucket Structure

```
s3://healthcare-project-data-jayesh-devre/
├── raw/
│   ├── historical/
│   │   ├── heart_attack_prediction_dataset.csv
│   │   ├── train/
│   │   │   └── train.csv
│   │   └── test/
│   │       └── test.csv
│   └── simulated/
│       └── simulated_vitals.csv
├── processed/
│   └── final_health_dataset_csv/
│       └── (EMR output files)
├── preprocess/
│   └── feature_list.txt
├── models/
│   └── xgboost/
│       └── (trained model artifacts)
├── predictions/
│   └── heart_attack_predictions_*.csv
└── athena/
    └── results/
        └── (Athena query results)
```

## Setup & Configuration

### Prerequisites

- AWS Account with appropriate permissions
- Python 3.7+
- AWS CLI configured
- PySpark 3.5.0+ (for EMR)
- Jupyter Notebook (for SageMaker training)

### AWS Services Required

- **S3**: Data storage
- **EMR**: Data processing
- **SageMaker**: Model training and deployment
- **Lambda**: Real-time prediction processing
- **Athena**: SQL analytics
- **SNS**: Alert notifications
- **IAM**: Service roles and permissions

### Configuration Steps

1. **Update S3 Bucket Name**: 
   - Update `BUCKET` in `sagemaker/config.py`
   - Update `BUCKET_NAME` in `lambda/config.py`
   - Update S3 paths in `emr/main.py`

2. **Configure SageMaker**:
   - Update `REGION` in `sagemaker/config.py` if needed
   - Ensure SageMaker execution role has S3 access

3. **Configure Lambda**:
   - Update `ENDPOINT_NAME` in `lambda/config.py` after model deployment
   - Update `ALERT_TOPIC_ARN` with your SNS topic ARN
   - Ensure Lambda execution role has permissions for:
     - SageMaker runtime
     - S3 read/write
     - SNS publish

4. **Configure Athena**:
   - Set query result location in Athena settings
   - Update S3 paths in `athena/ddl.sql` if needed

## Usage

### 1. Generate Simulated Data

```bash
cd phase1_sim
python gen_simulated_vitals.py
# Upload simulated_vitals.csv to S3
```

### 2. Process Data with EMR

```bash
# Submit EMR job with emr/main.py
# Ensure historical data is in S3: raw/historical/heart_attack_prediction_dataset.csv
```

### 3. Train Model

```bash
# Open sagemaker/train_model.ipynb in SageMaker Notebook
# Run all cells to train and deploy model
# Note the endpoint name for Lambda configuration
```

### 4. Deploy Lambda Function

```bash
# Update lambda/config.py with endpoint name and SNS topic ARN
# Deploy Lambda function with lambda_function.py
# Configure trigger (S3 event or scheduled)
```

### 5. Run Analytics

```bash
# Execute athena/ddl.sql to create tables
# Run queries from athena/analysis.sql
```

## Technology Stack

- **Data Processing**: Apache Spark (PySpark) on AWS EMR
- **Machine Learning**: XGBoost on AWS SageMaker
- **Real-time Processing**: AWS Lambda
- **Analytics**: AWS Athena
- **Notifications**: AWS SNS
- **Storage**: AWS S3
- **Languages**: Python, SQL

## Project Structure

```
.
├── athena/
│   ├── ddl.sql              # Athena table definitions
│   └── analysis.sql          # Analytics queries
├── emr/
│   └── main.py              # EMR PySpark processing script
├── lambda/
│   ├── config.py            # Lambda configuration
│   └── lambda_function.py   # Lambda prediction handler
├── phase1_sim/
│   ├── gen_simulated_vitals.py  # Data generation script
│   └── simulated_vitals.csv     # Generated data
├── sagemaker/
│   ├── config.py            # SageMaker configuration
│   ├── preprocess.py        # Preprocessing utilities
│   └── train_model.ipynb    # Model training notebook
├── heart_attack_prediction_dataset.csv  # Historical dataset
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Key Features

- **End-to-End Pipeline**: Complete workflow from data generation to predictions
- **Real-time Alerts**: Automated SNS notifications for high-risk patients
- **Scalable Processing**: EMR for big data processing, SageMaker for ML
- **Queryable Analytics**: Athena tables for SQL-based analysis
- **Feature Alignment**: Consistent preprocessing between training and inference

## Model Details

- **Algorithm**: XGBoost (Gradient Boosting)
- **Task**: Binary Classification (Heart Attack Risk)
- **Evaluation Metric**: AUC (Area Under Curve)
- **Hyperparameters**:
  - Learning rate (eta): 0.1
  - Max depth: 5
  - Subsample: 0.8
  - Column sample by tree: 0.8
  - Number of rounds: 100

## Alerting

The system automatically sends SNS notifications when:
- Patient risk score exceeds threshold (default: 0.45)
- Multiple high-risk patients detected in a batch

Alert message includes:
- Patient ID
- Risk score
- Risk status (HIGH_RISK/LOW_RISK)

## License

This project is part of IFT 512 coursework.

## Author

Jayesh Devre
