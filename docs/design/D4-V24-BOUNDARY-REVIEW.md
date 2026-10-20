# D4 — revisión de fronteras de V24

Fecha: 2026-10-20. **D4 abierto. V24 intacta; corrección V25 propuesta.**
Se reprodujeron dos defectos de V24 en PostgreSQL desechable: ID de paso numérico
aceptado al congelar, y checkpoint liquidado tras vencer la lease durante una espera
de bloqueo de cuenta. Reproducirlos no cuenta como validación positiva de V24.
A09 exige conservar compromiso al vencer; A13/A14 requieren intención verificable.

V25 se prepara como ampliación estática y revisable: validar tipos JSON antes de
extraer texto y volver a comprobar la lease tras la liquidación, revirtiendo todos
sus cambios si ha vencido. La función antigua quedará privada para impedir saltarse
la guarda; se trasladarán sus permisos de servicio a la entrada protegida.
No hay promoción, ejecución contra datos reales ni aprobación de cierre.

## Compatibilidad de campos adicionales: A aprobada

Los campos requeridos y sus tipos deben respetarse en ambas opciones. Los valores
mal tipados no se convierten ni se reparan silenciosamente. Una intención anterior
incompatible queda conservada y bloqueada para nueva admisión: no se borra ni se
crea otra operación para reiniciar intentos. V1 conserva su ruta independiente.

**A, recomendada:** esquema v2 cerrado. Rechazar campos adicionales en manifiesto,
paso y cuenta, además de tipos incorrectos. Las intenciones v2 anteriores con
campos adicionales se conservan pero no vuelven a admitirse tras el upgrade.
Una futura extensión necesita versión de esquema explícita.

**B:** conservar campos adicionales ligados al hash del contexto, sin interpretarlos.
Solo los campos v2 conocidos determinan pasos, costes y autoridad. Rechazar siempre
tipos incorrectos y campos obligatorios ausentes. Evita bloquear metadatos adicionales
que V24 admitía, a cambio de no detectar su uso erróneo como supuestas instrucciones.

El usuario aprobó expresamente «A: esquema cerrado (recomendada)» el 2026-10-20
(D4-A16). La aprobación procede de esa respuesta, no de las pruebas del borrador.
La guarda de lease y el traslado de permisos no dependen de esta decisión.

La [implementación V25](D4-V25-BOUNDARY-LAB.md) aplica A16. El informe
provisional anterior conserva su estado pendiente histórico; la campaña del
esquema cerrado tiene evidencia propia, sin sobrescribirlo.
