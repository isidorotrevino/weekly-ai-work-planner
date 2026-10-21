# D4 I12 — verificadores Java, presencia y matriz integrada

**Decisión posterior, 2026-10-20: cierre sintético aprobado expresamente.**
[Documento vigente](D4-approved.md) · [Manifiesto](../validation/D4-CLOSURE.json).
El texto de revisión siguiente conserva su estado anterior a esa aprobación.

Fecha: 2026-10-20. A23=B y A24=A aprobadas expresamente en esta sesión.
D4 sigue abierto; revisión final y aprobación de cierre pendientes. V29/V30
son propuestas aplicadas exclusivamente a bases desechables del laboratorio.
D1–D3, V1–V28 y los informes anteriores se conservan intactos.

## Port Java y procedencia

`TreeVerifier` porta los componentes locales a Java 21. Comprueba un árbol completo
contra el manifiesto confiable: hasta 64 archivos, 64 KiB por archivo, 4 MiB en total,
rutas acotadas, tamaños, SHA-256 y modo ejecutable. Rechaza archivos/directorios extra,
faltantes, rutas ambiguas, `.git`, symlinks, hardlinks y archivos no regulares.
Usa directorios seguros y canales sin seguir symlinks; rechaza alias en ancestros
del árbol y detecta cambios durante la observación. No promete una instantánea
atómica frente a escritores concurrentes: la fixture es confiable y exige
observación independiente de parada, exclusión y lecturas repetidas.

El Git nativo de la imagen fijada se invoca desde Java con comandos fijos, sin shell,
red, configuración heredada, hooks, filtros o fsmonitor. Se imponen límites de cinco
segundos y 2 MiB de salida por comando. Cada comprobación crea un bare nuevo en
`/tmp`, propiedad del verificador, y lo elimina al terminar. Comprueba tipos commit,
OIDs completos, ancestralidad, árbol, modos y contenido SHA-256 de blobs. Rechaza
configuración modificada, alternates, shallow, grafts, replace y alias de archivos.

El alcance sigue siendo A15: el verificador construye objetos de fixture a partir
de la base confiable y los bytes de archivos observados independientemente. El
commit candidato y su árbol pertenecen a ese repositorio sintético. **No acredita
historia Git producida por un worker ni importa un `.git` o bundle candidato.**
No ejecuta código candidato. La ampliación a importación Git arbitraria queda
fuera de este laboratorio, junto con conectores de proveedores reales.

`TreeEvidence` obtiene de SQL el manifiesto esperado y la base, congelados antes
del primer CLAIM. Comprueba su hash y la identidad, contexto y política; vuelve a
obtener la prueba host Ed25519 fresca de parada del proceso/grupo exactos. Lee el
volumen del worker montado de solo lectura, comprueba archivos, Git y otra vez el
árbol y la observación. El worker nunca proporciona el manifiesto esperado ni
puede insertar `tree_proofs`. Las rutas HTTPS de aceptación y checkpoint invocan
el port Java antes de registrar procedencia independiente.

V30 conserva `tree_requirements` y `tree_proofs` append-only, ligados a entrega e
intento. Un trigger exige prueba vigente de esa misma identidad/contexto/política
antes de cualquier nuevo ACCEPTANCE_PASS, incluso mediante entradas históricas,
y antes de insertar checkpoints nativos v1/v2. Solo se aplica a operaciones con
requisito congelado: no reinterpreta PASS históricos ni añade requisitos después
de un intento. El conjunto de requisitos y pruebas entra en el readset D3/CAS.
Los booleanos estructurales SQL no prueban criptografía por sí solos: el privilegio
de ingreso pertenece exclusivamente al verificador independiente.

La restauración es una condición de archivos esperada en política. La fixture
prepara el estado restaurado tras la salida real; el verificador lo observa, no
ejecuta `reset` ni scripts de rollback. APPLIED, consumo, generaciones y recibos
permanecen intactos. La campaña S27 primero rechaza un árbol aún sin restaurar y
luego acredita la restauración sin una segunda liquidación.

## Presencia durable sin autoridad de ejecución

V29 conserva sesiones, cabeza/secuencia, comandos y vínculo entrega→sesión.
Cada arranque tiene una incarnación UUID nueva. No es una atestación del host ni una defensa frente al uso malicioso de un
certificado comprometido: ordena mensajes y reinicios del principal autenticado.
El control plane registra la apertura solo para el worker mTLS habilitado en el catálogo y ONLINE por
administración, con CAS de la sesión anterior. Repetir el mismo comando no abre
otra sesión; cambiar su cuerpo se rechaza. Una apertura sustituida no se recupera
repitiendo un comando antiguo.

