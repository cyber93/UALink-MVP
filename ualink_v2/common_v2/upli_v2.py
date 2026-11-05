"""
UALink 2.0 Common Specification — UPLI 2.0 Interface
Implements 4 core channels + In-Network Compute collective requests.
"""
from typing import Optional, List, Dict, Callable
from .constants import ReqCmd, RspStatus, OrderingMode
from .types import UPLIRequest, UPLIResponse, INCOperation
from .in_network_compute import INCEngine, INCCollectiveCoordinator

class CreditTracker:
    def __init__(self, initial_pool: int = 16):
        self.pool = initial_pool
        self.initial = initial_pool

    def consume(self, amount: int = 1) -> bool:
        if self.pool >= amount:
            self.pool -= amount
            return True
        return False

    def replenish(self, amount: int = 1):
        self.pool = min(self.initial * 2, self.pool + amount)


class UPLI2Interface:
    """UALink Protocol Level Interface 2.0 with INC support."""

    def __init__(self, port_id: int = 0):
        self.port_id = port_id
        self.credits_req = CreditTracker(16)
        self.credits_data = CreditTracker(32)
        self.connected = False
        self._pending_reqs: List[UPLIRequest] = []
        self._on_response: Optional[Callable[[UPLIResponse], None]] = None

    def connect(self):
        self.connected = True

    def submit_request(self, req: UPLIRequest) -> bool:
        assert self.connected, "UPLI 2.0 not connected"
        if not self.credits_req.consume(1):
            return False
        self._pending_reqs.append(req)
        return True

    def drain_requests(self) -> List[UPLIRequest]:
        reqs = list(self._pending_reqs)
        self._pending_reqs.clear()
        return reqs

    def return_credit(self, amount: int = 1):
        self.credits_req.replenish(amount)
