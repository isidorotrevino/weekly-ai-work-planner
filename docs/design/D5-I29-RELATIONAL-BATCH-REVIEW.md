# D5 I29 — matriz de relaciones y lotes sintéticos

Fecha: 2026-10-22. **34 casos propuestos; ninguno ejecutado en I29.**
[Contrato A68–A70](D5-I29-RELATIONAL-BATCH-DESIGN.md) ·
[Comprobaciones documentales](../validation/D5-I29-design-review.json).

English: proposed in-memory batch tests, not SQL/D2 conformance or runtime results.
Cada fila tiene estado `DESIGN_NOT_EXECUTED`; puede requerir varios tests. Las
34 filas no se suman a las 157 pruebas históricas I28.

| Caso | Criterio | Fixture/estímulo | Resultado exigido |
|---|---|---|---|
| RB01 | GI28 | Fuente con requisitos/épicas/tareas explícitos y relaciones declaradas | Bytes/hash/localizadores conservados; UUID/claves registrados, sin inferencia por narrativa |
| RB02 | GI28 | Referencia a entidad existente vinculada o creada más tarde en el mismo lote | Resolver por identidad exacta; orden de filas no impone creación ni autoridad |
| RB03 | GI28 | Endpoint inexistente, UUID/clave incompatibles o entidad sin correspondencia | Bloquear todo el paquete; no adoptar por título ni crear contenedor faltante |
| RB04 | GI28 | Tipo de extremo incorrecto o proyecto distinto en cualquiera de las relaciones | Rechazo completo; capabilities/cross-project quedan fuera, no se degradan a vínculo local |
| RB05 | GI28 | EPIC_REQUIREMENT explícito, repetido idéntico y otro requisito distinto | Una unión por par, evidencia íntegra; adiciones válidas sin reemplazar relaciones anteriores |
| RB06 | GI28 | TASK_EPIC nulo→UUID, mismo UUID y cambio a otra épica | Primero asigna, segundo no-op con evidencia; tercero bloquea sin retirar la anterior |
| RB07 | GI28 | Dependencia predecessor/successor iguales | Self-loop bloqueado para HARD/SOFT/MOCKABLE/OPTIONAL |
| RB08 | GI28 | Dependencias con cuatro kinds explícitos y par duplicado con kind distinto | Conservar tipo; repetición exacta deduplica, cambio de kind bloquea |
| RB09 | GI28 | Ciclo HARD formado íntegramente por varias adiciones del lote | Bloquear todo; no publicar prefijo ni validar aristas aisladamente |
| RB10 | GI28 | Camino HARD ya existente cerrado por una adición nueva | Detectar ciclo en grafo completo; el subgrafo del paquete no basta |
| RB11 | GI28 | Ciclo SOFT o mixto cuya parte HARD es acíclica | Admitir si demás guardas válidas; sin convertir SOFT/MOCKABLE/OPTIONAL en HARD |
| RB12 | GI28 | Relaciones ausentes en revisión siguiente del documento | Conservar entidades, correspondencias y vínculos; ausencia no elimina/cierra |
| RB13 | GI29 | Lote válido de creaciones tipadas, actualizaciones y relaciones aditivas | Un commit raíz con entidades/mappings/vínculos/bases/procedencia/recibo; DRAFT/BACKLOG sin activación |
| RB14 | GI29 | Dos identidades para mismo UUID/clave o una identidad con dos destinos | Conflicto completo sin adoptar, renombrar claves o convertir tipos |
| RB15 | GI29 | Última entidad o relación de un lote mixto inválida | Ninguna creación, PATCH, correspondencia o vínculo parcial confirmado |
| RB16 | GI29 | Edición local previa a preparar, en contenido, epic_id o relaciones administradas | No capturarla como base del origen; bloquear lote entero sin resolución automática |
| RB17 | GI29 | Cambio local después de preparar en campo administrado o ajeno | CAS de snapshot/generación bloquea; preservar la edición y todo estado previo |
| RB18 | GI29 | Cambio/restauración ABA o edición concurrente de endpoint de solo lectura | Versión/generación monótona invalida aunque vuelva el mismo texto; cero efectos parciales |
| RB19 | GI29 | Estado fuera de DRAFT/BACKLOG, trabajo actual o histórico en entidad/tareas relacionadas | Bloquear por guardas de fixture; no crear operaciones reales para probarlo |
| RB20 | GI29 | Revocar/reemplazar SOURCE o BATCH tras preparar/aprobar | Invalidar ticket; revisión de otro flujo/publicación no autoriza batch |
| RB21 | GI29 | Aprobar manifiesto válido y aplicar su ticket exacto | Aprobación no invalida su propio paquete; hash inmutable sin referencia circular y generación de datos aprobada exacta, separada de root_revision de revisiones |
| RB22 | GI29 | Cambio de bytes/perfil/identidad de snapshot o adulteración de manifiesto/request | Rechazo por hash/versión/shape; sin reinterpretar revisión vieja por fecha |
| RB23 | GI29 | Dos lotes preparados/aprobados que compiten por una cabeza común | Solo uno publica; otro conflicto sin prefijo. Barrera en candidatos listos antes del CAS |
| RB24 | GI29 | Fallo durante preparación/validación o antes de publicar raíz | Cabeza previa íntegra; ningún recibo de aplicación o mapping huérfano confirmado |
| RB25 | GI29 | Pérdida de respuesta tras publicar raíz | Recuperar recibo exacto por comando/hash en memoria; ningún segundo efecto |
| RB26 | GI29 | Replay antiguo tras una cabeza nueva y otro request con mismo command_id | Replay histórico no rebobina; request diferente bloquea |
| RB27 | GI29 | Misma entidad recibe cambio de texto y asignación de épica en un lote | row_version avanza una vez; base D5/procedencia también una vez, sin doble PATCH |
| RB28 | GI29 | No-op de contenido o relación exacta con evidencia nueva | Conservar row_version; registrar procedencia/cabeza D5 una vez sin perder evidencia anterior |
| RB29 | GI29 | Campo description de épica, Status/Verified e instrucciones en texto | Description solo evidencia; estados/instrucciones no activan ni alteran whitelist |
| RB30 | GI29 | JSON duplicado/campo extra/tipo/UUID inválido o relación no declarada | Rechazo cerrado; no reparación/truncamiento/inferencia ni errores que revelen texto crudo |
| RB31 | GI29 | Exceder fuente 2 MiB, manifiesto 4 MiB, 32 elementos o 64 declaraciones | Bloquear antes de publicar; demostrar límites y distinguir pruebas con presupuestos reducidos |
| RB32 | GI29 | Exceder 128 entidades, 256 relaciones o 128 comandos confirmados | No avance ni recorte parcial; replay confirmado sigue recuperable al alcanzar límite |
| RB33 | GI29 | Perder toda la memoria o abrir otro modelo independiente | No afirmar recuperación durable ni heredar recibos/autoridad; sin reinicio de proceso probado |
| RB34 | GI29 | Final de campaña con regresiones históricas identificadas | Cero operaciones/activación/D2 persistente/HTTP/SQL/Docker; hilos propios terminados, evidencia anterior intacta y G01–G07 abiertos |

## Puerta de implementación

Propuesta: aprobar I29 y autorizar RB01–RB34 con fixtures en memoria, reloj/versiones
lógicos, fallos en fronteras de publicación y concurrencia controlada del harness.
Sin proveedores reales, SQL, persistencia D2, promoción, despliegue o D6. Las
regresiones I26 mantienen su filesystem/hijos propios y evidencia separada del
nuevo batch volátil. No se atribuirán pruebas nuevas a cierres D1–D4/I1–I20.

La aplicación propuesta es simulada y no cubre adopción, capacidades, cross-project,
reaparición, retirada de relaciones, resolución de ediciones locales ni grooming
real suficiente. No basta para GI30, GI38/GI39/GI40 generales o cierre global.
