# Bajar un comprobante autorizado del SRI por su clave de acceso

Sirve para **cualquier** comprobante electrónico ecuatoriano (retención, factura, NC, ND,
liquidación de compra) del que tengas la **clave de acceso de 49 dígitos**: la que viene en la
columna `CLAVE_ACCESO` del TXT de «Comprobantes recibidos» y la que está impresa en el RIDE.

## Por qué no se hace con Bash

El contenedor donde corre el agente **no tiene salida a `*.sri.gob.ec`**: `curl`, `urllib` y
`requests` devuelven `Tunnel connection failed: 403 Forbidden`. No es un problema del SRI ni del
script — es el proxy del sandbox. **No insistas por ahí y no reportes «el SRI no responde».**

La consulta se hace **desde el navegador del usuario** con las tools `claude-in-chrome`: se abre
una pestaña en el dominio del SRI y se hace el `fetch` **same-origin**, así no hay CORS.

## Endpoint

```
POST https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline
Content-Type: text/xml;charset=UTF-8
SOAPAction: (vacío)
```

Cuerpo:

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ec="http://ec.gob.sri.ws.autorizacion">
  <soapenv:Header/>
  <soapenv:Body>
    <ec:autorizacionComprobante>
      <claveAccesoComprobante>CLAVE_DE_49_DIGITOS</claveAccesoComprobante>
    </ec:autorizacionComprobante>
  </soapenv:Body>
</soapenv:Envelope>
```

La respuesta trae `<estado>` (debe decir `AUTORIZADO`), `<fechaAutorizacion>` y el XML del
comprobante **dentro de un CDATA** en `<comprobante>`.

## Procedimiento

1. `tabs_create_mcp` — **pestaña propia**, no reutilices la del usuario (si él navega, se pierde
   lo que tengas en `window`).
2. `navigate` a
   `https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl`.
3. `javascript_tool` con el script de abajo. **Devolvé solo el resumen parseado, nunca el XML
   completo ni base64** — el canal bloquea base64 y el XML crudo quema contexto para nada.
4. `tabs_close_mcp` al terminar.

```js
const claves = ["<clave1>", "<clave2>"];
const url = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline";
const env = c => `<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ec="http://ec.gob.sri.ws.autorizacion"><soapenv:Header/><soapenv:Body><ec:autorizacionComprobante><claveAccesoComprobante>${c}</claveAccesoComprobante></ec:autorizacionComprobante></soapenv:Body></soapenv:Envelope>`;
const P = new DOMParser();
const out = [];
for (const c of claves) {
  const t = await (await fetch(url, {method:"POST",
    headers:{"Content-Type":"text/xml;charset=UTF-8","SOAPAction":""}, body: env(c)})).text();
  const soap = P.parseFromString(t, "text/xml");
  const estado = soap.querySelector("estado")?.textContent;
  const x = P.parseFromString(soap.querySelector("comprobante")?.textContent || "", "text/xml");
  const g = (n, r) => (r||x).getElementsByTagName(n)[0]?.textContent || "";
  const s = x.getElementsByTagName("docSustento")[0];
  const rets = [...(s ? s.getElementsByTagName("retencion") : x.getElementsByTagName("impuesto"))]
    .map(r => [g("codigo",r), g("codigoRetencion",r), g("baseImponible",r),
               g("porcentajeRetener",r), g("valorRetenido",r)].join("|"));
  out.push([estado, g("estab")+"-"+g("ptoEmi")+"-"+g("secuencial"), g("razonSocial").slice(0,14),
            g("fechaEmision"), g("numDocSustento", s || x), rets.join(" ; ")].join(" # "));
}
out.join("\n")
```

Salida de ejemplo:

```
AUTORIZADO # 001-001-000000033 # EMPRESA XYZ SA # 04/08/2026 # 001001000002193 # 1|303A|225.00|5.00|11.25 ; 2|2|33.75|70.00|23.63
```

## Cómo leer el resultado

| Campo | Qué es |
|---|---|
| `estado` | Debe ser `AUTORIZADO`. Cualquier otra cosa → **frená**, no cargues nada. |
| `numDocSustento` | La **factura de venta** sobre la que aplica, sin guiones (`001001000002193` = `001-001-000002193`). Con eso ubicás el `account.move` en Odoo. |
| `codigo` | `1` = Renta · `2` = IVA · `6` = ISD. |
| `codigoRetencion` | El código del SRI (`303A`, `3440`, `2`…). **No lo asumas: varía por cliente.** |
| `baseImponible` / `porcentajeRetener` / `valorRetenido` | Los tres van tal cual al asistente de Odoo. |

## Límites conocidos

- Comprobantes **v1.0.0** (viejos) no traen `<docsSustento>`: las retenciones cuelgan de
  `<impuesto>` y el número de la factura está en `numDocSustento` dentro de cada impuesto. El
  script de arriba ya contempla los dos formatos.
- El canal del navegador **bloquea base64**, así que no se puede traer el XML para adjuntarlo a
  Odoo por esta vía. El respaldo formal en Odoo es el campo **número de autorización**; si además
  se quiere el XML archivado, lo baja el usuario del portal del SRI.
- Si la pestaña navega a otro dominio, `window.__…` se pierde. Guardá y parseá **en la misma
  llamada** cuando puedas.
