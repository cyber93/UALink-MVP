"""
UALink 2.0 Accelerator Model (Chapter 1)
"""
from typing import Dict, List, Optional
from ..upli.interface import UPLIInterface2
from ..constants import OrderingMode

class AcceleratorPort:
    def __init__(self, port_id: int):
        self.port_id = port_id
        self.upli = UPLIInterface2(port_id=port_id)
        self.peer_acc_id: Optional[int] = None
        self.peer_port_id: Optional[int] = None

    def connect(self, peer_acc_id: int, peer_port_id: int = 0):
        self.peer_acc_id = peer_acc_id
        self.peer_port_id = peer_port_id
        self.upli.connect()


class AcceleratorNode:
    """Represents a physical UALink 2.0 Accelerator node with local memory and ports."""
    def __init__(self, acc_id: int, ports_count: int = 4, memory_size_bytes: int = 1024 * 1024):
        self.acc_id = acc_id
        self.ports: Dict[int, AcceleratorPort] = {i: AcceleratorPort(i) for i in range(ports_count)}
        self.memory: bytearray = bytearray(memory_size_bytes)

    def read_local(self, addr: int, size: int = 64) -> bytes:
        offset = addr % len(self.memory)
        return bytes(self.memory[offset:offset+size])

    def write_local(self, addr: int, data: bytes):
        offset = addr % len(self.memory)
        self.memory[offset:offset+len(data)] = data
