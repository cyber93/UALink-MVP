"""
UALink 2.0 Switch Core with In-Network Compute (INC) Reduction Support
Combines stateless forwarding, VirtualPod isolation, and hardware-accelerated
collective reduction aggregators.
"""
from typing import Dict, List, Optional
from ..common_v2.types import UPLIRequest, INCOperation
from ..common_v2.constants import ReqCmd
from ..common_v2.in_network_compute import INCCollectiveCoordinator
from ..manageability.pod_controller_v2 import PodControllerV2

class SwitchCoreV2:
    """UALink 2.0 Switch Core supporting both standard routing and In-Network Compute."""

    def __init__(self, ports_count: int = 64, controller: Optional[PodControllerV2] = None):
        self.ports_count = ports_count
        self.routing_table: Dict[int, int] = {}       # AccID -> Egress Port
        self.controller = controller or PodControllerV2()
        self.active_collectives: Dict[int, INCCollectiveCoordinator] = {}

    def set_route(self, acc_id: int, egress_port: int):
        self.routing_table[acc_id] = egress_port

    def register_collective(self, collective_id: int, expected_peers: List[int], op: INCOperation):
        """Initializes an in-switch collective reduction session."""
        self.active_collectives[collective_id] = INCCollectiveCoordinator(
            collective_id=collective_id,
            expected_peers=expected_peers,
            op=op
        )

    def process_request(self, req: UPLIRequest) -> Optional[int]:
        """
        Routes a standard request or handles an in-network collective request.
        Returns egress port index, or -1 if handled in-network, or None if dropped.
        """
        # 1. Virtual Pod Security Check
        if not self.controller.is_communication_allowed(req.src_id, req.dst_id):
            return None  # Dropped due to isolation violation

        # 2. Check if this is an In-Network Compute (INC) collective primitive
        if req.cmd in (ReqCmd.READ_REDUCE, ReqCmd.WRITE_MULTICAST, ReqCmd.WRITE_FULL_MULTICAST) and req.inc_op:
            coll_id = req.inc_op.collective_id
            if coll_id in self.active_collectives:
                coord = self.active_collectives[coll_id]
                done = coord.contribute(req.src_id, req.inc_op.payload)
                self.controller.record_telemetry(req.src_id, inc_ops=1)
                if done:
                    # Collective complete! Switch now holds reduced result
                    return -1  # Handled inside switch
                return -2      # Pending other peers

        # 3. Standard Stateless Forwarding
        egress_port = self.routing_table.get(req.dst_id)
        if egress_port is not None:
            self.controller.record_telemetry(req.src_id, flits_sent=1)
        return egress_port
