# D3 scheduler core — I1

Estado vigente: [D3 aprobado y cerrado como MVP conservador 1.0](../docs/design/D3-approved.md) por «si, cierra D3». Las notas anteriores de cierre pendiente son históricas; no hay despliegue aprobado.
Primer incremento Java 21 del diseño D3 v0.2 aprobado. Biblioteca pura para integrar posteriormente en el control plane Spring Boot. No arranca servicios ni accede a SQL/proveedores. Licencia GPL-3.0-only; JUnit es dependencia exclusiva de pruebas.

## Uso y contrato

Construir un `PlanningModel.Request` con reloj fijo, zona, versiones de política/calibración y límites explícitos; suministrar `Snapshot` inmutable y llamar a `new CapacityScheduler().plan(request, snapshot)`. Las fixtures de `CapacitySchedulerTest` ofrecen ejemplos ejecutables. El resultado incluye disposición por operación, prioridades/ruta, slot, delta incremental, saldos virtuales y alternativas descartadas. `reviewOnly` siempre es true: el resultado no autoriza publicación ni CLAIM.

El adaptador futuro debe obtener de D2 elegibilidad, correspondencia exacta de aprobación/contexto y compatibilidad/evidencia. El núcleo no implementa SemVer ni considera suficiente un booleano generado por un worker sin confianza. `activeHardEdges` contiene exclusivamente aristas HARD activamente bloqueantes del contrato D2; `incidents` contiene incidentes abiertos; disponibilidad y exclusiones deben incluir todos los recursos afectados. Para trabajo activo se exige reserva y duración restante; si esta falta, se ocupa el resto del horizonte conservadoramente.

Todas las cuentas físicas vinculantes del recurso/slot deben aparecer en la estimación. Compromisos físicos deben estar completamente atribuidos a reservas; si falta uno se rechaza el snapshot. El diario y los saldos D2 son la fuente de verdad. Los consumos históricos sin atribución se conservan, con diagnóstico `FAIRNESS_HISTORY_INCOMPLETE`; no representan una garantía de equidad histórica. La apertura persistente y explícita de épocas corresponde a I2.

Se aplica 70/20/10 mediante los límites/saldos físicos importados: no se recalcula saldo desde cuotas de calendario ni se suman unidades/proveedores. Las vías 5%/20% se comprueban por cuenta, con uso anterior suministrado en `laneUsage`. Los retries conservan la vía de gasto de su reserva: no pueden eludir el cupo original cambiando de vía. Un snapshot que omita uso de vía ya acreditado por sus reservas se rechaza. El núcleo no crea préstamos, no libera reservas ni automatiza continuación desde checkpoint.

`ReplanPolicy` calcula lotes, deduplicación, cambios que rompen protección, barrido de 60 s y límite de dos recálculos. No consume/acuse eventos ni mantiene temporizadores. Su función de espera elegible une intervalos observados para no contar duplicados ni intervalos bloqueados.

## Ejecutar pruebas

Java 21 y Maven:

```bash
bash testing/D3/run-core-tests.sh
```

Desde la raíz, alternativa Docker con Maven/Java 21:

```bash
bash testing/D3/run-core-docker-tests.sh
```

La primera ejecución necesita Maven Central y la imagen de Maven. Para reutilizar una caché disponible, definir `D3_MAVEN_CACHE`; `D3_OFFLINE=1` impide red en el contenedor y requiere imagen/dependencias ya disponibles. Ambos runners eliminan únicamente `scheduler-core/target` antes de ejecutar para evitar evidencia obsoleta. No levantan PostgreSQL ni publican puertos.

Tras pruebas satisfactorias, el resumen portable se obtiene con:

```bash
bash testing/D3/run-postgres-tests.sh
python3 scripts/summarize-d3-postgres.py > docs/validation/D3-OPTIMIZATION-results.json
```

## Límites de esta entrega

- I2 (snapshot SQL, hechos de equidad, publicación CAS y concurrencia PostgreSQL) ya tiene un [adaptador separado](../scheduler-postgres/README.md). I3 (despacho/mapping+CLAIM/roles) ya tiene un [adaptador protegido](../docs/design/D3-I3-DISPATCH.md). No existe aún un servicio de aplicación.
- Solo se asigna trabajo actualmente elegible. Los consumidores HARD siguen bloqueados hasta evidencia real, sin slots CONDITIONAL pronosticados en esta entrega.
- La propagación de fechas usa duraciones conservadoras mínimas por alternativa como cota inferior y no demuestra viabilidad de deadlines bajo contención. Duraciones desconocidas producen riesgo UNKNOWN, no cero.
- Hay mediciones sintéticas acotadas; no hay SLA, cuotas reales ni proceso de integración real ejecutado. Las metas numéricas se aplazaron por 6B. El cierre D3 requiere aprobación expresa posterior.

Detalles y cobertura: [estado de implementación](../docs/design/D3-IMPLEMENTATION.md).

La [optimización 2A](../docs/design/D3-OPTIMIZATION.md) conserva la fuente previa exacta como recurso de prueba y compara el resultado completo en 82 escenarios. El informe I1 y su exportador describen aquella entrega histórica; no sobrescribir sus resultados para exportar el núcleo actual. El alcance conservador sin CONDITIONAL está aceptado por 1A.
