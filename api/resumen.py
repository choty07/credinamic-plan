"""GET /api/resumen?monto=...&tipo=...&cuotas=...&nombre=... -> tarjeta JPG 1200x630 (vista previa WhatsApp)."""
import io
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import generar_resumen  # noqa: E402
from plan import leer_parametros  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            monto, tipo, cuotas, nombre = leer_parametros(urlparse(self.path).query)
            buf = io.BytesIO()
            generar_resumen(monto, tipo, cuotas, buf, nombre)
            body = buf.getvalue()
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Cache-Control", "public, max-age=86400")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (ValueError, KeyError) as e:
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"Datos no validos: {e}".encode("utf-8"))
