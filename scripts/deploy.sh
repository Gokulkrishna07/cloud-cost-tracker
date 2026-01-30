#!/bin/bash

# Usage: ./scripts/deploy.sh <user> <host> <key_path>
# Example: ./scripts/deploy.sh ubuntu 1.2.3.4 ~/.ssh/myvideo-key.pem

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <user> <host> <path_to_private_key>"
    exit 1
fi

USER=$1
HOST=$2
KEY=$3

echo "Deploying to $USER@$HOST using key $KEY"

# Ensure target directory exists
ssh -i "$KEY" "$USER@$HOST" "mkdir -p ~/cloud-cost-mlops"

# Copy files (excluding .git and venv/artifacts to save bandwidth/time if not needed)
# We need docker-compose.yml, Dockerfile, requirements.txt, src (api, training), and data (schema)
# For simplicity, we copy everything but exclude some common heavy/unnecessary dirs
echo "Copying files..."
rsync -avz -e "ssh -i $KEY" \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude 'mlruns' \
    --exclude 'mlartifacts' \
    --exclude 'venv' \
    . "$USER@$HOST":~/cloud-cost-mlops

# Run Deployment on Remote
echo "Starting services on remote..."
ssh -i "$KEY" "$USER@$HOST" << EOF
    cd ~/cloud-cost-mlops
    
    # Check if docker is available
    if ! command -v docker &> /dev/null; then
        echo "Docker not found. Attempting to install..."
        chmod +x scripts/setup_vm.sh
        ./scripts/setup_vm.sh
    fi
    
    # Build and Start
    sudo docker compose down
    sudo docker compose up -d --build
    
    echo "Deployment Complete. Services running."
EOF
