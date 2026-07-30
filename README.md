# Marketplace de skills — Superávit Asesores

Repositorio que distribuye las skills operativas de la firma al equipo. Cada persona lo
instala **una vez** y después recibe las actualizaciones con un solo comando: no hay que
reenviar archivos `.skill` ni preocuparse por versiones desincronizadas.

## Para el equipo — instalar (una sola vez)

En la app de Claude:

1. Abrí el menú **Customize** (en Cowork, primero la pestaña **Cowork**).
2. Pestaña **Plugins** → **Browse plugins** → **Add from a repository**.
3. Pegá la URL del repo:

   ```
   https://github.com/SuperavitEC/skills-superavit
   ```

4. Aparece el marketplace **superavit**. Instalá el plugin **superavit-contable**.

Desde Claude Code el equivalente es:

```
/plugin marketplace add https://github.com/SuperavitEC/skills-superavit
/plugin install superavit-contable@superavit
/reload-plugins
```

## Para el equipo — actualizar

Cuando avisemos que hay versión nueva:

```
/plugin marketplace update superavit
```

O desde **Customize → Plugins**, refrescando el marketplace.

## Para Irwin — publicar un cambio

1. Editá la skill dentro de `plugins/superavit-contable/skills/<nombre>/SKILL.md`.
2. Subí la versión en `plugins/superavit-contable/.claude-plugin/plugin.json`.
3. Anotá el cambio en `CHANGELOG.md`.
4. `git add -A && git commit -m "..." && git push`
5. Avisá al equipo que corra la actualización.

## Qué trae el plugin

| Skill | Para qué |
|---|---|
| `acta-cuadre` | Acta de Cuadre Mensual: pedirla, interpretar bloqueos, subir insumos, cerrar el ciclo |
| `anexos-sae` | Armado del paquete de Anexos en Excel para clientes SAE |
| `analisis-anexos-sae` | Análisis de los anexos ya armados |
| `agente-compras` | Registro de facturas de proveedor (compras) en Odoo, en borrador |
| `agente-conciliacion-bancaria` | Carga de extractos y cuadre de bancos reales |
| `agente-tarjetas-pasarelas` | Cierre de tarjetas y pasarelas de pago |
| `agente-retenciones` | Retenciones emitidas y recibidas |
| `agente-nomina` | Carga del asiento de nómina |
| `agente-impuestos-odoo` | Declaración mensual F104 / F103 en Odoo |
| `revision-eef-odoo` / `revision-eef-sae` | Revisión de EEFF, según la fuente sea Odoo o SAE |
| `wikisuperavit` | Gestión de las wikis de cliente (alta y destilación) — útil solo para quien tiene el vault |

Las skills **no traen el procedimiento contable**: cada agente lo lee de la sección que le
corresponde en el `criterios-contables.md` del cliente en la wiki. Si esa sección no existe o
está incompleta, el agente frena y avisa — no improvisa.

## El sistema contable del cliente manda

No toda la cartera está en Odoo, y eso cambia cómo trabaja la IA:

- **Odoo** — la IA entra directo por el conector (lee y escribe, siempre con las reglas de
  cada skill). Es el caso de los agentes de registro, `agente-impuestos-odoo` y
  `revision-eef-odoo`.
- **SAE** — no hay conexión: el empleado **exporta los reportes y se los pasa a la IA**, que
  los procesa con `revision-eef-sae` → `anexos-sae` → `analisis-anexos-sae`. Para el acta,
  la fuente contable es el paquete de anexos subido como insumo.
- **Firesoft** — tampoco hay conexión y su metodología es propia; **todavía no hay skill**
  que la cubra. Ante un cliente en Firesoft, la IA frena y avisa.

Qué sistema usa cada entidad lo dice su `sistemas.md` en la wiki — los agentes lo verifican
antes de tocar nada y **nunca** intentan operar por Odoo una entidad que no está ahí.

## Nota importante

Las skills **no traen los procedimientos contables**: esos viven en el
`criterios-contables.md` de cada cliente en la wiki, y las skills mandan a leerlos. Este
plugin distribuye el *cómo operar*, no el *qué decidir*. Los criterios siguen siendo una
sola fuente de verdad en la wiki.

## Lo que este plugin todavía NO hace

No distribuye la configuración de los conectores (`odoo-superavit`, `wiki-superavit`).
Cada token `sodoo_` es personal y el servidor solo guarda su huella SHA-256, así que no se
puede empaquetar uno genérico. Eso sigue instalándose por script, y el procedimiento está
en `superavit/procesos/actas-de-control.md` de la wiki.
