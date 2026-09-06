"""장애 주입기. 실제 API 대신 씁니다. 네트워크 없이 돌아갑니다.

시나리오: normal · flaky · rate_limit · empty · paged · drift · html

사용 예:
    from fake_api import FakeAPI, SCENARIOS
    api = FakeAPI("paged")
    r = api.get("https://api.example/v2/indicator", params={"page": 1, "per_page": 500})
    payload = r.json()
"""


class FakeResponse:
    def __init__(self, status, payload=None):
        self.status_code = status
        self._payload = payload

    def json(self):
        if self._payload is None:
            raise ValueError("본문이 JSON이 아닙니다")
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def _rows(country, years, per_page, page, drift=False):
    key = "iso3" if drift else "countryiso3code"
    all_rows = [{
        "indicator": {"id": "SP.DYN.TFRT.IN"},
        key: country,
        "date": str(y),
        "value": None if y == 2019 else round(1.3 - 0.05 * (y - 2015), 3),
    } for y in years]
    start = (page - 1) * per_page
    return all_rows, all_rows[start:start + per_page]


class FakeAPI:
    def __init__(self, scenario="normal"):
        self.scenario = scenario
        self.calls = 0

    def get(self, url, params=None, timeout=None):
        self.calls += 1
        params = params or {}
        page = int(params.get("page", 1))
        per_page = int(params.get("per_page", 50))
        years = list(range(2015, 2026))
        if self.scenario == "rate_limit" and self.calls <= 2:
            return FakeResponse(429)
        if self.scenario == "flaky" and self.calls == 1:
            raise TimeoutError("연결 시간 초과")
        if self.scenario == "empty":
            return FakeResponse(200, [{"page": 1, "pages": 1, "per_page": per_page, "total": 0}, []])
        if self.scenario == "html":
            return FakeResponse(200, None)
        pp = 4 if self.scenario == "paged" else per_page
        all_rows, chunk = _rows("KOR", years, pp, page, drift=(self.scenario == "drift"))
        meta = {"page": page, "pages": (len(all_rows) + pp - 1) // pp, "per_page": pp, "total": len(all_rows)}
        return FakeResponse(200, [meta, chunk])


SCENARIOS = ["normal", "flaky", "rate_limit", "empty", "paged", "drift", "html"]
