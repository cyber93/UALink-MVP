"""
UALinkSec 2.0 — 96-bit AES-GCM IV Management (Chapter 9)
Format: SrcAccID (10b) + DstAccID (10b) + StreamID (2b) + Epoch (42b) + Invocation (32b) = 96 bits.
"""
from dataclasses import dataclass

@dataclass
class UALinkIV:
    src_id: int
    dst_id: int
    stream_id: int # 0=Req, 1=RdRsp, 2=WrRsp
    epoch: int = 1
    invocation: int = 0

    def to_bytes(self) -> bytes:
        """Constructs 12-byte (96-bit) IV."""
        # Packing: 32-bit invocation at low end
        fixed_high = (
            (self.src_id & 0x3FF) |
            ((self.dst_id & 0x3FF) << 10) |
            ((self.stream_id & 0x03) << 20) |
            ((self.epoch & 0x3FFFFFFFFF) << 22)
        )
        return self.invocation.to_bytes(4, 'little') + fixed_high.to_bytes(8, 'little')

class IVManager:
    """Tracks invocation counters per stream to prevent nonce reuse."""
    MAX_INVOCATION = (1 << 32) - 1

    def __init__(self, src_id: int, dst_id: int):
        self.src_id = src_id
        self.dst_id = dst_id
        self.counters = {0: 0, 1: 0, 2: 0} # stream_id -> counter
        self.epoch = 1

    def next_iv(self, stream_id: int) -> bytes:
        cnt = self.counters[stream_id]
        assert cnt < self.MAX_INVOCATION, "Invocation counter overflow! Key rollover required."
        self.counters[stream_id] += 1
        iv = UALinkIV(src_id=self.src_id, dst_id=self.dst_id, stream_id=stream_id,
                      epoch=self.epoch, invocation=cnt)
        return iv.to_bytes()
