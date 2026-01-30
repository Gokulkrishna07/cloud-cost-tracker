import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_synthetic_data(num_days=100, start_date="2024-01-01", output_path="data/raw/cloud_cost_data.csv"):
    """
    Generates synthetic cloud usage data with some seasonality and trend.
    """
    np.random.seed(42)
    dates = [datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i) for i in range(num_days)]
    
    # Base trends
    trend = np.linspace(0, 1, num_days) * 0.5  # Slight upward trend
    
    # Seasonality (weekly pattern)
    seasonality = np.sin(np.linspace(0, num_days * 2 * np.pi / 7, num_days)) * 0.2
    
    # Generate Features
    ec2_hours = np.maximum(0, 100 + 50 * trend + 20 * seasonality + np.random.normal(0, 10, num_days))
    storage_gb = np.maximum(0, 500 + 100 * trend + np.random.normal(0, 5, num_days)) # Storage grows steadily
    data_transfer_gb = np.maximum(0, 20 + 10 * trend + 10 * seasonality + np.random.normal(0, 5, num_days))
    rds_usage = np.maximum(0, 50 + 20 * trend + 5 * seasonality + np.random.normal(0, 2, num_days))
    lambda_invocations = np.maximum(0, 1000 + 500 * trend + 200 * seasonality + np.random.normal(0, 100, num_days)).astype(int)
    
    # Generate Target (Cost)
    # Simple linear combination with some noise
    # Prices: EC2=$0.05/hr, Storage=$0.02/GB, Transfer=$0.1/GB, RDS=$0.1/unit, Lambda=$0.000002/inv
    daily_cost = (
        ec2_hours * 0.05 + 
        storage_gb * 0.02 + 
        data_transfer_gb * 0.1 + 
        rds_usage * 0.1 + 
        lambda_invocations * 0.000002
    )
    
    # Add random noise to cost to make it non-deterministic
    daily_cost += np.random.normal(0, 2, num_days)
    daily_cost = np.maximum(0, daily_cost)

    df = pd.DataFrame({
        "date": dates,
        "ec2_hours": ec2_hours,
        "storage_gb": storage_gb,
        "data_transfer_gb": data_transfer_gb,
        "rds_usage": rds_usage,
        "lambda_invocations": lambda_invocations,
        "daily_cost": daily_cost
    })
    
    # Save processed to ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_days} days of data at {output_path}")
    return df

if __name__ == "__main__":
    generate_synthetic_data(num_days=365) # Generate 1 year of data
