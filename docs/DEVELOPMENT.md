# Local development / Desarrollo local

[English introduction](../README.md) · [Presentación en español](../README.es.md)

This guide describes the development fixture, not a production application. / Esta
guía describe la fixture de desarrollo, no una aplicación de producción.
D1–D4 remain approved and closed. No D5/D6, real provider, migration promotion or
deployment is included. [Validation of this environment](validation/DEV-ENV-results.md).

## Requirements / Requisitos

Validated on Linux with a local Docker Engine 29.9.1 and Compose 5.6.0. You need
Docker daemon access, Python 3, Bash, OpenSSL, GNU `timeout`, Git and enough memory
for five Java services (384 MiB each), PostgreSQL and build containers. `curl` is
used for optional host diagnostics. Java 21/Maven run inside Docker; neither is
required on the host. The repository path must be visible to the local daemon.
Windows, macOS, rootless/remote Docker and older Compose are not validated.

El primer build necesita acceso al registro Docker y a Maven Central. No se promete
arranque offline. El build utiliza imágenes fijadas por digest y guarda su caché
propia en `run_data/cache/m2`; no necesita la caché D4 ni modifica sus campañas.
Las bibliotecas empaquetadas conservan los [avisos de terceros](../THIRD-PARTY-NOTICES.md).

## Start / Arranque

From the repository root / Desde la raíz:

```bash
cp .env.example .env
python3 dev/dev.py config
python3 dev/dev.py build
python3 dev/dev.py up
python3 dev/dev.py smoke
```

Copy `.env.example` only when creating your configuration; keep an existing `.env`.
The parser accepts literal, unquoted `DEV_KEY=value` lines and comments on separate
lines, without interpolation or shell execution. Exported variables take precedence;
`--instance NAME` overrides `DEV_INSTANCE`. Allowed instance names match
`[a-z][a-z0-9-]{0,30}`. Do not run concurrent commands on the same instance.
Use the wrapper, not bare `docker compose up`: it selects paths, builds the image,
generates synthetic credentials and applies bootstrap only once.

El primer `up` genera identidades locales, crea la base vacía y aplica explícitamente
las propuestas V1–V30 **solo dentro de la fixture**. Después arranca y espera a que
los servicios estén sanos. Si el bootstrap se interrumpe, inspecciona los logs y
haz un reset explícito de esa instancia antes de repetirlo. No se repara una base
parcial insertando fixtures otra vez.

`smoke` runs one SUCCESS fixture through the worker, actual subprocess and receiver.
The host observes/signs process facts; the independent verifier checks them and
accepts the result via HTTPS. SQL accounting must show one attempt, one reservation,
one effect and consumption of eight synthetic units. Repeated smoke checks the
existing acceptance/accounting without executing again; it does not exercise a
second operation. Failures return a nonzero exit code. Reports stay in
`run_data/NAME/logs/`, separately from historical evidence.

## Topology and HTTPS / Topología y HTTPS

| Service | Responsibility / Función | Host HTTPS port (default) |
|---|---|---|
| db | Persistent PostgreSQL fixture / Base sintética | None |
| control-plane | HTTPS protocol and guarded SQL / Protocolo y SQL protegido | 18443 |
| effect-receiver | Durable synthetic effects / Efectos sintéticos durables | 18444 |
| worker-a, worker-b | Supervisors and mTLS sessions; no SQL / Supervisores sin SQL | 18445, 18446 |
| verifier | Independent evidence; read-only worker state / Evidencia independiente | 18447 |
| driver | Restricted diagnostic client / Cliente de diagnóstico restringido | None |
| diagnostics | Fixed TCP relay; TLS passthrough / Paso TCP sin terminar TLS | Publishes the five ports above |
| migrate | Explicit one-shot bootstrap profile / Bootstrap de una sola ejecución | None |

The three application networks remain `internal`. The diagnostic relay alone also
joins a normal bridge so Docker can publish ports, all hardcoded to **127.0.0.1**.
It has no TLS keys, SQL credentials, persistence network or Docker socket. Its only
routes are the five fixed service endpoints; it cannot relay arbitrary destinations.
Workers keep no Internet route. All application containers run without root, with
read-only image filesystems, capabilities dropped and resource limits. PostgreSQL
and the one-shot bootstrap have their documented initialization privileges; these
trusted fixtures are not a sandbox for hostile code. No container has Docker authority.

El acceso desde host sigue exigiendo mTLS. Para `local`, con los puertos por defecto:

```bash
curl --fail --cacert run_data/local/identity/public/ca.crt \
  --cert run_data/local/identity/private/driver.crt \
  --key run_data/local/identity/private/driver.key \
  https://localhost:18443/lab/health
```

