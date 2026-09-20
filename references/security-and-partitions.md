# Authentication, installation, and partitions

## Authentication preference

Use the organization's established mechanism. Prefer, in order:

1. IAM Identity Center with short-lived role credentials.
2. Organization-approved credential process or federation tooling.
3. A pre-existing, explicitly approved short-lived profile.

Do not introduce static access keys as an onboarding shortcut. Do not transfer credentials between people or accounts. Never print the output of credential-process commands, environment variables containing credentials, cached SSO tokens, or `~/.aws/credentials`.

## Installation boundaries

Read-only detection is always the first step. Before an install, identify the package source, requested version, destination, and whether administrator privileges are required. Use vendor documentation and managed-software channels where available. Stop when endpoint management blocks installation; report the requested package and version to the owning team.

Do not curl a remote installer directly into a shell. Download and verify it first when manual installation is required. Preserve an existing AWS CLI installation until the replacement has been validated.

## Partition invariants

| Partition | ARN prefix | Common regions | Console/domain cue |
| --- | --- | --- | --- |
| Commercial | `arn:aws:` | `us-east-1`, `us-west-2` | `amazonaws.com` |
| GovCloud (US) | `arn:aws-us-gov:` | `us-gov-west-1`, `us-gov-east-1` | `amazonaws-us-gov.com` |
| China | `arn:aws-cn:` | `cn-north-1`, `cn-northwest-1` | `amazonaws.com.cn` |

An ARN returned from STS is authoritative for the active partition. Do not reuse commercial ARNs, endpoints, SSO settings, or account assumptions in GovCloud. GovCloud and commercial accounts are distinct even when controlled by the same organization.

For IAM Identity Center, the start URL and SSO region may differ from the workload region. Preserve that distinction. Do not infer either value from the database hostname.

## Diagnosis boundaries

- Browser login failure: capture the non-secret error and check start URL, SSO region, device clock, and organizational assignment.
- `sts:GetCallerIdentity` failure: treat as authentication/profile configuration.
- Correct identity but `AccessDenied`: treat as authorization; report the exact action and resource without attempting a workaround.
- Correct identity and permission but connection timeout: check approved route, managed-node status, DNS resolution from the remote path, and security controls with the owning network/platform team.
- TLS or database authentication failure after TCP succeeds: treat as database trust/authentication, not a reason to alter network controls.

