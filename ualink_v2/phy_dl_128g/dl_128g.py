"""
UALink 128G Data Link & Physical Layer (DL & PL Spec 1.0)
Implements 128G optimized SerDes framing, rate adaptation,
and transport integration for PCIe-compatible electrical PHYs.
"""
import zlib
from typing import Callable, Optional
from ..common_v2.constants import TransportType
from ..common_v2.transport_interface import ITransportLayer

DL_FLIT_BYTES_128G = 256  # 128G optimized flit size
CRC_BYTES = 4
HEADER_BYTES = 2

class DL128GTransport(ITransportLayer):
    """
    128G Physical & Data Link Layer transport instance.
    Optimized for 128G SerDes lane rates and low-power packaging.
    """
    def __init__(self, port_id: int = 0):
        self.port_id = port_id
        self.peer: Optional['DL128GTransport'] = None
        self._rx_callback: Optional[Callable[[bytes], None]] = None
        self.seq_num: int = 1
        self.link_up: bool = False

    @property
    def transport_type(self) -> TransportType:
        return TransportType.LINK_128G

    def connect_endpoint(self, peer_transport: ITransportLayer):
        assert isinstance(peer_transport, DL128GTransport), "Peer must be 128G transport"
        self.peer = peer_transport
        peer_transport.peer = self
        self.link_up = True
        peer_transport.link_up = True

    def set_receive_callback(self, callback: Callable[[bytes], None]):
        self._rx_callback = callback

    def is_link_up(self) -> bool:
        return self.link_up and (self.peer is not None)

    def frame_flit(self, payload: bytes) -> bytes:
        header = self.seq_num.to_bytes(HEADER_BYTES, byteorder='little')
        usable_payload_len = DL_FLIT_BYTES_128G - HEADER_BYTES - CRC_BYTES
        flit_body = header + payload.ljust(usable_payload_len, b'\x00')[:usable_payload_len]

        crc = zlib.crc32(flit_body) & 0xFFFFFFFF
        flit = flit_body + crc.to_bytes(CRC_BYTES, byteorder='little')
        assert len(flit) == DL_FLIT_BYTES_128G
        return flit

    def verify_and_unframe(self, flit_bytes: bytes) -> Optional[bytes]:
        if len(flit_bytes) != DL_FLIT_BYTES_128G:
            return None
        body = flit_bytes[:-4]
        expected_crc = int.from_bytes(flit_bytes[-4:], byteorder='little')
        calc_crc = zlib.crc32(body) & 0xFFFFFFFF
        if expected_crc != calc_crc:
            return None
        return body[HEADER_BYTES:]

    def send_flit(self, payload_bytes: bytes) -> bool:
        if not self.is_link_up() or self.peer is None:
            return False

        flit = self.frame_flit(payload_bytes)
        self.seq_num = (self.seq_num % 255) + 1
        self.peer._receive_raw(flit)
        return True

    def _receive_raw(self, flit_bytes: bytes):
        payload = self.verify_and_unframe(flit_bytes)
        if payload is not None and self._rx_callback:
            self._rx_callback(payload)
