# 딥러닝 기말 프로젝트 학습 내용 종합 정리

> 이 문서는 대화에서 공유된 모든 자료(수업 내용 정리, 주차별 커리큘럼 연계 전략, 예시 프로젝트 6종, 과제 요구사항, 선정 주제)를 재구성한 레퍼런스입니다.

---

## 📌 Part 1. 과제 기본 정보

### 제출 조건

- **과목**: 딥러닝실습 (인공지능학과 구영현 교수)
- **대체 시험**: 중간고사 → 기말 프로젝트 계획서 제출
- **제출 기한**: 4월 19일 23:59
- **양식**: PPT
- **팀 구성**: 1인 1프로젝트 권장 (2인 이상이면 난도/완성도 부담 증가)
- **제출 방법**: 온라인 제출 (집현캠퍼스)
- **평가 방식**: 상대평가 — **완성도 + 구체성 + 실현 가능성**

### 필수 목차 (9개)

1. 프로젝트 개요
2. 프로젝트 구성도 (Architecture, Flow chart)
3. 사용할 데이터셋
4. 데이터 전처리
5. 사용할 모델들 소개
6. 성능평가 방안
7. 개발 일정
8. 활용 방안
9. 참고문헌 (reference)

### 선정 주제

**"냉장고 안 음식 사진 → 레시피 추천 딥러닝 end-to-end 시스템"**

---

## 📚 Part 2. 수업 내용 종합 정리

### 1. 머신러닝 아키텍처 & MLOps

#### 1-1. 머신러닝 시스템은 모델 하나가 아니다

프로젝트는 **데이터 수집 → 정제 → 레이블링 → 분석/시각화 → 피처 엔지니어링 → 모델 설계 → 학습 → 검증 → 성능 개선 → 배포**가 연결된 전체 워크플로우.

#### 1-2. 데이터 준비가 진짜 오래 걸린다

실제 프로젝트 시간의 대부분이 데이터 준비 단계(수집, 라벨링, 이상치 처리, 클래스 불균형 확인, 누락값 처리, 시각화)에 소요됨.

#### 1-3. 데이터 품질이 성능을 좌우한다

핵심 키워드:

- 합성 데이터 (synthetic data)
- Corner case / Edge case
- Data drift
- Data imbalance

"재밌는 문제"보다 **"데이터를 확보하고 설명할 수 있는 문제"**가 성공 확률이 높음.

#### 1-4. 성능 개선의 두 방향

- **Data-Centric**: 데이터 수, 품질, 특징 개선
- **Model-Centric**: 구조 변경, 파라미터 튜닝, 더 좋은 알고리즘

성능 안 나오면 **먼저 데이터 품질과 분포를 점검**할 것.

#### 1-5. 배포 방식 3가지

- **배치 인퍼런스**: 모아서 한 번에 예측 (예: 주기적 수요 예측)
- **온라인 인퍼런스**: 실시간 예측 (예: 실시간 이미지 분류 웹앱)
- **에지 인퍼런스**: 디바이스에서 직접 추론 (예: 모바일 앱)

#### 1-6. MLOps 핵심 요소

- **CI**: 코드 변경 자동 테스트
- **CD**: 배포 자동화
- **IaC**: 인프라를 코드로 관리
- **Monitoring**: 배포 후 감시
- **Data Management**: 데이터 버전/품질 관리

학생 프로젝트에서 MLOps 감점 방지 포인트:

- 모델 버전 관리
- 실험 로그 저장
- 학습/추론 코드 분리
- 재현 가능한 requirements 정리
- 데모 앱 제공

---

### 2. 파이토치 기초

- 파이토치는 텐서 기반 딥러닝 프레임워크
- 모든 데이터(이미지, 텍스트, 시계열)가 결국 Tensor로 처리됨
- 핵심 문법: 텐서 생성/shape/dtype/device, reshape/view, indexing, NumPy 변환, autograd, nn.Module, loss/optimizer/backward/step
- 환경 관리: GPU/CPU, 패키지 버전 고정, 재현성
- 모델 구조: 클래스 정의 → forward 구현 → 학습 루프

---

### 3. 파이토치 심화 (프로젝트 성능 개선의 핵심)

#### 3-1. 과대적합 / 과소적합 구분


