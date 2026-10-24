# D5 I52 — revocation inside local Remote.execute

Approved I51 RV01–RV20, T/R × CREATE/UPDATE. Run from repository root:
`python3 -B -m testing.durable_inflight_revocation.run_inflight_revocation_lab`.
JSON stdout is this campaign's raw; regressions are separate runs.

New workers use Client.dispatch and the existing remote Store hook. READY is armed
only inside the real Remote.execute, at before_object or after_head, with exact
run/store/manifest/send/ticket and EXECUTE cid/request identity. While its REMOTE
lock is held, another process commits CLIENT REVIEW REVOKE v2. Parent reads only
independent files until it releases the sender: no public remote snapshot or
summary under that lock. Receipt/hash and reachable review prove revocation before
RELEASE_ACK; the returned proof is not delivered to CLIENT before the release.

Lost-response rows raise OSError after the real execute returns a durable proof.
Dispatch RESULT(None) leaves UNKNOWN/2 without pending send; explicit new reconcile
uses lookup only and preserves REMOTE, confirming EFFECT_CONFIRMED/3 + STALE.
Successful response rows confirm EFFECT_CONFIRMED/2 + STALE. No rollback, re-review,
resend or regained execution authority. Replayed revocation receipts remain history.
Before-ISSUE controls preserve baseline sends/effects, including prior UPDATE setup.

Independent readers and public passive readers run in owned spawn children.
Protocol identity/EOF/normal-exit/reduced-timeout controls and ownership restoration
are distinct from successful inflight cases. Two timeout-control kills are not
positive recovery frontiers. Budgets: four live children,20s wait,120s case,900s
campaign,256 events/case,16KiB/event,8MiB raw. Optimization is rejected. Discovery
hashes inputs before/after; only owned roots are cleaned, with sibling sentinels.

No product/API/model or previous harness changes, real providers/credentials,
private corpus, consumption/reservations, activation, promotion, deployment or D6.
D1–D4/A52 preserved; D5/G01–G07 and global GI review remain open. This campaign does
not address SOURCE/BATCH/EVALUATION revocation, profile/account/origin races, all
relational variants or all crash boundaries; no recovery inferred from isolated PASS.
