"""참고본. 에이전트 출력이 이상할 때 대조용입니다. fake_api.py 와 같은 폴더에서 실행합니다."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import time
import pandas as pd

from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
KST = timezone(timedelta(hours=9))

MISSING_CODES = {
    "NA_NOTSURVEYED":   "미조사",
    "NA_NOTAPPLICABLE": "해당없음",
    "NA_CONFIDENTIAL":  "비공개",
}

@dataclass
class Observation:
    source: str
    indicator_code: str
    region_code: str
    period: int
    value: float | None
    unit: str
    vintage: str
    retrieved_at: str
    source_url: str
    missing_reason: str | None = None

    def __post_init__(self):
        if not (1900 <= self.period <= 2100):
            raise ValueError(f"period 범위 밖: {self.period}")
        if self.value is None and self.missing_reason not in MISSING_CODES:
            raise ValueError(f"결측인데 사유가 없습니다: region={self.region_code} period={self.period}")
        if self.value is not None and not isinstance(self.value, (int, float)):
            raise ValueError(f"value 타입 오류: {type(self.value).__name__}")
        if self.vintage not in ("확정", "잠정", "추계"):
            raise ValueError(f"vintage 값 오류: {self.vintage}")

def to_observations(raw_rows, source, source_url, vintage="확정"):
    now = datetime.now(KST).isoformat()
    out, rejected = [], []
    for x in raw_rows:
        try:
            v = x["value"]
            out.append(Observation(
                source=source,
                indicator_code=x["indicator"]["id"],
                region_code=x.get("countryiso3code") or x.get("iso3"),
                period=int(x["date"]),
                value=v,
                unit="명",
                vintage=vintage,
                retrieved_at=now,
                source_url=source_url,
                missing_reason=None if v is not None else "NA_NOTSURVEYED",
            ))
        except Exception as e:
            rejected.append({"원본": x, "사유": str(e)})
    return out, rejected
