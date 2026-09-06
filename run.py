#!/usr/bin/env python3
"""인구 지표 패널 파이프라인.

    python run.py --offline      스냅샷으로 실행 (망이 막힌 환경, 수업용)
    python run.py                실시간 수집
    python run.py --break-check  검증 실패 시 어떻게 멈추는지 보기 위한 데모

수집 → 정규화 → 검증 → 산출물. 검증에서 중단 조건에 걸리면 산출물을 만들지 않습니다.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime

import yaml

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from scripts import collect, normalize, report, validate  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="스냅샷으로 실행")
    ap.add_argument("--break-check", action="store_true", help="검증 실패 상황을 일부러 만듭니다")
    ap.add_argument("--config", default="config/sources.yml")
    args = ap.parse_args()

    with open(os.path.join(BASE, args.config), encoding="utf-8") as f:
        config = yaml.safe_load(f)

    t0 = time.time()
    lines = []

    def log(msg=""):
        print(msg)
        lines.append(msg)

    log(f"{config['project']} · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        f"{' · 스냅샷 모드' if args.offline else ''}")
    log("-" * 58)

    try:
        payloads, source_meta, run_date = collect.run(config, BASE, offline=args.offline, log=log)
        rows, unmapped, pending = normalize.run(payloads, config, BASE, log=log)

        if args.break_check:
            rows[0]["value"] = 99.9   # 값 범위 검사를 일부러 위반시킵니다
            log("  [데모] 첫 행의 값을 99.9 로 바꿔 검증을 위반시킵니다")

        checks, tally = validate.run(rows, config, log=log)
        elapsed = time.time() - t0
        report.run(rows, config, BASE, checks, tally, source_meta,
                   unmapped, pending, run_date, elapsed, log=log)

    except (collect.CollectError, validate.ValidationFailed, ValueError) as e:
        log("")
        log(f"중단: {e}")
        _write_log(lines, ok=False)
        sys.exit(1)

    log("-" * 58)
    log(f"완료 · {len(rows):,}행 · {time.time() - t0:.1f}초")
    _write_log(lines, ok=True)


def _write_log(lines, ok):
    d = os.path.join(BASE, "logs")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{datetime.now():%Y-%m-%d}.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"at": datetime.now().isoformat(timespec="seconds"),
                            "ok": ok, "output": lines}, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
