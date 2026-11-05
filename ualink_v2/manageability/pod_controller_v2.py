"""
UALink Manageability Specification v1.0 — Pod Controller & Enterprise Management
Orchestrates scale-up pod topologies, VirtualPod partitioning,
and telemetry monitoring across multi-node accelerator fabrics.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional

@dataclass
class NodeTelemetry:
    node_id: int
    temperature_c: float = 45.0
    link_errors: int = 0
    flits_tx: int = 0
    flits_rx: int = 0
    inc_operations_count: int = 0

class PodControllerV2:
    """Enterprise Pod Controller implementing UALink Manageability Spec 1.0."""

    def __init__(self, pod_id: str = "Pod-01"):
        self.pod_id = pod_id
        self.registered_nodes: Dict[int, str] = {}  # AccID -> Node name
        self.virtual_pods: Dict[int, Set[int]] = {} # VPodID -> set of AccIDs
        self.telemetry: Dict[int, NodeTelemetry] = {}

    def register_accelerator(self, acc_id: int, name: str) -> bool:
        """Discovers and registers a physical accelerator node."""
        if acc_id in self.registered_nodes:
            return False
        self.registered_nodes[acc_id] = name
        self.telemetry[acc_id] = NodeTelemetry(node_id=acc_id)
        return True

    def create_virtual_pod(self, vpod_id: int, member_acc_ids: List[int]) -> bool:
        """Partitions accelerators into an isolated Virtual Pod (tenant security)."""
        for aid in member_acc_ids:
            if aid not in self.registered_nodes:
                raise ValueError(f"Accelerator {aid} not registered in pod")
        self.virtual_pods[vpod_id] = set(member_acc_ids)
        return True

    def is_communication_allowed(self, src_acc_id: int, dst_acc_id: int) -> bool:
        """Enforces Virtual Pod security boundaries."""
        src_vpod = None
        dst_vpod = None
        for vpid, members in self.virtual_pods.items():
            if src_acc_id in members:
                src_vpod = vpid
            if dst_acc_id in members:
                dst_vpod = vpid

        if src_vpod is not None and dst_vpod is not None:
            return src_vpod == dst_vpod
        # If no VirtualPod restriction, allow pod-wide
        return True

    def record_telemetry(self, acc_id: int, flits_sent: int = 0, inc_ops: int = 0):
        if acc_id in self.telemetry:
            t = self.telemetry[acc_id]
            t.flits_tx += flits_sent
            t.inc_operations_count += inc_ops
