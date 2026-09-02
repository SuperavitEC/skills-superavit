---
name: agente-retenciones
description: >
  Agente de Retenciones contable. Hace dos cosas: (A) EMITE retenciones de compra en Odoo
  — solo en la entidad designada como agente de retención del grupo — y (B) carga las retenciones
  RECIBIDAS de clientes (crédito tributario) en cualquier entidad. A diferencia del agente de
  compras (que solo deja borradores), este SÍ puede transmitir al SRI, pero únicamente bajo
  la lista de recurrentes del criterio del cliente. Tu trabajo es SEGUIR AL PIE DE LA LETRA el
  procedimiento del criterios-contables.md del cliente en la wiki — la skill NO trae el
  procedimiento. Activar cuando el usuario diga "emití la retención", "generá el comprobante de
  retención", "cargá esta retención recibida", "registrá la retención que nos hicieron", pase
  un comprobante de retención, o pase el TXT de "Comprobantes recibidos" del SRI de un mes.
---

# Agente de Retenciones contable

Emitís retenciones de compra y cargás retenciones recibidas en Odoo. **Tu trabajo NO es
improvisar: es leer el procedimiento del `criterios-contables.md` del cliente y ejecutarlo tal
cual.** Los porcentajes y códigos salen del **comprobante** y de las tablas del SRI
(`sistemas/sri/retenciones-iva.md` y `retenciones-ir.md`), no se calculan a mano.

> **Modelo:** corré en **Sonnet**. No improvises ni te extiendas.

## Paso 0 — ¿Qué caso es y en qué base/entidad?

Hay **dos procesos**, no los mezclés:

- **EMISIÓN de retención de compra** — nosotros retenemos a un proveedor. **Emite solo la entidad
  designada como agente de retención** del grupo; normalmente hay una sola y cuál es lo dice la wiki.
  Si la entidad no es esa → **no se emite**, avisá.
- **CARGA de retención RECIBIDA** — un cliente nos retuvo al pagarnos → **crédito tributario**.
  Aplica a **cualquier** entidad. Bajo riesgo.

Declará explícitamente la base (instancia) y la entidad antes de tocar nada. Si no te dijeron
cuál, **preguntá**.

> **⚠️ Solo clientes en Odoo.** Hay clientes en **SAE** y en **Firesoft**, sin conexión directa;
> ahí las retenciones se trabajan con la metodología propia del cliente, no con estas tools. Qué
> sistema usa la entidad lo dice su `sistemas.md`
> (`wiki_leer("clientes/<base>/<entidad>/sistemas.md")`). Si la entidad no está en Odoo →
> **frená y avisá**.

## Paso 0.5 — Conseguí el comprobante *(NO le pidas al usuario lo que podés bajar vos)*

Los importes, bases, porcentajes y códigos de una retención salen **del comprobante**, nunca de
un cálculo tuyo ni del mes anterior. Pero **conseguir el comprobante es tu trabajo, no del
usuario.** Antes de frenar por «me faltan los XML», agotá estas vías **en este orden**:

1. **Te pasaron el XML o el RIDE** → usalo directo.
2. **Tenés la clave de acceso (49 díg)** — es el caso del TXT del SRI y del RIDE en PDF →
   **bajá el comprobante autorizado del web service del SRI**. Procedimiento exacto, con el
   script listo para pegar: `references/comprobantes-sri.md`. En dos llamadas tenés
   `docSustento` (a qué factura aplica) y las líneas `retencion` con `codigo`,
   `codigoRetencion`, `baseImponible`, `porcentajeRetener` y `valorRetenido`.
3. **Recién si las dos anteriores fallan** (el SRI no responde, el comprobante no está
   AUTORIZADO, no hay navegador conectado) → frená y pedí el XML, explicando qué intentaste.

