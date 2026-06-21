"""UALink 200 — DL Link-Level Replay (Section 6.6)."""
from collections import deque
from typing import Optional, Deque, Tuple
from .dl_flit import DLFlit, FlitHeader
from ..common.constants import (
    DL_REPLAY_SEQ_MAX, DL_REPLAY_MAX_UNACK, DL_REPLAY_REQ_COUNT
)


def seq_add(a: int, n: int) -> int:
    """Increment seq, 511→1 wrap (0 reserved)."""
    result = a + n
    while result > DL_REPLAY_SEQ_MAX:
        result = result - DL_REPLAY_SEQ_MAX
    return result

def seq_dist(a: int, b: int) -> int:
    """(a - b) % 511, wrapping 0→511."""
    return ((a - b) % DL_REPLAY_SEQ_MAX) or DL_REPLAY_SEQ_MAX


class TxReplayBuffer:
    """
    Sliding window replay buffer for transmitted DL Flits.
    Max 255 unacknowledged payload flits.
    Spec: Section 6.6.6.
    """
    def __init__(self):
        self._buf: Deque[Tuple[int, DLFlit]] = deque()
        self.tx_last_seq: int = DL_REPLAY_SEQ_MAX  # starts at 511
        self.rx_last_ack: int = 0
        self.tx_replay: bool = False
        self.tx_first_replay: bool = False
        self.tx_replay_ptr: int = 0
        self.tx_explicit_count: int = 7

    def enqueue(self, flit: DLFlit) -> Optional[int]:
        """Add flit to replay buffer. Returns seq_no or None if full."""
        unacked = len(self._buf)
        if self.tx_replay or unacked >= DL_REPLAY_MAX_UNACK:
            return None
        self.tx_last_seq = seq_add(self.tx_last_seq, 1)
        seq = self.tx_last_seq
        self._buf.append((seq, flit))
        return seq

    def ack(self, ack_seq: int) -> int:
        """Remove flits ≤ ack_seq. Spec: Section 6.6.6.3. Returns removed count."""
        removed = 0
        while self._buf:
            s, _ = self._buf[0]
            if seq_dist(ack_seq, s) >= seq_dist(ack_seq, self.rx_last_ack):
                break
            self._buf.popleft()
            removed += 1
        self.rx_last_ack = ack_seq
        return removed

    def start_replay(self, replay_seq: int):
        """Trigger replay from replay_seq. Spec: Section 6.6.6.3."""
        self.tx_replay = True
        self.tx_first_replay = True
        self.tx_replay_ptr = replay_seq

    def next_replay_flit(self) -> Optional[Tuple[int, DLFlit]]:
        for seq, flit in self._buf:
            if seq == self.tx_replay_ptr:
                self.tx_replay_ptr = seq_add(self.tx_replay_ptr, 1)
                if not any(s >= self.tx_replay_ptr for s, _ in self._buf):
                    self.tx_replay = False
                return seq, flit
        self.tx_replay = False
        return None

    def is_full(self) -> bool:
        return len(self._buf) >= DL_REPLAY_MAX_UNACK

    def unacked_count(self) -> int:
        return len(self._buf)


class ReplayStateMachine:
    """
    Full DL replay state machine: Rx ingress + Tx scheduling.
    Spec: Section 6.6.6, Fig 6-20, 6-21.
    """
    OP_ORIGINAL    = 0b000
    OP_REPLAY      = 0b001
    OP_ACK         = 0b010
    OP_REPLAY_REQ  = 0b011

    def __init__(self):
        self.tx_buf = TxReplayBuffer()
        self.rx_last_seq_calc: int = 0
        self.rx_bad_crc_count: int = 0
        self.rx_unexpected_count: int = 0
        self.rx_replay_limit: int = 50
        self.rx_ambiguous: bool = False
        self.rx_replay: bool = False
        self.rx_replay_ignore_count: int = 0
        self.tx_replay_req_count: int = 0
        self.tx_replay_req_seq_no: int = 0
        self.tx_explicit_count: int = 7
        self.tx_ack_counter: int = 0
        self.tx_ack_timeout: int = 40_000

    def on_rx_flit(self, flit: DLFlit, crc_ok: bool):
        """Process received flit. Spec: Rx Ingress Rules."""
        if self.rx_replay_ignore_count > 0:
            self.rx_replay_ignore_count -= 1

        if not crc_ok:
            self.rx_bad_crc_count += 1
            if self.rx_bad_crc_count >= 7:
                self.rx_ambiguous = True
            if self.rx_replay:
                self.rx_unexpected_count += 1
            return

        fh = flit.flit_header
        self._process_ack_or_replay_req(fh)
        self._process_seq(fh)

    def _process_ack_or_replay_req(self, fh: FlitHeader):
        seq = fh.ack_req_seq
        if seq == 0:
            return  # drop + log error per spec
        if fh.op == self.OP_REPLAY_REQ and self.rx_replay_ignore_count == 0:
            valid = (seq_dist(seq, self.tx_buf.rx_last_ack) <= 256 and
                     seq_dist(self.tx_buf.tx_last_seq, seq) <= 256)
            if valid:
                self.tx_buf.start_replay(seq)
                self.rx_replay_ignore_count = 12
        elif fh.op == self.OP_ACK:
            valid = (seq_dist(seq, self.tx_buf.rx_last_ack) <= 256 and
                     seq_dist(self.tx_buf.tx_last_seq, seq) <= 256)
            if valid:
                removed = self.tx_buf.ack(seq)
                if removed > 0:
                    self.tx_ack_counter = self.tx_ack_timeout

    def _process_seq(self, fh: FlitHeader):
        is_explicit = (fh.op in (self.OP_ORIGINAL, self.OP_REPLAY))
        if is_explicit or (not self.rx_ambiguous and not self.rx_replay):
            expected = self.rx_last_seq_calc + (1 if is_explicit else 0)
            if fh.ack_req_seq == expected:
                self.rx_last_seq_calc = fh.ack_req_seq
                self.rx_unexpected_count = 0
                self.rx_replay = False
                self.rx_ambiguous = False
                self.rx_bad_crc_count = 0
            elif not self.rx_replay:
                self.tx_replay_req_count = DL_REPLAY_REQ_COUNT
                self.rx_replay = True
                self.rx_unexpected_count = 0
            else:
                self.rx_unexpected_count += 1
                if self.rx_unexpected_count >= self.rx_replay_limit:
                    self.tx_replay_req_count = DL_REPLAY_REQ_COUNT
                    self.rx_bad_crc_count = 0

    def schedule_tx(self) -> Tuple[int, int, int]:
        """Returns (op, ack_req_seq, use_explicit_seq). Spec: Tx Scheduling."""
        self.tx_explicit_count = max(0, self.tx_explicit_count - 1)
        if self.tx_buf.tx_first_replay:
            self.tx_buf.tx_first_replay = False
            self.tx_explicit_count = 7
            return self.OP_REPLAY, self.tx_buf.tx_replay_ptr, 1
        if self.tx_explicit_count <= 0:
            self.tx_explicit_count = 7
            op = self.OP_REPLAY if self.tx_buf.tx_replay else self.OP_ORIGINAL
            return op, self.rx_last_seq_calc, 1
        if self.tx_replay_req_count > 0:
            if self.tx_replay_req_count == DL_REPLAY_REQ_COUNT:
                self.tx_replay_req_seq_no = seq_add(self.rx_last_seq_calc, 1)
            self.tx_replay_req_count -= 1
            return self.OP_REPLAY_REQ, self.tx_replay_req_seq_no, 0
        return self.OP_ACK, self.rx_last_seq_calc, 0
