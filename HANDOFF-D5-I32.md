# Handoff — continuar D5 después de I32

Fecha: **2026-10-23**, Europe/Madrid. Estado: I32 implementado/validado y guardado
localmente; publicación pendiente. **D5 global y G01–G07 siguen abiertos.**

English: continuation handoff after synthetic I32. Preserve all approved historical
milestones/evidence. I32 has 233 passing Python tests, is committed locally, and
has no publication authorization yet. Next global integration work requires a
concrete contract/review decision; no live providers, activation or deployment.

## Primeros pasos en la nueva sesión

1. Inspeccionar instrucciones locales, árbol, rama, cambios y remoto. Conservar
   cambios ajenos; no resetear ni asumir que este archivo describe el HEAD futuro.
2. Leer este handoff, [índice](docs/README.md), [I32](docs/design/D5-I32-PROFILES-QUOTAS-LAB.md)
   y sus [resultados](docs/validation/D5-I32-results.md) / [JSON](docs/validation/D5-I32-results.json).
3. Revisar el [hito local aceptado](docs/design/D5-LOCAL-SYNTHETIC-approved.md), su
   [registro](docs/validation/D5-LOCAL-SYNTHETIC-ACCEPTANCE.json) y el contrato/matriz
   [I23](docs/design/D5-I23-GLOBAL-INTEGRATION-DESIGN.md) /
   [42 criterios](docs/design/D5-I23-GLOBAL-INTEGRATION-REVIEW.md).
4. Presentar la publicación pendiente con commit concreto. No publicar I32 ni este
   handoff hasta obtener autorización específica. Continuar después con decisiones
   materiales del siguiente corte; no deducir implementación de una aprobación de diseño.

## Git y autorizaciones exactas al emitir el handoff

Repositorio: `https://github.com/isidorotrevino/weekly-ai-work-planner`, rama `main`.

| Referencia | SHA completo | Estado observado |
|---|---|---|
| I31, contrato perfiles/cuotas | `8e90a87cce7edbefc6c854a73ff1f60a20ae8485` | Autorizado y publicado; main remoto verificado el 2026-10-23 |
| I32, implementación/perfiles/cuotas | `7b64d87ef45b4973a5ea80dc676f1bd2eca220f7` | Commit local validado; **sin autorización de publicación** |

La autorización del usuario cubrió expresamente publicar I31 y aprobar/implementar
I32. No cubre publicar I32 ni commits posteriores. La petición actual autoriza
crear este handoff para otra sesión, no publicar o iniciar otra función. El commit
que guarde el handoff se consulta con `git log`; no introducir un hash autorreferente.
Si se autoriza publicar solo I32 y HEAD incluye este handoff u otros commits, usar
el SHA exacto autorizado como origen del push, no `git push` de todo HEAD.

```bash
git status --short
git log -4 --oneline
git remote get-url origin
git ls-remote origin refs/heads/main
```

No crear un chat nuevo automáticamente: el usuario pidió un documento de handoff.

## Límites permanentes

- D1–D4 aprobados/cerrados. Conservar código, SQL, targets, manifiestos y evidencia;
  [D3](docs/design/D3-approved.md) / [cierre](docs/validation/D3-CLOSURE.json) y
  [D4](docs/design/D4-approved.md) / [cierre](docs/validation/D4-CLOSURE.json).
- A52 acepta exclusivamente `D5-LOCAL-SYNTHETIC-I1-I20`, base ejecutable
  `d20f375f3eb45213d0d759f0530c056dd5ac251b`. No es cierre global D5 ni autorización
  de ampliación. No crear D5-approved/D5-CLOSURE globales por completar fixtures.
- Sin proveedores/credenciales reales, corpus privado publicado, activación,
  promoción de migraciones, despliegue o ampliación implícita D6.
- D3 conserva cuentas por recurso/dimensión/ventana, reservas compartidas, mappings
  congelados, 70/20/10 y retries por delta. Una evaluación positiva no concede
  capacidad, reservas, CLAIM o permiso de ejecución.
- Dev, baterías SQL y D4 están separados. El entorno dev ya existe: ver
  [guía](docs/DEVELOPMENT.md). No borrar run_data, proyectos Compose o evidencia
  ajenos; los laboratorios nuevos solo limpian recursos que ellos mismos crean.
