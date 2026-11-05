"""
UALink 2.0 Common Specification — Shared Types and Data Structures
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any
from .constants import ReqCmd, INCOpCode, INCDataType, INCRoundingMode, RspStatus, TransportType

@dataclass
class AcceleratorID:
    val: int  # 0 - 1023 (10-bit)
    def __post_init__(self):
        assert 0 <= self.val < 1024, f"AccID out of range: {self.val}"

@dataclass
class Tag:
    val: int  # 0 - 2047 (11-bit)
    def __post_init__(self):
        assert 0 <= self.val < 2048, f"Tag out of range: {self.val}"

@dataclass
class Address:
    val: int  # 57-bit System Physical Address
    def __post_init__(self):
        assert 0 <= self.val < (1 << 57), f"Address out of range: {self.val}"

@dataclass
class INCOperation:
    """In-Network Compute collective reduction descriptor (Ch 6)."""
    opcode: INCOpCode
    dtype: INCDataType
    vector_len: int           # Number of elements in vector
    collective_id: int        # Identifies collective group / barrier
    rounding_mode: INCRoundingMode = INCRoundingMode.ROUND_TO_NEAREST_EVEN
    stochastic_seed: int = 0  # 8-bit seed conveyed in ReqAttr
    payload: bytes = b''      # Vector data in binary format

@dataclass
class UPLIRequest:
    src_id: int
    dst_id: int
    cmd: ReqCmd
    addr: int = 0
    tag: int = 0
    len_dw: int = 0           # Length in DWords minus 1
    data: bytes = b''
    inc_op: Optional[INCOperation] = None
    vld_parity: int = 0

@dataclass
class UPLIResponse:
    src_id: int
    dst_id: int
    tag: int
    status: RspStatus = RspStatus.OKAY
    data: bytes = b''
    inc_result: Optional[bytes] = None
