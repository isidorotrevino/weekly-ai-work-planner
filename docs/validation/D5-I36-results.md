# D5 I36 — resultados de integración relacional durable R

Fecha: **2026-10-23**, Europe/Madrid. Base de diseño: `aee8b21`.
[Laboratorio](../design/D5-I36-DURABLE-RELATIONAL-LAB.md) ·
[Contrato I35](../design/D5-I35-DURABLE-RELATIONAL-DESIGN.md) ·
[JSON verificable](D5-I36-results.json).
**PASS acotado de fixture R; D5 global/G01–G07 abiertos. Sin publicación autorizada.**

El usuario aprobó I35 y autorizó implementar/validar R, DR01–DR40 y UI25/UI34 con
regresiones Python separadas. P0 sigue vigente; D1–D4 y A52/I1–I20 conservados.

## Campaña final

`python3 -m testing.D5.run_relational_durable_lab`, Linux/Python **3.14.4**,
biblioteca estándar, sin Docker/SQL, SDK/CLI/proveedores o credenciales reales:

| Grupo | Tests distintos | Fallos / errores / omisiones |
|---|---:|---|
| I36 R, DR01–DR40 | 40 | 0 / 0 / 0 |
| I34 T durable | 48 | 0 / 0 / 0 |
| I32 perfiles/cuotas | 38 | 0 / 0 / 0 |
| I30 lotes volátiles | 38 | 0 / 0 / 0 |
| I28 conciliación | 41 | 0 / 0 / 0 |
| I26 incremental | 30 | 0 / 0 / 0 |
| I24 offline | 35 | 0 / 0 / 0 |
| Python local anterior | 51 | 0 / 0 / 0 |
| Total | **321** | **0 / 0 / 0** |

40 nuevas + 281 regresiones reejecutadas en esta campaña final. UI/DR/DF, subcasos,
crashes, aserciones y ejecuciones de desarrollo no se suman como tests distintos.
El JSON lista los 321 IDs y mapas DR/UI→tests. SQL/D2/D3/D4 no se reejecutaron.

## Evidencia observada

- Bytes JSON originales conservados, incluso con espaciado distinto. Captura no
  selecciona/acepta; SOURCE liga generación explícita y ABA no revive paquetes.
- Lote confirma entidades, vínculos, mappings, bases, procedencia y recibo juntos.
  Positivos/negativos del grafo completo, endpoints, guardas de trabajo/estado,
  edición local y no-op comparados por API pública con I30; sin restaurar privados.
- La procedencia de cada modelo referencia su catálogo. Solo el hash de manifiesto
  propio del schema se normaliza al comparar; las demás evidencias/datos coinciden
  en los casos contrastados. No afirma equivalencia total o SQL/D2.
- Selección exige TASK participante de recibo aplicado exacto. Requisito/épica,
  UUID ajeno o manifiesto sin recibo no producen proyección. Description null/empty
  preservada, EPIC description solo evidencia, workflow/claims no se ejecutan.
- Cada TASK requiere PROJECTION propia. Un cambio local/relacional o lote no-op
  invalida el contexto de proyecto completo aunque title/description no cambien.
  A confirmada/B UNKNOWN conserva vector por TASK y lote local aplicado, sin rollback
  o atomicidad distribuida. El oráculo usa UUID explícitos, no orden de diccionarios.
- Ticket UNKNOWN durable antes de enviar, resultado/prueba REMOTE atómicos,
  respuesta perdida conciliable en proceso nuevo y lookup vacío sin prueba de ausencia.
  Cierre frente a execute, dos lotes y respuesta frente a consulta usan CAS y procesos.
- Nuevo lote local puede aplicar conservando ticket previo UNKNOWN/STALE; ese binding
  no admite otro envío hasta conciliar. Confirmada creación antigua, CREATE preparado
  antes queda STALE_DESTINATION y se exige nuevo UPDATE/base/revisión.
