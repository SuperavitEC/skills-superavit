#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""recalc.py — recalcula un .xlsx con LibreOffice headless (si está) y reporta las celdas con
error de fórmula. Verificación obligatoria antes de entregar el paquete de anexos.
Uso: python recalc.py ANEXOS.xlsx"""
import sys, subprocess, shutil, tempfile, os
import openpyxl
ERR={"#DIV/0!","#REF!","#VALUE!","#NAME?","#NULL!","#NUM!","#N/A","#ERROR!","#¡REF!","#¡VALOR!","#¡DIV/0!","#¿NOMBRE?"}
def main():
    if len(sys.argv)<2: print("uso: python recalc.py ANEXOS.xlsx"); return
    f=sys.argv[1]
    so=shutil.which("soffice") or shutil.which("libreoffice")
    if so:
        d=tempfile.mkdtemp()
        subprocess.run([so,"--headless","--calc","--convert-to","xlsx","--outdir",d,f],
                       check=False,capture_output=True)
        out=os.path.join(d, os.path.splitext(os.path.basename(f))[0]+".xlsx")
        if os.path.exists(out): f=out
    else:
        print("[aviso] LibreOffice no está instalado: se revisan los valores cacheados del archivo.")
    wb=openpyxl.load_workbook(f,data_only=True)
    errs=[]
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value,str) and c.value.strip() in ERR:
                    errs.append((ws.title,c.coordinate,c.value.strip()))
    print(f"total_errors: {len(errs)}")
    for e in errs[:50]: print("  ", e[0], e[1], e[2])
if __name__=="__main__": main()
