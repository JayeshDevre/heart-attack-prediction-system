-- Analysis Queries
-- SQL queries for analyzing health monitoring and heart attack prediction data

-- Use the healthcare analysis database
USE healthcare_analysis_db;

-- ============================================================================
-- Core Analytics Queries
-- ============================================================================

-- Query d: Who are the highest-risk patients and what are their other features?
-- Returns the top predicted-risk patients (highest probability first) together 
-- with vitals fields from the processed EMR output. This produces a ranked 
-- triage list clinicians can use for immediate outreach or case review.
SELECT
  p."Patient ID" AS patient_id,
  p."Heart Attack Risk" AS predicted_risk,
  p.Risk_Status,
  from_iso8601_timestamp(p.ScoredAt) AS scored_at,
  d.Age,
  d.Sex,
  d."Cholesterol",
  d."Blood Pressure",
  d.Country
FROM heart_attack_predictions p
LEFT JOIN heart_attack_processed_data d
  ON p."Patient ID" = d."Patient ID"
ORDER BY p."Heart Attack Risk" DESC
LIMIT 200;

-- Query e: How many patients exceed the alert threshold (> 0.45)?
-- Counts the number of prediction records with probability above 0.45. 
-- This gives a quick estimate of how many patients currently require urgent 
-- follow-up under the chosen threshold.
SELECT
  COUNT(*) AS high_risk_count
FROM heart_attack_predictions
WHERE "Heart Attack Risk" > 0.45;

-- Query f: Which age groups have higher average predicted risk?
-- Joins predictions with processed vitals data and computes average predicted 
-- risk for age cohorts. This reveals which age bands exhibit higher 
-- model-predicted risk, useful for targeted screening or educational outreach.
SELECT
  CASE
    WHEN d.Age < 30 THEN '20-29'
    WHEN d.Age BETWEEN 30 AND 39 THEN '30-39'
    WHEN d.Age BETWEEN 40 AND 49 THEN '40-49'
    WHEN d.Age BETWEEN 50 AND 59 THEN '50-59'
    WHEN d.Age BETWEEN 60 AND 69 THEN '60-69'
    ELSE '70+'
  END AS age_group,
  ROUND(AVG(p."Heart Attack Risk"), 3) AS avg_predicted_risk,
  COUNT(*) AS patients
FROM heart_attack_predictions p
JOIN heart_attack_processed_data d
  ON p."Patient ID" = d."Patient ID"
GROUP BY
  CASE
    WHEN d.Age < 30 THEN '20-29'
    WHEN d.Age BETWEEN 30 AND 39 THEN '30-39'
    WHEN d.Age BETWEEN 40 AND 49 THEN '40-49'
    WHEN d.Age BETWEEN 50 AND 59 THEN '50-59'
    WHEN d.Age BETWEEN 60 AND 69 THEN '60-69'
    ELSE '70+'
  END
ORDER BY age_group;

-- Query g: Is shorter sleep associated with higher predicted risk?
-- Buckets patients by integer sleep hours and shows average sleep and average 
-- predicted risk per bucket. This gives a quick exploratory test of association 
-- between sleep duration and model-predicted risk.
SELECT
  FLOOR(d."Sleep Hours Per Day") AS sleep_hours_floor,
  ROUND(AVG(d."Sleep Hours Per Day"), 2) AS avg_sleep,
  ROUND(AVG(p."Heart Attack Risk"), 3) AS avg_predicted_risk,
  COUNT(*) AS patients
FROM heart_attack_predictions p
JOIN heart_attack_processed_data d
  ON p."Patient ID" = d."Patient ID"
GROUP BY FLOOR(d."Sleep Hours Per Day")
ORDER BY sleep_hours_floor;

-- Query h: How does physical activity correlate with heart rate and predicted risk?
-- Computes overall averages: activity days, heart rate, and predicted risk 
-- across matched patients. This provides a quick sanity-check whether more 
-- activity correlates with lower heart rate and risk in your data.
SELECT
  ROUND(AVG(d."Physical Activity Days Per Week"), 2) AS avg_activity_days,
  ROUND(AVG(d."Heart Rate"), 1) AS avg_heart_rate,
  ROUND(AVG(p."Heart Attack Risk"), 3) AS avg_predicted_risk
FROM heart_attack_predictions p
JOIN heart_attack_processed_data d
  ON p."Patient ID" = d."Patient ID";
