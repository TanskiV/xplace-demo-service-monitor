from __future__ import annotations

import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class CheckResult:
    name: str
    url: str
    ok: bool
    status: int | None
    latency_ms: float | None
    error: str | None

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "url": self.url,
            "ok": self.ok,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "error": self.error,
        }


def check_service(name: str, url: str, timeout: float = 3.0) -> CheckResult:
    started = time.perf_counter()
    try:
        request = Request(url, headers={"User-Agent": "service-monitor-demo/0.1"})
        with urlopen(request, timeout=timeout) as response:
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            return CheckResult(name, url, 200 <= response.status < 400, response.status, latency_ms, None)
    except HTTPError as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        try:
            return CheckResult(name, url, False, exc.code, latency_ms, str(exc))
        finally:
            exc.close()
    except (URLError, TimeoutError, OSError) as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return CheckResult(name, url, False, None, latency_ms, str(exc))
