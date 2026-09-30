# Destilación — cómo volcar `_fuentes/` a los archivos fijos (Modo B)

El corazón del trabajo recurrente. Conviertes material crudo (correos, transcripciones) en
criterios operables que el agente de Registro pueda leer en segundos. Lee esto cuando vayas
a destilar.

## Principio

El crudo es largo y conversacional; el archivo fijo es corto y operable. No copias la
fuente: extraes el **criterio** y lo escribes claro, con su porqué cuando importa, y con la
cita de dónde salió. Piensa en el lector: el agente de Registro va a leer esto para decidir
cómo registrar una factura. ¿Qué necesita saber, y dónde lo va a buscar?

## Las fuentes y cómo leerlas

### Transcripciones (`_fuentes/transcripciones/*.md`)
Frontmatter (`cliente`, `audio-original`, `fecha-transcripcion`, `duracion`) + diálogo
`Speaker N:`. Son reuniones de levantamiento o capacitación. El oro suele estar en lo que
explica quien sabe del cliente (a veces Irwin enseñando, a veces el cliente describiendo su
operación). Ojo: hay muletillas, repeticiones y desvíos — quédate con la decisión o el
criterio, no con la charla. La fecha de la reunión suele estar en el nombre del archivo
(`2025-11-10 - Levantamiento 1.md`); úsala para la cita.

### Correos (`_fuentes/correos/*.md`)
Frontmatter (`cliente`, `fecha-original`, `remitente`, `asunto`, `internet-msg-id`,
`confianza-identificacion`) + el hilo reenviado. Suelen traer una instrucción, un acuerdo o
una consulta resuelta. La cita sale de `fecha-original` y el asunto.

Una fuente está **destilada** cuando sus hallazgos ya están en los archivos fijos citados con
su origen. Para saber si una fuente ya se procesó, busca su cita en «Decisiones de criterio»
de los archivos del cliente. Si no está, hay trabajo.

## Dónde cae cada hallazgo

| Lo que encuentras | Va a |
|---|---|
| Criterio de retención de IVA/Renta, caso especial, flujo intercompañía | `criterios-contables.md` de la entidad que aplica (secciones 1-3) |
| Cómo se configura algo en Odoo que afecta el registro | `criterios-contables.md`, sección «Particularidades» (o una subsección «Configuración en Odoo») |
| Calendario, anexos, vencimientos | `criterios-contables.md`, sección 5 |
| A qué se dedica, productos, clientes/proveedores, modelo operativo | `giro.md` de la entidad |
| Plataforma contable, bancos, pasarelas, correo Odoo | `sistemas.md` de la entidad |
| Razón social, RUC, representante legal, accionistas | `identidad.md` de la entidad |
| Una persona y su rol/contacto | `grupo/contactos.md` |
| Hito, incidencia que sienta precedente, cambio externo del SRI | `grupo/historico.md` |
| Alcance/plazos/canales del servicio | `grupo/acuerdos-superavit.md` |

### Fuentes que cruzan varias entidades
Una reunión puede tocar a todo el grupo o a dos entidades. Reparte los hallazgos a cada lado
según corresponda (un criterio de la empleadora va a su entidad; un acuerdo del grupo va a
`grupo/`). Si un mismo hecho aplica a dos entidades (ej. un flujo intercompañía entre A y B),
documéntalo en las dos desde su respectiva perspectiva (en A "como vendedor", en B "como
comprador"), no solo en una.

## Cómo escribir el criterio

- **Denso pero liviano.** El criterio operable en una o pocas frases. Subtítulo `###` por
  caso cuando hay varios en «Particularidades».
- **El porqué cuando importa.** Si el criterio existe por una razón (riesgo tributario,
  decisión del cliente), dila en una línea — ayuda al agente a no romperlo.
- **Cita siempre.** Al final del bloque: `*(Fuente: reunión 2025-11-10 Levantamiento 1.)*`
  o `*(Fuente: correo 2026-01-21.)*`. Sin cita, el criterio no es auditable.
- **Referencia, no copies, lo general.** Porcentajes y tablas del SRI/Odoo viven en
  `sistemas/`; desde el criterio pones "ver `sistemas/sri/retenciones-iva.md`".

## Deduplicar y actualizar

- Antes de agregar, relee la sección destino. Si el criterio ya está, no lo dupliques.
- Si la fuente **contradice o corrige** algo ya escrito, no borres el viejo a ciegas:
  actualiza el criterio y registra el cambio en «Decisiones de criterio» con la fecha y la
  razón (queda el rastro de por qué cambió). Si la contradicción es de fondo y no estás
  seguro de cuál vale, marca `<pendiente: confirmar con Irwin — A dice X, B dice Y>`.
- Toda decisión nueva o cambiada → una línea en «Decisiones de criterio (histórico)»:
  `AAAA-MM-DD — <decisión>: <razón>. (Fuente: ...)`.

## Confidencialidad al destilar

Repaso del freno (detalle en SKILL.md):
- Cifras contables/tributarias **del cliente** → sí van (es lo que Registro necesita).
- Honorarios/tarifas de Superávit y sueldos individuales → NO; describe la modalidad sin la
  cifra.
- Algo sensible o ambiguo → `<pendiente: confirmar con Irwin — ...>`, no lo afirmes en lo
  visible. El crudo queda intacto en `_fuentes/`; nada se pierde.

## Lo que NUNCA haces
- No tocas `_fuentes/` (ni mover, ni renombrar, ni borrar). Solo lees.
- No escribes en `sistemas/`.
- No inventas un archivo nuevo ni renombras los fijos.
- No cierras sin commit + push (ver `estructura.md` → «Cierre»).

## Al terminar
Resume a Irwin: qué fuentes destilaste, a qué archivos/entidades fue cada cosa, qué
`<pendiente>` quedaron. Después, commit + push.
