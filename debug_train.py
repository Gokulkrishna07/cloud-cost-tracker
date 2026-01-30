import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
import os
import shutil

# Force clean slate
if os.path.exists("mlruns"):
    shutil.rmtree("mlruns")
    
mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("cloud_cost_prediction")

print("Starting debug training...")
with mlflow.start_run():
    # Dummy training
    X = [[0,0,0,0,0,0,0,0,0]]
    y = [0]
    model = RandomForestRegressor()
    model.fit(X, y)
    
    mlflow.log_metric("test_metric", 1.0)
    
    signature = mlflow.models.infer_signature(X, model.predict(X))
    mlflow.sklearn.log_model(model, "model", signature=signature)
    print("Model logged successfully to mlruns")
