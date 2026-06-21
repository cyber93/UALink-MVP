"""UALink 200 — 64B TL Flit construction and parsing (Ch5)."""
from dataclasses import dataclass, field
from typing import List, Optional
from ..common.constants import (
    TL_FLIT_BYTES, TL_SECTOR_BYTES, TL_SECTORS_PER_FLIT,
    TL_HALF_FLIT_BYTES, TLFieldType, TL_FIELD_SECTORS
)
from ..common.logger import log


@dataclass
class TLFlit:
    """
    64-byte TL Flit = 32B control half-flit + 32B data half-flit.
    Control half-flit: up to 8 sectors of headers.
    Data half-flit: up to 8 sectors of data (or another control half-flit).
    Spec: Section 5.2.
    """
    control_half: bytes = field(default_factory=lambda: bytes(32))
    data_half: bytes    = field(default_factory=lambda: bytes(32))

    def to_bytes(self) -> bytes:
        data = self.control_half + self.data_half
        log.debug(f"TLFlit assembled payload: ctrl_len={len(self.control_half)} data_len={len(self.data_half)} bytes")
        return data

    @classmethod
    def from_bytes(cls, data: bytes) -> 'TLFlit':
        assert len(data) == TL_FLIT_BYTES
        return cls(control_half=data[:32], data_half=data[32:])

    def extract_sectors(self, half: str = 'control') -> List[bytes]:
        src = self.control_half if half == 'control' else self.data_half
        return [src[i*4:(i+1)*4] for i in range(8)]

    def set_sector(self, sector_idx: int, data: bytes):
        """Write 4 bytes to sector_idx (0-15 across full 64B flit)."""
        assert len(data) == 4
        offset = sector_idx * 4
        full = bytearray(self.to_bytes())
        full[offset:offset+4] = data
        self.control_half = bytes(full[:32])
        self.data_half    = bytes(full[32:])

    def get_sector(self, sector_idx: int) -> bytes:
        offset = sector_idx * 4
        return self.to_bytes()[offset:offset+4]

    def has_data_half(self) -> bool:
        return any(b != 0 for b in self.data_half)

    def __repr__(self):
        return f"TLFlit(ctrl={self.control_half[:4].hex()}, data={self.data_half[:4].hex()})"
