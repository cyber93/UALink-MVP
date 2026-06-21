from .routing_table import RoutingTable
from .port import SwitchPort
from .virtual_pod_partition import VPodPartition
from ..common.logger import log

class SwitchCore:
    def __init__(self, ports: int=64):
        self.ports = {i: SwitchPort(i) for i in range(ports)}
        self.rt = RoutingTable()
        self.vpods = {}
        self.port_to_vpod = {}

    def assign_vpod(self, port_idx: int, vpod_id: int):
        if vpod_id not in self.vpods:
            self.vpods[vpod_id] = VPodPartition(vpod_id)
        self.vpods[vpod_id].ports.add(port_idx)
        self.port_to_vpod[port_idx] = vpod_id

    def forward(self, req, in_port_idx: int = -1):
        p = self.rt.lookup(req.dst_acc_id)
        if p != -1: 
            src_vpod = self.port_to_vpod.get(in_port_idx)
            dst_vpod = self.port_to_vpod.get(p)
            if src_vpod is not None and dst_vpod is not None and src_vpod != dst_vpod:
                log.warning(f"Switch drop req: cross-vPod violation (Acc={req.src_acc_id}->Acc={req.dst_acc_id})")
                return None
            log.info(f"Switch forward req to Acc={req.dst_acc_id} via Port={p}")
            return self.ports[p]
        log.warning(f"Switch drop req to Acc={req.dst_acc_id} (No route)")
        return None
