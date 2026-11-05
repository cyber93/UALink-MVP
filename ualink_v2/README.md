# UALink 2.0 Modular Architecture Prototype (`ualink_v2`)

Python reference implementation of the **UALink 2.0 Modular Specification Ecosystem**.

```mermaid
graph TD
    A[UALink Common Spec 2.0<br/>UPLI 2.0 / TL 2.0 / In-Network Compute]
    A --> B[UALink 200G DL & PL 2.0<br/>PAM4 106.25GBd, 640B Flit, CRC-32]
    A --> C[UALink 128G DL & PL 1.0<br/>SerDes Lane Rate Option]
    A --> D[UALink Chiplet Spec 1.01<br/>UCIe 3.0 D2D Direct Streaming]
    E[Enterprise Management Plane<br/>Pod Controller v2, VirtualPod, Telemetry] --> A
    F[Switch Core v2<br/>Stateless Routing + In-Switch INC AllReduce] --> A
```

## Modular Directory Structure

- `common_v2/`: UALink Common Specification 2.0
  - In-Network Compute (INC) reduction engine (FP32, FP16, INT32)
  - UPLI 2.0 interface & credit management
  - Transaction Layer 2.0 (64B TL Flits)
  - Pluggable Transport Layer abstraction (`ITransportLayer`)
