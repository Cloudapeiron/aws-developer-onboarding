#!/usr/bin/env python3
"""Verify active AWS identity against an explicit onboarding contract."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile", help="Named AWS CLI profile")
    p.add_argument("--region", help="Expected workload region")
    p.add_argument("--expected-account", action="append", default=[], help="Allowed 12-digit account; repeatable")
    p.add_argument("--expected-partition", choices=("aws", "aws-us-gov", "aws-cn"))
    p.add_argument("--expected-role", help="Expected assumed-role or IAM principal name")
    return p


def identity_command(args: argparse.Namespace) -> list[str]:
    command = ["aws", "sts", "get-caller-identity", "--output", "json"]
    if args.profile:
        command.extend(["--profile", args.profile])
    if args.region:
        command.extend(["--region", args.region])
    return command


def principal(arn: str) -> tuple[str, str]:
    resource = arn.split(":", 5)[-1]
    if resource.startswith("assumed-role/"):
        pieces = resource.split("/")
        return "assumed-role", pieces[1] if len(pieces) > 1 else resource
    if resource.startswith("user/"):
        return "iam-user", resource.rsplit("/", 1)[-1]
    if resource == "root":
        return "root", "root"
    return "other", resource


def main() -> int:
    args = parser().parse_args()
    if not shutil.which("aws"):
        print(json.dumps({"verified": False, "error": "AWS CLI was not found"}, indent=2))
        return 2

    try:
        result = subprocess.run(
            identity_command(args), capture_output=True, text=True, timeout=30, check=False
        )
    except subprocess.TimeoutExpired:
        print(json.dumps({"verified": False, "error": "STS identity check timed out"}, indent=2))
        return 2

    if result.returncode != 0:
        error_line = next((line.strip() for line in result.stderr.splitlines() if line.strip()), "STS identity check failed")
        print(json.dumps({"verified": False, "error": error_line}, indent=2))
        return 2

    try:
        identity = json.loads(result.stdout)
        account = str(identity["Account"])
        arn = str(identity["Arn"])
        partition = arn.split(":", 2)[1]
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
        print(json.dumps({"verified": False, "error": f"Unexpected STS response: {type(exc).__name__}"}, indent=2))
        return 2

    principal_kind, principal_name = principal(arn)
    checks: dict[str, bool] = {}
    if args.expected_account:
        checks["account"] = account in args.expected_account
    if args.expected_partition:
        checks["partition"] = partition == args.expected_partition
    if args.expected_role:
        checks["role"] = principal_name == args.expected_role

    report = {
        "verified": all(checks.values()) if checks else True,
        "profile": args.profile or "default resolution chain",
        "region": args.region,
        "account": account,
        "partition": partition,
        "arn": arn,
        "principal_kind": principal_kind,
        "principal_name": principal_name,
        "checks": checks,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
