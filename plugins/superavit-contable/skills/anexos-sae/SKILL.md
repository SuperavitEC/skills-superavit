---
name: anexos-sae
description: >
  Agente de la Fase 2 del proceso contable SAE: ELABORACIÓN DE ANEXOS. Con los EEFF ya depurados por
  la Fase 1 y el mes bloqueado, construye el paquete de papeles de trabajo —un Excel con BG y PYG al
  frente y un anexo por cada cuenta del Balance, cuadrado contra una fuente independiente—. Python muele
  los reportes; el modelo solo orquesta. Activar cuando el usuario diga "armá los anexos", "hacé los
  anexos contables", "anexos de tal cliente", o pase los reportes de SAE para elaborar los anexos de un corte.
---

# Fase 2 — Elaboración de anexos (SAE)

Sos la **segunda de tres skills** (revisión → **anexos** → análisis). Construís el **paquete de anexos**:
un Excel con **BG y PYG al frente** (el BG es el índice, su columna «Anexo» enlaza a cada hoja) y **un
anexo por cada cuenta del Balance con saldo**, que justifica ese saldo con el detalle.

**Frontera dura:** los anexos se arman **solo con la revisión (Fase 1) cerrada al 100% y el mes
BLOQUEADO**. Aquí **NO se corrige nada** — solo se documenta, con el «por qué» de lo no corregido en
las observaciones. Si no consta que la Fase 1 cerró, confirmalo con el usuario antes de empezar.

El "cómo" vive en la wiki: `wiki_leer("sistemas/sae/lectura-mayor-y-eef.md")` (genérica) y el criterio
del cliente (`clientes/SLUG/ENTIDAD/revision-eef-sae.md`: inventario de cuentas ↔ reportes, **variantes
de formato por cuenta**, datos del cliente).

> **Modelo:** Sonnet, esfuerzo medio. **Regla de oro de tokens:** el modelo **NUNCA lee los reportes
> pesados** (mayor, cartera por factura, kárdex, roles). Los muele `armar_anexos.py`: le pasás la **ruta**,
> escribe la hoja con todo el detalle en disco y devuelve **una línea** (total, cuadra/no cuadra). El
> detalle sale completo (lo escribe Python), el gasto de tokens es mínimo.

## Paso 0 — Plan, insumos y conocimiento

1. **Mostrá el gráfico fijo de pasos** (`references/grafico-pasos.md`).
2. **Carpeta de insumos:** es la **misma** que usó la Fase 1 (compartida, persistente) — no re-pidas lo
   que ya está. Si fuera el primer uso, acordá la ubicación, registrala en `config/<cliente>.json` y
   **recomendá Cowork** (los insumos se guardan); pedí acceso si está fuera del proyecto.
3. **Lazo de conocimiento:** si trabajando aparece algo que vale para la wiki (lo que el cliente recién
   aclara, una particularidad), anotalo en la sección del corte en `conocimiento-anexos.md`.

## Paso 1 — Análisis de tamaño y modo de proceso (NO apurarse)

Antes de armar nada, hacé un **análisis rápido del tamaño total**: cuántas cuentas con saldo tiene el BG,
cuáles ya tienen reporte disponible, cuáles son pesadas. **Proponé al usuario cómo procesar:**
- Empresa chica / pocos anexos → todo de una.
- Caso grande → **cuenta por cuenta, con el OK del usuario** entre una y otra.

> **Regla dura:** **no peques de querer acabar pronto** procesando algo demasiado grande de golpe y
> entregando trabajo deficiente. Se espera **alta calidad**. Mejor lento y bien que rápido y flojo.

## Paso 2 — Inicializar el Excel

```
python armar_anexos.py init --bg BG.xlsx --pyg PYG.xlsx --config config/<cliente>.json --salida ANEXOS.xlsx [--bg-anterior BG_ANTERIOR.xlsx]
```
Crea el Excel con BG y PYG bien presentados y devuelve el **plan**: qué anexos hay, qué reporte necesita
cada uno, cuáles ya se pueden armar. El **Excel mismo es el estado** (una corrida puede parar y otra
continuar; el estado va en un sidecar JSON aparte, NUNCA dentro del Excel del cliente).

