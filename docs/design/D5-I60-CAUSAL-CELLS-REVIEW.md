# D5 I60 — matriz causal CE01–CE43

Fecha: **2026-10-25**. **NOT_RUN / NOT_REVIEWED**. [Contrato](D5-I60-CAUSAL-CELLS-DESIGN.md) · [Punteros, precondiciones y oráculos](../validation/D5-I60-design-review.json).

39 celdas I59 calificadas: 15 CLIENT T + 24 REMOTE T/R. Cada fila de dominio exige una caída positiva, raíz e identidad propias. Las restantes 101 celdas se conservan sin reevaluar. Cuatro controles separados; ninguna ejecución autorizada por este diseño.

| CE | Celda / F | Path / rol | Operación Store / modo / manifiesto | Punto | Publicado tras caída | Precondición |
|---|---|---|---|---|---|---|
| CE01 | FL07 / F3 | T / CLIENT | APPLY / LOCAL / None | before_object | No, HEAD previo | EFFECT_ACCEPTED_NOT_APPLIED |
| CE02 | FL07 / F3 | T / CLIENT | APPLY / LOCAL / None | after_object | No, HEAD previo | EFFECT_ACCEPTED_NOT_APPLIED |
| CE03 | FL07 / F3 | T / CLIENT | APPLY / LOCAL / None | before_replace | No, HEAD previo | EFFECT_ACCEPTED_NOT_APPLIED |
| CE04 | FL11 / F5 | T / CLIENT | ISSUE / CREATE / CREATE | before_object | No, HEAD previo | PROJECTION_ACCEPTED_NO_SEND |
| CE05 | FL11 / F5 | T / CLIENT | ISSUE / CREATE / CREATE | after_object | No, HEAD previo | PROJECTION_ACCEPTED_NO_SEND |
| CE06 | FL11 / F5 | T / CLIENT | ISSUE / CREATE / CREATE | before_replace | No, HEAD previo | PROJECTION_ACCEPTED_NO_SEND |
| CE07 | FL11 / F5 | T / CLIENT | ISSUE / CREATE / CREATE | after_head | Sí, recibo objetivo exacto | PROJECTION_ACCEPTED_NO_SEND |
| CE08 | FL12 / F6 | T / REMOTE | EXECUTE / CREATE / CREATE | before_object | No, HEAD previo | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE09 | FL12 / F6 | T / REMOTE | EXECUTE / CREATE / CREATE | after_object | No, HEAD previo | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE10 | FL12 / F6 | T / REMOTE | EXECUTE / CREATE / CREATE | before_replace | No, HEAD previo | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE11 | FL12 / F6 | T / REMOTE | EXECUTE / CREATE / CREATE | after_head | Sí, recibo objetivo exacto | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE12 | FL13 / F6 | T / REMOTE | EXECUTE / UPDATE / UPDATE | before_object | No, HEAD previo | CONFIRMED_CREATE_V1_FOREIGN_EDIT_V2_THEN_UPDATE_ISSUED |
| CE13 | FL13 / F6 | T / REMOTE | EXECUTE / UPDATE / UPDATE | after_object | No, HEAD previo | CONFIRMED_CREATE_V1_FOREIGN_EDIT_V2_THEN_UPDATE_ISSUED |
| CE14 | FL13 / F6 | T / REMOTE | EXECUTE / UPDATE / UPDATE | before_replace | No, HEAD previo | CONFIRMED_CREATE_V1_FOREIGN_EDIT_V2_THEN_UPDATE_ISSUED |
| CE15 | FL13 / F6 | T / REMOTE | EXECUTE / UPDATE / UPDATE | after_head | Sí, recibo objetivo exacto | CONFIRMED_CREATE_V1_FOREIGN_EDIT_V2_THEN_UPDATE_ISSUED |
| CE16 | FL14 / F6 | T / REMOTE | CLOSE / CLOSE / CREATE | before_object | No, HEAD previo | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE17 | FL14 / F6 | T / REMOTE | CLOSE / CLOSE / CREATE | after_object | No, HEAD previo | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE18 | FL14 / F6 | T / REMOTE | CLOSE / CLOSE / CREATE | before_replace | No, HEAD previo | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE19 | FL14 / F6 | T / REMOTE | CLOSE / CLOSE / CREATE | after_head | Sí, recibo objetivo exacto | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE20 | FL15 / F7 | T / CLIENT | QUERY / CREATE / CREATE | before_object | No, HEAD previo | ISSUED_EFFECT_PRESENT_NO_QUERY |
| CE21 | FL15 / F7 | T / CLIENT | QUERY / CREATE / CREATE | after_object | No, HEAD previo | ISSUED_EFFECT_PRESENT_NO_QUERY |
| CE22 | FL15 / F7 | T / CLIENT | QUERY / CREATE / CREATE | before_replace | No, HEAD previo | ISSUED_EFFECT_PRESENT_NO_QUERY |
| CE23 | FL15 / F7 | T / CLIENT | QUERY / CREATE / CREATE | after_head | Sí, recibo objetivo exacto | ISSUED_EFFECT_PRESENT_NO_QUERY |
| CE24 | FL16 / F7 | T / CLIENT | RESULT / CREATE / CREATE | before_object | No, HEAD previo | ISSUED_EFFECT_PRESENT_QUERY_ID_NONE |
| CE25 | FL16 / F7 | T / CLIENT | RESULT / CREATE / CREATE | after_object | No, HEAD previo | ISSUED_EFFECT_PRESENT_QUERY_ID_NONE |
| CE26 | FL16 / F7 | T / CLIENT | RESULT / CREATE / CREATE | before_replace | No, HEAD previo | ISSUED_EFFECT_PRESENT_QUERY_ID_NONE |
| CE27 | FL16 / F7 | T / CLIENT | RESULT / CREATE / CREATE | after_head | Sí, recibo objetivo exacto | ISSUED_EFFECT_PRESENT_QUERY_ID_NONE |
| CE28 | FL30 / F6 | R / REMOTE | EXECUTE / CREATE / CREATE | before_object | No, HEAD previo | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE29 | FL30 / F6 | R / REMOTE | EXECUTE / CREATE / CREATE | after_object | No, HEAD previo | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE30 | FL30 / F6 | R / REMOTE | EXECUTE / CREATE / CREATE | before_replace | No, HEAD previo | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE31 | FL30 / F6 | R / REMOTE | EXECUTE / CREATE / CREATE | after_head | Sí, recibo objetivo exacto | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE32 | FL31 / F6 | R / REMOTE | EXECUTE / UPDATE / UPDATE | before_object | No, HEAD previo | CONFIRMED_CREATE_V1_FOREIGN_EDIT_V2_THEN_UPDATE_ISSUED |
| CE33 | FL31 / F6 | R / REMOTE | EXECUTE / UPDATE / UPDATE | after_object | No, HEAD previo | CONFIRMED_CREATE_V1_FOREIGN_EDIT_V2_THEN_UPDATE_ISSUED |
| CE34 | FL31 / F6 | R / REMOTE | EXECUTE / UPDATE / UPDATE | before_replace | No, HEAD previo | CONFIRMED_CREATE_V1_FOREIGN_EDIT_V2_THEN_UPDATE_ISSUED |
| CE35 | FL31 / F6 | R / REMOTE | EXECUTE / UPDATE / UPDATE | after_head | Sí, recibo objetivo exacto | CONFIRMED_CREATE_V1_FOREIGN_EDIT_V2_THEN_UPDATE_ISSUED |
| CE36 | FL32 / F6 | R / REMOTE | CLOSE / CLOSE / CREATE | before_object | No, HEAD previo | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE37 | FL32 / F6 | R / REMOTE | CLOSE / CLOSE / CREATE | after_object | No, HEAD previo | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE38 | FL32 / F6 | R / REMOTE | CLOSE / CLOSE / CREATE | before_replace | No, HEAD previo | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |
| CE39 | FL32 / F6 | R / REMOTE | CLOSE / CLOSE / CREATE | after_head | Sí, recibo objetivo exacto | APPROVED_CREATE_ISSUED_NO_REMOTE_EFFECT |

| CE | Path | Control | Caídas positivas |
|---|---|---|---|
| CE40 | T | PROTOCOL_OWNERSHIP | 0 |
| CE41 | R | PROTOCOL_OWNERSHIP | 0 |
| CE42 | T | INVENTORY_RAW | 0 |
| CE43 | R | INVENTORY_RAW | 0 |

Los oráculos y continuaciones completos figuran por fila en el JSON y por familia en el contrato. Antes HEAD no significa ausencia de cualquier entidad: UPDATE conserva su entidad v2 de preparación (CREATE v1 + edición pública de foreign). Después HEAD CLOSE significa tombstone, sin efecto de entidad. No inferir el modo de la posición de la fila.

Regresiones propuestas, separadas: Python321 / HC24 / HF40 / IC30 / UQ24 / RV20 / NA36 / FN64. Cero pruebas ejecutadas en I60; sin cierre de UI22.2 o GI38.
