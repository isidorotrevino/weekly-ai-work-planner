# D4 I6 — ejecución prolongada y checkpoint cooperativo

Estado: opciones A/A aprobadas expresamente por el usuario, registradas como
[A10/A11](D4-DECISIONS.md); **D4 abierto**. [Implementación acotada](D4-I6-LONG-RUNNING-LAB.md)
y [resultados propios](../validation/D4-I6-results.json) disponibles, sin atribuir
aprobación al conjunto D4.

## Contrato conservado

Se reutilizan la identidad D2 completa, HEARTBEAT de lease, `/lab/grant`, el receptor
durable y las guardas I5. PRESENCE acredita elegibilidad; no renueva ejecución.
Solo la respuesta autenticada del control plane y la instalación confirmada del
grant en el receptor permiten extender la autoridad local. Una respuesta perdida
no autoriza extenderla. Cada renovación reintenta el mismo command_id y contenido;
la siguiente renovación usa otro ID. Ninguna espera HTTPS mantiene mutex SQL.

Un watchdog independiente de HTTP y de la espera del subproceso solicita parada
del grupo al perder autoridad. TERM y KILL mantienen los límites del supervisor;
una parada no confirmada conserva UNKNOWN. Ni matar el proceso ni vencer la lease
liberan reservas, exclusión o prueban ABSENT. El verificador debe observar la parada
y cerrar el receptor antes de cualquier transición que retire el compromiso.

El presupuesto local se calcula desde el inicio monotónico de la petición y se
acota por la duración firmada del grant; una respuesta tardía consume presupuesto.
También se comprueba su vencimiento UTC. No se convierte la fecha remota en una
garantía sobre relojes arbitrariamente desalineados. El laboratorio usa el reloj
del mismo host; sincronización y operación entre máquinas quedan para D6.

## Decisiones propuestas

**R1 — fallo de renovación, elegida A.** A: iniciar parada ante el primer ciclo
de renovación que no obtiene confirmación del control plane y del receptor, tras
un reintento acotado con el mismo ID; conservar el watchdog del último grant como
límite adicional. B: tolerar fallos y seguir hasta un margen de seguridad anterior
al último vencimiento confirmado. B mejora disponibilidad pero amplía la carrera
entre proceso vivo, renovación incierta y vencimiento; exige fijar y probar el
margen. Un rechazo de identidad, generación o autorización detiene en ambas.

**R2 — cooperación, elegida A.** A: consultar la solicitud de checkpoint durante
la ejecución y comunicarla a la fixture por un canal local fijo, ligado al intento.
La fixture termina el paso seguro, escribe el candidato y sale; el verificador
comprueba artefacto, parada y sello. Seguir renovando hasta la parada y el sellado;
COMMIT solo con lease viva, como A09. Si no coopera dentro del límite, parar y
mantener bloqueo para reconciliación, sin fabricar un checkpoint. B: solo aceptar
solicitudes en un punto seguro ya alcanzado; si está ejecutando, devolver DEFERRED
sin interrumpirlo. B es más simple y deja la preempción durante proceso pendiente.

Ambas opciones conservan autorización explícita de continuidad, mismo contador,
misma reserva, TOP_UP original, mapping y cuentas congelados. No amplían la ruta
desde RECONCILING ni resuelven contradicciones.

## Corte ejecutable propuesto tras decidir

1. Proceso de duración superior a 60 s con renovaciones reales D2/HTTPS, efecto y
   aceptación independiente; comprobar que no cambia intento ni generación.
2. Pérdida de comunicación durante renovación, parada observada externamente y
   compromiso retenido hasta la reconciliación; grant viejo rechazado al vencer.
3. Solicitud mientras el proceso sigue vivo, checkpoint parcial sellado y
   continuación I5; no emitir el sufijo antes de autorizar el nuevo intento.

S02/S04 conservan su fallo deliberado de proceso superviviente. La nueva ejecución
normal no debe ocultar esa inyección ni convertir la batería SQL existente en una
afirmación de validación Compose. Mantener S01–S05 como regresión separada.

La base del supervisor añade espera de salida sin señal y parada explícita. El
timeout de observación solo informa que el proceso sigue vivo: no escribe EXITED,
no libera el lock y no equivale a prueba de parada. La espera no toma el monitor
usado al finalizar, de modo que el watchdog puede detener mientras otro hilo espera.