| 구분   | 특징                | 처방                    |
| ---- | ----------------- | --------------------- |
| 과대적합 | train 좋음 / val 나쁨 | 정규화, 드롭아웃, 증강, 데이터 추가 |
| 과소적합 | train도 val도 나쁨    | 모델 복잡도 ↑, 학습 시간 ↑     |


→ 항상 train/val loss & acc를 같이 봐야 함.

#### 3-2. 배치 정규화 (Batch Normalization)

- 각 미니배치 기준 평균/분산 정규화
- 효과: 학습 안정화, 큰 학습률 사용 가능, 수렴 속도 향상, 초기값 민감도 감소
- 변형: LayerNorm, InstanceNorm, GroupNorm (데이터 형태와 배치 크기에 따라 선택)

#### 3-3. 가중치 초기화

- **상수 초기화**: 대칭성 문제로 비추천
- **Xavier / Glorot**: sigmoid, tanh 계열에 적합
- **He / Kaiming**: ReLU 계열에 적합 ← **CNN에서 표준**
- **Orthogonal**: RNN 계열에 유리

#### 3-4. 정칙화 (Regularization)


| 기법                | 설명                                       |
| ----------------- | ---------------------------------------- |
| L1                | 가중치를 0으로 보내 희소성 유도, 특징 선택 효과             |
| L2                | 가중치 전반을 작게 유지, 특정 특징 과의존 방지              |
| Weight Decay      | Optimizer의 `weight_decay` 파라미터, 실질적으로 L2 |
| Dropout           | 학습 시 일부 노드 랜덤 비활성화, 노드 간 의존성 감소          |
| Gradient Clipping | 기울기 폭주 방지, RNN/LSTM에서 특히 중요              |


#### 3-5. 데이터 증강 (Augmentation)

**텍스트**: 삽입, 삭제, 교체, 대체, 역번역 (문맥 훼손 주의)

**이미지**: 회전/대칭, crop/pad, resize, affine/perspective, color jitter, noise, cutout/random erasing, **mixup/cutmix**, blur/compression

→ 데이터 적을수록 증강 전략이 성능을 크게 좌우함.

#### 3-6. 사전학습 모델 & 전이학습 (Transfer Learning)


| 상황              | 전략          |
| --------------- | ----------- |
| 데이터 적음 + 유사성 큼  | 분류기만 학습     |
| 데이터 적음 + 유사성 작음 | 일부 계층만 미세조정 |
| 데이터 많음 + 유사성 큼  | 뒤쪽 계층 + 분류기 |
| 데이터 많음 + 유사성 작음 | 거의 전체 재학습   |


---

### 4. 모델 경량화

#### 4-1. Pruning (가지치기)

- **비정형 가지치기**: 개별 weight를 0으로
- **정형 가지치기**: 필터/채널 단위 제거 (실제 연산량 감소에 효과적)

#### 4-2. Quantization (양자화)

- 32-bit float → 16-bit, 8-bit 등으로 축소
- 종류: 정적 / 동적 / 학습 후 / **QAT(양자화 인식 학습)**

#### 4-3. Knowledge Distillation (지식 증류)

- 큰 teacher 모델의 지식을 작은 student 모델로 전이
- 예: ResNet teacher → 작은 CNN student

#### 4-4. Tensor Decomposition

- SVD, CP decomposition으로 가중치 텐서 분해
- 고급 주제 — 넣으면 깊이 있어 보이지만 구현 부담 큼

#### 4-5. ONNX

- 프레임워크 간 호환 가능한 중립 포맷
- "다른 환경에서 실행 가능한 모델" 증명용

---

### 5. 모델 서빙 / Docker / Streamlit

#### 5-1. 서빙 프레임워크 비교


| 프레임워크         | 특징                    | 용도          |
| ------------- | --------------------- | ----------- |
| Flask         | 가볍고 빠른 프로토타입          | 간단한 API     |
| Django        | 무겁지만 기능 풍부            | 큰 서비스       |
| **FastAPI**   | 빠르고 비동기 처리, 자동 API 문서 | **현대적 API** |
| **Streamlit** | Python만으로 UI 구현       | **데모 앱**    |


#### 5-2. Docker 핵심 가치

- 환경 격리
- 종속성 관리
- 이식성
- 확장성
- 유지보수성

→ "내 컴퓨터에서만 되는 코드" 탈출.

#### 5-3. 추천 조합

