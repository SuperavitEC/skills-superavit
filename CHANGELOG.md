# Cambios

## 1.5.0 — manifiestos alineados (2026-09-01)

Bump **sin cambio de contenido**, para que los dos manifiestos reconozcan la publicación de
hoy. `plugins/superavit-contable/.claude-plugin/plugin.json` ya había subido a `1.5.0` con las
skills reincorporadas; el que se había quedado en `1.1.0` es el `metadata.version` de
`.claude-plugin/marketplace.json`, que es el número que ve quien agrega el marketplace. Ningún
archivo de skill cambia con este commit.

## 1.5.0 — 2026-09-01

**Reincorpora lo que traían las versiones 1.2.0 y 1.3.0 del canal de My Uploads y que este
repositorio no tenía.** Son dos skills de procedimiento que se habían quedado atrás:

- **`agente-compras`** — actualizada.
- **`agente-retenciones`** — actualizada, y ahora trae su carpeta `references/` con
  `comprobantes-sri.md` (cómo leer los comprobantes de retención del SRI, incluidos los
  v1.0.0 viejos, que cuelgan las retenciones de `<impuesto>` en vez de `<docsSustento>`) y
  `recibidas-odoo.md` (cómo cargar en Odoo las retenciones recibidas de clientes).

Con esto **las dos fuentes quedan iguales y este repositorio pasa a ser la única**: lo que se
edite acá es lo que se distribuye, y el marketplace se publica desde acá.

> **Una diferencia deliberada respecto de la copia instalada.** La salida de ejemplo de
> `comprobantes-sri.md` mostraba la razón social de un cliente real. Este repositorio es
> **público**, así que el ejemplo va con una razón social ficticia del mismo largo — el largo
> importa, porque el script recorta el campo a 14 caracteres y eso es parte de lo que el
> ejemplo enseña. El procedimiento no cambia en nada.

## 1.4.0 — 2026-09-01

Dos correcciones en el builder de anexos (`anexos-sae/scripts/armar_anexos.py`). Las dos son
del **paquete que lee el acta de cuadre**: hasta ahora el Excel llevaba los números correctos
y el acta no podía usarlos, o los leía inflados. **No cambia ningún criterio contable.**

**Hoja `CUADRE` en el paquete de anexos.** Cada hoja de anexo imprime su caja «Saldo según
anexo / Saldo según Balance / Diferencia», pero la diferencia se escribe como **fórmula** y
solo uno de los constructores llegaba a poner esa caja. Quien lee el paquete después no
recalcula el libro ni puede confiar en el caché de Excel, así que la mayoría de los anexos
quedaba sin un total legible y su tramo salía «no evaluable». Ahora el paquete lleva una hoja
`CUADRE` con **una fila por anexo en valores duros** —anexo, descripción, hoja, saldo del
anexo, saldo del Balance, diferencia y estado—, escrita al inicializar y reescrita después de
cada `build`, detrás de BG y PYG. La regla que la justifica: **ningún total escrito como
fórmula cuenta como dato.**

**El saldo del Balance por anexo se suma CON SIGNO, no en valor absoluto.** La columna salía
de `write_state()`, que sumaba valores absolutos, e inflaba todo anexo con contra-cuenta
**exactamente al doble de esa cuenta**. El caso típico es propiedad, planta y equipo con su
depreciación acumulada: en valor absoluto el costo y la depreciación se suman en vez de
restarse. Como esa cifra es la que se compara contra el total del anexo, el defecto no se
quedaba en la presentación: producía un descuadre que no existe. Las **16 apariciones** del
mismo cálculo repartidas por los constructores se unificaron en `saldo_bg_tramo()`; el valor
absoluto queda aparte en `peso_bg_tramo()`, que sirve para **ordenar los anexos por peso y
nunca para cuadrar**. Además `build` refresca el saldo del Balance con el que realmente
comparó: el del `init` puede venir de otro export y la hoja tiene que mostrar las dos cifras
que produjeron la diferencia.

> **Sobre el número de versión.** Este repositorio venía de la **1.1.0** y salta a **1.4.0**
> para no colisionar con las versiones publicadas por el otro canal de distribución del
> plugin. Si alguna de esas versiones intermedias tocó archivos distintos de
> `armar_anexos.py`, este repositorio no las tiene: conviene contrastarlo antes de tomarlo
> como la copia completa.

## 1.1.0 — 2026-07-30

Limpieza del catálogo y refuerzo de la lectura de la wiki. **No cambia ningún criterio
contable**: cambia qué skills se distribuyen y cómo encuentran su procedimiento.

