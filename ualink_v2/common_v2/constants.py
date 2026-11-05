"""
UALink 2.0 Common Specification — Global Constants
Supports: Modular Architecture, Pluggable Transports, In-Network Compute (INC).
"""
from enum import IntEnum, auto

# ── System Limits ────────────────────────────────────────────────────────
MAX_ACCELERATORS       = 1024   # 10-bit AcceleratorID space (0-1023)
MAX_PORTS_PER_STATION  = 4      # x1/x2/x4 bifurcation
MAX_LANES_PER_STATION  = 4
MAX_TAG_VALUE          = 2047   # 11-bit ReqTag
MAX_VIRTUAL_CHANNELS   = 4      # 2-bit VC field (VC0 - VC3)
MAX_BEATS              = 4      # Max 64B data beats per transaction
MAX_BYTES_PER_REQ      = 256    # Max payload bytes
BOUNDARY_256B          = 256
BOUNDARY_64B           = 64

# ── Bit Widths ───────────────────────────────────────────────────────────
BITS_ACC_ID            = 10
BITS_TAG               = 11
BITS_CMD               = 6
BITS_LEN               = 6
BITS_ATTR              = 8
BITS_METADATA          = 8
BITS_ASI               = 2
BITS_VC                = 2
BITS_ADDR              = 57
BITS_AUTH_TAG          = 64
BITS_DATA              = 512    # 64 bytes
BITS_BYTE_EN           = 64
BITS_PORT_ID           = 2

# ── UPLI 2.0 ReqCmd Encodings ────────────────────────────────────────────
class ReqCmd(IntEnum):
    # Read Class (ReqCmd[5:4] = 00)
    READ               = 0x03
    VDC_READ_LO        = 0x08
    VDC_READ_HI        = 0x0F

    # Write Class (ReqCmd[5:4] = 10)
    WRITE              = 0x28
    WRITE_FULL         = 0x29
    UPLI_WRITE_MSG     = 0x2A
    VDC_WRITE_LO       = 0x2C
    VDC_WRITE_HI       = 0x2F

    # Atomic Class (ReqCmd[5:4] = 11)
    ATOMIC_R           = 0x30
    ATOMIC_NR          = 0x32
    VDC_ATOMIC_LO      = 0x3C
    VDC_ATOMIC_HI      = 0x3F

    # In-Network Compute (INC) Collective Primitives (UALink Common Spec 2.0 Ch 6)
    READ_REDUCE        = 0x38  # ReadReduce Collective Primitive
    WRITE_MULTICAST    = 0x39  # WriteMulticast Collective Primitive
    WRITE_FULL_MULTICAST = 0x3A # WriteFullMulticast Collective Primitive
    ATOMIC_NR_MULTICAST = 0x3B # AtomicNRMulticast Collective Primitive

# ── INC Rounding Modes (Ch 6.2.1) ────────────────────────────────────────
class INCRoundingMode(IntEnum):
    ROUND_TO_NEAREST_EVEN = 0b000
    ROUND_TOWARD_ZERO     = 0b001
    ROUND_UP              = 0b010
    ROUND_DOWN            = 0b011
    ROUND_STOCHASTIC      = 0b100

# ── INC Operation Codes (In-Network Compute) ───────────────────────────────
class INCOpCode(IntEnum):
    SUM                = 0x01
    MIN                = 0x02
    MAX                = 0x03
    PROD               = 0x04
    BAND               = 0x05  # Bitwise AND
    BOR                = 0x06  # Bitwise OR
    BXOR               = 0x07  # Bitwise XOR

class INCDataType(IntEnum):
    FP32               = 0x01
    FP16               = 0x02
    BF16               = 0x03
    INT32              = 0x04
    INT16              = 0x05
    INT8               = 0x06

# ── Transport Modes (Pluggable PHY/DL in UALink 2.0) ──────────────────────
class TransportType(IntEnum):
    LINK_200G          = 1   # 200G DL & PL 2.0 (PAM4 106.25GBd, 640B Flit)
    LINK_128G          = 2   # 128G DL & PL 1.0 (SerDes option)
    CHIPLET_UCIE       = 3   # Chiplet UCIe 3.0 D2D streaming

# ── Response Status ──────────────────────────────────────────────────────
class RspStatus(IntEnum):
    OKAY               = 0b0000
    TARGET_ABORT       = 0b0010
    DECODE_ERROR       = 0b0011
    PROTECTION_VIOLATION = 0b0110
    CMPLT_TIMEOUT      = 0b1000
    ISOLATE            = 0b1111

# ── Ordering Modes ───────────────────────────────────────────────────────
class OrderingMode(IntEnum):
    RELAXED            = 0   # 256B region ordering
    STRICT             = 1   # Global strict ordering (Security mode)
