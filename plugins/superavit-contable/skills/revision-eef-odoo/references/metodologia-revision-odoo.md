# Metodología — Revisión y corrección de EEFF en Odoo (Fase 1)

Manual genérico de la Fase 1 sobre Odoo. Lo específico de cada cliente vive en su
`revision-eef.md` en la wiki. Este archivo es común a todas las bases de Odoo de la firma y lo
comparten las tres fases (revisión → anexos → análisis).

## La diferencia con SAE (por qué esto es más barato)

En SAE no hay API: el empleado exporta mayor + BG + PYG + reportes de módulo y Python los muele. En
Odoo, el MCP **lee la base en vivo** y las tools de chequeo **muelen del lado del servidor**: cada
una devuelve un resumen chico (un saldo por cuenta, un descuadre por módulo, un conteo de partidas).
Consecuencia práctica:

- **Nunca leas `account.move.line` crudo en masa.** Son decenas de miles de líneas; te funden el
  contexto y no aportan. Para eso están `odoo_balance_comprobacion`, `odoo_cuadre_modulos`,
  `odoo_partidas_conciliables`, `odoo_lineas_sin_contacto`.
- **`odoo_consultar` / `odoo_agrupar` son un zoom,** para mirar las pocas líneas de UNA cuenta que
  no cuadra, o los apuntes de UN tercero. No para recorrer toda la contabilidad.
- **No hay "re-exportar":** para verificar una corrección, re-corrés el chequeo o
  `odoo_balance_comprobacion` y mirás el saldo nuevo. Es instantáneo.
- **No hay "mes bloqueado" nativo del flujo,** pero Odoo tiene **fechas de cierre / lock dates**
  (Contabilidad → Configuración → Fechas de cierre). Se sugiere al usuario ponerlas al terminar,
  para que las cifras no se muevan mientras se arman los anexos.

## Las 2 etapas (frontera dura)

Igual que en SAE: **estructura** primero, **consistencia** después. No se pasa a la Etapa 2 sin la
Etapa 1 cerrada al 100% y re-verificada. La razón: la consistencia (cuadre de módulos) se juzga mal
si todavía hay apuntes mal clasificados moviéndose entre cuentas.

### Etapa 1 — Estructura
Fuente: `odoo_balance_comprobacion` + criterio.
- **Saldos contrarios a su naturaleza** — respetando contra-cuentas (ver abajo).
- **Cuentas mal clasificadas** — naturaleza + `clasificacion_esperada` del criterio.
- **Transitorias sin cerrar** — con saldo ≠ 0 y que el criterio decía cerrar a esa fecha.
- **Partida doble** — en Odoo los posteados están cuadrados; solo mirás borradores descuadrados.

### Etapa 2 — Consistencia
Fuente: `odoo_cuadre_modulos`, `odoo_partidas_conciliables`, `odoo_lineas_sin_contacto` + criterio.
- **Cuadre de módulos** (CxC / CxP / inventario).
- **Conciliaciones pendientes** (partidas cruzables sin matchear).
- **Cuentas sin contacto.**
- **Detalles/orígenes no identificados** de cuentas misceláneas.

## Trabajo por partes y revelación progresiva

El agente **no intenta todo de una vez**. Dos motivos: al usuario le sirve más un flujo dosificado que
un muro de texto, y así puede validar/dar OK sobre porciones manejables.

- **Por grupos de cuentas.** Si el corte tiene muchas cuentas, se avanza por grupos naturales (bancos
  y caja → CxC → CxP → nómina/IESS → impuestos → transitorias → resto), con OK para pasar de uno al
  siguiente. No se corrige un grupo hasta cerrar el anterior.
- **Lista accionable, no prosa.** Al terminar un chequeo, presentá las cuentas marcadas como lista:
  **código + nombre + saldo + estado** (requiere acción / esperado). Encabezá por las accionables.
  Nada de conteos vagos ni de relleno («10 pero 7 no son error»): el usuario ve cada cuenta con su
  valor, incluidas las esperadas. El **detalle** que se ofrece aparte es el **origen** de un hallazgo
  (de dónde sale el saldo: apuntes, terceros), y se entrega solo si lo piden.
