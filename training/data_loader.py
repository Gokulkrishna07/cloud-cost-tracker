import pandas as pd
import os
from data.schema.validation import TrainingDataSchema

def load_data(file_path="data/raw/cloud_cost_data.csv"):
    """
    Loads data and validates schema.
    """
    # Handle relative path from different working directories
    if not os.path.exists(file_path):
        # Try from project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_root, file_path)
        
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read the CSV and check its structure
    df = pd.read_csv(file_path)
    print(f"Loaded CSV columns: {list(df.columns)}")
    
    # Check if this is AWS Cost Explorer format (Service column exists)
    if 'Service' in df.columns:
        print("Detected AWS Cost Explorer format, transforming...")
        df = transform_aws_cost_data(df)
    elif 'date' in df.columns:
        print("Detected standard format with date column")
        df['date'] = pd.to_datetime(df['date'])
    else:
        raise ValueError(f"Unrecognized CSV format. Expected 'Service' or 'date' column, got: {list(df.columns)}")
    
    print(f"Final columns after transformation: {list(df.columns)}")
    
    # Validate Schema
    try:
        TrainingDataSchema.validate(df)
        print("Data schema validation passed.")
    except Exception as e:
        print(f"Data schema validation failed: {e}")
        raise e
        
    return df

def transform_aws_cost_data(df):
    """
    Transform AWS Cost Explorer CSV format to training format.
    """
    # Remove the 'Service total' row
    df = df[df['Service'] != 'Service total'].copy()
    
    # Convert Service column (dates) to datetime
    df['date'] = pd.to_datetime(df['Service'])
    
    # Extract relevant features from AWS services, handling NaN values
    df['ec2_hours'] = pd.to_numeric(df.get('EC2-Other($)', 0), errors='coerce').fillna(0) * 24
    df['storage_gb'] = pd.to_numeric(df.get('S3($)', 0), errors='coerce').fillna(0) * 100
    df['data_transfer_gb'] = pd.to_numeric(df.get('CloudWatch($)', 0), errors='coerce').fillna(0) * 10
    df['rds_usage'] = pd.to_numeric(df.get('Relational Database Service($)', 0), errors='coerce').fillna(0)
    df['lambda_invocations'] = (pd.to_numeric(df.get('Lambda($)', 0), errors='coerce').fillna(0) * 1000000).astype(int)
    df['daily_cost'] = pd.to_numeric(df.get('Total costs($)', 0), errors='coerce').fillna(0)
    
    # Select only the required columns
    return df[['date', 'ec2_hours', 'storage_gb', 'data_transfer_gb', 'rds_usage', 'lambda_invocations', 'daily_cost']]
