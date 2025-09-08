from typing import Optional

from .transaction import Transaction
from utils.db import Postgres


class TransactionRepository:
    def __init__(self, db: Postgres) -> None:
        self.db = db

    def insert(self, t: Transaction) -> bool:
        return self.db.insert_row('transactions', t.to_dict()) > 0

    def delete_by_id(self, transaction_id: str) -> int:
        return self.db.delete_where('transactions', 'transaction_id = :id', {'id': transaction_id})


