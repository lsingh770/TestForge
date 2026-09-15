from __future__ import annotations

import uuid
from datetime import datetime, timedelta


class TestData:
    @staticmethod
    def user() -> dict:
        unique = uuid.uuid4().hex[:8]
        return {
            "name": f"Test User {unique}",
            "email": f"testuser_{unique}@example.com",
            "age": 28,
        }

    @staticmethod
    def order() -> dict:
        return {
            "user_id": 1,
            "total": 99.99,
            "currency": "USD",
        }

    @staticmethod
    def timestamp(days_from_now: int = 0) -> str:
        return (datetime.utcnow() + timedelta(days=days_from_now)).strftime("%Y-%m-%dT%H:%M:%SZ")
