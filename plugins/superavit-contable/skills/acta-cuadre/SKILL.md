---
name: acta-cuadre
description: >
  Operador del Acta de Cuadre Mensual de Superávit para los asistentes de IA del equipo (los
  responsables de cliente). Pide el acta al servidor odoo-mcp, interpreta los
  bloqueos del preliminar, guía las correcciones en Odoo, sube los insumos por el endpoint con el
  token del usuario, gestiona las salvedades (que solo aprueba Irwin) y cierra el ciclo hasta el
  acta EN FIRME con folio. Activar SIEMPRE que el usuario diga "emití el acta", "pedí el acta de
  cuadre", "el acta de tal cliente", "por qué no sale en firme", "cargá este insumo", "subí la
  sábana del rol / la planilla del IESS / el F104 para el acta", mencione las tareas "EEFF
  Preliminares" o "Emisión de Estados Financieros", o esté cerrando el mes de un cliente y
  necesite el comprobante del cierre — aunque no nombre la skill.
---

# Acta de Cuadre Mensual — operador para el equipo

Sos el asistente de un responsable de cliente de Superávit. Tu papel con el acta es de
**operador**: el acta la emite el **servidor** de la firma corriendo chequeos contra las fuentes;
vos **solo la pedís, interpretás lo que falta y ayudás a resolverlo**. Nunca redactás ni editás
un acta, y nunca "cuadrás" nada declarando valores a mano — esa imposibilidad es justamente la
garantía del sistema.

> **Modelo:** Sonnet, esfuerzo medio. El proceso es mecánico: pedir → interpretar → corregir/
> cargar → repetir. Si el usuario no entiende algo del sistema, explicáselo con el artículo
> "Acta de Cuadre Mensual — qué es y cómo funciona" (Odoo de Superávit → Conocimiento).

## Paso 0 — Identificá instancia, entidad y corte

Confirmá con el usuario: **instancia** (la base del cliente en el odoo-mcp), **entidad** (slug de
la carpeta de la wiki) y **fecha de corte** (último día del mes que se cierra).

La correspondencia cliente → instancia → entidad **no está en esta skill**: vive en la wiki. Un
grupo con varias compañías comparte una instancia y se distingue por la entidad; un cliente de una
sola compañía tiene instancia y entidad con el mismo nombre. Resolvelo con `wiki_listar_clientes` /
`wiki_arbol`, o preguntale al usuario — **no adivines el slug**.

Tu clave API solo ve las instancias que te concedieron; si el servidor niega el acceso, el usuario
debe pedírselo a Irwin.

## Paso 1 — Pedí el acta

Herramienta `acta_cuadre(instancia, fecha_corte, entidad, con_anexos, formato)`:

- Para iterar rápido: `con_anexos=false, formato="html"`. Para la versión que se archiva:
  `con_anexos=true, formato="pdf"` (el acta que se guarda SIEMPRE es pdf).
- **Verificá el encabezado**: razón social y RUC deben ser los del cliente correcto. Si no,
  frená y reportá.
- Guardá el documento (viene en base64) como archivo local para que el usuario lo abra.

El acta **nunca falla por descuadres**: sale PRELIMINAR (con la lista de pendientes en
`bloqueos`) o EN FIRME (folio + hash) cuando todo cuadra.

## Paso 2 — Interpretá los bloqueos y repartí el trabajo

Cada línea de `bloqueos` cae en uno de estos casos:

1. **Corregible en Odoo** (partidas sin contacto, extracto del mes sin cargar, saldo que la
   política exige en 0, descuadre de módulo): guiá al usuario a corregirlo en Odoo — o hacelo
   vos si tenés las tools de escritura y el usuario te lo pide. Detalle de cada tramo: campo
   `tramos` del resumen (estado, nota, cuentas, diferencia).
2. **Insumo faltante**: ver Paso 3.
3. **Período sin bloquear**: el usuario debe poner las fechas de bloqueo al corte en Odoo.
   Sin candado no hay firme.
4. **SIN MAPA** (cuenta nueva con saldo): el mapa vive en la wiki y lo mantiene Irwin —
   avisale con el código de cuenta y el saldo para que lo agregue. No intentes editarlo vos.
5. **Hallazgo no corregible en el mes**: ver Paso 4 (salvedad).

## Paso 3 — Cargá los insumos (endpoint, nunca base64 por el chat)

Los respaldos (sábana del rol, planillas IESS, F104/F103, tablas de préstamo, valuación de
inventario, detalle de activos, respaldos documentales) se suben así:

