"""UALink 200 — PCS/FEC stubs (Section 7.3, 7.4)."""
from ..common.constants import SerialRate, LinkWidth


class PCSStub:
    """
    PCS stub: structural model of RS(544,514) FEC encoding/decoding.
    In a real implementation: scramble, transcode 64B/66B→256B/257B,
    FEC encode, symbol distribution, alignment marker overwrite.
    This stub passes data through transparently (simulation only).
    Spec: Sections 7.3 (100G), 7.4 (200G/400G), 7.5 (800G).
    """
    def __init__(self, rate: SerialRate = SerialRate.G200,
                 width: LinkWidth = LinkWidth.X1):
        self.rate  = rate
        self.width = width
        self._fec_errors_injected = 0

    def encode(self, blocks: list) -> list:
        """Tx path: scramble + FEC encode. Stub: passthrough."""
        return blocks

    def decode(self, blocks: list) -> tuple:
        """Rx path: FEC decode + descramble. Stub: passthrough, no errors."""
        corrected = 0
        return blocks, corrected

    def inject_error(self):
        self._fec_errors_injected += 1

    @property
    def fec_correction_count(self) -> int:
        return self._fec_errors_injected


class LinkFaultSignaling:
    """
    RS Link Fault Signaling state machine per 802.3 clause 81.3.4.
    Spec: Section 7.2.4.
    """
    def __init__(self):
        self._local_fault  = False
        self._remote_fault = False

    def set_local_fault(self, f: bool):
        self._local_fault = f

    def set_remote_fault(self, f: bool):
        self._remote_fault = f

    def should_send_remote_fault(self) -> bool:
        return self._local_fault

    def should_send_idle(self) -> bool:
        return self._remote_fault

    def has_fault(self) -> bool:
        return self._local_fault or self._remote_fault
