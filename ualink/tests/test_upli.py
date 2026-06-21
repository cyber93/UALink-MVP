from ualink.upli.request_channel import RequestChannel
from ualink.common.constants import ReqCmd

def test_req_channel():
    req = RequestChannel(valid=True, cmd=ReqCmd.READ)
    req.compute_parity()
    assert req.vld_parity == 1
