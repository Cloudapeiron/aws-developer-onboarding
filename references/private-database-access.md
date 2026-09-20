# Private database access patterns

Use only a connection path approved by the project. These commands are templates: resolve every bracketed value and show the result before execution.

## Systems Manager through a managed node

Use this pattern when an existing SSM-managed EC2 instance or hybrid managed node can resolve and reach the private database:

```bash
aws ssm start-session \
  --profile <profile> \
  --region <region> \
  --target <managed-node-id> \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters '{"host":["<private-db-host>"],"portNumber":["<remote-port>"],"localPortNumber":["<local-port>"]}'
```

Bind and connect only through `127.0.0.1:<local-port>`. The AWS CLI/session plugin keeps the foreground process open; `Ctrl-C` is the normal teardown. Do not daemonize it unless the user explicitly requests managed background operation and a cleanup mechanism is provided.

Required AWS-side prerequisites are normally `ssm:StartSession` authorization, an online managed node, the named SSM document, DNS resolution from that node, and permitted node-to-database traffic. The skill diagnoses these prerequisites but does not create or change them.

## Port forwarding to the managed node itself

When the service listens on the managed node rather than a different host:

```bash
aws ssm start-session \
  --profile <profile> \
  --region <region> \
  --target <managed-node-id> \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["<remote-port>"],"localPortNumber":["<local-port>"]}'
```

Do not substitute this document for remote-host forwarding when the database is on RDS or another host.

## Existing private network

When Client VPN, Direct Connect, a corporate VPN, or another approved private route is already established, validate DNS and TCP reachability without changing routing. Use the private hostname and require TLS. Do not save a database password in a shell variable, URI, history, `.pgpass`, or client profile unless the organization's approved secret-handling procedure explicitly calls for it.

## Client checks

Use loopback for a forwarded session:

```bash
nc -vz 127.0.0.1 <local-port>
```

Then use the appropriate client with TLS. Prefer interactive password entry, IAM database authentication, or the organization's approved secret broker. Do not echo or log generated auth tokens.

Read-only validation examples, only after database authentication is authorized:

- PostgreSQL: `select current_user, current_database(), version();`
- MySQL/MariaDB: `select current_user(), database(), version();`

Do not enumerate schemas or data as part of onboarding unless separately requested and authorized.

