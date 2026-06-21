"""UALink 200 — UPLI Write Response Channel (Table 2-11)."""
from dataclasses import dataclass
from ..common.parity import even_parity
from ..common.constants import WrRspStatus


@dataclass
class WriteResponseChannel:
    valid: bool = False
    port_id: int = 0          # 2-bit
    auth_tag: int = 0         # 64-bit
    src_acc_id: int = 0       # 10-bit (debug)
    dst_acc_id: int = 0       # 10-bit (routing)
    tag: int = 0              # 11-bit
    status: int = WrRspStatus.OKAY  # 4-bit
    vc: int = 0               # 2-bit
    pool: bool = True
    vld_parity: int = 0
    parity: int = 0

    def compute_parity(self):
        self.vld_parity = even_parity(int(self.valid), 1)
        ctrl = (self.tag | (self.status << 11) | (self.src_acc_id << 15) |
                (self.dst_acc_id << 25) | (self.port_id << 35) | (self.vc << 37))
        self.parity = even_parity(ctrl, 39)

    def is_isolate(self) -> bool:
        return self.status == WrRspStatus.ISOLATE

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}
