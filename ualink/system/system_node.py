"""UALink 200 — System Node (Section 1.2)."""
from typing import List, Optional
from .accelerator import Accelerator


class SystemNode:
    """OS Domain: one or more CPUs + one or more Accelerators."""
    def __init__(self, node_id: int):
        self.node_id = node_id
        self.accelerators: List[Accelerator] = []
        self.virtual_pod_id: Optional[int] = None

    def add_accelerator(self, acc: Accelerator):
        self.accelerators.append(acc)

    def __repr__(self):
        return f"SystemNode(id={self.node_id}, accs={len(self.accelerators)})"
