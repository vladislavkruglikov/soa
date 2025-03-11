import pytest
from datetime import timedelta
from jose import jwt

from user_service.auth import get_password_hash, verify_password, create_access_token
from user_service.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def test_password_hash_and_verify():
    password = "secret123"
    hashed = get_password_hash(password)
    assert isinstance(hashed, str)
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == "testuser"
