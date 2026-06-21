from ualink.transaction_layer.tl_flit import TLFlit

def test_tl_flit():
    f = TLFlit()
    assert len(f.to_bytes()) == 64
