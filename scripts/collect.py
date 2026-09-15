"""수집 단계.

원칙
- 원본 응답은 손대지 않고 그대로 raw/{실행일}/ 에 저장합니다. 재현의 근거입니다.
- 실패를 조용히 넘기지 않습니다. 0건이거나 부분 수집이면 예외를 던집니다.
- --offline 이면 raw/sample/ 의 스냅샷을 씁니다. 망이 막힌 환경과 수업용입니다.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime

RETRY = 3
BACKOFF = 1.5


class CollectError(RuntimeError):
    pass


def _snapshot(base, run_date, source_id, payload):
    d = os.path.join(base, "raw", run_date)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{source_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    return path


def _request(url, params, timeout=30):
    """재시도와 백오프. 횟수를 제한해 무한 반복을 막습니다.

    응답이 JSON이 아니면 재시도하지 않습니다. 일시적 장애가 아니라 요청이
    잘못된 경우이기 때문입니다. 기관 API는 이럴 때 200과 함께 에러 객체를
    돌려주는 일이 많아, 원문 앞부분을 그대로 보여줍니다.
    """
    import requests

    last = None
    for attempt in range(RETRY):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            if r.status_code == 429:
                raise CollectError("호출 제한(429)")
            r.raise_for_status()
            try:
                return r.json()
            except ValueError:
                body = (r.text or "").strip().replace("\n", " ")[:300]
                raise CollectError(
                    "응답 본문이 JSON이 아닙니다. 파라미터나 인증키를 확인하세요.\n"
                    f"    요청: {r.url.split('?')[0]}\n"
                    f"    본문: {body}"
                ) from None
        except CollectError:
            raise
        except Exception as e:  # noqa: BLE001
            last = e
            if attempt < RETRY - 1:
                time.sleep(BACKOFF ** attempt)
    raise CollectError(f"{RETRY}회 재시도 후 실패: {last}")


def fetch(source, base, run_date, offline=False, log=print):
    """소스 하나를 수집해 원본 payload를 돌려줍니다."""
    sid = source["id"]

    if offline or source["kind"] == "web":
        path = os.path.join(base, source["sample"])
        if not os.path.exists(path):
            raise CollectError(f"샘플 스냅샷이 없습니다: {path}")
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        log(f"  [{sid}] 스냅샷 사용 {os.path.basename(path)}")
    else:
        auth = source.get("auth", {})
        params = dict(source.get("params", {}))
        if auth.get("required"):
            key = os.environ.get(auth.get("env", ""), "")
            if not key:
                raise CollectError(
                    f"[{sid}] 인증키가 없습니다. 환경변수 {auth.get('env')} 를 설정하거나 --offline 으로 실행하세요."
                )
            params[auth["param"]] = key
        url = source["endpoint"]
        if "{" in url:
            url = url.format(**{k: params.pop(k) for k in list(params) if "{%s}" % k in url})
        payload = _request(url, params)
        log(f"  [{sid}] 호출 완료")

    _verify_not_silent(sid, payload)
    _snapshot(base, run_date, sid, payload)
    return payload


def _verify_not_silent(sid, payload):
    """조용한 실패 탐지. 0건을 정상 종료로 처리하지 않습니다."""
    if payload is None:
        raise CollectError(f"[{sid}] 응답이 비어 있습니다")

    # 이 파이프라인의 소스는 전부 배열을 돌려줍니다. 객체 하나가 왔다면
    # 대개 에러 응답입니다. 여기서 막지 않으면 정규화까지 흘러가
    # 엉뚱한 자리에서 터집니다(조용한 실패).
    if isinstance(payload, dict):
        detail = ", ".join(f"{k}={v!r}" for k, v in list(payload.items())[:6])
        raise CollectError(
            f"[{sid}] 배열이 와야 하는데 객체가 왔습니다. 대개 에러 응답입니다.\n"
            f"    응답: {detail[:400]}"
        )

    if isinstance(payload, list) and len(payload) == 2 and isinstance(payload[0], dict) \
            and "total" in payload[0]:
        meta, rows = payload
        total, got = int(meta.get("total", 0)), len(rows)
        if total == 0 or got == 0:
            raise CollectError(f"[{sid}] 수집 0건. 요청 조건을 확인하세요.")
        if got < total:
            raise CollectError(f"[{sid}] 부분 수집 {got}/{total}건. 페이지 처리를 확인하세요.")
        return

    if isinstance(payload, list) and len(payload) == 0:
        raise CollectError(f"[{sid}] 수집 0건. 요청 조건을 확인하세요.")


def run(config, base, offline=False, log=print):
    run_date = datetime.now().strftime("%Y-%m-%d")
    log("[1/4] 수집")
    payloads, meta = {}, []
    for src in config["sources"]:
        t0 = time.time()
        payloads[src["id"]] = fetch(src, base, run_date, offline=offline, log=log)
        meta.append({
            "source_id": src["id"], "name": src["name"],
            "retrieved_at": datetime.now().isoformat(timespec="seconds"),
            "elapsed_sec": round(time.time() - t0, 2),
            "mode": "스냅샷" if (offline or src["kind"] == "web") else "실시간",
        })
    return payloads, meta, run_date
