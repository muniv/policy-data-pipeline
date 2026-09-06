"""참고 크롤러. python crawl_policy.py policy_page.html [--min-rows 15]

v1 페이지 셀렉터로 짜여 있습니다. v2 페이지에 돌리면 0건이 나오는데 에러는 없습니다.
그래서 기대 최소 행 수와 필수 필드를 검사에 넣어 조용히 빈 결과를 내지 않게 합니다.
"""
import sys, argparse
from bs4 import BeautifulSoup

def crawl(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    rows = []
    for card in soup.select("section.region-card"):
        region = card.select_one("h2.region-name").get_text(strip=True)
        for li in card.select("li.policy-item"):
            rows.append({"지역": region, "정책명": li.select_one("span.policy-name").get_text(strip=True)})
    return rows

def guard(rows, min_rows, required=("지역", "정책명")):
    if len(rows) < min_rows:
        raise RuntimeError(f"수집 {len(rows)}건 < 기대 최소 {min_rows}건. 페이지 구조가 바뀌었을 수 있습니다. 멈춥니다.")
    for r in rows:
        missing = [k for k in required if not r.get(k)]
        if missing:
            raise RuntimeError(f"필수 필드 누락 {missing}: {r}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("path"); ap.add_argument("--min-rows", type=int, default=15)
    a = ap.parse_args()
    rows = crawl(open(a.path, encoding="utf-8").read())
    print(f"{len(rows)}건 추출")
    guard(rows, a.min_rows)
    regions = {r["지역"] for r in rows}
    print(f"지역 {len(regions)}개 · 정상")