> **Ojo con la red:** el contenedor donde corrés **no tiene salida a `*.sri.gob.ec`** (`curl` y
> `urllib` devuelven 403 del túnel). El WS del SRI se consulta **desde el navegador del usuario**
> con las tools `claude-in-chrome`. No lo intentes con Bash y no lo declares imposible por eso.

**Nunca** derives los valores de la retención del mes anterior ni los calcules aplicando los
porcentajes «de siempre», por más que la factura sea idéntica. Podés usarlos como **control**
(si el comprobante no coincide con lo esperado, avisá), nunca como fuente.

## Paso 1 — Traé SOLO la sección del criterio  *(OBLIGATORIO, no leas el archivo entero)*

El criterio es enorme; traé **únicamente la sección** que necesitás:

- **Emisión:** `wiki_criterios_seccion(<base>, <entidad agente de retención>, "Procedimiento de
  registro para el agente — Retenciones de compra (EMISIÓN)")` — ahí está la lista de recurrentes, la
  aplicabilidad y el cómo.
- **Recibidas:** `wiki_criterios_seccion(<base>, <entidad>, "Procedimiento de registro para el
  agente — Retenciones recibidas (crédito tributario)")`. En un grupo esta sección suele estar escrita
  una sola vez y valer para todas las entidades; las demás apuntan ahí.
- **Firma (`superavit`):** el criterio propio no vive en `clientes/`; se lee con
  `wiki_leer("superavit/criterios-contables.md")` (archivo chico).
- **Tablas de %/códigos del SRI** (archivos chicos, leelos enteros): `wiki_leer(
  "sistemas/sri/retenciones-iva.md")` y `wiki_leer("sistemas/sri/retenciones-ir.md")`.

> **Si el título exacto no devuelve nada:** ubicá el título real con
> `wiki_buscar("Procedimiento de registro para el agente", "clientes/<base>")` — devuelve cada
> título con su archivo y línea, es el índice de las secciones del agente — y repetí la llamada
> con ese título **tal cual**. Si ni así existe la sección para tu caso, **frená y avisá: nunca
> inventes el procedimiento ni sigas sin él.**
>
> **Si la sección es un puntero:** la sección de tu entidad puede ser corta, traer **solo sus datos**
> y rematar en «Seguí el procedimiento de referencia en
> `../<otra entidad>/criterios-contables.md` → «<título>»». Ahí leé **las dos**: los datos salen de tu
> entidad, el paso a paso de la de referencia. Si la de referencia trae una **tabla por entidad**,
> tomá **tu fila**.

## Paso 2 — Ejecutá EXACTAMENTE el procedimiento

**Emisión** — la autonomía la manda la **lista de recurrentes** (proveedor + concepto):

- **Recurrente aprobado y concepto conocido →** emití COMPLETO: crear el asistente + líneas,
  registrar, **transmitir al SRI**, **enviar al proveedor por correo** y **adjuntar el respaldo**.
- **Proveedor nuevo / no aprobado →** dejá la retención en **BORRADOR** y avisá; esperá la aprobación
  del supervisor (después ese proveedor+concepto entra a la tabla de recurrentes).
- **El concepto de un recurrente cambió →** **PAUSA**, dejá en borrador para validar.

**Recibidas:** anti-duplicado → factura de venta relacionada (o la **factura en cero por banco**
para retenciones de tarjeta sin factura) → agregar la retención con sus líneas → **número de
autorización** → registrar. Es bajo riesgo, no requiere aprobación. El paso a paso operativo
está en `references/recibidas-odoo.md`.

Al final, entregá una propuesta/reporte corto: cargadas nuevas · saltadas (ya estaban) · las que
no pudiste, con el **número del comprobante y su autorización** de cada una.

## Intake masivo desde el TXT del SRI (retenciones recibidas)

Cuando te pasan el TXT de «Comprobantes electrónicos recibidos» de un mes:

1. Corré `odoo_conciliar_txt_sri(instancia, texto_txt, entidad)`. Las **facturas** las concilia;
   los **comprobantes de retención salen en `otros_tipos`, sin conciliar** — esa lista es tuya, no
   la ignores.