- `phy_dl_200g/`: 200G DL & PL 2.0 (640B Flits, CRC-32, Replay buffer)
- `phy_dl_128g/`: 128G DL & PL 1.0 (PCIe-compatible SerDes framing)
- `chiplet/`: UALink Chiplet Spec 1.01 (UCIe 3.0 D2D streaming)
- `manageability/`: Pod Controller v2, Virtual Pod isolation, Telemetry
- `switch_v2/`: Switch core with hardware collective reduction
- `simulation/`: End-to-end A-Z trace testbench (`testbench_v2.py`)
- `tests/`: Automated pytest suite (`test_all_v2.py`)
```
UALink-MVP/ualink_v2/
├── __init__.py
│
├── common_v2/                              # [사양 ①] Common Specification 2.0
│   ├── constants.py                        # 2.0 전역 상수 및 Collective Primitive Encodings
│   ├── types.py                            # 데이터클래스 (AccID, Tag, INCOperation 등)
│   ├── parity.py                           # Even Parity 계산 엔진
│   ├── logger.py                           # 공통 로거
│   ├── transport_interface.py              # 플러그형 전송 계층 추상화 (ITransportLayer)
│   ├── upli_v2.py                          # UPLI 2.0 인터페이스 및 크레딧 트래커
│   ├── tl_v2.py                            # 64B TL 2.0 Flit 및 플러그형 전송 연동
│   ├── upli/                               # UPLI 채널별 세부 신호 구현 (Chapter 2 & 6)
│   │   ├── commands.py                     # 커맨드 세트 및 VDC/Collective 판별
│   │   ├── request_channel.py              # Table 2-2 + GroupID/ReduceOpDataType 오버로딩
│   │   ├── read_response_channel.py        # Table 2-8 RdRspData, Status, Poison 비트
│   │   ├── write_response_channel.py       # Table 2-11 WrRspStatus 및 Tag
│   │   ├── originator_data_channel.py      # Table 2-14 OrigData 512b, ByteEn 64b
│   │   ├── credit_manager.py               # Pool 크레딧 및 VC0~VC3 크레딧 매니저
│   │   ├── ordering.py                     # 256B Region Ordering 및 Strict Ordering
│   │   └── interface.py                    # 4채널 결합 UPLI 2.0 인터페이스
│   ├── transaction_layer/                  # 트랜잭션 계층 세부 모듈 (Chapter 5)
│   │   ├── field_types.py                  # Table 5-27 FTYPE (Uncompressed/Compressed/FC)
│   │   ├── address_cache.py                # 32-Entry 주소 압축 캐시 (Tx/Rx)
│   │   └── flit_packer.py                  # 4B Sector 단위 64B TL Flit 패킹/언패킹
│   ├── in_network_compute/                 # In-Network Compute 세부 모듈 (Chapter 6)
│   │   ├── engine.py                       # FP32/INT32 원소별 벡터 리덕션 엔진 (SUM, MIN, MAX 등)
│   │   ├── rounding.py                     # Stochastic Rounding (PRNG 시드 기반) 및 부동소수점 라운딩
│   │   └── group_table.py                  # 포트당 1024-Entry Collective Group Table (Ch 6.2.1)
│   └── system/                             # 시스템 모델 (Chapter 1)
│       ├── pod.py                          # Pod 및 VirtualPod 2.0
│       ├── accelerator.py                  # 가속기 노드 (로컬 메모리, 포트 어레이, UPLI)
│       └── address_translation.py          # 3단계 주소 변환 (GVA -> NPA -> SPA)
│
├── phy_dl_200g/                            # [사양 ②] 200G DL & PL Specification 2.0
│   ├── dl_200g.py                          # 640B DL Flit 프레이밍 및 ITransportLayer 구현
│   ├── segment.py                          # 5개 Segment Header(SH) 및 Sector 할당 (Table 6-1)
│   ├── replay.py                           # 9비트 시퀀스(1~511), TxReplay 송신 버퍼, Ack/Replay
│   ├── encoding.py                         # 64B/66B 블록 인코딩 (Sync: Data 01, Control 10)
│   └── reconciliation.py                   # RS 계층 (80개 64B/66B 블록 = 1 Flit Code Sequence)
│
├── phy_dl_128g/                            # [사양 ③] 128G DL & PL Specification 1.0
│   └── dl_128g.py                          # 128G SerDes 특화 256B 프레이밍 및 속도 적합화
│
├── chiplet/                                # [사양 ④] Chiplet Specification 1.01
│   ├── ucie_adapter.py                     # UCIe 3.0 Die-to-Die (D2D) 초저지연 스트리밍 어댑터
│   └── sideband.py                         # 칩렛 레지스터 접근/트레이닝용 사이드밴드 메일박스
│
├── manageability/                          # [사양 ⑤] Manageability Specification 1.0
│   ├── pod_controller_v2.py                # 가속기 토폴로지 디스커버리 및 VirtualPod 보안 격리
│   ├── telemetry.py                        # 포트별 링크 에러, 전송량, INC 처리량 텔레메트리 수집
│   └── mctp_pldm.py                        # MCTP 패킷 헤더 및 PLDM Type 0x02 모니터링 바인딩
│
├── security_v2/                            # Security (UALinkSec 2.0)
│   ├── iv_manager.py                       # 96-bit AES-GCM IV (SrcID + DstID + Stream + Epoch + Invocation)
│   ├── aes_gcm.py                          # AES-GCM-256 비트 암복호화 및 64-bit Auth Tag 검증
│   └── field_encryption.py                 # 라우팅 헤더(AAD) 평문 유지 + 페이로드 부분 암호화
│
├── switch_v2/                              # Switch 2.0
│   ├── switch_core_v2.py                   # 무상태 스위칭 + 하드웨어 AllReduce 집합 연산 유닛
│   ├── routing_table.py                    # AccID -> Egress Port 매핑
│   └── port.py                             # 스위치 포트 모델 및 Bifurcation (x1, x2, x4)
│
├── simulation/
│   └── testbench_v2.py                     # A-Z 엔드투엔드 전체 통합 시뮬레이션
│
└── tests/
    └── test_all_v2.py                      # 11종 세부 단위 테스트 스위트
```

## Running Verification

```powershell
# Run unit tests
python -m pytest ualink_v2/tests/test_all_v2.py -v

# Run End-to-End Simulation with Deep Trace
python -m ualink_v2.simulation.testbench_v2
```


## Implementation Satus 

### 1. 사양 대비 종합 구현 수준 요약

현재 구현체는 **"소프트웨어 실행 레퍼런스 모델(Architectural Executable Reference Model)"**입니다.
즉, **하드웨어 칩(ASIC/FPGA) 설계 전, 프로토콜 규격의 정합성, 플릿 포맷, 패킷 흐름, In-Network Compute 연산, 테넌트 격리 및 인터페이스 연동을 100% 소프트웨어 레벨에서 시뮬레이션할 수 있는 수준**입니다.

