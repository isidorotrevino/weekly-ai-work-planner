# D5 I23 — matriz integrada propuesta G01–G07

Fecha: 2026-10-22. **DISEÑO; 42 casos propuestos, no ejecutados.**
[Contrato y decisiones A53–A58](D5-I23-GLOBAL-INTEGRATION-DESIGN.md) ·
[Hito local aceptado, distinto](D5-LOCAL-SYNTHETIC-approved.md).

English: proposed acceptance matrix, not test results. No implementation or live
provider exercise is claimed. Material choices A54–A58 are recorded; approval of
the integrated contract and any implementation is still pending. Synthetic and
real-provider evidence remain separate.

Todos los casos tienen estado `DESIGN_NOT_EXECUTED`. S significa candidato a
fixture sintética en un incremento posterior autorizado; R requiere evidencia
real/versionada y autorización separada. Un resultado S positivo nunca satisface
por sí solo la fila R correspondiente. La falta de autorización real se conserva
como pendiente; no se omite el caso para declarar completo D5.

| ID | Brecha | Capa | Criterio y resultado que se exigiría |
|---|---|---|---|
| GI01 | G01 | S | Perfil explícito y versionado: entrada admitida conserva bytes, localizadores y todos los campos; perfil desconocido bloquea |
| GI02 | G01 | S | Duplicados/ambigüedad y revisión incompatible bloquean sin normalizar silenciosamente la fuente |
| GI03 | G01 | S | Mover/editar checklist no adopta por línea/título; sin identidad estable explícita conserva solo preview |
| GI04 | G01 | S | Nueva versión de perfil/política requiere manifest/revisión nuevos y no cambia correspondencias históricas |
| GI05 | G01 | S | Routing no ejecuta instrucciones del documento ni cambia capacidad/política D3; script/capacidad desconocidos bloquean |
| GI06 | G01 | R | Muestras representativas y script Gentle-AI identificados por versión/interfaz; corpus privado revisado sin publicarlo ni ejecutar instrucciones arbitrarias |
| GI07 | G02 | S | Inventario inicial con ancla y replay procesa/deduplica el feed sin saltos de cursor; no promete snapshot global ni todas las revisiones intermedias |
| GI08 | G02 | S | Varias páginas/replay/reinicio: cada evento queda durable antes del cursor; fallo antes de commit no avanza; duplicado no duplica efecto |
| GI09 | G02 | S | Archivo fuera de allowlist/removed/pérdida de acceso: diagnóstico explícito recuperable, sin borrar/cerrar D2 ni elegir referencia válida |
| GI10 | G02 | S | Cambio de bytes/metadatos durante captura bloquea; exportación no atómica conserva grado observado, no revisión inmutable ficticia |
| GI11 | G02 | S | Cambiar ámbito invalida cursor; formato no soportado, tamaño, página inválida, error de permiso/rate limit no producen aceptación parcial silenciosa |
| GI12 | G02 | R | Instancia/ámbito/API/formatos/permisos/capturas reales autorizados; revisión/exportación y recuperación acreditadas en esa combinación |
| GI13 | G03 | S | Binding explícito y whitelist preservan campos ajenos y no adoptan por similitud ni traducen estado remoto a activación |
| GI14 | G03 | S | Edición remota antes o durante escritura exige precondición atómica en el doble; no disponible/rechazada abre conflicto o bloqueo, jamás PATCH incondicional |
| GI15 | G03 | S | Crear con respuesta perdida: correlación estable, unicidad acreditada y conciliación antes de retry; cero lecturas eventual no prueba ausencia; duplicados bloquean |
| GI16 | G03 | S | Cambiar D2/revisión/aprobación invalida paquete preparado; red fuera de locks y replay histórico nunca restauran payload viejo automáticamente |
| GI17 | G03 | S | Respuesta perdida tras envío conserva UNKNOWN; rechazo concluyente y 429 respetan presupuesto sin presumir éxito; ACK local no prueba efecto ni resuelve por fecha |
| GI18 | G03 | R | Versión/edición y contrato Plane objetivo demuestran CAS/alternativa atómica, correlación/creación y conflicto concurrente; mock o página pública no bastan |
| GI19 | G04 | S | Cuota desconocida, inválida o caducada bloquea; cero no se interpreta ilimitado ni se hereda frescura de otra cuenta |
| GI20 | G04 | S | Dimensiones/ventanas/proveedores se mantienen separados; observaciones/reintentos no crean capacidad ni reservas |
| GI21 | G04 | S | Routing incompatible, proveedor caído y denegación de permiso no disparan fallback de pago ni activación |
| GI22 | G04 | S | Observación y versión de adaptador ligadas al manifiesto; cambio/revocación invalida elegibilidad según D3 sin alterar su contrato |
| GI23 | G04 | S | Payload/errores/recibos no incluyen secretos y distinguen autorización declarada de permiso real comprobado |
| GI24 | G04 | R | Cada CLI/proveedor y modo unattended objetivo tienen evidencia empírica autorizada de permisos, ventanas/cuotas y errores; ninguna cifra sintética se presenta real |
| GI25 | G05 | S | Solo elementos explícitos por perfil producen propuestas; narrativa/título no inventa requisito, épica o dependencia |
| GI26 | G05 | S | Propuesta tipada y claves internas/UUID explícitos; campos inexistentes D2, como description de epic, permanecen evidencia y no crean columnas |
| GI27 | G05 | S | DRAFT/BACKLOG iniciales, procedencia exacta y revisión del manifiesto: Status/Verified no autorizan workflow ni grooming automático |
| GI28 | G05 | S | Referencias inexistentes/cross-project inválidas, ciclos o proyecto/tipo incompatibles bloquean; sin vínculos parciales |
| GI29 | G05 | S | Aplicación futura exige CAS, límites y guardas de edición local; batch mixto revierte completo, replay recupera y ausencia no borra |
| GI30 | G05 | R | Revisión humana de muestras representativas acredita suficiencia del contrato de grooming y sus exclusiones, separada de fixtures/estados de ejecución |
| GI31 | G06 | S | Toda obligación G01–G07 tiene contrato/criterio/evidencia propia; capacidad desconocida conserva pendiente explícito |
| GI32 | G06 | S | Aprobación de diseño, implementación, publicación, hito local y aceptación global se distinguen y no se infieren entre sí |
| GI33 | G06 | S | Inventario liga código/config/perfiles/versión/API a campaña; cambios relevantes invalidan evidencia aplicable sin reescribir historia |
| GI34 | G06 | S | Regresiones de I1–I20 y D1–D4 conservan hashes/targets separados; suites acumulativas no se suman como nuevas |
| GI35 | G06 | S | Clasificación sintético/real y bloqueos por permisos visibles; ninguna brecha D5 se mueve a D6 para afirmar completitud |
| GI36 | G06 | R | Decisión expresa de aceptación global sobre contratos, restricciones y evidencias integradas suficientes; publicación o aceptación local A52 no la sustituyen |
| GI37 | G07 | S | Ciclo sintético fuente→revisión→propuesta→aplicación simulada→proyección simulada→recibo conserva identidad/hashes en todas las fronteras |
| GI38 | G07 | S | Fallos antes/después de cada frontera, caída/reinicio y respuesta perdida recuperan sin duplicar efectos ni perder conflictos |
| GI39 | G07 | S | Ediciones concurrentes de origen/D2/Plane se reproducen y bloquean según contrato, sin sobrescritura ganadora por fecha |
| GI40 | G07 | S | Auditoría final demuestra cero activación/operaciones y limpieza selectiva del laboratorio autorizado; dev/D4 intactos |
| GI41 | G07 | S | Informe identifica qué integraciones son dobles y qué casos no corrieron; no afirma completar G01–G07 con PASS sintético |
| GI42 | G07 | R | Ciclo integrado autorizado de versiones/ámbitos reales acordados acredita conflictos, conciliación y recuperación; sin promoción/despliegue implícitos |