Los heartbeats de presencia usan la siguiente secuencia exacta y reloj SQL, nunca
una fecha del cliente. El periodo de la fixture es 15 s y la vigencia 90 s, conforme
al contrato existente. El ID de cada heartbeat se deriva de sesión+secuencia y se
reutiliza tras respuestas perdidas: su replay no refresca el tiempo observado.
El worker conserva el mismo comando de apertura durante los reintentos acotados.
Presencia no concede capacidades ni cambia automáticamente OFFLINE a ONLINE.

Nueva admisión, START, renovación y grants requieren presencia vigente. La entrega
queda ligada a su sesión: una incarnación nueva no adopta ni renueva una entrega
retenida del arranque anterior. El callback factual conserva su vínculo original
y las guardas de fencing D2; no equivale a un permiso de ejecutar. El transporte
rechaza requests PRESENCE antiguos sin sesión/secuencia. El controlador no expone
funciones SQL al worker.

La migración no inventa vínculos de sesión para entregas activas anteriores: sus
nuevos grants quedan bloqueados y necesitan la reconciliación existente. Los
vínculos añadidos por algunos tests son preparación explícita del propietario
para revalidar fronteras históricas, no comportamiento de upgrade.

Una sesión vencida o reemplazada no libera reserva, compromiso, lease ni exclusión;
no acredita parada ni cierra el receptor. Se conserva A10 para pérdida de renovación
de autoridad, A12 para pausa/rearme y A22 para cuarentena/barreras. El arranque con
historia local conserva RECOVERY_REQUIRED aunque su nueva presencia sea válida.
Para preparar el plan inicial, el propietario del bootstrap inserta sesiones de
fixture; cada worker las reemplaza mediante mTLS y confirma su primera secuencia
antes de anunciar health. Las entregas de Compose se ligan a esa sesión real del
arranque, no al seed de planificación. Este seed no es un protocolo de registro
productivo ni una prueba de presencia física.
El supervisor no adopta procesos por un cambio de sesión. La presencia y sus
vínculos se incluyen en el readset. Los mutex siguen el orden D3→D2.

## Campaña actual

`bash testing/D4/run-latest-matrix.sh` construye offline una sola imagen fijada y
revalida S01–S30 sobre V30 en dos grupos, como máximo dos proyectos simultáneos.
Cada caso conserva sus redes internas, roles, identidades efímeras, límites de
recursos, volúmenes e informe y hace cleanup selectivo por etiqueta. Un fallo
conserva evidencias y produce resultado no verde; no cierra D4.

Los casos nuevos son:

- S26: archivos y objetos Git verificados dentro de Java/HTTPS; polling espera
  PASS independiente y luego retira el trabajo.
- S27: rechazo de archivos sin restaurar; restauración local, comprobación Java
  independiente y PASS, con APPLIED y journal intactos.
- S28: polling pausado en checkpoint, recibo tardío, revisión y autorización
  explícitas; reinicio de worker/control/verificador; sesión durable nueva, rechazo
  de la sesión antigua y rearme explícito antes de completar la misma reserva.
- S30: reinicio real de PostgreSQL conserva sesiones/secuencias/vínculos; nuevo
  arranque del worker no adopta ni renueva la entrega anterior y conserva reserva,
  compromiso y lease sin fabricar parada.
- S29: polling con productor completado, reapertura y recurso físico en cuarentena;
  sin nueva admisión; el cierre del caso no rearma; comando nuevo admite la siguiente
  operación después de recalcular.

Las clases `LatestBoundaryTest` y `LatestReviewTest` reejecutan en V30 las fronteras
V25 y A21/A22, además de propagación por capacidades resueltas HARD/MOCKABLE y sus
consumidores transitivos, manteniendo SOFT/OPTIONAL. `LatestResetTest` espera una
frontera real de ventana física: START y renovación deben cubrir los 60 s completos,
sin rollover, cambio de mapping ni liberación. Las pruebas de presencia y
procedencia distinguen replays, sesión antigua, falta de prueba y permisos.
Las suites antiguas conservan sus targets originales y sus informes.

## Revisión final

La tabla de cobertura y el informe I12 deben distinguir la campaña actual V30,
las pruebas SQL sintéticas del propietario, el port Java y la regresión histórica.
Un resultado verde acredita únicamente el alcance acotado de fixtures confiables.
No valida proveedores, máquinas físicas, cuotas comerciales, código hostil,
importación Git arbitraria, compensación externa ni operación de producción.
Estos límites no se convierten en aprobaciones de D5/D6. El cierre formal de D4
requiere revisión final y aprobación expresa del usuario.

Resultado final: [informe I12](../validation/D4-I12-INTEGRATED-results.json),
638 pruebas positivas (281 D4 distintas, 332 D2/D3 y 25 Python) y 1.085
comprobaciones en S01–S30 sobre V30. Cinco pruebas repetidas del grupo adicional
se excluyen del total. Cleanup final confirmado por etiqueta. La
[revisión de aceptación](D4-I12-ACCEPTANCE-REVIEW.md) deja únicamente la aprobación
expresa del usuario pendiente; D4 sigue abierto.
