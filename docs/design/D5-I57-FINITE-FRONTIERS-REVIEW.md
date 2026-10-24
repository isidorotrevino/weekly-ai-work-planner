# D5 I57 — matriz finita F1–F7 y corte FN64

Fecha: **2026-10-24**. **PREPARED_FOR_REVIEW**.
[Contrato](D5-I57-FINITE-FRONTIERS-DESIGN.md) · [Sello/fuentes/punteros por celda](../validation/D5-I57-design-review.json).

**Inventario: 35 salidas/variantes T/R × cuatro puntos = 140 celdas, no tests.**
E=EXISTING_BOUNDED_EVIDENCE (41); H=EXISTING_HISTORICAL_METADATA_ONLY (15); M=EXISTING_MODE_UNLABELLED (24); D=PARTIAL_EXISTING_DIFFERENT_STATE (40); P=PENDING_NO_MATCHING_CASE (20). Ninguna etiqueta equivale a UI22 completa o criterio aceptado. D/P selecciona el estado/rama concreto del futuro FN; M/H permanecen calificados. Cada celda E/H/M/D tiene referencia path/pointer/hash verificable en el JSON; P no inventa un caso.

## Inventario lógico/físico

| Celda | Target / F | Operación / stage / modo | before_object | after_object | before_replace | after_head | FN propuesto / motivo |
|---|---|---|---|---|---|---|---|
| FL01 | T / F1 | IMPORT / SOURCE / LOCAL | D | D | D | D | FN01–FN04; DF08–DF12 vuelven a importar desde ready; no primera fuente en CLIENT vacío. |
| FL02 | T / F2 | REVIEW_SOURCE_ACCEPT / SOURCE / LOCAL | D | D | D | D | FN05–FN08; DF08–DF12 usan REVOKE v1→v2; falta ACCEPT v0→v1. |
| FL03 | T / F2 | PREPARE_EVALUATION / EVALUATION / LOCAL | D | D | D | D | FN09–FN12; phase_args parte de evaluación ya preparada; falta publicación inicial. |
| FL04 | T / F2 | REVIEW_EVALUATION_ACCEPT / EVALUATION / LOCAL | D | D | D | D | FN13–FN16; Revisión histórica interrumpida es REVOKE; falta ACCEPT inicial. |
| FL05 | T / F2 | PREPARE_EFFECT / EFFECT / LOCAL | D | D | D | D | FN17–FN20; phase_args parte de TASK ya aplicada; falta primer plan previo a APPLY. |
| FL06 | T / F2 | REVIEW_EFFECT_ACCEPT / EFFECT / LOCAL | D | D | D | D | FN21–FN24; Revisión histórica interrumpida es REVOKE; falta ACCEPT inicial. |
| FL07 | T / F3 | APPLY / EFFECT / LOCAL | H | H | H | E | Sin ejecución nueva propuesta; Primer APPLY; raw stdout original I34 NOT_RECORDED, metadata publicada y fuente disponibles. |
| FL08 | T / F4 | BIND / PROJECTION / LOCAL | P | P | P | P | FN25–FN28; No kill específico BIND en la matriz de commits histórica. |
| FL09 | T / F4 | PREPARE_PROJECTION / PROJECTION / LOCAL | D | D | D | D | FN29–FN32; phase_args parte de proyección ya preparada; falta primera publicación. |
| FL10 | T / F4 | REVIEW_PROJECTION_ACCEPT / PROJECTION / LOCAL | D | D | D | D | FN33–FN36; Revisión histórica interrumpida es REVOKE; falta ACCEPT inicial. |
| FL11 | T / F5 | ISSUE / PROJECTION / CREATE | H | H | H | H | Sin ejecución nueva propuesta; Metadata T conservada; raw stdout I34 original no registrado, no se reconstruye. |
| FL12 | T / F6 | EXECUTE / PROJECTION / CREATE | M | M | M | M | Sin ejecución nueva propuesta; Metadata T agrupa tres modos sin campo mode; el bucle literal CREATE/UPDATE/CLOSE orienta, no hay modo observado por registro. |
| FL13 | T / F6 | EXECUTE / PROJECTION / UPDATE | M | M | M | M | Sin ejecución nueva propuesta; Metadata T agrupa tres modos sin campo mode; el bucle literal CREATE/UPDATE/CLOSE orienta, no hay modo observado por registro. |
| FL14 | T / F6 | CLOSE / PROJECTION / CLOSE | M | M | M | M | Sin ejecución nueva propuesta; Metadata T agrupa tres modos sin campo mode; el bucle literal CREATE/UPDATE/CLOSE orienta, no hay modo observado por registro. |
| FL15 | T / F7 | QUERY / PROJECTION / CREATE | H | H | H | H | Sin ejecución nueva propuesta; Metadata T conservada; raw stdout I34 original no registrado, no se reconstruye. |
| FL16 | T / F7 | RESULT_DISPATCH / PROJECTION / CREATE | H | H | H | H | Sin ejecución nueva propuesta; Metadata T conservada; raw stdout I34 original no registrado, no se reconstruye. |
| FL17 | T / F7 | RESULT_QUERY / PROJECTION / CREATE | P | P | P | P | FN37–FN40; phase_args RESULT usa query_id=None; before_result no es before_object del commit. |
| FL18 | R / F1 | CAPTURE / SOURCE / LOCAL | E | E | E | E | Sin ejecución nueva propuesta; Primera publicación R, raw propio con operación/stage/punto. |
| FL19 | R / F1 | SELECT_SOURCE / SOURCE / LOCAL | E | E | E | E | Sin ejecución nueva propuesta; Primera publicación R, raw propio con operación/stage/punto. |
| FL20 | R / F2 | PREPARE_SOURCE / SOURCE / LOCAL | E | E | E | E | Sin ejecución nueva propuesta; Primera publicación R, raw propio con operación/stage/punto. |
| FL21 | R / F2 | REVIEW_SOURCE_ACCEPT / SOURCE / LOCAL | E | E | E | E | Sin ejecución nueva propuesta; Primera publicación R, raw propio con operación/stage/punto. |
| FL22 | R / F2 | PREPARE_BATCH / BATCH / LOCAL | E | E | E | E | Sin ejecución nueva propuesta; Primera publicación R, raw propio con operación/stage/punto. |
| FL23 | R / F2 | REVIEW_BATCH_ACCEPT / BATCH / LOCAL | E | E | E | E | Sin ejecución nueva propuesta; Primera publicación R, raw propio con operación/stage/punto. |
| FL24 | R / F3 | APPLY_BATCH / BATCH / LOCAL | E | E | E | E | Sin ejecución nueva propuesta; Raw R de I55 ejecuta DR23; rol/operación/punto y HEAD exactos. Stage/modo se enlazan a fuente, no se inventan. |
| FL25 | R / F4 | SELECT_TASKS / PROJECTION / LOCAL | D | D | D | D | FN41–FN44; DR23 cambia una selección ya existente; falta selección inicial desde recibo BATCH. |
| FL26 | R / F4 | BIND / PROJECTION / LOCAL | P | P | P | P | FN45–FN48; No kill específico BIND en DR23. |
| FL27 | R / F4 | PREPARE_PROJECTION / PROJECTION / LOCAL | D | D | D | D | FN49–FN52; DR23 parte de PROJECTION ya preparada. |
| FL28 | R / F4 | REVIEW_PROJECTION_ACCEPT / PROJECTION / LOCAL | P | P | P | P | FN53–FN56; DR23 no incluye REVIEW PROJECTION; falta ACCEPT inicial. |
| FL29 | R / F5 | ISSUE / PROJECTION / CREATE | E | E | E | E | Sin ejecución nueva propuesta; Raw R de I55 ejecuta DR23; rol/operación/punto y HEAD exactos. Stage/modo se enlazan a fuente, no se inventan. |
| FL30 | R / F6 | EXECUTE / PROJECTION / CREATE | M | M | M | M | Sin ejecución nueva propuesta; Raw actual registra tres entradas por punto, sin mode; correspondencia por orden de bucle es inferida, no campo empírico. |
| FL31 | R / F6 | EXECUTE / PROJECTION / UPDATE | M | M | M | M | Sin ejecución nueva propuesta; Raw actual registra tres entradas por punto, sin mode; correspondencia por orden de bucle es inferida, no campo empírico. |
| FL32 | R / F6 | CLOSE / PROJECTION / CLOSE | M | M | M | M | Sin ejecución nueva propuesta; Raw actual registra tres entradas por punto, sin mode; correspondencia por orden de bucle es inferida, no campo empírico. |
| FL33 | R / F7 | QUERY / PROJECTION / CREATE | E | E | E | E | Sin ejecución nueva propuesta; Raw R de I55 ejecuta DR23; rol/operación/punto y HEAD exactos. Stage/modo se enlazan a fuente, no se inventan. |
| FL34 | R / F7 | RESULT_DISPATCH / PROJECTION / CREATE | E | E | E | E | Sin ejecución nueva propuesta; Raw R de I55 ejecuta DR23; rol/operación/punto y HEAD exactos. Stage/modo se enlazan a fuente, no se inventan. |
| FL35 | R / F7 | RESULT_QUERY / PROJECTION / CREATE | P | P | P | P | FN57–FN60; DR23 RESULT usa query_id=None; falta publicación con QUERY pendiente. |

