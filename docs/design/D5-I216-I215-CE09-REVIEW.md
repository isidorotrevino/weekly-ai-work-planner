# I216 — revisión documental de CE09/I215

CE09 se confirma como baseline documental de proyección pendiente para PGO181 candidato 02, sin nuevos hallazgos documentales bloqueantes. **No se acepta una proyección real ni se crea o emite C o acceptance.** CE08 carece de freeze/aceptación competente; siguen ausentes identidades, valores, cuerpos, hashes, pruebas previas y reloj/vigencias reales. PJC115-R2 mantiene la no admisión; E01–E05 siguen abiertas, E06 sin ejecutar, D5 abierto e IR03 `NOT_READY`.

La revisión contrasta [CE09 de I215](../validation/D5-I193-CE09-EXACT-C-PROJECTION-CANDIDATE.json) con I193, los schemas C/acceptance y las reglas K08/K10/K11/K12/K13/K16 de I191. [La reconstrucción](../validation/D5-I216-I215-source-reconstruction.json), [el dictamen](../validation/D5-I216-I215-documentary-review.json) y [el sello](../validation/D5-I216-integrity.json) permiten revisar tipos, cobertura de digest, fases y preservación sin modificar I215.

## Resultado de la revisión

| Aspecto | Confirmación documental y límite |
| --- | --- |
| Tres evidencias, tres comprobaciones y seis reglas | Conservadas literalmente junto a la frontera negativa de autorización y snapshot fresco futuro. |
| Tipos compartidos | Coinciden 14 propiedades y seis definiciones transitivas. Hay 15 nombres comunes; `schema` tiene constantes distintas y queda excluido. |
| C y acceptance | Contratos cerrados con 19 y 27 campos requeridos de primer nivel. Todos los slots de valores reales siguen ausentes. |
| Proyección de valores | Trece requieren valores aceptados exactos; `validity` requiere contención de intervalo. Ninguna proyección real verificada. |
| Constantes y caps | C v3, repository/root-path/offline-key-status exactos; límites candidatos C 8 192 y acceptance 16 384 bytes. No son cuotas aplicadas ni prueba de recursos. |
| Evidencia previa | Cinco referencias para basis, recursos, runtime R01, plataforma R02 y aceptación separada R08. No existen aquí los cuerpos o decisiones competentes. |
| Predicados | PJ01–PJ10 pertenecen a CE09; PJ11–PJ12 se difieren a CE10. Los doce permanecen sin evaluar por falta de evidencia real. |
| Tiempo y currentness | Reglas de lifetime <=3600, error conservador <=5, epoch/revocación/vigencia y contención preservadas; sin trusted-now o snapshots reales. |
| Identidad, roles y scope | Ocho exclusiones S01 y fronteras de custodia intactas; cinco plazas de revisión sin persona ni appointment aceptado. |

Los conteos de campos sólo describen contratos de primer nivel. No acreditan completitud de arrays, cuerpos detrás de referencias, provenance, firmas, capacidad de heap/CPU o éxito en 900 segundos. La igualdad estática de tipos no acepta valores reales ni sustituye la requalificación del mismo scope de fuentes/runtime/imagen/recursos.

## Precisiones sobre contención y cobertura

`validity` tiene idéntico tipo en C y acceptance, pero C debe quedar contenido en las vigencias actuales relevantes. No se exige igualdad de extremos para convertirlos en un único intervalo. El epoch sí debe concordar y se requiere `error_plataforma <= C.clock_error_seconds <=5`, con checks de trusted-now a ambos lados del intervalo. El reloj del host o la fecha del cliente no constituyen esa prueba.

La cobertura de C en el bundle es **indirecta por digest**: `signed_core.records.acceptance_record.trust_context_sha256` debe fijar `SHA256(JCS(C real completo))`. El `signed_core` cerrado contiene cinco registros y sus hashes, no un cuerpo C adicional. I215 no se interpreta como autorización para añadir C a ese tipo ni a C un hash del bundle. Se conservan los ocho campos del core y los tres campos superiores de bundle: `schema`, `signed_core` y `approvals`.

La expresión «validez del bundle» de PJ12 y del documento I215 se entiende como validez/currentness efectiva de los cinco registros, incluido acceptance, con C contenido en sus intervalos aceptados. El schema de bundle no posee un campo `validity` propio; esta revisión no introduce ese campo ni una vigencia independiente inventada.

