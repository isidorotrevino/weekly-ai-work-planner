# D5 I34 — laboratorio TASK durable sintético

Fecha: **2026-10-23**, Europe/Madrid. Implementa el alcance T del
[contrato I33-F](D5-I33-DURABLE-INTEGRATION-DESIGN.md) y
[matriz DF01–DF48](D5-I33-DURABLE-INTEGRATION-REVIEW.md), con las 33 obligaciones
UI de base aplicables. [Resultados](../validation/D5-I34-results.md) ·
[Informe JSON](../validation/D5-I34-results.json).
**D5 global y G01–G07 abiertos; A52/I1–I20 sin ampliación.**

English: bounded new durable synthetic TASK authority on Linux local filesystem,
with separate I26 capture, CLIENT state and REMOTE fixture effects. Explicit
reviews, atomic local effects/receipts, pre-send durable tickets and explicit
reconciliation. No real provider, D2 SQL writes, consumption/reservations or activation.

## Autoridad, historial y publicación

El usuario eligió P0 + A (diseño integrado), F (completar contrato durable) y después
**A: aprobar contrato y autorizar implementar/validar TASK Markdown durable, las 33
obligaciones UI aplicables y DF01–DF48, con regresiones Python separadas**.
La aprobación incluye módulos/runner nuevos, filesystem temporal propio e hijos
propios para crash/reinicio; no publicación, proveedores/credenciales reales,
consumo/reservas, activación, promoción, despliegue ni D6.

El diseño aprobado se conserva con su estado histórico PREPARED_FOR_REVIEW y sus
inputs en el commit local `4158282`. Su texto anterior a la aprobación no revoca
esta decisión; el registro presente establece la implementación posterior.
I32 `7b64d87`, handoff `79c696a`, diseño I33 e implementación I34 siguen sin
autorización de publicación. No usar push de HEAD por una autorización futura
limitada a otro SHA. D1–D4 cerrados y el hito D5-LOCAL-SYNTHETIC-I1-I20 aceptado
conservan sus hashes/targets y perímetros. No se crea un cierre global D5.

## Ejecutar y reproducir

Desde la raíz, Linux/Python 3 con biblioteca estándar y filesystem local que admita
fsync/rename/flock; no requiere Docker, PostgreSQL, red o credenciales:

```bash
python3 -m testing.D5.demo_durable_integration
python3 -m unittest testing.D5.test_durable_integration -v
python3 -m testing.D5.run_durable_lab
```

La demo crea un evento Markdown sintético y revisiones propias, confirma un intento
CLIENT sin respuesta, ejecuta el doble en un hijo, abre otro cliente y concilia
explícitamente en otro proceso. Muestra UNKNOWN → EFFECT_CONFIRMED; después de
revocar la revisión de proyección muestra STALE sin restaurar el efecto anterior.
Imprime solo estados/contadores/IDs de fixture. El runner emite JSON saneado a stdout;
no guarda por sí mismo informes ni acepta rutas/URL/.env/corpus del operador.

## Componentes y autoridad

- [`durable_store.py`](../../source_ingest/durable_store.py): esquema cerrado,
  cadena de objetos SHA-256, HEAD, flock exclusivo, protocolo de commit y replay.
- [`durable_task_fixture.py`](../../source_ingest/durable_task_fixture.py): reducer
  CLIENT/REMOTE nuevo, importación verificada I26, revisiones/efecto/intentos y
  conciliación. El estado no pertenece a MemoryLab/EligibilityLab/ReconciliationLab.
- [`durable_support.py`](../../testing/D5/durable_support.py): harness confiable,
  control por pipes/barreras, spawn y lector independiente de archivos.
- [`test_durable_integration.py`](../../testing/D5/test_durable_integration.py): 48
  tests distintos con subcasos de crash/CAS/negativos; filas UI/DF no se suman como tests.

No se modifican parsers o módulos/harness históricos. Se reutiliza el parser y
validadores públicos de descriptores/políticas/observaciones I32; no atributos
privados, pickle o replay de ACCEPT para restaurar objetos volátiles. SOURCE,
EVALUATION, EFFECT y PROJECTION son revisiones del namespace durable nuevo.
Comparaciones con modelos I24/I28/I32 son acotadas, no equivalencia completa.

## Commit, fallo y recuperación

Cada CLIENT/REMOTE valida identidad/rol, JSON canónico, hashes/cadena y transición
pura cerrada desde génesis. No ejecuta comandos de documentos o imports dinámicos.
Efecto local confirma TASK BACKLOG, mapping, base/procedencia, generación y recibo
en una sola raíz. Una cabeza posterior conserva recibos anteriores; command_id con
otro request bloquea. Campos ajenos, snapshot completo y ABA impiden sobrescritura
por una copia obsoleta. Perfil nuevo requiere captura/revisión propias; evaluación
exige vector completo vigente de una cuenta, sin agregar ventanas/unidades/cuentas.

