import re

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError


password_hasher = PasswordHasher()


COMMON_PASSWORDS = {
    "password",
    "password123",
    "12345678",
    "123456789",
    "qwerty",
    "qwerty123",
    "1234567890",
    "admin",
    "admin123",
    "letmein",
    "welcome",
    "welcome123",
    "iloveyou",
    "monkey",
    "dragon",
    "football",
    "abc123",
    "password1",
    "passw0rd",
}


def validate_password_policy(password: str, email: str) -> None:
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")


    if len(password) > 12:
        raise ValueError("Password must not exceed 12 characters.")

    if not re.search(r"[A-Z]", password):
        raise ValueError(
            "Password must contain at least one uppercase letter."
        )
    if not re.search(r"[a-z]", password):
        raise ValueError(
            "Password must contain at least one lowercase letter."
        )


    if not re.search(r"\d", password):
        raise ValueError(
            "Password must contain at least one number."
        )
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError(
            "Password must contain at least one special character."
        )
    if password.casefold() == email.casefold():
        raise ValueError(
            "Password cannot be the same as your email."
        )
    if password.casefold() in {
        common.casefold() for common in COMMON_PASSWORDS
    }:
        raise ValueError(
            "This password is too common. Please choose a stronger password."
        )
