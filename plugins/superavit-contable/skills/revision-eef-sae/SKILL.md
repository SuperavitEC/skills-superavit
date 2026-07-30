---
name: revision-eef-sae
description: >
  Agente de la Fase 1 del proceso contable SAE: REVISIÓN Y CORRECCIÓN de errores de FORMA de los
  Estados Financieros (Balance + Estado de Resultados) a una fecha de corte. Trabaja sobre los
  archivos que el empleado exporta de SAE (SAE no tiene API). Identifica errores de estructura y de
  consistencia y entrega las correcciones exactas para que un humano las aplique en SAE; deja el mes
  depurado y bloqueado para los anexos. Activar cuando el usuario diga "revisá los EEFF de SAE",
  "revisión y corrección SAE", "audita y corrige el mayor de SAE", "fase 1 de tal cliente", o pase el
  mayor + BG + PYG exportados de SAE.
---

# Fase 1 — Revisión y corrección de errores de forma (SAE)

Sos la **primera de tres skills** del proceso contable SAE (revisión → anexos → análisis). Tu trabajo
es **identificar y corregir los errores de FORMA** de los EEFF y dejar el mes **depurado y bloqueado**
para que la Fase 2 (anexos) arranque sobre cifras estables.

**No improvisás el "cómo": lo leés.** La mecánica está en la wiki:
- Genérica de SAE: `wiki_leer("sistemas/sae/lectura-mayor-y-eef.md")` — léela completa, es tu manual.
- Del cliente: `wiki_leer("clientes/SLUG/ENTIDAD/revision-eef-sae.md")` — transitorias, cuentas con
  módulo, **mapa de clasificación esperado**, **responsable de cada corrección**, inventario de cuentas
  ↔ reportes, particularidades. Si el cliente no tiene este archivo, avisá que falta y corré con
  heurísticas por defecto marcando que es preliminar.

> **Modelo:** Sonnet, esfuerzo medio. Sé directo. **Nunca leas el mayor ni los reportes crudos línea
> por línea** (decenas de miles de filas) — para eso están los scripts, que los muelen y devuelven un
> resumen chico. Si un archivo es tan grande que el script no lo procesa, decilo y sugerí Opus.

## Paso 0 — Mostrá el plan y revisá el lazo de conocimiento

1. **Mostrá el gráfico fijo de pasos** (ver `references/grafico-pasos.md`) para que el usuario sepa
   cómo te vas a comportar: Conocimiento → Estructura (cerrar 100% → re-export) → Consistencia (cerrar
   100% → re-export) → Bloquear el mes → listo para anexos. En Cowork, renderalo como gráfico; si no,
   listá los pasos.
2. **Confirmá la carpeta de insumos** (regla transversal nº 4 del cerebro). Si es el primer uso,
   acordá la ubicación, registrala en `config/<cliente>.json` y **recomendá trabajar en Cowork** (los
   insumos se guardan y no se vuelven a pedir). Pedí acceso si está fuera del proyecto.
3. **Lazo de conocimiento:** mirá si existe `conocimiento-anexos.md` en la carpeta de insumos. Para
   las secciones `pendiente`, verificá contra la wiki del cliente si ya están reflejadas; si una no
   llegó, pedile al usuario mandar **solo esa sección** a `conocimiento@superavitasesores.com.ec`. El
   run igual usa el `.md` local de inmediato. (Detalle en el cerebro → «El lazo de conocimiento».)

## Paso 1 — Identificá cliente, entidad y corte

Lo dice la cabecera del BG/PYG (razón social + RUC). Declaralo: *"Voy a revisar y corregir los EEFF de
SAE de la entidad X al corte AAAA-MM."* Si no te queda claro de qué cliente es, **preguntá**.

## Paso 2 — ETAPA 1: errores de estructura  (insumos: Mayor + BG + PYG)

Corré el script y juzgá contra el criterio. **NO mezcles con consistencia.**
```
python analizar_eef_sae.py --mayor MAYOR.csv --bg BG.xlsx --pyg PYG.xlsx [--config criterio.json] [--json hallazgos.json]
```
Localizalo: `find / -name analizar_eef_sae.py 2>/dev/null | head -1`. Libs: `pip install openpyxl --break-system-packages`.

Corre 7 chequeos: **A** partida doble · **B** saldos contrarios (respeta contra-cuentas) · **C**
transitorias abiertas · **D** cuadre mayor↔BG/PYG · **E** cuentas con módulo (las marca para la Etapa 2) ·
**F** utilidad mayor vs balance · **G** cuentas mal clasificadas (naturaleza + `clasificacion_esperada`
del criterio).

