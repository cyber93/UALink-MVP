
폴더 내에 포함된 원본 표준 문서인 `UALink200_Specification_v1.0_Evaluation_Copy.docx`의 사양을 1:1로 매핑하여 모듈화한 구현체입니다.

---

### 1. 구현 대상 사양 (Specification) 개요

* **공식 표준 명칭**: Ultra Accelerator Link Consortium, Inc. Specification: **UALink_200 Rev 1.0**
* **표준 제정 기관**: UALink Consortium (AMD, Intel, Google, Microsoft, Meta, Cisco, Broadcom, HPE 등이 주도)
* **목적**: 대규모 AI 가속기 클러스터(Scale-Up Pod) 내에서 GPU/NPU 가속기 및 스위치 간 고대역폭, 초저지연, 캐시 일관성 및 메모리 공유(RMA)를 지원하는 개방형 표준 규격

---

### 2. 챕터별 사양 및 구현 내역

`UALink-MVP/ualink/` 패키지 아래에 스펙의 각 장(Chapter)이 다음과 같이 모듈 단위로 구현되어 있습니다.

| 스펙 챕터 | 구현 디렉토리/모듈 | 주요 구현 사양 및 기능 |
| :--- | :--- | :--- |
| **Ch 1. System Overview** | `system/` | • **Pod & Virtual Pod(VPod)**: 최대 1,024개 가속기(`MAX_ACCELERATORS = 1024`) 클러스터 구조 및 가상 격리 파티션<br>• **SystemNode & Accelerator**: 가속기 노드 및 포트 인터페이스<br>• **Address Translation**: GVA(가상주소) → NPA(노드물리주소) → SPA(시스템물리주소) 모델 |
| **Ch 2. UPLI Interface** | `upli/` | • **4개 핵심 채널 구현** (신호 규격 Table 2-2, 2-8, 2-11, 2-14 반영):<br>  - Request Channel (Req)<br>  - Read Response/Data Channel (RdRsp)<br>  - Write Response Channel (WrRsp)<br>  - Originator Data Channel (OrigData)<br>• **Command Encodings** (Table 2-6): Read(`0x03`), Write(`0x28`), WriteFull(`0x29`), UPLI Write Msg(`0x2A`), AtomicR(`0x30`), AtomicNR(`0x32`), Vendor Defined Commands(VDC)<br>• **Credit Manager**: 풀(Pool) 및 VC(Virtual Channel, 2비트) 단위 크레딧 흐름 제어, TDM 지원<br>• **Ordering**: 256B 경계 기준 비엄격 정렬(Relaxed) 및 암호화용 전역 엄격 정렬(Strict) |
| **Ch 3. RAS** | `ras/` | • **에러 카테고리 분류**: UPLI 제어/데이터/프로토콜 에러, 스위치 코어 에러, 링크 다운<br>• **End-to-End Parity**: Even Parity 계산 및 패리티 에러 검출<br>• **Poison Marking**: `RdRspDataError`, `OrigDataError` 신호를 통한 포이즌 전파<br>• **Error Containment**: 격리 모드(`ISOLATE` WrRspStatus `0xF`) 및 트래픽 드롭 처리 |
| **Ch 4. Reset & Init** | `reset/` | • UPLI 리셋 시퀀스 및 초기 연결 핸드셰이크(Handshake, Fig 4-1~4-4)<br>• 채널별 초기 크레딧(Credit Init Done) 동기화 |
| **Ch 5. Transaction Layer (TL)** | `transaction_layer/` | • **64-Byte TL Flit 구조**: 32B Control Half-Flit + 32B Data Half-Flit (총 16 sectors × 4B)<br>• **FTYPE (Field Type) 인코딩** (Table 5-27):<br>  - Uncompressed Req (4 sectors) / Rsp (2 sectors)<br>  - Compressed Req (2 sectors) / Compressed Rsp (1 sector)<br>  - Flow Control / NOP (1 sector)<br>• **Address Compression Cache**: 송수신단 주소 캐시 적중을 통한 64B 정렬 요청 압축 패킹 |
| **Ch 6. Data Link Layer (DL)** | `data_link/` | • **640-Byte DL Flit 구조** (Table 6-1): 3B Flit Header(FH) + 5개 Segment(각 1B Segment Header 포함) + 4B CRC-32 (IEEE 802.3 Clause 3.2.9)<br>• **Link-Level Replay**: 9비트 시퀀스 번호(1~511), TxReplay 송신 버퍼, 수신측 Ack/Replay Request 메커니즘<br>• **DL 메시지 서비스**: TL Rate Notification, Device ID/Port ID 질의, Channel Negotiation<br>• **DL UART Stream**: F/W 간 메시지 교환을 위한 가상 UART 스트림 버퍼 및 2^12 modulo 크레딧 제어<br>• **Link State Machine**: `Fault` → `Idle` → `NOP` → `Up` 상태 전이 |
| **Ch 7. Physical Layer (PHY)** | `physical_layer/` | • **Reconciliation Sublayer (RS)**: 80개의 64B/66B 블록 = 1개 Flit Code Sequence (640B DL Flit에 대응)<br>• **64B/66B Block 인코딩**: Data(01), Sync/Control(10) 및 Start(`0x78`), Idle(`0x1E`), Fault(`0x4B`)<br>• **속도 및 레인 설정**: 100G / 200G / 400G / 800G 인터리브 및 Alignment Marker(AM) 주기 모델 |
| **Ch 8. Manageability** | `manageability/` | • **Pod Controller**: 토폴로지 디스커버리, 가속기 ID(AccID) 할당, Virtual Pod 생성/관리<br>• **Node Agent (NMA) & Switch Agent (SMA)**: 관리 에이전트 인터페이스 |
| **Ch 9. Security (UALinkSec)** | `security/` | • **AES-GCM-256 암호화 및 8B 인증 태그(Auth Tag)**<br>• **96-bit IV(Initialization Vector)**: SrcAccID(10b) + DstAccID(10b) + StreamID(2b) + Epoch + InvocationField(32b)<br>• **3개 독립 스트림**: Request, ReadResponse, WriteResponse<br>• **Key Derivation (KDF)**: NIST SP 800-56C 기반 파생 키 생성 및 Epoch 추적<br>• **Key Swap / Key Roll**: UPLI Write Message를 활용한 키 교체 핸드셰이크<br>• **Partial Field Encryption**: 라우팅 헤더는 평문 유지(Stateless Switch 통과용), 메모리 주소 및 태그만 부분 암호화(AAD/MSG 분리) |
| **Ch 10. Switch Requirements** | `switch/` | • **비상태성(Stateless) 스위칭**: Req/Rsp 트래킹 및 타임아웃 없이 무손실(Lossless) 고속 포워딩<br>• **Routing Table**: Destination AccID → Egress Port 매핑<br>• **Virtual Pod 트래픽 격리**: VPod 간 크로스 트래픽 침범 감지 및 드롭<br>• **Bifurcation**: 스테이션당 x1, x2, x4 포트 분할 지원 |

