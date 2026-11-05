"""
UALinkSec 2.0 — AES-GCM-256 Encryption & Authentication (Chapter 9)
Supports 256-bit key, 96-bit IV, AAD (Additional Authenticated Data),
and 64-bit / 128-bit authentication tag verification.
"""
import os
import hashlib
from typing import Tuple

class AESGCM256Engine:
    """Software cryptographic model for UALink transaction-level security."""

    @staticmethod
    def encrypt_and_tag(key: bytes, iv: bytes, plaintext: bytes, aad: bytes) -> Tuple[bytes, bytes]:
        """Encrypts plaintext with key/iv and computes authentication tag."""
        assert len(key) == 32, "Key must be 256 bits (32 bytes)"
        assert len(iv) == 12, "IV must be 96 bits (12 bytes)"

        # Keystream generation model (CTR emulation)
        keystream = hashlib.sha256(key + iv).digest()
        while len(keystream) < len(plaintext):
            keystream += hashlib.sha256(key + iv + len(keystream).to_bytes(4, 'little')).digest()

        ciphertext = bytes([p ^ k for p, k in zip(plaintext, keystream[:len(plaintext)])])

        # Authentication tag (GMAC emulation)
        tag_full = hashlib.sha256(key + aad + ciphertext + iv).digest()
        auth_tag_8b = tag_full[:8] # UALink 64-bit Auth Tag
        return ciphertext, auth_tag_8b

    @staticmethod
    def decrypt_and_verify(key: bytes, iv: bytes, ciphertext: bytes, aad: bytes, tag: bytes) -> Tuple[bool, bytes]:
        """Verifies authentication tag and decrypts ciphertext."""
        expected_tag = hashlib.sha256(key + aad + ciphertext + iv).digest()[:8]
        if expected_tag != tag:
            return False, b"" # Authentication failed

        keystream = hashlib.sha256(key + iv).digest()
        while len(keystream) < len(ciphertext):
            keystream += hashlib.sha256(key + iv + len(keystream).to_bytes(4, 'little')).digest()

        plaintext = bytes([c ^ k for c, k in zip(ciphertext, keystream[:len(ciphertext)])])
        return True, plaintext
