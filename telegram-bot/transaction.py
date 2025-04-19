import uuid
import datetime
import re
from typing import Optional, Tuple

class Transaction:
    def __init__(self):
        self.transaction_id = str(uuid.uuid4())
        self.lcl_dttm = datetime.datetime.now()
        self.entity_type = None
        self.category = None
        self.user_uuid = None
        self.amount_lcy = None
        self.currency_code = None
        self.place = None
        self.description = None
        self.expected_transaction_id = None

    def _parse_dttm_from_msg(self, msg: str) -> Tuple[Optional[datetime.datetime], int]:
        """
        Try to find date in format DD.MM.YYYY or YYYY-MM-DD at the beginning of the message
        Returns: (parsed_date, end_index) where end_index is the position after the date
        """
        date_patterns = [
            r'^(\d{2}\.\d{2}\.\d{4})',  # DD.MM.YYYY
            r'^(\d{4}-\d{2}-\d{2})'      # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            match = re.match(pattern, msg)
            if match:
                date_str = match.group(1)
                try:
                    if '.' in date_str:
                        parsed_date = datetime.datetime.strptime(date_str, '%d.%m.%Y')
                    else:
                        parsed_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    return parsed_date, len(date_str)
                except ValueError:
                    continue
        return None, 0

    def parse_from_message(self, msg: str, default_currency: str = None) -> bool:
        """
        Parse transaction from message.
        Expected format: [date] amount [currency_code] place
        Example: 25.03.2024 100 USD Starbucks
        Example: 100 Starbucks (using default currency)
        """
        try:
            # Try to parse date at the beginning
            date, date_end = self._parse_dttm_from_msg(msg)
            if date:
                self.lcl_dttm = date
                # Remove the date part from the message
                msg = msg[date_end:].strip()
            
            # Split remaining message into parts
            parts = msg.strip().split()
            if len(parts) < 2:  # Need at least amount and place
                return False

            # Parse amount (should be the first part)
            self.amount_lcy = float(parts[0])
            
            # Check if the second part is a currency code (3 letter code)
            if len(parts) > 2 and len(parts[1]) == 3 and parts[1].isalpha():
                self.currency_code = parts[1].upper()
                self.place = parts[2]
            else:
                # No currency code provided, use default
                self.currency_code = default_currency
                self.place = parts[1]
            
            # If there are more parts after place, treat them as description
            if len(parts) > (3 if self.currency_code != default_currency else 2):
                desc_start = 3 if self.currency_code != default_currency else 2
                self.description = ' '.join(parts[desc_start:])

            return True
        except (ValueError, IndexError):
            return False

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

if __name__ == '__main__':
    x = Transaction()
    print(x.transaction_id)

    y = Transaction()
    print(y.transaction_id)