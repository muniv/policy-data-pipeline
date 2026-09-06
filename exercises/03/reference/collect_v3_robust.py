"""참고본. 에이전트 출력이 이상할 때 대조용입니다. fake_api.py 와 같은 폴더에서 실행합니다."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import time
import pandas as pd
from fake_api import FakeAPI, SCENARIOS

COLUMNS = ["source", "indicator_code", "region_code", "period", "value", "unit"]

def collect_v3(session, max_retries=3, base_delay=0.01, verbose=False):
    """3단계 산출물. 다섯 가지 실패를 각각 처리합니다."""
    collected, page = [], 1
    meta_total = None

    while True:
        # 실패 1: 일시적 오류와 호출 제한 → 재시도와 백오프. 횟수를 제한해 무한 반복을 막음
        for attempt in range(max_retries):
            try:
                r = session.get("https://api.example/v2/indicator",
                                params={"format": "json", "per_page": 500, "page": page},
                                timeout=20)
                if r.status_code == 429:
                    raise RuntimeError("호출 제한")
                r.raise_for_status()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"{max_retries}회 재시도 후 실패: {e}")
                time.sleep(base_delay * (2 ** attempt))
                if verbose: print(f"  재시도 {attempt+1}회 ({e})")

        # 실패 2: 본문이 JSON이 아님 (점검 페이지, 로그인 리다이렉트 등)
        try:
            payload = r.json()
        except Exception:
            raise RuntimeError("응답 본문이 JSON이 아닙니다. 원문을 확인하세요.")

        # 실패 3: 최상위 구조가 예상과 다름
        if not (isinstance(payload, list) and len(payload) == 2):
            raise RuntimeError(f"응답 구조가 명세와 다릅니다: {type(payload).__name__}")

        meta, rows = payload[0], payload[1]
        meta_total = int(meta.get("total", 0))

        # 실패 4: 스키마 드리프트. 필요한 키가 없으면 조용히 비우지 말고 멈춤
        if rows:
            need = {"date", "value", "indicator"}
            region_key = next((k for k in ("countryiso3code", "iso3") if k in rows[0]), None)
            missing = need - rows[0].keys()
            if missing or region_key is None:
                raise RuntimeError(f"응답 키가 바뀌었습니다. 누락 {missing or ''} 지역키 {region_key}")
            collected += [{
                "source": "WORLDBANK",
                "indicator_code": x["indicator"]["id"],
                "region_code": x[region_key],
                "period": int(x["date"]),
                "value": x["value"],
                "unit": "명",
            } for x in rows]

        if page >= int(meta.get("pages", 1)):
            break
        page += 1

    # 실패 5: 조용한 실패. 0건인데 정상 종료하는 것을 막음
    if meta_total == 0 or not collected:
        raise RuntimeError("수집 결과가 0건입니다. 조건을 확인하세요.")
    if len(collected) != meta_total:
        raise RuntimeError(f"부분 수집: {len(collected)}건 / 전체 {meta_total}건")

    return pd.DataFrame(collected)[COLUMNS]
