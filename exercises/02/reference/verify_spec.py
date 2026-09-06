"""명세서 검증 참고본. 사용법: python verify_spec.py spec_worldbank.json

명세서는 주장입니다. 실제 호출 한 건으로 대조한 뒤에 씁니다.
"""
import json, re, sys
import requests


def resolve_path(payload, path_expr):
    node = payload
    for key in re.findall(r"\[([^\]]+)\]", path_expr):
        key = key.strip("'\"")
        node = node[int(key)] if key.lstrip("-").isdigit() else node[key]
    return node


def verify(spec, path_values, query, expect_keys):
    url = spec["endpoint"].format(**path_values)
    checks = []
    def check(name, ok, detail=""):
        checks.append((name, "통과" if ok else "불일치", detail))
    try:
        r = requests.get(url, params=query, timeout=20)
    except Exception as e:
        check("호출 성공", False, f"{type(e).__name__}: {e}"); return url, checks
    check("HTTP 200", r.status_code == 200, f"status={r.status_code}")
    if r.status_code != 200: return url, checks
    try:
        payload = r.json(); check("JSON 파싱", True)
    except Exception:
        check("JSON 파싱", False, "본문이 JSON이 아닙니다"); return url, checks
    shape_ok = isinstance(payload, list) and len(payload) == 2
    check("응답 최상위 구조", shape_ok, f"타입 {type(payload).__name__}")
    try:
        rows = resolve_path(payload, spec["data_path"])
        check("data_path 유효", isinstance(rows, list) and len(rows) > 0, f"{len(rows)}건")
    except Exception as e:
        check("data_path 유효", False, str(e)); return url, checks
    missing = [k for k in expect_keys if k not in rows[0]]
    check("관측치 필수 키", not missing, f"누락 {missing}" if missing else "전부 존재")
    meta = payload[0] if shape_ok else {}
    if "total" in meta and "per_page" in meta:
        check("페이징 여유", int(meta["total"]) <= int(meta["per_page"]), f"total={meta['total']} per_page={meta['per_page']}")
    return url, checks


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    url, checks = verify(spec, {"country": "KOR", "indicator": "SP.DYN.TFRT.IN"},
                         {"format": "json", "date": "2015:2025", "per_page": 500},
                         ["countryiso3code", "date", "value", "indicator"])
    print("요청:", url)
    for name, res, detail in checks:
        print(f"  {res:4s}  {name:16s} {detail}")
