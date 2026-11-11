# I115 — propuesta conjunta concreta, habilitación pendiente

Fecha:2026-11-10, Europe/Madrid. **PJC115 está preparada para revisión documental;
NO está lista para autorizar implementación ni captura**. Se concretan cifras,
archivos propuestos, reserva atómica, matriz NOT_RUN y condiciones bloqueantes.
No se ejecutó producto, componentes o campañas; no se cambiaron cuotas ni se
crearon perfiles, registros, autoridades o destinos. HEAD permanece
`50c49678568bae2abeefbe5fec0285f26c628283`, sin commit/push.

[Referencias por raíz y30 sitios](../validation/D5-I115-refined-reference-envelope.json) ·
[Plan estructural de bytes](../validation/D5-I115-structural-byte-plan.json) ·
[Propuesta y24 cuotas](../validation/D5-I115-joint-capacity-proposal.json) ·
[Auditoría documental](../validation/D5-I115-audit.py) ·
[Sello](../validation/D5-I115-integrity.json).

## Referencias:442305 en lugar de10945598127

Se conserva **R>=19037>16384**. La cota superior por fuente se afina a
**R<=442305**, bajo las condiciones de la ruta original completa PASS y
observación válida de I113/I114. No es ejecución, máximo alcanzable o certificado
conjunto. Se reutilizan321 raíces y E<=30129; sólo se reclasifican sus desgloses
retenidos. Ninguna cifra deriva de extrapolar13/321 ni de imponer la cuota16384.

Los88 modelos T/R conservan sus vectores P/U/S/D/O/C/H/A/L; los30 Drive conservan
sus cinco categorías y lifecycle. Los203 restantes tienen modelos de sólo
aserciones/contextos/resultados y los bindings no alcanzan los observers de
Store/Client/Remote/FixtureStore. Ese cero es una exclusión por fuente y tipo,
no una asignación de0 a trabajo desconocido. En estos203 sigue habiendo charging
de subcases, threads y resultados. El JSON conserva enlace al modelo de cada raíz.

Los cambios decisivos son:

- **Owners/membresías por raíz:** un Store y su fachada son dos objetos. Cada
  Client/Remote de los fixtures durables construye un Store nuevo; labs y capturas
  acompañan a esas factories. Para T/R, A_t<=4K_t+2P_t+2 incluye además procesos,
  conexiones y los dos módulos support. Para Drive se cuentan FixtureStore,
  test-instance de spawn, protocolos y los objetos DI07. Resultan5190 orígenes
  de owner; Q15<=321+5190=5511, conservando cada membresía por frame. No se
  multiplica321 por el inventario global de owners.
- **Contextos:** no hay creación de hilos parentales en los cierres T/R/Drive;
  los hijos multiprocessing no están instrumentados. Sus subcases<=1+Z_t.
  Para los otros203 se añade conservadoramente A_t de aserciones para scopes
  observados de hilos. Se acotan1718 subcases, y los threads por la misma cota,
  en lugar de convertir cada consulta repetida de context en un objeto nuevo.
- **Grupos/witnesses:** en una raíz T/R hay como máximo K_t identidades de Store
  y2K_t objetos de dominio, incluidas sus fachadas. G_t<=min(D_t,K_t*S_t) y
  J_t<=min(D_t,2K_t*S_t). Resultan6615 claves de grupo y9285 membresías de
  witnesses. Los grupos siguen conservando ambas autoridades y objetos físicos.
- **Copias:** retain, close y los dos enlaces por oracle copian todos los witnesses
  del grupo; se usa1+2K_t por raíz. No se descuentan por interning ni por apuntar
  al mismo objeto desde otra estructura. Se conservan997 oráculos, todos los
  record links, DI07, joins/exit y late bindings. Los30 cargos se suman por separado.

Q16 conserva la cota **por fuente E=30129 páginas no vacías**, aunque sea muy
suelta. Así,442305 no presupone que las páginas quepan en32. Los cargos late
2+1 son globales una vez, fuera de las raíces. Los8 sitios inactivos se excluyen
por el mismo MRO. El máximo suelto de192 witnesses en un grupo no es una prueba
de que una fila real exceda4096 ni de que cumpla ese límite.