- Precondición remota/ABA rechazada no permite retry del paquete viejo. Prueba con
  run/store/ticket/key/hash incompatible deja CONFLICT persistente. Reinicio no
  envía/consulta/cierra/reintenta automáticamente ni renueva el reloj lógico.

Se registran **221 observaciones** de lector independiente (archivos/hash/cadena/
HEAD/estado/conteos), y **43 ejercicios kill_at** con rol/operación/failpoint/
exitcode/HEAD antes-después. La muerte del dueño de flock con otro escritor preparado
se comprueba adicionalmente. No se atribuye a un punto no instrumentado.

La campaña R creó **141 raíces propias**, un escenario por run_id con CLIENT/
REMOTE debajo. Los **86 hijos nuevos** terminaron: 42 normales y
**44 SIGKILL** controlados. Cero raíces/hijos R restantes; sentinel y limpieza
selectiva comprobados. Regresión T: **310 raíces** y
**149 hijos**, todos retirados/terminados. Regresión I26:
**33 raíces** y **7 hijos**,
todos retirados/terminados. Las regresiones terminaron **13 hilos** I28/I30/I32.
No se inspeccionó/paró/borró dev/run_data/D4 o evidencia ajena.

La demo muestra lote aplicado, vector EFFECT_CONFIRMED/UNKNOWN, efecto en otro
proceso todavía desconocido por CLIENT y conciliación explícita que confirma la
segunda TASK. Cuatro entidades/cuatro relaciones locales y dos TASK remotas de
fixture; cero operaciones/intentos operativos, consumo/reservas, activación y llamadas
reales. El estado/inspect íntegro es privado; reportes/demo evitan texto/paths privados.

## Límites y exclusiones

Se agotaron tres intentos y seis consultas. Historia/catálogos/planner y margen de
resultados se prueban con presupuestos reducidos declarados: comandos 2, historia 3,
commit 4 KiB, almacén 16 KiB y margen pendiente con commit 64 KiB/almacén 2 MiB.
Fuente >2 MiB se rechaza en la frontera de captura antes de parsear. No campaña de
todos los máximos de catálogo/4 MiB de manifiesto/32 MiB de commit/256 MiB de almacén
ni benchmark. Los límites inferiores se aplican sin truncar o resetear presupuesto.

Kernel I34 y laboratorios históricos intactos; nueva autoridad/esquemas R. La
fachada pública de llamadas locales no es servicio remoto real. Cierre de ticket
es capacidad inventada del doble; no demuestra CAS/unicidad/permisos Plane reales.
Reloj lógico explícito, no frescura comercial; sin prueba de pérdida de energía,
disco fallido, NFS/Windows, caller hostil, attestation o exactly-once externo.

UI25/UI34 reciben evidencia propia de unión R durable en este alcance. GI33/GI34/
GI38/GI39/GI40 conservan revisión global pendiente; no cerrar G01–G07 ni declarar
35/35 por sumar I30/T/R PASS. Docs y siete criterios reales siguen pendientes.
Sin SQL/D2 persistente, proveedores/credenciales reales, consumo/reservas, activación,
promoción, despliegue, D6 o ampliación A52. Sin publicación autorizada.

## Integridad documental

Se conservan los archivos de la base salvo índice y guía D5. Verificados 186
hashes ejecutables de cierres D3/D4, canónico D4 y aceptación local. I34: 73 inputs
runtime actuales y 73+7 históricos en su commit; I35: 90 inputs en su commit. No
reescribir informes por cambios de índices. Inputs ejecutados/documentales separados
en el JSON; los informes históricos no validan automáticamente código futuro.

```bash
python3 - <<'PYVERIFY'
import hashlib, json
from pathlib import Path
r = json.loads(Path('docs/validation/D5-I36-results.json').read_text())
for group in ('inputs', 'documentary_inputs'):
    for path, expected in r[group].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected, path
print('Inputs de campaña y documentación verificados')
PYVERIFY
```

Después de cambios posteriores, consultar bytes de índice/guía en el commit de
este informe y contrastar código actual por separado. Escaneo configurado y hashes
no son revisión exhaustiva de seguridad/corrección.