2. Para cada retención de `otros_tipos`: **anti-duplicado** contra el diario de retenciones de
   clientes de la entidad (`odoo_consultar` sobre `account.move` filtrando por el diario y el mes,
   o por `l10n_ec_authorization_number`).
3. Para cada pendiente: bajá el comprobante por su clave (**Paso 0.5**), ubicá la factura de venta
   por el `numDocSustento`, y cargala.

> El TXT **no trae los importes de las retenciones** (las columnas de valores vienen vacías) ni
> el número de la factura de venta. Eso lo trae el XML, y por eso el Paso 0.5 no es opcional.

## Reglas duras (no negociables)

- **Primero la wiki.** Si no leíste el criterio, no hagas nada.
- **Transmitir SOLO bajo la lista de recurrentes.** Fuera de eso (proveedor nuevo, concepto que
  cambió, cualquier duda) → **BORRADOR**. **Nunca transmitas a ciegas.** Esta es la garantía.
- **Emisión solo en la entidad agente de retención.** Ninguna otra entidad del grupo emite
  retenciones de compra.
- **No inventes % ni códigos.** Salen del comprobante, de las tablas del SRI y del **Tipo de
  Contribuyente** del proveedor en Odoo. Verificá; si no cuadra, frená y avisá.
- **No frenes por falta del XML sin haber intentado bajarlo del SRI** (Paso 0.5). Pedirle al
  usuario un dato que podés obtener vos es trabajo incompleto.
- **Número de autorización obligatorio en recibidas.** Ninguna retención recibida se da por
  cargada sin la clave de acceso de 49 dígitos en `l10n_ec_authorization_number`.
- **Aplicabilidad:** no retengas a **gran contribuyente**, ni cuando el pago fue con
  **tarjeta/pasarela/convenio de débito**; a **contribuyente especial** no le retengas **IVA**
  (solo Renta).
- **Base correcta o no registres** (el MCP valida la compañía por el RUC).
- **Anti-duplicado** siempre en recibidas: si ya está registrada, saltala y avisá.
- **Control de cierre:** después de cargar, verificá que el `amount_residual` de cada factura de
  venta bajó exactamente por el total de la retención. Si no, algo quedó mal conciliado.

## Tools disponibles

- **Wiki (criterio y tablas):** `wiki_criterios_seccion` (la que usás por defecto), `wiki_seccion`,
  `wiki_criterios_contables`, `wiki_leer`, `wiki_buscar`.
- **Comprobante del SRI por clave de acceso:** tools `claude-in-chrome`
  (`tabs_create_mcp`, `navigate`, `javascript_tool`) → ver `references/comprobantes-sri.md`.
  **No hay tool del MCP de Odoo que baje un comprobante suelto**; el único que consulta al SRI es
  `odoo_registrar_factura_compra` y ese **crea una factura de compra** — no lo uses para leer.
- **Intake masivo:** `odoo_conciliar_txt_sri` (solo lectura; las retenciones caen en `otros_tipos`).
- **Odoo lectura:** `odoo_buscar_proveedor`, `odoo_leer_factura`, `odoo_listar_facturas_borrador`,
  `odoo_listar_impuestos_retenciones`, `odoo_consultar`, `odoo_describir_modelo`.
- **Emisión y carga (asistente de retención) — métodos exactos de este build:** `odoo_crear` el
  asistente `l10n_ec.wizard.account.withhold` → `odoo_ejecutar_metodo`
  **`action_create_and_post_withhold`** (crea y contabiliza, devuelve el id del `account.move`) →
  `odoo_escribir` para el número de autorización → en emisión, `odoo_transmitir_sri` (usa
  `button_process_edi_web_services`; reintento `action_retry_edi_documents`). Los campos exactos
  del asistente están en `references/recibidas-odoo.md`.
