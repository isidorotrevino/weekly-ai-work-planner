# D5 I33 — matriz de unión y evidencia integrada

Fecha: **2026-10-23**. [Contrato propuesto](D5-I33-INTEGRATED-EVIDENCE-DESIGN.md).
**40 casos DESIGN_NOT_EXECUTED; cero pruebas nuevas ejecutadas.**

English: proposed cases, not results. M denotes the proposed volatile TASK path;
F now has a separate durable design and still requires approval; R denotes the
separate relational path. No isolated PASS satisfies an integrated restart case.

Todos los casos siguen pendientes. M no está autorizado para implementación;
F/R no se omiten ni se cuentan PASS si se elige solo M. Los oráculos son exigencias
para pruebas futuras. UIxx son IDs de matriz, no tests adicionales ni interfaz UI.

| ID | Criterio | Alcance | Caso y oráculo exigido |
|---|---|---|---|
| UI01 | GI33 | M | Inventario liga bytes de código/config/harness/perfil/esquema/entorno/comandos a run_id y resultados, incluyendo diff y archivos nuevos |
| UI02 | GI33 | M | Cambiar código o config relevante marca evidencia actual STALE_INPUTS; informe histórico conserva sus bytes/hash |
| UI03 | GI33 | M | Cambio de perfil/política/observación/versiones invalida paquete; etiqueta de versión o fecha reciente no sustituye hash/generación |
| UI04 | GI33 | M | Relación escenario→frontera→inputs→oráculo→resultado completa; input faltante/incompatible produce NOT_RUN/BLOCKED, sin PASS heredado |
| UI05 | GI33 | M | Bytes/evento/commit I26 exactos alcanzables; cursor no acepta fuente; OBSERVED_EXPORT no se eleva y queda fuera del T Markdown inicial |
| UI06 | GI33 | M | Inventario distingue API de fixture, código real y versión declarada; ninguna capacidad Plane/Gentle-AI/proveedor real se deduce |
| UI07 | GI33 | M | Cambio solo de índice se explica por separado; se verifica evidencia sellada en commit y aplicabilidad ejecutable actual sin reescribirla |
| UI08 | GI34 | M | Cierres D1–D4, aceptación A52 y código/SQL/harness históricos preservados; diferencias documentales permitidas identificadas |
| UI09 | GI34 | M | Cada grupo conserva target y comando/versiones propios; no etiquetar todas las regresiones como V30 |
| UI10 | GI34 | M | Suite acumulativa/IDs repetidos/filas/assertions no inflan tests distintos dentro de campaña; ejecuciones anteriores no se suman como nuevas |
| UI11 | GI34 | M | Históricos comprobados por hash, regresiones reejecutadas y escenarios nuevos en grupos separados; NOT_RUN SQL/D2–D4 explícito |
| UI12 | GI34 | M | Recursos/hijos/hilos de I26/I28/I30/I32 separados de los de unión; recuperación I26 no se atribuye a unión |
| UI13 | GI38 | M | F0→F1: fallo tras commit I26 y antes/después de importación no acepta fuente ni duplica identidad al repetir; bytes/ámbito/grado exactos |
| UI14 | GI38 | M | F1→F2: captura/perfil desconocido, fuente ambigua o discrepancia de hashes bloquea todos los efectos posteriores sin reparar datos |
| UI15 | GI38 | M | Revisiones SOURCE/EVALUATION/EFFECT/Plane independientes; falta/revocación/reemplazo de una no se cubre con otra aceptación |
| UI16 | GI38 | M | F2→F3: fallo previo conserva estado local; fallo posterior/respuesta perdida recupera recibo histórico exacto en memoria sin aplicar dos veces |
| UI17 | GI38 | M | F3→F4: fallo entre efecto local y binding conserva efecto local y fase pendiente; no inventa proyección ni recibo final exitoso |
| UI18 | GI38 | M | F4→F5: guardas fallidas antes de entrega producen NOT_SENT; entrega sin resultado concluyente preserva UNKNOWN, nunca retry ciego |
| UI19 | GI38 | M | F5→F6→F7: efecto simulado con respuesta perdida se concilia por clave/ticket/hash; un destino, cero restauración del payload viejo |
| UI20 | GI38 | M | Consulta eventual vacía/múltiple/incompatible y 429 ambiguo no prueban ausencia; conservar UNKNOWN/conflicto aunque cambie el paquete |
| UI21 | GI38 | M | Mismo command_id/request_hash recupera hecho histórico; request distinto bloquea; replay después de cambios no rebobina cabeza/revisiones |
| UI22 | GI38 | F | Caída/reinicio de cliente antes/después de cada F1–F7 con doble remoto superviviente; restaurar estado/recibos/conflictos sin duplicar efectos |
| UI23 | GI38 | F | Commit local incierto, intento durable previo al envío y respuesta perdida: recuperar raíz íntegra o bloquear; no inferir éxito de ACK local |
| UI24 | GI38 | F | Ledger/snapshot faltante/corrupto/incompatible y reloj reiniciado → bloqueo conservador, sin regenerar aceptación ni renovar frescura |
| UI25 | GI38 | R | Lote relacional completo o sin prefijo; TASK proyectada deriva del recibo/generación exactos; sin proyección de requisitos/épicas/relaciones ni conversión a perfil I32 |
| UI26 | GI39 | M | Origen/selección/revisión cambia antes del efecto: puerta de unión invalida snapshot copiado; ningún efecto bajo paquete viejo |
| UI27 | GI39 | M | Perfil/política/observación cambian o sufren ABA antes de confirmar: nuevas generaciones bloquean sin reutilizar revisión |
| UI28 | GI39 | M | Reloj cruza caducidad/horizonte con generación igual: evaluación bloquea y no concede capacidad/permiso |
| UI29 | GI39 | M | Edición de entidad local tras copiar a I28 y antes de entregar ticket detectada por vínculo con almacén dueño, sin envío obsoleto |
| UI30 | GI39 | M | Revocación/cambio local durante envío conserva efecto histórico + STALE/UNKNOWN y exige conciliación; no presume rollback remoto |
| UI31 | GI39 | M | Edición Plane antes/durante CAS, incluido ABA, bloquea sobrescritura; campos ajenos/sentinels se conservan |
| UI32 | GI39 | M | Dos comandos/paquetes y respuesta vs conciliación compiten con barreras: CAS conserva un resultado coherente y todos los conflictos, sin elegir por fecha |
| UI33 | GI39 | F | Dos procesos sobre el estado durable no pierden revisiones/recibos ni duplican intento; CAS/locks y puntos de crash requieren contrato F previo |
| UI34 | GI39 | R | Cambio local/relacional invalida lote y snapshot de TASK hacia I28; sin rebase parcial ni revisión I32 ficticia |
| UI35 | GI40 | M | Auditoría registra cero activación, operaciones/intentos operativos, consumo/reservas y permisos de ejecución; separa intentos Plane de fixture |
| UI36 | GI40 | M | No HTTP/SDK/CLI real, SQL/Docker nuevos ni lecturas de credenciales/corpus/dev; salidas evitan texto crudo/errores privados |
| UI37 | GI40 | M | Hilos nuevos terminan; regresiones identifican sus propios recursos; limpieza solo de raíces creadas con sentinels sintéticos hermanos intactos |
| UI38 | GI40 | F | Hijos de crash/reinicio terminados y raíces cliente/remoto propias limpiadas tras conservar evidencia saneada; nada de dev/D4 afectado por comandos |
| UI39 | GI40 | M | Límites propios y del componente más restrictivo bloquean sin truncar ni efecto parcial; presupuesto reducido no se presenta a tamaño completo |
| UI40 | GI40 | M | Informe final enumera qué corrió/no corrió, recursos, exclusiones y aplicabilidad; 30/35 previo no se convierte en 35/35 ni cierra G01–G07 por sumar PASS |

