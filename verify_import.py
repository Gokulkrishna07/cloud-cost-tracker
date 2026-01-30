import sys
import os
sys.path.append(os.getcwd())
try:
    from training.train import train_model
    print("Import Successful")
except Exception as e:
    print(f"Import Failed: {e}")
