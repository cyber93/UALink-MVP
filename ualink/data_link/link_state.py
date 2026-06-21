"""UALink 200 — DL Link State Machine (Section 6.7, Fig 6-23)."""
from enum import IntEnum
from ..common.constants import DLLinkState


class DLStateMachine:
    """
    DL Link State: Fault → Idle → NOP → Up.
    Spec: Section 6.7.1, Fig 6-23.
    """
    def __init__(self):
        self.state = DLLinkState.FAULT
        self._nop_sent  = 0
        self._nop_rcvd_consecutive = 0
        self._ctrl_rcvd_consecutive = 0
        self._enabled   = False

    def rs_fault(self):
        self.state = DLLinkState.FAULT
        self._nop_sent = 0
        self._nop_rcvd_consecutive = 0
        self._ctrl_rcvd_consecutive = 0

    def rs_no_fault(self):
        if self.state == DLLinkState.FAULT:
            self.state = DLLinkState.IDLE

    def enable(self):
        if self.state == DLLinkState.IDLE:
            self._enabled = True
            self.state = DLLinkState.NOP

    def on_nop_sent(self):
        if self.state == DLLinkState.NOP:
            self._nop_sent += 1

    def on_flit_received(self, is_data: bool):
        if self.state == DLLinkState.NOP:
            if self._nop_sent >= 10:
                self._nop_rcvd_consecutive += 1
                if self._nop_rcvd_consecutive >= 2:
                    self.state = DLLinkState.UP
        elif self.state == DLLinkState.UP:
            if not is_data:
                self._ctrl_rcvd_consecutive += 1
                if self._ctrl_rcvd_consecutive >= 4:
                    self.state = DLLinkState.IDLE
            else:
                self._ctrl_rcvd_consecutive = 0

    def error_containment(self):
        if self.state == DLLinkState.UP:
            self.state = DLLinkState.IDLE

    def ack_timeout(self):
        if self.state == DLLinkState.UP:
            self.state = DLLinkState.IDLE

    @property
    def is_up(self) -> bool:
        return self.state == DLLinkState.UP

    @property
    def can_send_payload(self) -> bool:
        return self.state == DLLinkState.UP

    @property
    def can_send_nop(self) -> bool:
        return self.state in (DLLinkState.NOP, DLLinkState.UP)

    def __repr__(self):
        return f"DLStateMachine(state={self.state.name})"
