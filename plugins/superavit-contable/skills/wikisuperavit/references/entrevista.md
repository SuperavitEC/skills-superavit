# Guía de entrevista — alta de un cliente nuevo (Modo A2)

La entrevista va ANTES de leer transcripciones. El contexto humano de Irwin te dice qué
buscar después en el material; al revés te perdés en horas de audio sin saber qué importa.

## Cómo conducirla

Conversacional, no un formulario disparado de golpe. Una o dos preguntas por turno, tomando
nota como lo haría una asistente. Irwin es contador y va al grano: si te da tres datos en
una respuesta, registralos los tres y seguí. No le preguntes lo que ya está en
`cartera-clientes.md` o en `_fuentes/` — leelo antes y confirmá, no interrogues de cero.

A medida que saques datos, volcalos a los archivos fijos correspondientes (no esperes al
final): identidad/giro/sistemas por entidad, contactos y organigrama al `grupo/`, y los
primeros criterios a `criterios-contables.md`.

## Qué necesitás sacar

### Estructura jurídica (define cuántas carpetas creás)
- ¿Es una sola empresa o un grupo de varias entidades con RUC propio?
- Por cada entidad: razón social, RUC, nombre comercial.
- ¿Hay una entidad que sea la empleadora del grupo? ¿Alguna designada agente de retención
  por el SRI? (Esto cambia mucho los criterios — confirmalo temprano.)

### Quién es quién
- Contactos del lado del cliente: quién maneja la contabilidad/operación, quién aprueba,
  quién pasa los requerimientos. Nombre, rol, correo, celular.
- Del lado de Superávit: quién lleva la cuenta.

### Giro real (no el del RUC, el de verdad)
- ¿A qué se dedica realmente? ¿Qué vende o qué servicio presta?
- ¿Es exportador, importador? ¿Maneja inventario? ¿Puntos de venta?
- Clientes y proveedores principales / recurrentes.
- ¿Algo del giro que cambie el tratamiento fiscal? (ICE, régimen especial, devolución de
  IVA, construcción, etc.)

### Sistemas
- ¿Usa Odoo? ¿Qué correo de proyecto (`<cliente>@superavit.odoo.com`)?
- Sistema de facturación electrónica.
- Bancos y cuentas; pasarelas de pago (Payphone, etc.) y a nombre de qué entidad están.
- ¿Dónde guardan los documentos?

### Criterios contables particulares (lo que más le sirve al agente de Registro)
- ¿Cómo retiene? ¿Hay casos especiales de retención propios de este cliente?
- Flujos intercompañía si es grupo (facturas entre entidades, traslados, reembolsos).
- Particularidades de su registro que un contador nuevo no adivinaría.
- ¿Maneja centros de costo? ¿Plan de cuentas estándar de Superávit o personalizado?
- Calendario: IVA mensual o semestral, qué anexos presenta, noveno dígito del RUC.

### Acuerdos con Superávit
- Alcance del servicio contratado, frecuencia de entregables, plazos, canales de
  comunicación.
- **Honorarios:** anotá la modalidad (ej. "por hora-hombre", "iguala mensual"), NO la cifra,
  salvo que Irwin pida explícitamente registrarla (ver Confidencialidad en SKILL.md).

### Material pasado (puente al backfill, Modo A3)
- ¿Qué reuniones grabadas / correos / documentos hay para indexar?
- ¿Algo perdido (audios de WhatsApp, etc.) que haya que reconstruir por dictado?

## Cierre de la entrevista
Resumí a Irwin lo que registraste y dónde, marcá los `<pendiente: ...>` que quedaron, y pasá
al backfill (destilar lo que ya esté en `_fuentes/`, Modo B).
