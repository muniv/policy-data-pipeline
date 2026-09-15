"""3교시 관전 트랙 · JSON · XML · CSV 세 형식을 표준 스키마 하나로 모읍니다.

    python exercises/03/offline_tour.py

따라하기 트랙은 에이전트에게 데이터클래스를 만들게 하고 변환시킵니다.
여기서는 같은 일을 완성된 코드로 돌려보며, 형식마다 결측이 어떻게 다르게
표기되는지, 어디서 값이 조용히 사라지는지를 직접 확인합니다.
"""
import csv
import json
import os
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, "samples")

MISSING = {"NA_NOTSURVEYED": "미조사", "NA_NOTAPPLICABLE": "해당없음", "NA_CONFIDENTIAL": "비공개"}


def head(n, title):
    print(f"\n{'─' * 66}\n{n}. {title}\n{'─' * 66}")


def row(source, region, period, value, missing_reason=None):
    """표준 스키마를 강제합니다. 값이 없는데 사유가 없으면 만들지 못합니다."""
    if value is None and missing_reason not in MISSING:
        raise ValueError(f"결측인데 사유가 없습니다: {source}/{region}/{period}")
    return {"source": source, "region": region, "period": int(period),
            "value": value, "missing_reason": missing_reason}


head(1, "JSON — World Bank 식.  결측은 value: null")
payload = json.load(open(os.path.join(S, "response.json"), encoding="utf-8"))
json_rows = [row("JSON", x["countryiso3code"], x["date"], x["value"],
                 None if x["value"] is not None else "NA_NOTSURVEYED")
             for x in payload[1]]
print(f"  {len(json_rows)}행 · 결측 {sum(r['value'] is None for r in json_rows)}건")
print("  null 은 파서가 그대로 None 으로 주므로 놓치기 어렵습니다.")

head(2, "XML — 공공데이터포털 식.  빈 태그 두 가지가 섞여 있습니다")
tree = ET.parse(os.path.join(S, "response.xml"))
xml_rows, empty_kinds = [], []
for item in tree.iter("item"):
    node = item.find("value")
    raw = node.text          # <value></value> 와 <value/> 는 둘 다 None 입니다
    region = item.findtext("regionName")
    year = item.findtext("year")
    if raw is None or not raw.strip():
        empty_kinds.append((region, year))
        xml_rows.append(row("XML", region, year, None, "NA_NOTSURVEYED"))
    else:
        xml_rows.append(row("XML", region, year, float(raw)))
print(f"  {len(xml_rows)}행 · 결측 {len(empty_kinds)}건 → {empty_kinds}")
print()
print("  ⚠ 여기가 조용히 틀리는 자리입니다.")
print("     <value></value> 와 <value/> 는 파서에서 똑같이 text=None 입니다.")
print("     이걸 건너뛰도록 짜면 행 자체가 사라집니다. 결측으로 남는 것과")
print("     행이 없어지는 것은 전혀 다릅니다. 9행이 7행이 되는데 에러는 없습니다.")

head(3, "CSV — KOSIS 내려받기 식.  '-' 와 공란은 뜻이 다릅니다")
csv_rows, dash, blank = [], [], []
with open(os.path.join(S, "response.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        raw = (r["값"] or "").strip()
        region, year = r["행정구역별"], r["시점"]
        if raw == "-":
            dash.append((region, year))
            csv_rows.append(row("CSV", region, year, None, "NA_CONFIDENTIAL"))
        elif raw == "":
            blank.append((region, year))
            csv_rows.append(row("CSV", region, year, None, "NA_NOTSURVEYED"))
        else:
            csv_rows.append(row("CSV", region, year, float(raw)))
print(f"  {len(csv_rows)}행")
print(f"  '-'  {len(dash)}건 → {dash}   비공개로 처리")
print(f"  공란 {len(blank)}건 → {blank}   미조사로 처리")
print()
print("  이 둘을 어느 코드로 보낼지는 응답만으로는 모릅니다.")
print("  표를 만든 사람만 압니다. 그래서 에이전트에게 '물어보라'고 시킵니다.")
print("  빈칸 하나로 뭉개면 나중에 복원할 수 없습니다.")

head(4, "셋을 합칩니다 — 같은 열 개 컬럼 하나로")
allrows = json_rows + xml_rows + csv_rows
print(f"  JSON {len(json_rows)} + XML {len(xml_rows)} + CSV {len(csv_rows)} = {len(allrows)}행")
print()
print(f"  {'source':<7} {'region':<12} {'period':>6} {'value':>7}  missing_reason")
for r in allrows:
    if r["value"] is None:
        print(f"  {r['source']:<7} {r['region']:<12} {r['period']:>6} {'—':>7}  "
              f"{r['missing_reason']} ({MISSING[r['missing_reason']]})")
print()
by_reason = {}
for r in allrows:
    if r["missing_reason"]:
        by_reason[r["missing_reason"]] = by_reason.get(r["missing_reason"], 0) + 1
print(f"  결측 합계 {sum(by_reason.values())}건 · 사유별 {by_reason}")
print("  형식은 셋이지만 결측 사유는 하나의 코드 체계로 모였습니다.")

head(5, "강제 장치가 실제로 막는지 확인")
try:
    row("TEST", "서울특별시", 2025, None)          # 사유 없이 결측을 만들어 봅니다
    print("  ✗ 통과되면 안 됩니다")
except ValueError as e:
    print(f"  ✓ 생성 자체가 실패합니다 — {e}")
print()
print("  나중에 검사하는 게 아니라 애초에 만들어지지 않게 하는 것이 요점입니다.")

print(f"\n{'─' * 66}")
print("이어서 돌려볼 것 (에이전트 없이 전부 동작합니다)")
print("  python exercises/03/reference/run_scenarios.py                    장애 7종 비교")
print("  python exercises/03/reference/crawl_policy.py exercises/03/policy_page.html")
print("  python exercises/03/reference/crawl_policy.py exercises/03/policy_page_v2.html")
print(f"{'─' * 66}\n")