```
모델 학습: PyTorch
데모 앱: Streamlit
API 서빙: FastAPI
배포 환경: Docker
```

---

## 📅 Part 3. 주차별 커리큘럼 연계 전략

### 수업 주차표와 프로젝트 매핑


| 주차         | 수업 내용                                        | 프로젝트 연계 포인트        |
| ---------- | -------------------------------------------- | ------------------ |
| Week 4     | 인공신경망 기초, 성능지표                               | Baseline 모델, 평가 지표 |
| Week 5     | Dropout / Activation / Normalization         | 성능 개선 실험           |
| Week 6     | Initialization / Optimizer / AutoEncoder     | 학습 안정화 비교          |
| Week 7     | MLP / CNN / Data Augmentation                | **이미지 프로젝트 핵심**    |
| Week 9     | CNN Architecture / Transfer Learning         | **사전학습 모델 활용**     |
| Week 10~11 | NLP (Tokenization, Embedding 등)              | 텍스트/레시피 매칭         |
| Week 12    | Object Detection / Segmentation / AutoML     | 이미지 고급 프로젝트        |
| Week 13    | GAN / Domain Adaptation / Continual Learning | (메인 지양, 확장 아이디어)   |
| Week 14~15 | Flask / Docker / Postman / 모델 서빙             | **최종 결과물 완성도**     |


### 교수님이 선호할 가능성이 높은 프로젝트 형태

> **"이미지 분류 + 성능 개선 실험 + 전이학습 + 데모/서빙"** 조합
> → CNN, augmentation, dropout/normalization, initialization/optimizer, transfer learning, 성능평가, 모델 서빙, Docker까지 수업 내용을 최대한 녹일 수 있음.

### 지양할 메인 주제 (확장 아이디어로는 가능)

- GAN 메인 프로젝트
- Meta Learning 메인
- 강화학습 메인
- Continual Learning 메인
- Domain Adaptation 메인
- Detection/Segmentation을 처음부터 메인으로 (데이터/학습 부담)

### 주제 선정 체크리스트 (6가지)

1. CNN 또는 NLP 수업 내용과 직접 연결되는가?
2. Dropout, Normalization, Augmentation, Transfer Learning을 넣을 수 있는가?
3. 성능 비교 실험이 가능한가?
4. 데이터셋을 쉽게 구할 수 있는가?
5. 결과를 시각적으로 보여주기 쉬운가?
6. Flask/Streamlit/Docker까지 확장 가능한가?

### 계획서에 넣으면 좋은 수업 연계 키워드

**이미지 프로젝트**:

- CNN 기반 feature extraction
- Data augmentation을 통한 일반화 성능 향상
- Batch Normalization과 Dropout을 통한 과대적합 방지
- Weight initialization 및 optimizer 설정 비교
- Transfer learning을 활용한 성능 개선
- Flask 또는 Streamlit을 활용한 데모 시스템 구현
- Docker 기반 배포 가능성 검토

**NLP 프로젝트**:

- Tokenization 및 OOV 처리
- Word embedding 기반 표현 학습
- 사전학습 언어모델 fine-tuning
- 텍스트 데이터 증강 실험
- REST API 기반 텍스트 분류 데모 구축

---

## 🗂️ Part 4. 예시 프로젝트 6종 Workflow 정리

### 1. 피부 이미지 분류 기반 스킨케어 프로젝트

**핵심 흐름**: 피부 이미지 → CNN/ViT 증상 분류 → 제품/리뷰 메타데이터 연결 → FastAPI/Streamlit 서비스화 → Docker 배포

**기술 스택**:

- 모델: EfficientNetV2 (local feature) + ViT (global feature)
- 환경: Google Colab + PyTorch
- 서빙: FastAPI + Streamlit + Docker
- DB: JSON / PostgreSQL
- 평가: Accuracy, Precision, Recall, F1-score (목표: 전체 90%+, 증상별 F1 0.85+)

**분류 대상**: 주름, 탄력, 모공, 색소침착

**메타데이터 처리**: 화장품 200~~300개 크롤링, 리뷰당 50~~80개, 가격 수치화, 광고성 리뷰 필터링, 피부타입/효능 태그 생성

---

### 2. 하이라이트 기반 PDF 요약본 생성 프로젝트

