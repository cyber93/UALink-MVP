"""
UALink 2.0 Common Specification — Write Response Channel (Table 2-11)
"""
from dataclasses import dataclass
from ..constants import RspStatus

@dataclass
class WriteResponseChannel:
    valid: bool = False
    vld_parity: int = 0
    port_id: int = 0          # 2-bit
    status: int = RspStatus.OKAY # 4-bit
    tag: int = 0              # 11-bit
    vc: int = 0               # 2-bit
    auth_tag: int = 0         # 64-bit

    def compute_parity(self):
        accum = int(self.valid) ^ self.port_id ^ self.status ^ self.tag ^ self.vc
        self.vld_parity = bin(accum).count('1') % 2
