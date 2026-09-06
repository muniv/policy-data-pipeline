"""참고본. 에이전트 출력이 이상할 때 대조용입니다. fake_api.py 와 같은 폴더에서 실행합니다."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import time
import pandas as pd
from fake_api import FakeAPI, SCENARIOS

def collect_v1(session):
    """1단계 산출물. 성공 경로만 있습니다."""
    r = session.get("https://api.example/v2/indicator", params={"format": "json"})
    payload = r.json()
    rows = payload[1]
    return pd.DataFrame([{
        "region_code": x.get("countryiso3code"),   # 키가 없어도 조용히 None
        "period": int(x["date"]),
        "value": x["value"],
    } for x in rows])
