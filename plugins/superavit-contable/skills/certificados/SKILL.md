---
name: certificados
description: Arma certificados de la firma (laboral, laboral con sueldo, prestación de servicios, servicios a un cliente o cualquier otro) con el membrete y el formato oficial, en PDF listo para la carpeta de firma electrónica. La skill NO trae los textos ni los datos del firmante; los lee de la wiki. NO firma ni sube el documento. Activar cuando digan "hazme un certificado", "necesito un certificado laboral", "certificado de trabajo", "certificado de prestación de servicios", "certificado para un cliente", "certificado de experiencia" o invoquen "/certificados".
---

# Certificados de la firma

**Tu trabajo NO es improvisar: es leer el proceso de la wiki y armar el certificado con
sus modelos, en el formato fijo que pone el script.** El documento solo vale cuando lo
firma el representante legal; tú dejas el PDF listo para que la persona lo suba a la
carpeta de firma.

> **Modelo:** corre en **Sonnet**.

## Paso 0 — Encuadre

Antes de escribir nada, deja claros estos datos. Si falta alguno, **pregunta, no asumas**:

1. **Quién lo pide** y **para quién es** (la misma persona, otro integrante del equipo o
   un cliente).
2. **Qué tipo de certificado.** Los tipos con modelo están en la wiki. Si piden uno que no
   tiene modelo, sigue igual: es el caso «Otro» del Paso 2.
3. **Para qué lo necesita**, solo si cambia el texto: un banco suele pedir el sueldo; una
   institución puede pedir que vaya dirigido a ella.

## Paso 1 — Lee el proceso

`wiki_leer("superavit/procesos/certificados.md")`. Ahí están los modelos de texto de cada
tipo, el bloque del firmante, de dónde sale cada dato y lo que hay que hacer después. Si la
página no responde, **frena y avisa**: sin ella no hay firmante ni modelos.

## Paso 2 — Reúne los datos y redacta

- Toma los datos de las fuentes que indica la wiki (la ficha del empleado en Odoo o la
  wiki del cliente). **Lo que no encuentres se lo preguntas a quien pide el certificado.**
- Confirma con quien lo pide el **nombre completo** tal como debe salir, el **trato**
  (señor, señora, señorita) y cualquier fecha que no esté clara.
- Redacta con el modelo del tipo, cambiando solo los datos.
- **Otro tipo de certificado:** pide a la persona qué tiene que decir el documento (a quién
  va, qué se certifica, desde cuándo, cualquier frase que le exijan) y redáctalo en el mismo
  estilo de los modelos.
- **Muestra el texto completo y espera el OK** antes de generar el PDF.

Reglas de redacción: ortografía completa con todas las tildes, sin rayas largas, sin
negritas en el cuerpo, fechas como en los modelos.

## Paso 3 — Genera el PDF

Escribe un JSON con el contenido y corre el script de esta skill:

```bash
python3 <carpeta de esta skill>/scripts/generar_certificado.py --spec certificado.json --salida <carpeta>
```

```json
{
  "archivo": "Certificado laboral - <Nombre Apellido> - AAAA-MM-DD",
  "fecha": "AAAA-MM-DD",
  "parrafos": ["<párrafo 1>", "<párrafo 2>"],
  "firmante": ["<líneas del bloque del firmante, tal como están en la wiki>"]
}
```

Opcionales: `lugar` (por defecto «Quito, Ecuador»), `titulo` (por defecto «CERTIFICADO»),
`cierre` (por defecto «Atentamente,»).

El script pone el membrete, la letra, el título con su línea y el marcador `[FIRMA]` en
blanco donde va el sello. **No cambies el formato ni quites el marcador**: el firmador
estampa la firma justo ahí.

Verifica antes de entregar: el PDF existe, tiene una sola página (salvo que el texto sea
largo) y el texto extraído (`pdftotext`) trae el nombre y la fecha correctos. Si el script
avisa que no hay LibreOffice, entrega el DOCX e indica que se exporte a PDF desde Word.

## Paso 4 — Entrega

Entrega el PDF y dile a la persona, con estas palabras:

> Súbelo en Odoo a **Documentos → Empresa → Firma electrónica → 01 - Pendientes de firma**.
> Cuando esté firmado aparece en **02 - Firmados** y te llega el aviso de Odoo.

## Reglas duras

- **Primero la wiki.** Modelos, firmante y fuentes de datos salen de
  `superavit/procesos/certificados.md`; nunca de memoria.
- **No inventes datos.** Lo que no está en las fuentes se pregunta.
- **No firmas ni subes nada.** La firma es del representante legal y la subida la hace
  quien pidió el certificado.
- **No subas archivos por el conector de Odoo en base64**: se truncan y llegan dañados.
- **No restrinjas tipos ni contenidos por tu cuenta.** Quien firma lee el documento antes
  de aprobarlo y decide.

## Tools que usa

- `wiki_leer` y `wiki_buscar` (conector de la wiki).
- `odoo_consultar` (conector de Odoo), solo lectura, para la ficha del empleado o del
  cliente que indica la wiki.
- El script `scripts/generar_certificado.py` (necesita `soffice` para el PDF).
