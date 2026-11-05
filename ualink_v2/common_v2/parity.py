"""
UALink 2.0 — Even Parity Computation
Spec: Chapter 2 & Chapter 3 (RAS)
"""

def even_parity(val: int, bits: int) -> int:
    """Calculates even parity over bits of an integer."""
    cnt = bin(val & ((1 << bits) - 1)).count('1')
    return cnt % 2

def compute_byte_parity(data: bytes) -> int:
    """Calculates even parity over a byte sequence."""
    total_ones = sum(bin(b).count('1') for b in data)
    return total_ones % 2
