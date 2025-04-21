#!/bin/bash

# Exit on error
set -e

# Configuration
REMOTE_HOST="your-server-ip"
REMOTE_USER="your-username"
REMOTE_DIR="/path/to/your/app"
REPO_URL="your-git-repo-url"
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting deployment process...${NC}"

# Check if we're on a feature branch
if [ "$BRANCH_NAME" != "main" ]; then
    echo -e "${YELLOW}You're on branch: ${BRANCH_NAME}${NC}"
    echo -e "${YELLOW}This script is designed to deploy from the main branch.${NC}"
    echo -e "${YELLOW}Do you want to:${NC}"
    echo -e "1) Create a Merge Request to main (recommended)"
    echo -e "2) Deploy directly from this branch (not recommended)"
    echo -e "3) Switch to main branch and deploy"
    read -p "Enter your choice (1-3): " choice
    
    case $choice in
        1)
            echo -e "${YELLOW}Creating Merge Request...${NC}"
            # Push the current branch
            git push origin $BRANCH_NAME
            
            # Open the MR creation page in the browser
            if [[ $REPO_URL == *"github.com"* ]]; then
                # For GitHub
                open "https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]//' | sed 's/\.git$//')/compare/main...$BRANCH_NAME?expand=1"
            elif [[ $REPO_URL == *"gitlab.com"* ]]; then
                # For GitLab
                open "https://gitlab.com/$(git config --get remote.origin.url | sed 's/.*gitlab.com[:/]//' | sed 's/\.git$//')/-/merge_requests/new?merge_request[source_branch]=$BRANCH_NAME&merge_request[target_branch]=main"
            else
                echo -e "${YELLOW}Please create a Merge Request manually from $BRANCH_NAME to main${NC}"
            fi
            echo -e "${GREEN}Merge Request created. Please merge it through the platform's interface before deploying.${NC}"
            exit 0
            ;;
        2)
            echo -e "${RED}Warning: Deploying directly from a feature branch is not recommended.${NC}"
            read -p "Are you sure you want to continue? (y/n): " confirm
            if [ "$confirm" != "y" ]; then
                echo -e "${YELLOW}Deployment cancelled.${NC}"
                exit 0
            fi
            ;;
        3)
            echo -e "${YELLOW}Switching to main branch...${NC}"
            git checkout main
            git pull origin main
            BRANCH_NAME="main"
            ;;
        *)
            echo -e "${RED}Invalid choice. Exiting.${NC}"
            exit 1
            ;;
    esac
fi

# Step 1: Push changes to the remote repository (if on main)
if [ "$BRANCH_NAME" = "main" ]; then
    echo -e "${YELLOW}Step 1: Pushing changes to remote repository...${NC}"
    git add .
    git commit -m "Update: $(date +%Y-%m-%d-%H-%M-%S)"
    git push origin main
fi

# Step 2: SSH into the server and update the application
echo -e "${YELLOW}Step 2: Updating application on server...${NC}"
ssh $REMOTE_USER@$REMOTE_HOST << EOF
    # Navigate to the application directory
    cd $REMOTE_DIR
    
    # Pull the latest changes
    git pull origin main
    
    # Check if .env file exists, if not create it from example
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Creating .env file from example...${NC}"
        cp .env.example .env
        echo -e "${RED}Please update the .env file with your actual credentials before continuing.${NC}"
        exit 1
    fi
    
    # Rebuild and restart the Docker containers
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    
    # Check if the containers are running
    docker-compose ps
    
    echo "Deployment completed on \$(date)"
EOF

echo -e "${GREEN}Deployment completed successfully!${NC}" 