#!/usr/bin/env python3
"""Read-only workstation discovery for AWS developer onboarding."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from pathlib import Path


COMMANDS = {
    "aws": ["--version"],
    "session-manager-plugin": [],
    "psql": ["--version"],
    "mysql": ["--version"],
    "terraform": ["version"],
    "python3": ["--version"],
}


def command_details(name: str, version_args: list[str]) -> dict[str, object]:
    executable = shutil.which(name)
    if not executable:
        return {"installed": False}

    details: dict[str, object] = {"installed": True, "path": executable}
    try:
        result = subprocess.run(
            [executable, *version_args],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        combined = " ".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
        details["version"] = combined.splitlines()[0] if combined else "unknown"
        details["version_exit_code"] = result.returncode
    except (OSError, subprocess.TimeoutExpired) as exc:
        details["version_error"] = type(exc).__name__
    return details


def main() -> int:
    shell = os.environ.get("SHELL") or os.environ.get("COMSPEC") or "unknown"
    aws_dir = Path.home() / ".aws"
    report = {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "shell": shell,
        },
        "aws_configuration": {
            "directory_present": aws_dir.is_dir(),
            "config_present": (aws_dir / "config").is_file(),
            "credentials_file_present": (aws_dir / "credentials").is_file(),
        },
        "commands": {
            name: command_details(name, args) for name, args in COMMANDS.items()
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