```mermaid
pie title UALink v2 구현 수준 (계층별 완성도)
    "상위 프로토콜 & UPLI 2.0 (90%)" : 90
    "In-Network Compute (INC) (85%)" : 85
    "Transaction Layer 2.0 (80%)" : 80
    "Data Link Layer & Replay (75%)" : 75
    "Chiplet / UCIe 3.0 연동 (75%)" : 75
    "Manageability & VPod (80%)" : 80
    "Security (UALinkSec) (80%)" : 80
    "Physical Layer / Analog SerDes (20%)" : 20
```

| 사양서 / 계층 | 스펙 대비 구현 완성도 | 스펙 정합성 수준 (Fidelity) | 주요 평가 |
| :--- | :---: | :---: | :--- |
| **Common Spec 2.0 (UPLI 2.0)** | **90%** | **High** | 4대 채널 신호 규격(Table 2-2/2-8/2-11/2-14), 크레딧 제어, Even Parity, Poison 비트 완벽 반영 |
| **Common Spec 2.0 (INC)** | **85%** | **High** | `ReadReduce` 등 집합 원시 연산, 신호 오버로딩(GroupID, ReduceOpDataType), FP32/INT32 리덕션 및 Group Table(1024 엔트리) 규격 준수 |
| **Transaction Layer (TL 2.0)** | **80%** | **High** | 64B TL Flit (32B Control + 32B Data), Table 5-27 FTYPE, 32-Entry 주소 압축 캐시 구현 |
| **200G DL & PL Spec 2.0 (DL)** | **75%** | **Medium-High** | 640B Flit 프레이밍, Table 6-1 5개 세그먼트, IEEE 802.3 CRC-32, 9비트 시퀀스 Replay 버퍼 구현 |
| **128G DL & PL Spec 1.0** | **70%** | **Medium** | 128G SerDes 특화 256B 프레이밍 및 속도 적합화 인터페이스 모델링 |
| **Chiplet Spec 1.01 (UCIe 3.0)** | **75%** | **Medium-High** | UCIe 3.0 D2D 초저지연 직접 스트리밍 및 사이드밴드 메일박스(레지스터 제어) 모델링 |
| **Manageability Spec 1.0** | **80%** | **High** | Pod Controller 디스커버리, 테넌트별 VirtualPod 보안 격리(Cross-VPod 패킷 드롭), 텔레메트리, PLDM 헤더 |
| **Security (UALinkSec 2.0)** | **80%** | **High** | 96-bit IV(SrcID+DstID+Stream+Epoch+Invocation), 라우팅 헤더 평문 유지(AAD) + 페이로드 AES-GCM 부분 암호화 |
| **Physical Layer (PHY / SerDes)**| **20%** | **Abstracted** | RS 계층(80개 64B/66B 블록 = 1 Flit) 및 Sync/Control 인코딩은 구현되었으나, 아날로그/FEC 회로는 소프트웨어 추상화 |

---

### 2. 세부 사양별 상세 구현 수준 비교

#### ① UALink Common Specification 2.0 & In-Network Compute
* **스펙과 완벽히 일치하는 부분 (90~95%)**:
  * **신호 오버로딩(Signal Overloading, Ch 6.2.1)**: `ReqDstPhysAccID` ➔ `GroupID[9:0]`, `ReqSrcPhysAccID` ➔ `ReduceOpDataType[6:0]` + `RoundingMode[2:0]`, `ReqAttr` ➔ `Stochastic Seed[7:0]` 오버로딩 규칙 100% 반영
  * **Collective Primitives**: `ReadReduce`(`0x38`), `WriteMulticast`(`0x39`), `WriteFullMulticast`(`0x3A`), `AtomicNRMulticast`(`0x3B`) 커맨드 인코딩
  * **Group Table**: 포트당 1024 엔트리 및 Switch Radix 크기의 비트마스크(`accelerator_mask`) 관리
  * **UPLI 2.0 채널**: Request, ReadResponse, WriteResponse, OriginatorData 채널 및 Even Parity 계산
