# 2교시 · API 문서 분석과 요청 구문 설계

10:30~11:30. 언어모델을 처음 도구로 씁니다. 대화 상대가 아니라 **문서 파서**로 씁니다.

## 1. 명세서 양식 (10:30)

수집 코드를 짜는 데 반드시 필요한 8항목입니다. 이 양식을 고정하는 것 자체가 실패 방지 장치입니다.

```
endpoint · params_required · params_optional · auth · response_shape · data_path · error_codes · pagination · rate_limit
```

등록 양식 전체는 `references/api-registry.md` 맨 아래에 있습니다.

## 2. MCP로 표 찾기 (10:42)

`mcp-kosis.md`를 따릅니다. KOSIS MCP 서버가 연결된 분만 직접, 나머지는 강사 화면으로.

## 3. 문서 → 명세서 (11:00)

> `exercises/02/worldbank-doc.md`와 `kosis-doc.md`를 읽고 `references/api-registry.md`의 등록 양식대로 명세서를 각각 작성해. 문서에 없는 항목은 '문서에 없음'으로 두고 추측하지 마. 결과는 JSON으로 `exercises/02/spec_worldbank.json`, `spec_kosis.json`에 저장해.

프롬프트에서 눈여겨볼 세 줄:
- "양식대로" → 출력 모양 고정. 다음 단계 코드가 같은 키를 기대합니다
- "문서에 없으면 '문서에 없음'" → 지어내기 차단. 이 줄이 없으면 그럴듯한 파라미터를 만들어 냅니다
- "JSON으로 저장" → 사람이 아니라 코드가 읽기 때문입니다

## 4. 명세서는 주장입니다. 검증합니다

> `spec_worldbank.json`이 맞는지 실제 호출 한 건으로 검증하는 스크립트를 만들고 실행해. HTTP 200과 JSON 파싱, 응답 최상위 구조, data_path로 관측치 도달, 필수 키 존재, 페이지 여유를 각각 확인하고 결과를 표로 보여줘. 검증 시각과 결과를 명세서 파일에 verified_at, verified_result로 추가해.

**불일치가 나오면 명세서를 고칩니다. 코드를 고치는 게 아닙니다.** 문서와 응답이 다르면 응답이 맞습니다.

KOSIS 명세서는 인증키가 있는 분만 검증까지. 없는 분은 요청 주소 조립까지만.

> 검증이 끝난 명세서를 `references/api-registry.md`의 해당 항목에 반영하고 최종 확인일자를 갱신해.

## 5. 연구 질문 → 파라미터 결정표 (11:18)

`worksheet.md`를 봅니다. 문서에서 시작하지 않고 **연구 질문에서 시작해** 파라미터까지 내려옵니다.

> 내 연구 질문은 "한국의 저출생은 다른 나라와 얼마나 다른가"야. 수집 전에 결정해야 할 항목을 표로 만들어줘. 각 항목이 어느 API 파라미터에 대응되는지, 빠뜨리면 무슨 일이 생기는지도.

에이전트가 **빠진 결정을 되묻는지** 관찰합니다. 안 물으면 여러분이 채웁니다.

## 참고본

`reference/02_api_spec_design.ipynb`, `reference/verify_spec.py`
