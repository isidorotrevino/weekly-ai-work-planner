# Handoff — entorno de desarrollo Docker Compose y documentación de entrada

Fecha: 2026-10-21, Europe/Madrid. Estado: trabajo siguiente autorizado, pendiente de implementar.

## Objetivo de la nueva sesión

Crear un entorno local de desarrollo basado en Docker Compose y hacer los README
más amigables, llevando los detalles técnicos a un subdocumento enlazado. Esta
sesión prepara el handoff; no declara que ese entorno de desarrollo exista ya.

Petición del usuario: «publica en git, y se aprueba el cierre de D4, crea un handoff
para que una sesión nueva se enfoque en crear un entorno de desarrollo basado en
docker compose y actualice el README de una manera más amigable, dejando los
detalles técnicos en un subdocumento».

D1, D2, D3 y el alcance sintético D4 están aprobados y cerrados. La aprobación D4
original del 2026-10-20 fue «A: aprobar cierre de D4 sintético»; el usuario la
ratifica en esta petición. La autoridad es [D4 aprobado](docs/design/D4-approved.md)
y su [manifiesto](docs/validation/D4-CLOSURE.json). Las referencias publicadas se
consultan en ese manifiesto y en Git; no usar este handoff como un SHA mutable.
El nuevo trabajo no inicia D5/D6 ni reabre D4.

## Lectura inicial

1. [README en inglés](README.md), [README en español](README.es.md),
   [índice](docs/README.md) y [contribuciones](CONTRIBUTING.md).
2. [Cierre D4](docs/validation/D4-CLOSURE.json),
   [tabla de aceptación](docs/design/D4-I12-ACCEPTANCE-REVIEW.md),
   [I12 integrado](docs/design/D4-I12-INTEGRATED-VERIFIERS-PRESENCE.md) y
   [decisiones](docs/design/D4-DECISIONS.md).
3. [Guía del laboratorio](testing/D4/README.md),
   [Compose de pruebas](testing/D4/compose.yaml),
   [build](testing/D4/build-lab.sh),
   [harness](testing/D4/lab-scenarios.py),
   [matriz actual](testing/D4/run-latest-matrix.sh) e
   [imagen](testing/D4/images/Dockerfile).
4. [Núcleo](scheduler-core/README.md), [adaptador](scheduler-postgres/README.md),
   [batería D2](testing/D2/README.md), [índice de validación](docs/validation/README.md)
   y [avisos de dependencias](THIRD-PARTY-NOTICES.md).

Inspeccionar primero el árbol, la rama, el remoto y las instrucciones locales.
Conservar cambios ajenos y verificar las referencias; no asumir que el SHA de una
sesión anterior sea el HEAD actual.

## Qué existe y qué hay que construir

Existen bibliotecas Java 21, contratos PostgreSQL y un laboratorio sintético HTTPS
con control plane, dos workers, receptor de efectos y verificador independiente.
`testing/D4/compose.yaml` usa configuración y certificados generados por el harness,
imágenes locales preparadas, redes internas, volúmenes por proyecto y ejecución
desechable por escenario. No basta con anunciar `docker compose up` en la raíz.
El bootstrap de ese laboratorio aplica propuestas hasta V30 en bases sintéticas;
no promueve esas propuestas a migraciones de producción.

Las baterías SQL históricas D2/D3 conservan sus targets propios. La matriz D4
actual recorre S01–S30 sobre V30. No confundir ninguna de ellas con un entorno de
desarrollo persistente o una aplicación web de producto, que todavía no existen.
Los README acumulan historia y contienen afirmaciones antiguas como «no hay
worker»; corregir el estado vigente al reorganizarlos, conservando historia en
sus documentos de origen.

La evidencia final D4 registra 638 pruebas distintas y 1.085 comprobaciones en 30
escenarios Compose, más limpieza de 30 proyectos finales y 14 de pilotos. No
reescribir esos informes, sus hashes ni los manifiestos como si nuevas ejecuciones
fueran las originales. Las nuevas validaciones tendrán resultados propios.

## Resultado esperado del entorno de desarrollo

Preparar una entrada claramente identificable, por ejemplo `compose.dev.yaml`,
con scripts pequeños y documentados. Reutilizar componentes del laboratorio cuando
sea apropiado sin cambiar sus entradas ejecutables selladas solo por comodidad.
Antes de decidir la ubicación, revisar qué reutilización evita duplicar configuración
sin alterar las campañas históricas.

El flujo debe permitir a una persona con Docker Engine y Compose arrancar datos
sintéticos, consultar salud y logs, modificar código y reconstruir los servicios
pertinentes, ejecutar un smoke test, parar y recuperar su sesión. Documentar qué
ocurre con los datos al reiniciar, qué requiere rebuild y cómo hacer un reset
explícito y selectivo. No prometer hot reload, Windows/macOS, ejecución offline o
arranque sin JDK/Maven de host sin haberlo comprobado para el flujo concreto.

