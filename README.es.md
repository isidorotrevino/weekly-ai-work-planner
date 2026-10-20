# Weekly AI Work Planner

**Orquestación de ingeniería asistida por IA, consciente de la capacidad y las dependencias entre proyectos.**

[English](README.md) · Español

Weekly AI Work Planner explora cómo convertir planes de ingeniería en sesiones breves y trazables de trabajo con IA, respetando límites de recursos, dependencias, incidentes y aprobaciones humanas.

**Estado actual: diseño técnico, prototipo PostgreSQL y núcleo inicial de planificación Java 21.** La arquitectura funcional (D1) está aprobada. El diseño de dominio (D2) está aprobado y cerrado tras su validación. Todavía no hay una aplicación de planificación, una flota de workers ni una interfaz web ejecutables.

## Qué problema aborda

Coordinar varias herramientas de IA y varios proyectos exige decidir qué ejecutar, con qué recurso, qué dependencias bloquean el trabajo y cómo recuperar una operación interrumpida después de cambiar un sistema externo.

El diseño propone:

- **Capacidad por recurso:** ventanas de cuota, reservas, consumo, confianza y reparto inicial 70% planificación / 20% incidentes / 10% incertidumbre.
- **Trabajo consciente de dependencias:** tareas y capabilities entre proyectos, compatibilidad verificada de versión/entorno y prioridad heredada solo por los caminos bloqueantes.
- **Sesiones breves:** context packs versionados, espacios de trabajo aislados, intentos acotados, evidencia y checkpoints.
- **Ejecución recuperable:** leases, fencing, comandos idempotentes, eventos transaccionales y reconciliación antes de repetir un efecto externo incierto.
- **Gobierno humano:** aprobación de acciones sensibles, historia inmutable y ningún cambio automático a APIs comerciales de pago.

Las entradas previstas son planes Markdown de Gentle-AI y documentos de negocio/técnicos sincronizados con herramientas como Google Drive y Plane. Los parsers y adaptadores reales son trabajo futuro.

## Qué se puede ejecutar hoy

El repositorio incluye migraciones PostgreSQL, propuestas de contratos de persistencia y una batería Java/JUnit. Comprueba contabilidad de capacidad, relaciones, concurrencia, estados, recuperación y procedencia con **datos sintéticos y adaptadores simulados**.

La ejecución registrada del **17 de octubre de 2026** completó **157 comprobaciones sin fallos, errores ni omisiones**, con PostgreSQL 16.15 y Java 21. La batería incluye 29.829 vectores de conformidad SemVer/npm dentro de una prueba JUnit. Algunas pruebas históricas reproducen deliberadamente huecos de versiones anteriores. Consulta el [resumen de validación](docs/validation/README.md) para conocer el alcance y los límites.

### Probar el núcleo de planificación

El módulo [scheduler-core](scheduler-core/README.md) calcula propuestas deterministas sobre snapshots sintéticos, sin ejecutar operaciones ni publicar planes. Ejecuta `bash testing/D3/run-core-tests.sh` con Java 21/Maven, o `bash testing/D3/run-core-docker-tests.sh`. Consulta el [estado D3](docs/design/D3-IMPLEMENTATION.md) y su [evidencia JUnit](docs/validation/D3-I1-results.json). El [adaptador PostgreSQL](scheduler-postgres/README.md) ya añade snapshots inmutables y publicación transaccional y [despacho protegido](docs/design/D3-I3-DISPATCH.md). Su suite aislada se ejecuta con `bash testing/D3/run-postgres-tests.sh`.

El [coordinador durable invocable](docs/design/D3-COORDINATOR.md) agrupa eventos, persiste barridos y publica con fencing y recálculos acotados. No hay worker, daemon ni servicio desplegado.

La [revisión integrada D3](docs/design/D3-REVIEW.md) corrige reaperturas críticas en V15 y registra mediciones acotadas. Se aceptó el alcance conservador 1A; la [optimización 2A](docs/design/D3-OPTIMIZATION.md) completa la fixture de 1.000 operaciones con presupuesto de 30 s. D3 está [aprobado y cerrado como MVP conservador](docs/design/D3-approved.md), sin despliegue aprobado.

### Ejecutar la auditoría

Requisitos: Bash, daemon Docker operativo y acceso a los registros de imágenes y Maven Central. Docker debe poder acceder al repositorio mediante bind mount. Java y Maven se ejecutan dentro del contenedor de pruebas.

```bash
git clone https://github.com/isidorotrevino/weekly-ai-work-planner.git
cd weekly-ai-work-planner
bash testing/D2/run-docker-audit.sh
```

El ejecutor crea seis bases desechables en un contenedor PostgreSQL temporal, ejecuta Flyway/JUnit y elimina sus contenedores y red al terminar. No publica puertos del host. Guarda logs, metadatos y reportes en `work/docker-audit/`, excluido de Git. Utiliza la batería únicamente con datos de prueba desechables.

La [guía de auditoría](testing/D2/README.md) explica la alternativa con PostgreSQL local y cómo seleccionar otras imágenes.

## Arquitectura propuesta

