# D5 I63 — matriz de intercalados GX01–GX90

Fecha: **2026-10-25**. **NOT_RUN / NOT_REVIEWED**. [Contrato](D5-I63-GI39-INTERLEAVINGS-DESIGN.md) · [Catálogo y oráculo completo por caso](../validation/D5-I63-design-review.json).

22 mutaciones, 86 casos de dominio y cuatro controles. La matriz selecciona órdenes/modos concretos, sin completar combinaciones no ensayadas. Cero ejecución en I63.

| Mutación | Path / objetivo | Comandos y efecto durable | Error con HEAD fresca: APPLY / ISSUE |
|---|---|---|---|
| S01 IMPORT_NEW_CAPTURE | T / UI26.2 | IMPORT de segunda captura I26 B ya confirmada y distinta de A; selecciona nuevo source_id y sube selection_generation. | STALE_SOURCE / STALE_SOURCE |
| S02 SOURCE_REVIEW_ABA | T / UI26.2 | SOURCE A ACCEPT v1 → REVOKE v2 → ACCEPT v3; decisión vuelve a ACCEPT, versión no vuelve a1. | REVIEW_REQUIRED / REVIEW_REQUIRED |
| S03 EVALUATION_REVOKE | T / UI26.2 | EVALUATION del paquete ACCEPT v1 → REVOKE v2. | REVIEW_REQUIRED / REVIEW_REQUIRED |
| S04 EFFECT_REVOKE | T / UI26.2 | EFFECT del paquete ACCEPT v1 → REVOKE v2. | REVIEW_REQUIRED / STALE_REVIEW |
| S05 SOURCE_SELECTION_ABA | R / UI26.2 | Precapturar SOURCE B; seleccionar A→B→A. source_generation+2 aunque el source_id final sea A. | STALE_SOURCE / STALE_SOURCE |
| S06 SOURCE_REVIEW_REVOKE | R / UI26.2 | SOURCE manifest del BATCH ACCEPT v1 → REVOKE v2. | REVIEW_REQUIRED / REVIEW_REQUIRED |
| S07 BATCH_REVIEW_REVOKE | R / UI26.2 | BATCH manifest ACCEPT v1 → REVOKE v2; no sustituir por PROJECTION REVOKE de RV20. | REVIEW_REQUIRED / REVIEW_REQUIRED |
| C01 PROFILE_ABA | T / UI27.2 | Perfil A→None→A; profile_generation+2 y source conserva pin de generación anterior. | STALE_PROFILE / STALE_PROFILE |
| C02 POLICY_ABA | T / UI27.2 | Política A required_horizon5 → B4 → A5, demás campos idénticos; policy_generation+2. | STALE_EVALUATION / STALE_EVALUATION |
| C03 OBSERVATION_SELECTION_ABA | T / UI27.2 | Observación B válida y distinta ya registrada antes de preparar EVALUATION; seleccionar A→B→A en el mismo slot. account_generation+2, selected final A. | STALE_EVALUATION / STALE_EVALUATION |
| C04 OBSERVATION_REVOKE | T / UI27.2 | Revocar observación seleccionada A por generation exacta; account_generation+1, revoked=True. | STALE_EVALUATION / STALE_EVALUATION |
| C05 ADAPTER_ABA | T / UI27.2 | Adapter A→B con release sintético distinto→A; binding inmutable, account_generation+2 y descriptor final A. | STALE_EVALUATION / STALE_EVALUATION |
| R01 TASK_TITLE | R / UI34.3 | Cambiar título de la TASK proyectada, row_version+1. data_generation+1, data_hash cambia; selección/PROJECTION previas no se renuevan. | STALE_SELECTION / STALE_SELECTION |
| R02 EPIC_TITLE | R / UI34.3 | Cambiar título del EPIC original, sin editar payload TASK. data_generation+1, data_hash cambia; selección/PROJECTION previas no se renuevan. | STALE_SELECTION / STALE_SELECTION |
| R03 REQUIREMENT_HAS_WORK | R / UI34.3 | Marcar has_work=True en REQUIREMENT de fixture; no activar trabajo ni ejecutar grooming real. data_generation+1, data_hash cambia; selección/PROJECTION previas no se renuevan. | STALE_SELECTION / STALE_SELECTION |
| R04 TASK_EPIC_FIELD | R / UI34.3 | Cambiar epic_id de TASK hacia EP2 existente; no reescribir relaciones automáticamente. data_generation+1, data_hash cambia; selección/PROJECTION previas no se renuevan. | STALE_SELECTION / STALE_SELECTION |
| R05 ADD_EPIC_REQUIREMENT | R / UI34.3 | Añadir EP original→REQ2; membresía nueva respecto al baseline. data_generation+1, data_hash cambia; selección/PROJECTION previas no se renuevan. | STALE_SELECTION / STALE_SELECTION |
| R06 ADD_TASK_EPIC | R / UI34.3 | Añadir TASK0→EP2; membresía nueva respecto al baseline. data_generation+1, data_hash cambia; selección/PROJECTION previas no se renuevan. | STALE_SELECTION / STALE_SELECTION |
| R07 ADD_DEPENDENCY_HARD | R / UI34.3 | Añadir TASK0→TASK2, kind HARD, sin arista previa o ciclo. data_generation+1, data_hash cambia; selección/PROJECTION previas no se renuevan. | STALE_SELECTION / STALE_SELECTION |
| R08 ADD_DEPENDENCY_SOFT | R / UI34.3 | Añadir TASK0→TASK2, kind SOFT, sin arista previa o ciclo. data_generation+1, data_hash cambia; selección/PROJECTION previas no se renuevan. | STALE_SELECTION / STALE_SELECTION |
| R09 ADD_DEPENDENCY_MOCKABLE | R / UI34.3 | Añadir TASK0→TASK2, kind MOCKABLE, sin arista previa o ciclo. data_generation+1, data_hash cambia; selección/PROJECTION previas no se renuevan. | STALE_SELECTION / STALE_SELECTION |
| R10 ADD_DEPENDENCY_OPTIONAL | R / UI34.3 | Añadir TASK0→TASK2, kind OPTIONAL, sin arista previa o ciclo. data_generation+1, data_hash cambia; selección/PROJECTION previas no se renuevan. | STALE_SELECTION / STALE_SELECTION |

