"""UALink 200 — Uncompressed Request/Response TL formats (Section 5.2)."""
from dataclasses import dataclass
from ..common.constants import TLFieldType, ReqCmd, RdRspStatus, WrRspStatus


@dataclass
class UncompressedRequest:
    """
    Uncompressed TL Request: 4 sectors (16 bytes) in control half-flit.
    Carries full 57-bit address. Spec Table 5-29.
    """
    ftype: int = TLFieldType.UNCOMPRESSED_REQ
    src_acc_id: int = 0       # 10-bit
    dst_acc_id: int = 0       # 10-bit
    tag: int = 0              # 11-bit
    cmd: int = ReqCmd.READ    # 6-bit
    addr: int = 0             # 57-bit
    length: int = 0           # 6-bit (DWs - 1)
    attr: int = 0             # 8-bit
    metadata: int = 0         # 8-bit
    asi: int = 0              # 2-bit
    vc: int = 0               # 2-bit
    num_beats: int = 0        # 2-bit

    def serialize(self) -> bytes:
        """Pack into 16 bytes (4 sectors)."""
        w0 = (self.ftype & 0xF) | (self.cmd << 4) | (self.src_acc_id << 10) | (self.dst_acc_id << 20)
        w1 = self.tag | (self.length << 11) | (self.attr << 17) | (self.metadata << 25)
        w2 = self.addr & 0xFFFFFFFF
        w3 = ((self.addr >> 32) & 0x1FFFFFF) | (self.vc << 25) | (self.num_beats << 27) | (self.asi << 29)
        return (w0.to_bytes(4,'little') + w1.to_bytes(4,'little') +
                w2.to_bytes(4,'little') + w3.to_bytes(4,'little'))

    @classmethod
    def deserialize(cls, data: bytes) -> 'UncompressedRequest':
        assert len(data) >= 16
        w0 = int.from_bytes(data[0:4],  'little')
        w1 = int.from_bytes(data[4:8],  'little')
        w2 = int.from_bytes(data[8:12], 'little')
        w3 = int.from_bytes(data[12:16],'little')
        obj = cls()
        obj.ftype      = w0 & 0xF
        obj.cmd        = (w0 >> 4)  & 0x3F
        obj.src_acc_id = (w0 >> 10) & 0x3FF
        obj.dst_acc_id = (w0 >> 20) & 0x3FF
        obj.tag        = w1 & 0x7FF
        obj.length     = (w1 >> 11) & 0x3F
        obj.attr       = (w1 >> 17) & 0xFF
        obj.metadata   = (w1 >> 25) & 0x7F
        obj.addr       = w2 | (int(w3 & 0x1FFFFFF) << 32)
        obj.vc         = (w3 >> 25) & 0x3
        obj.num_beats  = (w3 >> 27) & 0x3
        obj.asi        = (w3 >> 29) & 0x3
        return obj


@dataclass
class UncompressedResponse:
    """
    Uncompressed TL Response: 2 sectors (8 bytes). Spec Table 5-30.
    Used for Read and Write responses when compressed form not possible.
    """
    ftype: int = TLFieldType.UNCOMPRESSED_RSP
    tag: int = 0              # 11-bit
    status: int = 0           # 4-bit (RdRsp or WrRsp)
    src_acc_id: int = 0       # 10-bit
    dst_acc_id: int = 0       # 10-bit
    vc: int = 0               # 2-bit
    is_write_rsp: bool = False
    num_beats: int = 0        # 2-bit

    def serialize(self) -> bytes:
        w0 = (self.ftype & 0xF) | (int(self.is_write_rsp) << 4) | (self.status << 5) | (self.tag << 9)
        w1 = self.src_acc_id | (self.dst_acc_id << 10) | (self.vc << 20) | (self.num_beats << 22)
        return w0.to_bytes(4,'little') + w1.to_bytes(4,'little')

    @classmethod
    def deserialize(cls, data: bytes) -> 'UncompressedResponse':
        assert len(data) >= 8
        w0 = int.from_bytes(data[0:4],'little')
        w1 = int.from_bytes(data[4:8],'little')
        obj = cls()
        obj.ftype        = w0 & 0xF
        obj.is_write_rsp = bool((w0 >> 4) & 1)
        obj.status       = (w0 >> 5) & 0xF
        obj.tag          = (w0 >> 9) & 0x7FF
        obj.src_acc_id   = w1 & 0x3FF
        obj.dst_acc_id   = (w1 >> 10) & 0x3FF
        obj.vc           = (w1 >> 20) & 0x3
        obj.num_beats    = (w1 >> 22) & 0x3
        return obj