## Bytes: páginas refinadas; sidecar y operandos aún condicionales

El desglose suma4945 P,5076 U,12771 S,210 D,997 O,927 C,717 H,3326 A y1160 L.
Se deriva de los modelos sellados, no de una traza nueva. Las formas pequeñas
codificadas como diccionarios literales aportan envolventes S<=800, C<=600,
A<=1536 y L<=512 bytes. Las formas máximas ilustrativas no son fixtures de
producto ni evidencia funcional: sólo verifican longitudes de estructuras JSON.
Se incluyen contexto, UUID, refs de12 caracteres, digests y testigos tipados;
las aserciones observadas tienen como máximo dos operandos.

**Falta probar P/U/D/O/H<=4096 para la carga real.** Si esa premisa se demuestra,
la suma ponderada de eventos/comas es65432505 bytes. Con overhead<=256 y el
mismo argumento de ocupación de páginas I114, la envolvente es
**32 páginas /65440697 bytes**, margen1668167 frente a64MiB. Se conservan2MiB
por página,32 páginas y64MiB acumulados. La mejora no convierte el guard4096
en una prueba de los eventos causales reales.

El plan de sidecar conserva todas las tablas, claves, witnesses, autoridades,
record_links, frames, resultados, manifiesto y metadatos. Descompone12 familias:
frames, owners, declaraciones, bindings, Drive, grupos, retained, subcases,
protocolos, links, metadatos superiores y registros DI07. Bajo las premisas de
forma declaradas suma **35474392 bytes**. **No es aún una cota demostrada del
sidecar real**: cada allowance y, en especial, los524288 bytes de metadatos
superiores deben contrastarse con los campos y pins exactos. No se sustituyen
sus desconocidos por0. El candidato34MiB es el menor MiB entero que cubre esa
suma condicional, con margen177192 bytes.

Los3072 bytes por fila de subcase incluyen hasta8 parámetros de128 caracteres
con escapes de barra inversa, más sus refs de resultados aparte. Los protocolos
cuentan mensajes y exits repetidos, sin limitar su suma imponiendo la fila4096.
El JSON retiene fórmula, cantidades, unidades y premisa de cada componente.
Todas las filas individuales siguen sujetas a4096. La envolvente suelta de grupo
`600+200*192=39000` todavía no permite certificar esa condición: hace falta
refinar por contexto/identidad los witnesses realmente simultáneos.

Tampoco hay aún cota demostrada de los operandos completos con auxiliares,
profundidad32/string4096, raw con indentación original, contexto o launcher.
Un digest pequeño no limita su entrada. El techo32MiB del fixture no prueba el
techo16MiB del observer. Estas carencias bloquean la habilitación del candidato.

## PJC115: comparación concreta, sin aplicación

Las24 cuotas figuran completas en el JSON. Sólo se plantean cuatro diferencias:

| Recurso | Actual | Candidato documental | Base y condición |
|---|---:|---:|---|
| refs |16384|442305|Cota superior por fuente, incluida finalización<=E; no factor arbitrario|
| index_sidecar_bytes |12582912|35651584 (34MiB)|35474392 estructurales, pendientes sus premisas|
| package_bytes |117444608|140513280 (134MiB+4KiB)|64 páginas+12 raw+34 sidecar+12 contexto+12 launcher, en MiB, más OWNER|
| evidence_read_bytes |268435456|297799680 (284MiB+4KiB)|2*(12+34)+3*64MiB+OWNER, calendario normal original|

Los otros20 valores se conservan como candidatos, incluidos eventos/filas4096,
2048/test,131072/campaña,2MiB/32/64MiB de páginas,12MiB raw/contexto/launcher,
128MiB únicos de ambos Readers,16MiB de operandos y archivos,4096 paths,
depth32/string4096,20s/900s. **No se ha modificado ningún contrato vigente.**