**핵심 흐름**: PDF 업로드 → 하이라이트 추출 → 형태 분류 (ResNet-18) → OCR (TrOCR) → 규칙 기반 문장 구조화 → Word/PDF 요약본 생성

**하이라이트 형태 분류 (4종)**:

- `circle` → 대주제
- `wave` → 소주제 (주어)
- `line` → 문장 (설명)
- `break` → 줄바꿈

**OCR 모델 (TrOCR)**:

- 데이터셋: SynthText (pretraining), ICDAR 2015, DocBank
- 목표: CER ≤ 0.05, WA ≥ 0.90

**시스템 아키텍처 (Layered)**:

- Client Layer: React Web UI
- Application Layer: FastAPI Controller
- AI Core Layer: ResNet-18 + TrOCR + Sentence Structuring Engine
- Storage Layer: local storage + summary archive + log DB
- Infrastructure Layer: Docker + reverse proxy + cloud server

---

### 3. 인간지향적 AGI 윤리적 추론 연구

**핵심 흐름**: 윤리 상황 입력 → 초기 CoT 생성 → 외부 규범 검색 (RAG) → Reflection 자기검토 → 규범 구조화 → 최종 판단

**데이터셋**: MORALISE (13개 윤리 범주 — Integrity, Sanctity, Care, Harm, Fairness, Reciprocity, Discrimination, Authority, Justice, Liberty, Respect, Responsibility 등)

**학습 기법**:

- ICL + RAG (초기 성능 확보)
- SFT + RLHF (확장 단계)

**평가**: GPT-4o, Qwen, Gemma 등과 benchmarking

---

### 4. 입-가이드 음성분리 자막 프로젝트

**핵심 흐름**: 비디오+오디오 → 입 영역 추출 & 시간 정렬 → 오디오 분리기 + FiLM 시각 가이드 → 타깃 화자 분리 → Whisper 자막 생성

**데이터셋**:

- Train/Val: RAVDESS + GRID (2-Mix 합성)
- Test: LRS3-2Mix

**아키텍처 핵심**:

1. Read video → extract audio (16kHz) & lip ROI
2. Landmarks → L(t)
3. τ estimate → L(t-τ) (시간 정렬)
4. FiLM adapter → (γ, β)
5. Guidance gating (신뢰도 기반)
6. Separator
7. Output separated tracks
8. Optional: Whisper ASR

**평가 지표**: SDR(dB), STOI, PESQ, WER

**Ablation**: 오디오만 / +FiLM / +FiLM+게이팅 / +FiLM+게이팅+지연보정

---

### 5. MUSEED: AI 플레이리스트 자동 생성 플랫폼

**핵심 흐름**: FMA 수집 → MuQ-MuLan으로 태그/임베딩 생성 → 부분 파인튜닝 + Triplet 학습 → FAISS 인덱싱 → seed 음악 유사곡 검색

**데이터셋**: FMA (fma_full) — 90,192개 mp3, 161개 세부 장르, 16개 최상위 장르

**태그 생성 (다각도)**: Genre, Affect, Mood_style, Energy, Timbre

**모델**: MuQ-MuLan (Music-Text Contrastive Learning)

**파인튜닝 전략**:

- **부분 파인튜닝**: Conformer 12블록 중 앞 6개 freeze, 뒤 6개 + linear만 학습
- **Triplet Loss + Hard Negative Mining**: anchor/positive/negative 삼중항으로 임베딩 공간 재배치
- Weighted sampling으로 장르 불균형 해소

**시스템 구성**: Frontend + FastAPI Backend + Embedding Extractor + PostgreSQL + FAISS Vector DB

**평가**: k-NN 분류 정확도, 실루엣 계수, Triplet loss, t-SNE 시각화, 정성 평가

---

### 6. HoloTouch: 동적 제스처 기반 공간 AR UI

**핵심 흐름**: Jester 비디오 → MediaPipe 랜드마크 시퀀스 → TCN 학습 → ONNX 변환 → Unity Sentis 추론 → AR UI 상호작용

**데이터셋**: Jester (Qualcomm, 148,092개, 27클래스) — Swipe, Push, Pull 중심

**전처리 파이프라인**:

1. MediaPipe로 프레임별 손 랜드마크 21개 추출
2. x, y 좌표 42개 값 생성
3. 손목(0번) 기준 상대좌표 변환
4. 손바닥 크기 기준 정규화
5. 시퀀스 길이 T=30프레임 고정 (padding/truncating)
6. .npy/.npz 텐서 저장

