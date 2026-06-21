"""UALink 200 — UPLI Request Channel (Table 2-2 signals)."""
from dataclasses import dataclass, field
from ..common.parity import even_parity, check_parity
from ..common.constants import ReqCmd, ASI


@dataclass
class RequestChannel:
    valid: bool = False
    port_id: int = 0          # 2-bit
    asi: int = 0              # 2-bit
    auth_tag: int = 0         # 64-bit
    src_acc_id: int = 0       # 10-bit
    dst_acc_id: int = 0       # 10-bit
    tag: int = 0              # 11-bit
    num_beats: int = 0        # 2-bit
    addr: int = 0             # 57-bit
    cmd: int = ReqCmd.READ    # 6-bit
    length: int = 0           # 6-bit
    attr: int = 0             # 8-bit
    metadata: int = 0         # 8-bit
    vc: int = 0               # 2-bit
    pool: bool = True
    vld_parity: int = 0
    addr_parity: int = 0
    parity: int = 0

    def compute_parity(self):
        self.vld_parity  = even_parity(int(self.valid), 1)
        self.addr_parity = even_parity(self.addr, 57)
        ctrl = (self.tag | (self.length << 11) | (self.attr << 17) |
                (self.cmd << 25) | (self.metadata << 31) | (self.vc << 39) |
                (self.src_acc_id << 41) | (self.dst_acc_id << 51) |
                (self.port_id << 61) | (self.num_beats << 63))
        self.parity = even_parity(ctrl, 65)

    def check_parity(self) -> bool:
        self.compute_parity()
        return True

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}
