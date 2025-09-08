import logging
from typing import Any, Dict, Optional

import pandas as pd
from sqlalchemy import create_engine, URL, text

from config.settings import get_credentials


class Postgres:
    def __init__(self, credentials: Optional[Dict[str, str]] = None) -> None:
        self.cred = credentials or get_credentials()
        self._url_object = URL.create(
            'postgresql+psycopg2',
            username=self.cred['pg_user'],
            password=self.cred['pg_password'],
            host=self.cred['pg_host'],
            database=self.cred['pg_database'],
        )

        self.engine = create_engine(self._url_object)

    # Generic helpers
    def fetch_df(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        with self.engine.connect() as connection:
            return pd.read_sql_query(text(query), connection, params=params)

    def fetch_one(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        with self.engine.connect() as connection:
            result = connection.execute(text(query), params or {})
            row = result.mappings().fetchone()
            return dict(row) if row else None

    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        with self.engine.connect() as connection:
            result = connection.execute(text(query), params or {})
            connection.commit()
            return result.rowcount or 0

    def insert_row(self, table: str, values: Dict[str, Any]) -> int:
        if not values:
            return 0
        columns = ', '.join(values.keys())
        placeholders = ', '.join(f":{k}" for k in values.keys())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return self.execute(query, values)

    def delete_where(self, table: str, where_sql: str, params: Dict[str, Any]) -> int:
        query = f"DELETE FROM {table} WHERE {where_sql}"
        return self.execute(query, params)


