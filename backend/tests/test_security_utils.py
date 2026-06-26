import os
import sys
import pytest
from datetime import timedelta

# Ensure project root is in the Python path
sys.path.append(os.getcwd())

from backend.utils.security import hash_password, verify_password, create_access_token, decode_access_token

def test_password_hashing_and_verification():
    """
    Test that passwords are correctly hashed and verified.
    """
    password = "MySecurePassword123!"
    hashed = hash_password(password)
    
    # Verify the hash starts with bcrypt pattern or is not empty
    assert hashed != password
    assert len(hashed) > 0
    
    # Correct password should verify
    assert verify_password(password, hashed) is True
    
    # Incorrect password should not verify
    assert verify_password("WrongPassword!", hashed) is False

def test_access_token_creation_and_decoding():
    """
    Test JWT creation, successful decoding, and expiration validation.
    """
    subject = "user@example.com"
    token = create_access_token(subject=subject, is_admin=False)
    
    assert token is not None
    assert len(token) > 0
    
    # Decoding a valid token should return the subject
    decoded_subject = decode_access_token(token)
    assert decoded_subject == subject

def test_expired_token_returns_none():
    """
    Test that an expired JWT token returns None when decoded.
    """
    subject = "expired@example.com"
    # Create a token that expired 5 minutes ago
    expires_delta = timedelta(minutes=-5)
    token = create_access_token(subject=subject, is_admin=False, expires_delta=expires_delta)
    
    decoded_subject = decode_access_token(token)
    assert decoded_subject is None

def test_invalid_token_returns_none():
    """
    Test that an invalid/malformed JWT token returns None when decoded.
    """
    assert decode_access_token("not.a.valid.jwt.token") is None
    assert decode_access_token("") is None
