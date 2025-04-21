#!/bin/bash

# Exit on error
set -e

# Database configuration
DB_USER=${PG_USER:-postgres}
DB_PASSWORD=${PG_PASSWORD:-postgres}
DB_HOST=${PG_HOST:-localhost}
DB_NAME=${PG_DATABASE:-financial_tracker}

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Initializing database...${NC}"

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Error: psql is not installed. Please install PostgreSQL client.${NC}"
    exit 1
fi

# Create database if it doesn't exist
echo -e "${YELLOW}Creating database if it doesn't exist...${NC}"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME"

# Initialize database with schema
echo -e "${YELLOW}Initializing database schema...${NC}"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f database/init_tables.sql

echo -e "${GREEN}Database initialization completed successfully!${NC}" 