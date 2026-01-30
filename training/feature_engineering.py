import pandas as pd

def feature_engineering(df):
    """
    Adds lag features and rolling averages.
    """
    print(f"Feature engineering input columns: {list(df.columns)}")
    
    if 'date' not in df.columns:
        raise ValueError(f"Missing 'date' column in dataframe. Available columns: {list(df.columns)}")
    
    df = df.sort_values(by="date").reset_index(drop=True)
    
    # Lag features
    df['lag_1'] = df['daily_cost'].shift(1)
    
    # Rolling averages
    df['rolling_3'] = df['daily_cost'].rolling(window=3).mean().shift(1)
    df['rolling_7'] = df['daily_cost'].rolling(window=7).mean().shift(1)
    
    # Date features
    df['is_weekend'] = df['date'].dt.dayofweek.isin([5, 6]).astype(int)
    
    # Fill NaN values with 0 for lag and rolling features (for first few rows)
    df['lag_1'] = df['lag_1'].fillna(0)
    df['rolling_3'] = df['rolling_3'].fillna(df['daily_cost'])
    df['rolling_7'] = df['rolling_7'].fillna(df['daily_cost'])
    
    print(f"Feature engineering output columns: {list(df.columns)}")
    return df