- Decisiones materiales en español con opciones concretas. El flujo acordado es
  contrato/matriz → aprobación de contrato y alcance de implementación → ejecución
  y evidencia → autorización de publicación del commit concreto. No repetir
  permisos ya concedidos para el mismo acto ni inventar permisos futuros.

## Qué contiene I32 y qué se validó

A75 aprueba [I31](docs/design/D5-I31-PROFILES-QUOTAS-DESIGN.md) y
[PQ01–PQ34](docs/design/D5-I31-PROFILES-QUOTAS-REVIEW.md), solo en memoria, con
parsers existentes intactos. Reglas materiales heredadas:

- A73: otro perfil/política exige captura, preview y revisión nuevos. Conservar
  correspondencias originales; no convertirlas ni reutilizarlas automáticamente.
- A74: todas las restricciones necesarias vigentes de una cuenta/ámbito; no sumar
  cuentas/ventanas/unidades. Cambio o revocación exige evaluación/revisión nuevas.
- Fuente y evaluación tienen revisiones independientes y versiones CAS. Selección
  de perfil/observación explícita; fecha reciente no decide autoridad. ABA no revive
  generaciones anteriores. Caducidad/horizonte se revalidan al confirmar.

Código nuevo: [eligibility_fixture.py](source_ingest/eligibility_fixture.py).
`EligibilityLab` registra descriptores, selección de perfil, capturas, fixtures de
mappings históricos, cuentas/adaptadores, política y observaciones inmutables.
`prepare_evaluation`, `review` y `validate_evaluation` fijan hashes/generaciones y
revisiones exactas. No hay HTTP/SQL/D2, consumo/reserva o tareas creadas.

El decoder es una lista cerrada de parsers existentes; versiones de descriptor son
sintéticas, no un nuevo formato Gentle-AI. El hash de interfaz de fixture no es una
atestación del código: los hashes de archivos reales están en el informe. La cuenta
de proveedor de fixture no reemplaza las cuentas D3 separadas por dimensión/ventana.

Un recibo nuevo tiene `historical=false`; replay/read_command devuelve
`historical=true`. Ambos niegan autoridad de ejecución. Un resultado histórico
positivo nunca demuestra elegibilidad actual; otro comando comprueba hechos/reloj.
Capturas, manifests e inspect_facts contienen bytes/texto íntegros y son privados;
recibos, demo y runner publican solo datos saneados. No hay aislamiento frente a
caller Python hostil ni persistencia/recuperación durable del proceso.

Campaña I32 registrada, Linux/Python 3.14.4:

| Grupo | Tests distintos |
|---|---:|
| I32 perfiles/cuotas | 38 |
| I30 lotes | 38 |
| I28 conciliación Plane de fixture | 41 |
| I26 captura incremental | 30 |
| I24 offline | 35 |
| Python local anterior | 51 |
| Total | **233** |

Cero fallos/errores/omisiones. Tres hilos nuevos y diez de regresión terminados.
I26 eliminó sus 33 raíces propias y terminó siete hijos: tres normales y cuatro
SIGKILL controlados. Esa recuperación filesystem es **regresión I26**, no persistencia
I32. SQL/D2/D3/D4 no se reejecutaron ni se suman sus cifras históricas.

Se alcanzaron 16 perfiles, 16 cuentas, 16 restricciones, 128 observaciones y 128
recibos. Fuente >2 MiB y etiqueta de 257 caracteres bloquean. El manifiesto configura
1 MiB; su rama de rechazo se probó con presupuesto reducido a un byte, no a tamaño
completo. No presentar esa prueba como campaña de capacidad o rendimiento.

```bash
python3 -m testing.D5.demo_profiles_quotas
python3 -m unittest discover -s testing/D5 -p test_profiles_quotas.py -v
python3 -m testing.D5.run_eligibility_lab
```

El runner completo reejecuta regresiones I26 que requieren Linux/fsync/flock y usan
sus propios temporales/hijos. No repetir pruebas por editar solo este handoff.

## Pendientes globales comprobados tras I32

Hay **30/35 criterios sintéticos con evidencia acotada**, cinco S pendientes y
siete R pendientes. Ninguna brecha G01–G07 está cerrada.