## Estados iniciales del corte propuesto

| FL / target | Precondición de primera publicación o rama |
|---|---|
| FL01 / T | Perfil registrado/seleccionado y commit I26 real confirmado; CLIENT aún sin fuente importada. IMPORT verifica pin y bytes; no REVIEW implícita. |
| FL02 / T | Primera fuente importada; SOURCE sin revisión/v0. ACCEPT v0→v1, sin evaluación ni efecto. |
| FL03 / T | SOURCE ACCEPT v1; cuenta/política/observaciones sintéticas conocidas y elegibles; ninguna evaluación preparada. Preparación fija pins exactos, no acepta ni aplica. |
| FL04 / T | Evaluación nueva, sin revisión/v0; ACCEPT v0→v1, sin EFFECT. |
| FL05 / T | Evaluación ACCEPT v1; TASK target aún inexistente. Primer plan before=None, sin aplicar TASK/mapping/base/procedencia. |
| FL06 / T | Primer EFFECT nuevo, sin revisión/v0; ACCEPT v0→v1, aún sin APPLY. |
| FL08 / T | APPLY de una TASK confirmado; sin bindings, PROJECTION o sends. BIND registra la identidad exacta; no prepara ni envía. |
| FL09 / T | TASK aplicada y BIND confirmado; ninguna PROJECTION. Primer manifiesto fija payload/base/capabilities/identidad remota, sin revisión ni envío. |
| FL10 / T | Primera PROJECTION preparada, revisión ausente/v0; ACCEPT v0→v1. No ISSUE. |
| FL17 / T | ISSUE CREATE realmente emitido, EXECUTE remoto confirmado una vez, CLIENT UNKNOWN/ledger1; QUERY durable única, queries1, pending send+query_id; sin RESULT previo. |
| FL25 / R | APPLY_BATCH confirmado; selection=None, generación de selección0. Selección de una TASK participante por cid/request del recibo exacto; no BIND/PROJECTION. |
| FL26 / R | Primera selección TASK desde recibo BATCH confirmada; sin bindings. BIND de esa TASK exacta, sin PROJECTION ni send. |
| FL27 / R | TASK seleccionada y BIND confirmado; ninguna PROJECTION. Fija lote/recibo/selección/generaciones propios R; sin revisión ni envío. |
| FL28 / R | Primera PROJECTION R preparada, revisión ausente/v0. ACCEPT v0→v1 sin ISSUE. |
| FL35 / R | ISSUE CREATE realmente emitido de TASK seleccionada por recibo BATCH; EXECUTE confirmado una vez, UNKNOWN/ledger1; QUERY durable única, queries1, pending send+query_id; sin RESULT previo. |

