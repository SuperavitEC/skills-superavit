# Estructura del vault, alta y cierre

Detalle de referencia para el SKILL.md. Leé esto cuando vayas a crear la estructura de un
cliente nuevo (Modo A1), cuando dudes de qué va exactamente en cada archivo fijo, o para el
cierre con git.

## El árbol del vault

```
clientes/
  _plantilla/                 ← molde, NO se toca ni se sirve (regla del guion bajo)
    cliente-X/
      entidad-X/              ← 4 archivos fijos
        identidad.md
        giro.md
        sistemas.md
        criterios-contables.md
      grupo/                  ← 4 archivos del grupo (solo si hay varias entidades)
        organigrama.md
        contactos.md
        acuerdos-superavit.md
        historico.md
      _inbox/                 ← materia prima manual (no servido)
        correos/ documentos/ por-dictado/ reuniones/
  <slug-cliente>/             ← un cliente real, en minúsculas y con guiones
    <entidad-1>/  <entidad-2>/  ...   ← una por RUC
    grupo/
    _fuentes/                 ← lo deposita el pipeline del servidor (no servido, SOLO LECTURA)
      correos/
      transcripciones/
    _inbox/
sistemas/                     ← Odoo, SRI, plan de cuentas, normativa — territorio de Code, NO escribir
superavit/                    ← la firma (cartera-clientes.md vive acá) — no es un cliente
```

Diferencia importante entre `_inbox/` y `_fuentes/`:
- `_inbox/` viene en la plantilla; es para material que se carga a mano.
- `_fuentes/` lo crea el alta (vos) y lo llena el pipeline del servidor de Code (correos de
  `conocimiento@` → `_fuentes/correos/`; transcripciones → `_fuentes/transcripciones/`). De
  acá leés para destilar (Modo B). NUNCA escribís ni movés acá.

Ambas empiezan con `_` → ninguna la sirve el MCP a los agentes. Todo lo consumible va en los
archivos fijos sin guion bajo.

## Alta — comandos exactos (Modo A1)

Operás en el clon local del vault. En bash el vault está en
`/sessions/<sesión>/mnt/wikis-superavit`. Ajustá `<slug>` y las entidades.

```bash
cd /sessions/<sesión>/mnt/wikis-superavit/clientes

# 1. Copiar la plantilla a la carpeta del cliente
cp -r _plantilla/cliente-X <slug>

# 2A. CLIENTE DE UNA SOLA ENTIDAD: renombrar la entidad y borrar grupo/
cd <slug>
mv entidad-X <slug-entidad>
rm -rf grupo

# 2B. GRUPO DE VARIAS ENTIDADES: renombrar la primera y duplicar por cada una; conservar grupo/
cd <slug>
mv entidad-X <entidad-1>
cp -r <entidad-1> <entidad-2>     # repetir por cada entidad con RUC
# (vaciar el contenido de ejemplo de las copias si lo hubiera; la plantilla viene vacía)

# 3. Crear _fuentes/ (la plantilla no la trae; el pipeline del servidor la necesita)
mkdir -p _fuentes/correos _fuentes/transcripciones
touch _fuentes/correos/.gitkeep _fuentes/transcripciones/.gitkeep
```

Después, con las herramientas de archivo (Read/Edit), llená el frontmatter de cada archivo
fijo: `entidad: <razón social>`, `ruc: "<RUC>"` (con comillas, para que no se interprete
como número y pierda ceros), `ultima-revision: <fecha>`. En los del grupo: `grupo: <nombre>`.

Verificación antes de cerrar: debe existir `clientes/<slug>/_fuentes/transcripciones/`
(invariante que el servidor de Code necesita) y una carpeta por entidad con sus 4 archivos.

## Qué va en cada archivo fijo

### `identidad.md` (por entidad)
Datos duros de la entidad. Secciones: Datos generales (razón social, nombre comercial, RUC,
dirección fiscal, teléfonos, correo institucional); Constitución (fecha, escritura, tipo de
contribuyente, régimen tributario, obligado a llevar contabilidad); Representación legal
(nombre, CI, nombramiento y vencimiento); Accionistas / propiedad.

