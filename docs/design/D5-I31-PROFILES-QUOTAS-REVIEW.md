# D5 I31 — matriz de perfiles y cuotas sintéticas

Fecha: 2026-10-22. **34 casos propuestos; ninguno ejecutado en I31.**
[Contrato A72–A74](D5-I31-PROFILES-QUOTAS-DESIGN.md) ·
[Comprobaciones documentales](../validation/D5-I31-design-review.json).

English: proposed in-memory tests only; no real quota/provider permission proof,
D3 capacity mutation, source-profile conversion or integrated D5 acceptance.
Todas las filas tienen estado `DESIGN_NOT_EXECUTED`. Las 34 filas no se suman a
las 195 pruebas históricas I30; una fila puede necesitar más de un test.

| Caso | Criterio | Fixture/estímulo | Resultado exigido |
|---|---|---|---|
| PQ01 | GI04 | Bytes idénticos bajo descriptor/política anterior y nueva | Content hash igual, captura/preview/manifiesto distintos y revisiones propias |
| PQ02 | GI04 | Solo cambia versión de política y la proyección textual coincide | Paquete anterior obsoleto; no inferir compatibilidad ni heredar ACCEPT |
| PQ03 | GI04 | Descriptor/decoder desconocido o intento de ruta/comando/import | Bytes acotados conservados como BLOCKED; ningún código fuente ejecutado |
| PQ04 | GI04 | Documento+ID o título coincide con correspondencia de perfil anterior | Historial intacto y reutilización bloqueada; sin conversión/adopción automática |
| PQ05 | GI04 | Cambio/revocación/restauración ABA de perfil seleccionado | Generación monótona invalida el paquete viejo aunque vuelvan valores |
| PQ06 | GI04 | Revisión de fuente revocada/reemplazada y preview checklist sin ID estable | No obtener identidad estable ni elegibilidad por título/línea; SOURCE exacto requerido |
| PQ07 | GI04 | Replay de captura/recibo histórico tras cambio de perfil | Recuperar evidencia histórica sin restaurar selección o correspondencias |
| PQ08 | GI20 | Demanda de varias dimensiones y dos ventanas de una dimensión, todas válidas | Evaluar cada restricción exacta de la misma cuenta; nunca sumar unidades/ventanas |
| PQ09 | GI20 | Saldo suficiente repartido entre cuentas/proveedores distintos | Bloqueo de ámbito; no combinar ni heredar frescura |
| PQ10 | GI20 | Dos bindings/alias intentan representar un recurso como cuentas distintas | Conflicto o resolución a cuenta canónica explícita; cero capacidad multiplicada |
| PQ11 | GI20 | Falta una dimensión/ventana exigida o el caller omite una restricción | Bloquear vector incompleto; no elegir solo el subconjunto favorable |
| PQ12 | GI20 | Restricción duplicada, unidad distinta o coste float/negativo/cero | Rechazo cerrado sin sumar, convertir o redondear |
| PQ13 | GI20 | Saldo KNOWN cero frente a UNKNOWN/UNLIMITED_DECLARED/REVOKED | Estados distintos y bloqueo con coste positivo; cero no significa ilimitado |
| PQ14 | GI20 | Una observación caduca o aún no comienza su ventana | Bloquear el conjunto, sin sustituir por otra cuenta/ventana |
| PQ15 | GI20 | Caducidad/fin de ventana exactos y horizonte pierde cobertura | Bordes semiabiertos y cobertura explícita correctos; sin alterar lease D3 |
| PQ16 | GI20 | Reset/rollover, replay de observación y reintento de lectura | Historial intacto; sin saldo adicional, reservas nuevas o remapeo de compromisos |
| PQ17 | GI20 | Dos lectores concurrentes obtienen resultado positivo | Cero consumo/reservas y ninguna autoridad de ejecución; no prometer capacidad reservada |
| PQ18 | GI20 | Fuente contiene proveedor, comando, prioridad o fallback de pago | Datos inertes; política de demanda/binding solo del harness, sin fallback |
| PQ19 | GI22 | Manifiesto con adapter/release/hash y todos los IDs/hashes de observación | Revisión propia fija vector, hechos y generaciones exactos; SOURCE no la sustituye |
| PQ20 | GI22 | Nuevo ID de observación con los mismos valores | Avanzar generación de cuenta, invalidar paquete anterior y exigir evaluación/revisión nuevas |
| PQ21 | GI22 | Cambiar/revocar adaptador, permiso o capacidad | Invalidar elegibilidad aunque saldos sigan válidos; no rebajar D3 |
| PQ22 | GI22 | Datos de adaptador de otra release o snapshot incompleto | Bloqueo por ámbito/versiones, sin actualizar silenciosamente el manifiesto |
| PQ23 | GI22 | Observación más reciente por fecha sin selección explícita | No ganar por fecha; selección CAS/versionada exacta requerida |
| PQ24 | GI22 | Restaurar observación/capacidad anterior tras revocación | Historial y generaciones conservados; aprobación vieja no revive |
| PQ25 | GI22 | Aprobar una evaluación sobre hechos vigentes | Sin ciclo de hash; revisión/recibo no cambia hechos ni crea cuota |
| PQ26 | GI22 | Cambiar hechos o perfil después de calcular y antes del CAS | Conflicto completo, sin resultado positivo confirmado bajo snapshot viejo |
| PQ27 | GI22 | Revocar/reemplazar EVALUATION durante validación | CAS detecta cambio; otra revisión explícita no se confunde con la anterior |
| PQ28 | GI22 | Avanzar reloj sin modificar hechos hasta caducidad o pérdida de horizonte | Guardas temporales bloquean con generación sin cambios |
| PQ29 | GI22 | Replay confirmado tras caducidad/revocación y comando nuevo | Replay etiquetado histórico sin autoridad actual; comando nuevo revalida y bloquea |
| PQ30 | GI22 | Mismo command_id con request diferente | Conflicto, recibo anterior intacto y cero consumo |
| PQ31 | GI22 | Campos extra, tipos/IDs inválidos o payload/error con secreto no admitido | Rechazo/código saneado; sin texto fuente/cuerpo crudo en recibos públicos |
| PQ32 | GI22 | Superar perfiles/cuentas/restricciones/observaciones/recibos/tamaños | Bloqueo sin truncar ni reiniciar presupuesto; documentar límites completos o reducidos realmente probados |
| PQ33 | GI22 | Pérdida de memoria o apertura de otro laboratorio | No heredar aprobaciones/recibos ni afirmar recuperación durable |
| PQ34 | GI22 | Auditoría final, regresiones y recursos del harness | Cero SQL/HTTP/D2 persistente/consumo/reservas/activación; D3/historia intactos y G01–G07 abiertos |

## Puerta de implementación

Propuesta: aprobar I31 y autorizar PQ01–PQ34 con fixtures en memoria, parsers
existentes sin cambios y versiones sintéticas de descriptor, reloj lógico y
concurrencia controlada. Sin cambio de contratos/código D3, SQL, HTTP, proveedores
reales, efectos D2, consumo/reservas, activación, promoción, despliegue o D6.
Aprobación de diseño e implementación, publicación Git y aceptación global siguen
siendo decisiones separadas. Alternativas: aprobar solo diseño o pedir ajustes.
