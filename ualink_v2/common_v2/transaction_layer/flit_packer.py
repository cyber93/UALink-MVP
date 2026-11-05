"""
UALink 2.0 Common Specification — TL Flit Packer (Section 5.2)
"""
from typing import List
from .field_types import TLFieldType, TL_FIELD_SECTORS
from ..tl_v2 import TL2Flit

class TLFlitPacker:
    """Packs control/data sectors into 64B TL Flits (16 sectors x 4B)."""

    def __init__(self):
        self.control_sectors: List[bytes] = []
        self.data_sectors: List[bytes] = []

    def add_sector(self, sector_bytes: bytes, is_data: bool = False):
        assert len(sector_bytes) == 4, f"Sector must be 4B, got {len(sector_bytes)}"
        if is_data:
            self.data_sectors.append(sector_bytes)
        else:
            self.control_sectors.append(sector_bytes)

    def pack_flit(self) -> TL2Flit:
        """Assembles up to 8 control sectors and 8 data sectors into a 64B TL Flit."""
        ctrl = b"".join(self.control_sectors[:8]).ljust(32, b'\x00')
        data = b"".join(self.data_sectors[:8]).ljust(32, b'\x00')

        self.control_sectors = self.control_sectors[8:]
        self.data_sectors = self.data_sectors[8:]

        return TL2Flit(control_half=ctrl, data_half=data)
