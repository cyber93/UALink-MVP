# UALink 200 Rev 1.0 — Complete Python Prototype

Full software prototype implementing UALink_200 spec. Modular micro-architecture, presentable to team.

## Scope

Implement **all** spec chapters as Python modules:

| Spec Chapter | Module | Key Contents |
|---|---|---|
| Ch1 — System Overview | `system/` | Pod, SystemNode, Accelerator, VirtualPod, AddressTranslation |
| Ch2 — UPLI Interface | `upli/` | 4 channels, commands, credits, flow control, ordering, atomics |
| Ch3 — RAS | `ras/` | Error types, parity, poison, error containment, isolation |
| Ch4 — Reset/Init | `reset/` | UPLI handshake, reset sequences |
| Ch5 — Transaction Layer | `transaction_layer/` | TL Flit packing, compressed/uncompressed req/rsp, address cache, FC |
| Ch6 — Data Link Layer | `data_link/` | 640B flit, segments, CRC, DL messages, UART, replay, pacing |
| Ch7 — Physical Layer | `physical_layer/` | RS sublayer, 64B/66B encoding, FEC stubs, alignment markers |
| Ch8 — Manageability | `manageability/` | PodController, NodeMgmtAgent, SwitchMgmtAgent |
| Ch9 — Security | `security/` | AES-GCM, key derivation, key swap, IV mgmt, stream enc/dec |
| Ch10 — Switch | `switch/` | Routing table, forwarding, bifurcation, VirtualPod partitioning |

---

## Proposed File Structure

```
d:\Projects\UALink_2-0\ualink/
├── __init__.py
├── common/
│   ├── __init__.py
│   ├── constants.py          # Global enums, bit widths, max values
│   ├── types.py              # Shared dataclasses (AcceleratorID, Address, Tag, etc.)
│   └── parity.py             # Even parity computation
├── system/
│   ├── __init__.py
│   ├── pod.py                # Pod, VirtualPod
│   ├── system_node.py        # SystemNode, host references
│   ├── accelerator.py        # Accelerator with ports
│   └── address_translation.py # GVA→NPA→SPA model
├── upli/
│   ├── __init__.py
│   ├── interface.py          # UPLIInterface: 4 channels + handshake
│   ├── request_channel.py    # ReqChannel with all Table 2-2 signals
│   ├── read_response_channel.py  # RdRsp channel (Table 2-8)
│   ├── write_response_channel.py # WrRsp channel (Table 2-11)
│   ├── originator_data_channel.py # OrigData channel (Table 2-14)
│   ├── commands.py           # Read, Write, WriteFull, AtomicR, AtomicNR, UPLI Write Msg, VDC
│   ├── credit_manager.py     # Per-channel credit tracking (pool + VC)
│   └── ordering.py           # 256B region ordering, strict mode ordering
├── ras/
│   ├── __init__.py
│   ├── error_types.py        # UPLI Control/Data/Protocol errors, Switch core errors
│   ├── data_protection.py    # End-to-end parity, poison marking
│   ├── error_containment.py  # Isolation mode, drop mode
│   └── link_down_handler.py  # Link-down error recovery flow
├── reset/
│   ├── __init__.py
│   └── upli_reset.py         # Reset sequence, connection handshake (Fig 4-1..4-4)
├── transaction_layer/
│   ├── __init__.py
│   ├── tl_flit.py            # 64B TL Flit: control half-flit + data half-flit
│   ├── field_types.py        # FTYPE encodings (Table 5-27), uncompressed/compressed req/rsp
│   ├── compressed_request.py # Compressed req (2 sectors), restrictions (Table 5-32)
│   ├── compressed_response.py# Compressed rsp single-beat/multi-beat
│   ├── uncompressed.py       # Uncompressed req (4 sectors), uncompressed rsp (2 sectors)
│   ├── flow_control.py       # FC/NOP field, credit return via TL
│   ├── address_cache.py      # Tx/Rx address cache for compression
│   └── flit_packer.py        # Packing rules: half-flits → TL flit
├── data_link/
│   ├── __init__.py
│   ├── dl_flit.py            # 640B DL Flit: 5 segments, headers, CRC
│   ├── segment.py            # Segment header, sector allocation (Table 6-1)
│   ├── flit_packer.py        # TL→DL packing (Fig 6-5 flow)
│   ├── crc.py                # CRC-32 per 802.3 clause 3.2.9
│   ├── messages.py           # DL messages: TL Rate, DeviceID, PortID, NoOp, ChannelNeg
│   ├── uart.py               # UART stream: Tx/Rx buffers, credit FC, reset seq
│   ├── replay.py             # Link-level replay: TxReplay buffer, seq nums, Ack/Replay logic
│   ├── pacing.py             # Tx pacing, Rx rate adaptation
│   └── link_state.py         # DL states: Fault→Idle→NOP→Up (Fig 6-23)
├── physical_layer/
│   ├── __init__.py
│   ├── reconciliation.py     # RS: 64B/66B block encoding, flit code sequences
│   ├── encoding.py           # 64B/66B data/control blocks (Fig 7-2)
│   ├── alignment.py          # AM insertion/overwrite, Start/Idle/Fault/AM flit code seqs
│   ├── pcs_stub.py           # PCS: scramble, transcode, FEC encode stubs
│   └── rate_config.py        # Rate configs: 100G/200G/400G/800G, interleave modes
├── security/
│   ├── __init__.py
│   ├── ualinksec.py          # Main security controller: modes, config
│   ├── aes_gcm.py            # AES-GCM 256-bit enc/dec, tag gen/verify
│   ├── iv_manager.py         # 96-bit IV: fixed(srcID,dstID,streamID) + invocation counter
│   ├── key_manager.py        # Master keys (active/alternate), derived keys per stream
│   ├── key_derivation.py     # NIST KDF: master→derived key, epoch counters
│   ├── key_swap.py           # Key swap flow: KeyRollMsg.{Req,RdRsp,WrRsp}Channel
│   └── field_encryption.py   # Partial field enc: Addr[17:2], Tag, ASI; AAD/MSG mapping
├── switch/
│   ├── __init__.py
│   ├── switch_core.py        # Switch: stateless forwarding, routing
│   ├── routing_table.py      # Routing table: AccID→egress port mapping
│   ├── port.py               # Switch port: bifurcation (x1/x2/x4)
│   └── virtual_pod_partition.py # Port partitioning → Virtual Pods
├── manageability/
│   ├── __init__.py
│   ├── pod_controller.py     # Pod lifecycle, topology discovery, AccID assignment
│   ├── node_agent.py         # Node Management Agent
│   └── switch_agent.py       # Switch Management Agent
├── simulation/
│   ├── __init__.py
│   ├── end_to_end.py         # Full system sim: Acc→Switch→Acc read/write/atomic
│   └── demo.py               # CLI demo: create pod, run transactions, show results
└── tests/
    ├── __init__.py
    ├── test_upli.py           # UPLI channel signals, credit flow, ordering
    ├── test_commands.py       # Read/Write/WriteFull/Atomic/UPLI Write Msg
    ├── test_tl_flit.py        # TL flit packing, compressed/uncompressed
    ├── test_dl_flit.py        # DL flit packing, CRC, segment headers
    ├── test_replay.py         # Link-level replay: seq nums, ack, replay request
    ├── test_dl_messages.py    # DL messages: TL rate, DeviceID, ChannelNeg
    ├── test_security.py       # AES-GCM, IV, key derivation, key swap
    ├── test_switch.py         # Routing, forwarding, partitioning
    ├── test_ras.py            # Parity, poison, error containment
    ├── test_physical.py       # 64B/66B encoding, RS flit code sequences
    └── test_integration.py    # End-to-end: multi-accelerator pod transactions
```

