# D5 I50 — durable uncertainty laboratory

Implements the approved I49 contract and UQ01–UQ24 using existing T/R public APIs.
Run from the repository root with `python3 -B -m testing.durable_uncertainty.run_uncertainty_lab`.
JSON stdout is its own raw campaign; regressions are separate runs with their own context.

CREATE only, one reviewed TASK per setup. R TASK derives from the exact batch
receipt; T retains I26/SOURCE/EVALUATION/EFFECT authority. Instance-local wrappers
record calls before/after the real synthetic execute/lookup and are restored in
finally. No HTTP/provider/model changes. OSError represents missing proof, never
an actual HTTP429. Lists/envelopes are malformed-proof negatives, not native
multiple matches. MG01–MG03 remain NO_NATIVE_MODEL and are not tests.

Dispatch RESULT(None) may remove pending send while UNKNOWN remains blocking.
Query RESULT(None) removes query pending and preserves the original send pending.
A sticky identity conflict does not adopt a later correct proof. Retry eligibility
requires correlated NO_EFFECT and an eligible logical tick; UNKNOWN stays blocked.
Only explicit retry/reconcile is invoked; real-call counters distinguish each.

Independent file readers and fresh public readers run in owned spawn processes.
Passive reopen compares state/HEAD and requires zero transport calls. No positive
SIGKILL or new concurrency claims. UQ17/UQ18 each have a second isolated UNKNOWN
clock contrast; 26 scenarios are still 24 tests. Resources are cleaned only under
owned roots; inode/marker/sentinel/link negatives are restored before close.

Limits: four live children, 20s wait, 120s case, 900s campaign, 256 events/case,
16KiB/event, 8MiB raw. Optimization is rejected. Input discovery records before/
after hashes, module sources, fixture bytes, helpers, relevant contracts/seals.
Reduced negative budgets are not full capacity or host/power-loss attestation.

UI20.3/H07 remain partial/open; D5 global and G01–G07 remain open. D1–D4 and the
accepted local I1–I20 milestone are preserved. No real providers/credentials,
consumption/reservations, activation, promotion, deployment, publication or D6.