| Criterios pendientes | Trabajo que falta |
|---|---|
| GI33 / GI34 | Inventario integrado de código/config/perfiles/versiones/campaña e invalidación; conservación de targets/hashes y contabilidad separada de regresiones |
| GI38 / GI39 / GI40 | Evidencia integrada de fallos/reinicio/respuestas perdidas, concurrencia entre fronteras y auditoría de cero activación/limpieza selectiva |
| GI06 | Muestras representativas y script/interfaz Gentle-AI identificados y revisados; wrappers de fixture no lo acreditan |
| GI12 | Drive real, ámbito/permisos/revisión/exportación y recuperación autorizados |
| GI18 | Plane objetivo: condición atómica, correlación/creación y conflictos demostrados en versión/edición real |
| GI24 | CLI/proveedor/cuotas/permisos unattended reales con evidencia empírica autorizada |
| GI30 | Suficiencia de negocio/grooming revisada por humano sobre muestras representativas |
| GI36 | Aceptación global expresa sobre alcance y evidencia suficiente |
| GI42 | Ciclo integrado real autorizado con versiones/ámbitos y recuperación/conflictos |

La restricción vigente mantiene las pruebas reales fuera de alcance. No cambiarles
la etiqueta a sintéticas ni mover una brecha D5 a D6 para afirmar completitud.
Plane sigue bloqueado para escrituras reales hasta probar condición atómica;
GET seguido de PATCH no la sustituye. No se autoriza una pasarela Plane implícita.

**Siguiente paso recomendado para preguntar:** diseñar I33 para los cinco S
integrados, comenzando por inventario/contrato de unión y matriz. Aún no está
aprobado ese diseño ni su implementación. Concretar antes cómo conectar los dobles:
I24/I28/I30/I32 son volátiles, I26 sí conserva captura temporal entre procesos.
No se puede afirmar recuperación end-to-end por sumar sus PASS separados. Si se
propone persistencia/outbox nuevo o un laboratorio SQL, pedir decisión de alcance
antes de implementar. Mantener cronología, hashes y exclusiones de cada evidencia.

Opciones razonables para esa decisión: A) contrato integrado + matriz antes de
código (recomendada); B) primero auditoría documental de GI33/GI34, dejando la unión
funcional para otro corte. No pedir todavía permisos reales o credenciales.

## Preservación y comprobaciones documentales

I32 guarda 84 hashes de inputs. Para verificar su evidencia sellada tras modificar
un índice, consultar los bytes **en su commit**, sin reescribir el informe:

```bash
python3 - <<'PY'
import hashlib, json, subprocess
commit = '7b64d87ef45b4973a5ea80dc676f1bd2eca220f7'
report = json.loads(subprocess.check_output([
    'git', 'show', f'{commit}:docs/validation/D5-I32-results.json']))
for path, expected in report['inputs'].items():
    raw = subprocess.check_output(['git', 'show', f'{commit}:{path}'])
    assert hashlib.sha256(raw).hexdigest() == expected, path
print(len(report['inputs']), 'historical input hashes verified')
PY
python3 scripts/check-publication.py
git diff --check
```

Para trabajo ejecutable nuevo, contrastar también inputs actuales y explicar las
diferencias; solo anclar al commit no valida código modificado. Índices/README
pueden evolucionar, conservando sus hashes originales en informes históricos.
No depender de helpers de `/tmp` de la sesión anterior: no son herramientas
versionadas ni una receta durable del proyecto. No publicar logs/capturas privados.

## Prompt de continuación

> Lee HANDOFF-D5-I32.md y los documentos enlazados. Conserva D1–D4 cerrados y el
> hito D5-LOCAL-SYNTHETIC-I1-I20 aceptado; D5 global y G01–G07 siguen abiertos.
> I32 está implementado/validado en 7b64d87, pero su publicación y la del handoff
> no están autorizadas. Verifica Git y plantea la publicación concreta por separado.
> Después, pregúntame con opciones el siguiente corte para GI33/GI34/GI38/GI39/GI40,
> preparando contrato y matriz antes de implementar. No deduzcas persistencia o
> recuperación integrada de los PASS aislados. Sin proveedores/credenciales reales,
> consumo/reservas, activación, promoción, despliegue ni D6. Responde en español.
