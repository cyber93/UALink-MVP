"""UALink 200 — Compressed TL Request (2 sectors, Table 5-32 restrictions)."""
from dataclasses import dataclass
from typing import Optional
from ..common.constants import TLFieldType, ReqCmd


COMPRESSIBLE_CMDS = {ReqCmd.READ, ReqCmd.WRITE, ReqCmd.WRITE_FULL}

def can_compress_req(cmd: int, addr: int, length: int,
                     cache_hit: bool, src_eq_dst: bool = False) -> bool:
    """
    Table 5-32 compression restrictions:
    - Only Read, Write, WriteFull
    - Address must be 64B-aligned (bits[5:0] = 0)
    - Length must encode full cache-line (15 DWs = 60 bytes? No: ReqLen=15 = 16DW = 64B)
    - Address cache hit required
    - No metadata/asi restrictions on compressed form
    """
    if cmd not in COMPRESSIBLE_CMDS:
        return False
    if not cache_hit:
        return False
    if (addr & 0x3F) != 0:
        return False
    return True


@dataclass
class CompressedRequest:
    """
    Compressed TL Request: 2 sectors (8 bytes) in control half-flit.
    Uses address cache index instead of full address.
    Spec: Section 5.2.x, Table 5-32.
    """
    ftype: int = TLFieldType.COMPRESSED_REQ
    src_acc_id: int = 0       # 10-bit
    dst_acc_id: int = 0       # 10-bit
    tag: int = 0              # 11-bit
    cmd: int = ReqCmd.READ    # 6-bit
    cache_index: int = 0      # cache index (4-8 bits depending on impl)
    length: int = 15          # 6-bit
    attr: int = 0xFF          # 8-bit
    vc: int = 0               # 2-bit
    num_beats: int = 0        # 2-bit

    def serialize(self) -> bytes:
        w0 = (self.ftype & 0xF) | (self.cmd << 4) | (self.src_acc_id << 10) | (self.dst_acc_id << 20)
        w1 = self.tag | (self.length << 11) | (self.attr << 17) | (self.cache_index << 25) | (self.vc << 29) | (self.num_beats << 31)
        return w0.to_bytes(4,'little') + w1.to_bytes(4,'little')

    @classmethod
    def deserialize(cls, data: bytes) -> 'CompressedRequest':
        assert len(data) >= 8
        w0 = int.from_bytes(data[0:4],'little')
        w1 = int.from_bytes(data[4:8],'little')
        obj = cls()
        obj.ftype      = w0 & 0xF
        obj.cmd        = (w0 >> 4)  & 0x3F
        obj.src_acc_id = (w0 >> 10) & 0x3FF
        obj.dst_acc_id = (w0 >> 20) & 0x3FF
        obj.tag        = w1 & 0x7FF
        obj.length     = (w1 >> 11) & 0x3F
        obj.attr       = (w1 >> 17) & 0xFF
        obj.cache_index= (w1 >> 25) & 0xF
        obj.vc         = (w1 >> 29) & 0x3
        obj.num_beats  = (w1 >> 31) & 0x3
        return obj