Si todos los tamaños individuales y el calendario normal se demuestran, los
37 miembros suman140509220 bytes frente a140513280 (margen4060). El Reader de
evidencia consume como máximo115343396 únicos (<134217728) y297795620 leídos
(<297799680). Contexto y launcher siguen siendo miembros aunque ese Reader no
los lea; launcher se cuenta una vez. Aumentar sidecar exige así revisar paquete
y read_bytes a la vez: el margen anterior de Reader256MiB no basta para los
nuevos máximos independientes. Son máximos de admisión, no mediciones.

El input Reader permanece separado. I96 conserva63104330 únicos,293 paths,
archivo máximo9755833 y160864585 leídos para el worker normal **original**.
Hay107570871 bytes de margen de lectura respecto al techo actual, pero la nueva
implementación/contrato/registro/certificado/autoridad no tiene todavía pins ni
calendario. Ese margen no certifica el alcance futuro. No hay resets antes/
después/finish ni suma de ledgers.

## Alcance de implementación propuesto y puertas

Se propone el namespace nuevo `testing/prospective_capture_joint/`, con capture.py,
worker.py,test_joint_capture.py,run_joint_lab.py y README.md; registro y contrato
nuevos serían `D5-JOINT-CAPTURE-REGISTRY.json` y `D5-JOINT-CAPACITY-CONTRACT.json`.
**Son nombres de diseño: no se han creado esos archivos ni un perfil funcional.**
No se asigna autoridad, launcher o destino de captura. El certificado propuesto
es `d5.joint-source-capacity-certificate.v1`, con hashes,321 bindings/12 grupos,
30 sitios,24 recursos, calendarios Reader y premisas sin UNKNOWN para admitir.

La futura reserva cubre cada cambio correlacionado de owner/grupo/witness/
autoridad/tabla/frame/evento/página antes de publicar contador o estructura.
Un lock global, entero exacto no negativo, sin descuentos al cerrar frame ni
presupuesto alternativo por hilo. No se mantiene lock durante llamada original,
I/O, espera o cleanup. Se conserva una sola llamada original y la identidad de
retorno/excepción. Fallo previo a mutación, primer diagnóstico allowlisted,
parada entre tests, cleanup/restauración y escritura única; sin reparación,
muestreo, omisión de autoridad o reintentos. Si la implementación añade nuevos
cargos, deberá actualizarse la cota antes de admitirla.

El JSON incluye **JC01–JC20 NOT_RUN**, sólo componentes sintéticos futuros bajo
300s externos. Cubren UNKNOWN/pins, los30 sitios, atomicidad y concurrencia,
escapes y eventos/filas, páginas, sidecar, paquete, ambos Readers, operandos,
primer fallo y conservación de NP00/01/02/DI07. No autorizan reejecutar CB32,
NS12/DW24/PR96/CT96 ni tests históricos o capturas.

CP01–CP07 permanecen OPEN: eventos causales, filas individuales, operandos,
raw, allowances/metadatos sidecar, contexto/launcher y Reader futuro. CP08/09
siguen NOT_AUTHORIZED: implementación/componentes y captura nueva, con decisiones
separadas cuando el expediente esté habilitable. No se solicita ahora permiso
para aplicar un candidato con esas premisas pendientes. El próximo trabajo
permitido sigue siendo documental; el corte siguiente será I116 si está libre.

La captura nueva, cuando proceda, será321/12 una vez bajo900s, con autoridad/pins/
destino nuevos; I86/I89/I92 siguen INVALID_CAPTURE y no se suman/reanudan. IR03
permanece NOT_READY. Después requerirán sus decisiones propias revisión IR03,
suficiencia/aceptación global y publicación. No se afirma cierre por estas cuentas.

Se conservan P0;83 SUPPORTS_BOUNDED/1 PARTIAL, UI04.1 parcial, D1–D4 cerrados e
I1–I20/A52 aceptado. D5/H07/G01–G07/GI globales abiertos. GI06/12/18/24/30/36/42
requieren evidencia real o decisión humana; no se sustituyen con estos documentos.
Sin proveedores/credenciales/corpus reales, consumo/reservas, activación, promoción,
despliegue, SQL/Java/Docker nuevos, D6 ni inspección/limpieza operativa dev/run_data/D4.
No se deduce persistencia o recuperación integrada de PASS aislados.
