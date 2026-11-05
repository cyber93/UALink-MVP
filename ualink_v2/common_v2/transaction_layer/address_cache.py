"""
UALink 2.0 Common Specification — Address Cache for Request Compression (Section 5.3)
"""
from typing import Dict, Optional

class AddressCache:
    """32-entry Tx/Rx address cache for 64B-aligned compression."""
    MAX_ENTRIES = 32

    def __init__(self):
        self.entries: Dict[int, int] = {}  # index (0-31) -> base_addr (64B aligned)
        self.reverse: Dict[int, int] = {}  # base_addr -> index
        self.next_evict: int = 0

    def lookup(self, addr: int) -> Optional[int]:
        base = addr & ~0x3F  # 64B aligned
        return self.reverse.get(base)

    def insert(self, addr: int) -> int:
        base = addr & ~0x3F
        if base in self.reverse:
            return self.reverse[base]

        idx = self.next_evict
        if idx in self.entries:
            old_base = self.entries[idx]
            self.reverse.pop(old_base, None)

        self.entries[idx] = base
        self.reverse[base] = idx
        self.next_evict = (self.next_evict + 1) % self.MAX_ENTRIES
        return idx
