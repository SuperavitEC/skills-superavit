# Cambios

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
