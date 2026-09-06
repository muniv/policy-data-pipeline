# KOSIS 공유서비스 통계자료 API (문서 발췌, 실습용)

엔드포인트: `https://kosis.kr/openapi/Param/statisticsParameterData.do`

| 파라미터 | 설명 |
|---|---|
| `method` | `getList` 고정 |
| `apiKey` | 발급받은 인증키 |
| `orgId` | 기관 코드 (통계청 101) |
| `tblId` | 통계표 ID |
| `itmId` | 항목 ID. 여러 개는 `+`로 연결, 전체는 `ALL` |
| `objL1` ~ `objL8` | 분류 값. 전체는 `ALL` |
| `prdSe` | 수록주기. `Y` 연, `Q` 분기, `M` 월 |
| `startPrdDe` / `endPrdDe` | 시작·종료 시점 (예: `2015`, `2025`) |
| `format` | `json` |
| `jsonVD` | `Y` |

응답은 객체 배열입니다. 각 객체에 `C1`(분류 코드), `C1_NM`(분류명), `ITM_ID`, `ITM_NM`, `PRD_DE`(시점), `PRD_SE`, `UNIT_NM`, `DT`(값, 문자열)가 들어 있습니다. 값이 없으면 `DT`가 빈 문자열입니다.

인증키 발급: https://kosis.kr/openapi 회원가입 후 "Open API 사용 신청". 호출 제한은 발급 등급에 따라 다릅니다.

주의: 표마다 필요한 분류 파라미터(`objL1` 등)의 개수와 의미가 다릅니다. 표 번호와 항목 ID는 KOSIS 통계표 화면 또는 MCP 도구로 확인합니다.
