"""
UALink 2.0 — In-Network Compute (INC) Reduction Engine
Spec: UALink Common Specification Rev 2.0 (Chapter 6)
"""
import struct
from typing import Dict, List, Optional
from ..constants import INCOpCode, INCDataType
from ..types import INCOperation

class INCEngine:
    """Executes arithmetic/bitwise reductions on vector payloads directly in network nodes."""

    @staticmethod
    def reduce(opcode: INCOpCode, dtype: INCDataType, buf_a: bytes, buf_b: bytes) -> bytes:
        """Element-wise reduction between two binary vectors."""
        assert len(buf_a) == len(buf_b), f"Vector size mismatch: {len(buf_a)} vs {len(buf_b)}"

        if dtype == INCDataType.FP32:
            count = len(buf_a) // 4
            vals_a = struct.unpack(f"<{count}f", buf_a)
            vals_b = struct.unpack(f"<{count}f", buf_b)

            if opcode == INCOpCode.SUM:
                res = [a + b for a, b in zip(vals_a, vals_b)]
            elif opcode == INCOpCode.MIN:
                res = [min(a, b) for a, b in zip(vals_a, vals_b)]
            elif opcode == INCOpCode.MAX:
                res = [max(a, b) for a, b in zip(vals_a, vals_b)]
            elif opcode == INCOpCode.PROD:
                res = [a * b for a, b in zip(vals_a, vals_b)]
            else:
                raise ValueError(f"Unsupported FP32 opcode: {opcode}")
            return struct.pack(f"<{count}f", *res)

        elif dtype == INCDataType.INT32:
            count = len(buf_a) // 4
            vals_a = struct.unpack(f"<{count}i", buf_a)
            vals_b = struct.unpack(f"<{count}i", buf_b)

            if opcode == INCOpCode.SUM:
                res = [a + b for a, b in zip(vals_a, vals_b)]
            elif opcode == INCOpCode.MIN:
                res = [min(a, b) for a, b in zip(vals_a, vals_b)]
            elif opcode == INCOpCode.MAX:
                res = [max(a, b) for a, b in zip(vals_a, vals_b)]
            elif opcode == INCOpCode.BAND:
                res = [a & b for a, b in zip(vals_a, vals_b)]
            elif opcode == INCOpCode.BOR:
                res = [a | b for a, b in zip(vals_a, vals_b)]
            elif opcode == INCOpCode.BXOR:
                res = [a ^ b for a, b in zip(vals_a, vals_b)]
            else:
                raise ValueError(f"Unsupported INT32 opcode: {opcode}")
            return struct.pack(f"<{count}i", *res)

        else:
            return bytes([a ^ b for a, b in zip(buf_a, buf_b)])


class INCCollectiveCoordinator:
    """Coordinates collective reduction operations inside a Switch."""
    def __init__(self, collective_id: int, expected_peers: List[int], op: INCOperation):
        self.collective_id = collective_id
        self.expected_peers = set(expected_peers)
        self.received_peers = set()
        self.op = op
        self.accumulator: Optional[bytes] = None

    def contribute(self, peer_id: int, payload: bytes) -> bool:
        assert peer_id in self.expected_peers, f"Peer {peer_id} not in collective {self.collective_id}"
        assert peer_id not in self.received_peers, f"Duplicate submission from peer {peer_id}"

        self.received_peers.add(peer_id)
        if self.accumulator is None:
            self.accumulator = payload
        else:
            self.accumulator = INCEngine.reduce(self.op.opcode, self.op.dtype, self.accumulator, payload)

        return self.is_complete()

    def is_complete(self) -> bool:
        return self.received_peers == self.expected_peers

    def get_result(self) -> bytes:
        assert self.is_complete(), "Reduction not yet complete"
        return self.accumulator or b''
