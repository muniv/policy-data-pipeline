"""정규화 단계.

소스마다 다른 응답 모양을 표준 스키마 한 벌로 옮깁니다.

    source | indicator_code | region_code | period | value | unit | vintage | retrieved_at | source_url

원칙
- 지역·기간·단위는 규칙(사전)으로 맞춥니다. 사전에 없는 것만 판단 대상으로 남깁니다.
- 판단이 들어간 건은 pending 목록에 담아 코드북에 기록합니다. 자동으로 확정하지 않습니다.
- 결측은 세 가지로 구분합니다. 하나로 뭉개면 복원할 수 없습니다.
"""
from __future__ import annotations

import csv
import os
from datetime import datetime

MISSING = {"NA_NOTSURVEYED": "미조사", "NA_NOTAPPLICABLE": "해당없음", "NA_CONFIDENTIAL": "비공개"}

COLUMNS = ["source", "indicator_code", "region_code", "period", "value", "unit",
           "vintage", "retrieved_at", "source_url", "missing_reason"]

# 규칙으로 처리하는 정책 분류. 여기 없는 것만 판단 대상이 됩니다.
POLICY_TAXONOMY = {
    "출산장려금": "현금성 지원",
    "난임시술비 지원": "의료비 지원",
    "아이돌봄 서비스": "서비스 지원",
    "다자녀 우대카드": "할인·감면",
}


def load_region_map(base):
    path = os.path.join(base, "references", "region-codes.csv")
    with open(path, encoding="utf-8") as f:
        return {r["region_name"]: r["region_code"] for r in csv.DictReader(f)}


def _row(source, indicator, region, period, value, unit, vintage, url, missing=None):
    if value is None and missing not in MISSING:
        raise ValueError(f"결측 사유 누락: {source}/{region}/{period}")
    return dict(zip(COLUMNS, [source, indicator, region, int(period), value, unit,
                              vintage, datetime.now().isoformat(timespec="seconds"),
                              url, missing]))


def from_kosis(payload, src, region_map, unmapped):
    out = []
    for x in payload:
        name = x.get("C1_NM", "").strip()
        code = region_map.get(name)
        if code is None:
            unmapped.append({"항목": name, "종류": "지역명", "소스": src["id"]})
            continue
        raw = (x.get("DT") or "").strip()
        value = float(raw) if raw else None
        out.append(_row(
            "KOSIS", src["indicator_code"], code, x["PRD_DE"], value,
            x.get("UNIT_NM") or src["unit"], src["vintage"],
            src["endpoint"], None if value is not None else "NA_NOTSURVEYED",
        ))
    return out


def from_worldbank(payload, src, unmapped):
    meta, rows = payload
    out = []
    for x in rows:
        region = x.get("countryiso3code") or x.get("iso3")
        if not region:
            raise ValueError("응답에 국가코드 키가 없습니다. 스키마가 바뀌었는지 확인하세요.")
        v = x["value"]
        out.append(_row(
            "WORLDBANK", x["indicator"]["id"], region, x["date"], v,
            src["unit"], src["vintage"],
            "https://api.worldbank.org/v2/", None if v is not None else "NA_NOTSURVEYED",
        ))
    return out


def from_policy(payload, src, region_map, unmapped, pending):
    counts = {}
    for x in payload:
        code = region_map.get(x["지역"])
        if code is None:
            unmapped.append({"항목": x["지역"], "종류": "지역명", "소스": src["id"]})
            continue
        name = x["정책명"]
        if name not in POLICY_TAXONOMY:
            # 규칙으로 못 정합니다. 판단이 필요한 건으로 남깁니다.
            if not any(p["원문"] == name for p in pending):
                pending.append({"원문": name, "제안": "현금성 지원",
                                "근거": "지자체 안내문의 지급 방식 기술", "확인": "미확인"})
        counts[code] = counts.get(code, 0) + 1

    return [_row("정책브리핑", src["indicator_code"], code, 2026, float(n),
                 src["unit"], src["vintage"], "https://www.korea.kr/")
            for code, n in sorted(counts.items())]


def run(payloads, config, base, log=print):
    log("[2/4] 정규화")
    region_map = load_region_map(base)
    rows, unmapped, pending = [], [], []

    for src in config["sources"]:
        p = payloads[src["id"]]
        if src["id"].startswith("kosis"):
            got = from_kosis(p, src, region_map, unmapped)
        elif src["id"].startswith("wb"):
            got = from_worldbank(p, src, unmapped)
        else:
            got = from_policy(p, src, region_map, unmapped, pending)
        log(f"  [{src['id']}] {len(got)}행")
        rows += got

    if unmapped:
        log(f"  매핑 실패 {len(unmapped)}건 — references/region-codes.csv 를 확인하세요")
    if pending:
        log(f"  판단 필요 {len(pending)}건 — 코드북 4절에 기록됩니다")
    return rows, unmapped, pending