## FN01–FN64 — todos NOT_RUN / NOT_REVIEWED

FN01–FN60: un método, una caída objetivo y una raíz por fila; FN61–FN64 son controles. Todos usan lector independiente + CLIENT público spawn pasivos. Los suboráculos y regresiones no incrementan el conteo.

| ID | FL / target / frontera | Operación / stage | Punto | Resultado exigido al reabrir |
|---|---|---|---|---|
| FN01 | FL01 / T / F1 | IMPORT / SOURCE | before_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN02 | FL01 / T / F1 | IMPORT / SOURCE | after_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN03 | FL01 / T / F1 | IMPORT / SOURCE | before_replace | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN04 | FL01 / T / F1 | IMPORT / SOURCE | after_head | Única salida o ACCEPT v1 + recibo exacto alcanzables; no fases posteriores implícitas; replay histórico sin duplicar. |
| FN05 | FL02 / T / F2 | REVIEW_SOURCE_ACCEPT / SOURCE | before_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN06 | FL02 / T / F2 | REVIEW_SOURCE_ACCEPT / SOURCE | after_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN07 | FL02 / T / F2 | REVIEW_SOURCE_ACCEPT / SOURCE | before_replace | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN08 | FL02 / T / F2 | REVIEW_SOURCE_ACCEPT / SOURCE | after_head | Única salida o ACCEPT v1 + recibo exacto alcanzables; no fases posteriores implícitas; replay histórico sin duplicar. |
| FN09 | FL03 / T / F2 | PREPARE_EVALUATION / EVALUATION | before_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN10 | FL03 / T / F2 | PREPARE_EVALUATION / EVALUATION | after_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN11 | FL03 / T / F2 | PREPARE_EVALUATION / EVALUATION | before_replace | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN12 | FL03 / T / F2 | PREPARE_EVALUATION / EVALUATION | after_head | Única salida o ACCEPT v1 + recibo exacto alcanzables; no fases posteriores implícitas; replay histórico sin duplicar. |
| FN13 | FL04 / T / F2 | REVIEW_EVALUATION_ACCEPT / EVALUATION | before_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN14 | FL04 / T / F2 | REVIEW_EVALUATION_ACCEPT / EVALUATION | after_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN15 | FL04 / T / F2 | REVIEW_EVALUATION_ACCEPT / EVALUATION | before_replace | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN16 | FL04 / T / F2 | REVIEW_EVALUATION_ACCEPT / EVALUATION | after_head | Única salida o ACCEPT v1 + recibo exacto alcanzables; no fases posteriores implícitas; replay histórico sin duplicar. |
| FN17 | FL05 / T / F2 | PREPARE_EFFECT / EFFECT | before_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN18 | FL05 / T / F2 | PREPARE_EFFECT / EFFECT | after_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN19 | FL05 / T / F2 | PREPARE_EFFECT / EFFECT | before_replace | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN20 | FL05 / T / F2 | PREPARE_EFFECT / EFFECT | after_head | Única salida o ACCEPT v1 + recibo exacto alcanzables; no fases posteriores implícitas; replay histórico sin duplicar. |
| FN21 | FL06 / T / F2 | REVIEW_EFFECT_ACCEPT / EFFECT | before_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN22 | FL06 / T / F2 | REVIEW_EFFECT_ACCEPT / EFFECT | after_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN23 | FL06 / T / F2 | REVIEW_EFFECT_ACCEPT / EFFECT | before_replace | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN24 | FL06 / T / F2 | REVIEW_EFFECT_ACCEPT / EFFECT | after_head | Única salida o ACCEPT v1 + recibo exacto alcanzables; no fases posteriores implícitas; replay histórico sin duplicar. |
| FN25 | FL08 / T / F4 | BIND / PROJECTION | before_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN26 | FL08 / T / F4 | BIND / PROJECTION | after_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN27 | FL08 / T / F4 | BIND / PROJECTION | before_replace | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN28 | FL08 / T / F4 | BIND / PROJECTION | after_head | Única salida o ACCEPT v1 + recibo exacto alcanzables; no fases posteriores implícitas; replay histórico sin duplicar. |
| FN29 | FL09 / T / F4 | PREPARE_PROJECTION / PROJECTION | before_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN30 | FL09 / T / F4 | PREPARE_PROJECTION / PROJECTION | after_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN31 | FL09 / T / F4 | PREPARE_PROJECTION / PROJECTION | before_replace | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN32 | FL09 / T / F4 | PREPARE_PROJECTION / PROJECTION | after_head | Única salida o ACCEPT v1 + recibo exacto alcanzables; no fases posteriores implícitas; replay histórico sin duplicar. |
| FN33 | FL10 / T / F4 | REVIEW_PROJECTION_ACCEPT / PROJECTION | before_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN34 | FL10 / T / F4 | REVIEW_PROJECTION_ACCEPT / PROJECTION | after_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN35 | FL10 / T / F4 | REVIEW_PROJECTION_ACCEPT / PROJECTION | before_replace | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN36 | FL10 / T / F4 | REVIEW_PROJECTION_ACCEPT / PROJECTION | after_head | Única salida o ACCEPT v1 + recibo exacto alcanzables; no fases posteriores implícitas; replay histórico sin duplicar. |
| FN37 | FL17 / T / F7 | RESULT_QUERY / PROJECTION | before_object | UNKNOWN/ledger1/queries1, send+qid pending, sin recibo RESULT; reconcile explícita posterior → /2/2, sin execute/close. |
| FN38 | FL17 / T / F7 | RESULT_QUERY / PROJECTION | after_object | UNKNOWN/ledger1/queries1, send+qid pending, sin recibo RESULT; reconcile explícita posterior → /2/2, sin execute/close. |
| FN39 | FL17 / T / F7 | RESULT_QUERY / PROJECTION | before_replace | UNKNOWN/ledger1/queries1, send+qid pending, sin recibo RESULT; reconcile explícita posterior → /2/2, sin execute/close. |
| FN40 | FL17 / T / F7 | RESULT_QUERY / PROJECTION | after_head | EFFECT_CONFIRMED/ledger2/queries1, recibo único, sin pending; replay exacto histórico, REMOTE intacto. |
| FN41 | FL25 / R / F4 | SELECT_TASKS / PROJECTION | before_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN42 | FL25 / R / F4 | SELECT_TASKS / PROJECTION | after_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN43 | FL25 / R / F4 | SELECT_TASKS / PROJECTION | before_replace | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN44 | FL25 / R / F4 | SELECT_TASKS / PROJECTION | after_head | Única salida o ACCEPT v1 + recibo exacto alcanzables; no fases posteriores implícitas; replay histórico sin duplicar. |
| FN45 | FL26 / R / F4 | BIND / PROJECTION | before_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN46 | FL26 / R / F4 | BIND / PROJECTION | after_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN47 | FL26 / R / F4 | BIND / PROJECTION | before_replace | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN48 | FL26 / R / F4 | BIND / PROJECTION | after_head | Única salida o ACCEPT v1 + recibo exacto alcanzables; no fases posteriores implícitas; replay histórico sin duplicar. |
| FN49 | FL27 / R / F4 | PREPARE_PROJECTION / PROJECTION | before_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN50 | FL27 / R / F4 | PREPARE_PROJECTION / PROJECTION | after_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN51 | FL27 / R / F4 | PREPARE_PROJECTION / PROJECTION | before_replace | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN52 | FL27 / R / F4 | PREPARE_PROJECTION / PROJECTION | after_head | Única salida o ACCEPT v1 + recibo exacto alcanzables; no fases posteriores implícitas; replay histórico sin duplicar. |
| FN53 | FL28 / R / F4 | REVIEW_PROJECTION_ACCEPT / PROJECTION | before_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN54 | FL28 / R / F4 | REVIEW_PROJECTION_ACCEPT / PROJECTION | after_object | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN55 | FL28 / R / F4 | REVIEW_PROJECTION_ACCEPT / PROJECTION | before_replace | HEAD/estado alcanzables previos, salida ausente/revisión0 y sin recibo cid; replay expreso confirma una vez. |
| FN56 | FL28 / R / F4 | REVIEW_PROJECTION_ACCEPT / PROJECTION | after_head | Única salida o ACCEPT v1 + recibo exacto alcanzables; no fases posteriores implícitas; replay histórico sin duplicar. |
| FN57 | FL35 / R / F7 | RESULT_QUERY / PROJECTION | before_object | UNKNOWN/ledger1/queries1, send+qid pending, sin recibo RESULT; reconcile explícita posterior → /2/2, sin execute/close. |
| FN58 | FL35 / R / F7 | RESULT_QUERY / PROJECTION | after_object | UNKNOWN/ledger1/queries1, send+qid pending, sin recibo RESULT; reconcile explícita posterior → /2/2, sin execute/close. |
| FN59 | FL35 / R / F7 | RESULT_QUERY / PROJECTION | before_replace | UNKNOWN/ledger1/queries1, send+qid pending, sin recibo RESULT; reconcile explícita posterior → /2/2, sin execute/close. |
| FN60 | FL35 / R / F7 | RESULT_QUERY / PROJECTION | after_head | EFFECT_CONFIRMED/ledger2/queries1, recibo único, sin pending; replay exacto histórico, REMOTE intacto. |
| FN61 | CONTROL / T / CONTROL | PROTOCOL_OWNERSHIP / NONE | CONTROL | Negativos de protocolo/ownership o inventario/raw/budgets; restaurar antes de limpieza propia, cero residuos. No caída positiva. |
| FN62 | CONTROL / R / CONTROL | PROTOCOL_OWNERSHIP / NONE | CONTROL | Negativos de protocolo/ownership o inventario/raw/budgets; restaurar antes de limpieza propia, cero residuos. No caída positiva. |
| FN63 | CONTROL / T / CONTROL | INVENTORY_RAW / NONE | CONTROL | Negativos de protocolo/ownership o inventario/raw/budgets; restaurar antes de limpieza propia, cero residuos. No caída positiva. |
| FN64 | CONTROL / R / CONTROL | INVENTORY_RAW / NONE | CONTROL | Negativos de protocolo/ownership o inventario/raw/budgets; restaurar antes de limpieza propia, cero residuos. No caída positiva. |

