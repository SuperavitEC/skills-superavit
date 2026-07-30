---
name: wikisuperavit
description: >-
  Gestiona el ciclo de vida de las wikis de cliente de Superávit Asesores (vault Obsidian
  en C:\Users\Irwin\wikis-superavit). Úsala SIEMPRE que Irwin diga "tengo un cliente nuevo",
  "dá de alta este cliente", "armá la wiki de tal cliente"; cuando pida "destilá / volcá /
  pasá las transcripciones o los correos a los criterios", "actualizá la wiki / los criterios
  contables de un cliente o entidad"; cuando invoque "/wikisuperavit"; o en la destilación
  diaria (Motor 2). Crea la estructura de la wiki, entrevista a Irwin, y destila el material
  crudo de `_fuentes/` (correos + transcripciones) hacia los archivos fijos que leen los
  agentes Experto y de Registro, respetando un contrato estricto de rutas y un freno de
  confidencialidad. NO uses una skill genérica de wiki para las wikis de cliente: su estructura es fija a
  propósito y una skill genérica de wiki la rompería. Activala aunque Irwin no nombre la skill, siempre que
  el contexto sea armar, alimentar o actualizar la wiki de un cliente de la firma.
---

# /wikisuperavit — Ciclo de vida de las wikis de cliente

Esta skill mantiene las wikis de cliente de Superávit: la base de conocimiento por cliente
que consultan el **agente Experto** (solo lectura) y, sobre todo, el **agente de Registro
contable** (Fase 4). Su norte es que esos agentes contesten rápido y exacto sin importar
cuánto crezca la wiki — por eso la estructura es **fija**: el agente va directo a la ruta
exacta, no busca. Tu trabajo es llenar y mantener esa estructura sin romperla.

Operás en dos modos. No son skills distintas, es el mismo criterio aplicado en dos momentos:

- **Modo A — Alta de un cliente nuevo.** Crear la estructura → entrevistar a Irwin →
  backfill del material pasado. Ver «Modo A».
- **Modo B — Destilación.** Tomar lo nuevo que se acumuló en `_fuentes/` (correos que
  entran por `conocimiento@`, transcripciones de reuniones) y volcarlo a los archivos
  fijos. Es el corazón del trabajo recurrente (Motor 2). Ver «Modo B».

Antes de actuar, decidí en qué modo estás: si el cliente no existe todavía en el vault →
Modo A. Si existe y hay material crudo sin destilar → Modo B. Una sesión de alta termina
encadenando en una primera destilación, así que es normal hacer A y después B.

---

## El contrato — leelo antes de escribir una sola línea

Estas reglas no son estilo: son el **contrato** con el MCP de Wiki de Claude Code, que es
lo que hace que los agentes puedan leer lo que escribís. Romper una rompe el sistema. Cada
una tiene su porqué para que entiendas cuándo aplica.

1. **Regla del guion bajo.** Toda carpeta que empiece con `_` (`_fuentes/`, `_inbox/`,
   `_plantilla/`) queda **fuera del alcance de los agentes** — el MCP no la sirve. Por eso:
   el conocimiento que los agentes deben leer va **siempre** en archivos SIN guion bajo
   (los archivos fijos). Nunca pongas conocimiento consumible dentro de una carpeta `_`, ni
   asumas que el agente lee `_fuentes/`.

2. **`_fuentes/` es de SOLO LECTURA para vos.** Leés de ahí, nunca movés, renombrás ni
   borrás nada. Esta es la diferencia clave con una skill genérica de wiki (que mueve las fuentes a `raw/`).
   El pipeline del servidor de Code (`actualizar-inventario`, el registro de ingesta de
   `conocimiento@`) trackea esos archivos en su sitio exacto; si los tocás, rompés la
   sincronización y la idempotencia del servidor. El crudo se queda intacto donde está —
   eso además es el respaldo reversible (siempre se puede re-destilar).

3. **Rutas y nombres fijos, iguales en todos los clientes.** `criterios-contables.md`,
   `identidad.md`, `giro.md`, `sistemas.md` existen en TODA entidad con ese nombre exacto y
   las mismas secciones. El agente de Registro tiene un atajo que lee literal
   `clientes/<cliente>/<entidad>/criterios-contables.md`. No renombres, no reorganices, no
   inventes archivos nuevos con nombres propios. Si un archivo fijo se hincha y hay que
   partirlo, los sub-archivos deben ser **predecibles e iguales en todos los clientes**
   (misma lógica de nombre), nunca categorías emergentes — y sin guion bajo. Antes de
   partir un archivo, consultá a Irwin.