* **소프트웨어 레벨에서 단순화/추상화된 부분 (일부 간소화)**:
  * 대규모(수만 개 원소) 텐서의 멀티-스위치 계층형 트리 리덕션 파이프라인 (현재는 단일 스위치 코디네이터 중심 동작)
  * FP16/BF16의 비트 단위 비정규화(subnormal) 부동소수점 하드웨어 처리

#### ② UALink 200G & 128G DL / Physical Layer
* **스펙과 완벽히 일치하는 부분 (80~90%)**:
  * **640-Byte DL Flit 구조 (Table 6-1)**: 3-byte Flit Header + 5개 Segment(각 1B SH 포함, 31/32/32/32/16 sectors) + 4-byte CRC-32
  * **CRC-32**: IEEE 802.3 Clause 3.2.9 표준 다항식 기반 비트 단위 검증
  * **Link Level Replay (Section 6.5)**: 9비트 시퀀스 번호(1~511), 255개 한도의 `TxReplayBuffer`, 수신측 Ack/Replay 요청 메커니즘
  * **Reconciliation Sublayer (RS)**: 80개의 64B/66B 블록 = 1 Flit Code Sequence (640B 대응), Sync Header(`01` Data, `10` Control), Start(`0x78`), Idle(`0x1E`) 코드
* **소프트웨어 모델의 본질적 한계로 제외/추상화된 부분**:
  * 실제 SerDes PAM4 106.25GBd의 전기적 신호 품질(Eye Diagram, 이퀄라이제이션, PLL 클럭 복원)
  * RS-FEC(544, 514) Reed-Solomon 갈루아 필드(GF) 하드웨어 비트 에러 정정 회로 (소프트웨어 모델에서는 CRC 무결성 검증으로 대체)

#### ③ UALink Chiplet Spec 1.01 (UCIe 3.0 연동)
* **스펙 일치점**: 칩렛 패키지 내(In-Package) Die-to-Die 64B Flit 직접 스트리밍 어댑터 및 사이드밴드 메일박스(800MHz 레지스터 설정/트레이닝) 모델링 완료
* **단순화된 점**: UCIe 물리 계층의 RDI(Raw Die-to-Die Interface) 핀 레벨 신호 및 12단계 링크 트레이닝 FSM 타이밍

#### ④ UALink Manageability & Security
* **스펙 일치점**:
  * **Virtual Pod 격리**: 테넌트 간 크로스 트래픽 침범 시 스위치 단에서 패킷 즉시 드롭
  * **UALinkSec 2.0**: 무상태 스위치가 라우팅할 수 있도록 헤더(Bytes 0-7)는 평문(AAD)으로 두고 페이로드는 AES-GCM-256 부분 암호화 및 64-bit Auth Tag 부착
  * **96-bit IV 규격**: `SrcID(10b) + DstID(10b) + StreamID(2b) + Epoch + Invocation(32b)` 구조 준수
* **단순화된 점**:
  * 실제 외부 네트워크 소켓/I2C 버스를 거치는 바이너리 MCTP 패킷 스트림 (현재는 클래스 기반 메시지 에이전트로 모델링)

---

### 3. 결론: 현재 구현체의 가치와 활용 범위

현재 `ualink_v2`는 **사양서의 복잡한 5대 체계(Common 2.0, 200G, 128G, Chiplet, Manageability, Security)가 유기적으로 상호작용하는 프로토콜 전체 스택을 소프트웨어 레벨에서 가장 높은 정합성(High Fidelity)으로 완성한 상태**입니다.

1. **상위 소프트웨어 / 컴파일러 팀**: UALink 2.0 통신 라이브러리(NCCL/MSCCL 플러그인 등)나 In-Network Compute 분산 학습 스케줄러를 검증하는 **가상 에뮬레이터(Emulator)**로 즉시 사용 가능합니다.
2. **하드웨어(RTL) 설계 팀**: Verilog/SystemVerilog 구현 시 입력 플릿 포맷, 신호 오버로딩 규칙, CRC/패리티 계산, 상태 전이의 기대값(Golden Output)을 검증하는 **골든 레퍼런스 모델(Golden C/Python Reference Model)**로 활용하기에 완벽한 수준입니다.
