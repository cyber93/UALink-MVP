"""UALink 200 — Request/Response ordering per spec Section 2.7.6."""
from collections import defaultdict
from ..common.constants import OrderingMode


class OrderingTracker:
    """
    Enforces UPLI ordering rules per spec:
    - Non-strict: requests in same 256B region stay ordered per src/dst/VC
    - Strict (security on): ALL requests from src to dst stay ordered
    """
    def __init__(self, mode: OrderingMode = OrderingMode.RELAXED):
        self.mode = mode
        self._queues = defaultdict(list)

    def _key(self, src: int, dst: int, addr: int, vc: int) -> tuple:
        if self.mode == OrderingMode.STRICT:
            return (src, dst)
        region = addr & ~0xFF
        return (src, dst, region, vc)

    def enqueue(self, src: int, dst: int, addr: int, vc: int, tag: int):
        self._queues[self._key(src, dst, addr, vc)].append(tag)

    def can_issue(self, src: int, dst: int, addr: int, vc: int, tag: int) -> bool:
        key = self._key(src, dst, addr, vc)
        q = self._queues[key]
        return len(q) == 0 or q[-1] == tag

    def complete(self, src: int, dst: int, addr: int, vc: int, tag: int):
        key = self._key(src, dst, addr, vc)
        q = self._queues[key]
        if q and q[0] == tag:
            q.pop(0)
