"""GET /p?monto=...&tipo=...&cuotas=...&nombre=...

Pagina corta para enviar por WhatsApp: WhatsApp lee la etiqueta og:image y muestra
la imagen del plan de pagos como vista previa grande del enlace.
"""
import html
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, urlencode

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import plan, LIMITES  # noqa: E402
from plan import leer_parametros  # noqa: E402


def cop(v):
    return "$" + f"{v:,.0f}".replace(",", ".")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            monto, tipo, cuotas, nombre = leer_parametros(urlparse(self.path).query)
            lo, hi = LIMITES[tipo]
            if not (300_000 <= monto <= 1_500_000 and lo <= cuotas <= hi):
                raise ValueError("fuera de rango")
        except (ValueError, KeyError):
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Datos no validos".encode("utf-8"))
            return

        filas = plan(monto, tipo, cuotas)
        cuota = filas[0][4]
        freq = "quincenal" if tipo == "quincenales" else "mensual"
        params = {"monto": monto, "tipo": tipo, "cuotas": cuotas}
        if nombre:
            params["nombre"] = nombre
        host = self.headers.get("host", "")
        img = f"https://{host}/api/plan?{urlencode(params)}"
        og = f"https://{host}/api/resumen?{urlencode(params)}"
        titulo = f"Tu plan de pagos: {cuotas} cuotas de {cop(cuota)} ({freq})"
        desc = f"Crédito de {cop(monto)}. Valores aproximados, sujeto a estudio y aprobación."

        page = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titulo)}</title>
<meta property="og:title" content="{html.escape(titulo)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{html.escape(og)}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:type" content="website">
<style>body{{margin:0;background:#1e408c;display:flex;justify-content:center}}img{{width:100%;max-width:540px;height:auto}}</style>
</head><body><img src="{html.escape(img)}" alt="{html.escape(titulo)}"></body></html>"""
        body = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
