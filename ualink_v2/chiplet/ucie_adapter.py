"""
UALink Chiplet Specification v1.01 (UCIe 3.0 Integration)
Implements Die-to-Die (D2D) low-latency streaming adapter
bridging UALink 2.0 TL flits directly across UCIe 3.0 PHY interfaces.
"""
from typing import Callable, Optional
from ..common_v2.constants import TransportType
from ..common_v2.transport_interface import ITransportLayer

CHIPLET_FLIT_BYTES = 64  # Direct 64B Flit pass-through over UCIe streaming

class UCIeChipletAdapter(ITransportLayer):
    """
    UCIe 3.0 Die-to-Die (D2D) Transport Adapter for In-Package Multi-Die Accelerators.
    Offers ultra-low latency direct Flit transfer without bulky SerDes framing.
    """
    def __init__(self, die_id: int = 0):
        self.die_id = die_id
        self.peer_die: Optional['UCIeChipletAdapter'] = None
        self._rx_callback: Optional[Callable[[bytes], None]] = None
        self.d2d_ready: bool = False

    @property
    def transport_type(self) -> TransportType:
        return TransportType.CHIPLET_UCIE

    def connect_endpoint(self, peer_transport: ITransportLayer):
        assert isinstance(peer_transport, UCIeChipletAdapter), "Peer must be UCIe Chiplet adapter"
        self.peer_die = peer_transport
        peer_transport.peer_die = self
        self.d2d_ready = True
        peer_transport.d2d_ready = True

    def set_receive_callback(self, callback: Callable[[bytes], None]):
        self._rx_callback = callback

    def is_link_up(self) -> bool:
        return self.d2d_ready and (self.peer_die is not None)

    def send_flit(self, flit_bytes: bytes) -> bool:
        if not self.is_link_up() or self.peer_die is None:
            return False

        # In UCIe 3.0 D2D, 64B TL Flits stream directly across the physical lanes
        payload = flit_bytes[:CHIPLET_FLIT_BYTES].ljust(CHIPLET_FLIT_BYTES, b'\x00')
        self.peer_die._receive_d2d(payload)
        return True

    def _receive_d2d(self, flit_bytes: bytes):
        if self._rx_callback:
            self._rx_callback(flit_bytes)