---

## Key Implementation Details

### UPLI Interface (Ch2)
- 4 channels: Request, RdRsp, WrRsp, OrigData — each as class w/ exact signal fields from Tables 2-2, 2-8, 2-11, 2-14
- Commands enum: Read=0x03, Write=0x28, WriteFull=0x29, UPLI Write Msg=0x2A, AtomicR=0x30, AtomicNR=0x32 + VDC ranges
- Credit manager: pool + per-VC credits, 4 ports, credit return interface
- Ordering: per 256B region ordering (non-strict), all-ordered (strict/security mode)
- ReqAttr: byte enables for reads (first/last DW), OpType+OpSize for atomics
- Transaction tags: 11-bit, matching req→rsp
- UPLI Write Messages: NOP(0x00), KeyRollMsg variants(0x01-0x03), VDC(0xF0-0xFF)

### Transaction Layer (Ch5)
- 64B TL Flit = 8 sectors × 4B = 32B control half-flit + 32B data half-flit
- Field Types (FTYPE 4-bit): Uncompressed Req(4 sectors), Uncompressed Rsp(2), Compressed Req(2), Compressed Rsp single-beat(1), Compressed Rsp multi-beat/write(1), FC/NOP(1)
- Address cache: Tx cache + Rx cache for address compression
- Compressed req: subset of commands (Read, Write, WriteFull), 64B-aligned, cache hit required

