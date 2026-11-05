"""
UALink 2.0 Modular Specification Implementation Package
=========================================================
Implements the 5-pillar modular UALink 2.0 specification architecture:
1. UALink Common Specification 2.0 (UPLI 2.0, TL 2.0, In-Network Compute)
2. UALink 200G DL & PL Specification 2.0 (640B Flit, 200G PAM4)
3. UALink 128G DL & PL Specification 1.0 (128G SerDes lane rate)
4. UALink Chiplet Specification 1.01 (UCIe 3.0 D2D streaming)
5. UALink Manageability Specification 1.0 (Pod Controller, VPod, Telemetry)
"""

from .common_v2 import (
    ReqCmd, INCOpCode, INCDataType, INCRoundingMode, TransportType, RspStatus,
    UPLIRequest, UPLIResponse, INCOperation,
    INCEngine, INCCollectiveCoordinator,
    ITransportLayer, UPLI2Interface, TL2Flit, TransactionLayer2
)
from .phy_dl_200g import DL200GTransport, DL_FLIT_BYTES_200G
from .phy_dl_128g import DL128GTransport, DL_FLIT_BYTES_128G
from .chiplet import UCIeChipletAdapter, CHIPLET_FLIT_BYTES
from .manageability import PodControllerV2, NodeTelemetry
from .switch_v2 import SwitchCoreV2

__version__ = "2.0.0"
__all__ = [
    "ReqCmd", "INCOpCode", "INCDataType", "TransportType", "RspStatus",
    "UPLIRequest", "UPLIResponse", "INCOperation",
    "INCEngine", "INCCollectiveCoordinator",
    "ITransportLayer", "UPLI2Interface", "TL2Flit", "TransactionLayer2",
    "DL200GTransport", "DL_FLIT_BYTES_200G",
    "DL128GTransport", "DL_FLIT_BYTES_128G",
    "UCIeChipletAdapter", "CHIPLET_FLIT_BYTES",
    "PodControllerV2", "NodeTelemetry",
    "SwitchCoreV2"
]
