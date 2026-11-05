"""
UALink 200G DL & PL Spec 2.0 — Link-Level Replay (Section 6.5)
Features: 9-bit sequence numbering (1-511, 0 reserved), TxReplay buffer,
Ack/Replay requests with 3-replica transmission.
"""
from typing import Dict, List, Optional
from collections import deque

class TxReplayBuffer:
    """Manages unacknowledged flits for link-level replay recovery."""
    MAX_UNACK = 255
    SEQ_MAX = 511

    def __init__(self):
        self.buffer: Dict[int, bytes] = {} # seq_num -> 640B flit
        self.next_tx_seq: int = 1
        self.last_ack_seq: int = 0

    def enqueue(self, flit_bytes: bytes) -> int:
        assert len(self.buffer) < self.MAX_UNACK, "TxReplay buffer overflow"
        seq = self.next_tx_seq
        self.buffer[seq] = flit_bytes
        self.next_tx_seq = (self.next_tx_seq % self.SEQ_MAX) + 1
        return seq

    def handle_ack(self, ack_seq: int):
        """Removes acknowledged flits from replay buffer."""
        curr = (self.last_ack_seq % self.SEQ_MAX) + 1
        while True:
            if curr in self.buffer:
                del self.buffer[curr]
            if curr == ack_seq or not self.buffer:
                break
            curr = (curr % self.SEQ_MAX) + 1
        self.last_ack_seq = ack_seq

    def get_replay_flits(self, req_seq: int) -> List[bytes]:
        """Returns flits starting from requested sequence number."""
        flits = []
        curr = req_seq
        while curr in self.buffer:
            flits.append(self.buffer[curr])
            curr = (curr % self.SEQ_MAX) + 1
        return flits
