"""4교시 · 출생아수 지표 추가용 오프라인 스냅샷 생성기.

강의 중 에이전트가 이 지표를 추가하는 장면을 시연합니다. 실시간 KOSIS 호출이
막힌 환경에서도 같은 장면이 돌아가도록, 인구동향조사 출생아수 표(DT_1B81A01)의
응답 형태를 그대로 본뜬 스냅샷을 만듭니다.

    python exercises/04/reference/make_births_sample.py

raw/sample/kosis_births.json 이 생깁니다. 합계출산율 스냅샷과 같은 KOSIS 형태라
scripts/normalize.py 의 from_kosis 가 그대로 처리합니다.
"""
import json
import os
import random

random.seed(20260916)

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(BASE, "raw", "sample")
os.makedirs(OUT, exist_ok=True)

# 시도별 2025년 출생아수 규모(명). 실제 공표치가 아니라 구조 확인용 가공값입니다.
SIDO = {
    "서울특별시": 39500, "부산광역시": 12800, "대구광역시": 9600, "인천광역시": 14200,
    "광주광역시": 6100, "대전광역시": 6400, "울산광역시": 5200, "세종특별자치시": 2900,
    "경기도": 67000, "강원특별자치도": 6300, "충청북도": 6900, "충청남도": 9400,
    "전북특별자치도": 5800, "전라남도": 6700, "경상북도": 9700, "경상남도": 12600,
    "제주특별자치도": 2900,
}
YEARS = list(range(2015, 2026))

# 전국 출생아수 추세(명). 2015년을 1.0으로 둔 연도별 배율입니다.
TREND = {2015: 1.00, 2016: 0.93, 2017: 0.81, 2018: 0.76, 2019: 0.70,
         2020: 0.64, 2021: 0.61, 2022: 0.59, 2023: 0.55, 2024: 0.57, 2025: 0.60}

rows = []
for name, v2025 in SIDO.items():
    base_2015 = v2025 / TREND[2025]
    for y in YEARS:
        val = int(round(base_2015 * TREND[y] * random.uniform(0.98, 1.02), -1))
        rows.append({
            "ORG_ID": "101", "TBL_ID": "DT_1B81A01", "TBL_NM": "인구동향조사",
            "C1": name, "C1_NM": name, "ITM_ID": "T20", "ITM_NM": "출생아수",
            "PRD_DE": str(y), "PRD_SE": "Y", "UNIT_NM": "명",
            # 세종 2015년은 미조사로 둡니다. 결측 사유 표기 검사를 타는 자리입니다.
            "DT": "" if (name == "세종특별자치시" and y == 2015) else str(val),
        })

for y in YEARS:
    total = sum(int(r["DT"]) for r in rows if r["PRD_DE"] == str(y) and r["DT"])
    rows.append({
        "ORG_ID": "101", "TBL_ID": "DT_1B81A01", "TBL_NM": "인구동향조사",
        "C1": "전국", "C1_NM": "전국", "ITM_ID": "T20", "ITM_NM": "출생아수",
        "PRD_DE": str(y), "PRD_SE": "Y", "UNIT_NM": "명", "DT": str(total),
    })

path = os.path.join(OUT, "kosis_births.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False)

print(f"{path} · {len(rows)}건")
