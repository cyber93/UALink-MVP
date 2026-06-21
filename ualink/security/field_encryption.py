def extract_aad(req) -> bytes:
    w0 = (req.cmd & 0x3F) | ((req.length & 0x3F) << 6) | ((req.attr & 0xFF) << 12) | ((req.metadata & 0xFF) << 20) | ((req.vc & 0x3) << 28)
    w1 = (req.src_acc_id & 0x3FF) | ((req.dst_acc_id & 0x3FF) << 10) | ((req.port_id & 0x3) << 20)
    w2 = req.addr & 0x3  # only lower 2 bits plaintext
    return w0.to_bytes(4,'little') + w1.to_bytes(4,'little') + w2.to_bytes(4,'little')

def extract_plaintext(req) -> bytes:
    w0 = req.tag & 0x7FF
    w1 = (req.addr >> 2) & ((1<<55)-1)
    w2 = req.asi & 0x3
    return w0.to_bytes(2,'little') + w1.to_bytes(8,'little') + w2.to_bytes(1,'little')
