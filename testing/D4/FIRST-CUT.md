# D4 — primer corte: preparación histórica y entrega integrada

Actualización I5: A/A aprobado para el [checkpoint parcial sintético](../../docs/design/D4-I5-CHECKPOINT-LAB.md).
Los pendientes de checkpoint que aparecen en la preparación histórica siguiente
no describen el estado actual del corte I5. D4 permanece abierto.

Estado de I4: [I4 integrado](../../docs/design/D4-I4-LAB.md), con
`bash testing/D4/run-lab.sh` y [resultados propios](../../docs/validation/D4-I4-results.json).
D4 sigue abierto. La preparación que sigue es histórica; sus pendientes de Compose,
conexión y verificador se concretan en I4. I5 habilita el checkpoint acotado descrito arriba.

Fecha de la preparación: 2026-10-19. Dirección aceptada: [D4-A01–A04](../../docs/design/D4-DECISIONS.md).
**Entrega actual: diseño, manifiesto de escenarios, preflight y
[I1 entrega durable de persistencia](../../docs/design/D4-I1-DELIVERY.md). La vertical
de procesos/efectos y sus pruebas funcionales siguen pendientes.**

Avance I2: el [adaptador HTTPS/mTLS](../../docs/design/D4-I2-HTTPS.md) ya está probado
con clientes sintéticos y LOGIN restringido. Lo pendiente de la vertical son
procesos supervisados, receptor/grants/verificador y Compose; los cuatro escenarios
completos permanecen pendientes.

Avance I3: [supervisor y receptor](../../docs/design/D4-I3-PROCESS-EFFECTS.md)
implementados como componentes, con pruebas de subprocesos y diario. Quedan
conexión con I2/D2, verificador independiente, Compose y campaña completa.

## Qué puede ejecutarse hoy

Desde la raíz, con Python 3 y Docker accesible:

```bash
python3 testing/D4/preflight.py
```

Comprueba hashes de cierre D3, inventaría fuentes actuales y consulta Docker,
Compose e imágenes ya locales con timeout. Guarda un informe local propio en
`work/d4/preflight-<UTC>-<id>/preflight.json`, con permisos privados. No descarga,
construye ni inicia servicios; no necesita secretos. Un fallo de infraestructura
produce salida no cero e informe parcial; nunca cuenta como éxito funcional.
No comprueba todavía caché Maven completa ni disponibilidad de imágenes D4.
El digest vacío de una imagen local se registra vacío, no se inventa.

La batería existente `testing/D3/run-postgres-tests.sh` conserva sus plantillas
V11/V12/V13/V14/V15, usa PostgreSQL y Maven desechables y no inicia Spring Boot ni
workers. No se ha repetido por estos cambios de preparación. El preflight contrasta
hashes; eso no equivale a repetir sus pruebas.

## Secuencia concreta de construcción

Avance I1: V16 y harness de entrega implementados y probados; catálogo sintético y
rol NOLOGIN restringido. Faltan presencia/certificados y LOGIN runtime de laboratorio
para completar identidad. La prueba de continuidad con efectos parciales aún no
está implementada; no se infiere que todo I1/I5 esté terminado.

| Hito | Archivos futuros | Criterio verificable |
|---|---|---|
| I1 Persistencia/identidad | `migrations-d4-proposed/`, harness propio, registro/grants y entrega durable | Upgrade V15 propio; LOGIN runtime mínimos y receipts atómicos; V1–V15 intactos |
| I2 Vertical | Módulo Java 21/Spring Boot de control plane; worker/supervisor, receptor y verificador sintéticos | Una operación completa pasa exclusivamente por HTTPS, sin SQL en workers |
| I3 Entorno | `compose.yaml`, `images/`, bootstrap de CA y fixtures | Redes internas persistencia/workers/efectos; cero puertos y socket Docker; digests registrados |
| I4 Campaña | `run-lab.sh`, `scenarios/`, evidencias saneadas | Ejecutar D4-S01–S04 y guardas de identidad; timeout acotado y limpieza del proyecto |
| I5 Checkpoint | Entrada D4 protegida y transición de continuidad revisada | Parada y consumo parcial comprobados; sin continuar CANCELLED de forma implícita |

No crear Compose con comandos vacíos o servicios ficticios: no demostraría la
vertical elegida. Las versiones nuevas de Spring Boot/dependencias se fijarán
al implementar I2 y se revisarán antes del bootstrap; no se elige una versión
sin comprobar compatibilidad. Build con descargas separado de campaña offline.

## Topología fijada para I3

`db` y `migrate` en red de persistencia; `control-plane` en persistencia/workers;
dos workers en workers/efectos; receptor en efectos; `verifier` en workers/efectos
y únicamente la conexión de evidencia que requiera su rol. Driver con identidad
distinta y auditoría SQL de solo lectura; el host provoca reinicios/cortes sobre
el nombre único de proyecto, sin socket dentro de workers. Ninguna red con salida
externa durante campaña. Sin bases reales ni `trust` como identidad runtime D4.

Volúmenes propios para DB, diario del receptor y diario de cada worker; workspaces
sintéticos separados. No root en aplicaciones, rootfs de solo lectura, capabilities
eliminadas, no-new-privileges, límites de CPU/memoria/PIDs/tmpfs. Las excepciones
del migrador/PostgreSQL se documentarán en la configuración concreta. La evidencia
de parada se obtiene desde el host y se contrasta con diario/receptor; no del mismo
payload del worker. Solo fixtures confiables, sin promesa de sandbox para código hostil.

## Campaña acotada

[scenarios.json](scenarios.json) es una especificación de aserciones, no un runner.
Presupuesto propuesto: 30 s de readiness por servicio y 240 s por escenario
(incluye vencimiento real de lease de 60 s). Timeout global 20 min para cuatro
escenarios. Una espera agotada es fallo; un caso pendiente no se cuenta como PASS.

Cada fixture usa cuentas sintéticas OPERATIONS con límite 100 → 70/20/10 y coste
documentado, ventanas que cubren escenario/renovaciones, confianza 1, procedencia
fixture y dependencia real solo cuando corresponda. Para competencia por la misma
cuenta, las peticiones deben identificar el mismo recurso físico: el worker ajeno
no adquiere ese recurso por compartir la red. Otros escenarios usan recursos
independientes y exclusión compartida para probar concurrencia válida.

Cada aserción observa command/plan/operation/attempt/reservation/worker/resource/
generation, cuentas y diario, respuesta HTTP, grupo de procesos y diario del receptor.
El driver no puede insertar PASS, recibos de efecto ni prueba de parada de sí mismo.
Los fallos se inyectan en fronteras verificables, no mediante SQL que fabrique el
resultado esperado. Respuesta perdida se provoca después de confirmar el efecto.

El futuro `run-lab.sh` deberá separar preflight/build/run, fijar nombre único,
`--pull never` en ejecución, recoger evidencia antes de `down` selectivo y limpiar
solo recursos con ese proyecto. Conservar diarios exportados privados antes de
eliminar volúmenes; reiniciar no equivale a borrar volumen. Sin prune global.

No hay comandos `compose up` disponibles aún. Un resultado de preflight es
preparación de infraestructura; los resultados end-to-end y la aprobación del
diseño completo/cierre D4 siguen pendientes.