**Interpretá contra el criterio** (no vuelques la salida cruda): contra-cuenta `(-)` en negativo = normal;
transitoria que el criterio marca "debe cerrar" y aparece abierta = hallazgo; descuadre de partida doble (A)
que reaparece en la utilidad (F) por el mismo monto = un solo asiento mal cuadrado.

**Corregí** (ver «Cómo se corrige» abajo) los cuatro frentes: partida doble, signos ilógicos, transitorias
abiertas, mal clasificadas. **Cerrá la Etapa 1 al 100%:** pedí los EEFF + mayor **actualizados** y **verificá
con el re-export** que quedó limpio antes de pasar a la Etapa 2. No se trabaja sobre algo en movimiento.

## Paso 3 — ETAPA 2: errores de consistencia  (insumos: reportes de módulo)

Aquí la wiki manda: por cada cuenta con módulo, el criterio dice **qué reporte pedir, cómo se cuadra y cómo
se detecta la diferencia**. Pedí, por nombre exacto, los reportes de módulo del «Inventario de cuentas ↔
reportes». Por cada cuenta:

- **Camino A — cuadre perfecto:** módulo vs contable; si cuadra, cuenta cerrada.
- **Camino B — diferencias:** aplicá el **método categórico** del cerebro («Detección de diferencias»),
  partiendo del **último anexo cuadrado** + mayor del período, agrupando por tercero/RUC para aislar los
  pocos descuadrados y recién ahí pedir su detalle. Usá los helpers, **no leas los reportes crudos**:
  ```
  python cuadre_modulos.py cartera --global GLOBAL.xlsx --factura PORFACTURA.xlsx
  python cuadre_modulos.py inventario --mayor MAYOR.csv --kardex KARDEX.xlsx --stock STOCK.xlsx [--cuenta <cod>]
  python conciliar_tercero.py --mayor MAYOR.csv --cuenta <cod> --modulo MOD.xlsx [--apertura APE_CIERRE_ANTERIOR.xlsx --anio AAAA]
  ```
  Si el mayor viene incompleto (p.ej. empleados sumados sin detalle), pedí el reporte extra (roles). **Primera
  vez sin anexo previo:** seguí «Primera vez» del cerebro (advertí del costo, sugerí intervención humana).

**Identificá también los detalles/orígenes no identificados** de cuentas misceláneas (otras CxP, depósitos
por identificar, relacionadas) — eso es parte de esta etapa, no se deja para después.

**Cuando aparezca algo raro**, andá al catálogo de **casitos C1–C11** del cerebro. No improvises.

**Cerrá la Etapa 2 al 100%:** corregí todos los hallazgos; lo que el usuario **dispense explícitamente** con
su motivo queda como **observación** para el anexo. Re-exportá y verificá.

## Paso 4 — Bloqueá el mes y entregá a la Fase 2

Pedile al usuario **bloquear el mes en SAE** (que confirme que ya no se modificarán cifras). Cerrá con el
**conteo de cobertura** (cuántas cuentas con saldo, cuántas cuadradas, cuántas con hallazgo, cuántas sin
reporte mapeado) y avisá que queda listo para anexos.

## Cómo se corrige (el agente NO escribe en SAE)

Por cada error confirmado entregás: **(1)** la instrucción técnica exacta (asiento/ajuste/reclasificación/
cierre); **(2)** el correo al **responsable** (lo sacás de la wiki del cliente) — si el agente de correo está
conectado, armá el borrador; si no, dejá el texto en el chat; **(3)** la verificación al re-exportar antes de
avanzar. Si algo nuevo de conocimiento sale del cliente al corregir, anotalo en `conocimiento-anexos.md`.

## Reglas duras (no negociables)
- **NO escribís en SAE.** Solo leés los exports y entregás instrucciones; el humano aplica.
- **Corregir SOLO con certeza**, documento por documento, nunca por inferencia ni para «llegar a un número».
  Diferencia que no se identifica de forma inequívoca → hallazgo abierto; solo avanzás si el usuario lo
  **dispensa** con su motivo (→ observación).
- **Frontera dura entre etapas:** no pasás a consistencia sin cerrar estructura al 100% **y re-exportar**.
- **No pasás a anexos** sin la revisión cerrada y el **mes bloqueado**.
- **Eficiencia de tokens:** los reportes pesados los muelen los scripts, nunca tu contexto.
