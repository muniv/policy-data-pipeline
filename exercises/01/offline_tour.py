"""1교시 관전 트랙 · 에이전트 없이 응답 구조를 직접 뜯어봅니다.

    python exercises/01/offline_tour.py

따라하기 트랙은 에이전트에게 물어서 알아내는 내용입니다. 여기서는 같은 것을
스냅샷으로 직접 확인합니다. 인터넷도 인증키도 필요 없습니다.
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(BASE, "raw", "sample", "wb_tfr.json")


def head(n, title):
    print(f"\n{'─' * 62}\n{n}. {title}\n{'─' * 62}")


payload = json.load(open(PATH, encoding="utf-8"))

head(1, "최상위 구조 — 딕셔너리인가, 리스트인가")
print(f"  타입     : {type(payload).__name__}")
print(f"  원소 개수 : {len(payload)}")
print(f"  [0] 타입 : {type(payload[0]).__name__}   ← 페이징 메타")
print(f"  [1] 타입 : {type(payload[1]).__name__}   ← 관측치 배열")
print()
print("  문서만 읽고 payload['data'] 로 접근하는 코드는 여기서 깨집니다.")
print("  최상위가 딕셔너리가 아니라 '원소 2개짜리 리스트'이기 때문입니다.")

meta, rows = payload

head(2, "페이징 — 뒷장이 남았는가")
for k in ("page", "pages", "per_page", "total"):
    print(f"  {k:10} = {meta.get(k)}")
total, per_page, got = int(meta["total"]), int(meta["per_page"]), len(rows)
print()
print(f"  받은 행 수 {got} / 전체 {total}")
if got < total:
    print("  ⚠ 뒷장이 남았습니다. 이대로 분석에 들어가면 '부분 수집'입니다.")
else:
    print("  ✓ total 이 per_page 이하라 한 번에 다 받았습니다.")
print()
print("  이 검사를 안 하면 앞부분만 받고도 에러 없이 넘어갑니다.")

head(3, "결측 — 어느 연도가 비어 있는가")
missing = [x for x in rows if x["value"] is None]
print(f"  전체 {len(rows)}행 중 결측 {len(missing)}행")
for x in missing[:6]:
    print(f"    {x['countryiso3code']}  {x['date']}  value={x['value']}  obs_status={x['obs_status']!r}")
print()
print("  이 결측이 '미조사'인지 '해당없음'인지 '비공개'인지")
print("  응답만 보고 알 수 있습니까?  →  알 수 없습니다.")
print("  obs_status 가 비어 있습니다. 그래서 수집 시점에 사유를 적어야 합니다.")
print("  그때 안 적으면 이후 어느 단계에서도 복원할 방법이 없습니다.")

head(4, "국가 × 연도 교차표")
countries = sorted({x["countryiso3code"] for x in rows})
years = sorted({x["date"] for x in rows})
print("  국가 " + " ".join(f"{y:>7}" for y in years))
for c in countries:
    by_year = {x["date"]: x["value"] for x in rows if x["countryiso3code"] == c}
    cells = []
    for y in years:
        v = by_year.get(y)
        cells.append(f"{'':>7}" if y not in by_year else (f"{'결측':>6}" if v is None else f"{v:>7.2f}"))
    print(f"  {c:4} " + " ".join(cells))
print()
print(f"  국가 코드를 세미콜론으로 이으면 {len(countries)}개국이 요청 한 번입니다.")
print("  호출 제한을 지키는 첫 번째 방법입니다.")

print(f"\n{'─' * 62}")
print("여기까지가 1교시에서 에이전트에게 물어 알아내는 내용입니다.")
print("다음 → exercises/01/checklist.md 에 우리 기관 소스 세 개를 채워보세요.")
print(f"{'─' * 62}\n")