- **Nombres de cuenta en español (consistencia).** Identificá cada cuenta por su **código** (no
  ambiguo) + su nombre. Si el plan tiene cuentas con nombre en **inglés** (pasa cuando parte del plan
  salió de un template en inglés y quedó mezclado ES/EN), es un **hallazgo de consistencia**: la
  corrección es **renombrarlas a español en Odoo**, en lote y con OK, una sola vez (receta R6). No las
  traduzcas solo al vuelo: arreglar la fuente deja legibles todas las revisiones futuras y también los
  reportes que el cliente ve desde Odoo, sin costo recurrente. (Verificá antes que el nombre esté
  guardado en inglés y no sea una traducción faltante: si la base solo tiene español instalado y aun
  así el nombre viene en inglés, el valor está en inglés y se renombra.)
- **OK puntual.** Cada corrección se muestra antes → después y se aplica solo con el OK de esa
  corrección. El OK no es "para todo".

Este mismo criterio (revisar cosa por cosa, con el OK del usuario apoyado en los reportes que salen del
propio Odoo) es el que gobierna la Fase 2: en Odoo no se arma un Excel de anexos; el usuario aprende a
reproducir en Odoo la información que cuadra con cada cuenta del Balance.

## Citar el dato crudo (anti-confabulación)

Antes de interpretar, **repetí textual el número que devolvió la tool**: cuántas cuentas con saldo,
cuántas marcadas contrarias, qué diferencia por módulo, cuántas líneas sin contacto, qué saldo. No lo
parafrasees de memoria ni lo redondees a ojo, y **no completes con lo que "debería" dar**. Si el número
no salió de una llamada real a la tool en esta sesión, no lo afirmes. Un resumen inventado (cifras que
no coinciden con la base, hallazgos que no existen) es peor que no reportar: hace perder el tiempo del
supervisor y destruye la confianza en el agente.

## Todo el Balance debe quedar perfecto (nada se descarta)

No hay umbral de materialidad: **nada se marca como «ruido» ni se descarta por monto**. El objetivo es
dejar **cada cuenta del Balance justificada o corregida**, hasta los saldos de centavos. Un −0,33 o un
−8,16 no se ignoran: se rastrean y se resuelven igual que un saldo grande. La materialidad puede
ordenar la PRIORIDAD (qué se ataca primero), nunca sirve para dejar algo sin resolver.

## Permitir conciliación — el saldo real sale de los cruces

En Odoo, el **saldo que importa** de una cuenta conciliable no es el bruto sino lo que queda **abierto
tras los cruces** (conciliaciones). El flag **"Permitir conciliación"** (campo `reconcile` de
`account.account`, que `odoo_leer_plan_cuentas` ya devuelve) es lo que habilita esos cruces.

- Las tools `odoo_partidas_conciliables` y `odoo_lineas_sin_contacto` ya operan sobre las cuentas
  conciliables; ahí es donde el saldo real se determina por el matcheo débito↔crédito.
