# D5 I39 — matriz de revisión conjunta de suficiencia

Fecha: **2026-10-23**, Europe/Madrid.
[Contrato propuesto](D5-I39-SUFFICIENCY-REVIEW-DESIGN.md) · [Alcance A](D5-I39-NEXT-CUT-SCOPE.md).
**40 UI y SR01–SR14: REVIEW_NOT_EXECUTED. Cero dictámenes semánticos o tests nuevos.**

English: proposed documentary review matrix, not results. Candidate test mappings
are declarations copied from historical reports, not sufficiency conclusions.

## Obligaciones originales y foco propuesto

El texto original completo, modalidad y candidatos por test/field están en el
[JSON de diseño](../validation/D5-I39-design-review.json). Esta tabla resume el
foco de lectura futuro, sin sustituir o rebajar las obligaciones UI de I33.
En la columna declarada T=I34, R=I36; los números son referencias de test en mapas
por fila, no pruebas nuevas ni valoraciones de cobertura. I38 se usa en los controles
de inventario/contabilidad; sus EA no sustituyen fronteras o concurrencia T/R.

| UI | GI / modalidad original | Referencias declaradas | Foco y registro exigidos |
|---|---|---|---|
| UI01 | GI33 / M | T: 1; R: 0 | Contrastar inventario, comando y vínculo escenario/campaña; distinguir código/config embebida de versiones externas no registradas. |
| UI02 | GI33 / M | T: 1; R: 0 | Comprobar invalidación por cambio y por input nuevo; explicar I34 histórico MATCH con discovery actual STALE. |
| UI03 | GI33 / M | T: 1; R: 0 | Seguir pins de perfil/política/observación y generaciones en T; en R declarar ausencia de EVALUATION sin equivalencia ficticia. |
| UI04 | GI33 / M | T: 2; R: 0 | Desglosar escenario/frontera/oráculo/resultado; detectar mapa completo con caso parcial o detalle empírico ausente. |
| UI05 | GI33 / M | T: 1; R: 0 | Seguir bytes/IDs/procedencia entre captura I26 y T; distinguir captura JSON propia R y Docs OBSERVED_EXPORT pendiente. |
| UI06 | GI33 / M | T: 1; R: 0 | Delimitar API de fixture y capacidad real; no elevar CAS/cierre de ticket o versión declarada a capacidad Plane. |
| UI07 | GI33 / M | T: 1; R: 0 | Contrastar documentos emisores con los actuales; separar cambios de índices de cambios ejecutables y raw ausente. |
| UI08 | GI34 / M | T: 1; R: 0 | Enumerar preservación pública de cierres/A52 y sus límites D1/D2; no inferir inspección de dev/D4 operativo. |
| UI09 | GI34 / M | T: 1; R: 0 | Identificar targets/comandos/versiones de cada grupo efectivamente registrados; ausencias quedan NOT_RECORDED. |
| UI10 | GI34 / M | T: 1; R: 0 | Verificar IDs distintos y campañas separadas; intersección de 281 no suma 602 y casos/subcasos no añaden tests. |
| UI11 | GI34 / M | T: 2; R: 0 | Separar nuevos/regresiones ejecutadas y referencias históricas por hash; SQL/Java no reejecutados. |
| UI12 | GI34 / M | T: 1; R: 0 | Identificar recursos de T/R y regresiones; no atribuir persistencia al modelo volátil por recuperación I26. |
| UI13 | GI38 / M | T: 1; R: 0 | Localizar fallo antes/después de importación I26 a T y oráculo exacto; no confundir cursor capturado con fuente aceptada. |
| UI14 | GI38 / M | T: 2; R: 0 | Leer negativos de captura/perfil/hash/ámbito y comprobar bloqueo de efectos y ausencia de reparación silenciosa. |
| UI15 | GI38 / M | T: 2; R: 0 | Contrastar SOURCE/EVALUATION/EFFECT/PROJECTION T y SOURCE/BATCH/PROJECTION R; autoridad de revisión independiente. |
| UI16 | GI38 / M | T: 1; R: 0 | Verificar commit local y recibo juntos, fallos antes/después y replay histórico sin restauración o doble efecto. |
| UI17 | GI38 / M | T: 1; R: 0 | Examinar corte entre efecto local, binding y proyección; fase pendiente durable sin recibo final ficticio. |
| UI18 | GI38 / M | T: 2; R: 0 | Verificar guardas antes del ISSUE y ticket UNKNOWN durable antes de REMOTE; distinguir NOT_SENT de efecto posible. |
| UI19 | GI38 / M | T: 5; R: 0 | Seguir respuesta perdida y conciliación explícita con ticket/identidad/hash; prueba independiente de efecto único. |
| UI20 | GI38 / M | T: 4; R: 0 | Leer lookup vacío/múltiple/incompatible y 429; acreditar incertidumbre persistente y retry solo con no efecto concluyente. |
| UI21 | GI38 / M | T: 3; R: 0 | Contrastar command_id/request_hash, replay histórico y conflicto de payload; ningún rebobinado tras cambios posteriores. |
| UI22 | GI38 / F | T: 9; R: 0 | Expandir cada frontera y rol a puntos antes/después de crash/reinicio; no aceptar contador SIGKILL como cobertura completa. |
| UI23 | GI38 / F | T: 11; R: 0 | Verificar COMMIT_UNKNOWN/fsync, bloqueo de handle y reopen; ACK o excepción no prueban rollback o éxito. |
| UI24 | GI38 / F | T: 5; R: 0 | Leer corrupción/cadena/schema/huérfanos y reloj persistido; no génesis, fallback o frescura comercial inventada. |
| UI25 | GI38 / R | T: 0; R: 24 | Seguir lote R íntegro, recibo y generación exactos hasta TASK seleccionada y proyección; sin atomicidad remota distribuida. |
| UI26 | GI39 / M | T: 1; R: 0 | Contrastar fuente/selección/revisiones antes de efecto, incluidos cambios ABA; copia vieja no conserva autoridad. |
| UI27 | GI39 / M | T: 2; R: 0 | Examinar perfil/política/observación T y revocación/ABA; declarar diferencias de R sin forzar contrato Markdown. |
| UI28 | GI39 / M | T: 1; R: 0 | Leer caducidad y horizonte con generación igual y reloj lógico persistido; no permiso operacional o renovación al reiniciar. |
| UI29 | GI39 / M | T: 1; R: 0 | Contrastar dueño del snapshot local T/R frente a paquete preparado; justificar sustitución de objetos volátiles I28. |
| UI30 | GI39 / M | T: 1; R: 0 | Leer cambio/revocación durante envío y conciliación; conservar efecto histórico, STALE y UNKNOWN según frontera. |
| UI31 | GI39 / M | T: 2; R: 0 | Examinar cambio remoto y ABA frente a UPDATE/CAS; campos ajenos y base exacta, sin GET seguido de escritura incondicional. |
| UI32 | GI39 / M | T: 3; R: 0 | Identificar ordenaciones forzadas por barreras y resultados CAS; distinguir carrera real de interleaving secuencial. |
| UI33 | GI39 / F | T: 5; R: 0 | Verificar procesos sobre mismo estado, lock/CAS/revisiones/intentos; incluir oráculo independiente y resultados perdedores. |
| UI34 | GI39 / R | T: 0; R: 9 | Contrastar cambios locales/relacionales y nuevo lote no-op frente a snapshot R; incertidumbre previa bloquea nuevo envío. |
| UI35 | GI40 / M | T: 1; R: 0 | Separar declaraciones de cero actividad, guardas estáticas y observaciones; no elegibilidad como ejecución o reserva. |
| UI36 | GI40 / M | T: 2; R: 0 | Comprobar alcance de lectura/comandos/salida saneada; cero proveedores reales no equivale a revisión exhaustiva de seguridad. |
| UI37 | GI40 / M | T: 1; R: 0 | Leer creación/terminación de hilos y ownership de raíces/sentinels; regresiones y recursos nuevos separados. |
| UI38 | GI40 / F | T: 2; R: 0 | Contrastar tabla de hijos/exitcodes/raíces y limpieza selectiva con harness; no inferir estado operativo dev/D4. |
| UI39 | GI40 / M | T: 2; R: 0 | Enumerar límites realmente ejercitados y presupuestos reducidos; no capacidad simultánea máxima o benchmark. |
| UI40 | GI40 / M | T: 2; R: 0 | Contrastar resumen, casos no ejecutados, aplicabilidad, raw ausente y bloqueos; conservar D5/G01–G07 abiertos. |

