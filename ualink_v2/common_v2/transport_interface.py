"""
UALink 2.0 — Pluggable Transport Layer Interface
Abstracts the lower Physical and Data Link layers (200G, 128G, Chiplet UCIe)
from the upper Common Protocol Layer (UPLI 2.0 and Transaction Layer).
"""
from abc import ABC, abstractmethod
from typing import Callable, Optional
from .constants import TransportType

class ITransportLayer(ABC):
    """Abstract interface that any UALink 2.0 DL/PHY transport must implement."""

    @property
    @abstractmethod
    def transport_type(self) -> TransportType:
        """Returns the specific physical transport type (200G, 128G, Chiplet)."""
        pass

    @abstractmethod
    def connect_endpoint(self, peer_transport: 'ITransportLayer') -> None:
        """Point-to-point connection with a peer transport instance."""
        pass

    @abstractmethod
    def send_flit(self, flit_bytes: bytes) -> bool:
        """Transmit raw serialized flit through physical/link media."""
        pass

    @abstractmethod
    def set_receive_callback(self, callback: Callable[[bytes], None]) -> None:
        """Register handler for incoming flits from the transport."""
        pass

    @abstractmethod
    def is_link_up(self) -> bool:
        """Check if link training and framing is in UP state."""
        pass
