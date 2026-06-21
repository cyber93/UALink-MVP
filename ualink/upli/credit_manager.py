"""UALink 200 — Credit Manager: pool + per-VC credits, 4 ports."""
from dataclasses import dataclass, field
from typing import Dict
from ..common.logger import log


@dataclass
class ChannelCredits:
    pool_credits: int = 0
    vc_credits: Dict[int, int] = field(default_factory=lambda: {0:0,1:0,2:0,3:0})
    init_done: bool = False

    def add_pool(self, n: int):
        self.pool_credits += n

    def add_vc(self, vc: int, n: int):
        self.vc_credits[vc] = self.vc_credits.get(vc, 0) + n

    def consume(self, pool: bool, vc: int = 0) -> bool:
        if pool:
            if self.pool_credits > 0:
                self.pool_credits -= 1
                log.debug(f"Credit consumed: pool (rem: {self.pool_credits})")
                return True
            return False
        else:
            if self.vc_credits.get(vc, 0) > 0:
                self.vc_credits[vc] -= 1
                log.debug(f"Credit consumed: VC {vc} (rem: {self.vc_credits[vc]})")
                return True
            return False

    def return_credit(self, pool: bool, vc: int = 0, num: int = 1):
        if pool:
            self.pool_credits += num
            log.debug(f"Credit returned: pool +{num} (total: {self.pool_credits})")
        else:
            self.vc_credits[vc] = self.vc_credits.get(vc, 0) + num
            log.debug(f"Credit returned: VC {vc} +{num} (total: {self.vc_credits[vc]})")


class CreditManager:
    """
    Per-UPLI-interface credit manager.
    Tracks: Req CMD, Rsp CMD, Req Data, Rsp Data credits.
    Spec: Section 2.8 (UPLI Flow Control).
    """
    def __init__(self):
        self.req_cmd   = ChannelCredits()
        self.rdrsp_cmd = ChannelCredits()
        self.wrrsp_cmd = ChannelCredits()
        self.req_data  = ChannelCredits()
        self.rsp_data  = ChannelCredits()
        self.shared_data_buf = False

    def init_credits(self, req_cmd=8, rdrsp_cmd=8, wrrsp_cmd=8,
                     req_data=20, rsp_data=20, shared=False):
        self.req_cmd.pool_credits   = req_cmd
        self.rdrsp_cmd.pool_credits = rdrsp_cmd
        self.wrrsp_cmd.pool_credits = wrrsp_cmd
        self.req_data.pool_credits  = req_data
        self.rsp_data.pool_credits  = rsp_data
        self.shared_data_buf = shared
        self.req_cmd.init_done   = True
        self.rdrsp_cmd.init_done = True
        self.wrrsp_cmd.init_done = True
        self.req_data.init_done  = True
        self.rsp_data.init_done  = True

    def can_issue_request(self, pool=True, vc=0, data_beats=0) -> bool:
        has_cmd  = self.req_cmd.pool_credits > 0 if pool else self.req_cmd.vc_credits.get(vc,0) > 0
        has_data = True
        if data_beats > 0:
            avail = self.req_data.pool_credits if pool else self.req_data.vc_credits.get(vc,0)
            if self.shared_data_buf:
                avail += self.rsp_data.pool_credits
            has_data = avail >= data_beats
        return has_cmd and has_data

    def issue_request(self, pool=True, vc=0, data_beats=0):
        self.req_cmd.consume(pool, vc)
        for _ in range(data_beats):
            if not self.req_data.consume(pool, vc):
                if self.shared_data_buf:
                    self.rsp_data.consume(pool, vc)

    def return_req_credit(self, pool=True, vc=0, num=1):
        self.req_cmd.return_credit(pool, vc, num)

    def return_req_data_credit(self, pool=True, vc=0, num=1):
        self.req_data.return_credit(pool, vc, num)

    def return_rdrsp_credit(self, pool=True, vc=0, num=1):
        self.rdrsp_cmd.return_credit(pool, vc, num)

    def return_rsp_data_credit(self, pool=True, vc=0, num=1):
        self.rsp_data.return_credit(pool, vc, num)

    def return_wrrsp_credit(self, pool=True, vc=0, num=1):
        self.wrrsp_cmd.return_credit(pool, vc, num)
