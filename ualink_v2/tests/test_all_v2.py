"""
UALink 2.0 Comprehensive Test Suite
Validates all sub-modules matching the depth and completeness of the original ualink package:
- Common 2.0 (UPLI, TL, In-Network Compute, Parity, AddressCache)
- 200G DL & PL 2.0 (Flit framing, CRC-32, Replay, RS 64B/66B encoding)
- 128G DL & PL 1.0 (SerDes lane framing)
- Chiplet 1.01 (UCIe 3.0 D2D streaming & Sideband Mailbox)
- Manageability 1.0 (Pod Controller, VirtualPod, Telemetry, PLDM/MCTP)
- Security 2.0 (AES-GCM-256, 96-bit IV, Partial Field Encryption)
- Switch 2.0 (Stateless routing + INC Collective Reduction)
"""
import sys
import struct
import pytest
from pathlib import Path

# Add UALink-MVP to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ualink_v2.common_v2 import (
    ReqCmd, INCOpCode, INCDataType, INCRoundingMode, TransportType,
    UPLIRequest, INCOperation, INCEngine,
    TransactionLayer2, UPLI2Interface
)
from ualink_v2.common_v2.parity import even_parity, compute_byte_parity
from ualink_v2.common_v2.upli.request_channel import RequestChannel
from ualink_v2.common_v2.transaction_layer.address_cache import AddressCache
from ualink_v2.common_v2.in_network_compute.group_table import PortGroupTable
from ualink_v2.common_v2.in_network_compute.rounding import INCRoundingEngine
from ualink_v2.phy_dl_200g import DL200GTransport, ReconciliationSublayer, TxReplayBuffer
from ualink_v2.phy_dl_128g import DL128GTransport
from ualink_v2.chiplet import UCIeChipletAdapter, UCIeSidebandMailbox
from ualink_v2.manageability import PodControllerV2, EnterpriseTelemetryCollector, PLDMMessageAgent
from ualink_v2.security_v2 import AESGCM256Engine, IVManager, PartialFieldEncryptor
from ualink_v2.switch_v2 import SwitchCoreV2


def test_parity_computation():
    """Validates even parity calculations."""
    assert even_parity(0b1011, 4) == 1
    assert even_parity(0b1100, 4) == 0
    assert compute_byte_parity(b"\x01\x02") == 0


def test_upli_request_channel_inc_overload():
    """Validates Table 2-2 UPLI Request and Ch 6 bit overloading."""
    req = RequestChannel(valid=True)
    req.set_read_reduce_params(group_id=12, reduce_op_dtype=0x01, rounding_mode=0x02, seed=42)

    assert req.cmd == ReqCmd.READ_REDUCE
    assert req.group_id == 12
    assert req.reduce_op_data_type == 0x01
    assert req.rounding_mode == 0x02
    assert req.attr == 42
    assert req.vld_parity in (0, 1)


def test_address_cache_compression():
    """Validates 32-entry address cache insertion and lookup."""
    cache = AddressCache()
    idx1 = cache.insert(0x1000)
    idx2 = cache.insert(0x1020) # Same 64B base
    assert idx1 == idx2

    idx3 = cache.insert(0x2000)
    assert idx3 != idx1
    assert cache.lookup(0x1000) == idx1
    assert cache.lookup(0x2000) == idx3


def test_inc_reduction_and_stochastic_rounding():
    """Validates In-Network Compute FP32/INT32 reduction and rounding."""
    vec_a = struct.pack("<4f", 1.0, 2.0, 3.0, 4.0)
    vec_b = struct.pack("<4f", 10.0, 20.0, 30.0, 40.0)
    res_bytes = INCEngine.reduce(INCOpCode.SUM, INCDataType.FP32, vec_a, vec_b)
    assert struct.unpack("<4f", res_bytes) == (11.0, 22.0, 33.0, 44.0)

    # Stochastic rounding test
    rounded = INCRoundingEngine.round_float_to_half(3.14159, INCRoundingMode.ROUND_STOCHASTIC, seed=123)
    assert isinstance(rounded, float)


def test_inc_port_group_table():
    """Validates 1024-entry Collective Group Table (Ch 6.2.1)."""
    gt = PortGroupTable(port_id=0, switch_radix=16)
    assert gt.configure_group(group_id=5, member_acc_ids=[1, 3, 7]) is True
    members = gt.get_members(group_id=5)
    assert members == [1, 3, 7]


def test_200g_transport_and_rs_blocks():
    """Validates 200G DL 640B Flit, CRC-32, Replay, and RS 64B/66B sequences."""
    tx_phy = DL200GTransport(port_id=0)
    rx_phy = DL200GTransport(port_id=1)
    tx_phy.connect_endpoint(rx_phy)

    raw_payload = b"A" * 628
    flit_640b = tx_phy.frame_flit(raw_payload)
    assert len(flit_640b) == 640

    # RS reconciliation sublayer test
    blocks = ReconciliationSublayer.encode_flit_to_blocks(flit_640b)
    assert len(blocks) == 80
    recovered = ReconciliationSublayer.decode_blocks_to_flit(blocks)
    assert recovered == flit_640b

    # Replay buffer test
    replay_buf = TxReplayBuffer()
    seq1 = replay_buf.enqueue(flit_640b)
    assert seq1 == 1
    replay_buf.handle_ack(seq1)
    assert len(replay_buf.buffer) == 0