4. **Una subcarpeta por entidad con RUC**, no por marca comercial. El registro contable es
   por RUC. El número de entidades sale de la entrevista / `cartera-clientes.md`.

5. **No escribas en `sistemas/`.** Esa rama (Odoo, SRI, plan de cuentas, normativa) es
   territorio de Code. El conocimiento de cliente vive bajo `clientes/<slug>/`. Desde los
   archivos de cliente **referenciás** a `sistemas/` (ej. "ver `sistemas/sri/retenciones-iva.md`"),
   no copiás su contenido.

6. **Terminá siempre en commit + push.** El MCP lee del filesystem que se actualiza por
   `git push`; tu trabajo solo llega a los agentes cuando está pusheado a `main`. Ver
   «Cierre».

7. **Freno de confidencialidad (no negociable).** Ver «Confidencialidad». En resumen: el
   crudo siempre se preserva; nunca inventás cifras sensibles; lo ambiguo se deja marcado
   en espera del OK de Irwin, no se filtra a lo visible.

8. **Markdown UTF-8.** El conocimiento destilado va en `.md`, texto plano. Nada embebido en
   adjuntos.

Tenés **libertad en el frontmatter** — el MCP no exige un esquema. Mantené el que ya usan
las plantillas (`entidad`, `ruc`, `ultima-revision`, etc.) por consistencia, pero no es
parte del contrato.

---

## Dónde trabajás y cómo identificás al cliente

- **El vault** está en `C:\Users\Irwin\wikis-superavit` (en bash:
  `/sessions/<sesión>/mnt/wikis-superavit`). Confirmá que la conversación tiene esa carpeta
  seleccionada; si no, pedíselo a Irwin.
- **Fuente de verdad de clientes:** `superavit/cartera-clientes.md`. La mantiene Cowork.
  Trae los grupos cliente activos, sus entidades y slugs. Consultala SIEMPRE antes de
  inventar un slug o asumir cuántas entidades tiene un cliente. Si el cliente no está ahí y
  es alta nueva, primero se agrega a la cartera (es contenido de Cowork) y después se crea
  la wiki.
- **Convención de slug:** minúsculas, sin acentos, espacios → guiones medios. Debe matchear
  `^[a-z0-9][a-z0-9-]*$` (una razón social «Distribuidora Andina» daría `distribuidora-andina`).
  El slug del cliente y el
  de cada entidad deben ser estables (el atajo del agente de Registro los indexa).

---

## Modo A — Alta de un cliente nuevo

Orden no negociable: **estructura → entrevista → backfill**. La entrevista va ANTES de leer
cualquier transcripción (regla de Irwin: el contexto humano primero te dice qué buscar en
el material; al revés te perdés). Superávit es la única excepción a esta regla (es la firma,
no un cliente).

### A1. Crear la estructura (en el clon local, vos)

La skill crea la estructura completa copiando la plantilla; NO dependas del script del
servidor `crear-cliente-wiki` (ese es el fallback automático de Code para cuando llegan
transcripciones de un cliente sin wiki todavía — corre solo, en el servidor). Pasos
detallados, con los comandos exactos, en `references/estructura.md`. En resumen:

1. Confirmá el slug del cliente y la lista de entidades (con RUC) contra `cartera-clientes.md`
   y la entrevista.
2. Copiá `clientes/_plantilla/cliente-X/` a `clientes/<slug>/`.
3. Renombrá `entidad-X/` a una carpeta por entidad con RUC (slug de entidad). Si el cliente
   es **una sola entidad**, eliminá `grupo/` y dejá solo la entidad. Si es **grupo de
   varias**, duplicá la carpeta de entidad por cada una y conservá `grupo/`.
4. Creá las carpetas `_fuentes/correos/` y `_fuentes/transcripciones/` (la plantilla trae
   `_inbox/` pero no `_fuentes/`; el pipeline del servidor deposita en `_fuentes/`, así que
   tienen que existir). Dejá un `.gitkeep` en cada una.
5. Llená el frontmatter de cada archivo fijo (entidad, ruc, fecha).

