"""UALink 200 — TL Flow Control / NOP field (1 sector)."""
from dataclasses import dataclass
from ..common.constants import TLFieldType


@dataclass
class FCNOPField:
    """
    Flow Control / NOP sector: 1 sector (4 bytes).
    Carries credit return info or padding.
    Spec: Section 5.3 (TL Credit Return).
    """
    ftype: int = TLFieldType.FLOW_CTRL_NOP
    req_credits: int = 0    # Req CMD credits being returned
    data_credits: int = 0   # Data credits being returned
    vc: int = 0             # Virtual channel

    def serialize(self) -> bytes:
        w = (self.ftype & 0xF) | (self.req_credits << 4) | (self.data_credits << 12) | (self.vc << 20)
        return w.to_bytes(4,'little')

    @classmethod
    def deserialize(cls, data: bytes) -> 'FCNOPField':
        w = int.from_bytes(data[0:4],'little')
        obj = cls()
        obj.ftype        = w & 0xF
        obj.req_credits  = (w >> 4)  & 0xFF
        obj.data_credits = (w >> 12) & 0xFF
        obj.vc           = (w >> 20) & 0x3
        return obj