## Cortes de fachada existentes — no son todos puntos internos de Store

| Caso | Target / frontera | Punto | Límite |
|---|---|---|---|
| HF31 | T / F3→F4 | after_head | APPLY concreto antes de BIND, no fallo dentro de BIND |
| HF32 | R / F3→F4 | after_head | APPLY_BATCH antes de selección/BIND |
| HF33 | T / F6→F7 | after_remote | dispatch real desde UNKNOWN |
| HF34 | R / F6→F7 | after_remote | dispatch real desde UNKNOWN |
| HF35 | T / F7 | before_result | P observada, aún no se invocó RESULT |
| HF36 | R / F7 | before_result | P observada, aún no se invocó RESULT |
| HF37 | T / F7 | after_query | QUERY durable antes de lookup |
| HF38 | R / F7 | after_query | QUERY durable antes de lookup |
| NA29 | NATIVE_T / F7 | before_observe | Nuevo namespace; no transferencia a RESULT legacy ni a otras fases CORE. |
| NA30 | NATIVE_R / F7 | before_observe | Nuevo namespace; no transferencia a RESULT legacy ni a otras fases CORE. |
| NA31 | NATIVE_T / F7 | after_head | Nuevo namespace; no transferencia a RESULT legacy ni a otras fases CORE. |
| NA32 | NATIVE_R / F7 | after_head | Nuevo namespace; no transferencia a RESULT legacy ni a otras fases CORE. |

