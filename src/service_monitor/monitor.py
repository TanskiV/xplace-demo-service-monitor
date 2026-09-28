from __future__ import annotations

import ipaddress
import socket
import time
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _is_private_host(hostname: str) -> bool:
    host = hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"}:
        return True
    try:
        addresses = [ipaddress.ip_address(host)]
    except ValueError:
        try:
            addresses = [
                ipaddress.ip_address(info[4][0])
                for info in socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
            ]
        except socket.gaierror:
            return False
    return any(
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_reserved
        or address.is_unspecified
        for address in addresses
    )


def validate_public_url(url: str, *, allow_private_hosts: bool = False) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only an HTTP(S) URL with a hostname is supported")
    if not allow_private_hosts and _is_private_host(parsed.hostname):
        raise ValueError("Private, loopback, link-local and metadata hosts are not allowed")


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


def check_service(
    name: str,
    url: str,
    timeout: float = 3.0,
    *,
    allow_private_hosts: bool = False,
) -> CheckResult:
    started = time.perf_counter()
    try:
        validate_public_url(url, allow_private_hosts=allow_private_hosts)
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
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return CheckResult(name, url, False, None, latency_ms, str(exc))
