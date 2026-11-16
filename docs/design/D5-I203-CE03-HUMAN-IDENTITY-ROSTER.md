# I203 — CE03 preparado como recepción provisional de identidades faltantes

CE03 (HUMAN-IDENTITY-ROSTER) queda **preparado como dossier documental provisional**,
sin identidades humanas autenticadas, nombramientos, registro de actores ni
aceptación reales. La completitud del actor registry y sus hashes finales siguen
diferidos a CE08, después de conocer a los autores de toda la evidencia. Se
mantiene la no admisión de PGO181 candidato 02/PJC115-R2, D5 abierto e IR03
`NOT_READY`.

Fecha del cliente: 2026-11-16, Europe/Madrid. Base publicada I202:
`72ef842b5675c0c80aa56d3f0b7b4a9f07c05b47`.

## Entrega y dependencia pendiente

[CE03 candidato](../validation/D5-I193-CE03-HUMAN-IDENTITY-ROSTER-CANDIDATE.json)
ocupa la ruta exacta de `/steps/2` del plan I193. Conserva tres requisitos de
evidencia, tres checks, frontera de autorización y K02/K03/K10/K16. La checklist
sitúa actor_registry en CE03/CE08 y su freeze final en CE08, no en esta recepción.
El dossier tiene un schema documental propio; no es una instancia positiva I191
rellenada con nulos o una lista vacía presentada como registro completo.

La dependencia real de CE02 sigue insatisfecha: su candidato 02 y F199-01 fueron
confirmados documentalmente en I202, sin anchors, evidencia o aceptación competente.
La petición I203 permite preparar esta declaración de pendientes, sin descargar
la aceptación real de CE01/CE02 ni aceptar CE03. Las fuentes históricas permanecen
intactas.

El inventario fija 15 documentos por hash y tamaño físico: plan/checklist,
I191/pack, S01/I122, CE01/CE02 candidatos 02/I202 y referencias I192/perfil02/
protocolo/output/transporte. Son fuentes documentales, no evidencia de personas,
autoría, identidad, organización o nombramiento. Los 812 pins se contrastan con
Git y disco.

## Obligaciones por consumidor

| Obligación | Consumidor | Evidencia o política requerida; actualmente faltante |
| --- | --- | --- |
| IR01 | CE03 provisional | Humanos responsables y organizaciones bajo autoridad de identidad auténtica aceptada |
| IR02 | CE03 provisional | Alias completos, resolución canónica común y ausencia de colisiones/ambigüedad |
| IR03 | CE03 provisional | Competencia y nombramientos genuinos para los ocho roles, con scope y vigencia |
| IR04 | CE03 provisional | Espacio de identidad humana separado del principal software/service/process |
| IR05 | CE03 provisional | Solicitante, autor de fuentes y firmantes/custodios resueltos mediante la misma autoridad; sin exigir aprobaciones futuras |
| IR06 | CE03 provisional | Seguimiento de actividades/contribuciones conocidas y procedencia faltante, sin afirmar preparadores completos o crear registros positivos |
| IR07 | CE03 provisional | Política de ocho exclusiones S01, reglas source-author/root-key y separaciones extra, sin declarar verificaciones sobre identidades desconocidas |
| IR08 | CE03 provisional | Schemas/cotas/no truncamiento como política; no afirma ajuste de un registro final desconocido |
| IR09 | **CE08 diferido** | Freeze completo de actores/preparadores después de CE02–CE07 y sus autores reales; actor registry antes de image/caller/platform y antes de C, con refresh/revisión de dependientes |

Las nueve filas siguen `MISSING_NOT_EVALUATED`, sin proveedor, localizador,
nombramiento, hash, tamaño, aceptación reales ni permiso de contacto. Hay ocho
obligaciones provisionales CE03 y una de finalización CE08, explícitamente
excluida de los requisitos de completitud/hash de CE03. No se preaprueba ningún
autor futuro ni se inventan actores para completar listas.

## Humanos, software y contribuciones

`actual_identity_state` conserva ausentes humanos canónicos, organizaciones,
alias, asignaciones/competencia/nombramientos, solicitante/autor, principal caller,
preparadores autenticados, cuerpo/hash/tamaño/epoch/validez/completitud del
registro y autores futuros. No hay resolución de identidad o separación real
verificada, registro positivo I191 ni completitud final declarada.

El nombre de una persona, usuario Git, clave, rol aceptado por sí solo o string
distinto no demuestra una identidad humana distinta. El principal software caller
no reemplaza a un humano para eludir S01. El asistente se declara preparador de
este trabajo documental, con humano responsable canónico y organización ausentes;
no se lo registra como humano autenticado ni se infiere quién es desde la cuenta Git.

`documentary_preparation_tracking` distingue dos observaciones limitadas:

- La actividad declarada de este asistente preparando los cinco archivos I203,
  sin hash de contribución auténtica, autoría humana o registro positivo.
- Quince observaciones de documentos existentes y su incremento declarado, con
  hashes físicos reales, pero con humano responsable y evidencia de autoría
  ausentes. No equivalen a quince personas, quince preparadores o una lista completa.

Cada futuro preparation_record positivo requerirá actor autenticado, evidencia
real de la contribución y los pins exactos de perfil02/pack. K03 exige coincidencia
con C por actor_id/record_id y digest del registro completo; no se calcula ni se
emite ese registro aquí. Ningún preparation_record puede pinchar C, acceptance,
bundle o root futuro. La evidencia subyacente debe existir realmente; los hashes
solos no la sustituyen.

