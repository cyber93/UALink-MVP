"""UALink 200 — Alignment Marker insertion and Flit alignment (Section 7.2.2)."""
from ..common.constants import AM_INTERVAL_FLITS, SerialRate


class AlignmentController:
    """
    Manages Alignment Marker (AM) insertion timing.
    TX: sends Start Flit Code Sequence every N flits.
    RX: receives AM Flit Code Sequence for Flit synchronization.
    Spec: Section 7.2.2.
    """
    def __init__(self, rate: SerialRate = SerialRate.G200):
        self.rate = rate
        self._flit_count = 0
        self._am_interval = AM_INTERVAL_FLITS[rate]
        self._locked = False

    def tick_tx(self) -> bool:
        """Returns True if this flit should be a Start Flit Code Sequence."""
        result = (self._flit_count % self._am_interval == 0)
        self._flit_count += 1
        return result

    def on_rx_am(self):
        """Called when RS receives AM Flit Code Sequence from PCS."""
        self._locked = True

    def is_aligned(self) -> bool:
        return self._locked

    def set_rate(self, rate: SerialRate):
        self.rate = rate
        self._am_interval = AM_INTERVAL_FLITS[rate]
        self._flit_count = 0
        self._locked = False
