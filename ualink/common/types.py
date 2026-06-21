"""
UALink 200 Rev 1.0 — Shared Type Definitions
Dataclasses representing all key protocol entities.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from .constants import (
    ReqCmd, RdRspStatus, WrRspStatus, AtomicOpSize, ASI,
    UPLIWriteMsgType, SecurityStream
)


# ── Identifiers ───────────────────────────────────────────────

@dataclass
class AcceleratorID:
    """10-bit Physical Accelerator Identifier."""
    value: int  # 0-1023

    def __post_init__(self):
        assert 0 <= self.value < 1024, f"AccID {self.value} out of range [0,1023]"

    def __int__(self):
        return self.value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, AcceleratorID) and self.value == other.value


@dataclass
class TransactionTag:
    """11-bit Transaction Tag used to pair Requests with Responses."""
    value: int  # 0-2047

    def __post_init__(self):
        assert 0 <= self.value < 2048, f"Tag {self.value} out of range [0,2047]"

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, TransactionTag) and self.value == other.value


# ── Address ───────────────────────────────────────────────────

@dataclass
class PhysicalAddress:
    """57-bit UPLI Request Address (doubleword-aligned, [1:0] = 0)."""
    value: int  # Byte address, must be doubleword-aligned

    def __post_init__(self):
        assert self.value >= 0, "Address must be non-negative"
        assert (self.value & 0x3) == 0, f"Address 0x{self.value:X} not doubleword-aligned"
        assert self.value < (1 << 57), "Address exceeds 57-bit range"

    def boundary_256b(self) -> int:
        """256-byte boundary this address falls in."""
        return self.value & ~0xFF

    def exceeds_256b_boundary(self, length_bytes: int) -> bool:
        """True if [address, address+length) crosses a 256B boundary."""
        end = self.value + length_bytes - 1
        return (self.value & ~0xFF) != (end & ~0xFF)


@dataclass
class NetworkPhysicalAddress:
    """NPA: cross-domain address containing address handle + target AccID."""
    address_handle: int
    target_acc_id: AcceleratorID


@dataclass
class SystemPhysicalAddress:
    """SPA: local domain byte-addressed physical address."""
    value: int


# ── Request Beat ──────────────────────────────────────────────

@dataclass
class RequestBeat:
    """
    Single beat on the UPLI Request Channel.
    Matches Table 2-2 signal fields exactly.
    """
    # Control fields
    valid: bool = False
    port_id: int = 0                        # 2-bit TDM port
    asi: int = ASI.NORMAL                   # 2-bit address space identifier
    auth_tag: int = 0                       # 64-bit authorization tag
    src_acc_id: int = 0                     # 10-bit source accelerator ID
    dst_acc_id: int = 0                     # 10-bit destination accelerator ID
    tag: int = 0                            # 11-bit transaction tag
    num_beats: int = 0                      # 2-bit (actual = num_beats+1)
    addr: int = 0                           # 57-bit address
    cmd: int = ReqCmd.READ                  # 6-bit command
    length: int = 0                         # 6-bit (doublewords - 1)
    attr: int = 0                           # 8-bit request attributes
    metadata: int = 0                       # 8-bit metadata
    vc: int = 0                             # 2-bit virtual channel
    pool: bool = False                      # pool credit flag
    # Parity (computed, not manually set)
    vld_parity: int = 0
    addr_parity: int = 0
    parity: int = 0


@dataclass
class ReadResponseBeat:
    """
    Single beat on the UPLI Read Response/Data Channel.
    Matches Table 2-8 signal fields.
    """
    valid: bool = False
    port_id: int = 0
    auth_tag: int = 0                       # 64-bit
    src_acc_id: int = 0                     # 10-bit (debug, may be 0)
    dst_acc_id: int = 0                     # 10-bit (routing)
    tag: int = 0                            # 11-bit
    num_beats: int = 0                      # 2-bit
    data: bytes = field(default_factory=lambda: bytes(64))  # 512-bit (64 bytes)
    status: int = RdRspStatus.OKAY          # 4-bit
    offset: int = 0                         # 2-bit beat index
    last: bool = False
    data_error: bool = False                # poison indicator
    vc: int = 0
    pool: bool = False
    # Parity
    vld_parity: int = 0
    data_parity: int = 0                    # 8-bit, one per 64 data bits
    parity: int = 0


@dataclass
class WriteResponseBeat:
    """
    Single beat on the UPLI Write Response Channel.
    Matches Table 2-11 signal fields.
    """
    valid: bool = False
    port_id: int = 0
    auth_tag: int = 0                       # 64-bit
    src_acc_id: int = 0                     # 10-bit (debug)
    dst_acc_id: int = 0                     # 10-bit (routing)
    tag: int = 0                            # 11-bit
    status: int = WrRspStatus.OKAY          # 4-bit
    vc: int = 0
    pool: bool = False
    # Parity
    vld_parity: int = 0
    parity: int = 0


@dataclass
class OrigDataBeat:
    """
    Single beat on the UPLI Originator Data Channel.
    Matches Table 2-14 signal fields.
    """
    valid: bool = False
    port_id: int = 0
    data: bytes = field(default_factory=lambda: bytes(64))  # 512-bit (64 bytes)
    byte_enables: int = 0                   # 64-bit mask
    offset: int = 0                         # 2-bit beat index
    last: bool = False
    data_error: bool = False                # poison indicator
    # Parity
    vld_parity: int = 0
    fields_parity: int = 0
    data_parity: int = 0                    # 8-bit


# ── Credit Return ─────────────────────────────────────────────

@dataclass
class CreditReturn:
    """Credit return for one channel and one port."""
    valid: bool = False         # *CreditVld for this port
    pool: bool = False          # Pool (1) or VC (0) credit
    vc: int = 0                 # Virtual channel (when pool=False)
    num: int = 0                # Credits returned = num + 1


# ── High-level Transaction ────────────────────────────────────

@dataclass
class UPLITransaction:
    """
    Complete UPLI Transaction: Request + associated data + Response.
    Used for higher-level simulation.
    """
    cmd: int = ReqCmd.READ
    src_acc_id: AcceleratorID = field(default_factory=lambda: AcceleratorID(0))
    dst_acc_id: AcceleratorID = field(default_factory=lambda: AcceleratorID(1))
    tag: TransactionTag = field(default_factory=lambda: TransactionTag(0))
    addr: PhysicalAddress = field(default_factory=lambda: PhysicalAddress(0))
    length_dw: int = 1                      # doublewords (1 = 4 bytes)
    attr: int = 0xFF                        # all byte enables by default
    metadata: int = 0
    asi: int = ASI.NORMAL
    vc: int = 0
    pool: bool = True
    write_data: Optional[bytes] = None      # for Write/WriteFull/Atomic
    byte_enables: Optional[int] = None     # for Write (None = all 1s for WriteFull)
    op_type: int = 0                        # for Atomics: OpType[4:0]
    op_size: int = AtomicOpSize.BITS_64    # for Atomics
    msg_type: int = UPLIWriteMsgType.NOP   # for UPLI Write Message

    # Response fields (filled after completion)
    rd_status: Optional[int] = None
    wr_status: Optional[int] = None
    response_data: Optional[bytes] = None
    completed: bool = False

    def is_write(self) -> bool:
        return bool(self.cmd & 0x20)

    def is_read(self) -> bool:
        return (self.cmd & 0x30) == 0x00

    def is_atomic(self) -> bool:
        return (self.cmd & 0x30) == 0x30

    def payload_bytes(self) -> int:
        """Actual payload size in bytes."""
        if self.cmd in (ReqCmd.WRITE, ReqCmd.WRITE_FULL):
            return (self.length_dw + 1) * 4
        elif self.cmd == ReqCmd.READ:
            return (self.length_dw + 1) * 4
        return 64  # Atomics / UPLI Write Msg default


# ── DL Replay State ──────────────────────────────────────────

@dataclass
class ReplayState:
    """
    DL link-level replay state per link.
    Mirrors spec Section 6.6.6 variables.
    """
    # Rx flags/counters
    rx_last_seq_calc: int = 0
    rx_bad_crc_count: int = 0
    rx_unexpected_count: int = 0
    rx_replay_limit: int = 50
    rx_ambiguous: bool = False
    rx_replay: bool = False
    rx_replay_ignore_count: int = 0

    # Tx flags/counters
    tx_replay_req_seq_no: int = 0
    tx_replay_req_count: int = 0          # 2-bit countdown
    tx_last_seq: int = 0x1FF             # starts at 511
    tx_replay: bool = False
    tx_first_replay: bool = False
    tx_explicit_count: int = 7           # 3-bit countdown
    tx_ack_counter: int = 0             # 24-bit
    tx_ack_time_out: int = 40_000       # default ~1ms at 200GBASE


# ── Security State ────────────────────────────────────────────

@dataclass
class StreamSecurityState:
    """Per-stream security state for one (port, peer_acc_id) pair."""
    stream: SecurityStream = SecurityStream.REQUEST
    derived_key: bytes = field(default_factory=lambda: bytes(32))
    next_derived_key: bytes = field(default_factory=lambda: bytes(32))
    invocation_field: int = 0           # 32-bit IV counter
    epoch_counter: int = 0             # ≥32-bit epoch counter


@dataclass
class PortSecurityState:
    """Security state for one UALink port TX or RX direction."""
    peer_acc_id: int = 0
    active_master_key: bytes = field(default_factory=lambda: bytes(32))
    alternate_master_key: bytes = field(default_factory=lambda: bytes(32))
    active_key_valid: bool = False
    alternate_key_valid: bool = False
    streams: dict = field(default_factory=dict)  # SecurityStream → StreamSecurityState
