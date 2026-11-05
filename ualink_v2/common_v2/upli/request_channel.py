"""
UALink 2.0 Common Specification — Request Channel (Table 2-2 & Chapter 6 Overloading)
"""
from dataclasses import dataclass
from ..constants import ReqCmd, INCOpCode, INCDataType, INCRoundingMode
from ..parity import even_parity

@dataclass
class RequestChannel:
    """
    UPLI Request Channel signals per Table 2-2 with Chapter 6 INC signal overloading.
    """
    valid: bool = False
    vld_parity: int = 0
    port_id: int = 0          # 2-bit
    cmd: int = ReqCmd.READ     # 6-bit
    addr: int = 0             # 57-bit System Physical Address
    tag: int = 0              # 11-bit Transaction Tag
    len_dw: int = 0           # 6-bit (Length in doublewords - 1)
    attr: int = 0             # 8-bit Byte enables / Atomics Op / Stochastic Seed
    src_acc_id: int = 0       # 10-bit (Overloaded with ReduceOpDataType & RoundingMode for ReadReduce)
    dst_acc_id: int = 0       # 10-bit (Overloaded with GroupID[9:0] for Collective Primitives)
    asi: int = 0              # 2-bit Address Space Indicator
    vc: int = 0               # 2-bit Virtual Channel
    metadata: int = 0         # 8-bit
    auth_tag: int = 0         # 64-bit Authentication Tag (UALinkSec)

    def compute_parity(self):
        """Even parity across all request control signals."""
        accum = (
            (int(self.valid)) ^
            (self.port_id) ^
            (self.cmd) ^
            (self.tag) ^
            (self.len_dw) ^
            (self.attr) ^
            (self.src_acc_id) ^
            (self.dst_acc_id) ^
            (self.asi) ^
            (self.vc) ^
            (self.metadata)
        )
        self.vld_parity = bin(accum).count('1') % 2

    # INC Overloading helper accessors
    @property
    def group_id(self) -> int:
        """ReqDstPhysAccID overloaded as GroupID[9:0] for Collective Primitives (Ch 6.2.1)."""
        return self.dst_acc_id & 0x3FF

    @group_id.setter
    def group_id(self, val: int):
        self.dst_acc_id = val & 0x3FF

    @property
    def reduce_op_data_type(self) -> int:
        """ReqSrcPhysAccID[6:0] overloaded as ReduceOpDataType for ReadReduce."""
        return self.src_acc_id & 0x7F

    @property
    def rounding_mode(self) -> int:
        """ReqSrcPhysAccID[9:7] overloaded as RoundingMode for ReadReduce."""
        return (self.src_acc_id >> 7) & 0x07

    def set_read_reduce_params(self, group_id: int, reduce_op_dtype: int, rounding_mode: int, seed: int = 0):
        """Encodes ReadReduce collective primitive signals according to Chapter 6."""
        self.cmd = ReqCmd.READ_REDUCE
        self.dst_acc_id = group_id & 0x3FF
        self.src_acc_id = (reduce_op_dtype & 0x7F) | ((rounding_mode & 0x07) << 7)
        self.attr = seed & 0xFF
        self.compute_parity()
