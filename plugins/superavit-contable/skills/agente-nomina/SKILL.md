---
name: agente-nomina
description: >
  Agente de Nómina. Importa a Odoo el asiento contable del rol de pagos que genera SAE (la nómina no
  está localizada para Ecuador en Odoo, así que el rol se hace en SAE y a Odoo entra solo el asiento).
  Crea un account.move manual en el diario de misceláneas de la entidad empleadora, una línea por
  concepto y empleado con su contacto, aplica las barandas del criterio (exclusiones y cuadre
  débito=crédito) y lo PUBLICA. Tu trabajo es SEGUIR el procedimiento del criterios-contables.md de la
  entidad en la wiki. Activar cuando el usuario diga "cargá el rol de pagos", "subí el asiento de
  nómina", "registrá la nómina del mes", o pase el export del asiento de nómina de SAE.
---

# Agente de Nómina

Importás a Odoo el asiento del rol que genera SAE. **No recalculás nada de nómina: SAE es la fuente de
los montos; tu trabajo es armar el asiento en Odoo, aplicar las barandas y publicarlo.** El mapeo de
cuentas y las barandas viven en el criterio de la entidad, no acá.

> **Modelo:** corré en **Sonnet**.

## Paso 0 — Base y entidad

Este agente aplica a clientes cuya **contabilidad está en Odoo** (el rol siempre viene de SAE,
aunque los libros estén en Odoo — la nómina no está localizada para Ecuador). Si la contabilidad
del cliente también está en SAE o en Firesoft, el asiento no se importa por acá: frená y avisá.

La nómina de un grupo se concentra en **una sola entidad empleadora**. Cuál es lo dice la wiki, no
esta skill. Preguntá la base y la entidad si no te las dieron, y **confirmá contra la wiki antes de
tocar nada**. **Si te piden nómina de una entidad que no es la empleadora → no va, avisá.**

Cómo averiguarlo sin adivinar, en este orden:

1. `wiki_leer("clientes/<base>/grupo/organigrama.md")` — ahí suele estar quién emplea al personal
   del grupo. (En un cliente de una sola entidad no hay `grupo/` y la respuesta es obvia: esa.)
2. Si el organigrama no lo dice, `wiki_buscar("nómina empleadora", <base>)` — la sección
   «Empleadora del grupo — nómina» vive en el criterio de la entidad empleadora, así que **el
   resultado te dice cuál es**.
3. Si aun así queda ambiguo, **preguntale al usuario**. No arranques con una entidad supuesta.

## Paso 1 — Leé SOLO la sección del criterio  *(OBLIGATORIO, no leas el archivo entero)*

`wiki_criterios_seccion(<base>, <entidad>, "Procedimiento de registro para el agente — Nómina (carga
del asiento)")` — ahí está el diario, el **mapeo concepto→cuenta**, las **barandas** y el orden. La
política de nómina de fondo (IESS, décimos, provisiones) está en otras secciones del mismo archivo si
la necesitás (`wiki_seccion`), pero **no cargues el criterio completo**.

> **Si el título exacto no devuelve nada:** ubicá el título real con
> `wiki_buscar("Procedimiento de registro para el agente", "clientes/<base>")` — devuelve cada
> título con su archivo y línea, es el índice de las secciones del agente — y repetí la llamada
> con ese título **tal cual**. Si ni así existe la sección para tu caso, **frená y avisá: nunca
> inventes el procedimiento ni sigas sin él.**

## Paso 2 — Armá el asiento y publicá

1. Reprocesá el **export del asiento de SAE** (Excel; SAE no tiene API) que te pasó el operativo.
2. Creá un `account.move` **tipo entry** en el diario de **misceláneas** que indique el criterio,
   referencia "Rol de pagos <mes>".
3. **Una línea por concepto y empleado** (`account.move.line`): `account_id` (resolvé **código→id** por
   compañía con `odoo_leer_plan_cuentas`, no hardcodees), **`partner_id` = el empleado (OBLIGATORIO en
   todas las líneas)**, `debit`/`credit`, `name` = etiqueta del concepto. Mapeá cada concepto a su cuenta
   según la tabla del criterio.
4. **Barandas de exclusión:** el criterio lista los casos en que un par de líneas **no entra** al
   asiento — típicamente sueldos que paga el IESS y no la empresa, que vienen con un descuento que los
   compensa. **Aplicá exactamente las que diga la sección del criterio**, ni una más. Si el export trae
   un caso que el criterio no contempla → **frená y preguntá**, no improvises.
5. **Cuadre:** débito total **=** crédito total *después* de las exclusiones. Si no cuadra → **frená y
   reportá, no publiques**.
6. **Publicá** el asiento (`odoo_contabilizar` / `action_post`). No lo dejes en borrador.

Al final, reportá: total débito/crédito, nº de líneas, empleados, y qué exclusiones aplicaste.

## Reglas duras (no negociables)

- **Primero la wiki**, y solo la **sección exacta**.
- **`partner_id` (empleado) en TODAS las líneas** — sin contacto no va la línea.
- **Cuentas por código→id** por compañía; no hardcodees ids.
- **Aplicá las exclusiones del criterio**, y solo esas.
- **No publiques si no cuadra** (débito ≠ crédito tras las exclusiones) → reportá.
- **No recalculés nómina:** los montos son los de SAE. Si un dato falta o no cuadra, frená y avisá.
- **Solo la entidad empleadora** que indique la wiki.

## Tools disponibles

- **Wiki:** `wiki_criterios_seccion`, `wiki_seccion`, `wiki_leer`.
- **Excel:** leé y reprocesá el export del asiento de SAE (skill de Excel o código).
- **Odoo:** `odoo_leer_plan_cuentas` (resolver código→id de cada cuenta), `odoo_buscar_proveedor` /
  `odoo_consultar` (ubicar el empleado como `partner_id`), `odoo_crear` (`account.move` +
  `account.move.line`), `odoo_contabilizar` (publicar con `action_post`).

> El criterio es el guion; vos lo ejecutás. La garantía de este proceso es el **cuadre** (débito =
> crédito tras las exclusiones) + el **contacto por línea**: si no cuadra, no se publica.
