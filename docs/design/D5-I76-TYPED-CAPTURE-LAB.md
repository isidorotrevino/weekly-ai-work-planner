# I76 — laboratorio sintético del perfil tipado

Autoridad: selección A posterior a I75. Aprueba contrato, implementación del perfil/registro fijo y validación AT01–AT80 sólo con suites sintéticas. Excluye importar producto/runners históricos, reejecutar PG64, campañas funcionales y publicación. Base local `62f897ce765dcefa1df4673dad073c52b9588ff2`.

[Contrato](D5-I75-TYPED-ADAPTER-DESIGN.md) · [Matriz](D5-I75-TYPED-ADAPTER-REVIEW.md) · [Componentes](../../testing/prospective_capture_typed/README.md).

Comando `python3 -B -m testing.prospective_capture_typed.run_typed_lab`, bajo subprocess externo con timeout de 300 segundos; raw, entorno público, hashes pre/post, anclas AST y resultado por caso en archivos I76 nuevos. No se importa el módulo de pruebas PG64. Se reutilizan únicamente ayudantes puros I70/I73.

Ensayos con Fixture, PlaneError y EligibilityError sintéticos nuevos. Snapshot/constructor y operandos se observan después del retorno original sin llamadas adicionales al dominio. Vectores HMAC y representación tipada con clave sintética conocida; no se publican rutas o claves de capturas futuras. La proyección de excepciones abarca tipo y args, no el objeto completo. Pruebas de scopes exactos, metaclass/subclase desconocidos, restauración, cuotas y propagación de errores; límite real de 131072 eventos sintéticos y rechazo del siguiente. Procesos propios nuevos prueban READY/RELEASE, capacidad de directorio, espera y retirada del grupo; sentinels hermanos preservados.

El plan es NOT_RUN_I77_AUTHORIZATION_REQUIRED. No se crea autorización, destino ni copia de lanzamiento I77 en el checkout. La autoridad de prueba existe sólo en temporales sintéticos retirados. I74 y sus 35 frames incompletos permanecen inmutables. P01 completo (321 ocurrencias/12 grupos) requeriría autorización I77 separada, destino nuevo y revisión posterior de suficiencia; sin sumar resultados históricos.

P0 y agregado 81/3; UI01.2/UI04.1/UI09.2 PARTIAL. D1–D4 cerrados e hito D5-LOCAL-SYNTHETIC-I1-I20/A52 aceptado intactos. D5 global/H07/G01–G07/GI33/GI34/GI38/GI39/GI40 abiertos. Los PASS aislados no acreditan persistencia o recuperación integrada. Sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción, despliegue ni D6. Sólo I52 publicado; cualquier publicación posterior exige decisión separada sobre SHA concreto.