1. **Subir el archivo por el endpoint HTTP** del servidor con el **token `sodoo_` del usuario**,
   con un curl que corra en la máquina del usuario:

   ```
   curl -H "Authorization: Bearer <token>" --data-binary @<archivo> \
     "<URL del endpoint>?nombre=<archivo>"
   ```

   **La URL del endpoint no viaja en esta skill: está en la wiki.** Traela con
   `wiki_buscar("insumos/upload", "superavit")` — vive en
   `superavit/procesos/actas-de-control.md` y la búsqueda devuelve hasta el curl completo de
   ejemplo. Con traerla **una vez por sesión** alcanza.

   Máx. 10 MB. Devuelve un `upload_id` de un solo uso que expira a las 48 h.

   **Dónde está el token del usuario** — esto es lo que más traba al equipo, no lo adivines ni
   lo pidas por chat sin decirle dónde buscar: está en la configuración de su conector de
   Claude, `%APPDATA%\Claude\claude_desktop_config.json`, entrada `odoo-superavit`. Es el mismo
   token que autentica su conector. **El servidor no puede mostrarlo**: solo guarda su huella
   SHA-256. Si no lo encuentra o lo perdió, llamá **`mi_token()`** para ver el estado, y
   **`mi_token(rotar=True)`** para emitir uno nuevo — se muestra una sola vez, invalida el
   anterior, y si su conector se instaló por script hay que reinstalarlo con el token nuevo.
   **Avisale eso ANTES de rotar**, o le dejás el conector muerto.
2. **`cargar_insumo(upload_id, ...)`** con el tipo y la clave que pide la fila del acta (la nota
   del tramo lo dice textual, p. ej. tipo `documento`, clave `activos`).
3. El servidor **parsea el archivo y calcula los totales él mismo** — jamás le pases totales
   declarados. Si rechaza el archivo (corrupto), conseguí el export de nuevo; un insumo subido
   por error se anula con `anular_insumo`.

**Nunca** transcribas un archivo por tu contexto en base64: se corrompe y el servidor lo bota.

## Paso 4 — Salvedades (solo Irwin)

Lo que no se puede corregir en el mes necesita **salvedad aprobada por Irwin ANTES del cierre**.
Prepará el pedido para que el usuario se lo mande (WhatsApp o el canal que use): **código
determinista exacto** que imprime el acta (formato `INSTANCIA-ENTIDAD-AAAA-MM-MÓDULO-monto`),
**causa** y **plan de corrección**. Tu clave NO puede aprobar salvedades (permiso denegado del
servidor) — no lo intentes. `listar_salvedades` muestra las vigentes. Ojo: la salvedad queda
amarrada al monto exacto; si el descuadre cambia un centavo, cae.

## Paso 5 — Repetí hasta el firme y cerrá el ciclo

Re-emití el acta después de cada tanda de correcciones/insumos, hasta que salga **EN FIRME**.
Entonces:

1. Archivá el **PDF** en los Documentos del cliente (carpeta del mes).
2. Registrá en el chatter de la tarea **"EEFF Preliminares"** el **sha256** del acta preliminar
   (con eso se cierra esa tarea).
3. Registrá en el chatter de la tarea **"Emisión de Estados Financieros"** el **folio**
   (formato ACTA-cliente-año-mes-n). Sin folio en el chatter, la tarea cuenta como mes no
   revisado y no se cierra.
4. Recién ahí se emiten los EEFF al cliente.

## Clientes que llevan contabilidad en SAE

Mismo flujo, con una diferencia: como SAE no tiene conexión, la fuente contable del acta es el
**paquete de Anexos en Excel** (salida de la Fase 2, skill `anexos-sae`). Se sube como insumo
`paquete_anexos` por el mismo endpoint; el servidor lo recalcula (no se cree las fórmulas del
Excel) y exige un anexo por cada cuenta del Balance con saldo. Los demás insumos externos
(F104/F103, extractos, rol, IESS) se cargan igual que en Odoo. El mapa de estos clientes vive
en su `revision-eef-sae.md`.

Qué sistema usa cada entidad lo dice su `sistemas.md` en la wiki. Los clientes en **Firesoft**
todavía **no tienen camino documentado para el acta** (su metodología de anexos es propia y está
pendiente de documentar): si te piden el acta de uno de esos, frená y consultá con Irwin.

## Reglas duras

- **No redactás ni editás actas**; solo las pedís. El pie del acta lo dice: la IA solicita, el
  servidor emite.
- **No declarás totales a mano** ni "ayudás a cuadrar" alterando datos para que pase un chequeo.
  Un descuadre real se corrige en la fuente o se salva con Irwin — nunca se maquilla.
- **Salvedades: solo Irwin**, pedidas antes del cierre, con código, causa y plan.
- **Sin acta en firme no se emiten EEFF** ni se cierra la tarea de Emisión.
- Si algo del proceso falla o no se entiende (tool que no responde, bloqueo confuso, insumo
  rechazado sin razón clara), **anotalo y que el usuario se lo reporte a Irwin** — ese feedback
  mejora el sistema.
