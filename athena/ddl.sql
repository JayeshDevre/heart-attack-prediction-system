-- DDL (Data Definition Language) Scripts
-- Create tables and schemas for health monitoring data in Athena

-- 5.1: Create Athena Database & Set Results Location
-- Note: Set Query result location to s3://healthcare-project-data-jayesh-devre/athena/results/ in Athena UI Settings
CREATE DATABASE IF NOT EXISTS healthcare_analysis_db;

-- Use the database
USE healthcare_analysis_db;

-- 5.2a: Create Table: Processed EMR Output (Vitals data)
-- This table makes EMR output queryable in Athena for joining vitals data with prediction scores
CREATE EXTERNAL TABLE IF NOT EXISTS heart_attack_processed_data (
  `Patient ID` string,
  `Heart Rate` double,
  `Sleep Hours Per Day` double,
  `Physical Activity Days Per Week` int,
  `Blood Pressure` string,
  `Age` int,
  `Sex` string,
  `Cholesterol` double,
  `Diabetes` int,
  `Family History` int,
  `Smoking` int,
  `Obesity` int,
  `Alcohol Consumption` double,
  `Exercise Hours Per Week` double,
  `Diet` string,
  `Previous Heart Problems` int,
  `Medication Use` int,
  `Stress Level` int,
  `Sedentary Hours Per Day` double,
  `Income` bigint,
  `BMI` double,
  `Triglycerides` int,
  `Country` string,
  `Continent` string,
  `Hemisphere` string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  "separatorChar" = ",",
  "quoteChar"     = "\""
)
LOCATION 's3://healthcare-project-data-jayesh-devre/processed/final_health_dataset_csv/'
TBLPROPERTIES ('skip.header.line.count'='1');

-- Verify the processed data table creation
-- SELECT COUNT(*) FROM heart_attack_processed_data;

-- 5.2b: Create Table: Predictions Data
-- This table makes Lambda prediction outputs queryable in Athena
CREATE EXTERNAL TABLE IF NOT EXISTS heart_attack_predictions (
  `Patient ID` string,
  `Heart Attack Risk` double,
  `Risk_Status` string,
  `ScoredAt` string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  "separatorChar" = ",",
  "quoteChar"     = "\""
)
LOCATION 's3://healthcare-project-data-jayesh-devre/predictions/'
TBLPROPERTIES ('skip.header.line.count'='1');

-- Verify the predictions table creation
-- SELECT COUNT(*) FROM heart_attack_predictions;
