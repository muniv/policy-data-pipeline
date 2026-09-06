"""참고본. 에이전트 출력이 이상할 때 대조용입니다. fake_api.py 와 같은 폴더에서 실행합니다."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import time
import pandas as pd
from fake_api import FakeAPI, SCENARIOS
from collect_v1_naive import collect_v1
from collect_v3_robust import collect_v3

def try_run(fn, scenario, full=11):
    """행 수만 보지 않습니다. 조용히 망가진 흔적까지 같이 봅니다."""
    try:
        df = fn(FakeAPI(scenario))
    except Exception as e:
        return f"중단: {str(e)[:40]}"

    flags = []
    if len(df) < full:
        flags.append(f"{full - len(df)}행 유실")
    if "region_code" in df.columns and df["region_code"].isna().all():
        flags.append("지역 전부 소실")
    return f"{len(df)}행" + (f" ⚠ {', '.join(flags)}" if flags else " 정상")


table = []
for s in SCENARIOS:
    table.append({
        "시나리오": s,
        "1단계": try_run(collect_v1, s),
        "3단계": try_run(collect_v3, s),
    })

if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print(pd.DataFrame(table).to_string(index=False))
