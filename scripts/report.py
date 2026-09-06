"""산출물 생성 단계.

세 가지를 만듭니다.

- out/panel.csv        분석용 패널 (표준 스키마)
- out/codebook.md      데이터셋 사용설명서. 실행할 때마다 다시 만들어 항상 데이터와 일치합니다.
- out/dashboard.html   단일 파일 대시보드. 서버가 필요 없어 그대로 공유됩니다.

코드북을 사람이 나중에 쓰면 안 씁니다. 써도 데이터와 어긋납니다.
파이프라인이 매번 다시 뱉으면 사람의 성실성에 의존하지 않게 됩니다.
"""
from __future__ import annotations

import csv
import html
import os
from collections import defaultdict
from datetime import datetime

from scripts.normalize import COLUMNS, MISSING

SIDO_LABEL = {
    "KR-11": "서울", "KR-26": "부산", "KR-27": "대구", "KR-28": "인천", "KR-29": "광주",
    "KR-30": "대전", "KR-31": "울산", "KR-36": "세종", "KR-41": "경기", "KR-51": "강원",
    "KR-43": "충북", "KR-44": "충남", "KR-52": "전북", "KR-46": "전남", "KR-47": "경북",
    "KR-48": "경남", "KR-50": "제주",
}
ISO_LABEL = {"KOR": "한국", "JPN": "일본", "FRA": "프랑스", "DEU": "독일",
             "ITA": "이탈리아", "ESP": "스페인", "USA": "미국"}


def write_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)


# ────────────────────────────────────────────────────────────── 코드북

