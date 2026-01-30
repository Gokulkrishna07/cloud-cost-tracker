from pydantic import BaseModel, Field
import pandera as pa

# Input Schema for individual records (API)
class CloudUsageInput(BaseModel):
    ec2_hours: float = Field(..., ge=0, description="Total EC2 compute hours used in a day")
    storage_gb: float = Field(..., ge=0, description="Average storage consumed in GB")
    data_transfer_gb: float = Field(..., ge=0, description="Outbound data transfer in GB")
    rds_usage: float = Field(..., ge=0, description="Relational database usage units")
    lambda_invocations: int = Field(..., ge=0, description="Number of AWS Lambda invocations")
    budget: float = Field(..., gt=0, description="Defined budget for the day")

# Output Schema for API Response
class CostPredictionOutput(BaseModel):
    predicted_cost: float
    budget: float
    overrun: bool
    risk_level: str
    model_version: str
    timestamp: str

# Pandera Schema for Batch Training Data (Functional API for better compatibility)
TrainingDataSchema = pa.DataFrameSchema({
    "date": pa.Column(pa.DateTime, coerce=True),
    "ec2_hours": pa.Column(float, checks=pa.Check.ge(0)),
    "storage_gb": pa.Column(float, checks=pa.Check.ge(0)),
    "data_transfer_gb": pa.Column(float, checks=pa.Check.ge(0)),
    "rds_usage": pa.Column(float, checks=pa.Check.ge(0)),
    "lambda_invocations": pa.Column(int, checks=pa.Check.ge(0)),
    "daily_cost": pa.Column(float, checks=pa.Check.ge(0))
})
