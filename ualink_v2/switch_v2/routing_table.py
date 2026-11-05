"""
UALink 2.0 Switch — Routing Table (Chapter 10)
"""
from typing import Dict

class SwitchRoutingTable:
    def __init__(self):
        self.routes: Dict[int, int] = {}  # AccID -> Egress Port Index

    def set_route(self, acc_id: int, port_idx: int):
        self.routes[acc_id] = port_idx

    def lookup(self, acc_id: int) -> int:
        return self.routes.get(acc_id, -1)
