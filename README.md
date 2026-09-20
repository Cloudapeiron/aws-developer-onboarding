# AWS Developer Onboarding Skill

A reusable Codex skill for safely preparing and diagnosing developer workstations that need access to AWS workloads. It supports AWS CLI v2, IAM Identity Center, commercial AWS, AWS GovCloud, Systems Manager, and approved private-database connection paths.

The skill emphasizes identity verification, short-lived credentials, least privilege, explicit approval for persistent changes, and clear separation between local configuration, AWS authorization, network reachability, and database authentication failures.

## What it does

The skill operates in three modes:

- **Audit** — inspect local prerequisites and the active AWS identity without changing the workstation.
- **Setup** — install approved prerequisites, configure a named AWS profile, authenticate, and verify access.
- **Diagnose** — reproduce a failure and identify whether it belongs to local configuration, authentication, authorization, networking, or database access.

Key capabilities include:

- Detecting the operating system, architecture, shell, and installed tooling.
- Verifying the AWS account, partition, region, and assumed role.
- Supporting `aws`, `aws-us-gov`, and `aws-cn` partitions.
- Preferring IAM Identity Center and other short-lived credential mechanisms.
- Establishing approved Systems Manager port-forwarding sessions to private databases.
- Preventing workstation onboarding from silently changing IAM, security groups, routing, endpoints, or databases.

## Project structure

```text
aws-developer-onboarding/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── private-database-access.md
│   └── security-and-partitions.md
└── scripts/
    ├── preflight.py
    └── verify_aws_context.py
```

- `SKILL.md` defines when the skill applies, its workflow, and its safety boundaries.
- `agents/openai.yaml` provides display metadata and a default invocation prompt.
- `references/` contains detailed guidance loaded only when relevant.
- `scripts/` contains deterministic, read-only discovery and identity checks.

## Requirements

- Codex with local skill support.
- Python 3.
- AWS CLI v2 for authentication and AWS identity verification.
- Session Manager plugin when the approved access path requires it and the installed AWS CLI distribution does not include it.
- A database client such as `psql` or `mysql` only when database access is requested.

The skill does not request or store passwords, access keys, secret keys, session tokens, MFA codes, private keys, or database secrets.

## Install for local Codex use

Clone the repository to a stable local directory:

```bash
git clone https://github.com/Cloudapeiron/aws-developer-onboarding.git
cd aws-developer-onboarding
```

Create the local skills directory and symlink the repository into it:

```bash
mkdir -p ~/.agents/skills
ln -s "$(pwd)" ~/.agents/skills/aws-developer-onboarding
```

Codex can then select the skill when a request matches its description. It can also be invoked explicitly:

```text
$aws-developer-onboarding audit this Mac for approved AWS GovCloud access.
```

If the skill does not appear after installation, restart Codex.

## Example requests

```text
$aws-developer-onboarding audit my workstation for AWS CLI, SSO, and Session Manager prerequisites.
```

```text
$aws-developer-onboarding configure an approved AWS IAM Identity Center profile and verify the expected account and role.
```

```text
$aws-developer-onboarding diagnose why my SSM tunnel reaches the managed node but not the private PostgreSQL endpoint.
```

## Run the deterministic checks directly

Read-only workstation discovery:

```bash
python3 scripts/preflight.py
```

Review the AWS identity verifier's supported arguments:

```bash
python3 scripts/verify_aws_context.py --help
```

Example identity verification:

```bash
python3 scripts/verify_aws_context.py \
  --profile project-dev \
  --region us-gov-west-1 \
  --expected-account 123456789012 \
  --expected-partition aws-us-gov \
  --expected-role DeveloperAccess
```

Use only non-sensitive account, profile, region, partition, and role identifiers in commands and logs.

## Safety boundaries

This skill is limited to workstation onboarding and diagnostics. It does not:

- provision or modify AWS infrastructure;
- create IAM users, policies, roles, or permission assignments;
- open security groups or make private databases public;
- change routes, endpoints, VPNs, managed nodes, or database configuration;
- run database write queries;
- continue when the verified account, partition, or role does not match the approved access contract.

Infrastructure changes should be managed through the project's approved infrastructure-as-code and peer-review workflow.

## Development workflow

Before committing changes:

```bash
python3 scripts/preflight.py
python3 scripts/verify_aws_context.py --help
```

Changes to the skill should keep the entrypoint focused, place conditional detail in `references/`, and use scripts only where deterministic behavior improves reliability.
