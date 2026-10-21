# Weekly AI Work Planner

**Plan short AI-assisted engineering sessions around capacity, dependencies and human decisions.**

English · [Español](README.es.md)

When several projects share AI tools, deciding what to run next is only part of the
problem. You also need to track the available capacity, understand what is blocked,
and recover safely when a session stops after making a change.

This project explores that workflow for developers and teams building engineering
automation. It keeps separate physical resource accounts, starts from a 70% planned /
20% incident / 10% uncertainty allocation, prioritizes blocking dependencies, and
records attempts, approvals and recovery evidence.

## Try it locally

The development environment runs a **synthetic fixture**, with PostgreSQL, a Java
HTTPS control plane, two workers, an effect receiver and an independent verifier.
There is no production web UI or connection to real AI providers.

On Linux with Docker Engine, Compose, Python 3, Bash and OpenSSL, from the repository
root:

```bash
cp .env.example .env
python3 dev/dev.py build
python3 dev/dev.py up
python3 dev/dev.py smoke
```

The first build downloads pinned images and Maven dependencies. Java 21 and Maven
run inside Docker. HTTPS endpoints bind only to `127.0.0.1`; ports are set in `.env`.
The smoke executes one synthetic operation and verifies it independently. Repeating
it checks the preserved result without spending capacity again.

```bash
python3 dev/dev.py status
python3 dev/dev.py logs --service worker-a
python3 dev/dev.py stop
```

Data stays in `run_data/local/`; `up` resumes that session. A worker with local
history requires explicit recovery after restart. Synthetic identities expire after
48 hours; use the explicit selective reset to start a fresh fixture. See the
[development guide](docs/DEVELOPMENT.md) for HTTPS access, rebuilds, persistence,
reset and troubleshooting.

## What works today

- Java 21 scheduling libraries and PostgreSQL persistence contracts.
- Synthetic HTTPS workers, fencing, checkpoints, independent verification and
  explicit recovery paths.
- A persistent local development entry point, separate from the disposable SQL
  batteries and the D4 validation laboratory.

D1–D4 are **approved and closed within their recorded scope**. Their designs,
manifests and historical evidence remain in the [documentation index](docs/README.md)
and [validation overview](docs/validation/README.md). The
[D4 closure manifest](docs/validation/D4-CLOSURE.json) defines the synthetic boundary.
Source ingestion/integrations (D5) and governance/operations (D6) remain future work.
Local development does not promote SQL proposals or authorize deployment.

## Explore and contribute

Start with the [technical development guide](docs/DEVELOPMENT.md), then the
[approved architecture](docs/design/D1-architecture-baseline.md) and
[scheduler core](scheduler-core/README.md). The guide also links the independent
SQL and D4 test runners.

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md) before sharing
changes or diagnostics. Before staging files, run `python3 scripts/check-publication.py`
and review the diff. Generated data, private identities and raw logs stay out of Git.

Licensed under **GPL-3.0-only**: [LICENSE](LICENSE), [NOTICE](NOTICE),
[licensing guide](LICENSING.md) and [third-party notices](THIRD-PARTY-NOTICES.md).
