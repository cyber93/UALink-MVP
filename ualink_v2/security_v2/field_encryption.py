"""
UALinkSec 2.0 — Partial Field Encryption (Tables 9-8 through 9-24)
Routing fields (SrcAccID, DstAccID) are kept plaintext as AAD so stateless switches can route.
Address bits [17:2], Tag, and Data payloads are encrypted.
"""
from typing import Tuple
from .aes_gcm import AESGCM256Engine

class PartialFieldEncryptor:
    """Separates TL Flit into Plaintext AAD and Encrypted Payload."""

    @staticmethod
    def protect_flit(key: bytes, iv: bytes, flit_bytes: bytes) -> Tuple[bytes, bytes]:
        assert len(flit_bytes) == 64
        # Control half: Bytes 0-7 contain routing fields (AAD)
        aad = flit_bytes[:8]
        # Confidential payload: Bytes 8-63 (Address, Data, Metadata)
        confidential = flit_bytes[8:]

        ciphertext, tag = AESGCM256Engine.encrypt_and_tag(key, iv, confidential, aad)
        protected_flit = aad + ciphertext
        return protected_flit, tag

    @staticmethod
    def unprotect_flit(key: bytes, iv: bytes, protected_flit: bytes, tag: bytes) -> Tuple[bool, bytes]:
        assert len(protected_flit) == 64
        aad = protected_flit[:8]
        ciphertext = protected_flit[8:]

        ok, plaintext = AESGCM256Engine.decrypt_and_verify(key, iv, ciphertext, aad, tag)
        if not ok:
            return False, b""
        return True, (aad + plaintext)