Use `localhost` for certificate hostname verification; the binding is IPv4 loopback.
Change the five `DEV_*_PORT` values in `.env`, then run `up` to recreate the relay.
Do not disable certificate checks or use real credentials. The driver can inspect
worker state at `https://localhost:18445/lab/state`. Service-specific authorization
still applies: the driver cannot mint verification evidence.

## Daily work / Trabajo diario

```bash
python3 dev/dev.py status
python3 dev/dev.py logs --service worker-a
python3 dev/dev.py rebuild
python3 dev/dev.py smoke
python3 dev/dev.py stop
python3 dev/dev.py up
python3 dev/dev.py restart
```

Builds snapshot local sources into `run_data/builds/`, compile/package them, and
record hashes and image IDs. `build` only prepares/selects an image. `rebuild`
requires an initialized, running fixture, performs a build and recreates application
services while retaining data. For an
isolated Java service change you can use:

```bash
python3 dev/dev.py rebuild --service control-plane
```

All Java services share one image. A targeted rebuild immediately recreates only
that service; the next full `up` applies the selected image to the other services.
Use full rebuild for changes to shared libraries. There is no watch/hot reload.
Changing Java, resources or packaged fixture SQL requires rebuild; changing ports
requires `up`. Changing SQL does not migrate an existing fixture: inspect the
proposal, then explicitly reset to create a fresh database with the new image.
A bootstrap still expects the existing V30 contract; extending that contract is
outside this environment task.

`stop` saves a log snapshot and stops containers; `up` starts them again. `restart`
restarts services and waits for readiness. Neither clears journals or grants
acceptance, leases or authorization. A worker with local history returns as
**RECOVERY_REQUIRED**, with a fresh presence incarnation; it cannot adopt an old
execution. Smoke may still check an already accepted result in that state.

La retirada de un intento terminal exige un comando humano explícito. Solo cuando
el control plane acredita que es retirable y el supervisor observa EXITED, la ruta
existente puede retirarlo:

```bash
curl --fail --cacert run_data/local/identity/public/ca.crt \
  --cert run_data/local/identity/private/driver.crt \
  --key run_data/local/identity/private/driver.key \
  -H 'Content-Type: application/json' -d '{}' \
  https://localhost:18445/lab/recovery/retire
```

This is not a generic recovery/rearm command. Uncertain, active or blocked attempts
remain subject to the [approved D4 recovery contracts](design/D4-approved.md) and
[decisions A01–A24](design/D4-DECISIONS.md). The wrapper does not automate checkpoint
continuation, retry approval or polling rearm. For a fresh experiment, selective
reset discards the chosen synthetic session explicitly.

## Storage and selective reset / Persistencia y reset selectivo

User decision: persistent bind mounts inside the repository (`run_data/`), manual
rebuild and `.env`-configured loopback HTTPS; TCP relay approved separately to keep
worker network isolation. These directories are ignored by Git:

```text
run_data/NAME/state/db/        PostgreSQL data (may be owned by container UID 999)
run_data/NAME/state/receiver/  Receiver journal
run_data/NAME/state/worker-*/  Supervisor/job/loop history
run_data/NAME/identity/        Synthetic private keys, config and host observations
run_data/NAME/logs/            Local logs and smoke results
run_data/NAME/image.txt        Selected development image
run_data/cache/m2/            Independent Maven cache
run_data/builds/              Source snapshots, build logs and image metadata
```

The directory and identity files are private; do not commit or share them. The
bootstrap uses root with CHOWN to initialize only its bound fixture paths. Treat
`state/` as one consistency unit: **do not delete just PostgreSQL or a worker
journal**. Container removal alone does not remove bind-mounted data.

```bash
python3 dev/dev.py reset --instance local
python3 dev/dev.py up --instance local
python3 dev/dev.py smoke --instance local
```

`reset` is destructive for that synthetic instance and needs no additional prompt:
it stops/removes only Compose project `wap-dev-NAME`, deletes only that instance's
four state directories and identities, and removes its bootstrap marker. Logs,
image selection, build snapshots and cache remain. It uses no global prune and
never targets D2/D3/D4 projects or `work/` evidence. A subsequent `up` generates
new identities and data. Do not use symlinks for instance storage.

Para otra instancia, usa otro nombre y cinco puertos libres mediante variables
`DEV_*_PORT` exportadas o un cambio de `.env`. Cada instancia necesita su propio
`build`, configuración y base. Detén una
instancia antes de reutilizar sus puertos. `--instance` también selecciona el
proyecto para logs, parada y reset.

