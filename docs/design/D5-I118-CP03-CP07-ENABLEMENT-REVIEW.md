# I118 — dictamen CP03/CP07 para PJC115-R2

Fecha: 2026-11-10, Europe/Madrid. **PJC115-R2 sigue sin habilitarse.** Se resuelve
por fuente la rama negativa de mayor tamaño localizada en CP03 y se cierra el
inventario documental existente de CP07. No se obtiene una prueba positiva de
todos los operandos obligatorios ni se pueden asignar hashes a fuentes futuras
inexistentes. La habilitación solicitada no queda satisfecha; no se oculta tras
un cambio de nombre de las puertas. D5 abierto; IR03 NOT_READY.

[CP03: prueba DI24, hojas tipadas y censo](../validation/D5-I118-CP03-source-disposition.json) ·
[CP07: pins, presupuesto y dependencias](../validation/D5-I118-CP07-binding-review.json) ·
[Dictamen de puertas](../validation/D5-I118-gate-disposition.json) ·
[Auditoría documental](../validation/D5-I118-audit.py) ·
[Sello](../validation/D5-I118-integrity.json).

## CP03: la rama DI24 no puede tener un digest completo de 16 MiB

La fuente original de DI24 contiene exactamente:

    self.store.advance(b' '*(MAX_OBJECT+1))

MAX_OBJECT vale 32*1024*1024. El argumento tiene **33554433 bytes**. No se ha
construido ese buffer ni llamado a producto, codecs, wrappers o validadores.
Los AST, hashes y ecuaciones están en el JSON.

1. drive_request comprueba len(value)<=operand_bytes antes de strict_json y
   antes de calcular el hash de los bytes originales. Con el límite actual
   16777216, esta rama produce CAUSAL_FIELD_BUDGET.
2. El selector existente de DI24 admite ese método y ese fallo, y exige una
   excepción original de su catálogo: OBJECT_LIMIT es una de ellas. La rama
   está seleccionada por fuente; no se añade una exención genérica.
3. El fallback llama al digest I70 del diccionario de argumentos sin self,
   {'value': raw}. El escalar bytes completo costaría **33554448** y el
   diccionario completo **33554465**. El exceso hipotético del diccionario
   frente al límite es16777249. No son bytes realmente procesados hasta el final.
4. El prefijo fijo antes del payload cuesta31. Tras256 chunks de65536, el
   primer cargo que excede el techo intenta16777247. digest_value captura el
   fallo y devuelve exactamente NOT_RECORDED/OPERAND_BUDGET con sha256:null.
   El contador se incrementa antes de comprobar el límite; ese cargo fallido
   tampoco es una lectura gratuita ni un digest de un prefijo.
5. El wrapper conserva una llamada original. En FixtureStore.advance, decode
   rechaza el argumento por OBJECT_LIMIT antes de locks, carga o publicación.
   El wrapper comprueba el código permitido y vuelve a lanzar la misma excepción.
   Es una deducción sobre el camino de fuente, no una ejecución observada.

Esto **refuta la premisa universal de que todos los inputs originales obtienen
un digest completo bajo16 MiB**. No demuestra que una captura real sea inválida:
el formato existente hace visible precisamente este negativo mediante
NOT_RECORDED. validate_call_header trata primero EXCEPTION; no exige entonces
la forma de request de un retorno exitoso. No debe describirse esta rama como
un PASS de capacidad del input ni como prueba de fallo funcional.

El modelo inerte del terminal negativo mide1182 bytes, menor que el mayorante
negativo I116 de1397 y que el techo causal I117 de3546. No obliga a cambiar
cuotas, eventos, páginas, filas o el sidecar R2. Tampoco permite sustituir el
hash ausente por uno inventado, truncar datos, omitir el original o aceptar
negativos no seleccionados. Los seis checks OB118 siguen NOT_RUN.

## Qué queda probado y qué falta en CP03

Las hojas tipadas de las clases exactas PlaneError/EligibilityError se acotan
por la guarda original de un único código uppercase de hasta80 caracteres.
El digest I70 de args ocupa<=93; representación, prefijo y auxiliares de la
excepción suman<=383. La hoja de clase más larga suma<=189. Ambas caben en512
sin modificar operand_bytes. No es soporte de excepciones arbitrarias ni una
cota de contenedores de builtin o de paths.

Se conservan ORACLES I116 y el argumento grande de DR37 I117. Se añade un
censo reproducible de **62 sitios léxicos** de digest/helpers en cuatro capas,
con qualname, expresión, línea y AST hash. Incluye copias heredadas/sobrescritas;
no es el MRO activo, cobertura dinámica, un número de eventos o prueba de que
cada valor llegue a caber. No se usa para sumar cargos.

El JSON separa diez obligaciones positivas concretas: assertions; snapshots
completos; requests Store; requests Drive; receipts Store; receipts Drive;
estado/canonical independiente; inputs/resultados child y DI07; originales
retenidos/guards; compuestos tipados. Conserva las ecuaciones que deben
probarse para sus árboles originales y auxiliares, no sólo sus proyecciones.
Todas las obligaciones positivas aún no demostradas siguen OPEN_SOURCE_VALUE_CLOSURE.
No se presenta este censo como resolución global de CP03.

La rama negativa necesita una conclusión distinta a las operaciones obligatorias:
resultado esperado del guard y visibilidad del NOT_RECORDED, frente a prueba de
éxito del digest requerido. Es una aclaración de las fuentes existentes, sin
aprobar una relajación de suficiencia o de aceptación global.

