"""2교시 관전 트랙 · 명세서를 만들고, 호출 없이 스냅샷으로 검증합니다.

    python exercises/02/offline_tour.py

따라하기 트랙은 에이전트가 문서를 읽어 명세서를 쓰고 실제 호출로 검증합니다.
여기서는 완성된 명세서를 놓고, 같은 검증을 스냅샷 응답으로 돌립니다.
인터넷도 인증키도 필요 없습니다.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def head(n, title):
    print(f"\n{'─' * 62}\n{n}. {title}\n{'─' * 62}")


# exercises/02/worldbank-doc.md 를 읽고 등록 양식대로 채운 결과입니다.
# 문서에 없는 항목은 지어내지 않고 '문서에 없음' 으로 둡니다.
SPEC = {
    "endpoint": "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}",
    "params_required": ["country", "indicator"],
    "params_optional": ["format", "date", "per_page", "page"],
    "auth": "불필요",
    "response_shape": "원소 2개짜리 배열 [메타, 관측치배열]",
    "data_path": "[1]",
    "error_codes": "문서에 없음",
    "pagination": "[0].total 과 [0].per_page 비교",
    "rate_limit": "문서에 없음",
}

head(1, "명세서 8요소 — 문서에서 뽑은 것")
for k, v in SPEC.items():
    mark = "  ←  지어내지 않고 비워둡니다" if v == "문서에 없음" else ""
    print(f"  {k:17} {v}{mark}")
print()
print("  '문서에 없으면 문서에 없음으로 두라'는 한 줄이 없으면")
print("  언어모델은 그럴듯한 파라미터를 만들어 냅니다. 호출에서 400이 납니다.")

head(2, "명세서는 주장입니다 — 응답 한 건으로 대조합니다")
payload = json.load(open(os.path.join(BASE, "raw", "sample", "wb_tfr.json"), encoding="utf-8"))


def resolve(node, path_expr):
    for key in re.findall(r"\[([^\]]+)\]", path_expr):
        key = key.strip("'\"")
        node = node[int(key)] if key.lstrip("-").isdigit() else node[key]
    return node


checks = []

shape_ok = isinstance(payload, list) and len(payload) == 2
checks.append(("응답 최상위 구조가 명세서와 같은가", shape_ok,
               f"실제: {type(payload).__name__} 길이 {len(payload)}"))

try:
    rows = resolve(payload, SPEC["data_path"])
    path_ok = isinstance(rows, list) and len(rows) > 0
    detail = f"{SPEC['data_path']} → {len(rows)}행 도달"
except Exception as e:
    rows, path_ok, detail = [], False, str(e)
checks.append(("data_path 로 관측치에 도달하는가", path_ok, detail))

need = {"countryiso3code", "date", "value", "indicator"}
have = set(rows[0].keys()) if rows else set()
checks.append(("필수 키가 전부 있는가", need <= have,
               f"누락 {sorted(need - have)}" if need - have else f"{sorted(need)} 확인"))

meta = payload[0]
page_ok = len(rows) >= int(meta.get("total", 0))
checks.append(("페이지 여유 — 부분 수집이 아닌가", page_ok,
               f"받은 {len(rows)} / total {meta.get('total')}"))

w = max(len(c[0]) for c in checks)
for name, ok, detail in checks:
    print(f"  {'통과' if ok else '실패'}  {name:<{w}}  {detail}")
print()
print("  불일치가 나오면 명세서를 고칩니다. 코드를 고치는 게 아닙니다.")
print("  문서와 응답이 다르면 응답이 맞습니다.")

head(3, "문서를 대충 읽으면 걸리는 함정")
print("  World Bank 는 format 을 빼면 XML 이 옵니다. 기본값이 json 이 아닙니다.")
print("  명세서의 params_optional 에 format 이 들어 있는 이유입니다.")
print()
print("  이런 건 문서를 아무리 읽어도 안 보입니다. 호출 한 건이 알려줍니다.")

head(4, "연구 질문 → 파라미터 결정표")
table = [
    ("필요 지표", "합계출산율", "indicator", "—"),
    ("비교 대상", "OECD 주요 7개국 + 한국", "country", "국가 추가하며 재수집"),
    ("분석 기간", "2015~2025", "date", "추세 구간 짧아 재수집"),
    ("주기", "연간", "—", "분기 자료와 집계 충돌"),
    ("지역 단위", "국가 (국내는 시도)", "objL1", "국내외 결합 키 불일치"),
    ("단위", "명", "—", "환산 누락"),
]
print(f"  {'결정 항목':<12} {'우리 값':<24} {'파라미터':<11} 빠뜨리면")
for a, b, c, d in table:
    print(f"  {a:<12} {b:<24} {c:<11} {d}")
print()
print("  수집 전에 이 표를 채우면 재수집이 사라집니다.")
print("  문서에서 시작하지 않고 연구 질문에서 시작해 파라미터까지 내려옵니다.")

print(f"\n{'─' * 62}")
print("여기까지가 2교시에서 에이전트가 하는 일입니다.")
print("다음 → exercises/02/worksheet.md 를 본인 연구 질문으로 채워보세요.")
print(f"{'─' * 62}\n")
