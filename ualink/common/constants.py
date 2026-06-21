"""
UALink 200 Rev 1.0 — Global Constants
Source: UALink_200 Rev 1.0 Specification
"""
from enum import IntEnum, auto

# ── System limits ──────────────────────────────────────────────
MAX_ACCELERATORS       = 1024   # 10-bit AcceleratorID space
MAX_PORTS_PER_STATION  = 4      # x1/x2/x4 bifurcation
MAX_LANES_PER_STATION  = 4
MAX_TAG_VALUE          = 2047   # 11-bit ReqTag
MAX_VIRTUAL_CHANNELS   = 4      # 2-bit VC field
MAX_BEATS              = 4      # Max data beats per transaction
MAX_BYTES_PER_REQ      = 256    # Max read/write payload bytes
BOUNDARY_256B          = 256    # Requests may not cross 256B boundary
BOUNDARY_64B           = 64     # 64-byte beat size

# ── Bit widths (UPLI signal sizes from Tables 2-2, 2-8, 2-11, 2-14) ──
BITS_ACC_ID            = 10     # ReqSrcPhysAccID, ReqDstPhysAccID
BITS_TAG               = 11     # ReqTag, RdRspTag, WrRspTag
BITS_CMD               = 6      # ReqCmd
BITS_LEN               = 6      # ReqLen (doublewords - 1)
BITS_ATTR              = 8      # ReqAttr
BITS_METADATA          = 8      # ReqMetaData
BITS_ASI               = 2      # ReqASI
BITS_VC                = 2      # ReqVC, RdRspVC, WrRspVC
BITS_ADDR              = 57     # ReqAddr
BITS_AUTH_TAG          = 64     # ReqAuthTag, RdRspAuthTag, WrRspAuthTag
BITS_DATA              = 512    # 64 bytes per beat
BITS_BYTE_EN           = 64     # OrigDataByteEn
BITS_PORT_ID           = 2      # ReqPortID (TDM cycle)
BITS_NUM_BEATS         = 2      # ReqNumBeats, RdRspNumBeats
BITS_OFFSET            = 2      # RdRspOffset, OrigDataOffset
BITS_RD_STATUS         = 4      # RdRspStatus
BITS_WR_STATUS         = 4      # WrRspStatus

# ── ReqCmd encodings (Table 2-6) ──────────────────────────────
class ReqCmd(IntEnum):
    # Read class (ReqCmd[5:4] = 00)
    READ          = 0x03  # 00 0011b
    # Vendor Defined Read class
    VDC_READ_LO   = 0x08  # 00 1000b
    VDC_READ_HI   = 0x0F  # 00 1111b
    # Write class (ReqCmd[5:4] = 10)
    WRITE         = 0x28  # 10 1000b
    WRITE_FULL    = 0x29  # 10 1001b
    UPLI_WRITE_MSG= 0x2A  # 10 1010b
    # Vendor Defined Write class
    VDC_WRITE_LO  = 0x2C  # 10 1100b
    VDC_WRITE_HI  = 0x2F  # 10 1111b
    # Atomic class (ReqCmd[5:4] = 11)
    ATOMIC_R      = 0x30  # 11 0000b
    ATOMIC_NR     = 0x32  # 11 0010b
    # Vendor Defined Atomic class
    VDC_ATOMIC_LO = 0x3C  # 11 1100b
    VDC_ATOMIC_HI = 0x3F  # 11 1111b

def is_write_class(cmd: int) -> bool:
    """ReqCmd[5] = 1 → uses OrigData channel."""
    return bool(cmd & 0x20)

def is_read_class(cmd: int) -> bool:
    return (cmd & 0x30) == 0x00

def is_atomic_class(cmd: int) -> bool:
    return (cmd & 0x30) == 0x30

def is_vdc(cmd: int) -> bool:
    """Vendor Defined Command check."""
    return (
        (0x08 <= cmd <= 0x0F) or
        (0x2C <= cmd <= 0x2F) or
        (0x3C <= cmd <= 0x3F)
    )

# ── ReqMetaData: UPLI Write Message types (Table 2-7) ─────────
class UPLIWriteMsgType(IntEnum):
    NOP                    = 0x00
    KEY_ROLL_REQ_CHANNEL   = 0x01
    KEY_ROLL_RDRSP_CHANNEL = 0x02
    KEY_ROLL_WRRSP_CHANNEL = 0x03
    # 0x04-0xEF Reserved
    VDC_WRITE_MSG_LO       = 0xF0
    VDC_WRITE_MSG_HI       = 0xFF