Se retiraron cuatro skills duplicadas o fuera de lugar (de 16 a 12):

- `agente-registro` → **fusionada en `agente-compras`**. Eran la misma skill con las mismas
  frases de activación, y el usuario no tenía cómo saber cuál le tocaba. Quedó `agente-compras`
  (trae la lectura por sección, las vías de compra y la regla de código→id), con la sección de
  tools completa que solo tenía `agente-registro` (`clave_sri`, XML, comprobantes del exterior,
  líneas sin OC). De paso se corrigió que el archivo terminaba cortado a mitad de frase.
- `agente-impuestos` → **eliminada** en favor de `agente-impuestos-odoo`, que tenía descripción
  idéntica y es estrictamente mejor (no hardcodea el par de cuentas, distingue `action_submit`
  de `action_validate` y documenta el bloqueo del F103 por el check de conciliación bancaria).
- `revision-balances` → **eliminada** en favor de `revision-eef-odoo`, que ya la reemplazaba
  según su propia descripción y cubre los 5 chequeos más la clasificación de cuentas.
- `wiki-query` → **retirada**. Era una skill genérica que buscaba un `wiki/index.md` local y
  nunca usaba las tools `wiki_*` de la firma: a un empleado le habría contestado que no
  encuentra ninguna wiki.
- `wikisuperavit` **se queda en el plugin** (decisión de Irwin). Es la skill con la que se
  *escribe* el vault; a quien no tiene el vault en su máquina no le hace nada, así que no
  estorba. Se le quitaron las referencias a skills que no viajan en el plugin.

Además, en las skills que quedan:

- **Patrón «puntero» documentado.** En un grupo, el procedimiento suele estar escrito una sola
  vez en una entidad y las hermanas traen una sección corta con sus propios datos que remata en
  «Seguí el procedimiento de referencia en `../<otra entidad>/criterios-contables.md`». Ahora
  `agente-compras`, `agente-conciliacion-bancaria`, `agente-tarjetas-pasarelas` y
  `agente-retenciones` dicen explícitamente que hay que leer **las dos** secciones y tomar la
  fila de su entidad.
- **Títulos de sección que no calzan.** Los títulos varían entre entidades y la búsqueda es por
  texto exacto. Las skills ahora saben caer al índice de secciones y tomar la que empieza igual,
  en vez de seguir sin criterio.
- **`agente-nomina`** ya no exigía saber de antemano cuál es la entidad empleadora para poder
  averiguar cuál es la entidad empleadora. Ahora manda al `grupo/organigrama.md`, después a
  `wiki_buscar`, y si sigue ambiguo, a preguntar.
- **`revision-eef-odoo`** contempla que `revision-eef.md` puede no existir todavía: corre en
  modo genérico, marca los hallazgos «a confirmar contra criterio» y lo dice de entrada.
- **Guarda de sistema contable.** Las skills que operan por el conector de Odoo (compras,
  retenciones, conciliación bancaria, tarjetas, impuestos, revisión de EEFF) ahora verifican
  primero **en qué sistema está la entidad** (`sistemas.md` en la wiki): si está en **SAE**, el
  trabajo es sobre archivos exportados (y la revisión va por `revision-eef-sae`); si está en
  **Firesoft**, no hay skill que la cubra y el agente frena y avisa. Antes las skills asumían
  Odoo sin chequear, y Firesoft no aparecía en el paquete.
- `agente-conciliacion-bancaria` ya no lista bancos concretos: los bancos y diarios de cada
  entidad salen del criterio.
- `acta-cuadre` ya no publica la URL del endpoint de insumos: la trae de la wiki con una
  búsqueda (`superavit/procesos/actas-de-control.md`). El repo público queda sin ninguna URL
  de infraestructura de la firma.

## 1.0.0 — 2026-07-29

Primera publicación del marketplace.

- `acta-cuadre` **v2**: el Paso 3 ahora explica **dónde encuentra el usuario su token
  `sodoo_`** (`%APPDATA%\Claude\claude_desktop_config.json`, entrada `odoo-superavit`)
  antes de mostrar el `curl`, y documenta `mi_token()` / `mi_token(rotar=True)` con la
  advertencia de reinstalar el conector si se rota. Este fue el hueco que trabó al equipo
  en el primer despliegue.
- `anexos-sae` **v2**: hoja BG ANTERIOR.
- Resto de skills operativas, en el estado del 2026-07-24.
