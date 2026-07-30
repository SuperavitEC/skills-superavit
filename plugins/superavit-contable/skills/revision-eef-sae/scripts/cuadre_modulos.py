#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cuadre_modulos.py — Helper de cuadre de módulos SAE para el agente de Revisión.
Hace en Python los cruces PESADOS (cartera por factura↔global, inventario kárdex↔contable)
y devuelve un resumen chico. El modelo NUNCA lee las decenas de miles de filas — las muele
este script. Así el tamaño del archivo no importa (escala sin cambiar el costo del modelo).

Uso:
  Cartera:    python cuadre_modulos.py cartera --global GLOBAL.xlsx --factura PORFACTURA.xlsx
  Inventario: python cuadre_modulos.py inventario --mayor MAYOR.csv --kardex KARDEX.xlsx \
                       --stock STOCK.xlsx [--cuenta 1010306]
SOLO LEE.
"""
import argparse, re, unicodedata, csv
from pathlib import Path
TOL=0.01

def num(x):
    if x is None: return 0.0
    if isinstance(x,(int,float)): return float(x)
    s=str(x).strip()
    if s in("","-"): return 0.0
    neg=s.startswith("-") or s.startswith("(")
    s=s.lstrip("-(").rstrip(")").replace(".","").replace(",",".")
    s=re.sub(r"[^0-9.\-]","",s)
    try: v=float(s)
    except: return 0.0
    return -v if neg else v

def norm(t):
    t=unicodedata.normalize("NFKD",str(t)).encode("ascii","ignore").decode().upper()
    return re.sub(r"\s+"," ",t).strip()

def load_xlsx(path):
    import openpyxl
    wb=openpyxl.load_workbook(path,data_only=True); ws=wb.active
    return list(ws.iter_rows(values_only=True))

def header_row(rows, keyword):
    for i,r in enumerate(rows):
        if r and any(keyword in norm(x) for x in r if x): return i
    return 0

# ---------------- CARTERA ----------------
def cuadre_cartera(global_path, factura_path):
    g=load_xlsx(global_path); hs=header_row(g,"CEDULA")
    g_by={}; g_pend=g_ant=0.0
    for r in g[hs+1:]:
        if not r or r[0] is None: continue
        ced=str(r[0]).strip()
        if not ced or ced.upper().startswith("TOTAL"): continue
        pend=num(r[3]) if len(r)>3 else 0; ant=num(r[4]) if len(r)>4 else 0
        g_by[ced]=g_by.get(ced,0.0)+pend; g_pend+=pend; g_ant+=ant
    f=load_xlsx(factura_path); fs=header_row(f,"CEDULA")
    # detectar col cédula y pendiente
    hdr=[norm(c) for c in f[fs]]
    ci=next((i for i,h in enumerate(hdr) if "CEDULA" in h or "RUC" in h),5)
    pi=next((i for i,h in enumerate(hdr) if h=="PENDIENTE"),12)
    f_by={}; f_tot=0.0
    for r in f[fs+1:]:
        if not r or r[0] is None: continue
        ced=str(r[ci]).strip() if len(r)>ci and r[ci] else "?"
        p=num(r[pi]) if len(r)>pi else 0
        f_by[ced]=f_by.get(ced,0.0)+p; f_tot+=p
    difs=sorted([(c,round(f_by.get(c,0)-g_by.get(c,0),2)) for c in set(f_by)|set(g_by)],
                key=lambda x:abs(x[1]),reverse=True)
    difs=[(c,d) for c,d in difs if abs(d)>1]
    print("=== CUADRE CARTERA (por factura ↔ global) ===")
    print(f"  por factura Σ pendiente = {f_tot:,.2f}")
    print(f"  global      Σ pendiente = {g_pend:,.2f}   Σ anticipos = {g_ant:,.2f}")
    print(f"  diferencia por factura - global = {f_tot-g_pend:,.2f}")
    print(f"  clientes con diferencia (>$1): {len(difs)}")
    for c,d in difs[:15]:
        print(f"     {c:<16} factura={f_by.get(c,0):>12,.2f} global={g_by.get(c,0):>12,.2f} dif={d:>10,.2f}")
    if difs: print(f"  (top {min(15,len(difs))} mostrados; el resto suma {sum(d for _,d in difs[15:]):,.2f})")

# ---------------- INVENTARIO ----------------
def scan_mayor_cuenta(mayor_path, cuenta):
    raw=Path(mayor_path).read_bytes()
    for enc in ("utf-8-sig","utf-8","latin-1"):
        try: text=raw.decode(enc); break
        except: continue
    rows=list(csv.reader(text.splitlines(),delimiter=";"))
    H=[norm(h) for h in rows[0]]
    def col(*names):
        for n in names:
            for i,h in enumerate(H):
                if norm(n)==h or norm(n) in h: return i
        return None
    iC=col("CODIGO CUENTA","CODIGO"); iDoc=col("DOCUMENTO"); iD=col("DEBE"); iH=col("HABER")
    sal_ini=0.0; bydoc={}; total=0.0
    for r in rows[1:]:
        if len(r)<=iH or str(r[iC]).strip()!=cuenta: continue
        v=num(r[iD])+num(r[iH]); total+=v
        doc=str(r[iDoc]).strip() if iDoc is not None else ""
        if "SALDO" in norm(doc) and "INICIAL" in norm(doc): sal_ini+=v
        bydoc[norm(doc)]=bydoc.get(norm(doc),0.0)+v
    return sal_ini, total, bydoc

def cuadre_inventario(mayor_path, kardex_path, stock_path, cuenta):
    # stock
    s=load_xlsx(stock_path); hs=header_row(s,"COSTO TOTAL")
    hdr=[norm(c) for c in s[hs]]
    cct=next((i for i,h in enumerate(hdr) if "COSTO TOTAL" in h),9)
    cst=next((i for i,h in enumerate(hdr) if h=="STOCK"),7)
    stock_tot=0.0; items=0; neg=0
    for r in s[hs+1:]:
        if not r or r[0] is None: continue
        stock_tot+=num(r[cct]) if len(r)>cct else 0; items+=1
        if len(r)>cst and num(r[cst])<0: neg+=1
    # contable
    sal_ini, cont_total, cont_bydoc = scan_mayor_cuenta(mayor_path, cuenta)
    cont_mov = cont_total - sal_ini
    # kardex
    k=load_xlsx(kardex_path); ks=header_row(k,"BENEFICIARIO")
    # sub-headers en la fila siguiente; TOTAL de ingresos/salidas
    ing=sal=0.0; kbydoc={}; lastsaldo={}
    # offsets típicos SAE: INGRESOS.TOTAL=11, SALIDAS.TOTAL=14, SALDO.TOTAL=17, COD=1, DOC=6
    ING,SAL,STOT,COD,DOC,SCANT,SPU,NOM=11,14,17,1,6,15,13,3
    minsaldo={}; nombres={}; costos={}
    for r in k[ks+2:]:
        if not r or r[COD] is None: continue
        cod=str(r[COD])
        ing+=num(r[ING]); sal+=num(r[SAL])
        lastsaldo[cod]=num(r[STOT])
        d=norm(r[DOC]) if r[DOC] else ""
        kbydoc[d]=kbydoc.get(d,0.0)+num(r[ING])-num(r[SAL])
        sc=num(r[SCANT])
        if cod not in minsaldo or sc<minsaldo[cod]: minsaldo[cod]=sc
        nombres[cod]=str(r[NOM])[:36] if len(r)>NOM and r[NOM] else cod
        pu=num(r[SPU])
        if pu>0: costos.setdefault(cod,[]).append(pu)
    kneto=ing-sal
    # normalizar tipo de documento a categorías canónicas (el mayor y el kárdex los nombran distinto)
    def canon(d):
        if "SALDO" in d and "INICIAL" in d: return None  # apertura, no es movimiento del periodo
        if "CLIENTE" in d and ("FACTURA" in d or "NOTA DE CREDITO" in d or "NOTA CREDITO" in d): return "VENTAS (costo de ventas)"
        if "PROVEEDOR" in d and ("FACTURA" in d or "NOTA DE CREDITO" in d or "NOTA CREDITO" in d): return "COMPRAS"
        if "SIN DOCUMENTO" in d: return "AJUSTE MANUAL (NO pasa por kárdex)"
        if "INGRESO" in d or "BAJA" in d: return "AJUSTE DE KARDEX (ingreso/baja)"
        return "OTROS"
    def bucketize(by):
        out={}
        for d,v in by.items():
            c=canon(d)
            if c is None: continue
            out[c]=out.get(c,0.0)+v
        return out
    cb=bucketize(cont_bydoc); kb=bucketize(kbydoc)
    print("=== CUADRE INVENTARIO (stock/kárdex ↔ contable) ===")
    print(f"  Stock Global (Σ costo total) = {stock_tot:,.2f}  ({items} ítems, {neg} con stock negativo)")
    print(f"  Contable {cuenta}            = {cont_total:,.2f}  (saldo inicial {sal_ini:,.2f} + mov {cont_mov:,.2f})")
    print(f"  >>> DESCUADRE stock - contable = {stock_tot-cont_total:,.2f}")
    print(f"\n  Movimiento 2026 contable vs kárdex, por categoría (lo que DIVERGE es el origen):")
    for c in sorted(set(cb)|set(kb)):
        cv=cb.get(c,0.0); kv=kb.get(c,0.0); diff=round(cv-kv,2)
        mark=" <-- DIVERGE" if abs(diff)>TOL else " ok"
        print(f"     {c:<36} contable={cv:>13,.2f} kardex={kv:>13,.2f} dif={diff:>11,.2f}{mark}")
    print(f"\n  Total mov: contable={cont_mov:,.2f}  kárdex={kneto:,.2f}  dif={cont_mov-kneto:,.2f}")
    print("  → El 'AJUSTE MANUAL' (asientos sin documento que no pasan por el kárdex) y la")
    print("    diferencia en VENTAS (costeo) son las causas típicas del descuadre. Drill en esas.")
    import statistics
    negs=sorted([(c,minsaldo[c],nombres.get(c,c)) for c in minsaldo if minsaldo[c]<-1e-6], key=lambda x:x[1])
    print("\n  PRODUCTOS CON STOCK NEGATIVO en el kardex del periodo: %d" % len(negs))
    for c,ms,nom in negs[:20]:
        print("     %-16s %-36s min stock = %.1f" % (c,nom,ms))
    if not negs: print("     (ninguno este periodo -- OJO: revisar tambien los kardex de meses anteriores)")
    absurd=[]
    for c,lst in costos.items():
        if len(lst)<3: continue
        med=statistics.median(lst); mx=max(lst)
        if med>0 and mx>med*5: absurd.append((c,nombres.get(c,c),med,mx))
    absurd.sort(key=lambda x:(x[3]/x[2]) if x[2] else 0, reverse=True)
    print("\n  PRODUCTOS CON COSTO UNITARIO ABSURDO (un costo > 5x su mediana): %d" % len(absurd))
    for c,nom,med,mx in absurd[:15]:
        print("     %-16s %-36s mediana=%.2f  max=%.2f" % (c,nom,med,mx))

# ---------------- parser robusto a coma Y punto decimal (xlsx vs CSV SAE) ----------------
def dnum(x):
    if x is None: return 0.0
    if isinstance(x,(int,float)): return float(x)
    s=str(x).strip()
    if s in ("","-"): return 0.0
    neg=s.startswith("-") or s.startswith("(")
    s=s.lstrip("-(").rstrip(")").replace("$","").replace(" ","").replace("%","")
    if "," in s and "." in s: s=s.replace(".","").replace(",",".")  # SAE CSV: . miles, , decimal
    elif "," in s: s=s.replace(",",".")                              # decimal con coma
    s=re.sub(r"[^0-9.\-]","",s)                                      # solo '.' o sin sep -> ya decimal
    try: v=float(s)
    except: return 0.0
    return -v if neg else v

# ---------------- STOCK: anomalias (front-line, SOLO el reporte de stock) ----------------
def stock_anomalias(stock_path):
    s=load_xlsx(stock_path); hs=header_row(s,"COSTO TOTAL")
    hdr=[norm(c) for c in s[hs]]
    cct=next((i for i,h in enumerate(hdr) if "COSTO TOTAL" in h),9)
    cst=next((i for i,h in enumerate(hdr) if h=="STOCK"),7)
    ccu=next((i for i,h in enumerate(hdr) if "COSTO UNITARIO" in h or h=="COSTO U."),8)
    cnom=next((i for i,h in enumerate(hdr) if h=="NOMBRE"),2)
    tot=0.0; items=0; negS=[]; costNeg=[]; huerf=[]; incons=[]
    for r in s[hs+1:]:
        if not r or r[0] is None or str(r[0]).strip()=="" : continue
        cod=str(r[0]).strip()
        if cod.upper().startswith(("TOTAL","RESUMEN","CODIGO","CODIGO")): continue
        stock=dnum(r[cst]) if len(r)>cst else 0
        ctot=dnum(r[cct]) if len(r)>cct else 0
        cu=dnum(r[ccu]) if len(r)>ccu else 0
        nom=str(r[cnom])[:34] if len(r)>cnom and r[cnom] else cod
        tot+=ctot; items+=1
        if stock<0: negS.append((cod,nom,stock,cu,ctot))
        if stock>0 and ctot<-0.01: costNeg.append((cod,nom,stock,cu,ctot))
        if abs(stock)<1e-9 and abs(ctot)>0.01: huerf.append((cod,nom,stock,cu,ctot))
        if stock!=0 and abs(stock*cu-ctot)>0.05: incons.append((cod,nom,stock,cu,ctot,ctot-stock*cu))
    print("=== ANOMALIAS DE STOCK (front-line -- solo el reporte de stock) ===")
    print(f"  Sum costo total = {tot:,.2f}  ({items} items)")
    print(f"\n  [A] STOCK NEGATIVO (casito C1): {len(negS)}")
    for c,n,st,cu,ct in negS[:20]: print(f"      {c:<16} stock={st:>9,.2f} cu={cu:>10,.3f} ctot={ct:>11,.2f}  {n}")
    print(f"\n  [B] COSTO TOTAL NEGATIVO con stock>0 (baja mal costeada, casito C2): {len(costNeg)}")
    for c,n,st,cu,ct in costNeg[:20]: print(f"      {c:<16} stock={st:>9,.2f} cu={cu:>10,.3f} ctot={ct:>11,.2f}  {n}")
    print(f"\n  [C] HUERFANOS (stock=0 pero costo!=0): {len(huerf)}")
    for c,n,st,cu,ct in huerf[:20]: print(f"      {c:<16} ctot={ct:>11,.2f}  {n}")
    print(f"\n  [D] INCONSISTENCIA stock*cu != costo total: {len(incons)}")
    for c,n,st,cu,ct,dv in sorted(incons,key=lambda x:-abs(x[5]))[:15]:
        print(f"      {c:<16} stock={st:>8,.2f} cu={cu:>9,.3f} ctot={ct:>10,.2f} desvio={dv:>9,.2f}  {n}")
    if not (negS or costNeg or huerf or incons): print("\n  (sin anomalias -- inventario limpio)")
    else: print("\n  -> De [A]/[B]/[C]/[D] salen los items a pedir el kardex y correr 'kardex-item'.")

# ---------------- KARDEX de UN item: traza el quiebre del costeo ----------------
def kardex_item(kardex_path):
    k=load_xlsx(kardex_path)
    ks=next((idx for idx,rr in enumerate(k) if rr and len(rr)>1 and norm(rr[1])=="FECHA"), header_row(k,"FECHA"))
    rows=[r for r in k[ks+2:] if r and len(r)>14 and r[1] and str(r[1]).strip() and str(r[0]).strip()!=""]
    if not rows: print("Sin movimientos en el kardex."); return
    op=rows[0]
    print("=== TRAZA KARDEX DE UN ITEM ===")
    print(f"  Apertura: cant={dnum(op[12]):.0f}  cu={dnum(op[13]):.4f}  total={dnum(op[14]):.2f}   ({op[2]})")
    quiebres=[]
    for idx,r in enumerate(rows):
        sq=dnum(r[12]); st=dnum(r[14]); ev=[]
        if sq<0: ev.append("STOCK<0")
        if st<0: ev.append("TOTAL<0")
        if "BAJA" in norm(r[2]):
            prev=rows[idx-1] if idx>0 else r
            mm=dnum(prev[13]); salcu=dnum(r[10]); salc=dnum(r[9])
            if mm>0 and salcu>mm*2:
                ev.append(f"BAJA a ${salcu:.4f} vs media movil ${mm:.4f}  -> correcto {salc:.0f}u x {mm:.4f} = ${salc*mm:.2f}")
        if ev: quiebres.append((r,ev))
    if not quiebres:
        print("  Sin quiebres detectados (ni stock<0, ni total<0, ni bajas sobrecosteadas).")
    for r,ev in quiebres[:12]:
        print(f"  N{str(r[0]):>5} {r[1]} {str(r[2])[:17]:<17} doc {str(r[3]):<11}: {'; '.join(ev)}")
    last=rows[-1]
    print(f"  Saldo FINAL ({last[1]}): cant={dnum(last[12]):.0f}  cu={dnum(last[13]):.4f}  total={dnum(last[14]):.2f}")

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="tipo",required=True)
    c=sub.add_parser("cartera"); c.add_argument("--global",dest="g",required=True); c.add_argument("--factura",required=True)
    i=sub.add_parser("inventario"); i.add_argument("--mayor",required=True); i.add_argument("--kardex",required=True)
    i.add_argument("--stock",required=True); i.add_argument("--cuenta",default="1010306")
    sa=sub.add_parser("stock-anomalias"); sa.add_argument("--stock",required=True)
    ki=sub.add_parser("kardex-item"); ki.add_argument("--kardex",required=True)
    a=ap.parse_args()
    if a.tipo=="cartera": cuadre_cartera(a.g,a.factura)
    elif a.tipo=="inventario": cuadre_inventario(a.mayor,a.kardex,a.stock,a.cuenta)
    elif a.tipo=="stock-anomalias": stock_anomalias(a.stock)
    elif a.tipo=="kardex-item": kardex_item(a.kardex)

if __name__=="__main__": main()
