"""UALink 200 — Accelerator and Port model (Section 1.2)."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from ..common.constants import LinkWidth, MAX_PORTS_PER_STATION
from ..upli.interface import UPLIInterface
from .address_translation import AddressTranslator
from ..common.logger import log


@dataclass
class UALinkPort:
    port_index: int
    width: LinkWidth = LinkWidth.X1
    upli: Optional[UPLIInterface] = None
    connected_to: Optional[int] = None  # peer acc_id or switch port
    auth_tag: int = 0  # Expected AuthTag for incoming requests

    def __post_init__(self):
        self.upli = UPLIInterface(port_id=self.port_index)


class Accelerator:
    """
    UALink Accelerator with N ports.
    Spec: Section 1.2 (Accelerator System Node).
    """
    def __init__(self, acc_id: int, num_ports: int = 1,
                 width: LinkWidth = LinkWidth.X1):
        assert 0 <= acc_id < 1024
        assert 1 <= num_ports <= MAX_PORTS_PER_STATION
        self.acc_id = acc_id
        self.num_ports = num_ports
        self.memory: Dict[int, bytes] = {}  # addr → data (64B pages)
        self.ports: List[UALinkPort] = [
            UALinkPort(i, width) for i in range(num_ports)
        ]
        self.addr_translator = AddressTranslator()
        self.virtual_pod_id: Optional[int] = None
        self._pending_tags: Dict[int, dict] = {}
        self._tag_counter = 0

    def alloc_tag(self) -> int:
        tag = self._tag_counter % 2048
        self._tag_counter += 1
        return tag

    def write_local(self, addr: int, data: bytes):
        page = addr & ~0x3F
        self.memory[page] = data[:64]
        log.debug(f"Acc={self.acc_id} write_local addr={hex(addr)} size={len(data)}")

    def read_local(self, addr: int) -> bytes:
        page = addr & ~0x3F
        log.debug(f"Acc={self.acc_id} read_local addr={hex(addr)}")
        return self.memory.get(page, bytes(64))

    def get_port(self, idx: int) -> UALinkPort:
        return self.ports[idx]

    def connect_port(self, port_idx: int, peer_id: int):
        self.ports[port_idx].connected_to = peer_id
        self.ports[port_idx].upli.connect()
        log.info(f"Acc={self.acc_id} port={port_idx} connected to Peer={peer_id}")

    def process_request(self, port_idx: int, req) -> bool:
        port = self.ports[port_idx]
        if req.auth_tag != port.auth_tag:
            log.warning(f"Acc={self.acc_id} Port={port_idx} AuthTag mismatch: expected {port.auth_tag}, got {req.auth_tag}")
            return False
        return True

    def __repr__(self):
        return f"Accelerator(id={self.acc_id}, ports={self.num_ports})"