def write_codebook(rows, config, checks, tally, source_meta, unmapped, pending, path, run_date):
    ind = defaultdict(lambda: {"n": 0, "years": set(), "regions": set(), "unit": "", "src": ""})
    for r in rows:
        d = ind[r["indicator_code"]]
        d["n"] += 1
        d["years"].add(r["period"])
        d["regions"].add(r["region_code"])
        d["unit"], d["src"] = r["unit"], r["source"]

    L = []
    A = L.append
    A(f"# 코드북 — {config['project']}\n")
    A("> 이 문서는 파이프라인이 자동 생성합니다. 직접 고치지 마세요.")
    A("> 정의를 바꾸려면 `references/schema.md` 와 `config/sources.yml` 을 고칩니다.\n")
    A(f"- 생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    A(f"- 데이터 파일: `out/panel.csv` ({len(rows):,}행)")
    A(f"- 원본 스냅샷: `raw/{run_date}/`")
    A(f"- 검증: 통과 {tally['통과']} · 확인 {tally['확인']} · 실패 {tally['실패']}\n")

    A("---\n\n## 1. 변수 정의\n")
    A("| 컬럼 | 설명 |")
    A("|---|---|")
    for col, desc in [
        ("source", "출처 기관"), ("indicator_code", "지표 코드 (소스 원 코드 유지)"),
        ("region_code", "지역 코드. 국내 `KR-`+행정구역코드, 국외 ISO 3166-1 alpha-3"),
        ("period", "관측 연도"), ("value", "관측값. 결측이면 비고, 사유는 missing_reason"),
        ("unit", "단위"), ("vintage", "확정 / 잠정 / 추계 / 연간"),
        ("retrieved_at", "수집 시각"), ("source_url", "요청 주소"),
        ("missing_reason", "결측 사유 코드"),
    ]:
        A(f"| `{col}` | {desc} |")

    A("\n**결측 코드**\n")
    A("| 코드 | 의미 | 분석에서 |")
    A("|---|---|---|")
    for k, v in MISSING.items():
        note = {"미조사": "보간 검토 가능", "해당없음": "보간 금지",
                "비공개": "값은 존재. 다른 경로 검토"}[v]
        A(f"| `{k}` | {v} | {note} |")
    A("\n세 가지를 빈칸 하나로 뭉개면 이후에 복원할 수 없습니다. 수집 시점에만 알 수 있는 정보입니다.\n")

    A("---\n\n## 2. 지표 목록\n")
    A("| 지표 코드 | 출처 | 기간 | 지역 수 | 단위 | 행 수 |")
    A("|---|---|---|---|---|---|")
    for code, d in sorted(ind.items()):
        yrs = f"{min(d['years'])}–{max(d['years'])}" if len(d["years"]) > 1 else str(min(d["years"]))
        A(f"| `{code}` | {d['src']} | {yrs} | {len(d['regions'])} | {d['unit']} | {d['n']:,} |")

    A("\n---\n\n## 3. 수집 이력\n")
    A("| 소스 | 수집 시각 | 방식 | 소요 |")
    A("|---|---|---|---|")
    for m in source_meta:
        A(f"| {m['name']} | {m['retrieved_at']} | {m['mode']} | {m['elapsed_sec']}초 |")

    A("\n---\n\n## 4. 판정이 필요했던 항목\n")
    if pending:
        A("규칙으로 처리하지 못해 판단이 들어간 건입니다. **확인은 연구자가 합니다.**\n")
        A("| 원문 | 제안된 분류 | 근거 | 확인 |")
        A("|---|---|---|---|")
        for p in pending:
            A(f"| {p['원문']} | {p['제안']} | {p['근거']} | {p['확인']} |")
        A("\n확인이 끝나면 `scripts/normalize.py` 의 `POLICY_TAXONOMY` 에 등록하세요. "
          "등록된 뒤에는 판단 없이 규칙으로 처리됩니다.\n")
    else:
        A("이번 실행에서는 전부 규칙으로 처리되었습니다. 판단이 들어간 건이 없습니다.\n")

    if unmapped:
        A("### 매핑하지 못한 항목\n")
        A("| 항목 | 종류 | 소스 |")
        A("|---|---|---|")
        for u in unmapped[:20]:
            A(f"| {u['항목']} | {u['종류']} | {u['소스']} |")
        A("")

    A("---\n\n## 5. 검증 결과\n")
    A("| 검사 | 결과 | 실패 시 | 비고 |")
    A("|---|---|---|---|")
    for c in checks:
        A(f"| {c['검사']} | {c['결과']} | {c['실패 시']} | {c['비고']} |")

    A("\n---\n\n## 6. 인용 시 유의사항\n")
    A("- 국가별 최신 공표연도가 달라 국제 비교표는 연도가 혼재합니다. 인용 시 `period` 를 함께 표기하세요.")
    A("- 잠정치는 확정치 공표 후 값이 바뀔 수 있습니다. 과거 분석 재현을 위해 수집 시점 원본을 `raw/` 에 보관합니다.")
    A("- 각 소스의 이용약관과 출처 표기 의무는 `references/api-registry.md` 를 확인하세요.")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


# ────────────────────────────────────────────────────────────── 대시보드

_CSS = """
:root{--ground:#EEF0EC;--surface:#fff;--ink:#1B2430;--muted:#67707C;--rule:#D3D7D0;
--pass:#2E6F52;--warn:#9E6B12;--fail:#A33B2C;--data:#2F4B7C;--hi:#A33B2C}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-size:15px;line-height:1.55;
font-family:"Pretendard","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif}
.wrap{max-width:960px;margin:0 auto;padding:28px 20px 64px}
.num{font-variant-numeric:tabular-nums}
.status{background:var(--surface);border:1px solid var(--rule);border-left:5px solid %(barcolor)s;
padding:22px 24px;margin-bottom:22px}
.status h1{font-size:19px;font-weight:650;margin:0 0 2px;letter-spacing:-.01em}
.sub{color:var(--muted);font-size:13.5px;margin-bottom:16px}
.tally{display:flex;flex-wrap:wrap;gap:26px;align-items:baseline}
.tally div{display:flex;align-items:baseline;gap:7px}
.tally b{font-size:26px;font-weight:650;letter-spacing:-.02em}
.tally span{font-size:13px;color:var(--muted)}
.dot{width:8px;height:8px;border-radius:50%%;display:inline-block;flex:none;transform:translateY(-2px)}
.d-pass{background:var(--pass)}.d-warn{background:var(--warn)}.d-fail{background:var(--fail)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:22px}
@media(max-width:760px){.grid2{grid-template-columns:1fr}}
.panel{background:var(--surface);border:1px solid var(--rule);padding:20px 22px;margin-bottom:22px}
.panel h2{font-size:13.5px;font-weight:600;color:var(--muted);margin:0 0 14px}
.bars{display:grid;grid-template-columns:58px 1fr 46px;gap:7px 12px;align-items:center;font-size:13.5px}
.track{background:#E7E9E5;height:15px}.fill{background:var(--data);height:15px}.fill.hi{background:var(--hi)}
.v{text-align:right;color:var(--muted)}
table{width:100%%;border-collapse:collapse;font-size:13.5px}
th{text-align:left;font-weight:600;color:var(--muted);font-size:12.5px;padding:0 0 9px;border-bottom:1px solid var(--rule)}
td{padding:10px 0;border-bottom:1px solid var(--rule);vertical-align:top}
tr:last-child td{border-bottom:0}
.note{color:var(--muted);font-size:12.5px;margin-top:6px}
footer{margin-top:26px;padding-top:16px;border-top:1px solid var(--rule);color:var(--muted);font-size:12.5px}
"""


def _bars(items, maxv, hi=None):
    out = ['<div class="bars">']
    for label, val in items:
        cls = "fill hi" if label == hi else "fill"
        out.append(f'<span>{html.escape(label)}</span>'
                   f'<span class="track"><span class="{cls}" style="width:{val/maxv*100:.1f}%"></span></span>'
                   f'<span class="v num">{val:.2f}</span>')
    out.append("</div>")
    return "".join(out)


def write_dashboard(rows, config, checks, tally, source_meta, path, run_date, elapsed):
    latest = max(r["period"] for r in rows if r["source"] == "KOSIS")
    sido = sorted(
        [(SIDO_LABEL[r["region_code"]], r["value"]) for r in rows
         if r["indicator_code"] == "TFR" and r["period"] == latest
         and r["region_code"] in SIDO_LABEL and r["value"] is not None],
        key=lambda t: -t[1])
    intl_year = {}
    for r in rows:
        if r["source"] == "WORLDBANK" and r["value"] is not None:
            k = ISO_LABEL.get(r["region_code"], r["region_code"])
            if r["period"] >= intl_year.get(k, (0, 0))[0]:
                intl_year[k] = (r["period"], r["value"])
    intl = sorted(((k, v[1]) for k, v in intl_year.items()), key=lambda t: -t[1])

    nat = {r["period"]: r["value"] for r in rows
           if r["region_code"] == "KR-00" and r["indicator_code"] == "TFR" and r["value"] is not None}
    yrs = sorted(nat)
    lo, hi = min(nat.values()), max(nat.values())
    span = (hi - lo) or 1
    pts = " ".join(f"{40 + i*(580/(len(yrs)-1)):.0f},{160 - (nat[y]-lo)/span*130:.0f}"
                   for i, y in enumerate(yrs))

    bar = "var(--fail)" if tally["실패"] else ("var(--warn)" if tally["확인"] else "var(--pass)")
    chk_rows = "".join(
        f'<tr><td>{html.escape(c["검사"])}'
        + (f'<div class="note">{html.escape(c["비고"])}</div>' if c["비고"] and c["결과"] != "통과" else "")
        + f'</td><td style="width:76px"><span class="dot d-'
        + ("pass" if c["결과"] == "통과" else "warn" if c["결과"] == "확인" else "fail")
        + f'"></span> {c["결과"]}</td><td style="width:88px;color:var(--muted);font-size:12.5px">{c["실패 시"]}</td></tr>'
        for c in checks)
    src_rows = "".join(
        f'<tr><td>{html.escape(m["name"])}</td><td class="num">{m["retrieved_at"]}</td>'
        f'<td>{m["mode"]}</td><td class="num">{m["elapsed_sec"]}초</td></tr>' for m in source_meta)

    doc = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(config['project'])}</title><style>{_CSS % {'barcolor': bar}}</style></head><body><div class="wrap">
