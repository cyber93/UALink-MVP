"""
UALink 2.0 Switch Package
"""
from .switch_core_v2 import SwitchCoreV2
from .routing_table import SwitchRoutingTable
from .port import SwitchPort2

__all__ = ["SwitchCoreV2", "SwitchRoutingTable", "SwitchPort2"]
