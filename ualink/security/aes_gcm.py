"""UALink 200 — AES-GCM-256 encryption/decryption (Section 9.5)."""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SEC_KEY_BYTES = 32
SEC_TAG_BYTES = 8
SEC_IV_BYTES  = 12


def encrypt(key: bytes, iv: bytes, plaintext: bytes,
            aad: bytes = b'') -> tuple:
    """AES-GCM-256 encrypt. Returns (ciphertext, tag)."""
    assert len(key) == SEC_KEY_BYTES, "Key must be 256-bit"
    assert len(iv)  == SEC_IV_BYTES,  "IV must be 96-bit"
    aesgcm = AESGCM(key)
    ct_with_tag = aesgcm.encrypt(iv, plaintext, aad)
    ciphertext = ct_with_tag[:-16]
    full_tag   = ct_with_tag[-16:]
    tag = full_tag[:SEC_TAG_BYTES]  # 8-byte truncated tag
    return ciphertext, tag


def decrypt(key: bytes, iv: bytes, ciphertext: bytes,
            tag: bytes, aad: bytes = b'') -> tuple:
    """AES-GCM-256 decrypt. Returns (plaintext, auth_ok)."""
    assert len(key) == SEC_KEY_BYTES
    assert len(iv)  == SEC_IV_BYTES
    aesgcm = AESGCM(key)
    padded_tag = tag + bytes(16 - len(tag))
    try:
        plaintext = aesgcm.decrypt(iv, ciphertext + padded_tag, aad)
        return plaintext, True
    except Exception:
        return b'\x00' * len(ciphertext), False


def build_iv(iv_fixed: bytes, invocation: int) -> bytes:
    """Build 96-bit IV: 64-bit fixed || 32-bit invocation counter."""
    assert len(iv_fixed) == 8, "Fixed IV part must be 8 bytes (64 bits)"
    return iv_fixed + invocation.to_bytes(4, 'little')
