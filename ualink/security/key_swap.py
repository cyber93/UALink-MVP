from ..common.constants import UPLIWriteMsgType
from ..upli.request_channel import RequestChannel

def make_key_roll_req(src: int, dst: int, stream: int) -> RequestChannel:
    msg_type = {
        0: UPLIWriteMsgType.KEY_ROLL_REQ_CHANNEL,
        1: UPLIWriteMsgType.KEY_ROLL_RDRSP_CHANNEL,
        2: UPLIWriteMsgType.KEY_ROLL_WRRSP_CHANNEL
    }[stream]
    return RequestChannel(
        valid=True, src_acc_id=src, dst_acc_id=dst,
        cmd=0x2A, metadata=msg_type
    )