## Troubleshooting and limits / Problemas y límites

- Docker permission denied: use an account authorized for the local daemon.
- First build fails: inspect the newest `run_data/builds/*/build.log` or
  `image-build.log`; check registry/Maven access. A failed build keeps the previous
  selected image and leaves logs for diagnosis.
- Port already used: change `.env` ports; run `up`. PostgreSQL has no host port.
- HTTPS rejects a client: check the CA, client certificate, hostname and role.
  Synthetic identities generated by the unchanged D4 helper expire after **48 h**.
  This first cut has no certificate rotation: explicitly reset that instance after
  expiry. Persistence is validated across sessions inside that window, not indefinite
  operation. Calendars/estimates are also bounded synthetic fixtures.
- A healthy worker says RECOVERY_REQUIRED: this is a recovery guard, not readiness
  failure. Use the explicit terminal retirement only when eligible, inspect the
  approved recovery design, or explicitly reset your synthetic experiment.
- Interrupted bootstrap or mismatched database/journals: preserve logs and use
  selective reset. Never copy a real cluster into these directories.

## Separate tests and design / Pruebas y diseño separados

| Entry | Purpose / Propósito |
|---|---|
| `python3 dev/dev.py smoke` | Development session check; own new evidence |
| [D2 runner](../testing/D2/README.md) | Disposable SQL audit with historical targets |
| [D3 runners](../testing/D3/README.md) | Planning core and PostgreSQL library tests |
| [D4 laboratory](../testing/D4/README.md) | Scenario-based validation, separate Compose and cleanup |

El entorno reutiliza los componentes Java, la generación sintética de identidades
y utilidades host de D4. Mantiene su propio Compose, build, datos y scripts;
no ejecuta la matriz ni modifica las entradas selladas del laboratorio. Los cambios
de integración se validan con resultados nuevos; no se atribuyen las 638 pruebas
o 1.085 comprobaciones históricas a esta entrega.

Continue with the [documentation index](README.md), [D1 architecture](design/D1-architecture-baseline.md),
[D2 approved domain](design/D2.9-approved.md), [D3 approved core](design/D3-approved.md),
[D4 integrated verifier/presence design](design/D4-I12-INTEGRATED-VERIFIERS-PRESENCE.md)
and [closure manifest](validation/D4-CLOSURE.json). Future architecture includes
source adapters and an administration UI; those components are not started here.

## Repository and architectural context / Contexto técnico

| Area | Role / Función |
|---|---|
| `scheduler-core/` | Deterministic Java 21 planning library; immutable synthetic snapshots |
| `scheduler-postgres/` | JDBC capture, guarded publication/dispatch and callable coordination |
| `worker-control-plane/`, `worker-runtime/` | HTTPS/mTLS transport, supervision and durable effect components |
| `testing/D4/lab/` | Existing Java integration components reused by development |
| `dev/`, `compose.dev.yaml` | Local development entry point; independent lifecycle |
| `migrations/` | Preserved V1–V4 |
| `migrations-proposed/` | V5–V11 proposals; historical D2 targets retained |
| `migrations-d3*-proposed/` | Separate V12–V15 proposal locations for D3 |
| `migrations-d4-proposed/` | V16–V30 proposals used explicitly by synthetic bootstrap |
| `docs/design/`, `docs/validation/` | Approved contracts, historical decisions and portable evidence |

The proposed product architecture is a Java 21+/Spring Boot modular control plane
with PostgreSQL/Flyway, HTTPS polling workers, deterministic versioned integration
adapters and a future Angular administration UI. Gentle-AI Markdown plans and
business/technical documents are intended inputs; real parsers and Google Drive /
Plane adapters remain future work. Kafka, Temporal and Kubernetes are not required
for the proposed MVP. Worktrees provide change isolation, not security sandboxing.
The local fixture does not implement that entire proposed product.

| Stage | Recorded state / Estado registrado |
|---|---|
| D1 | Functional architecture approved / Arquitectura aprobada |
| D2 | Domain and SQL contracts approved and closed / Dominio y SQL cerrados |
| D3 | Conservative capacity scheduler MVP 1.0 approved and closed |
| D4 | Synthetic worker/recovery scope approved and closed |
| D5 | Source ingestion and integrations planned / Pendientes |
| D6 | Governance and operations planned / Pendientes |

D2's recorded 157 checks (including 29,829 SemVer vectors inside one JUnit check)
and D4's recorded 638 distinct tests / 1,085 Compose assertions retain their own
original versions and dates in the validation index. Some older audits intentionally
characterize gaps in historical schemas. None of those totals is a new run of this
development environment, a production guarantee or permission to promote proposals.
