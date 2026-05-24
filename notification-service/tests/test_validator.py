import pytest

from app.schemas import NotificationCreate
from app.validators.notification_validator import (
    NotificationValidationError,
    validate,
)


@pytest.fixture
def valid_sms():
    return NotificationCreate(
        type="sms",
        recipient="+1234567890",
        message="Hello, this is a test SMS notification.",
    )


@pytest.fixture
def valid_email():
    return NotificationCreate(
        type="email",
        recipient="test@example.com",
        message="Hello, this is a test email notification.",
    )


@pytest.fixture
def valid_telegram():
    return NotificationCreate(
        type="telegram",
        recipient="@max_test",
        message="Hello from Telegram",
    )


@pytest.fixture
def invalid_type():
    return NotificationCreate(
        type="pigeon",
        recipient="anyone",
        message="Hello",
    )


@pytest.fixture
def invalid_sms_no_plus():
    return NotificationCreate(
        type="sms",
        recipient="1234567890",
        message="Hello",
    )


@pytest.fixture
def invalid_email_no_at():
    return NotificationCreate(
        type="email",
        recipient="not-an-email",
        message="Hello",
    )


@pytest.fixture
def invalid_telegram_no_at():
    return NotificationCreate(
        type="telegram",
        recipient="max_test",
        message="Hello",
    )


async def test_valid_sms(valid_sms):
    await validate(valid_sms)

async def test_valid_email(valid_email):
    await validate(valid_email)

async def test_valid_telegram(valid_telegram):
    await validate(valid_telegram)

async def test_invalid_type(invalid_type):
    try:
        await validate(invalid_type)
    except NotificationValidationError as e:
        assert "unknown type" in str(e)

async def test_invalid_sms_no_plus(invalid_sms_no_plus):
    try:
        await validate(invalid_sms_no_plus)
    except NotificationValidationError as e:
        assert "sms recipient must start with '+'" in str(e)

async def test_invalid_email_no_at(invalid_email_no_at):
    try:
        await validate(invalid_email_no_at)
    except NotificationValidationError as e:
        assert "email recipient must contain '@'" in str(e)

async def test_invalid_telegram_no_at(invalid_telegram_no_at):
    try:
        await validate(invalid_telegram_no_at)
    except NotificationValidationError as e:
        assert "telegram recipient must start with '@'" in str(e)


