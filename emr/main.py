"""
EMR Main Processing Script
Main entry point for EMR (Elastic MapReduce) job processing.
"""
from pyspark.sql import SparkSession

from pyspark.sql.functions import avg, sum as _sum, round as _round, col, concat_ws

from pyspark.sql.types import IntegerType

# CONFIG

HIST_PATH = "s3://healthcare-project-data-jayesh-devre/raw/historical/heart_attack_prediction_dataset.csv"

SIM_PATH  = "s3://healthcare-project-data-jayesh-devre/raw/simulated/simulated_vitals.csv"

OUT_PATH  = "s3://healthcare-project-data-jayesh-devre/processed/final_health_dataset_csv/"

# Start Spark session

spark = SparkSession.builder.appName("AggregateVitalsJoinFinal").getOrCreate()

# Load datasets

hist = spark.read.option("header", True).csv(HIST_PATH, inferSchema=True)

sim  = spark.read.option("header", True).csv(SIM_PATH, inferSchema=True)

# Aggregate simulated vitals (7 days → weekly averages)

agg = sim.groupBy("Patient ID").agg(

    _round(avg(col("Heart Rate")), 0).alias("Heart Rate"),

    _round(avg(col("BP_Systolic")), 0).alias("AvgBP_Systolic"),

    _round(avg(col("BP_Diastolic")), 0).alias("AvgBP_Diastolic"),

    _round(avg(col("Sleep Hours Per Day")), 2).alias("Sleep Hours Per Day"),

    _sum(col("Physical Activity Per day")).alias("Physical Activity Days Per Week")

)

# Combine averaged systolic & diastolic into "Blood Pressure"

agg = agg.withColumn(

    "Blood Pressure",

    concat_ws("/", col("AvgBP_Systolic").cast(IntegerType()), col("AvgBP_Diastolic").cast(IntegerType()))

).drop("AvgBP_Systolic", "AvgBP_Diastolic")

# Clean historical dataset (drop old vitals and risk column)

hist_clean = hist.drop(

    "Heart Rate",

    "Blood Pressure",

    "Sleep Hours Per Day",

    "Physical Activity Days Per Week",

    "Heart Attack Risk"

)

# Join historical demographics with aggregated vitals

final =agg.join(hist_clean, on="Patient ID", how="left")

# Write final dataset to CSV (ready for SageMaker)

final.coalesce(1).write.mode("overwrite").option("header", True).csv(OUT_PATH)

print("Final dataset written successfully to:", OUT_PATH)

print("Columns in output:", final.columns)

spark.stop()