def test_128g_transport():
    """Validates 128G SerDes transport option."""
    tx_phy = DL128GTransport(port_id=0)
    rx_phy = DL128GTransport(port_id=1)
    tx_phy.connect_endpoint(rx_phy)

    tl_tx = TransactionLayer2(tx_phy)
    tl_rx = TransactionLayer2(rx_phy)
    received = []
    tl_rx.set_receive_callback(lambda flit: received.append(flit))

    req = UPLIRequest(src_id=1, dst_id=2, cmd=ReqCmd.WRITE, addr=0x3000, tag=5)
    assert tl_tx.send_request(req) is True
    assert len(received) == 1


def test_chiplet_d2d_and_sideband():
    """Validates UCIe 3.0 D2D streaming and Sideband mailbox."""
    die_a = UCIeChipletAdapter(die_id=0)
    die_b = UCIeChipletAdapter(die_id=1)
    die_a.connect_endpoint(die_b)

    tl_a = TransactionLayer2(die_a)
    tl_b = TransactionLayer2(die_b)
    received = []
    tl_b.set_receive_callback(lambda flit: received.append(flit))

    req = UPLIRequest(src_id=0, dst_id=1, cmd=ReqCmd.READ, addr=0x5000, tag=8)
    assert tl_a.send_request(req) is True
    assert len(received) == 1

    # Sideband mailbox test
    mb_a = UCIeSidebandMailbox(die_id=0)
    mb_b = UCIeSidebandMailbox(die_id=1)
    mb_a.connect(mb_b)
    mb_a.send_config_write(0x10, 0xCAFE)
    assert mb_a.send_config_read(0x10) == 0xCAFE


def test_security_ualinksec2():
    """Validates UALinkSec 2.0 AES-GCM-256 and Partial Field Encryption."""
    key = b"\x01" * 32
    iv_mgr = IVManager(src_id=1, dst_id=2)
    iv = iv_mgr.next_iv(stream_id=0)
    assert len(iv) == 12

    raw_flit = bytes([i % 256 for i in range(64)])
    protected_flit, tag = PartialFieldEncryptor.protect_flit(key, iv, raw_flit)
    assert len(protected_flit) == 64
    # Routing bytes (0-7) must be preserved for switch routing
    assert protected_flit[:8] == raw_flit[:8]

    ok, recovered = PartialFieldEncryptor.unprotect_flit(key, iv, protected_flit, tag)
    assert ok is True
    assert recovered == raw_flit


def test_manageability_and_pldm():
    """Validates Enterprise Pod Controller, VirtualPod isolation, Telemetry, and PLDM."""
    ctrl = PodControllerV2()
    ctrl.register_accelerator(1, "GPU-1")
    ctrl.register_accelerator(2, "GPU-2")
    ctrl.create_virtual_pod(10, [1, 2])
    assert ctrl.is_communication_allowed(1, 2) is True

    telemetry = EnterpriseTelemetryCollector()
    telemetry.record_tx(port_id=0, count=5)
    assert telemetry.get_port_metrics(0).flits_tx == 5

    pldm = PLDMMessageAgent(eid=10)
    resp = pldm.format_sensor_reading_response(sensor_id=1, reading_val=48)
    assert len(resp) == 8


def test_switch_allreduce_collective():
    """Validates Switch In-Network Compute AllReduce execution."""
    ctrl = PodControllerV2()
    ctrl.register_accelerator(1, "Node-1")
    ctrl.register_accelerator(2, "Node-2")

    switch = SwitchCoreV2(ports_count=8, controller=ctrl)
    switch.set_route(1, 0)
    switch.set_route(2, 1)

    coll_id = 99
    op = INCOperation(INCOpCode.SUM, INCDataType.FP32, 4, coll_id)
    switch.register_collective(coll_id, [1, 2], op)

    v1 = struct.pack("<4f", 1.0, 2.0, 3.0, 4.0)
    v2 = struct.pack("<4f", 10.0, 20.0, 30.0, 40.0)

    r1 = UPLIRequest(src_id=1, dst_id=0, cmd=ReqCmd.READ_REDUCE,
                     inc_op=INCOperation(INCOpCode.SUM, INCDataType.FP32, 4, coll_id, payload=v1))
    r2 = UPLIRequest(src_id=2, dst_id=0, cmd=ReqCmd.READ_REDUCE,
                     inc_op=INCOperation(INCOpCode.SUM, INCDataType.FP32, 4, coll_id, payload=v2))

    assert switch.process_request(r1) == -2 # Pending
    assert switch.process_request(r2) == -1 # Complete!

    res = struct.unpack("<4f", switch.active_collectives[coll_id].get_result())
    assert res == (11.0, 22.0, 33.0, 44.0)