Cada fila se desglosa por subcláusula y recorrido según el contrato. Exigir
path/commit/símbolo o línea, caso/test, frontera/rol/parametrización/oráculo, campo
de evidencia registrada, tres ejes de estado y pendiente. Ningún candidato se
eleva a SUPPORTS_BOUNDED hasta ejecutar y documentar la lectura autorizada.

## Controles transversales de revisión

| ID | GI | Control | Registro exigido |
|---|---|---|---|
| SR01 | GI33/GI34 | Autoridad, versiones y continuidad | Relacionar contratos emitidos, aprobaciones posteriores y namespaces; no restauración de privados o ampliación de A52. |
| SR02 | GI33 | Inventario y aplicabilidad | Fijar commits/bytes leídos, discovery histórico/actual y diferencias pertinentes; no rebaselinar. |
| SR03 | GI33 | Fuerza y trazabilidad de evidencia | Conservar raw I34/I36 NOT_RECORDED y raw propio I38 anclado; detalle empírico ausente no se reconstruye desde código. |
| SR04 | GI33/GI34/GI38/GI39/GI40 | Exhaustividad por cláusula y recorrido | UI01–UI40 completas, todas sus subcláusulas y modalidades; EXCLUDED local no elimina obligación global. |
| SR05 | GI33/GI38/GI39 | Escenario y oráculo | Resolver cada candidato a función/escenario/assert/harness; distinguir lector independiente de uso del propio estado calculado. |
| SR06 | GI38 | Fronteras y puntos de fallo | Tabla operación/rol/punto antes-después y resultados; comparar parametrización exigida y presente, sin sumar crashes. |
| SR07 | GI38/GI39 | Incertidumbre y recuperación | UNKNOWN/CONFLICT, reapertura pasiva, conciliación/retry y no efecto acreditado; ninguna consulta vacía prueba ausencia. |
| SR08 | GI39 | Ordenaciones concurrentes y ABA | Fuente/local/remoto, CAS y respuestas frente a revocación; evidencia de barreras y resultados de ambas ramas, no ganador por fecha. |
| SR09 | GI38/GI39 | Autoridad R y transacciones | BATCH local entero, selección desde recibo y proyección por TASK; vector parcial remoto sin rollback distribuido; T y R no intercambiables. |
| SR10 | GI33/GI40 | Elegibilidad y autoridad operacional | Pins/reloj/cuotas solo de fixture; positivo o recibo histórico no crea capacidad/reserva, permiso de ejecución o frescura real. |
| SR11 | GI34 | Targets y contabilidad | Separar 281/321/36 por campaña; intersección de IDs y SQL/Java históricos por hash; no cifra única de tests integrados. |
| SR12 | GI34/GI40 | Recursos y preservación pública | Hijos/hilos/raíces y sentinels por campaña, ownership/limpieza; conservar límites de prueba sobre D1–D4 sin inspección operativa. |
| SR13 | GI33/GI40 | Límites, privacidad y contexto | Máximos vs presupuestos reducidos; contexto Linux/fsync y exclusiones de caller hostil/energía; escaneo y hashes no garantía exhaustiva. |
| SR14 | GI33/GI34/GI38/GI39/GI40 | Dictamen y decisiones posteriores | Resumen de cinco GI trazable a subcláusulas/hallazgos; global_review OPEN, closure false y próximos pasos propuestos sin implementarlos. |

Los catorce controles son obligaciones documentales, no tests ejecutables ni
criterios globales nuevos. Sirven para comprobar coherencia entre las cuarenta UI
y los cinco resúmenes GI. No sustituyen filas, contraejemplos o ausencias.

## Decisión pendiente

**A:** aprobar I39 y autorizar la revisión documental I40 de UI/subcláusulas y
SR01–SR14, lectura pública T/R/I38 e integridad, sin modificar runtime o repetir
pruebas. **B:** aprobar solo diseño. **C:** ajustar contrato/matriz.

P0 continúa. D1–D4 cerrados y A52/I1–I20 sin ampliación; D5 global/G01–G07 abiertos.
Sin proveedores/credenciales reales, consumo/reservas, activación, promoción,
despliegue o D6. La publicación requiere autorización independiente del SHA concreto.