Invariante que el servidor de Code necesita: que exista
`clientes/<slug>/_fuentes/transcripciones/`. Verificalo antes de cerrar.

### A2. Entrevistar a Irwin

Guía completa de preguntas en `references/entrevista.md`. El objetivo es llenar de primera
mano lo que NO va a estar en las transcripciones o que las contextualiza: entidades y RUCs,
quién es quién, giro real, sistemas que usan, y los criterios contables particulares del
cliente. Hacelo conversacional, no un formulario disparado de golpe — una o dos preguntas
por turno, como pediría una asistente que toma notas.

Volcá lo que saques a los archivos fijos correspondientes a medida que avanzás (identidad,
giro, sistemas, contactos del grupo, y los primeros criterios).

### A3. Backfill del material pasado

Preguntá qué material pasado hay para indexar (transcripciones de reuniones, correos,
documentos). Lo que esté en `_fuentes/` ya entró por el pipeline; para lo que Irwin tenga
suelto, indicá que lo haga llegar por los canales (reenvío a `conocimiento@` para correos;
las transcripciones las trae Code). Una vez en `_fuentes/`, destilalo con el **Modo B**.

---

## Modo B — Destilación (el trabajo recurrente / Motor 2)

Tomás lo que se acumuló en `clientes/<slug>/_fuentes/` y lo volcás a los archivos fijos.
Esto es lo que más vas a hacer. El detalle fino (cómo leer cada tipo de fuente, dónde cae
cada hallazgo, cómo citar, cómo deduplicar) está en `references/destilacion.md`. El esqueleto:

1. **Identificá qué hay nuevo sin destilar.** Mirá `_fuentes/correos/` y
   `_fuentes/transcripciones/`. Una fuente está "destilada" cuando sus hallazgos ya están en
   los archivos fijos, citados con su origen. Si dudás, releé los archivos fijos y buscá la
   cita de esa fuente en «Decisiones de criterio».

2. **Leé la fuente entera.** Las transcripciones vienen como diálogo `Speaker N:` con
   frontmatter; los correos como hilo reenviado con frontmatter. Entendé el caso antes de
   escribir.

3. **Ubicá cada hallazgo en su archivo y entidad correctos.** Un criterio de retención →
   `criterios-contables.md` de la entidad que retiene. Un dato de giro → `giro.md`. Algo del
   grupo entero → `grupo/`. Si la fuente cubre varias entidades, repartí. Mapa en «Archivos
   fijos».

4. **Escribí denso pero liviano.** El agente de Registro necesita el criterio operable, no
   la transcripción. Frase clara, con el "por qué" cuando importa. Si un archivo se hincha,
   ver regla 3 del contrato (consultá a Irwin antes de partir).

5. **Citá siempre la fuente.** Cada criterio nuevo lleva su origen, ej.
   `*(Fuente: reunión 2025-11-10 Levantamiento 1.)*` o `*(Fuente: correo 2026-01-21.)*`.
   Esto hace el conocimiento auditable y reversible.

6. **Registrá en «Decisiones de criterio (histórico)»** una línea por decisión:
   `AAAA-MM-DD — <decisión>: <razón>. (Fuente: ...)`. Es el log append-only del archivo.

7. **Actualizá `ultima-revision`** en el frontmatter de cada archivo que tocaste.

8. **No toques `_fuentes/`** (regla 2). Solo leés.

9. **Cerrá con commit + push** (ver «Cierre»).

---

## Archivos fijos — qué va dónde

Mapa de referencia rápida. Detalle por sección en `references/estructura.md`.

| Archivo (ruta fija) | Qué contiene |
|---|---|
| `<entidad>/identidad.md` | Razón social, RUC, constitución, representación legal, accionistas. |
| `<entidad>/giro.md` | Actividad económica, productos/servicios, clientes y proveedores, modelo operativo. |
| `<entidad>/sistemas.md` | Sistema contable (Odoo + correo del proyecto), facturación, bancos, pasarelas, repositorio de documentos. |
| `<entidad>/criterios-contables.md` | **El más importante para Registro.** 6 secciones fijas: Retenciones de IVA, Retenciones de Renta, Particularidades del giro, Plan de cuentas y centros de costo, Calendario de obligaciones, Decisiones de criterio (histórico). |
| `grupo/organigrama.md` | Estructura y roles clave del grupo (solo si es grupo de varias entidades). |
| `grupo/contactos.md` | Personas: cliente y Superávit (nombre, rol, correo, celular, notas). |
| `grupo/acuerdos-superavit.md` | Alcance del servicio, frecuencia, plazos, canales. **Honorarios: ver Confidencialidad.** |
| `grupo/historico.md` | Hitos, incidencias/precedentes, cambios de criterio externos. |

