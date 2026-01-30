import requests
import json

url = "http://localhost:8000/predict"
payload = {
    "ec2_hours": 100,
    "storage_gb": 500,
    "data_transfer_gb": 20,
    "rds_usage": 50,
    "lambda_invocations": 1000,
    "budget": 200.0
}
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print(f"Error: {e}")
