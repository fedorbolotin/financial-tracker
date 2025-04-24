#!/bin/bash

# Exit on error
set -e

# Configuration
REMOTE_HOST="37.27.178.190"
REMOTE_USER="appuser"
REMOTE_DIR="/opt/apps/financial-tracker"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting deployment process...${NC}"

# SSH into the server and update the application
echo -e "${YELLOW}Step 2: Updating application on server...${NC}"
ssh $REMOTE_USER@$REMOTE_HOST << EOF
    # Navigate to the application directory
    cd $REMOTE_DIR
    
    # Pull the latest changes
    git pull origin main
    
    # Rebuild and restart the Docker containers
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    
    # Check if the containers are running
    docker-compose ps
    
    echo "Deployment completed on \$(date)"
EOF

echo -e "${GREEN}Deployment completed successfully!${NC}" 