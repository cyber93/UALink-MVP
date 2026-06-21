"""UALink 200 — Key Derivation Function (Section 9.5.15)."""
import hmac
import hashlib
from ..common.constants import SecurityStream, SEC_KEY_BYTES


def derive_key(master_key: bytes, context: bytes) -> bytes:
    """
    NIST SP 800-56C KDF (HKDF-SHA256).
    Input: master_key (256-bit), context (stream-specific).
    Output: 256-bit derived key.
    Spec: Section 9.5.15.
    """
    assert len(master_key) == SEC_KEY_BYTES
    prk = hmac.new(b'\x00' * 32, master_key, hashlib.sha256).digest()
    okm = hmac.new(prk, context + b'\x01', hashlib.sha256).digest()
    return okm[:SEC_KEY_BYTES]


def make_context(src_acc_id: int, dst_acc_id: int,
                 stream: SecurityStream, epoch: int) -> bytes:
    """
    Context for KDF: (src_acc_id || dst_acc_id || stream_id || epoch).
    Spec: Section 9.5.9.4.
    """
    return (src_acc_id.to_bytes(2, 'little') +
            dst_acc_id.to_bytes(2, 'little') +
            bytes([int(stream)]) +
            epoch.to_bytes(8, 'little'))