<div class="status"><h1>{html.escape(config['project'])}</h1>
<div class="sub num">{datetime.now().strftime('%Y-%m-%d %H:%M')} 갱신 · 실행 {elapsed:.1f}초 · 스냅샷 raw/{run_date}/</div>
<div class="tally">
<div><span class="dot d-pass"></span><b class="num">{tally['통과']}</b><span>검증 통과</span></div>
<div><span class="dot d-warn"></span><b class="num">{tally['확인']}</b><span>확인 필요</span></div>
<div><span class="dot d-fail"></span><b class="num">{tally['실패']}</b><span>실패</span></div>
<div><b class="num">{len(rows):,}</b><span>행</span></div></div></div>

<div class="panel"><h2>전국 합계출산율 {min(yrs)}–{max(yrs)}</h2>
<svg viewBox="0 0 660 180" width="100%" height="150" role="img" aria-label="전국 합계출산율 추이">
<line x1="40" y1="160" x2="640" y2="160" stroke="#D3D7D0"/>
<text x="6" y="34" font-size="11" fill="#67707C">{hi:.2f}</text>
<text x="6" y="164" font-size="11" fill="#67707C">{lo:.2f}</text>
<polyline fill="none" stroke="#2F4B7C" stroke-width="2.2" points="{pts}"/>
<text x="40" y="176" font-size="11" fill="#67707C">{min(yrs)}</text>
<text x="600" y="176" font-size="11" fill="#67707C">{max(yrs)}</text></svg>
<p class="note">최근값 {nat[max(yrs)]:.3f}</p></div>