**모델**: TCN (Temporal Convolutional Network) — 1D CNN 속도 + RNN 장기 의존성

**배포**: ONNX → Unity Sentis → MediaPipe API (실시간 AR)

---

## 🎨 Part 5. 예시 프로젝트 공통 패턴 (계획서 작성 시 참고)

1. **명확한 문제 정의 + 사용자 시나리오**
2. **데이터셋 출처와 규모를 구체적 숫자로 제시** (예: 9,767장, 90,192개 mp3, 148,092개 비디오)
3. **모델 2개 이상 비교** (baseline vs proposed, 또는 global vs local feature)
4. **Layered Architecture 다이어그램** (Client / Application / AI Core / Storage / Infra)
5. **정량 지표 + 정성 평가 조합**
6. **FastAPI + Streamlit + Docker 3단 세트가 기본값**
7. **Ablation 또는 단계별 개선 실험**으로 개선 근거 제시

---

## 🍳 Part 6. 선정 주제 분석: 냉장고 → 레시피 추천

### 주제 적합성 평가 (수업 활용도 관점)


| 수업 요소                        | 연계 가능성                            |
| ---------------------------- | --------------------------------- |
| CNN                          | ✅ 필수                              |
| Object Detection             | ✅ 냉장고 내 다중 재료 탐지 (Week 12)        |
| Transfer Learning            | ✅ YOLOv8, EfficientNet 등 (Week 9) |
| Data Augmentation            | ✅ 조명/각도/배치 다양성 (Week 7)           |
| NLP/임베딩                      | ✅ 레시피 매칭 (Week 10~11)             |
| FastAPI + Streamlit + Docker | ✅ 자연스러운 연결 (Week 14~15)           |
| 시각적 데모                       | ✅ 발표 임팩트 큼                        |


### 공개 데이터셋 후보

- **Food-101**: 101 food categories
- **Roboflow Ingredients Detection**: YOLO용 재료 탐지
- **Recipe1M+**: 대규모 레시피 + 이미지
- **AI Hub 한국 식품/재료 데이터셋**: 한국어 레시피에 유리

### 두 가지 핵심 갈림길

**1. 재료 인식 방식**

- Object Detection 중심 (YOLOv8 등 여러 재료 동시 탐지)
- Classification 중심 (크롭된 재료 각각 분류)
- Detection + Classification 2단계 파이프라인

**2. 레시피 매칭 방식**

- 규칙 기반 (재료 집합 → DB 검색)
- 임베딩 유사도 (FAISS 벡터 검색)
- LLM/GPT API 조합 (재료 → 프롬프트 → 레시피 생성)

### 유사 참고 사례

**"피부 분석 + 제품 추천"** 프로젝트 구조가 거의 동일:

- 이미지 분류 (피부 증상 / 재료)
- 메타데이터 매칭 (화장품 / 레시피)
- FastAPI + Streamlit 서비스화

---



### 실제 프로젝트 2개월 실행 로드맵

**Month 1 — 기획 & 데이터 파이프라인**

- Week 1: 문제 정의, 논문 서베이, 데이터셋 확보
- Week 2: EDA, 전처리 파이프라인 (Albumentations)
- Week 3: Baseline 모델 (ResNet50 / YOLOv8n) 학습
- Week 4: 실험 관리 (WandB/MLflow) 세팅 + 중간 리포트

**Month 2 — 모델 개발 & 고도화**

- Week 5-6: 아키텍처 실험 (EfficientNet, ViT, YOLOv8m)
- Week 8: 하이퍼파라미터 튜닝, Grad-CAM 설명가능성
- Week 8: 하이퍼파라미터 튜닝, Grad-CAM 설명가능성

**Month 3 — 백엔드 API 개발**

- Week 9: FastAPI 엔드포인트 설계 (`/predict`, `/health`, `/batch`)
- Week 10: 서빙 최적화 (ONNX, TorchScript, 배치 추론)
- Week 11: Streamlit 프론트엔드 (업로드, 시각화, 대시보드)
- Week 12: 통합 테스트, 로깅, 에러 핸들링

**Month 4 — 배포 & 마무리**