Las **6 secciones fijas de `criterios-contables.md`** no se renombran ni se reordenan: se
agrega contenido dentro de las que ya existen. Si una entidad no aplica a una sección (ej.
no maneja centros de costo, o no aplica ICE), se deja dicho explícitamente — el agente de
Registro necesita saber que NO aplica, no encontrar un hueco.

---

## Confidencialidad — el freno

Distinción clave, porque es sutil y es donde más fácil se mete la pata:

- **Las cifras contables y tributarias del CLIENTE sí van** — son justo lo que el agente de
  Registro necesita. Montos intercompañía, criterios de retención, valores de facturas de
  servicios entre entidades del grupo, etc. Eso se documenta con su cita.

- **Los honorarios y tarifas de SUPERÁVIT al cliente, y los sueldos individuales de
  personas, NO van** a la wiki de cliente. Describí el **modelo** sin las cifras (ej. "se
  factura por hora-hombre según lo registrado en Odoo"), pero no el valor. La sección
  «Honorarios y forma de pago» de `acuerdos-superavit.md` describe la modalidad, no el
  número. Si Irwin pide explícitamente meter una cifra de honorarios, ahí sí — pero no por
  defecto.

- **Lo ambiguo o sensible no se inventa.** Si una fuente sugiere algo confidencial o no
  estás seguro de un dato, no lo pongas como hecho en lo visible: dejá un marcador
  `<pendiente: confirmar con Irwin — ...>` y seguí. El crudo queda intacto en `_fuentes/`
  (siempre recuperable) y el cambio queda en git (reversible). Mejor un hueco honesto y
  marcado que un dato filtrado o inventado.

---

## Por qué NO una skill genérica de wiki para las wikis de cliente

Si pensás en usar `una skill genérica de wiki`: no, para esto no. una skill genérica de wiki asume un vault en blanco donde
la IA inventa la estructura (carpetas `raw/` + `wiki/` con categorías emergentes, su propio
frontmatter, grafo denso de wikilinks) y **mueve** las fuentes a `raw/`. Las wikis de
cliente son lo opuesto a propósito: estructura fija, `_fuentes/` excluido por la regla del
guion bajo, archivos que los agentes leen por ruta exacta. Correr una skill genérica de wiki acá movería las
transcripciones (rompiendo la sync de Code), crearía estructura paralela y no conoce la
regla `_`. Esta skill toma la *filosofía* de una skill genérica de wiki ("compilá el conocimiento una vez en
páginas durables") pero escribe en los archivos fijos de Superávit. una skill genérica de wiki queda intacto
para otros usos (p. ej. la wiki interna `superavit/`).

---

## Cierre — commit + push (siempre)

Tu trabajo solo llega a los agentes cuando está en `main` del repo del servidor. Al
terminar cualquier corrida:

1. Revisá lo que cambiaste (`git status`, `git diff` sobre los archivos de cliente).
2. `git add` de los archivos de cliente que tocaste (nunca de `_fuentes/`, que no tocaste).
3. Commit con mensaje claro, ej. `feat(clientes/<cliente>): destilo Levantamiento 1 a criterios de <entidad>`.
4. `git push`.

El vault de Irwin usa Obsidian Git (auto-sync cada 10 min), así que aunque no pushees a
mano el cambio terminaría propagándose; pero **hacelo explícito** para que el conocimiento
llegue de inmediato y el commit tenga un mensaje útil para la trazabilidad. Los comandos
exactos están en `references/estructura.md` → «Cierre».

---

## Referencias

- `references/estructura.md` — estructura del vault, comandos exactos de alta, el mapa
  detallado de cada archivo fijo y sus secciones, y el cierre con git.
- `references/entrevista.md` — guía de entrevista para el alta de un cliente nuevo.
- `references/destilacion.md` — cómo leer cada tipo de fuente y destilarla: dónde cae cada
  hallazgo, cómo citar, deduplicar y manejar fuentes que cruzan varias entidades.
