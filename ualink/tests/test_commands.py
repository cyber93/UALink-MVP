from ualink.upli.commands import is_write_class
from ualink.common.constants import ReqCmd

def test_commands():
    assert is_write_class(ReqCmd.WRITE)
    assert not is_write_class(ReqCmd.READ)
