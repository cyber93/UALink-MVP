"""
UALink 2.0 Common Specification — UPLI Commands and Encodings
Source: UALink Common Specification Rev 2.0 (Chapter 2 & Chapter 6)
"""
from ..constants import ReqCmd

def is_write_class(cmd: int) -> bool:
    """Uses OrigData channel if bit 5 is 1."""
    return bool(cmd & 0x20)

def is_read_class(cmd: int) -> bool:
    """Read class: ReqCmd[5:4] == 00."""
    return (cmd & 0x30) == 0x00

def is_atomic_class(cmd: int) -> bool:
    """Atomic class: ReqCmd[5:4] == 11."""
    return (cmd & 0x30) == 0x30

def is_inc_collective(cmd: int) -> bool:
    """In-Network Compute collective primitive check (Ch 6.2)."""
    return cmd in (
        ReqCmd.READ_REDUCE,
        ReqCmd.WRITE_MULTICAST,
        ReqCmd.WRITE_FULL_MULTICAST,
        ReqCmd.ATOMIC_NR_MULTICAST
    )

def is_vdc(cmd: int) -> bool:
    """Vendor Defined Command."""
    return (
        (0x08 <= cmd <= 0x0F) or
        (0x2C <= cmd <= 0x2F) or
        (0x3C <= cmd <= 0x3F)
    )
