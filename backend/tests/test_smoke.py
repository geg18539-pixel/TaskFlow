from jose import jwt

from auth import create_access_token, get_password_hash, verify_password
from database import settings
from models import TaskStatus, Priority


def test_password_hash_roundtrip():
    hashed = get_password_hash("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_contains_subject():
    token = create_access_token(42)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "42"
    assert "exp" in payload


def test_enum_values():
    assert TaskStatus.todo.value == "todo"
    assert Priority.medium.value == "medium"
