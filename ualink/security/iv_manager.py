"""UALink 200 — IV Manager (Section 9.5.1, Table 9-3)."""
from ..common.constants import SecurityStream, SEC_IV_BYTES


def build_iv_fixed(src_acc_id: int, dst_acc_id: int, stream: SecurityStream) -> bytes:
    """
    Fixed part of 96-bit IV (64 bits):
    Bits[63:54] = SrcAccID (10b)
    Bits[53:44] = DstAccID (10b)
    Bits[43:42] = StreamID (2b)
    Bits[41:0]  = Reserved/zero
    Spec: Table 9-3 IV Format.
    """
    val = ((src_acc_id & 0x3FF) << 54) | ((dst_acc_id & 0x3FF) << 44) | ((int(stream) & 0x3) << 42)
    return val.to_bytes(8, 'big')


class IVManager:
    """
    Manages 96-bit IVs per stream per destination accelerator.
    Invocation counter incremented per transaction.
    HW threshold: 2^32 - 1 → triggers key re-derivation.
    """
    def __init__(self, src_acc_id: int, dst_acc_id: int):
        self.src = src_acc_id
        self.dst = dst_acc_id
        self._counters = {s: 0 for s in SecurityStream}

    def get_iv(self, stream: SecurityStream) -> bytes:
        fixed = build_iv_fixed(self.src, self.dst, stream)
        inv   = self._counters[stream]
        return fixed + inv.to_bytes(4, 'little')

    def increment(self, stream: SecurityStream) -> int:
        self._counters[stream] += 1
        return self._counters[stream]

    def reset(self, stream: SecurityStream):
        self._counters[stream] = 0

    def get_invocation(self, stream: SecurityStream) -> int:
        return self._counters[stream]

    def is_expiring(self, stream: SecurityStream, threshold: int) -> bool:
        return self._counters[stream] >= threshold

    def is_hw_expired(self, stream: SecurityStream) -> bool:
        return self._counters[stream] >= (2**32 - 1)
