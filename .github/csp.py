#!/usr/bin/env python3
"""Le agrega a index.html la CSP (Content-Security-Policy) al publicar.

La CSP es una lista de los sitios desde donde la página puede cargar código, estilos, fuentes,
y a cuáles se puede conectar. Si alguien lograra meter código en la página (por ejemplo, con un
texto armado a propósito en una nota), el navegador no lo ejecuta porque no está en la lista.

El código de la app está en una etiqueta script dentro del mismo index.html. Para permitir ese
código y ningún otro, la CSP lleva su "huella" (un hash SHA-256): si cambia una sola letra,
la huella ya no coincide. Por eso la huella se calcula acá, al publicar, y no a mano.

GitHub Pages no deja configurar cabeceras, así que la CSP va como etiqueta meta. Por eso no se
puede usar frame-ancestors (impedir que otro sitio muestre la app adentro de un marco).

Uso: python3 .github/csp.py ruta/al/index.html   (modifica el archivo)
"""
import base64
import hashlib
import re
import sys


def huella(codigo):
    return "'sha256-" + base64.b64encode(hashlib.sha256(codigo.encode('utf-8')).digest()).decode() + "'"


def politica(html):
    scripts = re.findall(r'<script>(.*?)</script>', html, re.S)
    if not scripts or len(scripts) != len(re.findall(r'<script\b', html)):
        sys.exit('csp.py: se esperaba solo código en etiquetas script sin atributos; revisar la CSP a mano.')
    auth = re.search(r"authDomain: '([^']+)'", html)
    if not auth:
        sys.exit('csp.py: no encontré authDomain en FIREBASE_CONFIG.')
    # App Check usa reCAPTCHA, que carga su código y un marco invisible desde google.com
    # (https://cloud.google.com/recaptcha/docs/faq). Solo se permite si la app tiene la clave cargada.
    recaptcha = ' https://www.google.com/recaptcha/' if re.search(r"APP_CHECK_KEY = '[^']+'", html) else ''
    return '; '.join([
        "default-src 'self'",
        # El código de la app, Firebase (gstatic), el inicio de sesión de Google (apis.google.com) y ExcelJS.
        "script-src 'self' " + ' '.join(huella(s) for s in scripts)
        + ' https://www.gstatic.com https://apis.google.com https://cdn.jsdelivr.net' + recaptcha,
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
        'font-src https://fonts.gstatic.com',
        # Firestore baja una imagen de prueba de google.com para saber si volvió la conexión.
        "img-src 'self' https://www.google.com",
        # Firestore, el inicio de sesión y la renovación de la sesión (todos en *.googleapis.com).
        "connect-src 'self' https://*.googleapis.com" + recaptcha,
        # Firebase abre un marco invisible en el dominio de autenticación para el inicio de sesión.
        'frame-src https://' + auth.group(1) + (recaptcha + ' https://recaptcha.google.com/recaptcha/' if recaptcha else ''),
        "worker-src 'self'",
        "manifest-src 'self'",
        "object-src 'none'",
        "base-uri 'none'",
        "form-action 'self'",
    ])


def main(ruta):
    with open(ruta, encoding='utf-8') as f:
        html = f.read()
    if 'Content-Security-Policy' in html:
        sys.exit(f'csp.py: {ruta} ya tiene una CSP.')
    ancla = '<meta charset="utf-8">'
    if ancla not in html:
        sys.exit(f'csp.py: no encontré {ancla} en {ruta}.')
    meta = f'<meta http-equiv="Content-Security-Policy" content="{politica(html)}">'
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(html.replace(ancla, ancla + '\n' + meta, 1))
    print(f'CSP agregada a {ruta}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
