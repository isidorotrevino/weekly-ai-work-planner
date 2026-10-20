# Handoff para iniciar D3 — Weekly AI Work Planner

Fecha: 2026-10-18. Idioma de trabajo: español; código e identificadores técnicos en inglés.

## 1. Misión de la nueva sesión

Diseñar **D3: planificador de capacidad**, apoyado en D1 y D2 aprobados. El primer entregable es un **borrador técnico D3 v0.1**, con contratos de entrada/salida, algoritmo propuesto, decisiones pendientes y plan de validación sintética.

Este handoff prepara la continuidad. No significa que D3 esté diseñado o aprobado. Mantener el alcance en diseño y prototipos acotados de validación; solicitar aprobación expresa antes de cerrar D3 o iniciar la implementación completa.

## 2. Estado confirmado al entregar

| Elemento | Estado |
|---|---|
| D1 | Arquitectura funcional v1.0 aprobada; preservada sin cambios |
| D2 | Diseño final v1.0 aprobado y cerrado el 2026-10-17 |
| Evidencia D2 | 157 pruebas JUnit en Docker; cero fallos, errores u omisiones |
| SemVer | 29.829 vectores contrastados con npm/node-semver 7.7.2, sin discrepancias; incluidos dentro de una prueba JUnit |
| Entorno probado | PostgreSQL 16.15, Java 21, Flyway 13.10.3 |
| Migraciones | V1–V4 originales; V5–V11 en `migrations-proposed/`, sin promoción automática a producción |
| Aplicación | Prototipo SQL/JUnit; todavía no hay aplicación Spring Boot, scheduler completo, workers ni interfaz Angular |
| D3 | Próxima etapa; sin borrador ni decisiones específicas aprobadas al crear este handoff |

El usuario aprobó el cierre de D2 condicionado a una validación satisfactoria: «validalo y si es exitoso apruebo el cierre de D2». La condición se cumplió; **no volver a pedir aprobación de D2** ni tratarlo como borrador abierto.