- Week 13: Dockerfile + docker-compose (GPU 옵션)
- Week 14: CI/CD (GitHub Actions), 모니터링 (Prometheus/Grafana)
- Week 15: 클라우드 배포 (AWS EC2 / GCP) + 도메인 연결
- Week 16: README, 시연 영상, 발표자료, 블로그 포스팅
**Month 3 — 백엔드 API 개발**

- Week 9: FastAPI 엔드포인트 설계 (`/predict`, `/health`, `/batch`)
- Week 10: 서빙 최적화 (ONNX, TorchScript, 배치 추론)
- Week 11: Streamlit 프론트엔드 (업로드, 시각화, 대시보드)
- Week 12: 통합 테스트, 로깅, 에러 핸들링

**Month 4 — 배포 & 마무리**

- Week 13: Dockerfile + docker-compose (GPU 옵션)
- Week 14: CI/CD (GitHub Actions), 모니터링 (Prometheus/Grafana)
- Week 15: 클라우드 배포 (AWS EC2 / GCP) + 도메인 연결
- Week 16: README, 시연 영상, 발표자료, 블로그 포스팅

### C. 핵심 기술 스택

- **모델링**: PyTorch, torchvision, timm, ultralytics (YOLOv8)
- **실험관리**: WandB 또는 MLflow
- **백엔드**: FastAPI, Pydantic, Uvicorn
- **프론트엔드**: Streamlit (plotly 포함)
- **배포**: Docker, docker-compose, Nginx
- **테스트**: pytest, locust

### D. 최종 산출물 체크리스트

- GitHub 레포 (README + 폴더 구조)
- 학습된 모델 가중치 + 학습 리포트
- 배포된 데모 URL
- 기술 블로그 포스팅 2-3편
- 시연 영상 (3-5분)

---

## 📦 Part 7-1. 냉장고 AI 프로젝트 — 배포 완료 현황

> 이 프로젝트에 실제 적용된 배포 요약. 상세 명령은 [`../README.md`](../README.md) · [`fridge-recipe-plan-v3.md`](fridge-recipe-plan-v3.md) §5.7.

### 세 가지 실행 방법

| 방법 | 용도 | 접속 |
|------|------|------|
| **로컬 개발** | 코드 수정 | `run_api.py` + `run_ui.py` |
| **Docker Compose** | 재현성·리허설 | http://127.0.0.1:8501 |
| **Cloud Run** | 발표·공개 시연 | https://fridge-ui-579587565890.asia-northeast3.run.app |

### 배포 아키텍처

```
동일 Docker 이미지 (best.pt + FastAPI + Streamlit)
    ├── 로컬: docker-compose → fridge-api + fridge-ui
    └── GCP:  Cloud Build → Artifact Registry → Cloud Run 2서비스
```

- **GCP 프로젝트**: `fridge-ai-demo` · **리전**: 서울 (`asia-northeast3`)
- UI 컨테이너는 `API_URL` 환경변수로 API Cloud Run URL 호출 (로컬 Docker의 `http://api:8000`과 동일 역할)

---

## 🧭 Part 8. 프로젝트 작성 시 핵심 원칙

### 계획서 단계에서 반드시 기억할 5가지

1. 프로젝트는 **모델 성능만으로 평가되지 않는다** — 데이터 준비, 일반화, 배포, 설명가능성까지 중요
2. **데이터가 부족하면 전이학습과 데이터 증강이 핵심** — 처음부터 큰 모델 학습은 비효율
3. **성능이 안 나오면 원인 먼저 진단** — 과대적합/과소적합/데이터 문제/모델 문제 구분
4. **일반화 도구들을 적극 활용** — BN, 초기화, L1/L2, weight decay, dropout, augmentation, early stopping
5. **마지막에 보여줄 수 있어야 좋은 프로젝트** — Streamlit, FastAPI, Docker, Cloud Run (냉장고 AI는 **Cloud Run 배포 완료**)

### 계획서 단계에서 피해야 할 함정

- 멋있어 보이는 고급 기법을 메인으로 박기 (GAN, 강화학습, 메타러닝)
- 데이터 확보 경로가 불분명한 주제
- 성능 비교 실험을 설계하기 어려운 주제
- 시각화/데모가 어려운 주제
- 2개월 내 완성 불가능한 스케일

---

*이 문서는 이후 PPT 계획서 작성, 프로젝트 구체화, 실행 단계에서 지속적으로 참고할 수 있도록 구성되었습니다.*