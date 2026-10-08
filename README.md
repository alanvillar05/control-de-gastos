# Libreta de cuentas

App web para anotar ingresos, gastos, deudas y lo que te deben, con saldos por cuenta (Mercado Pago, efectivo y las que agregues), resumen anual y exportación a Excel.

**Privacidad:** no hay servidor ni base de datos compartida. Lo que anota cada persona se guarda solo en el navegador de su dispositivo (`localStorage`). Nadie más lo ve.

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `index.html` | La app completa (HTML, CSS y JavaScript en un solo archivo). |
| `manifest.webmanifest` | Nombre e íconos para instalarla en la pantalla de inicio. |
| `sw.js` | Service worker: permite abrirla sin conexión. |
| `icon-*.png`, `apple-touch-icon.png` | Íconos. |

## Publicar en GitHub Pages

1. Crear un repositorio **público** (por ejemplo `libreta`).
2. Subir todos estos archivos a la raíz del repositorio.
3. **Settings › Pages › Build and deployment**: *Source* = *Deploy from a branch*, *Branch* = `main`, carpeta `/ (root)`. Guardar.
4. En unos minutos queda en `https://USUARIO.github.io/libreta/`.

## Actualizar

Reemplazar `index.html` en el repositorio. Si se cambian otros archivos, subir también el número de `CACHE` en `sw.js` (por ejemplo `libreta-v2`) para que los celulares descarten la copia vieja.

## Recomendaciones para quien la usa

- Hacer de vez en cuando una copia desde **⋯ › Descargar copia de seguridad**: si se borran los datos del navegador, se pierde lo anotado.
- Para tenerla como app: en Chrome, **⋮ › Agregar a la pantalla principal** (o *Instalar app*).
