"""
UALink 2.0 Common Specification — Credit Manager (Chapter 2 Flow Control)
"""
from typing import Dict

class ChannelCredits:
    def __init__(self, pool_init: int = 16, vc_init: int = 4):
        self.pool_credits = pool_init
        self.vc_credits: Dict[int, int] = {i: vc_init for i in range(4)}

    def consume(self, vc: int = 0) -> bool:
        if self.pool_credits > 0:
            self.pool_credits -= 1
            return True
        if self.vc_credits.get(vc, 0) > 0:
            self.vc_credits[vc] -= 1
            return True
        return False

    def replenish_pool(self, amount: int = 1):
        self.pool_credits += amount

    def replenish_vc(self, vc: int, amount: int = 1):
        self.vc_credits[vc] = self.vc_credits.get(vc, 0) + amount


class UPLI2CreditManager:
    """Manages flow control credits for all 4 UPLI channels."""
    def __init__(self):
        self.req_cmd = ChannelCredits(pool_init=16, vc_init=4)
        self.req_data = ChannelCredits(pool_init=32, vc_init=8)
        self.rd_rsp = ChannelCredits(pool_init=32, vc_init=8)
        self.wr_rsp = ChannelCredits(pool_init=16, vc_init=4)

    def init_credits(self):
        self.__init__()
