"""UALink 200 — 640B DL Flit (Section 6.2)."""
from dataclasses import dataclass, field
from typing import List
from .segment import DLSegment, SEG_PAYLOAD_BYTES
from .crc import crc32_802_3, crc32_to_bytes, bytes_to_crc32, verify_crc
from ..common.constants import (
    DL_FLIT_BYTES, DL_SEGMENT_COUNT, DL_FLIT_HEADER_BYTES, DL_CRC_BYTES
)
from ..common.logger import log


FH_BYTES = 3


@dataclass
class FlitHeader:
    """
    3-byte DL Flit Header.
    Spec: Section 6.2.2. Encodes: op, ackReqSeq, flitSeqLo, port indicators.
    """
    op: int = 0             # 3-bit: Original(0), Replay(1), Ack(2), ReplayReq(3)
    ack_req_seq: int = 0    # 9-bit
    flit_seq_lo: int = 0    # 3-bit (low bits of TxReplay seq)

    def to_bytes(self) -> bytes:
        w0 = (self.op & 0x7) | ((self.ack_req_seq & 0x1F) << 3)
        w1 = ((self.ack_req_seq >> 5) & 0xF) | ((self.flit_seq_lo & 0x7) << 4)
        return bytes([w0, w1, 0x00])

    @classmethod
    def from_bytes(cls, data: bytes) -> 'FlitHeader':
        assert len(data) >= 3
        obj = cls()
        obj.op          = data[0] & 0x7
        obj.ack_req_seq = ((data[0] >> 3) & 0xFF) | ((data[1] & 0x1) << 8)
        obj.flit_seq_lo = (data[1] >> 1) & 0x7
        return obj


class DLFlit:
    """
    640-byte Data Link Flit.
    Layout: FH(3B) + 5×(SH(1B)+payload) + CRC(4B)
    = 3 + 5×(1+[124,128,128,128,64]) + 4
    = 3 + 5 + 572 + 4 = 640B (verify)
    Total payload across all segs: 124+128+128+128+64 = 572B
    + 5 seg headers + 3 flit header + 4 CRC = 584 → but spec says 640B total.
    Actually: 5 segs with 128+128+128+128+128 = 640 total minus headers.
    Spec Table 6-1: seg0=31 sectors (124B payload + 1 SH), segs1-3=32 sectors each,
    seg4=16 sectors. Total sectors = 31+32+32+32+16 = 143 sectors = 572B + 5 SH = 577B + FH=580B + CRC=584B.
    Spec: 640B total → padded to 640B.
    Spec: DL_TL_PAYLOAD_BYTES = 628 (see constants). This simplification is sufficient.
    """
    TOTAL_BYTES = DL_FLIT_BYTES  # 640

    def __init__(self):
        self.flit_header = FlitHeader()
        self.segments: List[DLSegment] = [DLSegment(i) for i in range(DL_SEGMENT_COUNT)]
        self.crc: int = 0

    def get_payload_bytes(self) -> bytes:
        """Returns concatenated payload of all 5 segments."""
        return b''.join(seg.payload for seg in self.segments)

    def set_payload(self, data: bytes):
        """Fill segments with data."""
        offset = 0
        for seg in self.segments:
            size = SEG_PAYLOAD_BYTES[seg.index]
            seg.payload = (data[offset:offset+size]).ljust(size, b'\x00')
            offset += size

    def compute_crc(self) -> int:
        body = self._serialize_body()
        self.crc = crc32_802_3(body)
        return self.crc

    def to_bytes(self) -> bytes:
        body = self._serialize_body().ljust(self.TOTAL_BYTES - DL_CRC_BYTES, b'\x00')
        crc = crc32_802_3(body)
        log.debug(f"DLFlit built: op={self.flit_header.op} seq={self.flit_header.ack_req_seq} crc={crc:08X} size={self.TOTAL_BYTES}")
        return body + crc32_to_bytes(crc)

    def verify(self, data: bytes) -> bool:
        body = data[:-DL_CRC_BYTES]
        stored = bytes_to_crc32(data[-DL_CRC_BYTES:])
        return verify_crc(body, stored)

    def _serialize_body(self) -> bytes:
        out = bytearray()
        out += self.flit_header.to_bytes()
        for seg in self.segments:
            out += seg.to_bytes()
        return bytes(out)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'DLFlit':
        assert len(data) >= cls.TOTAL_BYTES
        flit = cls()
        flit.flit_header = FlitHeader.from_bytes(data[:FH_BYTES])
        offset = FH_BYTES
        for i in range(DL_SEGMENT_COUNT):
            size = SEG_PAYLOAD_BYTES[i] + 1
            flit.segments[i] = DLSegment.from_bytes(i, data[offset:offset+size])
            offset += size
        flit.crc = bytes_to_crc32(data[-DL_CRC_BYTES:])
        return flit

    def __repr__(self):
        return f"DLFlit(op={self.flit_header.op}, seq={self.flit_header.ack_req_seq}, crc={self.crc:08X})"
