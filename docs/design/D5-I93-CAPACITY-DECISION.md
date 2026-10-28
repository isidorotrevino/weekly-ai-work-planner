# I93 — decisión documental de capacidad tras I92

Fecha:2026-10-27, Europe/Madrid. **PREPARED_DOCUMENTARY_DECISION_NOT_IMPLEMENTED**.
[Resultado I92](../validation/D5-I92-results.md) ·
[Evaluación estructurada y anclas](../validation/D5-I93-capacity-review.json).

I92 ejecutó una vez el P01 autorizado y quedó INVALID_CAPTURE tras13/321 tests,
1/12 grupos, por REFERENCE_BUDGET. Se conserva íntegro. Esta revisión lee el
paquete sellado y fuentes; no ejecuta campañas, importa producto/runners, cambia
cuotas/perfiles ni reconstruye el retorno o la primera asignación fallida.

## Hallazgo y alcance

El contador es16393 frente al techo16384. Recorder.reference heredado incrementa
antes de comprobar; los intentos posteriores pueden incrementarlo de nuevo. Hay
nueve anclas de fuente por función/clase/hash. No hay traza de la asignación que
agotó primero la cuota: no atribuir un wrapper, valor o secuencia únicos.

I82 dispone que contextos/subcasos/procesos/keys/referencias causales consumen la
misma cuota global; toda asignación real de puntero/enlace cuenta. I87 añade
conjuntos completos de witnesses bajo esa cuota. I90/I91 preservan los límites.
El cambio de test, tabla, hilo o página no habilita reset, ni un contador paralelo.
La compresión de JSON no elimina referencias semánticas realmente asignadas.

El prefijo contiene6882 eventos,4 páginas/7.582.675 bytes, sidecar1.091.122 bytes y
máximo1317 eventos/frame. Estar bajo esos techos no dispensa la cuota de referencias.
Tampoco se puede multiplicar el prefijo13/321 para afirmar una cuota final segura:
los demás grupos/rutas tienen diferentes patrones; fuentes no son mediciones.
La viabilidad lossless dentro de todas las cuotas actuales **no está demostrada**;
este expediente tampoco prueba imposibilidad de toda representación alternativa.

Una comprobación atómica antes del incremento puede evitar sobrepasar el contador
retenido, pero no concede capacidad adicional ni resuelve por sí sola321/12. No
se modifica ahora ni se corrige retrospectivamente el16393 del paquete inválido.

## Decisión concreta propuesta

**A — permitir elaborar un diseño de capacidad que proponga revisiones explícitas
y justificadas del contrato de cuotas**, junto con alternativas de representación
sin pérdida. Es **sólo diseño**, sin aplicar ninguna cuota, implementar perfil,
ejecutar componentes, repetir captura o publicar. Debe entregar:

- Comparación versionada de cada techo actual/propuesto y semántica de charging.
- Envolvente por fuente para321/12 y sus incertidumbres, sin ejecutar el runner.
- Análisis conjunto de referencias, eventos/campaña/test, bytes/fila/evento,
  páginas, raw/sidecar/contexto/launcher, miembros/bytes del paquete, valores y
  Reader acumulado antes/después/autoridad, sin resets encubiertos.
- Reglas de carga atómica, fallo/diagnóstico/cleanup y conservación de todos los
  contextos/witnesses/recibos/enlaces y autoridades, sin muestreo ni evidencia omitida.
- Matriz sintética futura con límites exactos/uno más, fallos y restauración,
  namespace/registro nuevos y casos NOT_RUN. Implementación/componentes y captura
  funcional completa requerirán decisiones posteriores separadas.

**B — conservar exactamente todas las cuotas actuales** y registrar la captura
completa bloqueada, sin nueva campaña ni promesa de una implementación que quepa.
Puede proseguir trabajo documental; no se declara cerrada la obligación.

No se propone un número arbitrario que sólo supere el prefijo. La opción A permite
**proponer** cambios de contrato, no aprobarlos o aplicarlos. La autorización I92
se agotó en su única ejecución; no cubre un cambio de cuotas o un nuevo perfil.

## Invariantes de cierre

I86/I89/I92 permanecen inválidos y separados: no sumar/reanudar paquetes. NS12 y
los13 PASS raw no prueban compatibilidad321/12, persistencia/recuperación integrada,
independencia o fsync nativo. IR03 sigue NOT_READY hasta captura completa válida y
posterior decisión de revisión. Publicación y aceptación global son separadas.

P0;83 SUPPORTS_BOUNDED/1 PARTIAL(UI04.1). D1–D4 cerrados e I1–I20/A52 aceptado;
30/35 sin promoción. D5 global/H07/G01–G07/GI33/34/38/39/40 OPEN. Sin proveedores,
credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue,
SQL/Java/Docker nuevos o D6. No hay autoridad/destino/perfil futuro creados.
