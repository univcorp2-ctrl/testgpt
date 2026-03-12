from __future__ import annotations

import base64
from pathlib import Path

from cryptography.fernet import Fernet


def get_fernet(key: str) -> Fernet:
    raw = key.encode()
    if len(raw) != 44:
        padded = base64.urlsafe_b64encode(raw.ljust(32, b"0")[:32])
        return Fernet(padded)
    return Fernet(raw)


def encrypt_to_file(path: Path, payload: bytes, key: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fernet = get_fernet(key)
    path.write_bytes(fernet.encrypt(payload))


def decrypt_from_file(path: Path, key: str) -> bytes:
    fernet = get_fernet(key)
    return fernet.decrypt(path.read_bytes())
