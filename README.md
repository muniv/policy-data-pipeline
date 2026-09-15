# research-data-pipeline

LLM 에이전트와 파이썬으로 정책연구 데이터를 **주기적으로 자동 수집·정제·검증·문서화**하는 파이프라인. 경제·인문사회연구회 산하 국책연구기관 연구직 과정 「(고급) LLM Agent 기반 연구 데이터 파이프라인」(2026. 9. 16.)의 실습 저장소입니다.

한 문장으로: **에이전트에게 데이터를 맡기지 말고, 파이프라인을 짜게 하십시오.**

## 바로 실행

```bash
pip install -r requirements.txt
python run.py --offline
```

`--offline`은 `raw/sample/`의 스냅샷을 씁니다. **인터넷과 인증키 없이 전 과정이 돌아갑니다.** 망이 막힌 기관에서도 구조를 먼저 확인할 수 있습니다. 실행이 끝나면 `out/`에 네 가지가 생깁니다.

| 파일 | 용도 |
|---|---|
| `out/panel.csv` | 분석용 패널. 표준 스키마 10개 컬럼 |
| `out/codebook.md` | 데이터셋 사용설명서. 실행할 때마다 다시 생성 |
| `out/dashboard.html` | 단일 파일 대시보드. 서버 불필요 |
| `out/tables/` | 보고서 부록용 표 (마크다운 + 엑셀). 출처·기준시점·단위 자동 표기 |

실시간 수집은 KOSIS 인증키가 필요합니다. `.env` 에 적거나 셸 환경변수로 설정합니다.

```bash
cp .env.example .env        # 파일을 열어 KOSIS_API_KEY= 뒤에 인증키를 붙여넣습니다
python run.py
```

셸 환경변수로 하셔도 됩니다. 셸 값이 `.env` 보다 우선합니다.

```bash
export KOSIS_API_KEY="발급받은_인증키"     # Windows PowerShell: $env:KOSIS_API_KEY="..."
python run.py
```

검증이 실패하면 어떻게 멈추는지 보려면 `python run.py --offline --break-check`.

## 수업 자료

| 교시 | 폴더 | 내용 |
|---|---|---|
| 1교시 | `exercises/01/` | 환경 점검, 첫 에이전트 요청, 응답 구조 함정, 소스 점검표 |
| 2교시 | `exercises/02/` | API 문서 → 명세서 → 실제 호출 검증, **MCP로 KOSIS 표 찾기**, 결정표 |
| 3교시 | `exercises/03/` | 세 소스 각각: API(장애 주입, 세 형식) · 웹크롤링(픽스처 v1/v2) · 내부 엑셀(2단계 변환) |
| 4교시 | `exercises/04/` | 세 갈래 붙이기, 검증, 지표 추가 전체 사이클, 주기 갱신, 보고서용 표 |

각 폴더의 `README.md`에 Claude Code에 붙여넣을 프롬프트가 순서대로 있습니다. **에이전트 없이 따라오는 분은 각 프롬프트 아래 `관전 트랙` 상자를 보세요** — `python exercises/0N/offline_tour.py` 로 같은 내용을 확인하고, claude.ai 무료 웹에서 할 수 있는 것도 함께 적어두었습니다. `reference/`는 에이전트 출력이 이상할 때 대조하는 참고본입니다.

## 실습 환경

VS Code + Claude Code + Python 3.10 이상. 저장소를 VS Code로 열고 터미널에서 `claude`를 실행합니다.

- `CLAUDE.md` : 에이전트 규칙 파일. 원칙 · 코드체계 · 중단 조건 · 자주 쓰는 명령
- `SKILL.md` : 지표 추가 · 정기 갱신 절차
- `.mcp.json` : KOSIS MCP 서버 등록 (선택). 키는 환경변수 `KOSIS_API_KEY`에서 읽습니다

MCP 실습은 선택입니다. `exercises/02/mcp-kosis.md` 참고.

## 구조

```
CLAUDE.md · SKILL.md · .mcp.json
config/sources.yml          수집 대상 정의 ← 지표 추가는 여기
references/
  api-registry.md           소스별 요청 명세 ← 다른 기관으로 옮길 때 여기
  schema.md                 표준 스키마와 중단 조건
  region-codes.csv          지역명 → 코드 사전
scripts/
  collect.py                수집. 재시도·백오프·조용한 실패 탐지
  normalize.py              표준 스키마 변환. 규칙 우선, 판단은 기록
  validate.py               검사와 중단 조건
  report.py                 패널·코드북·대시보드·보고서용 표 생성
  make_samples.py           오프라인 스냅샷 생성기 (수업용)
raw/sample/                 오프라인 스냅샷
exercises/01~04/            교시별 프롬프트·픽스처·참고본
run.py                      전체 실행
```

## 표준 스키마

```
source | indicator_code | region_code | period | value | unit | vintage | retrieved_at | source_url | missing_reason
```

결측은 `NA_NOTSURVEYED`(미조사) · `NA_NOTAPPLICABLE`(해당없음) · `NA_CONFIDENTIAL`(비공개) 셋으로 구분합니다. 정의와 중단 조건은 `references/schema.md`.

## 우리 기관 지표로 바꾸기

1. `references/api-registry.md`에 우리 소스의 명세를 등록합니다 (실제 호출 1건으로 검증 후)
2. `config/sources.yml`에 지표를 추가합니다
3. `scripts/normalize.py`에 변환 함수를 하나 추가합니다

`collect.py`, `validate.py`, `report.py`는 손대지 않습니다.

## 주의

- 샘플 데이터의 시도별·국제 비교 수치는 구조 확인용입니다. 전국 합계출산율만 KOSIS 공표치입니다. 실제 수집으로 갈아끼우고 쓰세요
- 세종 2016년 값에는 검증 경고를 보여주기 위한 급변이 일부러 심어져 있습니다
- OECD는 접근 경로 개편 이력이 있습니다. 사용 전 실제 호출로 확인하세요
- MCP 서버는 전부 커뮤니티 프로젝트입니다. 설치 전 코드와 보안 스캔을 확인하고, 키는 환경변수에만, 내부 자료는 도구에 넘기지 않습니다
- `exercises/` 밖의 실제 내부 자료를 에이전트에 읽히기 전에 기관 규정과 데이터 등급을 확인하세요

## 라이선스

코드는 MIT. 샘플 데이터와 픽스처는 수업용이며 실제 통계가 아닙니다. 인용하지 마세요.