<div class="grid2">
<div class="panel"><h2>시도별 · {latest}년</h2>{_bars(sido, max(v for _, v in sido) * 1.1, hi=sido[-1][0])}</div>
<div class="panel"><h2>국제 비교 · 최근 가용연도</h2>{_bars(intl, max(v for _, v in intl) * 1.05, hi="한국")}
<p class="note">국가별 공표연도가 달라 최신 가용연도를 씁니다. 연도는 코드북에 기록됩니다.</p></div>
</div>

<div class="panel"><h2>검증 결과</h2><table>
<tr><th>검사</th><th>결과</th><th>실패 시</th></tr>{chk_rows}</table></div>

<div class="panel"><h2>수집 이력</h2><table>
<tr><th>소스</th><th>수집 시각</th><th>방식</th><th>소요</th></tr>{src_rows}</table>
<p class="note">전체 정의와 판정 이력은 out/codebook.md 에 있습니다.</p></div>

<footer>policy-data-pipeline · 잠정치가 확정치로 바뀌어도 과거 분석을 재현할 수 있도록 수집 시점 원본을 보관합니다.</footer>
</div></body></html>"""

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


# ────────────────────────────────────────────────────────────── 보고서용 표

def write_tables(rows, config, out_dir, run_date):
    """보고서 부록 형식 표. 출처 · 기준시점 · 단위를 표 하단에 자동으로 붙입니다."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment

    os.makedirs(out_dir, exist_ok=True)
    years = sorted({r["period"] for r in rows if r["indicator_code"] == "TFR" and r["region_code"] != "KR-00"})
    years = [y for y in years if y >= max(years) - 4]   # 최근 5개년
    sido = {}
    for r in rows:
        if r["indicator_code"] == "TFR" and r["region_code"] in SIDO_LABEL and r["period"] in years:
            sido.setdefault(SIDO_LABEL[r["region_code"]], {})[r["period"]] = r["value"]
    nat = {r["period"]: r["value"] for r in rows if r["region_code"] == "KR-00" and r["indicator_code"] == "TFR"}

    intl = {}
    for r in rows:
        if r["source"] == "WORLDBANK" and r["value"] is not None:
            k = ISO_LABEL.get(r["region_code"], r["region_code"])
            if r["period"] >= intl.get(k, (0, 0))[0]:
                intl[k] = (r["period"], r["value"])

    def fmt(v):
        return "" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))

    # 표 1: 시도별 합계출산율 (최근 5개년)
    t1 = ["# 표 1. 시도별 합계출산율 (최근 5개년)", "", "| 시도 | " + " | ".join(map(str, years)) + " |",
          "|---|" + "---|" * len(years)]
    t1.append("| 전국 | " + " | ".join(fmt(nat.get(y)) for y in years) + " |")
    for name in sorted(sido, key=lambda n: -(sido[n].get(max(years)) or 0)):
        t1.append(f"| {name} | " + " | ".join(fmt(sido[name].get(y)) for y in years) + " |")
    t1 += ["", f"주: 단위 명(여성 1명당). 출처 KOSIS 인구동향조사. 수집 {run_date}. 최신 연도는 잠정치일 수 있음. 빈칸은 결측(사유는 codebook.md 참조)."]

    # 표 2: 국제 비교 (최근 가용연도)
    t2 = ["# 표 2. 합계출산율 국제 비교 (최근 가용연도)", "", "| 국가 | 연도 | 합계출산율 |", "|---|---|---|"]
    for k, (y, v) in sorted(intl.items(), key=lambda kv: -kv[1][1]):
        t2.append(f"| {k} | {y} | {v:.2f} |")
    t2 += ["", f"주: 단위 명. 출처 World Bank Indicators SP.DYN.TFRT.IN. 수집 {run_date}. 국가별 공표연도가 달라 최신 가용연도를 표기함."]

    with open(os.path.join(out_dir, "tables.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(t1) + "\n\n" + "\n".join(t2) + "\n")

    wb = Workbook()
    ws = wb.active; ws.title = "표1 시도별"
    ws.append(["시도"] + years)
    ws.append(["전국"] + [nat.get(y) for y in years])
    for name in sorted(sido, key=lambda n: -(sido[n].get(max(years)) or 0)):
        ws.append([name] + [sido[name].get(y) for y in years])
    ws.append([]); ws.append([t1[-1]])
    ws2 = wb.create_sheet("표2 국제비교")
    ws2.append(["국가", "연도", "합계출산율"])
    for k, (y, v) in sorted(intl.items(), key=lambda kv: -kv[1][1]): ws2.append([k, y, v])
    ws2.append([]); ws2.append([t2[-1]])
    for w in (ws, ws2):
        for row in w.iter_rows():
            for c in row:
                c.font = Font(name="Arial", size=10, bold=(c.row == 1))
                if c.row == 1: c.alignment = Alignment(horizontal="center")
        w.column_dimensions["A"].width = 16
    wb.save(os.path.join(out_dir, "tables.xlsx"))


def run(rows, config, base, checks, tally, source_meta, unmapped, pending, run_date, elapsed, log=print):
    log("[4/4] 산출물 생성")
    out = os.path.join(base, "out")
    write_csv(rows, os.path.join(out, "panel.csv"))
    write_codebook(rows, config, checks, tally, source_meta, unmapped, pending,
                   os.path.join(out, "codebook.md"), run_date)
    write_dashboard(rows, config, checks, tally, source_meta,
                    os.path.join(out, "dashboard.html"), run_date, elapsed)
    write_tables(rows, config, os.path.join(out, "tables"), run_date)
    for f in ("panel.csv", "codebook.md", "dashboard.html", "tables/tables.md", "tables/tables.xlsx"):
        log(f"  out/{f}")