Mantener separados datos de desarrollo, proyectos Compose de pruebas y evidencia.
El reset solo debe afectar al proyecto de desarrollo elegido; evitar `docker system
prune` o borrados globales. Generar configuración/certificados locales sintéticos
en rutas ignoradas, ofrecer solo ejemplos seguros y registrar las dependencias
necesarias para un primer arranque. No copiar CA privadas ni logs a Git.

El observador host y la prueba real de parada requieren conservar su frontera de
confianza. No meter un socket Docker en workers, darles SQL ni convertir el driver
en autoridad de evidencia para facilitar el entorno. Si la topología local exige
un mecanismo distinto, preparar el diseño concreto antes de pedir una decisión.
El entorno persistente debe respetar presencia/incarnación, recuperación y rearme
explícitos; reiniciar servicios no puede fabricar parada, leases ni autorización.

## README y subdocumento técnico

Actualizar `README.md` y `README.es.md` de forma coherente. La entrada debe explicar
qué problema resuelve el proyecto, para quién, qué funciona hoy, cómo empezar con
el entorno comprobado y dónde seguir leyendo. Mantener los comandos iniciales
breves y ejecutables; señalar que son fixtures sintéticas y que no hay interfaz
web de producción. Conservar enlaces a licencia, contribuciones y seguridad.

Crear una guía técnica enlazada, por ejemplo `docs/DEVELOPMENT.md`, con requisitos,
topología, build/rebuild, configuración, puertos locales si los hay, persistencia,
pruebas, parada, reset, troubleshooting y límites. Enlazar desde ella los diseños,
matrices e informes existentes en vez de duplicar toda la historia. Si hace falta
una segunda guía de arquitectura, justificar su separación; no añadir documentos
vacíos. El README no debe seguir acumulando párrafos de cada incremento I1–I12.
Actualizar también el índice documental para que las rutas sean fáciles de hallar.

## Decisiones y límites

Resolver autónomamente decisiones reversibles dentro del alcance. Si aparece una
decisión material, preguntar en español con opciones concretas, recomendación y
consecuencia. En particular, concretar antes de preguntar:

- Persistencia por defecto: volumen local conservado entre sesiones (propuesta)
  frente a reinicio desechable por arranque; ambos con reset explícito.
- Acceso desde host, si resulta necesario: puertos enlazados solo a loopback frente
  a comandos de diagnóstico dentro de Compose. No publicar en todas las interfaces
  ni añadir una UI nueva como parte implícita de este trabajo.
- Rebuild manual documentado (primer corte propuesto) frente a modo watch; verificar
  compatibilidad y permisos antes de ofrecer watch.

Conservar cuentas físicas, reservas entre planes, reparto 70/20/10, dimensiones,
dependencias, prioridad por camino bloqueante, fencing, contadores y las
aprobaciones/rearmes expresos. No integrar proveedores ni credenciales reales,
no promover migraciones, no desplegar y no alterar cierres D1–D4. Si un cambio
necesita ampliar un contrato aprobado, explicar el caso y pedir decisión antes de
implementar esa ampliación. No requiere aprobación adicional el trabajo ordinario
de documentación, scripts y entorno local ya autorizado.

## Validación y entrega

Ejecutar desde una configuración nueva el camino documentado: build, arranque,
salud, smoke sintético, cambio/rebuild y parada. Comprobar restart y persistencia
si se ofrecen; comprobar que reset no borra proyectos o evidencia ajenos. Registrar
versiones, comandos, resultados y límites en un informe nuevo, sin atribuirse las
638 pruebas históricas. Escalar a regresiones significativas solo si cambia código,
contratos o integración; no repetir toda la matriz por ediciones documentales.

Validar Compose, enlaces, coherencia bilingüe y `git diff --check`; ejecutar
`python3 scripts/check-publication.py` y revisar el diff antes de publicar. Conservar
artefactos brutos bajo `work/`, fuera de Git. Al terminar, explicar lo que puede
hacer ya un desarrollador, qué se validó y qué queda pendiente. La autorización de
publicación de esta sesión corresponde al cierre D4 y a este handoff; no inferir
publicación automática de cualquier cambio futuro.

## Prompt para iniciar la nueva sesión

> Lee HANDOFF-DEV-ENV.md y los documentos indicados. D1–D4 están aprobados y
> cerrados; conserva sus manifiestos y evidencias. Crea un entorno de desarrollo
> local con Docker Compose, claramente separado de las baterías SQL y del
> laboratorio de validación D4. Haz los README en inglés y español más amigables y
> lleva los detalles técnicos a un subdocumento enlazado. Implementa y valida el
> flujo de arranque, rebuild, smoke, parada y reset selectivo que documentes.
> Pregúntame las decisiones materiales con opciones concretas. Sin proveedores ni
> credenciales reales, promoción de migraciones, despliegue o ampliación implícita
> de D5/D6. Responde en español.
