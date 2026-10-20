# D4 I10 — ausencia sin progreso, revisión y reapertura

Fecha: 2026-10-20. **Opciones A/A/A aprobadas expresamente; implementación y validación en curso; D4 abierto.**
La petición autoriza preparar esta ampliación. Las respuestas expresas A20–A22 autorizan las opciones A siguientes. Se conservan
V1–V26, sus informes y A17: mismo receptor/diario, APPLIED no revocable, sin arbitraje
externo, compensación ni resolución tras pérdida de diario.

## Contratos y huecos comprobados

V26 exige progress>0, mantiene una sola liquidación por operación/generación y
compara su conjunto completo de recibos con los actuales. Otro recibo invalida la
resolución; las guardas de autorización/CLAIM/aceptación vuelven a bloquear. La lease
parcial/terminal ya puede haberse retirado; no se puede volver a exigir una lease
que correctamente dejó de existir ni fabricarla para reutilizar V26.

COMPLETED conserva ACCEPTANCE_PASS y sus consumidores pueden usarlo. Por tanto,
reabrir un caso no basta: hay que invalidar su elegibilidad de integración mientras
se revisa, sin borrar el PASS, y propagar el bloqueo a HARD/MOCKABLE reales y a
snapshots/publicación/CLAIM. Si otra ejecución ya ocupa el workspace/tarea/recurso,
no se puede superponer una supuesta exclusión antigua ni asegurar que está parada.

## Frontera común propuesta

- Hechos, revisiones, autorizaciones y cierres nuevos append-only, enlazados a la
  resolución/caso anterior. CAS de cabeza, versión y conjunto completo de recibos.
  Cambiar contenido bajo el mismo command_id produce conflicto.
- Una revisión del mismo diario cerrado puede explicar recibos nuevos por los
  mismos resultados canónicos. No hace aparecer APPLIED después de un ABSENT
  autoritativo cerrado del mismo diario. Un cambio de resultado/hash que contradiga
  ese cierre queda bloqueado para diagnóstico; no se liquida una diferencia ficticia.
- Si el resultado/coste acumulado no cambia, ninguna revisión vuelve a CONSUME o
  RELEASE. Reservas, mapping y consumo ya registrados permanecen intactos. No
  restaurar una reserva liberada silenciosamente ni resetear intentos o generación.
- Un caso posterior activa una cuarentena explícita por operación y claves físicas
  de tarea/workspace/recurso antes de permitir nuevas admisiones. No crea una lease.
  Si hay ejecutores afectados, se revoca la autorización de efectos/renovación y se
  exige su parada/cierre independiente antes de levantar cuarentena o admitir una
  continuación. No asumir que una reserva nueva puede quitarse para reparar la vieja.
- El PASS anterior se conserva como hecho, pero la aceptación deja de ser vigente
  durante revisión. El consumo de efectos APPLIED sigue consumido. Revalidar de forma
  explícita y volver a autorizar/rearmar cuando corresponda; nunca hacerlo por un
  callback o por una declaración de ausencia del worker.

## Tres decisiones materiales

1. Sin progreso (todo el sufijo ABSENT; puede existir prefijo de otro intento):
   A recomendada: sello de ausencia distinto de checkpoint de progreso; transición
   RECONCILING→RETRY_PENDING y autorización explícita a READY. No fabricar el
   checkpoint v1 fijo 4/6. Misma operación/reserva, nuevo intento/generación dentro
   del límite D2 y TOP_UP original. Conservar el prefijo anterior si existe.
   B: generalizar el checkpoint sellado para permitir cero progreso y pasar por
   CANCELLED, con un nuevo tipo de procedencia y ampliación explícita de v1/v2.
   En ambas, una ausencia sin cierre/parada sigue siendo UNKNOWN.
2. Revisión después de liquidar, sin cambiar el resultado canónico ni los costes:
   A recomendada: el verificador admite una revisión append-only con delta contable
   cero; se invalidan las autorizaciones anteriores y la continuación/rearme siguen
   requiriendo autorización expresa vigente. No autoriza levantar una cuarentena
   por sí sola. B: exigir además autorización humana/driver explícita para admitir
   cada revisión, incluso si solo explica un recibo nuevo idéntico o UNKNOWN tardío.
3. Reapertura de CANCELLED/COMPLETED por hechos nuevos:
   A recomendada: abrir un caso de revisión separado con cuarentena; mantener el
   estado terminal histórico de la operación y representar su vigencia mediante
   el caso/cabeza de aceptación. El caso puede cerrarse tras verificación y decisión
   explícita. La ejecución parcial solo vuelve a READY por procedencia autorizada.
   B: añadir transiciones reales CANCELLED/COMPLETED→RECONCILING, tras activar la
   cuarentena y asegurar la barrera física. Sigue sin recrear lease ni intento;
   requiere rutas nuevas de prueba/aceptación y restitución del estado terminal.
   En ambas, ejecuciones o consumidores ya iniciados quedan visibles como afectados;
   no se deshacen ni se declaran seguros automáticamente.

## Validación prevista; todavía no ejecutada

SQL: upgrade vivo desde V26; todo ABSENT con y sin prefijo; intentos agotados;
replay/CAS, revisión duplicada/fuera de orden y nuevo recibo tras captura; delta
contable cero; fallo íntegro ante hash/diario incompatible; aceptación anterior
conservada pero inelegible; dependencias y prioridad por camino bloqueante;
cuarentena antes/después de CLAIM, renovación y grant; roles e inmutabilidad.
Compose: cierre real sin efectos, reintento explícito y fencing; revisión tras
checkpoint y terminal; consumidor afectado y contención de proceso existente;
revalidación/decisión de cierre sin autoarranque; regresiones acotadas v1/v2.
Registrar qué barreras se ejecutaron realmente; no equiparar un flag SQL con parada
kernel ni una retención administrativa con reserva de capacidad.

## Avance acotado

[I10.1, ausencia sin progreso](D4-I10-ABSENCE-LAB.md) implementa A20 y mantiene
A21/A22 como siguientes pendientes ya autorizados. El SQL de revisión/cuarentena
es un borrador separado excluido de migraciones y bootstrap; no se cuenta como
implementación ni como validación. No se infiere cierre D4.
