# D5 I65 — suficiencia finita GI39

Fecha: **2026-10-26**. [Dictamen](D5-I65-results.md) · [Punteros completos y fuentes](D5-I65-results.json).

86 secuencias de dominio revisadas; cuatro controles separados. B=SUPPORTS_BOUNDED sólo para la fila seleccionada I63 T/R v1; todas global_accepted=false. Sin nuevas ejecuciones.

| Caso | Parte / mutación | Familia / orden | Modo / punto | Dictamen causal |
|---|---|---|---|---|
| GX01 | UI26.2 / S01 | LOCAL_APPLY / MUTATION_FIRST | LOCAL / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_SOURCE sin efecto/recibo. |
| GX02 | UI26.2 / S01 | LOCAL_APPLY / COMMIT_FIRST | LOCAL / before_object | B: APPLY gana y conserva recibo histórico; contender E vieja → CONFLICT_HEAD; nueva mutación confirma; preparación vieja → STALE_SOURCE sin nuevo send. |
| GX03 | UI26.2 / S02 | LOCAL_APPLY / MUTATION_FIRST | LOCAL / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → REVIEW_REQUIRED sin efecto/recibo. |
| GX04 | UI26.2 / S02 | LOCAL_APPLY / COMMIT_FIRST | LOCAL / before_object | B: APPLY gana y conserva recibo histórico; contender E vieja → CONFLICT_HEAD; nueva mutación confirma; preparación vieja → REVIEW_REQUIRED sin nuevo send. |
| GX05 | UI26.2 / S03 | LOCAL_APPLY / MUTATION_FIRST | LOCAL / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → REVIEW_REQUIRED sin efecto/recibo. |
| GX06 | UI26.2 / S03 | LOCAL_APPLY / COMMIT_FIRST | LOCAL / before_object | B: APPLY gana y conserva recibo histórico; contender E vieja → CONFLICT_HEAD; nueva mutación confirma; preparación vieja → REVIEW_REQUIRED sin nuevo send. |
| GX07 | UI26.2 / S04 | LOCAL_APPLY / MUTATION_FIRST | LOCAL / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → REVIEW_REQUIRED sin efecto/recibo. |
| GX08 | UI26.2 / S04 | LOCAL_APPLY / COMMIT_FIRST | LOCAL / before_object | B: APPLY gana y conserva recibo histórico; contender E vieja → CONFLICT_HEAD; nueva mutación confirma; preparación vieja → REVIEW_REQUIRED sin nuevo send. |
| GX09 | UI26.2 / S05 | LOCAL_APPLY / MUTATION_FIRST | LOCAL / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_SOURCE sin efecto/recibo. |
| GX10 | UI26.2 / S05 | LOCAL_APPLY / COMMIT_FIRST | LOCAL / before_object | B: APPLY gana y conserva recibo histórico; contender E vieja → CONFLICT_HEAD; nueva mutación confirma; preparación vieja → STALE_SOURCE sin nuevo send. |
| GX11 | UI26.2 / S06 | LOCAL_APPLY / MUTATION_FIRST | LOCAL / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → REVIEW_REQUIRED sin efecto/recibo. |
| GX12 | UI26.2 / S06 | LOCAL_APPLY / COMMIT_FIRST | LOCAL / before_object | B: APPLY gana y conserva recibo histórico; contender E vieja → CONFLICT_HEAD; nueva mutación confirma; preparación vieja → REVIEW_REQUIRED sin nuevo send. |
| GX13 | UI26.2 / S07 | LOCAL_APPLY / MUTATION_FIRST | LOCAL / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → REVIEW_REQUIRED sin efecto/recibo. |
| GX14 | UI26.2 / S07 | LOCAL_APPLY / COMMIT_FIRST | LOCAL / before_object | B: APPLY gana y conserva recibo histórico; contender E vieja → CONFLICT_HEAD; nueva mutación confirma; preparación vieja → REVIEW_REQUIRED sin nuevo send. |
| GX15 | UI26.2 / S01 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX16 | UI26.2 / S01 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX17 | UI26.2 / S02 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX18 | UI26.2 / S02 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX19 | UI26.2 / S03 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX20 | UI26.2 / S03 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX21 | UI26.2 / S04 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX22 | UI26.2 / S04 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX23 | UI26.2 / S05 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX24 | UI26.2 / S05 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX25 | UI26.2 / S06 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX26 | UI26.2 / S06 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX27 | UI26.2 / S07 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX28 | UI26.2 / S07 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX29 | UI26.2 / S01 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; UNKNOWN/2/0 hasta reconcile explícita lookup1/execute0 → EFFECT_CONFIRMED/3/1 STALE. |
| GX30 | UI26.2 / S05 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; UNKNOWN/2/0 hasta reconcile explícita lookup1/execute0 → EFFECT_CONFIRMED/3/1 STALE. |
| GX31 | UI27.2 / C01 | LOCAL_APPLY / MUTATION_FIRST | LOCAL / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_PROFILE sin efecto/recibo. |
| GX32 | UI27.2 / C01 | LOCAL_APPLY / COMMIT_FIRST | LOCAL / before_object | B: APPLY gana y conserva recibo histórico; contender E vieja → CONFLICT_HEAD; nueva mutación confirma; preparación vieja → STALE_PROFILE sin nuevo send. |
| GX33 | UI27.2 / C02 | LOCAL_APPLY / MUTATION_FIRST | LOCAL / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_EVALUATION sin efecto/recibo. |
| GX34 | UI27.2 / C02 | LOCAL_APPLY / COMMIT_FIRST | LOCAL / before_object | B: APPLY gana y conserva recibo histórico; contender E vieja → CONFLICT_HEAD; nueva mutación confirma; preparación vieja → STALE_EVALUATION sin nuevo send. |
| GX35 | UI27.2 / C03 | LOCAL_APPLY / MUTATION_FIRST | LOCAL / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_EVALUATION sin efecto/recibo. |
| GX36 | UI27.2 / C03 | LOCAL_APPLY / COMMIT_FIRST | LOCAL / before_object | B: APPLY gana y conserva recibo histórico; contender E vieja → CONFLICT_HEAD; nueva mutación confirma; preparación vieja → STALE_EVALUATION sin nuevo send. |
| GX37 | UI27.2 / C04 | LOCAL_APPLY / MUTATION_FIRST | LOCAL / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_EVALUATION sin efecto/recibo. |
| GX38 | UI27.2 / C04 | LOCAL_APPLY / COMMIT_FIRST | LOCAL / before_object | B: APPLY gana y conserva recibo histórico; contender E vieja → CONFLICT_HEAD; nueva mutación confirma; preparación vieja → STALE_EVALUATION sin nuevo send. |
| GX39 | UI27.2 / C05 | LOCAL_APPLY / MUTATION_FIRST | LOCAL / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_EVALUATION sin efecto/recibo. |
| GX40 | UI27.2 / C05 | LOCAL_APPLY / COMMIT_FIRST | LOCAL / before_object | B: APPLY gana y conserva recibo histórico; contender E vieja → CONFLICT_HEAD; nueva mutación confirma; preparación vieja → STALE_EVALUATION sin nuevo send. |
| GX41 | UI27.2 / C01 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX42 | UI27.2 / C01 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX43 | UI27.2 / C02 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX44 | UI27.2 / C02 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX45 | UI27.2 / C03 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX46 | UI27.2 / C03 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX47 | UI27.2 / C04 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX48 | UI27.2 / C04 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX49 | UI27.2 / C05 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX50 | UI27.2 / C05 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX51 | UI27.2 / C01 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; UNKNOWN/2/0 hasta reconcile explícita lookup1/execute0 → EFFECT_CONFIRMED/3/1 STALE. |
| GX52 | UI27.2 / C02 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; UNKNOWN/2/0 hasta reconcile explícita lookup1/execute0 → EFFECT_CONFIRMED/3/1 STALE. |
| GX53 | UI27.2 / C03 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; UNKNOWN/2/0 hasta reconcile explícita lookup1/execute0 → EFFECT_CONFIRMED/3/1 STALE. |
| GX54 | UI34.3 / R01 | BEFORE_ISSUE / MUTATION_FIRST | CREATE / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_SELECTION sin efecto/recibo. |
| GX55 | UI34.3 / R02 | BEFORE_ISSUE / MUTATION_FIRST | CREATE / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_SELECTION sin efecto/recibo. |
| GX56 | UI34.3 / R03 | BEFORE_ISSUE / MUTATION_FIRST | CREATE / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_SELECTION sin efecto/recibo. |
| GX57 | UI34.3 / R04 | BEFORE_ISSUE / MUTATION_FIRST | CREATE / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_SELECTION sin efecto/recibo. |
| GX58 | UI34.3 / R05 | BEFORE_ISSUE / MUTATION_FIRST | CREATE / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_SELECTION sin efecto/recibo. |
| GX59 | UI34.3 / R06 | BEFORE_ISSUE / MUTATION_FIRST | CREATE / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_SELECTION sin efecto/recibo. |
| GX60 | UI34.3 / R07 | BEFORE_ISSUE / MUTATION_FIRST | CREATE / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_SELECTION sin efecto/recibo. |
| GX61 | UI34.3 / R08 | BEFORE_ISSUE / MUTATION_FIRST | CREATE / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_SELECTION sin efecto/recibo. |
| GX62 | UI34.3 / R09 | BEFORE_ISSUE / MUTATION_FIRST | CREATE / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_SELECTION sin efecto/recibo. |
| GX63 | UI34.3 / R10 | BEFORE_ISSUE / MUTATION_FIRST | CREATE / before_lock | B: Mutación confirma primero; E vieja → CONFLICT_HEAD sin recibo, luego nueva invocación explícita con E fresca → STALE_SELECTION sin efecto/recibo. |
| GX64 | UI34.3 / R01 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX65 | UI34.3 / R01 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX66 | UI34.3 / R02 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX67 | UI34.3 / R02 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX68 | UI34.3 / R03 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX69 | UI34.3 / R03 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX70 | UI34.3 / R04 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX71 | UI34.3 / R04 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX72 | UI34.3 / R05 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX73 | UI34.3 / R05 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX74 | UI34.3 / R06 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX75 | UI34.3 / R06 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX76 | UI34.3 / R07 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX77 | UI34.3 / R07 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX78 | UI34.3 / R08 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX79 | UI34.3 / R08 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX80 | UI34.3 / R09 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX81 | UI34.3 / R09 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX82 | UI34.3 / R10 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE / before_object | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX83 | UI34.3 / R10 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; EFFECT_CONFIRMED/2/0 STALE. |
| GX84 | UI34.3 / R03 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; UNKNOWN/2/0 hasta reconcile explícita lookup1/execute0 → EFFECT_CONFIRMED/3/1 STALE. |
| GX85 | UI34.3 / R06 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; UNKNOWN/2/0 hasta reconcile explícita lookup1/execute0 → EFFECT_CONFIRMED/3/1 STALE. |
| GX86 | UI34.3 / R07 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE / after_head | B: Efecto histórico del ticket ya autorizado; RESULT conserva mutación y STALE, sin nuevo intento; UNKNOWN/2/0 hasta reconcile explícita lookup1/execute0 → EFFECT_CONFIRMED/3/1 STALE. |

