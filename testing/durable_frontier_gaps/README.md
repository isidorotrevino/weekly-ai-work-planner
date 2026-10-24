# D5 I58 — finite frontier gap laboratory

Approved I57, FN01–FN64. Run from repository root:
`python3 -B -m testing.durable_frontier_gaps.run_frontier_gaps_lab`.
Stdout is this campaign's raw. Seven regressions retain separate raw/context files.

60 domain methods each use a new T/R v1 root and one SIGKILL at before_object,
after_object,before_replace or after_head. Four methods are protocol/ownership and
inventory/raw controls; negative timeout kills do not count as positive recovery.
The matrix identifies the exact 15 initial-publication or QUERY-result states.
T setup stops before the target instead of using a fully ready existing manifest;
R selection starts with selection=None and references its actual batch receipt.

RESULT_QUERY uses an issued CREATE ticket and one remote effect. A public QUERY
is durable before the child starts. The spawned child gets identity/ledger/qid and
fixed cid/expected, reads its own client state, performs real Remote.lookup and
constructs RESULT locally. The parent sends no proof. READY includes actual command
and proof hashes; its exact operation/stage/mode/stores/attempt are checked before
SIGKILL. No product, fixture, schema, kernel or hook changes are required.

Independent file readers and fresh passive public readers run before explicit
continuation. Uncommitted first publications are explicitly replayed once; committed
ones return historical receipts. A newer CLOCK is preserved by historical replay.
Uncommitted QUERY-result uses a new explicit reconcile without execute/close;
committed QUERY-result keeps one receipt and empty pending entries. Remote state,
entity/version/payload/foreign and ticket proof remain unchanged during reads.

64 tests do not accept all 140 inventory cells. Historical metadata, missing mode
labels, OSError scopes and other native CORE boundaries retain their limits. The
four native F7 cases NA29–NA32 remain separate; native NA36 is only a regression.
No inference of integrated recovery from summing unrelated PASS results.

Input discovery records source/helper/fixture/design/evidence hashes pre/post and
Python/build/platform/optimization/debug/command. Optimization, stale or extra
inputs, missing/duplicate IDs, skips, malformed JSON/hash/budgets and resources left
alive fail. Budgets: four live children,20s wait,120s case,900s own campaign,
256 events/case,16KiB/event,12MiB raw. Existing kernel/T/R limits are unchanged.
Negative inode/marker/sentinel/symlink changes are restored before owned cleanup;
no inspection or cleanup of operational dev/run_data/D4.

UI22.2 remains PARTIAL and the I56 77/7 assessment is preserved. D1–D4/A52 stay
closed/accepted; D5 global/G01–G07 and five GI remain open. No real providers,
credentials, private corpus, consumption/reservations, activation, promotion,
deployment, publication, SQL/Java/Docker/auditor execution or D6.
