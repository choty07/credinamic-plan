"""GET /api/plan?monto=1500000&tipo=quincenales&cuotas=14&nombre=Laura -> imagen PNG del plan de pagos."""
import io
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import generar  # noqa: E402


def leer_parametros(query):
    q = parse_qs(query)
    get = lambda k, d=None: (q.get(k) or [d])[0]
    monto = int(str(get("monto", "0")).replace(".", "").replace(",", "").replace("$", "").strip())
    tipo = (get("tipo", "quincenales") or "").lower()
    if tipo.startswith("q"):
        tipo = "quincenales"
    elif tipo.startswith("m"):
        tipo = "mensuales"
    cuotas = int(get("cuotas", "0"))
    nombre = get("nombre")
    if nombre:
        nombre = nombre.strip().split()[0][:20].capitalize()
    return monto, tipo, cuotas, nombre


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            monto, tipo, cuotas, nombre = leer_parametros(urlparse(self.path).query)
            buf = io.BytesIO()
            generar(monto, tipo, cuotas, buf, nombre)
            body = buf.getvalue()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Cache-Control", "public, max-age=86400")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (ValueError, KeyError) as e:
            msg = f"Datos no validos: {e}".encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(msg)