- **Config faltante = hallazgo:** si una cuenta que por su naturaleza debería ser conciliable (CxC,
  CxP, anticipos, transitorias por cruzar) **no** tiene el flag, coméntalo (en genérico, "a
  confirmar contra criterio"). Sin el flag no se puede determinar su saldo abierto real.
- **Excepción — no todo lleva el flag:** Odoo **no deja** marcar como conciliables ciertos grupos
  porque se concilian de otra manera. El caso típico es **bancos y caja**, que se concilian contra el
  **estado de cuenta bancario** (conciliación bancaria), no por el flag de la cuenta. Esos **NO son
  hallazgo de configuración**.
- **Contactos:** en las cuentas comerciales (CxC/CxP) y donde el criterio lo pida, las líneas deben
  llevar contacto (`partner_id`). Reportá las que falten. Nómina, IESS, impuestos, transferencias
  internas y saldos iniciales suelen ir legítimamente sin contacto — no las infles como hallazgo.

## Contra-cuentas (NO son error del chequeo de naturaleza)

Llevan saldo invertido **por diseño**: depreciación y amortización **acumulada** (activo con saldo
acreedor), **provisiones / deterioro** (incobrables), **anticipos** a proveedores o de clientes.
`odoo_balance_comprobacion` las marca `saldo_contrario`. **Listalas igual, con su código y saldo**,
marcadas como «contra-cuenta, saldo invertido esperado» (sin acción): el usuario debe verlas, no las
escondas en un conteo. Lo que NO hacés es tratarlas como error. Y listá aparte, encabezando, las que
sí requieren revisión (las que no son contra-cuenta ni excepción del criterio).

## Qué es FORMA (lo corregís aquí) y qué es FONDO (Fase 3)

- **Forma** (Fase 1): un apunte en la cuenta equivocada, una transitoria que quedó abierta por un
  cruce que faltó, una partida cruzable sin conciliar, una línea sin contacto, algo cargado fuera de
  su módulo. Son errores de **presentación/estructura** que se corrigen sin discutir la operación de
  fondo.
- **Fondo** (Fase 3): cartera muy antigua, saldo de un empleado/tercero inactivo, un activo
  totalmente depreciado que sigue depreciándose, un saldo que no tiene sentido para el giro. Eso
  **no se toca acá**: se anota como observación y lo trabaja la Fase 3 (análisis), con correcciones
  agendadas para el mes siguiente.

Ante la duda de si algo es forma o fondo: si corregirlo cambia **cómo se presenta** un saldo que ya
es correcto de fondo → forma; si cuestiona **si el saldo debería existir** → fondo.

## Recetas de corrección en Odoo

Regla transversal: **mostrar antes → después, pedir OK, aplicar, verificar.** Preferir siempre el
fix **no destructivo**. Todas las llamadas llevan `instancia` y la entidad/RUC.

### R1 — Reclasificación (cuenta equivocada, mal clasificada, saldo contrario por mala cuenta)
El fix limpio y auditable es un **asiento de reclasificación** en un diario tipo Varios /
Miscellaneous, **con fecha en el período abierto**, que mueve el saldo de la cuenta equivocada a la
correcta. NO edites el asiento original si ya está posteado y declarado.

- Identificá el monto exacto a reclasificar (zoom con `odoo_consultar` sobre las líneas de la cuenta).
- Creá el asiento con `odoo_crear` (modelo `account.move`, `move_type='entry'`, `journal_id` del
  diario Varios, `line_ids` con las dos patas: Dr/Cr moviendo de la cuenta mal a la cuenta bien;
  conservá el contacto y la **distribución analítica** si la línea original la tenía).
- Posteá con `odoo_contabilizar` (action_post) **tras el OK**.
- Verificá con `odoo_balance_comprobacion`: la cuenta origen baja, la destino sube.

### R2 — Cerrar una transitoria que quedó abierta
Si la transitoria debía netear en cero y quedó con saldo por un cruce que faltó:
- Si el saldo debe **cruzarse contra otra partida** (p. ej. pagos en tránsito contra el banco):
  es conciliación → **R3**.
- Si el saldo debe **reclasificarse a su cuenta final** (según el criterio): es reclasificación → **R1**.
Nunca "cierres" una transitoria contra resultados por comodidad; seguí lo que diga el criterio.

### R3 — Conciliar partidas cruzables (`cruzable=true`)
Débito y crédito por el mismo valor que debían matchearse. No cambia saldos; ordena la cuenta.
- Tomá los `id` de las líneas a conciliar (los da `odoo_partidas_conciliables`, o zoom con
  `odoo_consultar` sobre `account.move.line`).
- Conciliá con `odoo_ejecutar_metodo` (modelo `account.move.line`, método `reconcile`, sobre los
  ids) **tras el OK**.
- Verificá que `odoo_partidas_conciliables` ya no las lista.

### R4 — Poner el contacto que falta
Cuenta que requiere contacto y tiene líneas sin `partner_id`.
- Confirmá cuál es el contacto correcto (del documento origen; con certeza, no por inferencia).
- `odoo_escribir` sobre `account.move.line` fijando `partner_id`. En Odoo el contacto de una línea
  posteada suele ser editable sin reabrir; si la base no lo permite, decilo y dejalo como hallazgo.
- Verificá con `odoo_lineas_sin_contacto`.

### R5 — Borrador descuadrado o mal armado (raro)
Si es un asiento en **borrador** (no posteado), se puede editar directo con `odoo_escribir` y
postear con `odoo_contabilizar` tras el OK. Solo borradores.

### R6 — Renombrar cuentas a español (consistencia de idioma)
Cuando parte del plan tiene el nombre en inglés y el resto en español, se unifica a español. Es
**seguro**: cambia solo el nombre visible, no toca el código, los saldos ni los asientos. Flujo:
leé el plan (`odoo_leer_plan_cuentas`), armá la lista **código / nombre actual (inglés) / propuesta
en español**, mostrala para OK, y escribí con `odoo_escribir` sobre `account.account` (solo el campo
`name`), en lote. Es una limpieza **de una sola vez** por cliente: después toda revisión y todo
reporte quedan en español, sin costo de tokens recurrente. No inventes códigos ni cambies estructura,
solo el `name`. Traducciones típicas del plan EC: «Funds in Transit» → Fondos en tránsito;
«Outstanding Payments» → Pagos pendientes; «Accounts receivable...» → Cuentas por cobrar...;
«Local accounts and notes payable» → Cuentas y documentos por pagar locales; «Retained earnings» →
Utilidades retenidas; «Sale of goods» → Venta de bienes.

## Casitos (patrones que aparecen seguido)

- **CO-1 — la transitoria que netea en cero.** Tiene movimiento sin conciliar adentro pero saldo
  neto 0. **No es hallazgo de saldo** (chequeo de estructura); si tiene partidas cruzables sin
  matchear, es chequeo 4 (conciliación), y se ordena con R3. El saldo real por depurar, si existe,
  está en OTRA cuenta del balance.
- **CO-2 — código de cuenta vacío en multicompañía.** Si `odoo_balance_comprobacion` devuelve
  `code=false` en algunas cuentas, es que no pasaste la entidad/compañía. Volvé a llamar con la
  entidad. En Odoo 19 el código de cuenta es por compañía.
- **CO-3 — descuadre de módulo que en realidad es fondo.** Un cuadre de CxC/CxP que no cierra puede
  venir de cartera antigua o registros con fecha hacia atrás. Si es de **forma** (algo cargado fuera
  del módulo), reclasificá (R1); si huele a **fondo**, no lo fuerces: observación para Fase 3.
- **CO-4 — período cerrado/declarado.** Cualquier corrección que toque un mes ya declarado al SRI
  NO se aplica: se escala. La reclasificación, si procede, se hace con **fecha en el período
  abierto**, nunca reabriendo lo declarado.
- **CO-5 — documento con XML autorizado.** Jamás reabrir ni re-transmitir. Si el error está en un
  documento ya autorizado, el camino es una nota de crédito / ajuste que decide el humano, no vos.

## El lazo de conocimiento

Si al corregir el cliente aclara algo que sirve para la wiki (una particularidad, una transitoria
nueva, un responsable), anotalo y pedile al usuario mandarlo a
`conocimiento@superavitasesores.com.ec` en el cuerpo del correo con la etiqueta `Cliente: <slug>`.
El destilador lo suma al `revision-eef.md`. No frena el run: seguís con el `.md` local que ya tenés.

## Modo genérico (sin `revision-eef.md` del cliente)

Si el archivo no existe: avisá que falta, corré los chequeos igual y marcá cada hallazgo como
**"a confirmar contra criterio"** (sin la regla del cliente hay falsos positivos: transitorias que
ese cliente cierra a fin de año, contra-cuentas no listadas, cuentas que legítimamente van sin
contacto). **No corrijas en modo genérico** salvo lo inequívoco (una partida claramente cruzable sin
conciliar); lo demás queda como hallazgo para confirmar. Recomendá crear el archivo.
