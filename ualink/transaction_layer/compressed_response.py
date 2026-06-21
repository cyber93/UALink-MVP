"""UALink 200 — Compressed TL Response (1 sector, single/multi-beat)."""
from dataclasses import dataclass
from ..common.constants import TLFieldType


@dataclass
class CompressedResponseSingleBeat:
    """Compressed Read Rsp: 1 sector (4 bytes). Spec Table 5-33."""
    ftype: int = TLFieldType.COMPRESSED_RSP_SB
    tag: int = 0        # 11-bit
    status: int = 0     # 4-bit
    vc: int = 0         # 2-bit

    def serialize(self) -> bytes:
        w = (self.ftype & 0xF) | (self.status << 4) | (self.tag << 8) | (self.vc << 19)
        return w.to_bytes(4,'little')

    @classmethod
    def deserialize(cls, data: bytes) -> 'CompressedResponseSingleBeat':
        w = int.from_bytes(data[0:4],'little')
        obj = cls()
        obj.ftype  = w & 0xF
        obj.status = (w >> 4)  & 0xF
        obj.tag    = (w >> 8)  & 0x7FF
        obj.vc     = (w >> 19) & 0x3
        return obj


@dataclass
class CompressedResponseWriteOrMulti:
    """Compressed Write Rsp or Multi-beat Read Rsp: 1 sector. Spec Table 5-34."""
    ftype: int = TLFieldType.COMPRESSED_RSP_WR
    tag: int = 0        # 11-bit
    status: int = 0     # 4-bit
    vc: int = 0         # 2-bit
    num_beats: int = 0  # 2-bit (for multi-beat read)
    is_write: bool = False

    def serialize(self) -> bytes:
        w = (self.ftype & 0xF) | (int(self.is_write) << 4) | (self.status << 5) | (self.tag << 9) | (self.vc << 20) | (self.num_beats << 22)
        return w.to_bytes(4,'little')

    @classmethod
    def deserialize(cls, data: bytes) -> 'CompressedResponseWriteOrMulti':
        w = int.from_bytes(data[0:4],'little')
        obj = cls()
        obj.ftype    = w & 0xF
        obj.is_write = bool((w >> 4) & 1)
        obj.status   = (w >> 5)  & 0xF
        obj.tag      = (w >> 9)  & 0x7FF
        obj.vc       = (w >> 20) & 0x3
        obj.num_beats= (w >> 22) & 0x3
        return obj
