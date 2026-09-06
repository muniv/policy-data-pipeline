"""참고본. 에이전트 출력이 이상할 때 대조용입니다. fake_api.py 와 같은 폴더에서 실행합니다."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import time
import pandas as pd

def validate(df, expected_regions=None, expected_years=None):
    results = []

    def rule(name, ok, gate, detail=""):
        results.append({"검사": name, "결과": "통과" if ok else ("확인" if gate == "기록" else "실패"),
                        "실패 시": gate, "비고": detail})

    rule("행 수 0 아님", len(df) > 0, "중단", f"{len(df)}행")

    need = {"source", "indicator_code", "region_code", "period", "value", "unit", "vintage"}
    miss = need - set(df.columns)
    rule("필수 컬럼 존재", not miss, "중단", f"누락 {miss}" if miss else "")

    dup = df.duplicated(subset=["indicator_code", "region_code", "period"]).sum()
    rule("중복 키 없음", dup == 0, "중단", f"중복 {dup}건")

    vals = df["value"].dropna()
    out_of_range = ((vals < 0) | (vals > 3)).sum()
    rule("값 범위 0~3", out_of_range == 0, "중단", f"이탈 {out_of_range}건")

    if expected_regions:
        got = set(df["region_code"])
        missing_r = set(expected_regions) - got
        rule("지역 전수 존재", not missing_r, "중단", f"누락 {missing_r}" if missing_r else "")

    if expected_years:
        missing_y = set(expected_years) - set(df["period"])
        rule("기간 연속성", not missing_y, "중단", f"누락 연도 {sorted(missing_y)}" if missing_y else "")

    s = df.dropna(subset=["value"]).sort_values("period")
    chg = s["value"].pct_change().abs()
    spikes = int((chg > 0.30).sum())
    rule("전년 대비 변화율 30% 이내", spikes == 0, "기록",
         f"초과 {spikes}건 — 원문 대조 필요" if spikes else "")

    return pd.DataFrame(results)

def gate(report_df):
    blocking = report_df[(report_df["결과"] == "실패") & (report_df["실패 시"] == "중단")]
    if len(blocking):
        raise RuntimeError(
            "검증 실패로 파이프라인을 중단합니다:\n"
            + "\n".join(f"  - {r['검사']}: {r['비고']}" for _, r in blocking.iterrows())
        )
    warn = report_df[report_df["결과"] == "확인"]
    return {"통과": int((report_df["결과"] == "통과").sum()),
            "확인": len(warn), "실패": 0}