```mermaid
flowchart LR
    Plans[Planes Markdown y documentos] --> Control[Control plane Java / Spring Boot]
    Control <--> DB[(PostgreSQL)]
    Control <--> Workers[Workers de ejecución distribuidos]
    Control <--> Integrations[Adaptadores deterministas]
    UI[Administración Angular] --> Control
```

El diagrama representa el sistema previsto. El prototipo actual valida contratos de persistencia PostgreSQL; no inicia esos servicios.

| Componente | Tecnología prevista |
|---|---|
| Control plane | Java 21+ / Spring Boot, monolito modular |
| Estado y cola transaccional | PostgreSQL, Flyway, leases y polling HTTPS |
| Recursos de ejecución | Workers CLI/modelo con presupuestos independientes |
| Administración | Angular, en una fase posterior |
| Integración | Adaptadores deterministas y versionados, con detección de conflictos |

El MVP propuesto no requiere Kafka, Temporal ni Kubernetes. Los worktrees aíslan cambios; no son sandboxes de seguridad.

## Organización del repositorio

```text
.
├── README.md / README.es.md    Presentación en inglés y español
├── docs/
│   ├── design/                Diseños D1 y D2 aprobados
│   │   └── history/           Iteraciones anteriores
│   ├── validation/            Cobertura, límites y resultados portables
│   └── archive/sql-markdown/  Mirrors históricos de V1–V4
├── migrations/                SQL V1–V4 preservado
├── migrations-proposed/       Correcciones y contratos V5–V11 en borrador
├── scheduler-core/            Java 21 planning core / Núcleo Java 21
├── scheduler-postgres/        JDBC snapshot and publication adapter / Adaptador JDBC
├── migrations-d3-proposed/    I2 V12 isolated proposal / Propuesta I2 aislada
├── migrations-d3-dispatch-proposed/  I3 V13 dispatch / Despacho
├── migrations-d3-coordinator-proposed/  V14 callable coordination / Coordinación
├── testing/D2/                Batería Java/JUnit y ejecutores
├── scripts/                   Comprobaciones previas a publicación
└── .github/                   Plantillas de issues y pull requests
```

Los adjuntos originales, notas de continuidad, evidencia bruta, credenciales, cachés y archivos de bases de datos se conservan localmente, excluidos de Git.

### Por dónde empezar

1. [Índice de documentación](docs/README.md).
2. [Arquitectura aprobada — D1](docs/design/D1-architecture-baseline.md).
3. [Diseño aprobado de D2](docs/design/D2.9-approved.md).
4. [Matriz de validación](docs/validation/D2-VALIDATION-MATRIX.md) y [resultados portables](docs/validation/latest-results.json).

Las migraciones originales V1–V4 y las propuestas V5–V11 se mantienen separadas. La aprobación del diseño no promueve estas propuestas a migraciones de producción; sigue siendo necesaria una revisión previa al despliegue.

## Hoja de ruta

| Etapa | Alcance | Estado |
|---|---|---|
| D1 | Arquitectura funcional | Aprobada |
| D2 | Dominio y contratos PostgreSQL | Aprobado y cerrado; prototipo de validación |
| D3 | Planificación consciente de capacidad | Aprobado y cerrado; MVP conservador 1.0, bibliotecas/SQL validados |
| D4 | Protocolo de workers y laboratorio de recuperación sintética | En curso; revisión abierta |
| D5 | Ingestión e integraciones | Prevista |
| D6 | Gobierno y operación | Prevista |

## Contribuciones y seguridad

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) antes de proponer cambios y [SECURITY.md](SECURITY.md) antes de compartir información de diagnóstico.

Antes de preparar un commit, ejecuta:

```bash
python3 scripts/check-publication.py
```

La comprobación revisa archivos versionados y no ignorados para detectar patrones habituales de credenciales, rutas privadas y artefactos generados. Es una protección ligera, no un escáner exhaustivo de secretos. Revisa también el diff preparado: `.gitignore` no protege archivos que Git ya versiona.

## Licencia

Este proyecto utiliza la **GNU General Public License, versión 3 exclusivamente** (`GPL-3.0-only`). Consulta [LICENSE](LICENSE), [NOTICE](NOTICE) y la [guía bilingüe de licencia](LICENSING.md).

Puedes usarlo, modificarlo y redistribuirlo, también comercialmente. Al distribuir una versión modificada cubierta por la GPL, debe conservarse esa licencia y proporcionarse el código fuente correspondiente según sus condiciones. Se permiten modificaciones privadas que no se distribuyan; GPLv3 no incorpora la obligación de ofrecer fuentes por uso en red propia de AGPL.

Las atribuciones de terceros se conservan en [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

[D4 I4: laboratorio Compose integrado](docs/design/D4-I4-LAB.md) y [evidencia propia](docs/validation/D4-I4-results.json). D4 sigue abierto; sin despliegue ni migraciones promovidas.

[D4 I6: renovación y checkpoint cooperativo](docs/design/D4-I6-LONG-RUNNING-LAB.md):
nueve escenarios sintéticos y [resultados separados](docs/validation/D4-I6-results.json).
D4 permanece abierto; alcance acotado, sin proveedores reales.

[D4 I7: polling normal y retirada verificada](docs/design/D4-I7-POLLING-LAB.md),
con [doce escenarios registrados](docs/validation/D4-I7-results.json).
