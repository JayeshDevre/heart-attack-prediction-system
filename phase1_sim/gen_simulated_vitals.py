"""
Generate Simulated Vital Signs Data
This script generates simulated patient vital signs data for testing and development.
"""
import pandas as pd
import random
import time

patient_ids = [
    "BMW7812","CZE1114","BNI9906","JLN3497","GFO8847","ZOO7941",
    "WYV0966","XXM0972","XCQ5937","FTJ5456","HSD6283","YSP0073",
    "FPS0415","YYU9565","VTW9069","DCY3282","DXB2434","COP0566",
    "XBI0592","RQX1211"
]

records = []
for pid in patient_ids:
    for i in range(7):
        record = {
            "Patient ID": pid,
            "Heart Rate": random.randint(60, 110),
            "BP_Systolic": random.randint(100, 170),
            "BP_Diastolic": random.randint(60, 120),
            "Sleep Hours Per Day": round(random.uniform(3, 9), 1),
            "Physical Activity Per day": random.randint(0, 1),
            "Timestamp": int(time.time()) + i
        }
        records.append(record)

df = pd.DataFrame(records)
df.to_csv("simulated_vitals.csv", index=False)
print("Generated simulated_vitals.csv")



