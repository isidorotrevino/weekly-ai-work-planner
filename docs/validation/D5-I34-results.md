# D5 I34 — resultados TASK durable sintética

Fecha: **2026-10-23**, Europe/Madrid. Base de diseño local: `4158282`.
[Laboratorio](../design/D5-I34-DURABLE-TASK-LAB.md) ·
[Contrato I33-F](../design/D5-I33-DURABLE-INTEGRATION-DESIGN.md) ·
[JSON verificable](D5-I34-results.json).
**PASS acotado T; D5 global y G01–G07 abiertos. Sin publicación autorizada.**

El usuario aprobó el contrato y autorizó implementar/validar T durable, las 33
obligaciones UI aplicables y DF01–DF48 con regresiones Python separadas. P0 conserva
I32, handoff, diseño e implementación sin publicar. No amplía A52/I1–I20 ni D1–D4.

## Campaña final registrada

`python3 -m testing.D5.run_durable_lab`, Linux/Python **3.14.4**, biblioteca estándar:

| Grupo | Tests distintos | Fallos / errores / omisiones |
|---|---:|---|
| I34 durable, DF01–DF48 | 48 | 0 / 0 / 0 |
| I32 perfiles/cuotas | 38 | 0 / 0 / 0 |
| I30 relaciones/lotes | 38 | 0 / 0 / 0 |
| I28 conciliación | 41 | 0 / 0 / 0 |
| I26 captura incremental | 30 | 0 / 0 / 0 |
| I24 offline | 35 | 0 / 0 / 0 |
| Python local anterior | 51 | 0 / 0 / 0 |
| Total | **281** | **0 / 0 / 0** |

48 nuevas + 233 regresiones efectivamente reejecutadas en esta campaña final.
UI/DF, subcasos, reinicios y ejecuciones de desarrollo previas no se suman como
pruebas distintas. El JSON lista los 281 IDs únicos y los mapas DF/UI→tests. No
se reejecutaron SQL/D2/D3/D4 ni se sumaron campañas históricas.

## Resultados y oráculos

- Fuente/pin I26 exactos; perfil explícito y SOURCE/EVALUATION/EFFECT/PROJECTION
  independientes. Duplicados, ámbito/hash incompatibles, formato desconocido,
  revisión sustituida, ABA y caducidad bloquean sin efecto posterior.
- Efecto local confirma TASK/mapping/base/procedencia/recibo juntos. Los fallos
  parametrizados antes/después de HEAD no dejan prefijos; replay devuelve historia
  y otro request bajo el mismo comando bloquea sin restaurar una cabeza anterior.
- Intento UNKNOWN confirmado antes de envío. Caída del cliente no borra el efecto
  REMOTE; proceso nuevo concilia explícitamente. Lookup vacío conserva UNKNOWN.
  Cierre atómico de ticket compite con execute y frena llegadas tardías sin efecto.
- CREATE único, UPDATE con base/version/hash exactos y campos ajenos preservados.
  Edición ABA remota rechaza el paquete; rechazo de precondición no permite retry
  del paquete viejo. Nuevo contenido/base requiere paquete/revisión nuevos.
- Respuesta frente a consulta, cierre frente a execute y escritores CLIENT desde
  la misma HEAD compiten en procesos distintos. CAS preserva conflictos y no elige
  ganador por fecha. Un escritor preparado progresa tras morir el dueño del flock.
- Comparación acotada con APIs públicas I24/I28/I32: proyección, elegibilidad,
  caducidad negativa, UNKNOWN/conciliación/replay y rechazo de base remota. La
  durabilidad y settle_or_close son capacidades nuevas del modelo, no paridad total.

Se registran **254 observaciones del lector independiente** (JSON/hash/cadena/
HEAD/conteos), con hashes de estado y HEAD. Los 70 ejercicios de
kill_at detallan rol, operación, failpoint, exitcode y HEAD anterior/posterior.
Las muertes adicionales de inicialización y dueño de lock se comprueban en sus
casos; no se atribuyen a un punto no instrumentado en el JSON.

La campaña creó **310 raíces superiores propias**: harness e I26 por cada
run_id independiente de un escenario T. CLIENT/REMOTE son subalmacenes. Los
**149 hijos nuevos** terminaron: 77 normales y **72 SIGKILL**
controlados. Cero raíces/hijos nuevos restantes. Las regresiones eliminaron sus
**33 raíces I26**, terminaron sus siete hijos (cuatro SIGKILL) y **13 hilos** I28/
I30/I32. Nuevos y regresiones se cuentan por separado; dev/run_data/D4 no se tocaron.

La demo registrada muestra UNKNOWN → EFFECT_CONFIRMED por conciliación en proceso
nuevo, una entidad remota de fixture y STALE después de revocar PROJECTION. Cero
operaciones/intentos operativos, consumo/reservas, autoridad de ejecución y peticiones
reales. La limpieza propia queda comprobada; no imprime texto fuente o rutas privadas.

## Límites y exclusiones

Historia/catálogos/margen se ejercitan con presupuestos reducidos identificados:
commit 4 KiB, almacén 16 KiB, margen pendiente con commit 64 KiB/almacén 2 MiB;
se rechaza antes de emitir cuando no cabe el resultado. También tres intentos y
seis consultas agotados. El rechazo de fuente >2 MiB se prueba en la frontera del
reducer con límite completo; **no es campaña end-to-end de capacidad máxima**.
No afirmar capacidad 32 MiB/256 MiB o rendimiento de todos los catálogos por esos PASS.

El helper público I26 crea una raíz separada del harness (ajuste de layout) y el
doble usa llamadas locales sobre filesystem independiente; los procesos spawn de
prueba no son un servicio remoto permanente. Reinicio conserva el reloj lógico:
representar tiempo transcurrido exige avance explícito. Sin prueba de energía/disco
fallido/NFS/Windows, aislamiento de caller hostil o exactly-once externo.

R relacional y Docs no corrieron; tampoco proveedores, credenciales o capacidades
reales de Plane/Drive/cuotas. GI33/GI34/GI38/GI39/GI40 tienen evidencia **acotada T**
y permanecen pendientes a escala global. Se conserva la cuenta anterior 30/35;
no se convierte en 35/35 por sumar PASS aislados. Los siete R y G01–G07 siguen
abiertos; sin aceptación global, promoción, despliegue ni D6.

## Preservación y reproducción documental

Se preservan los archivos de la base de diseño salvo índice y guía D5. Se verifican
186 hashes ejecutables de los cierres D3/D4, canónico D4, aceptación local,
84 inputs históricos I32 y 90 inputs I33 en sus commits, sin reescribir informes.
Los inputs ejecutados y documentales finales están separados en el JSON. La
comprobación de publicación y enlaces no es garantía exhaustiva de seguridad.

Para verificar los inputs de esta campaña sin ejecutar de nuevo pruebas:

```bash
python3 - <<'PYVERIFY'
import hashlib, json
from pathlib import Path
r = json.loads(Path('docs/validation/D5-I34-results.json').read_text())
for group in ('inputs', 'documentary_inputs'):
    for path, expected in r[group].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected, path
print('Inputs de campaña y documentación verificados')
PYVERIFY
```

Después de cambios de índices/guías, verificar sus bytes en el commit de este
informe y contrastar el código actual por separado. Un informe histórico válido
no acredita automáticamente inputs ejecutables posteriores.
