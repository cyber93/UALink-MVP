"""
UALink 200G DL & PL Spec 2.0 — DL Segment Model (Table 6-1)
Each 640B DL Flit contains 5 Segments with 1B Segment Header (SH).
"""
from dataclasses import dataclass
from typing import List

SEGMENT_SECTORS = [31, 32, 32, 32, 16] # Table 6-1 payload sectors
SECTOR_BYTES = 4

@dataclass
class DLSegment:
    seg_idx: int
    header: int = 0             # 1-byte SH
    sectors: List[bytes] = None # List of 4B sectors

    def __post_init__(self):
        max_sec = SEGMENT_SECTORS[self.seg_idx]
        if self.sectors is None:
            self.sectors = [bytes(4) for _ in range(max_sec)]

    def to_bytes(self) -> bytes:
        return bytes([self.header]) + b"".join(self.sectors)
