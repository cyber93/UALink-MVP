"""UALink 200 — UPLI Read Response/Data Channel (Table 2-8)."""
from dataclasses import dataclass, field
from ..common.parity import even_parity, compute_data_parity
from ..common.constants import RdRspStatus


@dataclass
class ReadResponseChannel:
    valid: bool = False
    port_id: int = 0          # 2-bit
    auth_tag: int = 0         # 64-bit
    src_acc_id: int = 0       # 10-bit (debug only, may be 0)
    dst_acc_id: int = 0       # 10-bit (routing)
    tag: int = 0              # 11-bit
    num_beats: int = 0        # 2-bit
    data: bytes = field(default_factory=lambda: bytes(64))  # 512-bit
    status: int = RdRspStatus.OKAY  # 4-bit, same across all beats
    offset: int = 0           # 2-bit beat index
    last: bool = False
    data_error: bool = False  # poison indicator
    vc: int = 0               # 2-bit
    pool: bool = True
    vld_parity: int = 0
    data_parity: list = field(default_factory=lambda: [0]*8)  # 8-bit
    parity: int = 0

    def compute_parity(self):
        self.vld_parity   = even_parity(int(self.valid), 1)
        self.data_parity  = compute_data_parity(self.data)
        ctrl = (self.tag | (self.status << 11) | (self.offset << 15) |
                (int(self.last) << 17) | (self.num_beats << 18) |
                (self.vc << 20) | (self.src_acc_id << 22) |
                (self.dst_acc_id << 32) | (self.port_id << 42) |
                (int(self.data_error) << 44))
        self.parity = even_parity(ctrl, 45)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}
