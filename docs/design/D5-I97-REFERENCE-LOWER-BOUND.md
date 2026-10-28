# I97 — el techo actual de referencias es insuficiente

Fecha: 2026-10-28, Europe/Madrid. Revisión documental por la petición «continúa».
Fuentes y contabilidad I91/I92 conservadas. Cero campañas, tests, imports de
producto/runners, cambios de implementación/cuotas o publicación.

**Una captura completa válida de P01 con el perfil actual exige al menos19.037
referencias; el límite sigue siendo16.384.** Es una cota mínima condicional por
fuente, no una nueva ejecución, una cuota suficiente o una reconstrucción de I92.

## Derivación reproducible por anclas

El [registro JSON](../validation/D5-I97-reference-lower-bound.json) conserva hashes,
anclas AST y árboles de multiplicación para los48 DF y40 DR. De ellos,71 tests
aportan llamadas demostradas; todos corresponden al inventario causal T/R del
registro pinneado. Se incluyen self.phase_args/commit_crashes/remote_crashes/phase,
iteraciones literales y subTest. No se ejecutaron esos helpers.

| Ruta parental obligatoria | Invocaciones mínimas | Transacciones por invocación | Total mínimo |
|---|---:|---:|---:|
| durable_support.ready |136|14|1904|
| relational_support.prepare |113|6|678|
| Total | | |2582|

ready: REGISTER_PROFILE, SELECT_PROFILE, IMPORT, REVIEW SOURCE, BIND_ACCOUNT,
POLICY, dos pares OBSERVE/SELECT_OBSERVATION, PREPARE/REVIEW EVALUATION y
PREPARE/REVIEW EFFECT. prepare: CAPTURE, SELECT_SOURCE, PREPARE/REVIEW SOURCE y
PREPARE/REVIEW BATCH. Se omiten APPLY, proyecciones, dispatch y otros costes
opcionales, aunque se ejecuten en varias rutas. No se cuentan comandos del hijo.

En cada Client.perform exitoso, el wrapper abre C; el Store.transact anidado
abre otro C, carga2 slots de grupo/witness al retornar y enlaza el padre con
SAME_THREAD_NESTED_CALL mediante una L y2 extremos. Son **7 cargos distintos**
(Q19/Q35/Q37), incluso con resultados iguales o replay. Snapshot retorna entre
ambos boundaries y no sustituye esos cargos. Los selectores están activos para
todos los tests contribuyentes.

Además, cada uno de los321 frames exige al menos una S key al comenzar (Q19),
una membresía de TEST_RESULT exitoso (Q24) y la unidad constante de stop (Q15).
El guard118 no suprime begin ni ese resultado, como demostró I96. Estas963
unidades son distintas de los cargos por comandos:

`R ≥ (136×14 +113×6)×7 +321×3 =19.037 >16.384`, exceso mínimo2653.

## Alcance de la prueba

La hipótesis es completar321 PASS con observación válida, mismas fuentes,
bindings, MRO y contabilidad. No se presupone que tal ejecución haya ocurrido.
Se revisaron las llamadas retenidas sin asignaciones a ready/prepare ni
short-circuit condicional; los bucles contados no tienen break/return que
reduzca sus iteraciones. Ningún continue omite una llamada retenida. phase_args
y phase llaman al helper antes de sus retornos. df26/dr29 quedan sin aporte
por sus Try omitidos. El extractor restringido no es un analizador general de
Python: los árboles y las anclas permiten revisar los fragmentos concretos.

Try/while/callbacks, despacho desconocido y demás términos no demostrados se
omiten como costes no negativos de este piso. **UNKNOWN no se convierte en
coste real0, N/A ni dispensa de evidencia.** Los owners, declaraciones, oráculos,
mensajes, otros comandos y muchos cargos de contexto aún aumentan la demanda.

I92 sigue inválido,13/321 observados, primer diagnóstico REFERENCE_BUDGET y
contador16393. Esta deducción no identifica su primer wrapper fallido ni convierte
PASS aislados en captura completa o recuperación integrada.

## Decisión que permite esta evidencia

El perfil actual no admite P01 completo con16384 refs. Aún no existe una cota
superior completa que justifique otra cifra. No se cambia la cuota a19037 ni
se crea un certificado de admisión, perfil, autoridad o destino funcional.
Continúa la revisión documental de [recursos pendientes](D5-I97-RESOURCE-BOUND-REGISTER.md).
Una implementación o campaña nueva, IR03 y publicación requieren sus decisiones.

P0;83 SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial. D1–D4 cerrados e I1–I20/A52
aceptado. D5/H07/G01–G07 y GI33/34/38/39/40 globales abiertos. Sin proveedores,
credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue
ni D6. Sin inferir fsync, persistencia o recuperación integrada de esta aritmética.
