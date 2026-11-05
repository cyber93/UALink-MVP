"""
UALink 2.0 Common Specification — Transaction Layer 2.0 (TL 2.0)
Constructs 64B TL Flits and interfaces with Pluggable Transport implementations.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Callable
from .types import UPLIRequest, UPLIResponse
from .constants import ReqCmd, TransportType
from .transport_interface import ITransportLayer

TL_FLIT_BYTES = 64
TL_HALF_FLIT_BYTES = 32

@dataclass
class TL2Flit:
    """64-byte TL 2.0 Flit consisting of 32B Control Half-Flit and 32B Data Half-Flit."""
    control_half: bytes = field(default_factory=lambda: bytes(32))
    data_half: bytes    = field(default_factory=lambda: bytes(32))

    def serialize(self) -> bytes:
        data = self.control_half.ljust(32, b'\x00')[:32] + self.data_half.ljust(32, b'\x00')[:32]
        assert len(data) == TL_FLIT_BYTES
        return data

    @classmethod
    def deserialize(cls, raw: bytes) -> 'TL2Flit':
        assert len(raw) == TL_FLIT_BYTES
        return cls(control_half=raw[:32], data_half=raw[32:])


class TransactionLayer2:
    """TL 2.0 Engine interfacing UPLI requests with the underlying Transport."""

    def __init__(self, transport: Optional[ITransportLayer] = None):
        self.transport = transport
        if self.transport:
            self.transport.set_receive_callback(self._on_transport_flit)
        self._rx_callback: Optional[Callable[[TL2Flit], None]] = None

    def set_transport(self, transport: ITransportLayer):
        self.transport = transport
        self.transport.set_receive_callback(self._on_transport_flit)

    def set_receive_callback(self, cb: Callable[[TL2Flit], None]):
        self._rx_callback = cb

    def pack_request(self, req: UPLIRequest) -> TL2Flit:
        """Packs a UPLI 2.0 request into a 64B TL 2.0 Flit."""
        ctrl = bytearray(32)
        # Header bytes: [src_id: 10b, dst_id: 10b, cmd: 6b, tag: 11b, ...]
        ctrl[0] = req.src_id & 0xFF
        ctrl[1] = ((req.src_id >> 8) & 0x03) | ((req.dst_id & 0x3F) << 2)
        ctrl[2] = ((req.dst_id >> 6) & 0x0F) | ((req.cmd & 0x0F) << 4)
        ctrl[3] = (req.cmd >> 4) & 0x03
        ctrl[4] = req.tag & 0xFF
        ctrl[5] = (req.tag >> 8) & 0x07

        # Address in bytes 8-15
        ctrl[8:16] = req.addr.to_bytes(8, byteorder='little')

        # If INC operation present, encode opcode & dtype in metadata bytes
        if req.inc_op:
            ctrl[16] = req.inc_op.opcode
            ctrl[17] = req.inc_op.dtype
            ctrl[18:20] = req.inc_op.collective_id.to_bytes(2, 'little')

        data = req.data[:32].ljust(32, b'\x00')
        return TL2Flit(control_half=bytes(ctrl), data_half=data)

    def send_request(self, req: UPLIRequest) -> bool:
        assert self.transport is not None, "Transport layer not attached"
        flit = self.pack_request(req)
        return self.transport.send_flit(flit.serialize())

    def _on_transport_flit(self, raw_bytes: bytes):
        flit = TL2Flit.deserialize(raw_bytes[:TL_FLIT_BYTES])
        if self._rx_callback:
            self._rx_callback(flit)
