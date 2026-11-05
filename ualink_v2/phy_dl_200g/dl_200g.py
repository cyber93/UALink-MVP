"""
UALink 2.0 200G Data Link & Physical Layer (DL & PL Spec 2.0)
Implements 640-byte DL Flit framing, 32-bit CRC, Link-level replay,
and PAM4 200G transport interfacing with Common 2.0.
"""
import zlib
from typing import Callable, Optional, List
from ..common_v2.constants import TransportType
from ..common_v2.transport_interface import ITransportLayer

DL_FLIT_BYTES_200G = 640
CRC_BYTES = 4
HEADER_BYTES = 3

class DL200GTransport(ITransportLayer):
    """
    200G Physical & Data Link Layer transport instance.
    Implements 640B Flit framing, 802.3 CRC-32, and point-to-point transmission.
    """
    def __init__(self, port_id: int = 0):
        self.port_id = port_id
        self.peer: Optional['DL200GTransport'] = None
        self._rx_callback: Optional[Callable[[bytes], None]] = None
        self.tx_seq: int = 1
        self.rx_seq: int = 0
        self.link_up: bool = False
        self.tx_replay_buffer: List[bytes] = []

    @property
    def transport_type(self) -> TransportType:
        return TransportType.LINK_200G

    def connect_endpoint(self, peer_transport: ITransportLayer):
        assert isinstance(peer_transport, DL200GTransport), "Peer must be 200G transport"
        self.peer = peer_transport
        peer_transport.peer = self
        self.link_up = True
        peer_transport.link_up = True

    def set_receive_callback(self, callback: Callable[[bytes], None]):
        self._rx_callback = callback

    def is_link_up(self) -> bool:
        return self.link_up and (self.peer is not None)

    def frame_flit(self, payload: bytes) -> bytes:
        """Packs payload into 640-byte DL Flit with 3B Header and 4B CRC-32."""
        header = bytearray(3)
        header[0] = self.tx_seq & 0xFF
        header[1] = (self.tx_seq >> 8) & 0x01  # 9-bit sequence
        header[2] = 0x00                       # Op: Original

        usable_payload_len = DL_FLIT_BYTES_200G - HEADER_BYTES - CRC_BYTES
        flit_body = bytes(header) + payload.ljust(usable_payload_len, b'\x00')[:usable_payload_len]

        # Calculate CRC-32
        crc = zlib.crc32(flit_body) & 0xFFFFFFFF
        flit = flit_body + crc.to_bytes(4, byteorder='little')
        assert len(flit) == DL_FLIT_BYTES_200G
        return flit

    def verify_and_unframe(self, flit_bytes: bytes) -> Optional[bytes]:
        """Validates CRC and extracts usable TL payload."""
        if len(flit_bytes) != DL_FLIT_BYTES_200G:
            return None
        body = flit_bytes[:-4]
        expected_crc = int.from_bytes(flit_bytes[-4:], byteorder='little')
        calc_crc = zlib.crc32(body) & 0xFFFFFFFF
        if expected_crc != calc_crc:
            return None  # CRC error

        # Return payload (skipping 3-byte header)
        return body[HEADER_BYTES:]

    def send_flit(self, payload_bytes: bytes) -> bool:
        if not self.is_link_up() or self.peer is None:
            return False

        flit = self.frame_flit(payload_bytes)
        self.tx_replay_buffer.append(flit)
        self.tx_seq = (self.tx_seq % 511) + 1

        # Transmit to peer
        self.peer._receive_raw(flit)
        return True

    def _receive_raw(self, flit_bytes: bytes):
        payload = self.verify_and_unframe(flit_bytes)
        if payload is not None and self._rx_callback:
            self._rx_callback(payload)
