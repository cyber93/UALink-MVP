"""
UALink 2.0 Common Specification — Originator Data Channel (Table 2-14)
"""
from dataclasses import dataclass

@dataclass
class OriginatorDataChannel:
    valid: bool = False
    vld_parity: int = 0
    port_id: int = 0          # 2-bit
    data: bytes = bytes(64)   # 512 bits (64 bytes)
    byte_en: int = (1 << 64) - 1 # 64-bit byte enables
    offset: int = 0           # 2-bit (beat 0-3)
    data_parity: int = 0      # 1-bit
    data_error: bool = False  # Poison

    def compute_parity(self):
        accum = int(self.valid) ^ self.port_id ^ self.offset
        self.vld_parity = bin(accum).count('1') % 2
        total_ones = sum(bin(b).count('1') for b in self.data)
        self.data_parity = total_ones % 2