T DF16 y R DR25 acreditan además after_issue desde ticket durable antes de entrega; se conservan como fuente/metadata histórica, no como FN nuevos. OSError T DF11/DF19, R DR24/DR27-fsync y HF25–HF30 se distingue de SIGKILL. No hay transferencia a operaciones/estados nuevos por compartir Store.

## No aplicables justificados y perímetro

| ID / target | Operación / obligación acotada | Razón y conservación |
|---|---|---|
| NAp01 / R / NATIVE_R | IMPORT_I26 | R admite bytes JSON y SOURCE/BATCH propios; no captura Drive/I26 ni pin Markdown. |
| NAp02 / R / NATIVE_R | EVALUATION_MARKDOWN_AND_EFFECT_T | La ruta R prepara/revisa BATCH; no inventar EVALUATION/EFFECT T. |
| NAp03 / T / NATIVE_T | APPLY_BATCH_SELECT_TASKS_R | T aplica una TASK por EFFECT; las operaciones de lote/selección R no existen en esa autoridad. |
| NAp04 / REMOTE.lookup/query | STORE_COMMIT_OF_PURE_READ | La consulta remota es lectura; no existe publicación REMOTE a interrumpir. QUERY/RESULT/OBSERVE CLIENT y pérdida de P sí son aplicables. |
| NAp05 / NATIVE_T / NATIVE_R I54 | CLOSE_PUBLIC_API | El alcance I54 es CREATE y su nueva fachada no expone CLOSE. El CLOSE legacy de FL14/FL32 permanece aplicable. |
| NAp06 / F0 I26 | NEW_F0_CAMPAIGN_IN_I58 | F0 es prerrequisito y queda fuera del corte F1–F7; no se declara cubierto por matar IMPORT ni se reabre I26. |

NAp06 es exclusión del corte, no inaplicabilidad de F0 al sistema. La ausencia de CLOSE en la fachada nativa no elimina CLOSE legacy. Operación existente sin evidencia es P/D/M/H según corresponda, nunca N/A. Perfil/cuenta/política/observaciones/CLOCK/VALIDATE son auxiliares o entradas: no se certifican todos sus intercalados aquí.

NATIVE_T/NATIVE_R conserva únicamente las cuatro secuencias F7 de NA29–NA32 en este catálogo. Las demás afirmaciones de recuperación de esa extensión son NOT_ASSESSED; I58 no añade casos nativos ni los da por cubiertos por T/R v1. Una ampliación futura exige perímetro propio, no un producto cartesiano obligatorio por defecto. I38 sigue fijo y no se ejecuta.

I57 sólo diseña, sin runtime/discovery/campañas. UI22.2 PARTIAL; I56 77/7 y H07/global abiertos intactos. D1–D4/A52 conservados; D5 global/G01–G07 y cinco GI abiertos. Sin publicación nueva, proveedor/credenciales reales, consumo/reservas, activación, promoción, despliegue o D6.
