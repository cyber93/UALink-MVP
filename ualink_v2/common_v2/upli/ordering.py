"""
UALink 2.0 Common Specification — Ordering Tracker (Section 2.5)
"""
from typing import Dict, List
from ..constants import OrderingMode

class OrderingTracker:
    def __init__(self, mode: OrderingMode = OrderingMode.RELAXED):
        self.mode = mode
        self.region_queues: Dict[int, List[int]] = {} # region_addr -> list of tags
        self.strict_queue: List[int] = []

    def get_region_id(self, addr: int) -> int:
        return addr >> 8  # 256-byte aligned region

    def enqueue(self, tag: int, addr: int):
        if self.mode == OrderingMode.STRICT:
            self.strict_queue.append(tag)
        else:
            rid = self.get_region_id(addr)
            self.region_queues.setdefault(rid, []).append(tag)

    def is_head_of_line(self, tag: int, addr: int) -> bool:
        if self.mode == OrderingMode.STRICT:
            return bool(self.strict_queue and self.strict_queue[0] == tag)
        rid = self.get_region_id(addr)
        q = self.region_queues.get(rid, [])
        return bool(q and q[0] == tag)

    def complete(self, tag: int, addr: int):
        if self.mode == OrderingMode.STRICT:
            if self.strict_queue and self.strict_queue[0] == tag:
                self.strict_queue.pop(0)
        else:
            rid = self.get_region_id(addr)
            q = self.region_queues.get(rid, [])
            if q and q[0] == tag:
                q.pop(0)
