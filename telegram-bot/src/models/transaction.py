import uuid
import datetime
import re
from dataclasses import dataclass, field
from typing import Optional, Tuple
from dateparser.search import search_dates
import dateparser


@dataclass()
class Transaction:
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    lcl_dttm: datetime.datetime = field(default_factory=datetime.datetime.now)
    entity_type: Optional[str] = None
    category: Optional[str] = None
    user_uuid: Optional[str] = None
    amount_lcy: Optional[float] = None
    currency_code: Optional[str] = None
    place: Optional[str] = None
    description: Optional[str] = None
    expected_transaction_id: Optional[str] = None

    @staticmethod
    def _parse_dttm_from_msg(msg: str) -> Tuple[Optional[datetime.datetime], int]:
        """
        Try to find a date at the beginning of the message using dateparser.
        Supports flexible formats like "25.03.2024", "2024-03-25", "yesterday",
        "25 Mar 2024", etc.
        Returns: (parsed_date, end_index) where end_index is the position after the detected date
        """
        if not msg:
            return None, 0

        # Strategy A: explicit anchored formats to avoid over-consuming tokens
        explicit_patterns = [
            (r'^(\d{4}-\d{2}-\d{2})', '%Y-%m-%d'),               # 2025-09-07
            (r'^(\d{1,2}\.\d{1,2}\.\d{4})', '%d.%m.%Y'),       # 8.09.2025 or 08.09.2025
        ]
        for pattern, fmt in explicit_patterns:
            m = re.match(pattern, msg)
            if m:
                date_str = m.group(1)
                try:
                    parsed = datetime.datetime.strptime(date_str, fmt)
                    return parsed, len(date_str)
                except ValueError:
                    pass

        # Strategy B: natural language single-token dates (e.g., "yesterday")
        tokens = msg.strip().split()
        if tokens:
            first_token = tokens[0].rstrip(',.;')
            parsed_single = dateparser.parse(first_token, settings={
                'PREFER_DATES_FROM': 'past',
                'RETURN_AS_TIMEZONE_AWARE': False,
            })
            if parsed_single and msg.lower().startswith(first_token.lower()):
                return parsed_single, len(first_token)

        # Heuristic 2: fallback to search_dates but require prefix match
        try:
            results = search_dates(msg, settings={
                'PREFER_DATES_FROM': 'past',
                'RETURN_AS_TIMEZONE_AWARE': False,
            })
        except Exception:
            results = None

        if results:
            for matched_text, parsed_dt in results:
                matched_text_stripped = matched_text.strip().rstrip(',.;')
                if msg.lower().startswith(matched_text_stripped.lower()):
                    return parsed_dt, len(matched_text_stripped)

        return None, 0

    @classmethod
    def from_message(cls, msg: str, default_currency: str = None) -> Optional["Transaction"]:
        """
        Parse transaction from message.
        Expected format: [date] amount [currency_code] category
        Examples:
          - "25.03.2024 100 USD Groceries"
          - "yesterday 250 taxi"
          - "100 USD Utilities: Electricity"
          - "100 food" (uses default currency if provided)
        Returns: Transaction instance or None if parsing fails
        """
        try:
            tx = cls()
            # Try to parse date at the beginning
            date, date_end = cls._parse_dttm_from_msg(msg)
            if date:
                tx.lcl_dttm = date
                # Remove the date part from the message
                msg = msg[date_end:].strip()
            
            # Split remaining message into parts
            parts = msg.strip().split()
            # Need at least amount and category (currency is optional)
            if len(parts) < 2:
                return None

            # Parse amount (should be the first part)
            amount_token = parts[0].replace(',', '.')
            tx.amount_lcy = float(amount_token)
            
            # Check if the second part is a currency code (3-letter alphabetic)
            if len(parts) >= 3 and len(parts[1]) == 3 and parts[1].isalpha():
                tx.currency_code = parts[1].upper()
                # Everything after currency is category (can be multi-word)
                tx.category = ' '.join(parts[2:]) if len(parts) > 2 else None
            else:
                # No currency code provided, use default
                tx.currency_code = default_currency
                # Everything after amount is category (can be multi-word)
                tx.category = ' '.join(parts[1:]) if len(parts) > 1 else None
            
            # Place and description are not part of the new format
            tx.place = None
            tx.description = None

            return tx
        except (ValueError, IndexError):
            return None

    def to_dict(self) -> dict:
        """Convert transaction to dictionary for database insertion"""
        return {
            'transaction_id': self.transaction_id,
            'lcl_dttm': self.lcl_dttm,
            'entity_type': self.entity_type,
            'category': self.category,
            'user_uuid': self.user_uuid,
            'amount_lcy': self.amount_lcy,
            'currency_code': self.currency_code,
            'place': self.place,
            'description': self.description,
            'expected_transaction_id': self.expected_transaction_id
        }
