"""UALink 200 — UPLI Interface: 4 channels + handshake + flow control."""
from typing import Optional, List, Callable
from .request_channel import RequestChannel
from .read_response_channel import ReadResponseChannel
from .write_response_channel import WriteResponseChannel
from .originator_data_channel import OriginatorDataChannel
from .credit_manager import CreditManager
from .ordering import OrderingTracker
from ..common.constants import OrderingMode, ReqCmd, WrRspStatus
from ..common.parity import even_parity
from ..common.logger import log


class UPLIInterface:
    """
    UPLI point-to-point interface between Originator and Completer.
    Implements: channels, credits, ordering, handshake, parity checking.
    Spec: Chapter 2 (UPLI Interface Definition).
    """

    def __init__(self, port_id: int = 0, mode: OrderingMode = OrderingMode.RELAXED):
        self.port_id = port_id
        self.connected = False
        self.handshake_done = False
        self.credits = CreditManager()
        self.req_credit_init_done = False
        self.rdrsp_credit_init_done = False
        self.wrrsp_credit_init_done = False
        self.ordering = OrderingTracker(mode)
        self._pending: dict = {}  # tag → transaction context
        self._req_q: List[RequestChannel] = []
        self._rdrsp_q: List[ReadResponseChannel] = []
        self._wrrsp_q: List[WriteResponseChannel] = []
        self._origdata_q: List[OriginatorDataChannel] = []
        self.isolation_mode = False
        self._on_request: Optional[Callable] = None
        self._on_rdrsp: Optional[Callable] = None
        self._on_wrrsp: Optional[Callable] = None
        self._on_vdm: Optional[Callable] = None

    def connect(self):
        """Complete UPLI connection handshake (Section 4)."""
        self.connected = True
        self.handshake_done = True
        self.credits.init_credits()
        self.req_credit_init_done = True
        self.rdrsp_credit_init_done = True
        self.wrrsp_credit_init_done = True
        log.debug(f"UPLI Port {self.port_id} connected")

    def set_handler(self, on_request=None, on_rdrsp=None, on_wrrsp=None, on_vdm=None):
        self._on_request = on_request
        self._on_rdrsp   = on_rdrsp
        self._on_wrrsp   = on_wrrsp
        self._on_vdm     = on_vdm

    def send_request(self, req: RequestChannel,
                     data_beats: Optional[List[OriginatorDataChannel]] = None) -> bool:
        assert self.handshake_done, "Handshake not complete"
        assert not self.isolation_mode, "Interface in isolation mode"
        nb = len(data_beats) if data_beats else 0
        if not self.credits.can_issue_request(req.pool, req.vc, nb):
            return False
        req.compute_parity()
        self.credits.issue_request(req.pool, req.vc, nb)
        self.ordering.enqueue(req.src_acc_id, req.dst_acc_id, req.addr, req.vc, req.tag)
        self._req_q.append(req)
        if data_beats:
            for beat in data_beats:
                beat.compute_parity()
                self._origdata_q.append(beat)
                
        is_vdm = (req.cmd >= 0x08 and req.cmd <= 0x0F) or (req.cmd >= 0x2C and req.cmd <= 0x2F) or (req.cmd >= 0x3C and req.cmd <= 0x3F)
        if is_vdm and self._on_vdm:
            self._on_vdm(req, data_beats)
            log.info(f"UPLI Port {self.port_id} routed Vendor Defined Message: cmd={req.cmd}")
        elif self._on_request:
            self._on_request(req, data_beats)
            
        log.info(f"UPLI Port {self.port_id} sent Request: cmd={req.cmd} addr={req.addr}")
        return True

    def recv_read_response(self, rsp: ReadResponseChannel):
        assert self.handshake_done
        rsp.compute_parity()
        self._rdrsp_q.append(rsp)
        if rsp.last:
            self.credits.return_rdrsp_credit(rsp.pool, rsp.vc)
        if self._on_rdrsp:
            self._on_rdrsp(rsp)
        log.info(f"UPLI Port {self.port_id} recv ReadResponse: tag={rsp.tag}")

    def recv_write_response(self, rsp: WriteResponseChannel):
        assert self.handshake_done
        rsp.compute_parity()
        if rsp.is_isolate():
            self.isolation_mode = True
        self._wrrsp_q.append(rsp)
        self.credits.return_wrrsp_credit(rsp.pool, rsp.vc)
        if self._on_wrrsp:
            self._on_wrrsp(rsp)
        log.info(f"UPLI Port {self.port_id} recv WriteResponse: tag={rsp.tag} status={rsp.status}")

    def return_req_credit(self, pool: bool, vc: int = 0, num: int = 1):
        self.credits.return_req_credit(pool, vc, num)

    def return_rsp_data_credit(self, pool: bool, vc: int = 0, num: int = 1):
        self.credits.return_rsp_data_credit(pool, vc, num)

    def drain_requests(self) -> List[RequestChannel]:
        reqs = list(self._req_q)
        self._req_q.clear()
        for r in reqs:
            log.debug(f"UPLI Port {self.port_id} drain Req: tag={r.tag} cmd={r.cmd} addr={r.addr}")
        return reqs

    def drain_data(self) -> List[OriginatorDataChannel]:
        data = list(self._origdata_q)
        self._origdata_q.clear()
        for d in data:
            log.debug(f"UPLI Port {self.port_id} drain Data: tag={d.tag} sz={len(d.data_payload)}B")
        return data
