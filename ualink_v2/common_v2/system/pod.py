"""
UALink 2.0 System Model — Pod and Virtual Pod (Chapter 1)
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional

@dataclass
class VirtualPod:
    vpod_id: int
    member_acc_ids: Set[int] = field(default_factory=set)

    def contains(self, acc_id: int) -> bool:
        return acc_id in self.member_acc_ids


class SystemPod:
    """Pod model representing up to 1024 accelerators and interconnect fabric."""
    def __init__(self, pod_id: str = "Pod-0"):
        self.pod_id = pod_id
        self.accelerators: Dict[int, Any] = {}
        self.virtual_pods: Dict[int, VirtualPod] = {}

    def add_accelerator(self, acc):
        self.accelerators[acc.acc_id] = acc

    def add_vpod(self, vpod_id: int, members: List[int]) -> VirtualPod:
        vpod = VirtualPod(vpod_id=vpod_id, member_acc_ids=set(members))
        self.virtual_pods[vpod_id] = vpod
        return vpod
