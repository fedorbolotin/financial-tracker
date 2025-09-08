from typing import Optional

from .user import User
from utils.db import Postgres


class UserRepository:
    def __init__(self, db: Postgres) -> None:
        self.db = db

    def insert(self, user: User) -> bool:
        return self.db.insert_row('users', user.to_dict()) > 0

    def get_by_telegram(self, username: str) -> Optional[dict]:
        return self.db.fetch_one(
            'SELECT user_uuid, telegram_account, default_currency_code FROM users WHERE telegram_account = :u',
            {'u': username}
        )


