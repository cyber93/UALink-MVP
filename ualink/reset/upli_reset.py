"""UALink 200 — UPLI Reset and Connection Handshake (Section 4, Fig 4-1 to 4-4)."""
from enum import IntEnum, auto


class ResetState(IntEnum):
    RESET      = auto()
    CONNECTING = auto()
    CONNECTED  = auto()


class UPLIReset:
    """
    UPLI reset and connection handshake.
    Rules: Fig 4-2/4-3/4-4 — Originator first, Completer first, concurrent.
    """
    def __init__(self, role: str = 'originator'):
        assert role in ('originator', 'completer')
        self.role  = role
        self.state = ResetState.RESET
        self._peer_ready  = False
        self._self_ready  = False

    def assert_reset(self):
        self.state       = ResetState.RESET
        self._peer_ready = False
        self._self_ready = False

    def deassert_reset(self):
        self._self_ready = True
        self.state = ResetState.CONNECTING
        self._try_connect()

    def peer_connected(self):
        self._peer_ready = True
        self._try_connect()

    def _try_connect(self):
        if self._self_ready and self._peer_ready:
            self.state = ResetState.CONNECTED

    def is_connected(self) -> bool:
        return self.state == ResetState.CONNECTED

    def is_reset(self) -> bool:
        return self.state == ResetState.RESET
