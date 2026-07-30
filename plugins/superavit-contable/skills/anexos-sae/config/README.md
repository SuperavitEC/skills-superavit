# Configuraciones por cliente

Este directorio **no lleva configuraciones reales**. Cada archivo `<cliente>.json`
identifica a un cliente por razón social y RUC, y describe qué cuentas entran en cada
anexo — es información del cliente, no un procedimiento, y por eso no viaja en el
repositorio público de la firma.

`_plantilla.json` es la estructura vacía. Para dar de alta un cliente:

1. Copiar `_plantilla.json` a `<cliente>.json` **en la máquina donde se corre el script**.
2. Llenar `cliente` y `ruc`.
3. Ajustar los códigos de cuenta de cada anexo al plan de cuentas de ese cliente.
4. Registrar en la wiki, en `clientes/<cliente>/`, qué anexos aplican y cualquier
   particularidad de sus reportes.

Los archivos `<cliente>.json` que se creen acá **no se suben al repositorio**. El
`.gitignore` de la raíz ya los excluye.

> Regla de la firma: la skill describe *cómo se arma un anexo*; la wiki dice *qué decide
> cada cliente*. Ver `superavit/procesos/distribucion-skills.md`.