## Separaciones y finalización

Se conservan las ocho exclusiones S01 universalmente sobre **todos** los
preparadores del alcance aceptado, las reglas R08/source-author e issuer-key/
acceptor-key y las cuatro separaciones de custodia R08 frente a R01/R02 por
humano y clave. R01/R02 pueden coincidir cuando el mismo humano sea genuinamente
competente para ambos: no se impone una prohibición global nueva. La política de
aprobaciones no exige un bundle en CE03; la prueba real de esas aprobaciones
sigue en CE10, conforme a la reparación F199-01.

Los slots de revisión CE03 son R06 y R08, sin personas, nombramientos,
competencia o aceptación. Los ocho roles permanecen en el alcance de resolución
y sus separaciones no se satisfacen con nombres/keys distintos o flags aceptados.
No se ejecuta comparación de personas reales ni se declara independencia efectiva.

CE08 mantiene exactamente CE02–CE07 como prerrequisitos. Sólo con los autores de
evidencia realmente conocidos puede congelar primero el actor registry completo,
luego image_manifest, caller_identity y platform_custody, antes de CE09/C.
Cambiar contribuyentes, alias, cuerpos, identidad/runtime/imagen, epoch, claves o
scope invalida hashes/revisiones dependientes; se vuelve a revisar CE03–CE10 y
CE11 según el plan. Ese refresh documental no aplica un rebind activo.

Los cinco fragmentos de schema son exactos: actor_registry, actor,
preparation_record, evidence_reference y validity. Actores 1–64, aliases por actor
0–16, competence_scopes 1–8 y preparadores 1–16 son límites candidatos, no una
lista completa ni cuotas activas. El cuerpo final actor_registry tiene cap
98.304 bytes; **no es el cap de este wrapper** y no demuestra ajuste de cuerpos
subyacentes, heap/CPU/IO o 900 s. Los checks reales de cuerpo/hash/codec/caps
finales quedan en CE08; no se ejecutan aquí.

## Preservación y verificación

I122 sigue `IMPLEMENTED_NOT_ADMITTED`, CP03 verdadero sólo en su alcance heredado
sellado, CP07 falso, atomicidad correlacionada no verificada y componentes
`NOT_RUN`. Permanecen las nueve condiciones completas CP07, los candidatos
numéricos y las cotas anteriores; E01–E05 abiertos y cero obligaciones cerradas,
E06 separado y sin ejecutar, F179-01/S01 sin aceptación. Las seis fuentes sucesoras
y ocho cuerpos I191 siguen ausentes; los otros nueve dossiers planificados no
se crean. No cambia cuota, reserva, presupuesto, schema activo, Reader, canal,
capture_inputs, binding, autoridad/root, destino, claim o worker.

El mismo asistente/chat prepara el dossier; no acredita independencia personal
u organizativa, revisión competente R06 ni aceptación separada R08. La ausencia
de evidencias no se suple con contacto, enrollment, claves, cripto o ejecución.

Crear CE03 ahora no reescribe los históricos que lo describían ausente. La
auditoría prueba con `git ls-tree` su ausencia en la base I202 y sólo proyecta la
consulta de presencia de **esta ruta exacta** mientras reproduce las funciones
documentales heredadas I202. Los guards CE02/CE01 originales siguen anidados,
sin modificar sus bytes. `finally` restaura el método; fuera de esa reproducción
se exige CE03 real presente, hashes correctos, CE01/CE02 preservados y los otros
nueve slots ausentes. No ejecuta los `main` de publicación históricos.

```sh
python3 docs/validation/D5-I203-audit.py
```

Resultado exigido: `PASS_STATIC_SOURCE_ONLY_PROVISIONAL_IDENTITIES_MISSING`.
[La preparación reproducible](../validation/D5-I203-preparation-review.json)
verifica fuentes, rules, schemas, separaciones y fronteras de fase; siete
contraejemplos sólo en memoria deben rechazarse: adelantar freeze a CE03,
afirmar completitud final, colapsar humano/software, preaprobar autores futuros,
permitir hashes futuros en preparation_record, quitar un prerrequisito CE08 o
aceptar CE03 por preparación documental. No son pruebas de componentes.
[El sello](../validation/D5-I203-integrity.json) preserva 504 archivos publicados
y fija los otros cuatro artefactos de la unidad. Harness runtime: N/A, dossier
provisional sin producto/componentes/identidad/registry codec/cripto/imagen/claim/protocolo.

Unidad única superior a 400 líneas por pins, matrices y preservación; se declara
el exceso sin recortar evidencia. Commit/push publica para revisión estos cinco
archivos y limita la reversión a ellos:

- `docs/design/D5-I203-CE03-HUMAN-IDENTITY-ROSTER.md`
- `docs/validation/D5-I193-CE03-HUMAN-IDENTITY-ROSTER-CANDIDATE.json`
- `docs/validation/D5-I203-preparation-review.json`
- `docs/validation/D5-I203-audit.py`
- `docs/validation/D5-I203-integrity.json`

El siguiente alcance posible es revisar este dossier CE03 y su frontera
provisional/CE08. La evidencia auténtica, la dependencia competente CE02 y
cualquier aceptación/finalización real permanecen pendientes, sin liberar D5.
