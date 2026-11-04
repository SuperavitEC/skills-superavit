#!/usr/bin/env python3
"""Arma un certificado de la firma (DOCX + PDF) sobre el membrete oficial.

Uso:
    python3 generar_certificado.py --spec certificado.json --salida <carpeta>

El JSON trae solo el contenido; el formato (membrete, letra, título, línea,
marcador de firma) lo pone este script, para que todos los certificados salgan
iguales. Campos del JSON:

    archivo     nombre del archivo sin extensión (obligatorio)
    fecha       "AAAA-MM-DD" (por defecto, hoy)
    lugar       por defecto "Quito, Ecuador"
    titulo      por defecto "CERTIFICADO"
    parrafos    lista de párrafos del cuerpo (obligatorio)
    cierre      por defecto "Atentamente,"
    firmante    lista de líneas del bloque de firma (obligatorio)

Requiere LibreOffice (soffice) para el PDF. Sin LibreOffice deja solo el DOCX
y avisa: se exporta a PDF desde Word.
"""
import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI.parent / "assets"
PLANTILLA = ASSETS / "membrete-certificado.docx"
FUENTES = ASSETS / "fuentes"

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

LETRA = "Georgia"
TAM = 24  # medios puntos: 12 pt


def fecha_larga(iso: str) -> str:
    """'2026-01-09' -> 'Enero 9/2026', el formato del modelo de la firma."""
    d = dt.date.fromisoformat(iso)
    return f"{MESES[d.month - 1]} {d.day}/{d.year}"


def rpr(negrita=False, color=None):
    partes = [f'<w:rFonts w:ascii="{LETRA}" w:hAnsi="{LETRA}" w:cs="{LETRA}"/>']
    if negrita:
        partes.append("<w:b/><w:bCs/>")
    partes.append("<w:i/><w:iCs/>")
    if color:
        partes.append(f'<w:color w:val="{color}"/>')
    partes.append(f'<w:sz w:val="{TAM}"/><w:szCs w:val="{TAM}"/><w:lang w:val="es-EC"/>')
    return "<w:rPr>" + "".join(partes) + "</w:rPr>"


def parrafo(texto="", jc="left", antes=0, despues=0, negrita=False, color=None,
            borde=False, keep_next=False):
    ppr = []
    if keep_next:
        ppr.append("<w:keepNext/><w:keepLines/>")
    if borde:
        # Línea gruesa bajo el título, como en el modelo.
        ppr.append('<w:pBdr><w:bottom w:val="single" w:sz="36" '
                   'w:space="10" w:color="000000"/></w:pBdr>')
    ppr.append(f'<w:spacing w:before="{antes}" w:after="{despues}" '
               'w:line="274" w:lineRule="exact"/>')
    if borde:
        ppr.append('<w:ind w:left="-180" w:right="60"/>')
    ppr.append(f'<w:jc w:val="{jc}"/>')
    run = ""
    if texto:
        run = (f"<w:r>{rpr(negrita, color)}"
               f'<w:t xml:space="preserve">{escape(texto)}</w:t></w:r>')
    return f"<w:p><w:pPr>{''.join(ppr)}{rpr(negrita, color)}</w:pPr>{run}</w:p>"


def cuerpo_xml(spec: dict) -> str:
    p = []
    p.append(parrafo(spec.get("lugar", "Quito, Ecuador"), antes=430))
    p.append(parrafo(fecha_larga(spec["fecha"])))
    # Título centrado con su línea, a la altura del modelo.
    p.append(parrafo(spec.get("titulo", "CERTIFICADO"), jc="center", antes=1980,
                     despues=0, negrita=True, borde=True))
    primero = True
    for texto in spec["parrafos"]:
        p.append(parrafo(texto, jc="both", antes=840 if primero else 0, despues=274))
        primero = False
    # Cierre y bloque de firma, que no se separan entre páginas.
    p.append(parrafo(spec.get("cierre", "Atentamente,"), antes=1080, keep_next=True))
    # Hueco de la firma: el firmador estampa el sello sobre [FIRMA] (en blanco).
    # El sello mide unos 42 pt y baja desde el marcador: tres líneas libres debajo.
    p.append(parrafo("[FIRMA]", color="FFFFFF", keep_next=True))
    p.append(parrafo("", keep_next=True))
    p.append(parrafo("", keep_next=True))
    p.append(parrafo("", keep_next=True))
    lineas = spec["firmante"]
    for i, linea in enumerate(lineas):
        p.append(parrafo(linea, keep_next=i < len(lineas) - 1))
    return "".join(p)


def instalar_fuentes():
    """Si el equipo no tiene Georgia, usa Gelasio (métricas compatibles, OFL)."""
    try:
        hay = subprocess.run(["fc-list", ":family=Georgia"], capture_output=True,
                             text=True).stdout.strip()
    except FileNotFoundError:
        return
    if hay:
        return
    destino = Path.home() / ".fonts"
    destino.mkdir(parents=True, exist_ok=True)
    for f in FUENTES.glob("*.ttf"):
        shutil.copy2(f, destino / f.name)
    conf_dir = Path.home() / ".config" / "fontconfig"
    conf_dir.mkdir(parents=True, exist_ok=True)
    conf = conf_dir / "fonts.conf"
    alias = ("<alias binding=\"same\"><family>Georgia</family>"
             "<prefer><family>Gelasio</family></prefer></alias>")
    if not conf.exists() or "Gelasio" not in conf.read_text(encoding="utf-8"):
        conf.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd">'
                        f"<fontconfig><dir>{destino}</dir>{alias}</fontconfig>",
                        encoding="utf-8")
    subprocess.run(["fc-cache", "-f"], capture_output=True)


def armar_docx(spec: dict, salida: Path) -> Path:
    destino = salida / f"{spec['archivo']}.docx"
    with zipfile.ZipFile(PLANTILLA) as zin, \
            zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                xml = data.decode("utf-8")
                assert "<!--CUERPO-->" in xml, "La plantilla no trae el marcador del cuerpo"
                data = xml.replace("<!--CUERPO-->", cuerpo_xml(spec)).encode("utf-8")
            zout.writestr(item, data)
    return destino


def a_pdf(docx: Path, salida: Path):
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return None
    instalar_fuentes()
    with tempfile.TemporaryDirectory() as perfil:
        subprocess.run([soffice, f"-env:UserInstallation=file://{perfil}", "--headless",
                        "--convert-to", "pdf", "--outdir", str(salida), str(docx)],
                       capture_output=True, timeout=180)
    pdf = salida / (docx.stem + ".pdf")
    return pdf if pdf.exists() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--salida", required=True)
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    for campo in ("archivo", "parrafos", "firmante"):
        if not spec.get(campo):
            sys.exit(f"Falta el campo «{campo}» en el JSON.")
    spec.setdefault("fecha", dt.date.today().isoformat())
    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    docx = armar_docx(spec, salida)
    pdf = a_pdf(docx, salida)
    print(json.dumps({"docx": str(docx), "pdf": str(pdf) if pdf else None,
                      "aviso": None if pdf else
                      "Sin LibreOffice: exportar el DOCX a PDF desde Word."},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