## Cobertura del primer corte offline propuesto

Dieciocho criterios S: GI01/GI02/GI03/GI05/GI10/GI13/GI14/GI19/GI21/GI23/
GI25/GI26/GI27/GI31/GI32/GI35/GI37/GI41, con dobles en memoria y sin efectos D2
persistentes. Los demás 17 S y los siete R permanecen fuera de ese primer corte.
GI37 solo acreditaría el ciclo simulado; no una importación SQL ni un efecto remoto.
La aprobación debe nombrar expresamente este alcance; no se deduce de A54–A58.

## Puertas de decisión

- A54–A58 ya fijan extracción, autoridad D2, perfiles separados, contenido Drive y
  bloqueo Plane. No quedan esas preguntas pendientes; el contrato integrado sigue
  para revisión y no implica aprobación de implementación.
- Aprobar contrato y alcance de implementación concreto antes de SQL/conectores
  nuevos. El primer corte offline propuesto no ejecutaría GI06/12/18/24/30/36/42
  como pruebas reales ni escribiría tareas D2.
- Separar validación sintética, con evidencia propia, de cualquier campaña real.
  La autorización actual no permite proveedores/credenciales reales o activación.
- Mantener G01–G07 abiertos hasta cumplir el criterio de cada brecha y su decisión
  de aceptación. Un bloqueo correcto de escritura sin CAS es comportamiento seguro,
  pero no equivale a haber validado la integración Plane completa.