## CP07: inventario exacto actual y presupuesto actualizado

Se verifican **471 pins /84917841 bytes** de evidencia documental existente,
incluidos los siete archivos I117 completos. Máximo por archivo9755833.
La unión no es una autoridad ni un perfil funcional nuevo. Se preservan los39
archivos locales previos y HEAD50c49678568bae2abeefbe5fec0285f26c628283.

Incorporar I117 añade837075 bytes y consume2511225 de la holgura de lectura
que figuraba en su propuesta. No se reutiliza el margen11340698 como si la
prueba nueva fuera gratuita. Para el protocolo versionado propuesto:

    base = 3 * 84917841 + 4852460 = 259605983
    3*S + X <= 8829473
    84917841 + S <= 134217728

S incluye los seis archivos I118, todos los archivos futuros y la autoridad;
X incluye las nuevas lecturas Input Reader adicionales al calendario fijo.
Ambos siguen desconocidos antes de tener las fuentes futuras. Sólo si X=0
se demuestra, S podría alcanzar2943157. No se presume X=0. La auditoría informa
por separado el tamaño real del expediente I118 y la holgura que deja; esto no
asigna tamaño cero al código o a la autoridad futuros.

BEFORE, AFTER y FINISH consumen cada uno una pasada completa en el mismo
Input Reader. DURING conserva lecturas frescas de targets/bindings/late checks;
no se sustituyen por snapshots ni por otro Reader. El protocolo de snapshots
inmutables para comprobaciones puras sigue siendo un cambio explícito propuesto,
no una propiedad ya verificada del código vigente. I96 describe que el runtime
original no llama a inputs.finish(); no se le atribuye retroactivamente una
tercera pasada. No se mezclan Input Reader y Evidence Reader.

El manifiesto cerrado propuesto tiene471 existentes +6 I118 +12 nombres
futuros +1 autoridad=**490 paths**. El modelo top I117 se recalcula con esos
pins antes/después: **483185 bytes**, aún bajo524288. Los hashes futuros del
modelo son placeholders de anchura y están marcados como tales. No son pins
reales ni campos adicionales del sidecar. Las otras cotas R2 no cambian:
333109 refs,30996862 bytes de sidecar,714/212 por grupo/registro.

## CP07 exacto: dependencia temporal que no puede darse por resuelta

Los doce nombres futuros siguen ausentes. No existen implementaciones R2,
registro/contrato exactos, certificado conjunto o evidencia de componentes que
puedan recibir los hashes exigidos. La autoridad y el destino siguen sin asignar.
No se inventan archivos, hashes, PASS o procedencia para completar la tabla.

El expediente concreta un orden acíclico para revisión:

| Etapa | Evidencia necesaria | Estado I118 |
|---|---|---|
| Revisión de propuesta | Pins existentes y presupuesto paramétrico finito | Preparado; no habilitación global |
| Fuentes | Código/registro/contrato exactos y grafo completo de lecturas | Ausentes; CP08 no autorizado |
| Certificado | Prueba CP03 completa, fuentes finales y calendario acotado | No creado |
| Componentes | Evidencia nueva, sellada y vinculada a fuentes | NOT_RUN; decisión separada |
| Autoridad | Pins finales aceptados, sin auto-hash ni dependencia de outputs | No creada |
| Captura | Autoridad explícita y todas las puertas de admisión satisfechas | No autorizada |

Se propone distinguir la revisión paramétrica de propuesta de la vinculación
exacta previa a captura. **No se aplica esa división de puertas ni se rebaja
CP07.** Exigir hashes finales para permitir crear las propias fuentes produce
una dependencia temporal imposible; eliminarlos de la admisión de captura
sería un cambio injustificado. La revisión tiene que resolver el orden de esas
etapas, con CP03 global igualmente pendiente.

Un registro no debe fijar el hash de un certificado que a su vez fija ese mismo
registro. Las evidencias de componentes llegan después de las fuentes. La
autoridad es consumidora final de pins y no incluye su propio hash. Sus lecturas
y finish deben contarse en el grafo real. Los futuros tests-raw/results/integrity
son evidencia de componentes previa a captura, nunca outputs de la captura
usados para autorizarla. El sello I118 omite su auto-hash expresamente.

## Validación y conservación

La auditoría usa sólo stdlib para hashes, AST, JSON y aritmética. Comprueba la
expresión DI24, el catálogo y las guardas, las hojas tipadas, todos los pins,
el censo léxico reproducido, el modelo top y los márgenes. No ejecuta tests ni
componentes ni importa producto/runner. No cambia cuotas, fuentes de producto,
perfiles, autoridades o destinos; no hace commit/push ni inspección/limpieza
operativa de dev/run_data/D4. La pasada documental PASS no constituye un
certificado numérico conjunto o evidencia funcional nueva.

P0;83 SUPPORTS_BOUNDED/1 PARTIAL y UI04.1 permanecen. D1–D4 cerrados;
I1–I20/A52 aceptados. D5/H07/G01–G07/GI globales abiertos. Las siete obligaciones
humanas/reales GI06/12/18/24/30/36/42 siguen pendientes. I86/I89/I92 permanecen
INVALID_CAPTURE, sin reanudación ni mezcla. Sin proveedores, credenciales,
corpus reales, consumo, reservas, activación, promoción, despliegue, D6 o nuevas
operaciones SQL/Java/Docker. No se solicita aprobación de ejecución incompleta.