### `giro.md` (por entidad)
Cómo gana plata la entidad y qué la hace particular fiscalmente. Secciones: Actividad
económica principal; Productos / servicios; Clientes principales; Proveedores recurrentes;
Modelo operativo (con detalle suficiente para entender sus retenciones, IVA y
particularidades).

### `sistemas.md` (por entidad)
Herramientas. Secciones: Sistema contable (plataforma — normalmente Odoo — y el correo del
proyecto Odoo, formato `<cliente>@superavit.odoo.com`); Sistema de facturación; Bancos y
cuentas; Plataformas de pago (Payphone, etc.); Repositorio de documentos.

### `criterios-contables.md` (por entidad) — EL CRÍTICO
Lo lee el agente de Registro por ruta fija. Las 6 secciones NO se renombran ni reordenan; se
agrega dentro de ellas. Cuando una no aplica, decilo explícito ("ICE — no aplica", "no
maneja centros de costo").

1. **Retenciones de IVA** — por tipo de proveedor y particularidad. Decí si la entidad es o
   no agente de retención designado (dato del RUC), qué formulario declara (103), y los
   criterios propios. Los porcentajes generales no se copian: se referencian a
   `sistemas/sri/retenciones-iva.md`.
2. **Retenciones de Renta** — análogo; referenciá `sistemas/sri/retenciones-ir.md`. Anotá
   particularidades (ej. retención por relación de dependencia si es la empleadora).
3. **Particularidades del giro** — el grueso de los criterios operativos: casos especiales,
   flujos intercompañía, regularizaciones, decisiones del cliente. Subtítulos `###` por caso.
4. **Plan de cuentas y centros de costo** — normalmente "plan estándar de Superávit, ver
   `sistemas/plan-de-cuentas/`"; decí si maneja o no centros de costo.
5. **Calendario de obligaciones tributarias** — mensuales (IVA, 103, ATS), anuales (Renta,
   anexos), y el noveno dígito del RUC para los vencimientos.
6. **Decisiones de criterio (histórico)** — log append-only. Una línea por decisión:
   `AAAA-MM-DD — <decisión>: <razón>. (Fuente: ...)`.

Para calibrar profundidad y estilo, abrí el `criterios-contables.md` de un cliente ya trabajado
(`wiki_listar_clientes` te dice cuáles hay): criterios densos, citados, con marcadores
`<pendiente: ...>` donde falta dato.

### Archivos del `grupo/` (solo si el cliente tiene varias entidades)
- `organigrama.md` — estructura general y roles clave.
- `contactos.md` — personas. Formato por línea: `Nombre — rol — correo — celular — notas`.
  Una parte cliente y una parte Superávit.
- `acuerdos-superavit.md` — alcance del servicio, frecuencia de entregables, plazos,
  canales. **Honorarios:** describí la modalidad sin cifras (ver Confidencialidad en SKILL.md).
- `historico.md` — hitos (cambio de representante, fusiones), incidencias/precedentes,
  cambios externos del SRI que afectan al grupo.

## Cierre — git (Modo A y B)

Al terminar cualquier corrida, propagá al servidor:

```bash
cd /sessions/<sesión>/mnt/wikis-superavit
git status                                   # revisá qué cambió
git add clientes/<slug>                       # solo lo de cliente; NUNCA _fuentes/ (no lo tocaste)
git commit -m "feat(clientes/<slug>): <qué destilaste o creaste>"
git push
```

Mensajes de commit útiles (la trazabilidad importa, es una firma contable):
- Alta: `feat(clientes/<slug>): alta de <Cliente> (<N> entidades)`
- Destilación: `feat(clientes/<slug>): destilo <fuente> a criterios <entidad>`

Si `git push` pide credenciales o falla, no fuerces nada: avisá a Irwin (su Obsidian Git
igual sincroniza cada 10 min, pero conviene confirmar que el push salió).
