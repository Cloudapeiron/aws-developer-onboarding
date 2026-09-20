---
name: aws-developer-onboarding
description: Prepare or diagnose a developer workstation for approved AWS CLI, IAM Identity Center, GovCloud, Systems Manager, and private database access. Use for repeatable AWS project onboarding; do not use it to provision cloud infrastructure or grant permissions.
---

# AWS Developer Onboarding

Turn the project's approved access details into a working, verified local setup. Keep the workflow local to the workstation: never create or modify IAM policies, security groups, routes, endpoints, instances, databases, or other AWS infrastructure.

## Choose the mode

- **Audit:** inspect prerequisites and identity without changing the workstation.
- **Setup:** install approved local prerequisites, create or update a named AWS profile, authenticate, and verify access.
- **Diagnose:** reproduce the failing step, distinguish local configuration from AWS authorization or network reachability, and report the smallest corrective action.

If the user did not specify a mode, infer it from the request. Start with read-only discovery in every mode.

## Establish the access contract

Before changing anything, obtain or locate the values that materially constrain safe access:

- AWS partition: `aws`, `aws-us-gov`, or `aws-cn`;
- approved account ID or account allowlist;
- approved role or permission set;
- region and profile name;
- Identity Center start URL and SSO region, when SSO is used;
- database engine, hostname, remote port, and desired local port;
- approved connection path: direct private network, Client VPN, or Systems Manager through a named managed node.

Do not ask for values already present in project documentation or configuration. Never ask for passwords, access keys, secret keys, session tokens, MFA codes, private keys, or database secrets in chat. Treat a missing account, role, region, or connection path as a blocker to that step, not permission to guess.

Read [references/security-and-partitions.md](references/security-and-partitions.md) when selecting authentication, installing AWS tooling, handling GovCloud, or diagnosing a partition mismatch. Read [references/private-database-access.md](references/private-database-access.md) only when database connectivity is requested.

## Run read-only discovery

Run `python3 scripts/preflight.py` from this skill directory. Use its JSON output to identify the operating system, architecture, shell, and installed tool versions. Also inspect relevant project-local onboarding files if the user identified a repository.

Do not recursively search the home directory or print AWS configuration/credential file contents. It is acceptable to list profile names with `aws configure list-profiles`; do not display resolved credential values.

Summarize what is present, missing, and incompatible. In setup mode, present the exact persistent local changes before making them unless the user's request already authorized those exact changes. Obtain confirmation before using administrator privileges, installing packages, replacing a profile, modifying shell startup files, or starting a long-lived tunnel.

## Install or verify local prerequisites

Install only what the selected path requires:

- AWS CLI v2;
- Session Manager plugin when Systems Manager is the approved path and it is not integrated into the installed CLI distribution;
- the relevant database client;
- optional project-declared tools such as Terraform only when part of the onboarding request.

Prefer vendor-supported installers or the organization's approved package manager. Verify package origin and signatures or checksums when the distribution method provides them. Do not disable platform security controls or bypass a managed-device policy. Re-run the preflight after changes.

## Configure authentication

Prefer IAM Identity Center or another organization-approved short-lived credential flow. For Identity Center, use a named profile and `aws configure sso` or the organization's existing `sso-session` configuration, then run `aws sso login --profile <profile>`.

Do not create static IAM users or store long-lived access keys. Do not overwrite an existing profile silently. When a profile already exists, inspect only its non-secret settings, show the proposed difference, and preserve unrelated profiles.

Authentication in a browser may require the user to complete the sign-in. Never copy device codes or tokens into logs or artifacts.

## Verify the AWS context

After authentication, run:

```bash
python3 scripts/verify_aws_context.py \
  --profile <profile> \
  --region <region> \
  --expected-account <12-digit-account> \
  --expected-partition <partition> \
  --expected-role <role-or-permission-set-name>
```

Omit only expectations the user genuinely did not supply. Do not continue to private-resource access when the account, partition, or role check fails. A successful `sts:GetCallerIdentity` proves identity, not authorization to a database or workload.

## Establish private database access

Follow the approved pattern in [references/private-database-access.md](references/private-database-access.md). Prefer an existing Systems Manager path or approved private network. Never make the database public, add `0.0.0.0/0` ingress, open a security group, create an ad hoc bastion, or change routing as part of workstation onboarding.

Show the fully resolved command with non-secret identifiers before starting a tunnel. Keep credentials out of command-line arguments and saved connection strings. Bind local forwarding to loopback. If the requested local port is occupied, select an unused high port and report it rather than terminating the existing process.

## Validate and hand off

Validate each layer separately:

1. Required binaries execute and meet project version requirements.
2. The named profile authenticates to the expected account, partition, region, and role.
3. The approved managed node or private route is reachable.
4. The local forwarded port accepts a TCP connection.
5. The database client reaches the server; authentication is performed by the user or an approved short-lived method.

Do not run write queries. If a database validation query is authorized, use the engine's read-only identity/version query.

Finish with a concise report containing the profile, partition, account, role, region, connection method, local endpoint, validation results, files changed, and exact teardown command. Redact secrets and ephemeral tokens. Separate local failures from AWS permission or network failures, and name the owning team for any required external fix.
