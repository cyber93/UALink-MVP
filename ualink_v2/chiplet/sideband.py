"""
UALink Chiplet Specification v1.01 — UCIe 3.0 Sideband Mailbox Protocol
Provides out-of-band register access, link training, and telemetry
across in-package die-to-die interfaces.
"""
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class SidebandMessage:
    msg_type: int     # 0=Config Read, 1=Config Write, 2=Training, 3=Status
    addr: int
    data: int = 0

class UCIeSidebandMailbox:
    """Simulates 800MHz UCIe 3.0 sideband mailbox for in-package die control."""
    def __init__(self, die_id: int = 0):
        self.die_id = die_id
        self.registers: Dict[int, int] = {
            0x00: 0x101,  # Chiplet spec rev 1.01
            0x04: 0x01,   # Link status: Trained & Ready
            0x08: 0x00,   # Error counter
        }
        self.peer_mailbox: Optional['UCIeSidebandMailbox'] = None

    def connect(self, peer: 'UCIeSidebandMailbox'):
        self.peer_mailbox = peer
        peer.peer_mailbox = self

    def send_config_write(self, addr: int, val: int) -> bool:
        if not self.peer_mailbox:
            return False
        self.peer_mailbox.registers[addr] = val
        return True

    def send_config_read(self, addr: int) -> Optional[int]:
        if not self.peer_mailbox:
            return None
        return self.peer_mailbox.registers.get(addr, 0)
