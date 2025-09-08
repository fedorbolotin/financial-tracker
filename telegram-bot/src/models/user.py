from dataclasses import dataclass
from typing import Optional


@dataclass()
class User:
    user_uuid: str
    telegram_account: str
    default_currency_code: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'user_uuid': self.user_uuid,
            'telegram_account': self.telegram_account,
            'default_currency_code': self.default_currency_code,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
        }

    @classmethod
    def from_signup(cls, user_uuid: str, username: str, currency_code: Optional[str]) -> "User":
        return cls(
            user_uuid=user_uuid,
            telegram_account=username,
            default_currency_code=currency_code
        )