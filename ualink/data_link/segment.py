"""UALink 200 — DL Flit Segment (Section 6.2, Table 6-1)."""
from dataclasses import dataclass, field
from ..common.constants import DL_SEG_PAYLOAD_SECTORS, DL_SECTOR_BYTES


SEG_PAYLOAD_BYTES = [n * DL_SECTOR_BYTES for n in DL_SEG_PAYLOAD_SECTORS]
# [124, 128, 128, 128, 64] bytes of payload per segment


@dataclass
class SegmentHeader:
    """
    1-byte segment header per DL Flit segment.
    Spec: Table 6-2. Encodes: DL msg present, DL msg type, carry-over info.
    """
    dl_msg_present: bool = False
    dl_msg_start: bool = False
    dl_msg_end: bool = False
    tl_sector_start: int = 0    # which TL sector starts in this segment
    is_alt_sector: bool = False  # uses DL alternative sector (non-TL)

    def to_byte(self) -> int:
        b = 0
        b |= int(self.dl_msg_present) << 7
        b |= int(self.dl_msg_start)   << 6
        b |= int(self.dl_msg_end)     << 5
        b |= int(self.is_alt_sector)  << 4
        b |= self.tl_sector_start & 0xF
        return b

    @classmethod
    def from_byte(cls, b: int) -> 'SegmentHeader':
        obj = cls()
        obj.dl_msg_present = bool(b & 0x80)
        obj.dl_msg_start   = bool(b & 0x40)
        obj.dl_msg_end     = bool(b & 0x20)
        obj.is_alt_sector  = bool(b & 0x10)
        obj.tl_sector_start= b & 0xF
        return obj


@dataclass
class DLSegment:
    """One of 5 segments in a 640B DL Flit."""
    index: int   # 0-4
    header: SegmentHeader = field(default_factory=SegmentHeader)
    payload: bytes = field(default_factory=bytes)

    def __post_init__(self):
        expected = SEG_PAYLOAD_BYTES[self.index]
        if not self.payload:
            self.payload = bytes(expected)
        assert len(self.payload) == expected, \
            f"Seg {self.index}: expected {expected}B, got {len(self.payload)}B"

    def to_bytes(self) -> bytes:
        return bytes([self.header.to_byte()]) + self.payload

    @classmethod
    def from_bytes(cls, index: int, data: bytes) -> 'DLSegment':
        expected = SEG_PAYLOAD_BYTES[index] + 1
        assert len(data) >= expected
        hdr  = SegmentHeader.from_byte(data[0])
        pl   = data[1:expected]
        return cls(index=index, header=hdr, payload=pl)
