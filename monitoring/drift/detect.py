import pandas as pd
from scipy.stats import ks_2samp
import json

class DriftDetector:
    def __init__(self, reference_data_path):
        self.reference_data = pd.read_csv(reference_data_path)
        
    def detect_drift(self, new_data_df, threshold=0.05):
        """
        Checks for drift in key features using KS test.
        """
        report = {
            "drift_detected": False,
            "feature_drifts": {}
        }
        
        features = ['ec2_hours', 'storage_gb', 'data_transfer_gb', 'rds_usage', 'lambda_invocations']
        
        for feature in features:
            if feature not in new_data_df.columns:
                continue
                
            stat, p_value = ks_2samp(self.reference_data[feature], new_data_df[feature])
            
            is_drift = p_value < threshold
            report["feature_drifts"][feature] = {
                "p_value": float(p_value),
                "drift": is_drift
            }
            
            if is_drift:
                report["drift_detected"] = True
                
        return report

if __name__ == "__main__":
    # Example usage
    detector = DriftDetector("data/raw/cloud_cost_data.csv")
    # Simulate new data
    new_data = pd.read_csv("data/raw/cloud_cost_data.csv").sample(50) 
    # Add bias to simulate drift
    new_data['ec2_hours'] = new_data['ec2_hours'] * 1.5 
    
    drift_report = detector.detect_drift(new_data)
    print(json.dumps(drift_report, indent=2))
