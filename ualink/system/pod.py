"""UALink 200 — Pod and VirtualPod (Section 1.1)."""
from typing import List, Dict, Set, Optional
from .system_node import SystemNode
from .accelerator import Accelerator


class VirtualPod:
    """Non-overlapping subset of Pod Accelerators for one tenant."""
    def __init__(self, vpod_id: int):
        self.vpod_id = vpod_id
        self.acc_ids: Set[int] = set()
        self.security_settings: dict = {}

    def add(self, acc_id: int):
        self.acc_ids.add(acc_id)

    def remove(self, acc_id: int):
        self.acc_ids.discard(acc_id)

    def __contains__(self, acc_id: int):
        return acc_id in self.acc_ids

    def __repr__(self):
        return f"VirtualPod(id={self.vpod_id}, accs={sorted(self.acc_ids)})"


class Pod:
    """
    Physical Pod: all Accelerators connected via UALink Switches.
    Max 1024 Accelerators. Spec: Section 1.1.
    """
    def __init__(self):
        self.nodes: List[SystemNode] = []
        self._acc_map: Dict[int, Accelerator] = {}
        self.virtual_pods: Dict[int, VirtualPod] = {}
        self._vpod_counter = 0

    def add_node(self, node: SystemNode):
        self.nodes.append(node)
        for acc in node.accelerators:
            assert acc.acc_id not in self._acc_map, f"Duplicate AccID {acc.acc_id}"
            assert len(self._acc_map) < 1024, "Pod full (max 1024 Accelerators)"
            self._acc_map[acc.acc_id] = acc

    def get_acc(self, acc_id: int) -> Optional[Accelerator]:
        return self._acc_map.get(acc_id)

    @property
    def all_acc_ids(self) -> List[int]:
        return sorted(self._acc_map.keys())

    def create_virtual_pod(self, acc_ids: List[int]) -> VirtualPod:
        for aid in acc_ids:
            for vp in self.virtual_pods.values():
                assert aid not in vp, f"AccID {aid} already in VirtualPod {vp.vpod_id}"
        vp = VirtualPod(self._vpod_counter)
        self._vpod_counter += 1
        for aid in acc_ids:
            vp.add(aid)
            if aid in self._acc_map:
                self._acc_map[aid].virtual_pod_id = vp.vpod_id
        self.virtual_pods[vp.vpod_id] = vp
        return vp

    def destroy_virtual_pod(self, vpod_id: int):
        vp = self.virtual_pods.pop(vpod_id, None)
        if vp:
            for aid in vp.acc_ids:
                if aid in self._acc_map:
                    self._acc_map[aid].virtual_pod_id = None

    def __repr__(self):
        return f"Pod(nodes={len(self.nodes)}, accs={len(self._acc_map)}, vpods={len(self.virtual_pods)})"
