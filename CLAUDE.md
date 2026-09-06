# research-data-pipeline

정책연구용 데이터 파이프라인. 국내외 공공·국제기구 통계를 수집해 표준 스키마 패널로 만들고, 검증·코드북·대시보드·보고서용 표를 자동 생성한다.

## 이 저장소에서 지킬 것

**값을 읽지 말고, 값을 읽는 코드를 쓴다.** API 응답이나 파일에서 숫자를 직접 옮겨 적지 않는다. 항상 스크립트가 파싱하고, 그 출력을 확인한다. MCP 도구로 받은 값도 마찬가지다. 도구는 탐색·조회·검증용이고, 수집은 `scripts/collect.py`가 한다.

**검증에 실패하면 멈춘다.** `scripts/validate.py`의 중단 조건에 걸리면 산출물을 만들지 않는다. 검사를 느슨하게 고쳐 통과시키지 않는다. 임계값을 바꿔야 한다면 근거를 말하고 사용자 확인을 받는다.

**판단한 건은 기록한다.** 규칙(사전)으로 처리하지 못해 판단이 들어간 매핑은 코드북 4절에 미확인으로 남긴다. 확정은 사용자가 한다. 확정된 뒤에만 사전 파일에 등록한다.

**결측은 세 가지다.** `NA_NOTSURVEYED`(미조사) · `NA_NOTAPPLICABLE`(해당없음) · `NA_CONFIDENTIAL`(비공개). 빈칸 하나로 뭉개지 않는다. 사유를 모르면 사용자에게 묻는다.

**내부 자료는 함부로 읽지 않는다.** `exercises/` 밖의 엑셀·CSV를 읽기 전에 그 파일이 외부로 나가도 되는 자료인지 사용자에게 확인한다.

## 표준 스키마

```
source | indicator_code | region_code | period | value | unit | vintage | retrieved_at | source_url | missing_reason
```

정의와 중단 조건: `references/schema.md`

## 코드체계

- 국내 지역: `KR-` + 행정구역코드 2자리. 사전은 `references/region-codes.csv`. 사전에 없는 지역명은 임의로 매핑하지 말고 멈춘다.
- 국가: ISO 3166-1 alpha-3.
- 기간: 연도 정수. 분기·월은 소스 설정에 적힌 방식으로 연 단위 집계.
- 단위: `unit` 컬럼에 기록. 환산은 `normalize.py`에서만.

## 소스 우선순위

같은 지표가 여러 소스에 있으면 `references/api-registry.md`에 적힌 순서를 따른다. 국내 지표는 KOSIS, 국제 비교는 World Bank → OECD 순.

## 자주 쓰는 명령

```bash
python run.py --offline          # 스냅샷으로 전 과정 (인증키 불필요)
python run.py                    # 실시간 수집 (KOSIS_API_KEY 필요)
python run.py --offline --break-check   # 검증 실패 시 멈추는 장면
```

## 새 지표를 추가할 때

`SKILL.md`의 절차를 따른다. 요약: 레지스트리 확인 → `config/sources.yml` 추가 → `normalize.py`에 변환 함수 → 허용 범위 등록 → `--offline` 실행 → 검증 → 산출물 확인 → 추가 행 수와 확인 필요 항목 보고.
