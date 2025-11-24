"""
Preprocessing Utilities for Health Data
Contains functions for preprocessing health monitoring data before model training.
"""

import pandas as pd


def preprocess_health_data(df):
    """
    Preprocess health data for machine learning model training.
    
    Steps:
    1. Split blood pressure column into systolic and diastolic
    2. Drop identifier columns (Patient ID, Country, Continent, Hemisphere)
    3. One-hot encode categorical variables
    4. Fill missing values with 0
    
    Args:
        df (pd.DataFrame): Raw health data dataframe
        
    Returns:
        pd.DataFrame: Preprocessed dataframe ready for model training
    """
    df = df.copy()
    
    # Split blood pressure
    if "Blood Pressure" in df.columns:
        bp = df["Blood Pressure"].astype(str).str.split("/", n=1, expand=True)
        df["BP_Systolic"] = pd.to_numeric(bp[0], errors="coerce")
        df["BP_Diastolic"] = pd.to_numeric(bp[1], errors="coerce")
        df.drop(columns=["Blood Pressure"], inplace=True)
    
    # Drop identifiers
    df = df.drop(columns=["Patient ID", "Country", "Continent", "Hemisphere"], errors="ignore")
    
    # One-hot encode categoricals
    df = pd.get_dummies(df, drop_first=True).fillna(0)
    
    return df


def prepare_train_test_split(df, test_size=0.2, random_state=42):
    """
    Prepare train/test split from preprocessed dataframe.
    
    Args:
        df (pd.DataFrame): Preprocessed dataframe
        test_size (float): Proportion of data for testing (default: 0.2)
        random_state (int): Random seed for reproducibility (default: 42)
        
    Returns:
        tuple: (train_df, test_df, X, y) where:
            - train_df: Training dataframe with target and features
            - test_df: Testing dataframe with target and features
            - X: Feature columns
            - y: Target column (Heart Attack Risk)
    """
    proc_df = preprocess_health_data(df)
    
    y = proc_df["Heart Attack Risk"].astype(int)
    X = proc_df.drop(columns=["Heart Attack Risk"])
    
    final_df = pd.concat([y, X], axis=1)
    
    from sklearn.model_selection import train_test_split
    train_df, test_df = train_test_split(
        final_df, 
        test_size=test_size, 
        random_state=random_state, 
        stratify=y
    )
    
    return train_df, test_df, X, y

