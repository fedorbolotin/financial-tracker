import os
import logging

# Global settings
CHOOSING_CURRENCY = 1
VALID_CURRENCIES = ['EUR', 'USD', 'RUB']

# Get credentials from environment variables
def get_credentials():
    required_keys = ['TG_BOT_TOKEN', 'PG_USER', 'PG_PASSWORD', 'PG_HOST', 'PG_DATABASE']

    if all(key in os.environ for key in required_keys):
        return {
            'tg_bot_token': os.environ['TG_BOT_TOKEN'],
            'pg_user': os.environ['PG_USER'],
            'pg_password': os.environ['PG_PASSWORD'],
            'pg_host': os.environ['PG_HOST'],
            'pg_database': os.environ['PG_DATABASE']
        }
    else: 
        missing_vars = []
        for var in required_keys:
            if var not in os.environ:
                missing_vars.append(var)
        logging.error(f'Missing environment variables: {missing_vars}')
        raise ValueError(f'Missing environment variables: {missing_vars}')
