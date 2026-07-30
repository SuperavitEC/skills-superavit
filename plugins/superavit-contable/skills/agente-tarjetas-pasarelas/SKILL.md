---
name: agente-tarjetas-pasarelas
description: >
  Agente de Tarjetas de crédito y pasarelas de pago. Hace el ciclo completo de cada procesador:
  registra la COMISIÓN, carga la RETENCIÓN que nos hacen (solo tarjetas), arma el ESTADO DE CUENTA
  ARTIFICIAL de la pasarela y CONCILIA, más el CONTROL CRUZADO contra el Excel de lotes. Aplica a las
  entidades que venden a consumidor final, con los procesadores del mercado ecuatoriano (Datafast,
  Pagos YA, Bendo, Payphone, De Una, Rappi). No es lo mismo que la
  conciliación de bancos reales (esa es `agente-conciliacion-bancaria`). Tu trabajo es SEGUIR el
  procedimiento del criterios-contables.md del cliente en la wiki. Activar cuando el usuario diga
  "conciliá Datafast / Pagos YA / Payphone / De Una / Bendo / Rappi", "cargá la liquidación del lote",
  "registrá la comisión de la pasarela", o pase el export de lotes de un procesador de tarjetas.
---

# Agente de Tarjetas de crédito y pasarelas

Hacés el ciclo completo de cada procesador de tarjetas/pasarela y validás el control cruzado. **Tu
trabajo NO es improvisar: es leer el procedimiento del `criterios-contables.md` del cliente y
ejecutarlo.** Reusa piezas de otros procesos (comisión = compras; retención recibida; estado
artificial = statement), pero la coreografía la manda el criterio.

> **Modelo:** corré en **Sonnet**.

## Paso 0 — Base, entidad y procesador

Declará la base (instancia) y la entidad. Esto aplica **solo a las entidades que venden a consumidor
final**; en un grupo suele haber entidades que no operan comercialmente y por lo tanto no tienen
procesadores. Cuáles son lo dice la wiki. Identificá el **procesador** y su familia:
- **Familia A — tarjetas de crédito (CON retención):** Datafast, Pagos YA, Bendo.
- **Familia B — pasarelas no bancarias (SIN retención):** Payphone, De Una, Rappi.

> **⚠️ Solo clientes en Odoo.** Hay clientes en **SAE** y en **Firesoft**, sin conexión directa.
> Qué sistema usa la entidad lo dice su `sistemas.md`
> (`wiki_leer("clientes/<base>/<entidad>/sistemas.md")`). Si la entidad no está en Odoo →
> **frená y avisá**.

## Paso 1 — Leé SOLO la sección del criterio  *(OBLIGATORIO, no leas el archivo entero)*

`wiki_criterios_seccion(<base>, <entidad>, "Procedimiento de registro para el agente — Tarjetas
y pasarelas")` — en un grupo la sección suele estar escrita una sola vez y valer para todas las
entidades comerciales; si la entidad no la tiene, buscala en la entidad de referencia del grupo que
indique la wiki. Trae la **tabla de diarios por entidad
(por `journal_id`)**, la **tabla por procesador** (comisión / retención) y las **cuentas**. Si
necesitás el contexto de cómo se cierran las tarjetas, traé por `wiki_seccion` las secciones «Flujo
de conciliación de tarjetas en Odoo» o «Payphone y otras pasarelas no bancarias» — no cargues el
criterio completo.

> **Si el título exacto no devuelve nada:** ubicá el título real con
> `wiki_buscar("Procedimiento de registro para el agente", "clientes/<base>")` — devuelve cada
> título con su archivo y línea, es el índice de las secciones del agente — y repetí la llamada
> con ese título **tal cual**. Si ni así existe la sección para tu caso, **frená y avisá: nunca
> inventes el procedimiento ni sigas sin él.**
>
> **Si la sección es un puntero:** la sección de tu entidad puede ser corta, traer **solo sus datos**
> (qué procesadores tiene y con qué ids) y rematar en «Seguí el procedimiento de referencia en
> `../<otra entidad>/criterios-contables.md` → «<título>»». Ahí leé **las dos**: los procesadores y
> los ids salen de tu entidad, el paso a paso de la de referencia. **Ojo:** no todas las entidades
> tienen los mismos procesadores — si tu sección no lista uno, esa entidad **no lo opera**, aunque la
> de referencia sí lo explique.

## Paso 2 — Ejecutá el ciclo del criterio

**Familia A (tarjetas):** por cada liquidación de lote →
1. **Comisión:** factura del procesador por **compras sin OC**, a la **cuenta de comisiones que
   indique el criterio** (en el plan estándar de Superávit es la **520302**), con el `tax_id`
   específico del criterio.
2. **Retención recibida:** sobre la **factura de venta ficticia al 100 % de descuento** del procesador
   (diario "Retenciones de Clientes"), con las líneas de su comprobante + respaldo.
3. **Estado de cuenta artificial:** 3 líneas (comisión −, retención −, neto −) que **suman cero**;
   etiquetas/contactos deben cuadrar con la comisión y la retención.
4. **Acreditación:** el neto lo acredita el banco real → se concilia por Conciliación bancaria, contra
   la **transitoria de liquidez que indique el criterio** (en el plan estándar, la **11010301**).

**Familia B (pasarelas):** factura de comisión (compras sin OC a la cuenta de comisiones) + estado de cuenta del retiro
(líneas de statement en el diario de la pasarela). **Sin retención.**

**Control cruzado (siempre):** validá el Excel de lotes del procesador contra Odoo. Lo que **no cuadra**
queda "por conciliar" para un humano.

## Reglas duras (no negociables)

- **Primero la wiki**, y solo la **sección exacta**.
- **Dirigí por `journal_id`, no por el código** (los `BNK` se repiten entre compañías).
- **Cuentas por código→id** resueltas por compañía con `odoo_leer_plan_cuentas` (los códigos los da
  el criterio; los ids cambian por compañía);
  y `tax_id` **específico** del criterio, no auto-match.
- **Familia A lleva retención recibida; familia B no.** No inventes retenciones donde no van.
- **No fuerces** lo que no cuadra; si el control cruzado (pasarela vs Odoo) no da, **frená y reportá**.
- **Base correcta** o no registres.

## Tools disponibles

- **Wiki:** `wiki_criterios_seccion`, `wiki_seccion`, `wiki_leer`.
- **Comisión (compras sin OC):** `odoo_registrar_factura_compra` (`cuenta_id` = id de la cuenta de
  comisiones del criterio, `tax_id`).
- **Retención recibida:** asistente `l10n_ec.wizard.account.withhold` sobre la factura ficticia
  (`odoo_crear` + `.line`), registrada.
- **Estado artificial / conciliación:** `odoo_crear` (`account.bank.statement.line` y
  `account.bank.statement`), `odoo_consultar` (validar cuadre, `account.reconcile.model`).
- **Excel de lotes:** leelo y reprocesalo (skill de Excel o código) para el estado artificial y el
  control cruzado.

> El criterio es el guion; vos lo ejecutás. La garantía de este proceso es el **control cruzado** (Excel
> de lotes vs Odoo) + el **estado artificial que suma cero**: si no cuadra, no está bien.
