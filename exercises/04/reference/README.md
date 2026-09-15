# 4교시 참고본 · 지표 추가 완성본

16:10 시연의 정답지입니다. 에이전트가 만든 결과가 이상할 때 대조합니다.

## 시연 전에 한 번 (강사용)

출생아수 스냅샷을 먼저 만들어 둡니다. 없으면 `--offline` 실행이 샘플을 못 찾고 멈춥니다.

```bash
python exercises/04/reference/make_births_sample.py
# raw/sample/kosis_births.json · 198건
```

## 시연

```
> KOSIS 출생아수 지표를 파이프라인에 추가해. SKILL.md 절차대로 진행해.
```

에이전트가 밟아야 할 순서와, 각 단계에서 실제로 바뀌는 파일입니다.

| | 단계 | 건드리는 파일 |
|---|---|---|
| 1 | 레지스트리 확인 | `references/api-registry.md` (읽기만) |
| 2 | 소스 항목 추가 | `config/sources.yml` |
| 3 | 변환 함수 | **추가 없음** — 아래 설명 |
| 4 | 허용 범위 등록 | `config/sources.yml` 의 `value_range` |
| 5 | 스냅샷 실행 | `python run.py --offline` |
| 6 | 검증 | 통과해야 7단계로 |
| 7 | 산출물 갱신 | `out/` 전체 |

## 3단계에 관하여 — 이 강의에서 가장 중요한 장면

`scripts/normalize.py` 는 소스 id 가 `kosis` 로 시작하면 `from_kosis` 로 보냅니다.
출생아수 표는 합계출산율 표와 응답 형태가 같으므로 **변환 함수를 새로 쓸 필요가 없습니다.**

에이전트가 `from_kosis_births` 같은 함수를 새로 만들려 하면 멈추고 물어보십시오.
같은 기관의 같은 응답 형태에 함수를 하나씩 늘리면, 3년 뒤 이 파일은 손댈 수 없게 됩니다.
**소스가 늘어도 스크립트는 그대로**라는 것이 이 구조의 요점입니다.

## 기대 결과

```
[2/4] 정규화
  [kosis_tfr] 198행
  [kosis_births] 198행
  [wb_tfr] 77행
  [policy_brief] 17행
[3/4] 검증
  통과 8 / 확인 1 / 실패 0
완료 · 490행
```

292행에서 **490행**으로 늘어납니다. `out/dashboard.html` 을 새로고침하면 지표가 하나 더 보입니다.

## 되돌리기

시연을 다시 하려면 `config/sources.yml` 에서 `kosis_births` 항목과 `BIRTHS` 범위를 지웁니다.
`raw/sample/kosis_births.json` 은 남겨둬도 됩니다.