| GX | Mutación | Path / parte | Familia / orden | Modo | Punto primario | Respuesta perdida |
|---|---|---|---|---|---|---|
| GX01 | S01 | T / UI26.2 | LOCAL_APPLY / MUTATION_FIRST | LOCAL | before_lock | No |
| GX02 | S01 | T / UI26.2 | LOCAL_APPLY / COMMIT_FIRST | LOCAL | before_object | No |
| GX03 | S02 | T / UI26.2 | LOCAL_APPLY / MUTATION_FIRST | LOCAL | before_lock | No |
| GX04 | S02 | T / UI26.2 | LOCAL_APPLY / COMMIT_FIRST | LOCAL | before_object | No |
| GX05 | S03 | T / UI26.2 | LOCAL_APPLY / MUTATION_FIRST | LOCAL | before_lock | No |
| GX06 | S03 | T / UI26.2 | LOCAL_APPLY / COMMIT_FIRST | LOCAL | before_object | No |
| GX07 | S04 | T / UI26.2 | LOCAL_APPLY / MUTATION_FIRST | LOCAL | before_lock | No |
| GX08 | S04 | T / UI26.2 | LOCAL_APPLY / COMMIT_FIRST | LOCAL | before_object | No |
| GX09 | S05 | R / UI26.2 | LOCAL_APPLY / MUTATION_FIRST | LOCAL | before_lock | No |
| GX10 | S05 | R / UI26.2 | LOCAL_APPLY / COMMIT_FIRST | LOCAL | before_object | No |
| GX11 | S06 | R / UI26.2 | LOCAL_APPLY / MUTATION_FIRST | LOCAL | before_lock | No |
| GX12 | S06 | R / UI26.2 | LOCAL_APPLY / COMMIT_FIRST | LOCAL | before_object | No |
| GX13 | S07 | R / UI26.2 | LOCAL_APPLY / MUTATION_FIRST | LOCAL | before_lock | No |
| GX14 | S07 | R / UI26.2 | LOCAL_APPLY / COMMIT_FIRST | LOCAL | before_object | No |
| GX15 | S01 | T / UI26.2 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX16 | S01 | T / UI26.2 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX17 | S02 | T / UI26.2 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX18 | S02 | T / UI26.2 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX19 | S03 | T / UI26.2 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX20 | S03 | T / UI26.2 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX21 | S04 | T / UI26.2 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX22 | S04 | T / UI26.2 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX23 | S05 | R / UI26.2 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX24 | S05 | R / UI26.2 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX25 | S06 | R / UI26.2 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX26 | S06 | R / UI26.2 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX27 | S07 | R / UI26.2 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX28 | S07 | R / UI26.2 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX29 | S01 | T / UI26.2 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE | after_head | Sí |
| GX30 | S05 | R / UI26.2 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE | after_head | Sí |
| GX31 | C01 | T / UI27.2 | LOCAL_APPLY / MUTATION_FIRST | LOCAL | before_lock | No |
| GX32 | C01 | T / UI27.2 | LOCAL_APPLY / COMMIT_FIRST | LOCAL | before_object | No |
| GX33 | C02 | T / UI27.2 | LOCAL_APPLY / MUTATION_FIRST | LOCAL | before_lock | No |
| GX34 | C02 | T / UI27.2 | LOCAL_APPLY / COMMIT_FIRST | LOCAL | before_object | No |
| GX35 | C03 | T / UI27.2 | LOCAL_APPLY / MUTATION_FIRST | LOCAL | before_lock | No |
| GX36 | C03 | T / UI27.2 | LOCAL_APPLY / COMMIT_FIRST | LOCAL | before_object | No |
| GX37 | C04 | T / UI27.2 | LOCAL_APPLY / MUTATION_FIRST | LOCAL | before_lock | No |
| GX38 | C04 | T / UI27.2 | LOCAL_APPLY / COMMIT_FIRST | LOCAL | before_object | No |
| GX39 | C05 | T / UI27.2 | LOCAL_APPLY / MUTATION_FIRST | LOCAL | before_lock | No |
| GX40 | C05 | T / UI27.2 | LOCAL_APPLY / COMMIT_FIRST | LOCAL | before_object | No |
| GX41 | C01 | T / UI27.2 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX42 | C01 | T / UI27.2 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX43 | C02 | T / UI27.2 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX44 | C02 | T / UI27.2 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX45 | C03 | T / UI27.2 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX46 | C03 | T / UI27.2 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX47 | C04 | T / UI27.2 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX48 | C04 | T / UI27.2 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX49 | C05 | T / UI27.2 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX50 | C05 | T / UI27.2 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX51 | C01 | T / UI27.2 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE | after_head | Sí |
| GX52 | C02 | T / UI27.2 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE | after_head | Sí |
| GX53 | C03 | T / UI27.2 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE | after_head | Sí |
| GX54 | R01 | R / UI34.3 | BEFORE_ISSUE / MUTATION_FIRST | CREATE | before_lock | No |
| GX55 | R02 | R / UI34.3 | BEFORE_ISSUE / MUTATION_FIRST | CREATE | before_lock | No |
| GX56 | R03 | R / UI34.3 | BEFORE_ISSUE / MUTATION_FIRST | CREATE | before_lock | No |
| GX57 | R04 | R / UI34.3 | BEFORE_ISSUE / MUTATION_FIRST | CREATE | before_lock | No |
| GX58 | R05 | R / UI34.3 | BEFORE_ISSUE / MUTATION_FIRST | CREATE | before_lock | No |
| GX59 | R06 | R / UI34.3 | BEFORE_ISSUE / MUTATION_FIRST | CREATE | before_lock | No |
| GX60 | R07 | R / UI34.3 | BEFORE_ISSUE / MUTATION_FIRST | CREATE | before_lock | No |
| GX61 | R08 | R / UI34.3 | BEFORE_ISSUE / MUTATION_FIRST | CREATE | before_lock | No |
| GX62 | R09 | R / UI34.3 | BEFORE_ISSUE / MUTATION_FIRST | CREATE | before_lock | No |
| GX63 | R10 | R / UI34.3 | BEFORE_ISSUE / MUTATION_FIRST | CREATE | before_lock | No |
| GX64 | R01 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX65 | R01 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX66 | R02 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX67 | R02 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX68 | R03 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX69 | R03 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX70 | R04 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX71 | R04 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX72 | R05 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX73 | R05 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX74 | R06 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX75 | R06 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX76 | R07 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX77 | R07 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX78 | R08 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX79 | R08 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX80 | R09 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX81 | R09 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX82 | R10 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | CREATE | before_object | No |
| GX83 | R10 | R / UI34.3 | INFLIGHT / MUTATION_DURING_EXECUTE | UPDATE | after_head | No |
| GX84 | R03 | R / UI34.3 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE | after_head | Sí |
| GX85 | R06 | R / UI34.3 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE | after_head | Sí |
| GX86 | R07 | R / UI34.3 | INFLIGHT_LOST_RESPONSE / MUTATION_DURING_EXECUTE | CREATE | after_head | Sí |

