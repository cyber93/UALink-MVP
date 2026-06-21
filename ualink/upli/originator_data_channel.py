"""UALink 200 — UPLI Originator Data Channel (Table 2-14)."""
from dataclasses import dataclass, field
from ..common.parity import even_parity, compute_data_parity


@dataclass
class OriginatorDataChannel:
    valid: bool = False
    port_id: int = 0          # 2-bit
    data: bytes = field(default_factory=lambda: bytes(64))  # 512-bit
    byte_enables: int = 0     # 64-bit mask
    offset: int = 0           # 2-bit
    last: bool = False
    data_error: bool = False  # poison indicator
    vld_parity: int = 0
    fields_parity: int = 0
    data_parity: list = field(default_factory=lambda: [0]*8)

    def compute_parity(self):
        self.vld_parity   = even_parity(int(self.valid), 1)
        self.data_parity  = compute_data_parity(self.data)
        ctrl = (self.byte_enables | (self.offset << 64) |
                (int(self.last) << 66) | (int(self.data_error) << 67) |
                (self.port_id << 68))
        self.fields_parity = even_parity(ctrl, 70)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}