# ── RdRspStatus encodings (Table 2-9) ─────────────────────────
class RdRspStatus(IntEnum):
    OKAY               = 0b0000
    TARGET_ABORT       = 0b0010
    DECODE_ERROR       = 0b0011
    PROTECTION_VIOLATION = 0b0110
    CMPLT_TIMEOUT      = 0b1000

# ── WrRspStatus encodings (Table 2-12) ────────────────────────
class WrRspStatus(IntEnum):
    OKAY               = 0b0000
    TARGET_ABORT       = 0b0010
    DECODE_ERROR       = 0b0011
    PROTECTION_VIOLATION = 0b0110
    CMPLT_TIMEOUT      = 0b1000
    ISOLATE            = 0b1111   # UPLI isolation mode trigger

# ── AtomicR/AtomicNR OpSize encoding (Table 2-5) ──────────────
class AtomicOpSize(IntEnum):
    BITS_32 = 0b00
    BITS_64 = 0b01
    BITS_16 = 0b10
    BITS_8  = 0b11

# ── ASI values ────────────────────────────────────────────────
class ASI(IntEnum):
    NORMAL       = 0b00
    # Others: implementation/vendor defined for VDC/UPLI Write Msg

# ── TL Flit constants (Ch5) ───────────────────────────────────
TL_FLIT_BYTES       = 64    # 64-byte TL Flit
TL_SECTOR_BYTES     = 4     # 1 sector = 4 bytes
TL_SECTORS_PER_FLIT = 16    # 64B / 4B = 16 sectors
TL_HALF_FLIT_BYTES  = 32    # 32-byte half-flit

# TL Field Type encodings (Table 5-27, high 4 bits of control field)
class TLFieldType(IntEnum):
    UNCOMPRESSED_REQ    = 0x4   # 4 sectors
    UNCOMPRESSED_RSP    = 0x2   # 2 sectors
    COMPRESSED_REQ      = 0x6   # 2 sectors
    COMPRESSED_RSP_SB   = 0x8   # 1 sector (single-beat read)
    COMPRESSED_RSP_WR   = 0x9   # 1 sector (write or multi-beat read)
    FLOW_CTRL_NOP       = 0x0   # 1 sector

TL_FIELD_SECTORS = {
    TLFieldType.UNCOMPRESSED_REQ:  4,
    TLFieldType.UNCOMPRESSED_RSP:  2,
    TLFieldType.COMPRESSED_REQ:    2,
    TLFieldType.COMPRESSED_RSP_SB: 1,
    TLFieldType.COMPRESSED_RSP_WR: 1,
    TLFieldType.FLOW_CTRL_NOP:     1,
}

# TL message indicator bits
class TLMessageType(IntEnum):
    CONTROL_HALF_FLIT = 0  # bit=0 → Control Half-Flit
    DATA_HALF_FLIT    = 1  # bit=1 → Data Half-Flit

# ── DL Flit constants (Ch6) ───────────────────────────────────
DL_FLIT_BYTES        = 640   # 640-byte DL Flit
DL_SEGMENT_COUNT     = 5     # 5 segments per DL Flit
DL_SECTOR_BYTES      = 4     # 1 sector = 4 bytes
DL_CRC_BYTES         = 4     # CRC-32
DL_FLIT_HEADER_BYTES = 3     # FH[2:0]
DL_SEG_HEADER_BYTES  = 1     # SH per segment (5 bytes total)

# Segment sector counts (Table 6-1, including headers)
DL_SEG_PAYLOAD_SECTORS = [31, 32, 32, 32, 16]  # payload sectors per segment
DL_TL_PAYLOAD_BYTES = 628    # 640 - 4 CRC - 3 FH - 5 SH = 628 usable bytes

# Replay constants (Ch6)
DL_REPLAY_SEQ_MAX    = 511   # Valid seq: 1-511 (0 reserved)
DL_REPLAY_MAX_UNACK  = 255   # Max unacknowledged flits in TxReplay
DL_REPLAY_REQ_COUNT  = 3     # Send 3 replay requests