### Data Link Layer (Ch6)
- 640B DL Flit = 5 segments, each w/ segment header(1B)
- Segment sectors: Table 6-1 allocation (31/32/32/32/16 sectors + headers)
- Flit packing: sector-basis, TL flits packed in order, carry-over across segments
- CRC-32 over entire 640B (802.3 clause 3.2.9), placed in last 4 bytes
- DL Messages: TL Rate Notification, Device ID Req, Port ID Req, No-Op, Channel Negotiation
- UART: Tx/Rx buffers (128 DW recommended), modulo-2^12 credit flow control, stream reset
- Link-level replay: 9-bit seq nums (1-511), TxReplay buffer, Ack/Replay Request, 3-replica replay requests
- Link states: DL Fault → DL Idle → DL NOP → DL Up

### Physical Layer (Ch7)
- RS: 80 × 64B/66B blocks = one Flit Code Sequence
- Block types: Data(sync=01), Control(sync=10). Types: 0x1E(Idle/Error), 0x78(Start), 0x4B(Fault)
- Flit code sequences: Data, Idle, Idle Start, Fault, Fault Start, AM
- Rate configs: 100G/200G/400G/800G, x1/x2/x4 lanes
- Alignment markers: every 4096/4096/8192/16384 flits per rate
- FEC interleave: 4-way(standard), 2-way, 1-way modes

### Security (Ch9)
- AES-GCM-256 per transaction, optional 8B auth tag
- IV = 96 bits: SrcAccID(10b) + DstAccID(10b) + StreamID(2b) + Epoch(varies) + InvocationField(32b)
- 3 streams: Request, ReadResponse, WriteResponse — each independently ordered
- Master keys: active + alternate per (port, dest/src accelerator)
- Key derivation: NIST SP 800-56C KDF, epoch counter tracks derivations
- Key swap: KeyRollMsg.{ReqChannel, RdRspChannel, WrRspChannel} UPLI Write Messages
- Partial encryption: Addr[17:2], Tag, ASI encrypted; routing fields plaintext
- AAD/MSG mapping per Tables 9-8 through 9-24

### Switch (Ch10)
- Stateless: no tracking of req/rsp, no timeouts
- Routing table: AccID → egress port, per-VirtualPod partitions
- Non-blocking, lossless delivery guaranteed
- Forward progress guarantee
- Bifurcation: x4, x2, x1 per station

### RAS (Ch3)
- Error categories: UPLI Control, UPLI Data, UPLI Protocol, Switch Core, Link Down
- End-to-end parity: even parity per channel, separate data parity
- Poison: RdRspDataError, OrigDataError signals
- Error containment: Isolation mode via ISOLATE WrRspStatus(0xF)
- Link-down recovery: PHY→DL→TL→Accelerator cascade

---

## Open Questions

> [!IMPORTANT]
> **AES-GCM dependency**: Use Python `cryptography` lib for AES-GCM? Or pure-Python impl for portability? Recommend `cryptography` lib.

> [!IMPORTANT]
> **Test granularity**: Should every table/signal encoding have dedicated tests, or focus on behavioral tests (e.g., "read transaction end-to-end")?

> [!NOTE]
> **PHY layer depth**: Physical layer (RS, PCS, FEC) = largely IEEE 802.3 references. Prototype implements structural stubs + 64B/66B encoding logic. Full FEC encode/decode not practical in Python. OK?

---

## Verification Plan

### Automated Tests
```bash
cd d:\Projects\UALink_2-0
python -m pytest ualink/tests/ -v
```

### Test Coverage by Module:
| Module | Test Focus |
|---|---|
| `test_upli.py` | All 4 channels signals match Table 2-2/2-8/2-11/2-14 sizes, credit flow, TDM |
| `test_commands.py` | All ReqCmd encodings (Table 2-6), ReqAttr for reads/atomics, byte enables |
| `test_tl_flit.py` | FTYPE packing, compressed req restrictions (Table 5-32), half-flit construction |
| `test_dl_flit.py` | 640B structure, segment headers, CRC calculation, TL→DL mapping |
| `test_replay.py` | Seq num wrapping(511→1), TxReplay enqueue/dequeue, replay request flow |
| `test_dl_messages.py` | TL rate msg, Device/Port ID request-response, Channel negotiation |
| `test_security.py` | AES-GCM enc/dec round-trip, IV construction, key derivation, key swap flow |
| `test_switch.py` | Routing table lookup, AccID→port mapping, partition isolation |
| `test_ras.py` | Parity computation, poison propagation, ISOLATE response generation |
| `test_physical.py` | 64B/66B block encoding, sync headers, flit code sequence construction |
| `test_integration.py` | Multi-Acc pod: Read→Response, Write→Response, Atomic end-to-end |

### Manual Verification
- Run `demo.py` CLI → shows pod creation, transaction flow, output verification
- Review module structure matches spec chapter organization
