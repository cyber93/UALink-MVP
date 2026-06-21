"""UALink 200 — 64B/66B encoding (Section 7.2, Fig 7-2)."""
from ..common.constants import (
    BLOCK_TYPE_DATA, BLOCK_TYPE_CONTROL,
    CTRL_BLOCK_IDLE, CTRL_BLOCK_START, CTRL_BLOCK_FAULT
)


def encode_data_block(data: bytes) -> bytes:
    """64B/66B data block: sync header 01 + 64 bytes = 65 bytes."""
    assert len(data) == 64
    return bytes([BLOCK_TYPE_DATA]) + data  # simplified: 1B sync + 64B data

def encode_idle_block() -> bytes:
    return bytes([BLOCK_TYPE_CONTROL, CTRL_BLOCK_IDLE] + [0x00]*7)

def encode_start_block() -> bytes:
    return bytes([BLOCK_TYPE_CONTROL, CTRL_BLOCK_START] + [0x00]*7)

def encode_fault_block(is_remote: bool = False) -> bytes:
    return bytes([BLOCK_TYPE_CONTROL, CTRL_BLOCK_FAULT, int(is_remote)] + [0x00]*6)

def is_data_block(block: bytes) -> bool:
    return len(block) > 0 and block[0] == BLOCK_TYPE_DATA

def is_control_block(block: bytes) -> bool:
    return len(block) > 0 and block[0] == BLOCK_TYPE_CONTROL

def get_block_type(block: bytes) -> int:
    return block[1] if len(block) > 1 else 0
