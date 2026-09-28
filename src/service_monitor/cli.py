from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .monitor import check_service


def main() -> None:
    parser = argparse.ArgumentParser(description="Check HTTP service health")
    parser.add_argument("config", type=Path, help="JSON array of {name,url} objects")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=3.0)
    args = parser.parse_args()
    services = json.loads(args.config.read_text(encoding="utf-8"))
    checks = [check_service(item["name"], item["url"], args.timeout) for item in services]
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "ok": all(check.ok for check in checks),
        "checks": [check.as_dict() for check in checks],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
