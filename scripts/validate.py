"""검증 단계.

각 검사에는 실패했을 때 무엇을 할지가 붙어 있습니다.

- 중단  — 파이프라인을 멈춥니다. 사람이 확인하기 전에는 산출물을 만들지 않습니다.
- 기록  — 진행하되 코드북과 대시보드에 남깁니다.

검증을 사람 눈에 맡기지 않는 것이 요점입니다.
"""
from __future__ import annotations

from collections import defaultdict


class ValidationFailed(RuntimeError):
    pass


def _add(results, name, ok, gate, detail=""):
    results.append({
        "검사": name,
        "결과": "통과" if ok else ("확인" if gate == "기록" else "실패"),
        "실패 시": gate,
        "비고": detail,
    })


def run(rows, config, log=print):
    log("[3/4] 검증")
    v = config["validation"]
    results = []

    _add(results, "행 수 0 아님", len(rows) > 0, "중단", f"{len(rows)}행")

    required = {"source", "indicator_code", "region_code", "period", "value", "unit", "vintage"}
    missing_cols = required - set(rows[0].keys()) if rows else required
    _add(results, "표준 스키마 컬럼 존재", not missing_cols, "중단",
         f"누락 {sorted(missing_cols)}" if missing_cols else "9개 컬럼 확인")

    seen, dups = set(), 0
    for r in rows:
        k = (r["indicator_code"], r["region_code"], r["period"])
        dups += k in seen
        seen.add(k)
    _add(results, "중복 키 없음", dups == 0, "중단", f"중복 {dups}건" if dups else "")

    bad = []
    for r in rows:
        rng = v["value_range"].get(r["indicator_code"])
        if rng and r["value"] is not None and not (rng[0] <= r["value"] <= rng[1]):
            bad.append(f"{r['region_code']}/{r['period']}={r['value']}")
    _add(results, "값 범위 확인", not bad, "중단",
         f"이탈 {len(bad)}건 {bad[:3]}" if bad else "지표별 허용 범위 내")

    sido = {r["region_code"] for r in rows
            if r["region_code"].startswith("KR-") and r["region_code"] != "KR-00"}
    need = v["expected_regions_시도"]
    _add(results, f"시도 {need}개 전수 존재", len(sido) == need, "중단", f"{len(sido)}개 수집")

    y0, y1 = v["expected_years"]
    kr_years = {r["period"] for r in rows if r["source"] == "KOSIS"}
    miss_y = set(range(y0, y1 + 1)) - kr_years
    _add(results, f"기간 연속성 {y0}~{y1}", not miss_y, "중단",
         f"누락 {sorted(miss_y)}" if miss_y else "")

    missing_no_reason = sum(1 for r in rows if r["value"] is None and not r.get("missing_reason"))
    _add(results, "결측에 사유 표기", missing_no_reason == 0, "중단",
         f"사유 없는 결측 {missing_no_reason}건" if missing_no_reason else "")

    # 전년 대비 급변 — 원자료가 맞을 수도 있어 중단하지 않고 기록합니다
    series = defaultdict(list)
    for r in rows:
        if r["value"] is not None:
            series[(r["indicator_code"], r["region_code"])].append((r["period"], r["value"]))
    limit, spikes = v["yoy_change_limit"], []
    for key, pts in series.items():
        pts.sort()
        for (p0, v0), (p1, v1) in zip(pts, pts[1:]):
            if v0 and abs(v1 - v0) / abs(v0) > limit:
                spikes.append(f"{key[1]} {p0}→{p1}")
    _add(results, f"전년 대비 변화율 {int(limit*100)}% 이내", not spikes, "기록",
         f"초과 {len(spikes)}건 — 원문 대조 필요 {spikes[:2]}" if spikes else "")

    # 전국값과 시도 평균의 정합
    nat = {r["period"]: r["value"] for r in rows
           if r["region_code"] == "KR-00" and r["indicator_code"] == "TFR" and r["value"] is not None}
    by_year = defaultdict(list)
    for r in rows:
        if r["indicator_code"] == "TFR" and r["region_code"] not in ("KR-00",) \
                and r["region_code"].startswith("KR-") and r["value"] is not None:
            by_year[r["period"]].append(r["value"])
    gaps = [y for y, nv in nat.items()
            if by_year.get(y) and abs(sum(by_year[y]) / len(by_year[y]) - nv) / nv > 0.15]
    _add(results, "전국값과 시도 평균 정합", not gaps, "기록",
         f"괴리 {sorted(gaps)}" if gaps else "")

    blocking = [r for r in results if r["결과"] == "실패"]
    tally = {
        "통과": sum(r["결과"] == "통과" for r in results),
        "확인": sum(r["결과"] == "확인" for r in results),
        "실패": len(blocking),
    }
    log(f"  통과 {tally['통과']} / 확인 {tally['확인']} / 실패 {tally['실패']}")

    if blocking:
        raise ValidationFailed(
            "검증 실패로 중단합니다. 산출물을 만들지 않습니다.\n"
            + "\n".join(f"  - {r['검사']}: {r['비고']}" for r in blocking)
        )
    return results, tally
