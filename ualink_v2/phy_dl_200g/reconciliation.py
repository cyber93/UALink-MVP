"""
UALink 200G DL & PL Spec 2.0 — Reconciliation Sublayer (RS) Flit Code Sequences
Spec: Section 7.2. 80 x 64B/66B blocks = 1 Flit Code Sequence (640B DL Flit over PHY).
"""
from typing import List
from .encoding import encode_64b66b_data, encode_64b66b_control, CTRL_START, CTRL_IDLE

class ReconciliationSublayer:
    BLOCKS_PER_FLIT = 80  # 80 x 8B = 640B

    @staticmethod
    def encode_flit_to_blocks(dl_flit_bytes: bytes) -> List[bytes]:
        assert len(dl_flit_bytes) == 640
        blocks = []
        for i in range(ReconciliationSublayer.BLOCKS_PER_FLIT):
            chunk = dl_flit_bytes[i*8:(i+1)*8].ljust(64, b'\x00')
            blocks.append(encode_64b66b_data(chunk))
        return blocks

    @staticmethod
    def decode_blocks_to_flit(blocks: List[bytes]) -> bytes:
        assert len(blocks) == ReconciliationSublayer.BLOCKS_PER_FLIT
        flit_bytes = b"".join(b[1:9] for b in blocks)
        return flit_bytes[:640]
