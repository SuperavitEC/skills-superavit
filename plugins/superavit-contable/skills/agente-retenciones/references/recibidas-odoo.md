# Cargar una retención recibida en Odoo — campos exactos

Complementa el procedimiento del `criterios-contables.md` del cliente (que es el que manda).
Acá está solo el **cómo mecánico** en este build de Odoo, para que no tengas que descubrirlo
cada vez.

## 1. Anti-duplicado

```
odoo_consultar(instancia, modelo="account.move",
  dominio=[["journal_id.code","=","<código del diario de retenciones de clientes>"],
           ["date",">=","AAAA-MM-01"], ["date","<=","AAAA-MM-31"]],
  campos=["name","ref","date","partner_id","l10n_ec_authorization_number","amount_total"],
  entidad="<entidad>")
```

El diario lo dice el criterio del cliente (en Superávit es `RVNTA` «Retenciones de Clientes»).
Si la retención ya está, saltala y avisá.

## 2. Ubicar la factura de venta

Del comprobante sale `numDocSustento` (sin guiones). Buscá el `account.move`:

```
odoo_consultar(instancia, modelo="account.move",
  dominio=[["move_type","=","out_invoice"], ["state","=","posted"],
           ["l10n_latam_document_number","=","001-001-000002193"]],
  campos=["name","partner_id","amount_total","amount_residual","payment_state"],
  entidad="<entidad>")
```

Si no aparece → **frená**: o la factura no está registrada, o la retención es de otra entidad.
Caso especial (retenciones de banco/tarjeta sin factura): usá la **factura en cero por banco**
que indique el criterio del cliente.

## 3. Crear el asistente

Modelo `l10n_ec.wizard.account.withhold`:

| Campo | Valor |
|---|---|
| `partner_id` | el cliente que retuvo |
| `journal_id` | id del diario de retenciones de clientes **de esa compañía** (hay uno por compañía; filtrá por `company_id`) |
| `date` | **fecha de emisión del comprobante**, no la de hoy |
| `withhold_type` | `"out_withhold"` (retención de ventas). `"in_withhold"` es emisión de compra |
| `manual_document_number` | `true` |
| `document_number` | el número del comprobante, con guiones: `001-005-000000684` |
| `related_invoice_ids` | `[[6, 0, [<id de la factura>]]]` |
| `withhold_line_ids` | una línea por cada `<retencion>` del XML |

Cada línea (`l10n_ec.wizard.account.withhold.line`):

| Campo | Valor |
|---|---|
| `invoice_id` | el mismo id de la factura |
| `taxsupport_code` | normalmente `"01"` |
| `tax_id` | el `account.tax` que corresponde al código del comprobante |
| `base` | `baseImponible` del XML |
| `amount` | `valorRetenido` del XML |

Para resolver `tax_id`, mirá qué impuesto usó una retención anterior del mismo tipo:

```
odoo_consultar(instancia, modelo="account.move.line",
  dominio=[["move_id","in",[<ids de retenciones previas>]], ["tax_line_id","!=",false]],
  campos=["move_id","name","tax_line_id","tax_base_amount","debit"])
```

o listalos con `odoo_listar_impuestos_retenciones`. **Verificá que el porcentaje del impuesto
coincida con el `porcentajeRetener` del comprobante** — si el cliente cambió de porcentaje, el
impuesto es otro.

## 4. Contabilizar

```
odoo_ejecutar_metodo(instancia, modelo="l10n_ec.wizard.account.withhold",
  metodo="action_create_and_post_withhold", ids=[<id del asistente>], entidad="<entidad>")
```

Devuelve el id del `account.move` de la retención, ya **posteado** y conciliado contra la factura.
No hay paso de borrador: el asistente crea y postea en una sola acción.

## 5. Número de autorización — obligatorio

```
odoo_escribir(instancia, modelo="account.move", ids=[<id del move>],
  valores={"l10n_ec_authorization_number": "<clave de acceso de 49 dígitos>"},
  entidad="<entidad>")
```

Se puede escribir aunque el asiento esté posteado. **Sin esto la retención no está cargada**: es
el dato con el que se sustenta el crédito tributario en un reclamo del SRI.

## 6. Control de cierre

Releé la factura de venta: el `amount_residual` tiene que haber bajado **exactamente** por el
total de la retención, y el `payment_state` pasar a `partial` (o `paid` si ya estaba cobrada la
diferencia). Si no bajó, la conciliación no se hizo y hay que revisar antes de seguir.