## Lectura de cobertura y decisiones

- **33 M**, **5 F** (UI22–UI24/UI33/UI38) y **2 R** (UI25/UI34): total **40**.
- La distribución por criterio y alcance se comprueba en el JSON documental.
- Elegir M deja los cinco casos F y dos R como NOT_RUN, además de cualquier otra
  exclusión descubierta; no satisface GI38 completo. GI39/GI40 solo tendrían
  evidencia del alcance efectivamente ejecutado y auditado.
- El usuario eligió **F para diseño**. El [contrato durable](D5-I33-DURABLE-INTEGRATION-DESIGN.md)
  y [DF01–DF48](D5-I33-DURABLE-INTEGRATION-REVIEW.md) concretan almacenamiento,
  reinicio y nuevo doble remoto; están preparados para revisión, no aprobados.
  Los 33 casos M son obligaciones de base aplicables a F, los cinco F se desglosan
  allí y los dos R siguen fuera. No se atribuye restauración a APIs volátiles.
- Aprobación de este diseño, autorización de implementación, validación,
  publicación de SHA y aceptación global son decisiones separadas.

D1–D4 cerrados; hito A52 aceptado sin ampliación. **D5 global y G01–G07 abiertos**.
Sin proveedores/credenciales reales, consumo/reservas, activación, promoción,
despliegue o D6. No hay resultados nuevos de runtime en I33 documental.
