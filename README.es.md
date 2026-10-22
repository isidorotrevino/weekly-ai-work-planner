# Weekly AI Work Planner

**Planifica sesiones breves de ingeniería con IA según la capacidad, las dependencias y las decisiones humanas.**

[English](README.md) · Español

Cuando varios proyectos comparten herramientas de IA, decidir qué ejecutar a
continuación es solo parte del problema. También hace falta conocer la capacidad
disponible, entender los bloqueos y recuperar una sesión que se interrumpe después
de realizar un cambio.

Este proyecto explora ese flujo para desarrolladores y equipos que construyen
automatización de ingeniería. Mantiene cuentas físicas separadas por recurso,
parte de un reparto 70% planificación / 20% incidentes / 10% incertidumbre,
prioriza las dependencias bloqueantes y registra intentos, aprobaciones y evidencia
de recuperación.

## Pruébalo en local

El entorno de desarrollo ejecuta una **fixture sintética**, con PostgreSQL, un
control plane HTTPS Java, dos workers, un receptor de efectos y un verificador
independiente. No hay interfaz web de producción ni conexión con proveedores reales
de IA.

En Linux con Docker Engine, Compose, Python 3, Bash y OpenSSL, desde la raíz del
repositorio:

```bash
cp .env.example .env
python3 dev/dev.py build
python3 dev/dev.py up
python3 dev/dev.py smoke
```

El primer build descarga imágenes fijadas y dependencias Maven. Java 21 y Maven se
ejecutan dentro de Docker. Los endpoints HTTPS escuchan solo en `127.0.0.1`; los
puertos se configuran en `.env`. El smoke ejecuta una operación sintética y la
verifica de forma independiente. Repetirlo comprueba el resultado conservado sin
volver a consumir capacidad.

```bash
python3 dev/dev.py status
python3 dev/dev.py logs --service worker-a
python3 dev/dev.py stop
```

Los datos permanecen en `run_data/local/`; `up` recupera esa sesión. Un worker con
historia local exige recuperación explícita tras reiniciarse. Las identidades
sintéticas caducan a las 48 horas; el reset selectivo explícito permite crear una
fixture nueva. Consulta la [guía de desarrollo](docs/DEVELOPMENT.md) para acceder
por HTTPS, reconstruir servicios, gestionar persistencia, reset y problemas comunes.

## Qué funciona hoy

- Bibliotecas de planificación Java 21 y contratos de persistencia PostgreSQL.
- Workers HTTPS sintéticos, fencing, checkpoints, verificación independiente y
  rutas explícitas de recuperación.
- Una entrada de desarrollo local persistente, separada de las baterías SQL
  desechables y del laboratorio de validación D4.

D1–D4 están **aprobados y cerrados dentro de su alcance registrado**. Sus diseños,
manifiestos y evidencias históricas se conservan en el [índice documental](docs/README.md)
y el [resumen de validación](docs/validation/README.md). El
[manifiesto de cierre D4](docs/validation/D4-CLOSURE.json) delimita el alcance
sintético. El [laboratorio D5](testing/D5/README.md) permite previsualizar fuentes, importar
tareas BACKLOG con revisión y resolver conflictos, sin activar tareas. La [auditoría de alcance](docs/design/D5-I21-SCOPE-AUDIT.md)
separa esta base local de las integraciones D5 pendientes; D5 sigue abierto.
Gobierno y operación (D6) siguen pendientes.
El desarrollo local no promueve propuestas SQL ni autoriza despliegues.

## Explorar y contribuir

Empieza por la [guía técnica de desarrollo](docs/DEVELOPMENT.md), y continúa con la
[arquitectura aprobada](docs/design/D1-architecture-baseline.md) y el
[núcleo de planificación](scheduler-core/README.md). La guía también enlaza los
runners independientes de SQL y D4.

Lee [CONTRIBUTING.md](CONTRIBUTING.md) y [SECURITY.md](SECURITY.md) antes de compartir
cambios o diagnósticos. Antes de preparar archivos para Git, ejecuta
`python3 scripts/check-publication.py` y revisa el diff. Los datos generados, las
identidades privadas y los logs brutos quedan fuera de Git.

Licencia **GPL-3.0-only**: [LICENSE](LICENSE), [NOTICE](NOTICE),
[guía de licencias](LICENSING.md) y [avisos de terceros](THIRD-PARTY-NOTICES.md).
