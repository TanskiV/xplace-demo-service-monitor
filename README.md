# Service Monitor Demo

Demonstration/reference project; not client work. It uses a synthetic
configuration, requires no credentials and sends no alerts.

Small reference utility that checks a list of HTTP health endpoints and writes
a JSON report with status, latency, timestamp and an overall pass/fail result.
It is designed for bounded diagnostics: no credentials, no alert delivery and
no production endpoints are included. Private, loopback, link-local, metadata
and non-HTTP(S) targets are rejected by default; local test servers use an
explicit test-only opt-in. Redirects are not followed.

This is a demonstration/reference project, not a client monitoring system.

## Run

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
python -m service_monitor.cli examples/services.json --output build/report.json
```

The sample uses `example.test` placeholders and is intentionally not expected
to reach a real service. A permitted public endpoint may be supplied for a
local diagnostic after reviewing its terms and scope.

## Test

```bash
python -m unittest discover -s tests -v
```

## Business problem

Before debugging an application, an operator needs a reproducible snapshot of
which endpoints respond, how quickly, and when the check happened. This tool
keeps that first diagnostic small, explicit and easy to automate later.
