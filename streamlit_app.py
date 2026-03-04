import os

import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://103.49.125.28:8501")

st.set_page_config(
    page_title="Churn Prediction",
    page_icon="📊",
    layout="wide",
)

st.title("Telco Customer Churn Prediction")
st.markdown("---")

with st.sidebar:
    st.header("Customer Profile")

    st.subheader("Demographics")
    gender = st.selectbox("Gender", ["Male", "Female"])
    senior_citizen = st.selectbox("Senior Citizen", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    partner = st.selectbox("Partner", ["Yes", "No"])
    dependents = st.selectbox("Dependents", ["Yes", "No"])

    st.subheader("Account")
    tenure = st.slider("Tenure (months)", 0, 72, 12)
    contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
    paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
    payment_method = st.selectbox("Payment Method", [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ])
    monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, value=65.0, step=0.5)
    total_charges = st.number_input("Total Charges ($)", min_value=0.0, value=float(tenure * monthly_charges), step=1.0)

    st.subheader("Services")
    phone_service = st.selectbox("Phone Service", ["Yes", "No"])
    multiple_lines = st.selectbox("Multiple Lines", ["Yes", "No", "No phone service"])
    internet_service = st.selectbox("Internet Service", ["Fiber optic", "DSL", "No"])
    online_security = st.selectbox("Online Security", ["Yes", "No", "No internet service"])
    online_backup = st.selectbox("Online Backup", ["Yes", "No", "No internet service"])
    device_protection = st.selectbox("Device Protection", ["Yes", "No", "No internet service"])
    tech_support = st.selectbox("Tech Support", ["Yes", "No", "No internet service"])
    streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"])
    streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"])

predict_clicked = st.sidebar.button("Predict Churn", type="primary", use_container_width=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Tenure", f"{tenure} months")
with col2:
    st.metric("Monthly Charges", f"${monthly_charges:.2f}")
with col3:
    st.metric("Contract", contract)

st.markdown("---")

if predict_clicked:
    payload = {
        "gender": gender,
        "SeniorCitizen": senior_citizen,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless_billing,
        "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
    }

    with st.spinner("Predicting..."):
        try:
            response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()

            churn = result["churn_prediction"]
            probability = result["churn_probability"]
            risk = result["risk_level"]
            confidence = result["confidence"]
            model_type = result.get("model_version", result.get("model_type", "N/A"))

            risk_colors = {"LOW": "green", "MEDIUM": "orange", "HIGH": "red"}
            color = risk_colors[risk]

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                label = "WILL CHURN" if churn == 1 else "WILL NOT CHURN"
                delta_color = "inverse" if churn == 1 else "normal"
                st.metric("Prediction", label)
            with c2:
                st.metric("Churn Probability", f"{probability:.1%}")
            with c3:
                st.metric("Risk Level", risk)
            with c4:
                st.metric("Model Confidence", f"{confidence:.1%}")

            st.progress(probability, text=f"Churn probability: {probability:.1%}")

            if churn == 1:
                st.error(f"⚠️ This customer is at **{risk} RISK** of churning ({probability:.1%} probability).")
            else:
                st.success(f"✅ This customer is at **{risk} RISK** of churning ({probability:.1%} probability).")

        except requests.exceptions.ConnectionError:
            st.error(f"Cannot connect to API at `{API_URL}`. Make sure the API is running.")
        except requests.exceptions.HTTPError as e:
            st.error(f"API error: {e.response.status_code} — {e.response.text}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
else:
    st.info("Configure the customer profile in the sidebar and click **Predict Churn**.")
