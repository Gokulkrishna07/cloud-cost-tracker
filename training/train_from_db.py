import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from database.db_manager import DatabaseManager
from training.feature_engineering import feature_engineering

def train_model_from_db():
    """Train model using data from database"""
    db = DatabaseManager()
    
    # Get training data from database
    df = db.get_training_data()
    
    if len(df) < 10:
        print("Not enough training data in database. Need at least 10 records.")
        return
    
    # Apply feature engineering
    df = feature_engineering(df)
    
    if len(df) == 0:
        print("No data remaining after feature engineering")
        return
    
    # Features and Target
    X = df[['ec2_hours', 'storage_gb', 'data_transfer_gb', 'rds_usage', 'lambda_invocations', 
            'lag_1', 'rolling_3', 'rolling_7', 'is_weekend']]
    y = df['daily_cost']
    
    # Split Data (Time-based split)
    train_size = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
    
    # MLflow Tracking
    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("cloud_cost_prediction")
    
    with mlflow.start_run():
        # Model Parameters
        params = {
            "n_estimators": 100,
            "random_state": 42,
            "max_depth": 10
        }
        mlflow.log_params(params)
        
        # Train Model
        model = RandomForestRegressor(**params)
        model.fit(X_train, y_train)
        
        # Evaluate
        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        rmse = mse ** 0.5
        
        print(f"MAE: {mae}")
        print(f"RMSE: {rmse}")
        
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        
        # Log Model
        signature = mlflow.models.infer_signature(X_train, model.predict(X_train))
        mlflow.sklearn.log_model(model, "model", signature=signature, registered_model_name="cost_prediction_model")
        
        print(f"Model logged to MLflow")

if __name__ == "__main__":
    train_model_from_db()