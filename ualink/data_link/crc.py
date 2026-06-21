"""UALink 200 — CRC-32 per IEEE 802.3 clause 3.2.9."""


CRC32_POLY = 0x04C11DB7
CRC32_INIT = 0xFFFFFFFF
CRC32_XOR  = 0xFFFFFFFF

def _reflect(val: int, bits: int) -> int:
    result = 0
    for _ in range(bits):
        result = (result << 1) | (val & 1)
        val >>= 1
    return result

def crc32_802_3(data: bytes) -> int:
    """Compute CRC-32 over data per 802.3 clause 3.2.9."""
    crc = CRC32_INIT
    for byte in data:
        b = _reflect(byte, 8)
        for _ in range(8):
            if (crc ^ (b << 24)) & 0x80000000:
                crc = ((crc << 1) ^ CRC32_POLY) & 0xFFFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFFFF
            b <<= 1
    return _reflect(crc, 32) ^ CRC32_XOR

def crc32_to_bytes(crc: int) -> bytes:
    return crc.to_bytes(4, 'little')

def bytes_to_crc32(data: bytes) -> int:
    return int.from_bytes(data[:4], 'little')

def verify_crc(data: bytes, stored_crc: int) -> bool:
    return crc32_802_3(data) == stored_crc
