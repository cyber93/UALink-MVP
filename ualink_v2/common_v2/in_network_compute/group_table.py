"""
UALink 2.0 In-Network Compute — Group Table (Chapter 6.2.1)
Each port implements a Group Table of up to 1024 entries.
Each entry consists of a Valid bit and a bitmask equal to the Switch radix.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class GroupTableEntry:
    valid: bool = False
    accelerator_mask: int = 0  # Bitmask where bit i = Accelerator with ID i is in group

class PortGroupTable:
    """1024-entry Collective Group Table indexed by GroupID[9:0]."""
    MAX_ENTRIES = 1024

    def __init__(self, port_id: int = 0, switch_radix: int = 64):
        self.port_id = port_id
        self.switch_radix = switch_radix
        self.entries: Dict[int, GroupTableEntry] = {}

    def configure_group(self, group_id: int, member_acc_ids: List[int]) -> bool:
        assert 0 <= group_id < self.MAX_ENTRIES, f"GroupID {group_id} exceeds 1024"
        mask = 0
        for aid in member_acc_ids:
            assert 0 <= aid < self.switch_radix, f"AccID {aid} exceeds switch radix {self.switch_radix}"
            mask |= (1 << aid)

        self.entries[group_id] = GroupTableEntry(valid=True, accelerator_mask=mask)
        return True

    def lookup(self, group_id: int) -> Optional[GroupTableEntry]:
        entry = self.entries.get(group_id)
        if entry and entry.valid:
            return entry
        return None

    def get_members(self, group_id: int) -> List[int]:
        entry = self.lookup(group_id)
        if not entry:
            return []
        return [i for i in range(self.switch_radix) if (entry.accelerator_mask & (1 << i))]