# UART constants (Ch6)
UART_TX_BUF_DWORDS   = 128   # Recommended Tx buffer
UART_RX_BUF_DWORDS   = 128   # Recommended Rx buffer
UART_MAX_STREAMS     = 8     # Stream ID field allows 8
UART_MAX_MSG_DWORDS  = 32    # Max UART Stream Transport Message DWords
UART_FC_SEQ_MODULO   = 4096  # 2^12 credit counter

# ── Physical Layer constants (Ch7) ────────────────────────────
RS_BLOCKS_PER_FLIT   = 80    # 80 × 64B/66B blocks = 1 Flit Code Sequence
PCS_CODEWORD_BYTES   = 680   # 640B DL Flit + 40B FEC overhead

class SerialRate(IntEnum):
    G100 = 100   # 100GBASE-KR1/CR1
    G200 = 200   # 200GBASE-KR1/CR1
    G400 = 400   # 400GBASE-KR2/CR2
    G800 = 800   # 800GBASE-KR4/CR4

class LinkWidth(IntEnum):
    X1 = 1
    X2 = 2
    X4 = 4

# Alignment marker intervals (flits) per rate
AM_INTERVAL_FLITS = {
    SerialRate.G100: 4096,
    SerialRate.G200: 4096,
    SerialRate.G400: 8192,
    SerialRate.G800: 16384,
}

# 64B/66B block type constants
BLOCK_TYPE_DATA        = 0b01   # Sync header 01 → data block
BLOCK_TYPE_CONTROL     = 0b10   # Sync header 10 → control block
CTRL_BLOCK_IDLE        = 0x1E   # /I/ idle codes
CTRL_BLOCK_START       = 0x78   # Start of Flit Code Sequence
CTRL_BLOCK_FAULT       = 0x4B   # Sequential ordered set (local/remote fault)

# ── Security constants (Ch9) ──────────────────────────────────
SEC_KEY_BYTES          = 32     # AES-GCM-256 key = 256 bits
SEC_TAG_BYTES          = 8      # Authentication tag = 8 bytes (optional)
SEC_IV_BITS            = 96     # AES-GCM IV = 96 bits
SEC_IV_BYTES           = 12
SEC_INVOCATION_BITS    = 32     # Invocation field within IV
SEC_INVOCATION_MAX     = (1 << 32) - 1   # 2^32 - 1 HW threshold
SEC_EPOCH_BITS_MIN     = 32     # Epoch counter minimum width

class SecurityStream(IntEnum):
    REQUEST        = 0   # Read/Write/Atomic requests + payload
    READ_RESPONSE  = 1   # Read responses + payload, AtomicR payload
    WRITE_RESPONSE = 2   # Write responses

class SecurityMode(IntEnum):
    DISABLED       = 0   # No security
    ENCRYPT_ONLY   = 1   # Encryption enabled
    ENCRYPT_AUTH   = 2   # Encryption + integrity (AES-GCM with tag)

# ── Switch constants (Ch10) ───────────────────────────────────
SWITCH_MAX_PORTS       = MAX_ACCELERATORS  # Switch radix = Pod size

# ── DL Link States (Ch6, Fig 6-23) ───────────────────────────
class DLLinkState(IntEnum):
    FAULT  = 0   # Reset state; link down
    IDLE   = 1   # Link down; Tx Idle
    NOP    = 2   # Link down; Tx NOP flits only
    UP     = 3   # Link up; Tx NOP or payload flits

# ── DL Message types (Table 6-3) ──────────────────────────────
class DLMsgClass(IntEnum):
    BASIC   = 0
    CONTROL = 1
    UART    = 2

class DLMsgType(IntEnum):
    # Basic
    TL_RATE_NOTIFICATION = 0
    DEVICE_ID_REQUEST    = 1
    PORT_ID_REQUEST      = 2
    NO_OP                = 3
    # Control
    CHANNEL_NEGOTIATION  = 0
    # UART
    UART_RESET_REQUEST   = 0
    UART_RESET_RESPONSE  = 1
    UART_TRANSPORT       = 2
    UART_CREDIT_UPDATE   = 3

class DLAckField(IntEnum):
    REQUEST          = 0
    ACK              = 1
    NACK             = 2
    DECISION_PENDING = 3

# ── Ordering ──────────────────────────────────────────────────
class OrderingMode(IntEnum):
    RELAXED = 0   # Per-256B ordering (default)
    STRICT  = 1   # All-ordered (when encryption/auth active)