Repositorio público: [isidorotrevino/weekly-ai-work-planner](https://github.com/isidorotrevino/weekly-ai-work-planner).

Último commit de cierre D2 publicado y verificado: `69d71c3877e79bdfef088956b090d4eb6b447be9`, rama `main`. Es la referencia de cierre, no una afirmación sobre futuros HEAD. Al comenzar, inspeccionar el estado Git y preservar cambios locales posteriores.

Licencia: **GPL-3.0-only**; conservar los avisos de terceros.

## 3. Lectura y autoridad documental

Leer primero, en este orden:

1. [README en español](README.es.md) e [índice documental](docs/README.md).
2. [D1 aprobado](docs/design/D1-architecture-baseline.md).
3. [D2 aprobado — consolidación final](docs/design/D2.9-approved.md).
4. [Registro de decisiones y cierre D2](docs/design/D2-DECISIONS.md).
5. [Matriz de validación D2](docs/validation/D2-VALIDATION-MATRIX.md), [resultados registrados](docs/validation/latest-results.json) y [evidencia con hashes](docs/validation/semver-evidence.json).
6. [Informe SemVer](docs/design/D2-SEMVER-VALIDATION.md).
7. SQL de `migrations/` y `migrations-proposed/`, especialmente V7–V11, y [guía de auditoría](testing/D2/README.md).

D1 y el D2 final prevalecen sobre los borradores anteriores. Los documentos de `docs/design/history/` y la revisión D2.8 conservan contexto histórico; sus frases «D2 abierto» describen otro momento. Consultarlos cuando haga falta rastrear una decisión, sin reabrir el cierre por una frase obsoleta.

Los documentos de `docs/internal/`, adjuntos y reportes brutos son locales y están ignorados. No son necesarios para iniciar D3 ni deben publicarse. No modificar D1, D2 aprobado o migraciones históricas para resolver silenciosamente una discrepancia: documentarla y presentar una propuesta de cambio explícita.

## 4. Políticas aprobadas que D3 debe respetar

- Horizonte semanal móvil; replanificación ante incidentes, cambios de capacidad, prioridad y dependencias.
- **70% PLANNED / 20% INCIDENT / 10% UNCERTAINTY por recurso**. No sumar cuotas entre proveedores, recursos o unidades distintas.
- Proyectos P0/P1/P2/P3/P4 con pesos iniciales **8/4/2/1/0**. P4 pausado para asignación planificada por defecto. El peso orienta un reparto proporcional entre trabajo elegible, no garantiza cuota ni sustituye los filtros de seguridad.
- Equidad, participación mínima y prevención de inanición configurables; la fórmula y sus límites concretos pertenecen a D3 y aún requieren diseño.
- Herencia de prioridad solo por el camino que bloquea trabajo de mayor prioridad; no elevar todo un proyecto productor ni cambiar su prioridad base.
- Dependencias HARD, SOFT, MOCKABLE y OPTIONAL. Desbloqueo mediante la tarea/capability pertinente; no esperar a que termine todo el proyecto proveedor.
- Capabilities compatibles por versión y entorno, AVAILABLE y con evidencia vigente. MOCKABLE permite desarrollo con mocks, pero exige integración real compatible para completar.
- Incidentes SEV1/SEV2 disparan replanificación inmediata. La preempción requiere checkpoint seguro; el trabajo no interrumpible se aplaza conforme al contrato existente, sin matar procesos desde SQL.
- La reserva de incidentes solo se presta a trabajo interrumpible con checkpoint verificable, sin demanda crítica observada. UNCERTAINTY no se presta.
- Los aplazamientos conservan motivo e historia; considerar deadlines y dependencias críticas.
- Autonomía por defecto, con las aprobaciones exigidas por política. No eludir una aprobación para mejorar utilización o cumplir una fecha.

Recursos previstos: laptop con Claude Pro; PC con Claude Max 20x; PC con Codex/ChatGPT Business Standard; servidor Gemma4:31B vía LiteLLM. Sus nombres describen la arquitectura aprobada, no verificaciones actuales de productos o cuotas. Las capacidades comerciales y la ejecución desatendida siguen pendientes de comprobación real.

No inventar cuotas de tokens, interpretar «20x» como rendimiento exacto ni habilitar fallback automático a APIs comerciales de pago. Una cuota desconocida bloquea admisión; no significa capacidad ilimitada.

## 5. Contratos de D2 que condicionan el planificador

### Capacidad y reservas

- Las cuentas físicas se identifican por recurso, dimensión y ventana real; se comparten entre versiones del plan. Replanificar no crea capacidad.
- Ventanas de sesión y semana pueden limitar simultáneamente una operación. La semana del calendario no demuestra un reset del proveedor.
- El diario es inmutable; el disponible se reconstruye como límite efectivo menos compromiso pendiente y consumo reconocido. El consumo real y los déficits no se borran para hacer encajar un plan.
- Una reserva pertenece a una operación y permanece estable entre planes. El CLAIM ejecutable comprueba las cuentas y crea la reserva de manera transaccional.
- D3 debe distinguir asignación tentativa de planificación y compromiso físico efectivo. Publicar un plan no puede duplicar las reservas que ya existen ni contabilizar dos veces una futura reserva al CLAIM.
- Estimación, observación, confianza y calibración versionada son datos diferentes. OPERATIONS, SECONDS, TOKENS y CALIBRATED_QUOTA son dimensiones separadas; no convertirlas sin una calibración explícita.

### Planes y concurrencia

- Un plan nace DRAFT. Publicado, congela configuración, presupuestos, asignaciones, slots, prioridades, razones, aplazamientos y enlaces según las guardas D2.
- Sustituir un plan requiere sucesor PUBLISHED explícito. No editar retroactivamente un snapshot publicado.
- El mutex global conservador está aprobado para el MVP; no mantener locks durante llamadas externas. El mutex de publicación se adquiere antes de locks de filas.
- D3 debe diseñar cálculo, validación final y publicación frente a cambios concurrentes: un plan calculado sobre datos obsoletos no autoriza por sí solo un claim inseguro.
- Las guardas de ejecución permanecen vigentes aunque el plan haya considerado elegible una operación antes.

### Recuperación y evidencia

- Expirar un lease conduce a RECONCILING y conserva compromisos. Un efecto externo UNKNOWN bloquea sin reintentar ni liberar capacidad a ciegas.
- BLOCKED_APPROVAL→RECONCILING requiere evidencia nueva y concluyente; la transición no ejecuta de nuevo el efecto.
- Tres intentos totales por defecto, configurable entre 1 y 20, solo con evidencia de reintento seguro. Replanificar no reinicia el contador.
- SemVer 2.0.0 y rangos npm ya están validados en V11, con límites operativos documentados. Reutilizar su contrato; no crear un intérprete divergente en el scheduler.
- Igual precedencia de versiones no permite compartir evidencia entre artefactos/builds, entornos, hashes o generaciones distintos.

## 6. Trabajo de D3, en orden

1. **Inventario de interfaz:** mapear las entradas necesarias del scheduler a entidades, vistas y entrypoints D2. Identificar datos derivados, observados y todavía no disponibles.
2. **Contrato de planificación:** definir solicitud, snapshot de entrada, reloj/zona horaria, horizonte, versión de política/calibración y resultado. Preservar razones, confianza, trabajo no asignado y aplazamientos.
3. **Filtros de elegibilidad:** dependencias, estados, evidencia, aprobaciones, disponibilidad técnica, ventanas y capacidad. Diferenciar bloqueo, aplazamiento y falta de información.
4. **Algoritmo MVP:** proponer una estrategia determinista y explicable, con pseudocódigo, desempates estables y complejidad. Comparar alternativas solo cuando afecten a decisiones reales; no introducir un solver externo sin justificar su necesidad.
5. **Reparto y puntuación:** concretar pesos, equidad, antigüedad, deadlines y prioridad heredada. Separar restricciones duras de preferencias y explicitar qué sucede cuando son incompatibles.
6. **Replanificación:** diseñar eventos, coalescencia, estabilidad del plan, reservas/leases existentes, incidentes y solicitudes de checkpoint; documentar consistencia con publicación y CLAIM.
7. **Validación sintética:** escenarios y propiedades de seguridad, determinismo y equidad; usar un prototipo acotado si aporta evidencia sin construir la plataforma completa.
8. **Revisión:** entregar D3 v0.1 con propuestas claramente diferenciadas de lo aprobado. Preguntar al usuario solo decisiones materiales todavía pendientes, con recomendación y consecuencias.

Decisiones de D3 que deben concretarse, sin presentarlas como aprobadas: significado operativo de fechas límite; ventanas del horizonte y zona horaria; límites de antigüedad/equidad; tratamiento de estimaciones poco fiables; selección entre recursos elegibles; criterios de replanificación y estabilidad; objetivos y límites de rendimiento del MVP.

No pedir credenciales ni muestras reales de Gentle-AI para empezar el diseño sintético del scheduler. Los parsers y APIs reales corresponden a D5; pedir datos adicionales cuando sean necesarios para un contrato concreto.

## 7. Validación esperada y límites

Proponer al menos escenarios de: múltiples proyectos y recursos; cuotas desconocidas o simultáneas; sobreconsumo/recalibración; replanificación sin cuota duplicada; incidentes durante préstamos; operación no interrumpible; camino crítico entre proyectos; invalidación de capability; P4 y trabajo aplazado; riesgo de inanición; deadlines incompatibles; publicación concurrente y determinismo de desempates.

La suite D2 está disponible con:

```bash
bash testing/D2/run-docker-audit.sh
```

Usa seis bases desechables, no publica puertos y conserva evidencia local ignorada. Docker funcionó en la sesión de cierre, incluido `hello-world`; comprobar su disponibilidad en una sesión nueva antes de atribuirle nuevas ejecuciones. No repetir toda D2 solo por leer el handoff o editar prosa; ejecutar las regresiones pertinentes cuando cambien entradas ejecutables o aparezca una preocupación concreta.

Las 157 pruebas registradas incluyen caracterización de huecos históricos V4/V5; no equivalen a 157 garantías de producción. La evidencia usa datos sintéticos y efectos simulados. Cuotas reales, workers/CLI, proveedores, APIs, permisos de despliegue y política operativa de retención conservan validación posterior D3–D6 según el reparto aprobado.

## 8. Entregables y disciplina del repositorio

Crear como mínimo:

- `docs/design/D3-capacity-scheduler-draft.md`: D3 v0.1, contratos, pseudocódigo, invariantes, escenarios y decisiones abiertas.
- `docs/design/D3-DECISIONS.md`: propuestas, respuestas explícitas y estado de aprobación; no inventar decisiones del usuario.
- Enlace en `docs/README.md`. Si se ejecutan pruebas nuevas, conservar un resumen portable separado de la evidencia histórica D2.

Mantener Java 21+/Spring Boot y PostgreSQL como arquitectura aprobada, Angular para administración posterior y polling HTTPS para workers. No introducir Kafka, Temporal o Kubernetes por defecto. Los workers no reciben credenciales SQL; worktrees no son sandboxes de seguridad.

Preservar D1, D2 aprobado y V1–V11. Proponer cambios de contrato por separado si D3 descubre una necesidad real. No promover migraciones ni desplegar servicios al producir el borrador. No cerrar D3 sin aprobación explícita.

Antes de publicar cambios, revisar el diff y ejecutar:

```bash
python3 scripts/check-publication.py
```

Conservar `.gitignore`, GPL-3.0-only y avisos de terceros. No versionar credenciales, adjuntos privados, conversaciones, datos reales ni evidencia bruta. Verificar permisos GitHub vigentes cuando haga falta publicar; no solicitar tokens en el chat.

## 9. Prompt para pegar en la sesión nueva

> Lee HANDOFF-D3.md y los documentos que indica. D1 y D2 están aprobados; D2 está cerrado y su referencia publicada es el commit 69d71c3. Inicia el diseño técnico de D3 y prepara D3 v0.1 para el planificador de capacidad. Primero identifica los contratos que ya ofrece D2 y las decisiones específicas de planificación que faltan; después desarrolla entradas/salidas, algoritmo explicable y escenarios de validación sintética. Respeta cuentas físicas, reservas compartidas entre planes, reparto 70/20/10 por recurso, dependencias y prioridad heredada por camino bloqueante. Pregúntame las decisiones materiales pendientes con propuestas concretas. Mantén el alcance en diseño y validación acotada; no inicies la implementación completa ni cierres D3 sin mi aprobación. Responde en español.
