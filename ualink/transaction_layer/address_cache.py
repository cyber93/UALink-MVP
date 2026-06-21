"""UALink 200 — Tx/Rx address cache for TL compression (Section 5.2)."""
from collections import OrderedDict
from typing import Optional


CACHE_SIZE_DEFAULT = 8  # typical implementation cache depth


class AddressCache:
    """
    LRU address cache for TL request compression.
    Hit: compressed req (2 sectors) with cache index.
    Miss: uncompressed req (4 sectors) with full 57-bit address.
    Spec: Section 5.2.x (Compressed Request format).
    """
    def __init__(self, size: int = CACHE_SIZE_DEFAULT):
        self.size  = size
        self._lru: OrderedDict = OrderedDict()

    def lookup(self, addr: int) -> Optional[int]:
        """Returns cache index if hit, else None."""
        page = addr & ~0x3F
        if page in self._lru:
            self._lru.move_to_end(page)
            return list(self._lru.keys()).index(page)
        return None

    def insert(self, addr: int) -> int:
        """Insert address, evict LRU if full. Returns cache index."""
        page = addr & ~0x3F
        if page in self._lru:
            self._lru.move_to_end(page)
        else:
            if len(self._lru) >= self.size:
                self._lru.popitem(last=False)
            self._lru[page] = True
        return list(self._lru.keys()).index(page)

    def invalidate(self):
        self._lru.clear()

    def __len__(self) -> int:
        return len(self._lru)