| Control | Familia | Dictamen |
|---|---|---|
| GX87 | PROTOCOL_OWNERSHIP | CONTROL_ONLY; no dominio |
| GX88 | PROTOCOL_OWNERSHIP | CONTROL_ONLY; no dominio |
| GX89 | INVENTORY_RAW | CONTROL_ONLY; no dominio |
| GX90 | INVENTORY_RAW | CONTROL_ONLY; no dominio |

## Catálogo de mutaciones

| ID | Variante y autoridad | Secuencias I64 revisadas |
|---|---|---|
| S01 | T / IMPORT_NEW_CAPTURE | GX01, GX02, GX15, GX16, GX29 |
| S02 | T / SOURCE_REVIEW_ABA | GX03, GX04, GX17, GX18 |
| S03 | T / EVALUATION_REVOKE | GX05, GX06, GX19, GX20 |
| S04 | T / EFFECT_REVOKE | GX07, GX08, GX21, GX22 |
| S05 | R / SOURCE_SELECTION_ABA | GX09, GX10, GX23, GX24, GX30 |
| S06 | R / SOURCE_REVIEW_REVOKE | GX11, GX12, GX25, GX26 |
| S07 | R / BATCH_REVIEW_REVOKE | GX13, GX14, GX27, GX28 |
| C01 | T / PROFILE_ABA | GX31, GX32, GX41, GX42, GX51 |
| C02 | T / POLICY_ABA | GX33, GX34, GX43, GX44, GX52 |
| C03 | T / OBSERVATION_SELECTION_ABA | GX35, GX36, GX45, GX46, GX53 |
| C04 | T / OBSERVATION_REVOKE | GX37, GX38, GX47, GX48 |
| C05 | T / ADAPTER_ABA | GX39, GX40, GX49, GX50 |
| R01 | R / TASK_TITLE | GX54, GX64, GX65 |
| R02 | R / EPIC_TITLE | GX55, GX66, GX67 |
| R03 | R / REQUIREMENT_HAS_WORK | GX56, GX68, GX69, GX84 |
| R04 | R / TASK_EPIC_FIELD | GX57, GX70, GX71 |
| R05 | R / ADD_EPIC_REQUIREMENT | GX58, GX72, GX73 |
| R06 | R / ADD_TASK_EPIC | GX59, GX74, GX75, GX85 |
| R07 | R / ADD_DEPENDENCY_HARD | GX60, GX76, GX77, GX86 |
| R08 | R / ADD_DEPENDENCY_SOFT | GX61, GX78, GX79 |
| R09 | R / ADD_DEPENDENCY_MOCKABLE | GX62, GX80, GX81 |
| R10 | R / ADD_DEPENDENCY_OPTIONAL | GX63, GX82, GX83 |

No es el producto cartesiano de todos los campos, órdenes, modos, puntos, mutaciones simultáneas o fases CORE nativas. Las 81 partes no dirigidas conservan I62. Pendientes parciales: UI01.2/UI04.1/UI09.2; criterios globales abiertos.
