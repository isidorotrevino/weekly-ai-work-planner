# D4 I2 — transporte Spring Boot/HTTPS y mTLS

Fecha: 2026-10-19. **Adaptador sintético implementado y probado. D4 abierto.**
Dirección autorizada por A01/A02 y continuaciones del usuario; [decisiones](D4-DECISIONS.md).
I2 no habilita continuidad parcial ni resolución de contradicciones.

## Cambio

[worker-control-plane](../../worker-control-plane/README.md) añade un servidor
Spring Boot con HTTPS obligatorio y certificados sintéticos. La identidad deriva
del certificado, su SAN y un pin autorizado recargado por petición. Comprueba
caducidad/revocación en conexiones reutilizadas y rechaza certificados ajenos,
identidad en payload y cabeceras de suplantación.

[V17 propuesta](../../migrations-d4-proposed/V17__worker_transport_commands.sql)
guarda sobre completo y respuesta en la transacción del comando de dominio.
Recupera entregas V16, selecciona trabajo en el servidor, confirma recepción,
limita acciones y permite consulta del recibo propio. No cambia V1–V16 ni el
dispatch/lease/generación/cuota aprobado. La presencia no autoconcede capacidades
ni cambia el estado administrativo ONLINE/OFFLINE.

El uso de un único endpoint de comandos concreta las rutas inicialmente propuestas
en el borrador: la versión/acción identifica el contrato y todas las mutaciones
comparten la misma frontera de validación/deduplicación. No es una API SQL genérica.

La aplicación usa un LOGIN sintético con solo tres entrypoints de d4. No tiene
permisos de propietario, verificador, contabilidad ni bypass de CLAIM D3. El
bootstrap crea LOGIN únicamente en PostgreSQL desechable, fuera de migraciones.

## Evidencia

[Resultados portables I2](../validation/D4-I2-results.json), con hashes de fuentes,
versiones e imágenes observadas y grupos separados:

| Grupo | Pruebas | Alcance |
|---|---:|---|
| Entrega I1 | 14 | V16, instalación/upgrade y contratos de persistencia previos |
| Transporte I2 | 12 | V17: HTTPS real, mTLS, ownership, LOGIN restringido, replay/reinicio, límites y rollback; incluye un upgrade SQL V16→V17 con entrega RUNNING |
| Regresión D2 | 157 | Harness histórico sin cambios, V1–V11; corpus SemVer incluido en una prueba |

Cero fallos, errores u omisiones. La campaña final D4 se ejecutó con Maven offline
y red Docker interna. Bootstrap/descarga y construcción del JAR se realizaron
antes, en contenedor sin conexión a DB ni credenciales de runtime. No hay puertos
publicados. No se afirma que las 157 pruebas D2 se ejecutaran sobre V17.

Una prueba rechaza persistencia del recibo después de ejecutar START dentro de la
transacción: revierten estado y recibos d3/d4; repetir el mismo ID tras retirar el
fallo produce un único START confirmado. Otra aplica V17 sobre V16 con entrega,
intento RUNNING, reserva/diario/lease y verifica que polling recupera el mismo intento.

Los casos de replay confirman el comando, ignoran su respuesta o reinician el
adaptador y repiten. Todavía no son cortes de cable/red entre contenedores de worker.
Un caso modifica el vencimiento por SQL para verificar el comportamiento de
recibos antiguos: no demuestra expiración real de lease con proceso superviviente.

## Límites que permanecen

Servidor Spring y clientes HttpClient de prueba están en el mismo JVM/contenedor
Maven; PostgreSQL está en otro contenedor. El harness dispone de credencial dueña
para fixtures/auditoría; las peticiones funcionales usan el LOGIN restringido.
Esto demuestra autorización de API/SQL, no aislamiento de un worker comprometido.
Los tests usan clases del módulo junto a dependencias de pruebas; no son una
campaña de ejecución del JAR empaquetado en un contenedor de aplicación separado.

Solo fixtures confiables y certificados locales efímeros. No se ha contactado un
proveedor real ni usado credenciales comerciales. No hay supervisor de procesos,
efecto externo, grant de receptor, checkpoint, prueba independiente de aceptación
ni Compose. CALLBACK llega a VERIFYING y no autoaprueba ACCEPTANCE_PASS.

La batería Docker histórica D3 permanece separada. Se verificaron sus hashes de
cierre sin repetir toda su batería; informes previos conservados. I1 conserva V16
como target explícito pese a incorporar la propuesta V17 al mismo harness D4.

El siguiente incremento es supervisor/fixtures de procesos, receptor durable con
grant y cierre y verificador independiente; después Compose/campaña D4-S01–S04
con aislamiento, reinicios y vencimiento real. Las decisiones A05–A07 de continuidad
siguen como diseño a revisar. Ningún PASS cierra D4 ni promueve/despliega migraciones.
