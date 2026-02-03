import requests
import json

# Test different possible URLs
urls_to_test = [
    "http://localhost:8000/predict",
    "http://127.0.0.1:8000/predict", 
    "http://0.0.0.0:8000/predict"
]

payload = {
    "ec2_hours": 100,
    "storage_gb": 500,
    "data_transfer_gb": 20,
    "rds_usage": 50,
    "lambda_invocations": 1000,
    "budget": 200.0
}
headers = {'Content-Type': 'application/json'}

for url in urls_to_test:
    try:
        print(f"\nTesting: {url}")
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")