Acceptance tampoco tiene firma propia. La expresión de K12 sobre firmar el digest se lee junto con I193 CE09 y el schema cerrado: las tres aprobaciones por dominios R01/R02/R08 de CE10 cubren el mismo `signed_core`, incluido acceptance con el digest de C. No se añade una firma al registro. Los anchors y contrato/schema de custodia deben seleccionarse independientemente; claves declaradas por C/bundle no se convierten automáticamente en anchors. Esto comprueba el contrato de cobertura, no una firma real.

## Autenticación previa y fases

La futura cobertura CE10 no suministra por sí sola los antecedentes auténticos de CE08 ni las cinco evidencias de acceptance. Roles/preparadores/requester/claves, imagen/runtime, caller/dominio/constructor y scope deben estar genuinamente aceptados y concordar. La decisión de acceptance sigue siendo exclusivamente de custodia, sin admisión de recursos o captura.

El grafo de pasos es acíclico: CE09 tiene CE01–CE08 como ancestros y no depende de CE10/CE11/CE12. En el DAG I191, C precede a acceptance y acceptance al bundle; este último no es el antecedente de su propia aceptación. Un root, E06 o recibo futuros tampoco justifican pruebas previas ausentes.

CE10 conserva bundle, aprobaciones y mapping; CE11 no depende del recibo CE12. Claim real y recibo continúan sujetos a admisión completa, autorización explícita separada y todos los prerrequisitos externos de I193. No se emiten C wire, Q, request, root, bundle, mapping, claim o recibo en esta unidad. Cambios de autor, cuerpo, scope, dominio, epoch/clave/política exigen nueva revisión de los candidatos afectados y CE11; no hay transferencia automática de hashes/aceptaciones ni rebind activo.

El certificado I122 conserva `IMPLEMENTED_NOT_ADMITTED`, CP03 heredado sólo en su scope original, CP07 falso, atomicidad correlacionada sin verificar y componentes `NOT_RUN`. No se emite `SOURCE_CAPACITY_VERIFIED` ni se cierra ninguna obligación de recursos. La reconstrucción la realiza el mismo asistente que preparó I215; no equivale a revisión independiente competente ni aceptación separada R08.

## Verificación y publicación

Comando exclusivamente documental: `python3 docs/validation/D5-I216-audit.py`.

Resultado: `PASS_STATIC_SOURCE_ONLY_C_AND_ACCEPTANCE_MISSING`. Contrasta 877 pins con blobs del commit base I215 `b098d19c639e39be6e2ccacde1227cd405bfd311`, preserva 569 archivos publicados y exige cinco archivos nuevos. Reconstruye directamente los tipos y sus referencias, constantes, campos, evidencias, cobertura y fases; reproduce el build documental I215 y sus doce rechazos en memoria, sin invocar mains históricos de publicación. No es un PASS de recursos, de proyección real o de cualificación.

El guard histórico se comprueba directamente: CE09 no existía en la base I215 y sí existe en la base I216. Sólo se proyecta aquella consulta exacta `Path.exists`, con restauración ante éxito y excepción. No cambian blobs ni controles de otras rutas. CE01–CE09 siguen presentes y los tres dossiers CE10–CE12 ausentes.

Harness runtime: N/A; sólo se revisan JSON/Git/hash, fragments de schemas, tipos y dependencias. No se importan, compilan ni ejecutan producto/componentes ni codecs/crypto positivos, builds, probes, clocks/ledger, claims, procesos, benchmarks, enrollment, firmas o contactos. No se cambian cuotas, reservas, presupuesto, bindings, autoridades, destinos o contratos activos.

Commit y push autorizados para una unidad documental; se declara el exceso de 400 líneas por sus pins, matrices y preservación. Reversión exacta: retirar este documento, `D5-I216-I215-source-reconstruction.json`, `D5-I216-I215-documentary-review.json`, `D5-I216-audit.py` y `D5-I216-integrity.json`. Publicar no emite C ni acepta proyecciones. CE09 queda como baseline documental para una preparación CE10 solicitada por separado, con toda evidencia real y aceptación competente todavía pendiente.
