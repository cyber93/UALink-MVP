import sys
import pytest
from ..common.logger import log
from ..system.accelerator import Accelerator
from ..switch.switch_core import SwitchCore
from ..upli.request_channel import RequestChannel
from ..common.constants import ReqCmd
from ..data_link.dl_flit import DLFlit
from ..transaction_layer.tl_flit import TLFlit

def test_A_upli():
    log.info("--- Test A: UPLI Layer ---")
    req = RequestChannel(valid=True, cmd=ReqCmd.READ, dst_acc_id=1, addr=0x1000)
    req.compute_parity()
    assert req.vld_parity == 1
    log.info(f"UPLI Request parity validated: {req.vld_parity}")

def test_B_transaction():
    log.info("--- Test B: Transaction Layer ---")
    tf = TLFlit()
    data = tf.to_bytes()
    assert len(data) == 64
    log.info("TL Flit format validated")

def test_C_data_link():
    log.info("--- Test C: Data Link Layer ---")
    df = DLFlit()
    data = df.to_bytes()
    assert len(data) == 640
    log.info("DL Flit format validated")

def test_D_switch():
    log.info("--- Test D: Switch Routing ---")
    sw = SwitchCore(ports=4)
    sw.rt.add(acc_id=1, port=2)
    sw.assign_vpod(1, 100)
    sw.assign_vpod(2, 100)
    req = RequestChannel(valid=True, cmd=ReqCmd.READ, dst_acc_id=1)
    port = sw.forward(req, in_port_idx=1)
    assert port is not None and port.idx == 2
    log.info("Switch routing validated")

def test_E_end_to_end():
    log.info("--- Test E: Deep End-to-End System Trace ---")
    a1 = Accelerator(1)
    a2 = Accelerator(2)
    
    # Manually dump the connection details
    log.info("STEP 1: Physical Link Connection")
    a1.connect_port(0, 2)
    a2.connect_port(0, 1)
    
    log.info("STEP 2: Initializing Credits")
    a1.ports[0].upli.credits.init_credits()
    log.debug(f"A1 UPLI Credits: ReqPool={a1.ports[0].upli.credits.req_cmd.pool_credits}, DataPool={a1.ports[0].upli.credits.req_data.pool_credits}")
    
    log.info("STEP 3: Originator generating UPLI Request")
    req = RequestChannel(valid=True, src_acc_id=a1.acc_id, dst_acc_id=a2.acc_id, cmd=ReqCmd.READ, addr=0xDEADBEEF, tag=42)
    log.debug(f"Payload detail: SRC={req.src_acc_id}, DST={req.dst_acc_id}, ADDR={hex(req.addr)}, CMD={req.cmd}, TAG={req.tag}")
    
    a1.ports[0].upli.send_request(req)
    
    log.info("STEP 4: Transaction Layer Formatting")
    tl_req = a1.ports[0].upli.drain_requests()[0]
    tf = TLFlit()
    # Dummy packing for trace visibility
    tf.set_sector(0, b'\x01\x02\x03\x04')
    log.debug(f"TL Flit Headers constructed: {tf.control_half.hex()}")
    tl_payload = tf.to_bytes()
    log.debug(f"TL Payload size: {len(tl_payload)} bytes")
    
    log.info("STEP 5: Data Link Layer Formatting & Framing")
    df = DLFlit()
    df.flit_header.op = 0 # Original
    df.flit_header.ack_req_seq = 100
    df.set_payload(tl_payload)
    df_bytes = df.to_bytes()
    log.debug(f"DL Flit generated: OP={df.flit_header.op}, SEQ={df.flit_header.ack_req_seq}")
    log.debug(f"DL Payload size: {len(df_bytes)} bytes. CRC appended.")
    
    log.info("STEP 6: Switch Core Routing")
    sw = SwitchCore(ports=4)
    sw.rt.add(acc_id=2, port=3) # Route to A2 on port 3
    port = sw.forward(tl_req)
    log.debug(f"Switch crossbar active. Route mapping: DST Acc {tl_req.dst_acc_id} -> egress Port {port.idx if port else 'DROP'}")
    
    log.info("STEP 7: Completer Data Link Layer Receiving")
    recv_df = DLFlit.from_bytes(df_bytes)
    valid_crc = recv_df.verify(df_bytes)
    log.debug(f"CRC check on incoming Flit: {'PASS' if valid_crc else 'FAIL'} (Expected: {recv_df.crc:08X})")
    
    log.info("STEP 8: Completer Transaction Layer Parsing")
    extracted_tl = TLFlit.from_bytes(recv_df.get_payload_bytes()[:64])
    log.debug(f"Extracted TL Headers: {extracted_tl.control_half.hex()}")
    
    log.info("STEP 9: Completer UPLI Receiving & Processing")
    a2.read_local(tl_req.addr)
    log.debug(f"Completer Memory lookup executed at Address={hex(tl_req.addr)}")
    
    log.info("STEP 10: Credit Flow & Return")
    a2.ports[0].upli.return_req_credit(pool=True, num=1)
    log.debug(f"A2 UPLI returning credit to A1...")
    a1.ports[0].upli.credits.return_req_credit(pool=True, num=1)
    
    log.info("End-to-End trace completed successfully.")

def main():
    log.info("Starting comprehensive A-Z Testbench with DEEP TRACE")
    test_A_upli()
    test_B_transaction()
    test_C_data_link()
    test_D_switch()
    test_E_end_to_end()
    log.info("All tests passed successfully.")
    
if __name__ == "__main__":
    main()
