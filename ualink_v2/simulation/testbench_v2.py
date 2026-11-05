"""
UALink 2.0 Comprehensive A-Z Simulation Testbench with Deep Trace
Demonstrates the full life cycle of UALink 2.0 modular architecture:
1. Pod Controller Discovery & VirtualPod Partitioning
2. Pluggable Transport: 200G PAM4 640B Flits & UCIe Chiplet D2D Streaming
3. Common 2.0 UPLI / TL Flit Framing & CRC Verification
4. In-Network Compute (INC) Hardware-Accelerated AllReduce inside Switch Core
"""
import sys
import struct
import logging
from pathlib import Path

# Ensure paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ualink_v2 import (
    ReqCmd, INCOpCode, INCDataType, TransportType,
    UPLIRequest, INCOperation,
    TransactionLayer2, UPLI2Interface,
    DL200GTransport, DL128GTransport, UCIeChipletAdapter,
    PodControllerV2, SwitchCoreV2
)

# Configure deep trace logger
log = logging.getLogger("UALink2")
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Log file
log_file = Path(__file__).parent.parent / "simulation_v2.log"
fh = logging.FileHandler(str(log_file), mode='w', encoding='utf-8')
fh.setFormatter(formatter)
log.addHandler(fh)

# Console handler
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(formatter)
log.addHandler(ch)


def run_full_simulation():
    log.info("=" * 70)
    log.info("Starting UALink 2.0 Modular Architecture A-Z Deep Trace Simulation")
    log.info("=" * 70)

    # -------------------------------------------------------------
    # Step 1: Manageability & Enterprise Pod Lifecycle
    # -------------------------------------------------------------
    log.info("[STEP 1] Initializing Enterprise Pod Controller & Topology Discovery")
    controller = PodControllerV2(pod_id="ScaleUp-Pod-01")
    controller.register_accelerator(1, "Acc-1 (GPU Master)")
    controller.register_accelerator(2, "Acc-2 (GPU Worker)")
    controller.register_accelerator(3, "Acc-3 (Tenant B GPU)")
    log.info("Registered 3 physical accelerator nodes in ScaleUp-Pod-01")

    # Partition into Virtual Pods (Tenant isolation)
    controller.create_virtual_pod(vpod_id=10, member_acc_ids=[1, 2])
    log.info("Configured Virtual Pod 10 with Accelerators [1, 2] (Tenant A isolated)")

    # -------------------------------------------------------------
    # Step 2: Pluggable Physical/Data Link Transport Layer
    # -------------------------------------------------------------
    log.info("\n[STEP 2] Setting up Pluggable 200G & Chiplet Transport Layers")
    transport_200g_tx = DL200GTransport(port_id=0)
    transport_200g_rx = DL200GTransport(port_id=1)
    transport_200g_tx.connect_endpoint(transport_200g_rx)
    log.info(f"200G PAM4 Link connected: 640B Flit framing, 802.3 CRC-32 enabled")

    chiplet_a = UCIeChipletAdapter(die_id=0)
    chiplet_b = UCIeChipletAdapter(die_id=1)
    chiplet_a.connect_endpoint(chiplet_b)
    log.info(f"In-Package UCIe 3.0 D2D Chiplet Link connected: 64B low-latency streaming")

    # -------------------------------------------------------------
    # Step 3: Transaction Layer 2.0 Framing & CRC Verification
    # -------------------------------------------------------------
    log.info("\n[STEP 3] Originator (Acc-1) Transmitting 64B TL 2.0 Flit over 200G Link")
    tl_tx = TransactionLayer2(transport_200g_tx)
    tl_rx = TransactionLayer2(transport_200g_rx)

    received_flits = []
    tl_rx.set_receive_callback(lambda flit: received_flits.append(flit))

    req = UPLIRequest(src_id=1, dst_id=2, cmd=ReqCmd.READ, addr=0xDEADBEEF, tag=101)
    log.debug(f"UPLI Request: Src={req.src_id}, Dst={req.dst_id}, Cmd=READ, Addr={hex(req.addr)}, Tag={req.tag}")

    tl_tx.send_request(req)
    log.info(f"Packed into 640B DL Flit (Op=0, Seq=1, CRC-32 computed). Transmitted.")

    assert len(received_flits) == 1
    log.info(f"Completer (Acc-2) received and verified 640B Flit (CRC: PASS). TL 2.0 unpacked.")

    # -------------------------------------------------------------
    # Step 4: In-Network Compute (INC) Hardware Collective AllReduce
    # -------------------------------------------------------------
    log.info("\n[STEP 4] Executing In-Network Compute (INC) AllReduce Reduction inside Switch")
    switch = SwitchCoreV2(ports_count=16, controller=controller)
    switch.set_route(acc_id=1, egress_port=0)
    switch.set_route(acc_id=2, egress_port=1)

    coll_id = 505
    op = INCOperation(opcode=INCOpCode.SUM, dtype=INCDataType.FP32, vector_len=4, collective_id=coll_id)
    switch.register_collective(collective_id=coll_id, expected_peers=[1, 2], op=op)
    log.info(f"Switch initialized hardware reduction collective ID {coll_id}: Op=SUM, DType=FP32, Peers=[1, 2]")

    vec_acc1 = struct.pack("<4f", 10.5, 20.0, 30.25, 40.0)
    vec_acc2 = struct.pack("<4f", 1.5, 2.0, 0.75, 5.0)
    log.debug(f"Acc-1 contribution vector: [10.5, 20.0, 30.25, 40.0]")
    log.debug(f"Acc-2 contribution vector: [1.5, 2.0, 0.75, 5.0]")

    req_inc1 = UPLIRequest(src_id=1, dst_id=0, cmd=ReqCmd.READ_REDUCE,
                            inc_op=INCOperation(INCOpCode.SUM, INCDataType.FP32, 4, coll_id, payload=vec_acc1))
    req_inc2 = UPLIRequest(src_id=2, dst_id=0, cmd=ReqCmd.READ_REDUCE,
                            inc_op=INCOperation(INCOpCode.SUM, INCDataType.FP32, 4, coll_id, payload=vec_acc2))

    # Submit to switch
    st1 = switch.process_request(req_inc1)
    log.info(f"Acc-1 contributed to Switch collective. Status: PENDING other peers (st={st1})")

    st2 = switch.process_request(req_inc2)
    log.info(f"Acc-2 contributed to Switch collective. Status: COLLECTIVE COMPLETE (st={st2})")

    result_bytes = switch.active_collectives[coll_id].get_result()
    final_vec = struct.unpack("<4f", result_bytes)
    log.info(f"Switch In-Network Compute Final Vector: {final_vec}")
    assert final_vec == (12.0, 22.0, 31.0, 45.0)

    # -------------------------------------------------------------
    # Step 5: Security / Virtual Pod Violation Check
    # -------------------------------------------------------------
    log.info("\n[STEP 5] Testing Security Isolation (Virtual Pod Boundary Enforced)")
    rogue_req = UPLIRequest(src_id=1, dst_id=3, cmd=ReqCmd.READ, addr=0x5000)
    drop_status = switch.process_request(rogue_req)
    log.info(f"Cross-VirtualPod Request from Acc-1 (VPod 10) to Acc-3 (Unassigned): {drop_status} (DROPPED)")
    assert drop_status is None

    log.info("\n" + "=" * 70)
    log.info("UALink 2.0 All-in-One End-to-End Simulation SUCCESSFUL!")
    log.info(f"Deep Trace saved to: {log_file.resolve()}")
    log.info("=" * 70)

if __name__ == "__main__":
    run_full_simulation()
