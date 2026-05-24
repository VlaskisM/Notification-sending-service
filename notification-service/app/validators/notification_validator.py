from abc import ABC, abstractmethod

from app.schemas import NotificationCreate


class NotificationValidationError(Exception):
    pass


async def validate(data: NotificationCreate) -> None:
    ALLOWED_TYPES = {"email", "sms", "telegram"}

    if data.type not in ALLOWED_TYPES:
        raise NotificationValidationError(
            f"unknown type {data.type}, expected one of {sorted(ALLOWED_TYPES)}"
        )
    if not data.recipient.strip():
        raise NotificationValidationError("recipient is required")
    if not data.message.strip():
        raise NotificationValidationError("message is required")
    if data.type == "email" and "@" not in data.recipient:
        raise NotificationValidationError("email recipient must contain '@'")
    if data.type == "telegram" and not data.recipient[0] == "@":
        raise NotificationValidationError("telegram recipient must start with '@'")
    if data.type == "sms" and not data.recipient[0] == "+":
        raise NotificationValidationError("sms recipient must start with '+'")

