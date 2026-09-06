# 표준 스키마

모든 소스는 결국 이 한 벌로 수렴합니다. 소스가 늘어도 이 모양은 바뀌지 않습니다.

```
source | indicator_code | region_code | period | value | unit | vintage | retrieved_at | source_url | missing_reason
```

| 컬럼 | 타입 | 규칙 |
|---|---|---|
| `source` | 문자 | 출처 기관 코드. `config/sources.yml` 에 정의된 값 |
| `indicator_code` | 문자 | 소스의 원 코드를 그대로 유지. 임의로 바꾸지 않음 |
| `region_code` | 문자 | 국내 `KR-`+행정구역코드 2자리, 국외 ISO 3166-1 alpha-3 |
| `period` | 정수 | 관측 연도 (YYYY). 1900~2100 |
| `value` | 실수 또는 공백 | 공백이면 `missing_reason` 필수 |
| `unit` | 문자 | 단위 |
| `vintage` | 문자 | 확정 / 잠정 / 추계 / 연간 |
| `retrieved_at` | 문자 | ISO 8601, KST |
| `source_url` | 문자 | 해당 값을 얻은 요청 주소 |
| `missing_reason` | 문자 또는 공백 | `NA_NOTSURVEYED` / `NA_NOTAPPLICABLE` / `NA_CONFIDENTIAL` |

## 결측을 셋으로 나누는 이유

| 코드 | 의미 | 분석에서 |
|---|---|---|
| `NA_NOTSURVEYED` | 미조사 | 보간 검토 가능 |
| `NA_NOTAPPLICABLE` | 해당없음 | 보간 금지 |
| `NA_CONFIDENTIAL` | 비공개 | 값은 존재. 다른 경로 검토 |

수집 시점에만 알 수 있는 정보입니다. 그때 안 적으면 이후에 복원할 방법이 없습니다.

## 중단 조건

아래 검사에 실패하면 파이프라인이 멈추고 산출물을 만들지 않습니다.

- 수집 행 수 0
- 표준 스키마 컬럼 누락
- 중복 키 (`indicator_code` + `region_code` + `period`)
- 지표별 값 범위 이탈
- 시도 17개 미충족
- 기간 연속성 위반
- 사유 없는 결측

아래는 기록만 하고 진행합니다. 원자료가 실제로 그럴 수 있기 때문입니다.

- 전년 대비 변화율 30% 초과
- 전국값과 시도 평균의 괴리
