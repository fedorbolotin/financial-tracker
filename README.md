# Financial Tracker Telegram Bot

A Telegram bot for tracking financial transactions with support for multiple currencies.

## Server Setup

### Prerequisites

- Docker and Docker Compose installed on your server
- Git installed on your server
- A Telegram Bot Token (obtained from [@BotFather](https://t.me/BotFather))

### Deployment Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/financial-tracker.git
   cd financial-tracker
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your actual credentials:
   ```
   # Telegram Bot Token
   TG_BOT_TOKEN=your_telegram_bot_token

   # Database Configuration
   PG_USER=postgres
   PG_PASSWORD=your_secure_password
   PG_HOST=db
   PG_DATABASE=financial_tracker
   ```

3. **Deploy using Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Verify the deployment**
   ```bash
   docker-compose ps
   ```
   You should see both the bot and database containers running.

### Updating the Application

To update the application to the latest version:

```bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Troubleshooting

- **Check logs**: `docker-compose logs -f bot`
- **Restart services**: `docker-compose restart`
- **Database access**: `docker-compose exec db psql -U postgres -d financial_tracker`

## Features

- User registration with default currency selection
- Transaction recording with flexible format
- Database storage for transactions and user data

## Development Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd financial-tracker
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up your Telegram bot credentials:
   - Create a bot using [@BotFather](https://t.me/BotFather) on Telegram
   - Copy the API token
   - Create a `telegram-bot/credentials.json` file with the following content:
     ```json
     {
       "tg_bot_token": "your-bot-token",
       "pg_user": "postgres",
       "pg_host": "localhost",
       "pg_database": "financial_tracker"
     }
     ```

4. Run the bot locally:
   ```
   python telegram-bot/main.py
   ```

## Development Workflow

### Feature Development

1. Create a new branch for your feature:
   ```
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```
   git add .
   git commit -m "Add your feature"
   ```

3. Push your branch to the remote repository:
   ```
   git push origin feature/your-feature-name
   ```

4. Create a Merge Request (MR) on GitHub/GitLab from your feature branch to main

5. After review and approval, merge the MR through the platform's interface

### Deployment

1. Update the `deploy.sh` script with your server details:
   - `REMOTE_HOST`: Your server's IP address
   - `REMOTE_USER`: SSH username
   - `REMOTE_DIR`: Path to the application on the server
   - `REPO_URL`: Your Git repository URL

2. Make the script executable:
   ```
   chmod +x deploy.sh
   ```

3. Run the deployment script:
   ```
   ./deploy.sh
   ```

   The script will:
   - If you're on a feature branch, prompt you to create an MR or switch to main
   - If you're on main, push changes and deploy to the server

## Docker Deployment

### Local Docker Setup

1. Build and run the Docker containers:
   ```
   docker-compose up -d
   ```

2. Check the logs:
   ```
   docker-compose logs -f
   ```

## Transaction Format

The bot accepts transactions in the following format:
```
[date] amount [currency_code] place
```

Examples:
- `25.03.2024 100 USD Starbucks` - With date and currency
- `100 Starbucks` - Without date (uses current time) and without currency (uses user's default currency)

## Database Schema

The application uses PostgreSQL with the following tables:
- `users`: User information and default currency
- `transactions`: Recorded financial transactions
- `expected_transactions`: Planned future transactions
- `currencies`: Supported currencies
- `exchange_rates`: Currency exchange rates

## Next Steps

- Add transaction categories
- Implement transaction statistics and reports
- Add support for recurring transactions
- Implement budget tracking
- Add multi-currency support with automatic conversion