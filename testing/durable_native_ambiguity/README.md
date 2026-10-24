# D5 I55 — native durable ambiguity laboratory

Approved I54 contract and NA01–NA36, implemented with new schemas and owned roots.
Run from the repository root:
`python3 -B -m testing.durable_native_ambiguity.run_native_ambiguity_lab`.
Stdout JSON is this campaign's raw; six regressions have independent raw/context.

The new fixture composes T/R pure reducers inside one outer Store. Core receipts
are materialized from the outer chain for reducer and facade reads, never persisted
as another authority. Core operations are named CORE(kind,args); native OBSERVE is
distinct from the older T eligibility observation. Capture I26 is retained for T;
R still requires the exact applied batch receipt and selected TASK.

DECLARE_VIEW publishes a synthetic external catalog, separate from emitted CREATE
effects, ticket proofs, unique keys and entities. query returns a valid collection
and independent ticket proof from one snapshot. A collection is never selected,
deduplicated or adopted. Multiple matches and incompatible identity remain sticky
CONFLICT even after a later exact proof. Catalog imports are not authorized sends.

Native synthetic responses expose status 200/429 and logical retry metadata.
AMBIGUOUS_429_BEFORE records transport without core effect; AFTER atomically stores
the real effect/proof and hides it from the returned response. Both leave UNKNOWN;
only explicit query can confirm the same ticket. No actual HTTP or provider is used.
A correlated NO_EFFECT RATE_LIMIT proof is a separate retry control. Status/tick
alone never permits resend. Response replay returns the original commit reference.

NA29–NA32 kill spawned processes at before_observe or OBSERVE Store after_head;
READY, request identity, reachable chain, receipts, pending and fresh passive reads
are checked in each same-ticket sequence. These four cases do not cover all F1–F7.
Protocol timeouts are negative controls, not positive crash/recovery evidence.

36 tests include four controls; repeated-ID, foreign-scope, metadata and donor
subscenarios do not add tests. Raw labels retain their separate roles. Budgets:
four live children,20s wait,120s case,900s campaign,256 events/case,64KiB envelope
and event,12MiB raw,eight matches,64 catalog keys. Store limits remain unchanged.
Input discovery records effective source/helper/fixture/design hashes before/after;
invalid maps/skips/JSON/hash/budgets/residues fail. Cleanup checks ownership and
restores negative inode/marker/sentinel/symlink cases before closing owned roots.

The Python321 regression can use the unchanged JSON-instrumented
`testing.D5.run_relational_durable_lab` runner: it performs the same testing/D5
unittest discovery named in I54 and additionally reports its resource inventories.
HC24/HF40/IC30/UQ24/RV20 retain their original commands and separate reports.

MG01/MG02 implementation awaits semantic review; MG03 selection/adoption is absent.
UI20.3/H07 and D5/G01–G07 stay partial/open. D1–D4 and A52 remain unchanged. No
real provider/credentials/private corpus, consumption/reservations, activation,
promotion, deployment, publication or D6. No operational dev/run_data/D4 inspection.