El commit escribe/fsync objeto, lo publica sin reemplazo, fsync objects, escribe/
fsync HEAD temporal, replace y fsync directorio. Antes de HEAD no hay confirmación;
después de replace sin fsync confirmado hay COMMIT_UNKNOWN y handle bloqueado hasta
reapertura. Un proceso nuevo valida cabeza visible y cadena y fsync antes de afirmar
recibo. Huérfanos no se promueven; corrupción no selecciona padre ni crea génesis.
No reparación automática, migración, compactación o GC.

CLIENT emite un ticket UNKNOWN **durable antes de llamar al doble** y libera lock.
Revocar antes bloquea; después de emisión conserva incertidumbre/hecho histórico y
vigencia STALE. Reabrir no envía, consulta, cierra o reintenta automáticamente.
REMOTE confirma atómicamente entidad/índice único/ticket/prueba; UPDATE exige versión
y base remota exactas y conserva campos ajenos. Una respuesta perdida no elimina
el efecto: el otro almacén y el ticket sobreviven al cliente.

Lookup vacío deja UNKNOWN. `settle_or_close` es capacidad nueva **solo de fixture**:
si no existe ticket, confirma CLOSED_NO_EFFECT y rechaza llegada tardía; si existe,
devuelve su prueba. Execute frente a cierre se serializa en REMOTE, sin locks CLIENT
anidados. No demuestra CAS, unicidad, cancelación o recuperación de Plane real.
NO_EFFECT concluyente permite retry explícito bajo guardas/presupuesto originales;
identidad incompatible produce CONFLICT persistente. Ni lectura/replay/positivo de
cuota crea capacidad, reserva, permiso de ejecución o autoridad actual.

El reloj lógico se persiste y solo avanza por comando explícito del harness.
Reinicio no lo renueva: simular tiempo durante parada requiere avanzar tick antes
de evaluar/aplicar/enviar. No hay frescura comercial basada en el tiempo real.

## Recursos, límites y ajustes de implementación

I26 crea su raíz temporal independiente mediante `TemporaryFixtureLab` público;
CLIENT/REMOTE viven bajo la raíz propia del harness. Es el ajuste respecto al layout
capture/client/remote en una misma carpeta propuesto en I33: no se mueve I26 ni se
usan inicializadores privados para forzar ese layout. La evidencia cuenta dos raíces
superiores propias por escenario (harness e I26), además de sus subalmacenes.

La API del doble es una llamada local síncrona a su almacén independiente; el
harness ejecuta operaciones en procesos spawn nuevos para probar reinicio y matar
CLIENT o REMOTE en puntos controlados. No hay proceso servidor, red ni aislamiento
de seguridad entre roles. La supervivencia que se acredita es de estado filesystem
separado, no de un proveedor externo o servicio permanente.

Cada run_id del harness contiene un único escenario T (dentro del límite de ocho);
la batería agrega múltiples instancias independientes para los casos parametrizados,
sin compartir identidad/estado ni sumarlas como tests nuevos. Mantiene límites
I33-F y los inferiores de componentes. Antes de emitir se conserva
margen lógico para resultados de todos los intentos/consultas pendientes (commits,
slots de recibos y bytes de prueba); otras mutaciones no pueden agotarlo. No son
reservas de cuota/capacidad D3. Los ensayos de historia, catálogos y margen usan
límites reducidos y se identifican así; no acreditan capacidad máxima o rendimiento.
La fuente >2 MiB se rechaza con el límite completo. El informe detalla lo ejercitado.

Limpieza valida marca/IDs/inodos, rechaza symlinks, termina únicamente hijos propios
y conserva sentinel hermano hasta retirar los almacenes. Regresiones I26 crean sus
propias raíces/hijos y se contabilizan aparte. Nada inspecciona ni elimina dev,
run_data, D4 o evidencia ajena. Datos/inspecciones íntegros contienen texto privado
de fixture; no publicar directorios temporales ni logs crudos.

## Alcance de la evidencia

Los resultados acreditan únicamente T sintético y sus fallos/reinicios locales bajo
el modelo Linux descrito. R relacional y exportaciones Docs no corrieron, ni SQL/
D2/D3/D4 o validación real. GI33/GI34/GI38/GI39/GI40 reciben evidencia acotada de este
recorrido; no se convierten automáticamente en criterios globales completos.
D5 y G01–G07 siguen abiertos, con los siete criterios R pendientes. Las campañas
históricas y la cuenta anterior 30/35 no se suman para declarar 35/35.

Sin pérdida de energía/disco defectuoso/NFS/Windows, aislamiento de caller Python
hostil, attestación del host o garantía exactly-once externa. Escaneo de publicación
y hashes no son auditoría exhaustiva de secretos/defectos. Publicación requiere
la autorización separada del SHA concreto de implementación.