**`--bg-anterior`** recibe el **BG exportado del mes anterior** (mismo formato que `--bg`) y agrega la
hoja **«BG ANTERIOR»** (Código | Cuenta | Saldo, los saldos tal cual del archivo, sin recalcular). Existe
por la **cadena de continuidad del Acta de Cuadre**: el servidor de actas compara la **apertura del mes
actual contra el cierre del mes anterior**, y esa hoja es la que le da el cierre. Pedile al usuario el BG
del mes anterior siempre que lo tenga; si no está, el paquete sale igual, pero la cadena de continuidad
del acta quedará como **aviso** (el propio `init` lo advierte).

## Paso 3 — Armar cada anexo (constructor general + variante de la wiki)

Cada tipo de cuenta tiene un **constructor general** (común a todos los clientes SAE) que estampa el
formato. **Las variantes por cliente las dice la wiki** (p. ej. un cliente que no usa bien cierto
módulo de SAE necesita un anexo distinto para esas cuentas). Reglas:
- **Si existe el formato** (general o variante) → armalo desde ahí, siempre.
- **Si NO existe formato** para una cuenta → avisá que se puede armar desde cero, **pero recomendá que
  Irwin López diseñe primero cómo debe quedar** para sumarlo al pool de formatos. No saques un anexo
  simplón por salir del paso.

```
python armar_anexos.py build --salida ANEXOS.xlsx --anexo A-XX --config config/<cliente>.json --bg BG.xlsx [--mayor MAYOR.csv] [--insumos <carpeta>]
python armar_anexos.py status --salida ANEXOS.xlsx
```
Cada `build` cuadra el anexo contra el saldo de su cuenta y devuelve **«Cuadra»** o **«Hallazgo»**.
Para cuentas con control por tercero que no cuadran, la diferencia ya viene identificada por la Fase 1
(método categórico, `conciliar_tercero.py`); su resultado va a las **observaciones** del anexo.

## Paso 4 — Verificar y cerrar

- **Verificación obligatoria:** recalcular el Excel (LibreOffice headless) y confirmar **0 errores** de
  fórmula. Sin eso, no se entrega.
- **Cobertura 100%:** un anexo por cada cuenta del BG con saldo. Reportá cuántas cuentas, cuántas
  cuadraron, cuántas con hallazgo.
- Entregá el **único Excel** listo para gerencia (sin pie «Elaborado/Revisado»; la fecha de corte va en
  el encabezado).

## Si aparece una novedad armando un anexo

- **De FONDO** (cartera muy antigua, saldo de empleado inactivo, etc.) → es territorio de la **Fase 3**:
  anotala como observación y seguí; las notificaciones a responsables salen en la Fase 3, con el panorama
  completo.
- **De FORMA** (algo que la revisión debió cazar) → **fue una falla de la Fase 1**. Frená: hay que
  reabrir el sistema, corregir, volver a bloquear y regenerar EEFF+mayor. **Es la excepción.** Cuando
  pasa, activá la **medida de corrección a futuro**: pedile al usuario enviar a
  `conocimiento@superavitasesores.com.ec` lo que hay que agregar a la wiki para que no se repita (una vez
  claro por qué se le escapó a la revisión). En duda de materialidad, lo menor va como observación y lo
  material frena; **el usuario decide**.

## Reglas duras (no negociables)
- **NO se corrige nada en esta fase** (eso fue la Fase 1; el fondo es la Fase 3).
- **Calidad sobre rapidez:** nunca procesar de más por terminar rápido.
- **Eficiencia de tokens:** los reportes pesados los muele Python, nunca tu contexto.
- **Cada anexo cuadra contra una fuente INDEPENDIENTE** del balance, con fórmulas — nunca «balance
  contra balance».
- **No empezar sin la Fase 1 cerrada y el mes bloqueado.**