| GX | Path | Control |
|---|---|---|
| GX87 | T | PROTOCOL_OWNERSHIP |
| GX88 | R | PROTOCOL_OWNERSHIP |
| GX89 | T | INVENTORY_RAW |
| GX90 | R | INVENTORY_RAW |

Conteos: 24 LOCAL_APPLY, 10 BEFORE_ISSUE, 44 INFLIGHT, 8 INFLIGHT_LOST_RESPONSE y cuatro controles. Por obligación: UI26.2=30, UI27.2=23, UI34.3=33. Cero SIGKILL positivos nuevos.

MUTATION_FIRST requiere distinguir CONFLICT_HEAD del rechazo semántico con HEAD fresca. COMMIT_FIRST conserva efecto histórico antes del cambio. INFLIGHT reconoce el ticket ya emitido y exige STALE, sin rollback; pérdida de respuesta sólo se recupera mediante consulta explícita. Los oráculos por caso están en el JSON.

No seleccionados: producto cartesiano completo de puntos/modos/mutaciones; CORE nativo; OSError/fsync y crash adicionales; campos/ediciones relacionales no nombrados. R no posee la autoridad de elegibilidad T; no se falsifican sus campos. Nueve regresiones futuras separadas, todas NOT_RUN; no aportan tests nuevos GX.
