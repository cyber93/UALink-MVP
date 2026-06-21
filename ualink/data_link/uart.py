"""UALink 200 — UART: DL Universal Anonymous Receiver/Transmitter (Section 6.4)."""
from dataclasses import dataclass, field
from typing import List, Optional
from collections import deque
from ..common.constants import (
    UART_TX_BUF_DWORDS, UART_RX_BUF_DWORDS,
    UART_MAX_STREAMS, UART_MAX_MSG_DWORDS, UART_FC_SEQ_MODULO
)


@dataclass
class UARTMessage:
    stream_id: int = 0
    payload: bytes = field(default_factory=bytes)


class UARTStream:
    """One UART stream: bidirectional, credit-based, modulo-2^12 seq."""
    def __init__(self, stream_id: int):
        self.stream_id = stream_id
        self._tx_buf: deque = deque(maxlen=UART_TX_BUF_DWORDS)
        self._rx_buf: deque = deque(maxlen=UART_RX_BUF_DWORDS)
        self._tx_seq = 0
        self._rx_expected = 0
        self._tx_credits = UART_TX_BUF_DWORDS  # peer's rx buffer space
        self._rx_credits = UART_RX_BUF_DWORDS  # our rx buffer space (to send back)

    def send(self, msg: UARTMessage) -> bool:
        n_dw = (len(msg.payload) + 3) // 4
        if self._tx_credits < n_dw:
            return False
        self._tx_buf.append((self._tx_seq, msg))
        self._tx_seq = (self._tx_seq + 1) % UART_FC_SEQ_MODULO
        self._tx_credits -= n_dw
        return True

    def recv(self, msg: UARTMessage, seq: int) -> Optional[UARTMessage]:
        if seq != self._rx_expected:
            return None
        self._rx_expected = (self._rx_expected + 1) % UART_FC_SEQ_MODULO
        self._rx_buf.append(msg)
        n_dw = (len(msg.payload) + 3) // 4
        self._rx_credits -= n_dw
        return msg

    def return_credits(self, n_dw: int):
        self._tx_credits = min(self._tx_credits + n_dw, UART_TX_BUF_DWORDS)
        self._rx_credits = min(self._rx_credits + n_dw, UART_RX_BUF_DWORDS)

    def drain_rx(self) -> List[UARTMessage]:
        msgs = list(self._rx_buf)
        self._rx_buf.clear()
        return msgs


class UARTController:
    """Manages up to 8 UART streams per link."""
    def __init__(self):
        self.streams = {i: UARTStream(i) for i in range(UART_MAX_STREAMS)}

    def get_stream(self, sid: int) -> UARTStream:
        return self.streams[sid]

    def reset_stream(self, sid: int):
        self.streams[sid] = UARTStream(sid)
