"""Fernet-based symmetric encryption for wallet private keys."""

from __future__ import annotations

import logging

from cryptography.fernet import Fernet

from bot.config import settings

logger = logging.getLogger(__name__)


def _get_fernet() -> Fernet:
    """Build a Fernet instance from the configured key.

    If the key in settings is the placeholder value, generate a real key,
    log a warning, and use the generated key for this session.
    """
    key = settings.wallet_encryption_key
    placeholder = "GENERATE_ME"

    if key == placeholder or not key:
        generated = Fernet.generate_key().decode()
        logger.warning(
            "WALLET_ENCRYPTION_KEY is not set. A temporary key has been "
            "generated for this session: %s  -- Put this in your .env file "
            "to persist wallet data across restarts.",
            generated,
        )
        return Fernet(generated.encode())

    return Fernet(key.encode())


# Build a Fernet instance once at import time.
_fernet = _get_fernet()


def encrypt(plaintext: str) -> str:
    """Encrypt a plaintext string and return the ciphertext as a UTF-8 string."""
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a ciphertext string and return the original plaintext."""
    return _fernet.decrypt(ciphertext.encode()).decode()


def generate_key() -> str:
    """Generate a new Fernet key and return it as a string.

    Useful as a CLI helper:
        python -c "from bot.utils.encryption import generate_key; print(generate_key())"
    """
    return Fernet.generate_key().decode()
