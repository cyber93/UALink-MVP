"""UALink 200 — DL Tx Pacing (Section 6.5)."""
from ..common.constants import SerialRate


class TxPacer:
    """
    Tx rate pacing: limits DL Flit tx rate based on TL rate notification.
    RS injects Idle every 1024 codewords for rate matching.
    Spec: Section 7.3.6.
    """
    def __init__(self, rate: SerialRate = SerialRate.G200):
        self.rate = rate
        self._flit_count = 0
        self._idle_interval = 1024  # inject idle every N codewords

    def tick(self) -> bool:
        """Returns True if should send Idle (not payload)."""
        self._flit_count += 1
        if self._flit_count % self._idle_interval == 0:
            return True
        return False

    def set_rate(self, rate: SerialRate):
        self.rate = rate
