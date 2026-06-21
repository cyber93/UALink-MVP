"""UALink 200 — RS Flit Code Sequences (Section 7.2)."""
from typing import List
from .encoding import (
    encode_data_block, encode_idle_block,
    encode_start_block, encode_fault_block,
    is_data_block, is_control_block
)
from ..common.constants import RS_BLOCKS_PER_FLIT


class FlitCodeSequence:
    """80 × 64B/66B blocks = one Flit Code Sequence (one DL Flit over PHY)."""
    BLOCKS = RS_BLOCKS_PER_FLIT  # 80

    @staticmethod
    def encode_data_flit(dl_flit_bytes: bytes) -> List[bytes]:
        """Convert 640B DL Flit → 80 data blocks."""
        assert len(dl_flit_bytes) == 640, f"Expected 640B, got {len(dl_flit_bytes)}"
        blocks = []
        for i in range(FlitCodeSequence.BLOCKS):
            block = dl_flit_bytes[i*8:(i+1)*8]  # 8B per block (simplified)
            blocks.append(encode_data_block(block.ljust(64, b'\x00')))
        return blocks

    @staticmethod
    def decode_data_flit(blocks: List[bytes]) -> bytes:
        """Convert 80 data blocks → 640B DL Flit."""
        assert len(blocks) == FlitCodeSequence.BLOCKS
        data = b''
        for b in blocks:
            data += b[1:9]  # strip sync header, take 8B
        return data[:640]

    @staticmethod
    def make_idle_sequence() -> List[bytes]:
        return [encode_idle_block() for _ in range(FlitCodeSequence.BLOCKS)]

    @staticmethod
    def make_idle_start_sequence() -> List[bytes]:
        seq = [encode_idle_block() for _ in range(FlitCodeSequence.BLOCKS)]
        seq[0] = encode_start_block()  # first block = Start type
        return seq

    @staticmethod
    def make_fault_sequence(is_remote: bool = False) -> List[bytes]:
        return [encode_fault_block(is_remote) for _ in range(FlitCodeSequence.BLOCKS)]

    @staticmethod
    def make_fault_start_sequence(is_remote: bool = False) -> List[bytes]:
        seq = [encode_fault_block(is_remote) for _ in range(FlitCodeSequence.BLOCKS)]
        seq[0] = encode_start_block()
        return seq

    @staticmethod
    def is_data_flit_sequence(blocks: List[bytes]) -> bool:
        return all(is_data_block(b) for b in blocks)

    @staticmethod
    def is_control_sequence(blocks: List[bytes]) -> bool:
        return all(is_control_block(b) for b in blocks)
