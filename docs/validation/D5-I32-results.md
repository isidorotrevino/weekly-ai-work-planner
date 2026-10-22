# D5 I32 — resultados de perfiles y cuotas sintéticas

Fecha: 2026-10-22. Base publicada: `8e90a87`.
[Laboratorio](../design/D5-I32-PROFILES-QUOTAS-LAB.md) ·
[Contrato aprobado I31](../design/D5-I31-PROFILES-QUOTAS-DESIGN.md) ·
[Informe verificable](D5-I32-results.json).
**PASS de modelo en memoria; G01–G07 y D5 global abiertos.**

D5-A75 aprueba I31 y autoriza PQ01–PQ34 con fixtures en memoria y parsers existentes
sin cambios, conservando A72–A74. Sin SQL, HTTP, cambios D3, efectos persistentes
D2, consumo/reservas, proveedores reales, activación, promoción, despliegue o D6.

## Campaña ejecutada

`python3 -m testing.D5.run_eligibility_lab`, Linux/Python **3.14.4**, biblioteca estándar:

| Grupo | Tests distintos | Fallos / errores / omisiones |
|---|---:|---|
| I32 perfiles/cuotas PQ01–PQ34 | 38 | 0 / 0 / 0 |
| I30 relaciones/lotes de fixture | 38 | 0 / 0 / 0 |
| I28 conciliación Plane de fixture | 41 | 0 / 0 / 0 |
| I26 captura incremental de fixture | 30 | 0 / 0 / 0 |
| I24 integración offline | 35 | 0 / 0 / 0 |
| Python local anterior | 51 | 0 / 0 / 0 |
| Total de esta campaña | **233** | **0 / 0 / 0** |

Las 34 filas de matriz no se suman como tests adicionales. El JSON mapea los 38
nuevos a esas filas e identifica los 233 IDs distintos. Las 195 regresiones se
reejecutaron ahora; no son cifras copiadas de I30. No se reejecutan SQL/D2/D3/D4.
El elapsed es observación de campaña, no benchmark.

`python3 -m testing.D5.demo_profiles_quotas` evalúa dos dimensiones de una cuenta
sintética, revisa fuente/evaluación por separado y muestra resultado positivo.
Tras caducidad, replay conserva el resultado antiguo con etiqueta histórica y
otro comando devuelve BLOCKED. Se registran dos recibos, cero consumo/reservas y
ninguna solicitud remota; no se imprime texto fuente ni datos completos de cuenta.

## Comportamiento observado

- PQ01–PQ07: mismos bytes/proyección interna bajo nuevo perfil o política producen
  otra captura/preview/manifiesto y exigen revisión propia. Descriptor/decoder
  desconocido conserva bytes bloqueados, sin ejecutar rutas. Historial de mappings
  permanece intacto y no se adopta por UUID o documento+ID entre perfiles. Revocar/
  restaurar selección no revive generación vieja; checklist no adquiere ID estable.
- PQ08–PQ18: todas las restricciones de política deben satisfacerse con observaciones
  seleccionadas de una cuenta/scope exactos. No se agregan cuentas, unidades o
  ventanas. Faltantes, costes inválidos, estados desconocidos/cero/ilimitado declarado,
  observación futura/caducada y pérdida de horizonte bloquean. Se ejercitan bordes
  de ventana y caducidad distintos. Dos lectores positivos conservan los mismos
  hechos/saldos, sin reserva. Las instrucciones reales insertadas en el texto de
  fixture no cambian política, proveedor, permisos o fallback.
- PQ19–PQ25: manifiesto fija adaptador, IDs/hashes, generaciones y vector completo;
  SOURCE no sustituye EVALUATION. Otro ID de observación con valores iguales deja
  obsoleto el paquete; cambios/revocaciones de adaptador/capacidad/permiso también.
  Otro release o payload incompleto bloquea. Publicar una observación más reciente
  sin seleccionarla no sustituye la anterior. Aprobar/consultar no cambia hechos.
- PQ26–PQ30: un hilo detenido tras lectura detecta publicación de hechos antes del
  CAS; cambios de perfil/política y revocación o reemplazo de EVALUATION en ese punto
  tampoco confirman un resultado antiguo. Avanzar reloj durante validación produce
  BLOCKED sin cambiar generación. Replay después de caducidad queda histórico;
  pérdida de respuesta tras confirmar recupera solo ese recibo. Otro request con
  el mismo command_id bloquea, sin alterar el anterior.
- PQ31–PQ34: shapes/tipos/IDs/secret fields no admitidos se rechazan y los recibos
  públicos evitan texto crudo. Otro laboratorio no hereda hechos/recibos/revisiones
  ni prueba recuperación durable. Resúmenes registran cero autoridad operativa.

Se alcanzan **16 perfiles**, **16 cuentas**, **16 restricciones por política**,
**128 observaciones** y **128 recibos**; el siguiente bloquea y replay sigue
recuperable al límite. Fuente >2 MiB y etiqueta de 257 caracteres se rechazan.
El límite configurado de manifiesto es 1 MiB; su rechazo se ejercita con presupuesto
reducido a un byte. No se presenta como prueba a tamaño completo o benchmark.

Los **tres hilos nuevos** terminan. I32 no crea raíces de datos o hijos de proceso.
Las regresiones terminan **diez hilos I28/I30**, eliminan **33 raíces I26** y dejan
**cero hijos propios vivos** de siete iniciados: tres normales y cuatro SIGKILL
controlados. El filesystem/reinicio pertenece a I26; no al modelo de cuotas I32.
Dev/run_data/D4 reales no se inspeccionan ni borran.

## Preservación y alcance

Entre archivos anteriores solo se amplían índice y guía D5. Se comprueban los
demás archivos de la base, 245 entradas de cierres D3/D4, canónico D4 y 560 entradas
históricas D5 I4–I20. I21–I31 y aceptación local conservan sus bytes; sus inputs se
verifican en el commit original si índices/guías han evolucionado. Los hashes del
parser/código real son inputs de esta campaña, separados del hash de interfaz
fixture del decoder. Enlaces, diff y patrones de publicación comprobados; el
escaneo de patrones no es una garantía universal de ausencia de secretos/defectos.

GI04/GI20/GI22 tienen evidencia acotada de **modelo**: 30/35 S con evidencia,
cinco S y siete R pendientes. No se acredita formato Gentle-AI nuevo, permisos o
cuotas comerciales reales, elegibilidad/reservas D3, SQL o durabilidad. GI33/GI34/
GI38/GI39/GI40 integrados y G01–G07 globales siguen abiertos. El hito aceptado
D5-LOCAL-SYNTHETIC-I1-I20 conserva su aceptación/perímetro exactos.
