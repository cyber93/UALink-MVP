"""
UALink 2.0 Common Specification — Read Response Channel (Table 2-8)
"""
from dataclasses import dataclass
from ..constants import RspStatus
from ..parity import even_parity

@dataclass
class ReadResponseChannel:
    valid: bool = False
    vld_parity: int = 0
    port_id: int = 0          # 2-bit
    status: int = RspStatus.OKAY # 4-bit
    tag: int = 0              # 11-bit
    offset: int = 0           # 2-bit (0-3 beat offset)
    num_beats: int = 1        # 2-bit (1-4 beats)
    vc: int = 0               # 2-bit
    data: bytes = bytes(64)   # 512 bits (64 bytes per beat)
    data_parity: int = 0      # 1-bit even parity over data
    data_error: bool = False  # Poison indication bit
    auth_tag: int = 0         # 64-bit Auth Tag (optional)

    def compute_parity(self):
        accum = (int(self.valid) ^ self.port_id ^ self.status ^ self.tag ^
                 self.offset ^ self.num_beats ^ self.vc)
        self.vld_parity = bin(accum).count('1') % 2
        total_ones = sum(bin(b).count('1') for b in self.data)
        self.data_parity = total_ones % 2
