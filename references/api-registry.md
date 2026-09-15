# 소스 레지스트리

2교시에서 만든 요청 명세서가 여기에 쌓입니다. **다른 기관으로 옮길 때 고치는 파일이 이것입니다.**

각 항목은 실제 호출 1건으로 검증한 뒤에 등록합니다. 문서와 응답이 다르면 응답이 맞습니다.

---

## World Bank Indicators

- 엔드포인트: `https://api.worldbank.org/v2/country/{country}/indicator/{indicator}`
- 인증: 불필요
- 필수 파라미터: `country` (ISO3, 세미콜론으로 복수 지정), `indicator`
- 선택 파라미터: `format=json` (기본값은 xml), `date=2015:2025`, `per_page`, `page`
- 응답 최상위: **원소 2개짜리 배열**. `[0]`은 페이징 정보, `[1]`은 관측치 배열
- `data_path`: `[1]`
- 페이지 처리: `[0].total`과 `[0].per_page`를 비교. `total`이 크면 뒷장이 남아 있음
- 결측: `value`가 `null`
- 최종 확인: 2026-08-31

**주의** — `format`을 빼면 XML이 옵니다. 문서를 대충 읽으면 반드시 걸리는 함정입니다.

---

## KOSIS 공유서비스

- 엔드포인트: `https://kosis.kr/openapi/Param/statisticsParameterData.do`
- 인증: 필요. `apiKey` 파라미터. 환경변수 `KOSIS_API_KEY`
- 필수 파라미터: `method=getList`, `apiKey`, `orgId`, `tblId`, `itmId`, `objL1`, `prdSe`(Y/Q/M), `startPrdDe`, `endPrdDe`, `format=json`, `jsonVD=Y`
- **`method` · `itmId` · `objL1` · `format` · `jsonVD` 중 하나라도 빠지면** 200과 함께 에러 객체가 옵니다. 표준 JSON이 아니라 파싱에서 터집니다
- 응답: 평평한 객체 배열. 지역은 `C1_NM`, 기간은 `PRD_DE`, 값은 `DT`(문자열)
- 결측: `DT`가 빈 문자열
- 호출 제한: 발급 등급에 따라 다름. 발급 화면에서 확인 후 여기에 기록할 것
- 통계표: `DT_1B81A21` 시도/합계출산율. 항목 `itmId=T1`. 분류 `objL1=ALL` 이면 전국+17개 시도
- **`DT_1B81A17` 은 시군구 표입니다.** 시도 단위로 착각해 쓰면 `err=21` 이 납니다
- 표 찾기: `https://kosis.kr/openapi/statisticsSearch.do?method=getList&apiKey=...&searchNm=합계출산율&format=json&jsonVD=Y`
- 주의: `UNIT_NM` 이 표의 8개 항목 단위를 합친 문자열로 옵니다
- 최종 확인: 2026-09-16 실시간 호출 198행 검증 완료

**주의** — `DT`가 문자열로 옵니다. `float()` 변환 전에 빈 문자열을 걸러야 합니다.

---

## OECD Data Explorer

- 엔드포인트 계열: `https://sdmx.oecd.org/public/rest/data/...`
- SDMX 구조. dataflow / dimension / codelist 개념을 먼저 이해해야 합니다
- **접근 경로가 개편된 이력이 있습니다.** 강의 전 반드시 실제 호출로 재확인하고 확인일자를 갱신할 것
- 최종 확인: (미검증)

---

## Eurostat

- 데이터브라우저에서 무료 내려받기 가능. SDMX API 제공
- 기업 AI 활용률 등 디지털 지표는 `isoc_` 계열
- 최종 확인: (미검증)

---

## 등록 양식

새 소스를 추가할 때 아래를 채우고, 실제 호출로 검증한 뒤 확인일자를 남기세요.

```
- 엔드포인트:
- 인증:
- 필수 파라미터:
- 선택 파라미터:
- 응답 최상위 구조:
- data_path:
- 페이지 처리:
- 결측 표기:
- 호출 제한:
- 출처 표기 문구:
- 최종 확인:
```
