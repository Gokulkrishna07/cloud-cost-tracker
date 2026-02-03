#!/bin/bash

# Install PostgreSQL
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE cloud_cost_db;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE cloud_cost_db TO postgres;
ALTER USER postgres CREATEDB;
\q
EOF

echo "PostgreSQL setup completed!"
echo "Database: cloud_cost_db"
echo "User: postgres"
echo "Password: password"