# D4 I6 — renovación y preempción cooperativa sintéticas

Estado: implementación y validación acotada de [A10/A11](D4-DECISIONS.md);
**D4 abierto**. [Revisión y alternativas](D4-I6-LONG-RUNNING-REVIEW.md).

[Resultados I6](../validation/D4-I6-results.json): S01–S09, 283 comprobaciones;
84 pruebas D4, 175 D3 y 157 D2 sin fallos, errores ni omisiones en las ejecuciones
finales. Se conservan las ejecuciones fallidas de diagnóstico; no cuentan como PASS.
Los nueve proyectos finales terminaron sin contenedores, redes ni volúmenes propios.

Incremento posterior: [I7](D4-I7-POLLING-LAB.md) añade el bucle de polling normal.
Los resultados y límites siguientes corresponden a la campaña I6 original.

## Comportamiento

Una fixture prolongada separa mantenimiento de autoridad en un hilo virtual y
watchdog en un hilo de plataforma dedicado. Cada 10 s el mantenimiento pide `/lab/grant` con command_id
nuevo, reutilizando HEARTBEAT D2 y todas sus guardas; instala el grant firmado en
el receptor antes de publicarlo localmente. Una pérdida de respuesta de transporte
permite un reintento con el mismo ID y contenido, también para la instalación.
Un rechazo explícito termina el ciclo sin reintento. No cambia generación, mapping,
vector ni reserva. PRESENCE sigue siendo un anuncio distinto de HEARTBEAT.

El watchdog consulta cada 100 ms un presupuesto monotónico desde el inicio de la
petición, acotado por la duración firmada, y el vencimiento UTC. Reserva 10 s antes
del vencimiento para iniciar la parada; no espera una llamada HTTPS. La espera del
proceso usa `awaitExit`, que no envía señales ni retiene el monitor de finalización.
Parada explícita, captura y evento durable reutilizan el supervisor anterior,
con `ReentrantLock` para no fijar carriers mientras espera. Las dos lecturas
bloqueantes de pipes usan hilos de plataforma dedicados, limitados por la exclusión
de un proceso por workspace. Una prueba en JVM separada reproduce el bloqueo con
un solo carrier antes de la corrección y confirma dos paradas concurrentes después.
No es una garantía de tiempo real ante bloqueo del kernel, disco o scheduling.

Primer ciclo no confirmado, presupuesto agotado, cambio de binding o solicitud sin
cooperación inician TERM/KILL y conservan BLOCKED_UNKNOWN. Un efecto ya iniciado
puede preceder a la parada: solo la observación externa y el cierre serializado del
receptor permiten concluir su situación. El worker no libera compromisos ni crea
pruebas autoritativas. El callback sigue siendo candidato para el verificador.

V22 añade exclusivamente `d4.worker_checkpoint_signal(worker,delivery)` y revoca
PUBLIC. El control plane obtiene el worker del certificado y solo entrega la señal
de su delivery, intento, generación y versión RUNNING con lease viva. Lectura bajo
los mutex existentes, sin procesos ni HTTP dentro de SQL. El rol runtime solo
recibe EXECUTE; no SELECT sobre solicitudes, ni permisos de evidencia.
V1–V21 y las funciones históricas D2/D3 permanecen intactas.

Para la fixture parcial prolongada, el mantenimiento consulta la señal cada segundo
entre llamadas. El supervisor escribe por rename/fsync un archivo fijo con esquema,
identidad completa y request_id; repetir igual es idempotente y otro ID se rechaza.
La fixture comprueba el binding y sale en su frontera segura, produciendo el mismo
candidato PARTIAL que I5. No se interpretan comandos shell ni rutas remotas.
El watchdog concede 15 s de cooperación; sin candidato válido detiene y bloquea.

Tras la salida se aplica el paso sintético del prefijo bajo autoridad vigente.
CHECKPOINT_READY continúa renovando hasta que el receptor se cierre o el control
plane deje de autorizar; esa pérdida no convierte el candidato ya parado en PASS.
El verificador comprueba bytes, firma externa de parada, APPLIED/ABSENT y sello, y
COMMIT revalida lease viva. Continúan vigentes A08/A09 y el TOP_UP conservador de 10.
Si el cierre precede a un COMMIT rechazado por expiración, permanece bloqueado.

La planificación explícita de continuación puede recapturar y recalcular hasta
dos veces si CAS devuelve SQLSTATE 40001. No reintenta otros rechazos ni publica
una captura obsoleta. El piloto encontró ese rechazo por presencia concurrente;
la campaña final valida la continuación con esta corrección.

## Campaña y reproducción

```bash
bash testing/D4/run-long-running-lab.sh
```

Construcción offline con imágenes fijadas y caché local; nueve proyectos Compose
aislados en dos grupos de concurrencia fija, sin puertos publicados ni socket Docker
en workers. Los workers fuerzan un solo carrier virtual para probar progreso con
ese límite. Recoge
auditorías, journals, observaciones firmadas y logs privados bajo `work/d4/` antes
del cleanup. Comprueba ausencia de contenedores, redes y volúmenes de cada proyecto.

| Escenario | Observación exigida |
|---|---|
| S01–S05 | Regresión de éxito, competencia, callback perdido, superviviente y continuidad I5 |
| S06 | Proceso de 70 s, más allá del grant inicial; múltiples renovaciones, mismo intento/generación y aceptación independiente |
| S07 | Corte del canal de control después de renovar; parada antes de expiración, retención de 10 y UNKNOWN bloqueado tras reconciliar |
| S08 | Solicitud con grupo vivo, señal ligada al intento, parada cooperativa y toda la continuación I5 hasta consumir 4+6 |
| S09 | Fixture ignora solicitud; parada a 15 s, candidato rechazado, sin checkpoint ni liquidación y UNKNOWN bloqueado |

Las fixtures SURVIVOR de S02/S04 siguen sin watchdog por inyección expresa del
contexto inmutable. Su supervivencia conserva la prueba negativa aprobada; no es el
comportamiento normal de las fixtures prolongadas. Todas son procesos confiables.

## Límites y pendientes D4

El arranque y la admisión de la siguiente operación siguen explícitos mediante el
driver; falta el bucle ordinario de polling del worker. Reiniciar sigue requiriendo
recuperación y no respawnea. No se añade daemon de planificación ni operación D6.
El checkpoint sigue limitado a una cuenta vinculante, dos pasos y un checkpoint.
El efecto lo aplica el adaptador del worker tras la salida de la fixture; no prueba
un CLI comercial ni efectos de un proceso arbitrario durante su ejecución.

Faltan la generalización a varias cuentas/pasos/checkpoints, verificadores de
artefactos/Git/rollback y parte de la matriz negativa Compose. UNKNOWN y
contradicciones permanecen bloqueados según A04; checkpoint desde RECONCILING
sigue excluido según A09. D5/D6, promoción, despliegue y cierre no están autorizados.
