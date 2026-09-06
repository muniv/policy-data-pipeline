"""수업용 오프라인 스냅샷 생성기.
실제 수집 전에 파이프라인을 돌려볼 수 있도록 소스별 원본 형태의 샘플을 만듭니다.
"""
import json, os, random

random.seed(20260916)
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "raw", "sample")
os.makedirs(OUT, exist_ok=True)

SIDO = {
    "서울특별시": 0.61, "부산광역시": 0.72, "대구광역시": 0.76, "인천광역시": 0.78,
    "광주광역시": 0.81, "대전광역시": 0.83, "울산광역시": 0.85, "세종특별자치시": 1.03,
    "경기도": 0.80, "강원특별자치도": 0.89, "충청북도": 0.88, "충청남도": 0.87,
    "전북특별자치도": 0.84, "전라남도": 0.97, "경상북도": 0.86, "경상남도": 0.86,
    "제주특별자치도": 0.84,
}
YEARS = list(range(2015, 2026))
NATIONAL = {2015: 1.24, 2016: 1.17, 2017: 1.05, 2018: 0.98, 2019: 0.92,
            2020: 0.84, 2021: 0.81, 2022: 0.78, 2023: 0.72, 2024: 0.75, 2025: 0.799}

# ── KOSIS 형태: 평평한 객체 리스트 ─────────────────────────────
kosis = []
for name, v2025 in SIDO.items():
    scale = v2025 / NATIONAL[2025]
    for y in YEARS:
        val = round(NATIONAL[y] * scale + random.uniform(-0.012, 0.012), 3)
        kosis.append({
            "ORG_ID": "101", "TBL_ID": "DT_1B81A17", "TBL_NM": "인구동향조사",
            "C1": name, "C1_NM": name, "ITM_ID": "T10", "ITM_NM": "합계출산율",
            "PRD_DE": str(y), "PRD_SE": "Y", "UNIT_NM": "명",
            "DT": "" if (name == "세종특별자치시" and y == 2015) else str(val),
        })
for y in YEARS:
    kosis.append({
        "ORG_ID": "101", "TBL_ID": "DT_1B81A17", "TBL_NM": "인구동향조사",
        "C1": "전국", "C1_NM": "전국", "ITM_ID": "T10", "ITM_NM": "합계출산율",
        "PRD_DE": str(y), "PRD_SE": "Y", "UNIT_NM": "명", "DT": str(NATIONAL[y]),
    })

# 수업용으로 급변 1건을 일부러 심습니다.
# 검증이 "확인 필요"를 띄우는 장면과, 그때 연구자가 원문을 대조하는 절차를 보여주기 위한 장치입니다.
for x in kosis:
    if x["C1_NM"] == "세종특별자치시" and x["PRD_DE"] == "2016":
        x["DT"] = str(round(float(x["DT"]) * 1.45, 3))

# ── World Bank 형태: 원소 2개짜리 배열 ─────────────────────────
WB = {"KOR": NATIONAL, "JPN": {y: round(1.45 - 0.025 * (y - 2015), 2) for y in YEARS},
      "FRA": {y: round(1.96 - 0.034 * (y - 2015), 2) for y in YEARS},
      "DEU": {y: round(1.50 - 0.015 * (y - 2015), 2) for y in YEARS},
      "ITA": {y: round(1.35 - 0.015 * (y - 2015), 2) for y in YEARS},
      "ESP": {y: round(1.33 - 0.014 * (y - 2015), 2) for y in YEARS},
      "USA": {y: round(1.84 - 0.022 * (y - 2015), 2) for y in YEARS}}
wb_rows = []
for iso, series in WB.items():
    for y in YEARS:
        wb_rows.append({
            "indicator": {"id": "SP.DYN.TFRT.IN", "value": "Fertility rate, total"},
            "country": {"id": iso[:2], "value": iso},
            "countryiso3code": iso, "date": str(y),
            "value": None if y == 2025 and iso != "KOR" else series[y],
            "unit": "", "obs_status": "", "decimal": 2,
        })
wb = [{"page": 1, "pages": 1, "per_page": 500, "total": len(wb_rows),
       "lastupdated": "2026-07-01"}, wb_rows]

# ── 웹 수집 형태: 자유 기술이 섞인 반정형 ──────────────────────
POLICY_TERMS = ["첫만남이용권", "출산장려금", "산후조리 경비 지원", "난임시술비 지원",
                "아이돌봄 서비스", "다자녀 우대카드"]
policy = []
for name in SIDO:
    for t in random.sample(POLICY_TERMS, random.randint(3, 5)):
        policy.append({"지역": name, "정책명": t, "수집일": "2026-08-31",
                       "출처": "https://www.korea.kr/"})

for fn, obj in [("kosis_tfr.json", kosis), ("wb_tfr.json", wb), ("policy_brief.json", policy)]:
    with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    print(f"{fn:22s} {len(obj) if isinstance(obj, list) else '-'}건")
