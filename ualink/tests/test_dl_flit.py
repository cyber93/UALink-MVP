from ualink.data_link.dl_flit import DLFlit

def test_dl_flit():
    f = DLFlit()
    assert len(f.to_bytes()) == 640
