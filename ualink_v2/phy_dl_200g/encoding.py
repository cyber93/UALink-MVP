"""
UALink 200G DL & PL Spec 2.0 — 64B/66B Physical Layer Encoding (Chapter 7)
"""
SYNC_DATA    = 0b01
SYNC_CONTROL = 0b10

CTRL_IDLE    = 0x1E
CTRL_START   = 0x78
CTRL_FAULT   = 0x4B

def encode_64b66b_data(payload_64b: bytes) -> bytes:
    """Prepends 2-bit Data sync header (01). Stored as 1B header + 64B payload."""
    assert len(payload_64b) == 64
    return bytes([SYNC_DATA]) + payload_64b

def encode_64b66b_control(ctrl_type: int, payload_56b: bytes = bytes(56)) -> bytes:
    """Prepends 2-bit Control sync header (10) followed by 8-bit block type code."""
    return bytes([SYNC_CONTROL, ctrl_type]) + payload_56b[:56].ljust(56, b'\x00')
