#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analizar_eef_sae.py — Procesador del Mayor General de SAE para el agente de
Revisión de EEFF. Digiere el libro mayor (CSV de SAE) y, opcionalmente, el
Balance de Situación y el Estado de Resultados (XLSX de SAE), reconstruye los
saldos por cuenta y corre los chequeos de la v1. SOLO LEE — no modifica nada.

Uso:
    python analizar_eef_sae.py --mayor MAYOR.csv [--bg BG.xlsx] [--pyg PYG.xlsx]
                               [--config criterio.json] [--json salida.json]

Convenciones de SAE (vistas en los exports reales):
  - CSV ';'-delimitado, utf-8-sig. Decimales con coma, miles con punto.
  - El HABER viene en NEGATIVO  => saldo neto = sum(DEBE) + sum(HABER).
  - El balance presenta pasivo/patrimonio/ingreso en valor ABSOLUTO; el activo,
    costo y gasto tal cual (incluidas contra-cuentas "(-)", que van negativas).
  - Naturaleza por primer dígito: 1=Activo 2=Pasivo 3=Patrimonio 4=Ingreso
    5=Costo 6/7=Gasto.
"""
import argparse, json, re, unicodedata
from pathlib import Path

TOL = 0.01

def num(s):
    if s is None: return 0.0
    s = str(s).strip()
    if s in ("", "-"): return 0.0
    neg = s.startswith("-") or s.startswith("(")
    s = s.lstrip("-(").rstrip(")").replace(".", "").replace(",", ".")
    s = re.sub(r"[^0-9.\-]", "", s)
    try: v = float(s)
    except ValueError: return 0.0
    return -v if neg else v

def norm(t):
    t = unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", t).strip()

def naturaleza(codigo, nombre, contracuentas):
    es_contra = str(nombre).strip().startswith("(-)") or codigo in contracuentas
    base = {"1":"D","2":"H","3":"H","4":"H","5":"D","6":"D","7":"D"}.get(str(codigo)[:1], "?")
    if es_contra and base in ("D","H"):
        base = "H" if base == "D" else "D"
    return base, es_contra

def nat_presentacion(codigo):
    return "D" if str(codigo)[:1] in ("1","5","6","7") else "H"

def cargar_mayor(path):
    import csv
    raw = Path(path).read_bytes()
    for enc in ("utf-8-sig","utf-8","latin-1"):
        try: text = raw.decode(enc); break
        except UnicodeDecodeError: continue
    head = text.splitlines()[0]
    sep = ";" if head.count(";") >= head.count(",") else ","
    rows = list(csv.reader(text.splitlines(), delimiter=sep))
    header = [norm(h) for h in rows[0]]
    def col(*names):
        for n in names:
            for i,h in enumerate(header):
                if norm(n) == h or norm(n) in h: return i
        return None
    ic = {"cod":col("CODIGO CUENTA","CODIGO","CUENTA CODIGO"),
          "nom":col("NOMBRE CUENTA","NOMBRE","DESCRIPCION"),
          "doc":col("DOCUMENTO"), "debe":col("DEBE"), "haber":col("HABER"),
          "asi":col("NUMERO ASIENTO","NRO ASIENTO","ASIENTO"), "fecha":col("FECHA")}
    if ic["cod"] is None or ic["debe"] is None or ic["haber"] is None:
        raise SystemExit(f"ERROR: faltan columnas CÓDIGO/DEBE/HABER. Cabecera: {header}")
    cuentas = {}; asientos = {}; tot_debe = tot_haber = 0.0; nfilas = 0
    for r in rows[1:]:
        if not r or len(r) <= ic["cod"]: continue
        cod = str(r[ic["cod"]]).strip()
        if cod == "": continue
        nfilas += 1
        d = num(r[ic["debe"]]); h = num(r[ic["haber"]])
        tot_debe += d; tot_haber += h
        c = cuentas.setdefault(cod, {"codigo":cod,
            "nombre": str(r[ic["nom"]]).strip() if ic["nom"] is not None else "",
            "debe":0.0,"haber":0.0,"n":0,"tiene_saldo_inicial":False})
        c["debe"] += d; c["haber"] += h; c["n"] += 1
        if not c["nombre"] and ic["nom"] is not None:
            c["nombre"] = str(r[ic["nom"]]).strip()
        if ic["doc"] is not None and "SALDOS INICIALES" in norm(r[ic["doc"]]):
            c["tiene_saldo_inicial"] = True
        an = str(r[ic["asi"]]).strip() if ic["asi"] is not None else ""
        a = asientos.setdefault(an, {"asiento":an, "debe":0.0, "haber":0.0, "n":0,
            "fecha": str(r[ic["fecha"]]).strip() if ic["fecha"] is not None else "",
            "doc": str(r[ic["doc"]]).strip() if ic["doc"] is not None else ""})
        a["debe"] += d; a["haber"] += h; a["n"] += 1
    for c in cuentas.values():
        c["saldo"] = round(c["debe"] + c["haber"], 2)
        c["debe"] = round(c["debe"], 2); c["haber"] = round(c["haber"], 2)
    for a in asientos.values():
        a["desbalance"] = round(a["debe"] + a["haber"], 2)
    return cuentas, asientos, round(tot_debe,2), round(tot_haber,2), nfilas

def cargar_balance(path):
    try: import openpyxl
    except ImportError: return None, {}
    wb = openpyxl.load_workbook(path, data_only=True); ws = wb.active
    filas = list(ws.iter_rows(values_only=True))
    meta = {"titulo":"","entidad":"","periodo":""}
    if filas: meta["entidad"] = str(filas[0][0] or "").strip()
    hstart = 0
    for i,f in enumerate(filas):
        if f and any("CODIGO" in norm(x) for x in f if x): hstart = i+1; break
        if f and "ESTADO DE RESULTADOS" in norm(f[0] or ""): meta["titulo"]="Estado de Resultados"
        if f and "BALANCE DE SITUACION" in norm(f[0] or ""): meta["titulo"]="Balance de Situación"
        if f and f[0] and "DESDE" in norm(f[0]): meta["periodo"] = str(f[0]).strip()
    detalle = {}
    for f in filas[hstart:]:
        if not f or f[0] in (None,""): continue
        cod = str(f[0]).strip()
        if not re.match(r"^\d+$", cod): continue
        saldo = f[3] if len(f) > 3 else None
        if saldo not in (None,""):
            try: detalle[cod] = round(float(saldo),2)
            except (TypeError,ValueError): pass
    return detalle, meta

TRANSITORIAS_HEUR = ["IVA EN COMPRAS","IVA EN VENTAS",
    "RETENCIONES EN LA FUENTE A PROVEEDORES","DEPOSITOS POR IDENTIFICAR",
    "POR IDENTIFICAR","POR CLASIFICAR","CUENTAS TRANSITORIAS","PARTIDAS POR",
    "ANTICIPO IMPORTACIONES TRANSITO"]
MODULO_HEUR = [("CLIENTES","CxC – Cartera de clientes"),
    ("CUENTAS POR COBRAR","CxC"),("DOCUMENTOS Y CUENTAS POR COBRAR","CxC"),
    ("CUENTAS Y DOCUMENTOS POR PAGAR","CxP – Proveedores"),("CUENTAS POR PAGAR","CxP"),
    ("INVENTARIO","Inventario / Kárdex"),("MERCADERIA","Inventario / Kárdex")]

def slim(c): return {"codigo":c["codigo"],"nombre":c["nombre"],"saldo":c["saldo"]}
def cuenta_va_en(balance, cod):
    return cod[:1] in (("1","2","3") if balance=="BG" else ("4","5","6","7"))

def correr_chequeos(cuentas, asientos, bg, pyg, cfg):
    contracuentas = set(cfg.get("contracuentas", []))
    transitorias_cfg = cfg.get("transitorias", [])
    transitorias_nom = [norm(x) for x in cfg.get("transitorias_nombre", TRANSITORIAS_HEUR)]
    modulos_cfg = cfg.get("modulos", {})
    res = {"chequeos":{}}
    td = round(sum(c["debe"] for c in cuentas.values()),2)
    th = round(sum(c["haber"] for c in cuentas.values()),2)
    desc = round(td+th,2)
    descu = [a for a in (asientos or {}).values() if abs(a.get("desbalance",0)) > TOL]
    descu.sort(key=lambda a: abs(a["desbalance"]), reverse=True)
    res["chequeos"]["partida_doble"] = {"total_debe":td,"total_haber":th,
        "descuadre":desc,"cuadra":abs(desc)<=TOL,
        "asientos_descuadrados":[{"asiento":a["asiento"] or "(saldos iniciales / sin nº)",
            "fecha":a.get("fecha",""), "doc":a.get("doc",""),
            "desbalance":a["desbalance"], "lineas":a["n"]} for a in descu]}
    contrarios = []
    for c in cuentas.values():
        if abs(c["saldo"]) <= TOL: continue
        nat, es_contra = naturaleza(c["codigo"], c["nombre"], contracuentas)
        if nat=="D" and c["saldo"] < -TOL:
            contrarios.append({**slim(c),"naturaleza":"Deudora","contracuenta":es_contra})
        elif nat=="H" and c["saldo"] > TOL:
            contrarios.append({**slim(c),"naturaleza":"Acreedora","contracuenta":es_contra})
    contrarios.sort(key=lambda x: abs(x["saldo"]), reverse=True)
    res["chequeos"]["saldos_contrarios"] = {"cuentas":contrarios,"total":len(contrarios)}
    trans = []
    for c in cuentas.values():
        es_trans = c["codigo"] in transitorias_cfg or any(t in norm(c["nombre"]) for t in transitorias_nom)
        if es_trans: trans.append({**slim(c),"abierta":abs(c["saldo"])>TOL})
    abiertas = [t for t in trans if t["abierta"]]
    res["chequeos"]["transitorias"] = {"detectadas":trans,"abiertas":abiertas,
        "total_detectadas":len(trans),"total_abiertas":len(abiertas)}
    res["chequeos"]["cuadre_balances"] = {}
    for nombre, bal in (("BG",bg),("PYG",pyg)):
        if not bal: continue
        difs, faltan_en_mayor, faltan_en_balance = [], [], []
        for cod, sb in bal.items():
            c = cuentas.get(cod)
            if c is None:
                faltan_en_mayor.append({"codigo":cod,"saldo_balance":sb}); continue
            pres = -c["saldo"] if nat_presentacion(cod)=="H" else c["saldo"]
            if abs(round(pres-sb,2)) > TOL:
                difs.append({"codigo":cod,"nombre":c["nombre"],"saldo_balance":sb,
                    "saldo_mayor":round(pres,2),"diferencia":round(pres-sb,2)})
        cods_bal = set(bal.keys())
        for cod, c in cuentas.items():
            if abs(c["saldo"])>TOL and cod not in cods_bal and cuenta_va_en(nombre,cod):
                faltan_en_balance.append(slim(c))
        res["chequeos"]["cuadre_balances"][nombre] = {"cuentas_balance":len(bal),
            "descuadres":difs,"total_descuadres":len(difs),
            "en_balance_no_en_mayor":faltan_en_mayor,"en_mayor_no_en_balance":faltan_en_balance}
    con_modulo = []
    for c in cuentas.values():
        if abs(c["saldo"]) <= TOL: continue
        if c["codigo"][:1] not in ("1","2"): continue
        mod = modulos_cfg.get(c["codigo"])
        if not mod:
            for patron, etiqueta in MODULO_HEUR:
                if patron in norm(c["nombre"]): mod = etiqueta; break
        if mod: con_modulo.append({**slim(c),"modulo":mod})
    res["chequeos"]["modulos_a_verificar"] = {"cuentas":con_modulo,"total":len(con_modulo)}
    # G. Clasificacion esperada (cuentas mal clasificadas) - naturaleza + mapa del criterio
    clas_esp = cfg.get("clasificacion_esperada", {})
    mal_clas = []
    for cod, esp in (clas_esp or {}).items():
        c = cuentas.get(cod)
        if c is None or abs(c["saldo"]) <= TOL: continue
        e = str(esp).strip().upper()
        if e in ("D","H"):
            nat,_ = naturaleza(c["codigo"], c["nombre"], contracuentas)
            ok = (nat == e); det = f"naturaleza esperada {e}, real {nat}"
        else:
            ok = (str(cod)[:1] == e[:1]); det = f"grupo esperado {e[:1]}, codigo {cod}"
        if not ok:
            mal_clas.append({**slim(c), "esperado": e, "detalle": det})
    res["chequeos"]["clasificacion"] = {"con_mapa": bool(clas_esp),
        "mal_clasificadas": mal_clas, "total": len(mal_clas)}
    # F. Utilidad: reconstruida del mayor vs declarada en el Balance
    ing = -sum(c["saldo"] for c in cuentas.values() if c["codigo"][:1]=="4")
    cos = sum(c["saldo"] for c in cuentas.values() if c["codigo"][:1]=="5")
    gas = sum(c["saldo"] for c in cuentas.values() if c["codigo"][:1] in ("6","7"))
    util_mayor = round(ing - cos - gas, 2)
    util_bg = None
    pat = ["GANANCIA NETA","PERDIDA NETA","RESULTADO DEL EJERCICIO","RESULTADO DEL PERIODO",
           "UTILIDAD DEL EJERCICIO","UTILIDAD NETA","GANANCIA DEL PERIODO","PERDIDA DEL EJERCICIO"]
    for cod, sb in (bg or {}).items():
        nom = (cuentas.get(cod) or {}).get("nombre","")
        # buscar también por el nombre que trae el propio balance no es posible aquí;
        # se identifica por código de patrimonio típico de resultado (3070x/360x) o por nombre del mayor
        if cod[:3] in ("307","306","360") or any(x in norm(nom) for x in pat):
            if cod[:3] in ("307","360"):
                util_bg = sb; break
    res["chequeos"]["utilidad"] = {
        "ingresos": round(ing,2), "costos": round(cos,2), "gastos": round(gas,2),
        "util_mayor": util_mayor, "util_balance": util_bg,
        "diferencia": (round(util_mayor - util_bg, 2) if util_bg is not None else None),
        "cuadra": (util_bg is not None and abs(util_mayor - util_bg) <= TOL),
    }
    return res

def money(x): return f"{x:>16,.2f}"

def reporte(res, cuentas, meta_bg, meta_pyg, nfilas):
    L = []
    ent = (meta_bg or {}).get("entidad") or (meta_pyg or {}).get("entidad") or "(entidad)"
    per = (meta_bg or {}).get("periodo") or (meta_pyg or {}).get("periodo") or ""
    L.append(f"ANÁLISIS DE EEFF (SAE) — {ent}")
    if per: L.append(f"Periodo: {per}")
    L.append(f"Mayor: {nfilas:,} líneas · {len(cuentas)} cuentas con movimiento"); L.append("")
    ch = res["chequeos"]
    pd_ = ch["partida_doble"]
    L.append("【A】 PARTIDA DOBLE DEL MAYOR")
    L.append(f"   Debe {money(pd_['total_debe'])}   Haber {money(pd_['total_haber'])}   Descuadre {money(pd_['descuadre'])}")
    if pd_["cuadra"]:
        L.append("   OK El mayor cuadra.")
    else:
        ad = pd_.get("asientos_descuadrados", [])
        L.append(f"   X DESCUADRE de {pd_['descuadre']:,.2f} en {len(ad)} asiento(s). Registros a revisar:")
        for a in ad[:40]:
            doc = (a.get("doc","") or "")[:22]
            L.append(f"      {a['asiento']:<24} {a.get('fecha',''):<12} {doc:<22} {a['lineas']:>3} lin  desbal={a['desbalance']:>10,.2f}")
        if len(ad) > 40:
            L.append(f"      ... y {len(ad)-40} asiento(s) más (ver el JSON).")
    L.append("")
    sc = ch["saldos_contrarios"]
    L.append(f"【B】 SALDOS CONTRARIOS A SU NATURALEZA — {sc['total']} cuenta(s)")
    if not sc["cuentas"]: L.append("   OK Ninguna cuenta con saldo del signo equivocado.")
    for c in sc["cuentas"]:
        flag = " (contra-cuenta, revisar)" if c["contracuenta"] else ""
        L.append(f"   X {c['codigo']:<12} {c['nombre'][:40]:<40} {money(c['saldo'])}  [{c['naturaleza']}]{flag}")
    L.append("")
    tr = ch["transitorias"]
    L.append(f"【C】 TRANSITORIAS ABIERTAS — {tr['total_abiertas']} abierta(s) de {tr['total_detectadas']} detectada(s)")
    for t in tr["detectadas"]:
        mark = "X ABIERTA" if t["abierta"] else "OK en cero"
        L.append(f"   {mark:<10} {t['codigo']:<12} {t['nombre'][:40]:<40} {money(t['saldo'])}")
    if not tr["detectadas"]: L.append("   (No se detectaron transitorias. Definir la lista en el criterio.)")
    L.append("")
    cb = ch.get("cuadre_balances", {})
    L.append("【D】 CUADRE MAYOR ↔ BALANCES")
    if not cb: L.append("   (No se entregó BG/PYG — el cruce no se corrió.)")
    for nombre, d in cb.items():
        L.append(f"   {nombre}: {d['cuentas_balance']} cuentas de detalle · {d['total_descuadres']} descuadre(s)")
        for x in d["descuadres"]:
            L.append(f"      X {x['codigo']:<12} {x['nombre'][:36]:<36} balance={x['saldo_balance']:,.2f}  mayor={x['saldo_mayor']:,.2f}  dif={x['diferencia']:,.2f}")
        if d["en_balance_no_en_mayor"]:
            L.append(f"      ! {len(d['en_balance_no_en_mayor'])} cuenta(s) en el balance sin movimiento en el mayor")
        if d["en_mayor_no_en_balance"]:
            L.append(f"      ! {len(d['en_mayor_no_en_balance'])} cuenta(s) con saldo en el mayor que no aparecen en el balance")
            for x in d["en_mayor_no_en_balance"][:8]:
                L.append(f"          {x['codigo']:<12} {x['nombre'][:36]:<36} {money(x['saldo'])}")
        if d["total_descuadres"]==0 and not d["en_mayor_no_en_balance"]:
            L.append("      OK Cuadra con el mayor.")
    L.append("")
    mv = ch["modulos_a_verificar"]
    L.append("【E】 CUENTAS CON MÓDULO (cuadre módulo↔contable — pendiente del reporte)")
    L.append("   Para verificar estas, pasá el reporte del módulo correspondiente:")
    for c in mv["cuentas"]:
        L.append(f"   • {c['codigo']:<12} {c['nombre'][:38]:<38} {money(c['saldo'])}  → {c['modulo']}")
    if not mv["cuentas"]: L.append("   (Ninguna identificada.)")
    L.append("")
    ut = ch.get("utilidad")
    if ut:
        L.append("【F】 UTILIDAD: MAYOR vs BALANCE")
        L.append(f"   Ingresos {money(ut['ingresos'])}  Costos {money(ut['costos'])}  Gastos {money(ut['gastos'])}")
        L.append(f"   Utilidad reconstruida del mayor: {money(ut['util_mayor'])}")
        if ut["util_balance"] is not None:
            L.append(f"   Ganancia neta declarada en BG:    {money(ut['util_balance'])}")
            if ut["cuadra"]:
                L.append("   OK La utilidad del mayor cuadra con la del Balance.")
            else:
                L.append(f"   X DIFERENCIA de {ut['diferencia']:,.2f} entre el mayor y el Balance.")
        else:
            L.append("   (No se identificó la cuenta de resultado en el Balance.)")
        L.append("")
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mayor", required=True)
    ap.add_argument("--bg"); ap.add_argument("--pyg")
    ap.add_argument("--config"); ap.add_argument("--json")
    a = ap.parse_args()
    cfg = {}
    if a.config and Path(a.config).exists():
        cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    cuentas, asientos, td, th, nfilas = cargar_mayor(a.mayor)
    bg, meta_bg = (cargar_balance(a.bg) if a.bg else (None, {}))
    pyg, meta_pyg = (cargar_balance(a.pyg) if a.pyg else (None, {}))
    res = correr_chequeos(cuentas, asientos, bg, pyg, cfg)
    res["resumen"] = {"entidad":(meta_bg or {}).get("entidad") or (meta_pyg or {}).get("entidad",""),
        "periodo":(meta_bg or {}).get("periodo") or (meta_pyg or {}).get("periodo",""),
        "cuentas":len(cuentas),"lineas_mayor":nfilas}
    print(reporte(res, cuentas, meta_bg, meta_pyg, nfilas))
    if a.json:
        Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[JSON de hallazgos guardado en {a.json}]")

if __name__ == "__main__":
    main()
