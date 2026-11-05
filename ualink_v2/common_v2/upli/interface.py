"""
UALink 2.0 Common Specification — UPLI Interface
Spec: Chapter 2 (UPLI Interface Definition and Operation Rules)
"""
from typing import Optional, List, Callable
from .request_channel import RequestChannel
from .read_response_channel import ReadResponseChannel
from .write_response_channel import WriteResponseChannel
from .originator_data_channel import OriginatorDataChannel
from .credit_manager import UPLI2CreditManager
from .ordering import OrderingTracker
from ..constants import OrderingMode

class UPLIInterface2:
    """Full point-to-point UPLI 2.0 Originator/Completer Interface."""

    def __init__(self, port_id: int = 0, mode: OrderingMode = OrderingMode.RELAXED):
        self.port_id = port_id
        self.connected = False
        self.credits = UPLI2CreditManager()
        self.ordering = OrderingTracker(mode)
        self.isolation_mode = False

        self._req_q: List[RequestChannel] = []
        self._rdrsp_q: List[ReadResponseChannel] = []
        self._wrrsp_q: List[WriteResponseChannel] = []
        self._origdata_q: List[OriginatorDataChannel] = []

        self._on_request: Optional[Callable] = None
        self._on_rdrsp: Optional[Callable] = None
        self._on_wrrsp: Optional[Callable] = None

    def connect(self):
        self.connected = True
        self.credits.init_credits()

    def send_request(self, req: RequestChannel, data_beats: Optional[List[OriginatorDataChannel]] = None) -> bool:
        assert self.connected, "UPLI not connected"
        if not self.credits.req_cmd.consume(req.vc):
            return False

        req.compute_parity()
        self._req_q.append(req)
        self.ordering.enqueue(req.tag, req.addr)

        if data_beats:
            for beat in data_beats:
                beat.compute_parity()
                self._origdata_q.append(beat)

        if self._on_request:
            self._on_request(req)
        return True

    def drain_requests(self) -> List[RequestChannel]:
        reqs = list(self._req_q)
        self._req_q.clear()
        return reqs