---

### 3. 동작 검증 및 엔드투엔드 시뮬레이션 흐름

`ualink.simulation.testbench` (`simulation.log`)를 통해 검증된 전체 트랜잭션 수명 주기는 다음과 같이 사양의 전체 스택을 거칩니다:

1. **Physical Link Connection & Reset**: 가속기 A1과 A2의 포트 연결 및 UPLI 연결 핸드셰이크 (`reset/upli_reset.py`)
2. **Credit Initialization**: 풀 크레딧(ReqPool, DataPool) 할당
3. **UPLI Request 생성**: A1(Originator)이 A2(Completer)의 주소(`0xDEADBEEF`)로 Read 커맨드(`0x03`, Tag `42`) 및 Parity 생성
4. **Transaction Layer (TL) Flit 패킹**: 64B TL Flit 생성 (제어 헤더 및 데이터 분할)
5. **Data Link Layer (DL) Framing**: TL 페이로드를 640B DL Flit에 패킹하고 Flit Header(Op=0, Seq) 부착 및 32-bit CRC 계산
6. **Switch Routing**: 스위치 코어가 대상 가속기 ID(AccID=2)를 확인하여 지정된 포트로 무손실 포워딩 (VPod 권한 검사 포함)
7. **Completer DL/TL 파싱**: Completer가 Flit 수신 후 CRC 검증(`PASS`), 64B TL Flit 및 원본 UPLI 요청 복원
8. **Memory Access & Credit Return**: 주소 조회 및 메모리 처리 후 Originator로 크레딧 반환 완료

---

### 요약

`UALink-MVP`는 **UALink_200 Rev 1.0 (2025년 4월 제정)** 사양서의 전 계층(시스템 구조, UPLI 프로토콜, RAS, 리셋 시퀀스, 트랜잭션 계층 플릿 구조, 데이터링크 프레이밍/CRC/리플레이, 물리 계층 RS 인코딩, 관리성, UALinkSec 암호화/인증, 무상태 스위치 라우팅)을 **소프트웨어 레벨에서 완결적으로 모델링하고 검증할 수 있도록 만든 파이썬 기반 UALink 200 레퍼런스 프로토타입**입니다.