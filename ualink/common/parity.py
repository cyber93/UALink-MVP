"""UALink 200 — Even parity utilities."""

def even_parity(value: int, width: int) -> int:
    bits = bin(value & ((1 << width) - 1)).count('1')
    return bits % 2

def parity_byte(data: bytes) -> int:
    result = 0
    for byte in data:
        result ^= byte
    bits = bin(result).count('1')
    return bits % 2

def compute_data_parity(data: bytes) -> list:
    """8-bit data parity: one parity bit per 8 bytes (64-bit chunk)."""
    assert len(data) == 64
    result = []
    for i in range(8):
        chunk = data[i*8:(i+1)*8]
        val = int.from_bytes(chunk, 'little')
        result.append(bin(val).count('1') % 2)
    return result

def check_parity(value: int, width: int, parity_bit: int) -> bool:
    total_bits = bin(value & ((1 << width) - 1)).count('1') + parity_bit
    return total_bits % 2 == 0
