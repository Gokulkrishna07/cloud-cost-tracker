import os
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'cloud_cost_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password'),
            'port': os.getenv('DB_PORT', '5432')
        }
    
    def get_connection(self):
        return psycopg2.connect(**self.db_config)
    
    def create_tables(self):
        """Create necessary tables for storing prediction data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ec2_hours FLOAT NOT NULL,
                storage_gb FLOAT NOT NULL,
                data_transfer_gb FLOAT NOT NULL,
                rds_usage FLOAT NOT NULL,
                lambda_invocations INTEGER NOT NULL,
                budget FLOAT NOT NULL,
                predicted_cost FLOAT,
                actual_cost FLOAT,
                risk_level VARCHAR(10),
                overrun BOOLEAN,
                model_version VARCHAR(50)
            )
        """)
        
        # Create training_data table (transformed from predictions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_data (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                ec2_hours FLOAT NOT NULL,
                storage_gb FLOAT NOT NULL,
                data_transfer_gb FLOAT NOT NULL,
                rds_usage FLOAT NOT NULL,
                lambda_invocations INTEGER NOT NULL,
                daily_cost FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def save_prediction(self, prediction_data):
        """Save prediction data to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO predictions (
                ec2_hours, storage_gb, data_transfer_gb, rds_usage, 
                lambda_invocations, budget, predicted_cost, risk_level, 
                overrun, model_version
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            prediction_data['ec2_hours'],
            prediction_data['storage_gb'],
            prediction_data['data_transfer_gb'],
            prediction_data['rds_usage'],
            prediction_data['lambda_invocations'],
            prediction_data['budget'],
            prediction_data.get('predicted_cost'),
            prediction_data.get('risk_level'),
            prediction_data.get('overrun'),
            prediction_data.get('model_version', 'v1')
        ))
        
        prediction_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return prediction_id
    
    def get_training_data(self):
        """Get data for model training"""
        conn = self.get_connection()
        
        # Get data from training_data table
        df = pd.read_sql_query("""
            SELECT date, ec2_hours, storage_gb, data_transfer_gb, 
                   rds_usage, lambda_invocations, daily_cost
            FROM training_data 
            ORDER BY date
        """, conn)
        
        conn.close()
        return df
    
    def add_training_data(self, data):
        """Add new training data (when actual costs are known)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO training_data (
                date, ec2_hours, storage_gb, data_transfer_gb, 
                rds_usage, lambda_invocations, daily_cost
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['date'],
            data['ec2_hours'],
            data['storage_gb'],
            data['data_transfer_gb'],
            data['rds_usage'],
            data['lambda_invocations'],
            data['daily_cost']
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def get_recent_predictions(self, limit=10):
        """Get recent predictions for display"""
        conn = self.get_connection()
        
        df = pd.read_sql_query("""
            SELECT timestamp, ec2_hours, storage_gb, predicted_cost, 
                   budget, risk_level, overrun
            FROM predictions 
            ORDER BY timestamp DESC 
            LIMIT %s
        """, conn, params=[limit])
        
        conn.close()
        return df