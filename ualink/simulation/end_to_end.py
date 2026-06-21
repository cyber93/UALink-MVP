from ..system.pod import Pod
from ..system.system_node import SystemNode
from ..system.accelerator import Accelerator
from ..switch.switch_core import SwitchCore
from ..upli.request_channel import RequestChannel

def simulate_read(acc1, acc2):
    req = RequestChannel(valid=True, src_acc_id=acc1.acc_id, dst_acc_id=acc2.acc_id, cmd=0x03)
    acc1.ports[0].upli.send_request(req)
