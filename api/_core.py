"""Generador de imagen "Tu plan de pagos" - Credinamic (prototipo).

Usa la misma formula del simulador de credinamic.com.co:
  quincenal: 0,7% por periodo | mensual: 1,65% por periodo
  cuota fija (sistema frances), cada componente redondeado como en la pagina.

Uso: python3 plan_pagos.py <monto> <quincenales|mensuales> <cuotas> <salida.png> [nombre]
"""
import sys
from PIL import Image, ImageDraw, ImageFont

TASAS = {"quincenales": 0.007, "mensuales": 0.0165}
LIMITES = {"quincenales": (6, 14), "mensuales": (3, 14)}

import os
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
FONT_DIR = BASE + "/"
POPPINS = os.path.join(BASE, "Poppins-Bold.ttf")


def f(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def plan(valor, tipo, cuotas):
    c = TASAS[tipo]
    k = (1 + c) ** cuotas - 1
    filas = []
    for i in range(1, cuotas + 1):
        ac = round(valor * c * (1 + c) ** (i - 1) / k)
        ai = round(valor * c * ((1 + c) ** cuotas - (1 + c) ** (i - 1)) / k)
        sc = round(valor * ((1 + c) ** cuotas - (1 + c) ** i) / k)
        filas.append((i, ac, ai, max(0, sc), ac + ai))
    return filas


def cop(v):
    return "$ " + f"{v:,.0f}".replace(",", ".")


# Colores tomados del estilo de la pagina de Credinamic
AZUL_1 = (30, 64, 140)
AZUL_2 = (42, 84, 160)
CELESTE = (91, 179, 219)
CARD = (62, 96, 168)
BLANCO = (255, 255, 255)
TEXTO = (22, 34, 64)
GRIS = (98, 110, 135)
LINEA = (226, 232, 242)
HEADER_TABLA = (239, 243, 250)


def generar(valor, tipo, cuotas, salida, nombre=None):
    lo, hi = LIMITES[tipo]
    if not (300_000 <= valor <= 1_500_000):
        raise ValueError("El monto debe estar entre $300.000 y $1.500.000")
    if not (lo <= cuotas <= hi):
        raise ValueError(f"Para pago {tipo} las cuotas van de {lo} a {hi}")

    filas = plan(valor, tipo, cuotas)
    total_int = sum(r[2] for r in filas)
    total_pagar = sum(r[4] for r in filas)
    cuota = filas[0][4]

    W = 1080
    PAD = 60
    row_h = 66
    table_top = 700
    H = table_top + 80 + row_h * cuotas + 280

    img = Image.new("RGB", (W, H), AZUL_1)
    d = ImageDraw.Draw(img)

    # degradado de fondo
    for y in range(H):
        t = y / H
        col = tuple(int(AZUL_2[j] * (1 - t) + AZUL_1[j] * t) for j in range(3))
        d.line([(0, y), (W, y)], fill=col)

    # Encabezado
    d.text((PAD, 50), "credinamic", font=ImageFont.truetype(POPPINS, 40), fill=BLANCO)
    d.text((PAD, 98), "Crédito de libranza 100% digital", font=f("Inter-Regular.otf", 24), fill=(200, 215, 240))
    titulo_y = 170
    tf = ImageFont.truetype(POPPINS, 64)
    d.text((PAD, titulo_y), "Tu plan de ", font=tf, fill=BLANCO)
    w = d.textlength("Tu plan de ", font=tf)
    d.text((PAD + w, titulo_y), "pagos", font=tf, fill=CELESTE)
    sub = f"Hola {nombre}, este es el detalle de tu crédito." if nombre else "Este es el detalle de tu crédito, cuota por cuota."
    d.text((PAD, 258), sub, font=f("Inter-Regular.otf", 28), fill=(220, 230, 248))

    # Tarjetas resumen (2x2)
    frecuencia = "quincenal" if tipo == "quincenales" else "mensual"
    cards = [
        ("CRÉDITO SOLICITADO", cop(valor), False),
        (f"CUOTA {frecuencia.upper()}", cop(cuota), False),
        ("TOTAL INTERESES", cop(total_int), False),
        ("TOTAL A PAGAR", cop(total_pagar), True),
    ]
    cw = (W - 2 * PAD - 24) // 2
    ch = 130
    for idx, (lab, val, dest) in enumerate(cards):
        x = PAD + (idx % 2) * (cw + 24)
        y = 320 + (idx // 2) * (ch + 20)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=26,
                            fill=CELESTE if dest else CARD,
                            outline=None if dest else (110, 140, 200), width=2)
        d.text((x + 30, y + 26), lab, font=f("Inter-SemiBold.otf", 20),
               fill=TEXTO if dest else (210, 222, 245))
        d.text((x + 30, y + 58), val, font=ImageFont.truetype(POPPINS, 44),
               fill=TEXTO if dest else BLANCO)

    # Etiqueta de condiciones
    cond = f"{cuotas} cuotas {'quincenales' if tipo == 'quincenales' else 'mensuales'}"
    d.text((PAD, table_top - 56), cond, font=f("Inter-SemiBold.otf", 26), fill=BLANCO)

    # Tabla
    tx0, tx1 = PAD, W - PAD
    ty1 = table_top + 70 + row_h * cuotas
    d.rounded_rectangle([tx0, table_top, tx1, ty1 + 10], radius=28, fill=BLANCO)
    d.rounded_rectangle([tx0, table_top, tx1, table_top + 70], radius=28, fill=HEADER_TABLA)
    d.rectangle([tx0, table_top + 40, tx1, table_top + 70], fill=HEADER_TABLA)

    cols = [tx0 + 30, tx0 + 330, tx0 + 530, tx0 + 760, tx1 - 30]  # x de referencia
    heads = ["CUOTA", "CAPITAL", "INTERÉS", "SALDO", "VALOR"]
    hf = f("Inter-SemiBold.otf", 19)
    for j, h in enumerate(heads):
        if j == 0:
            d.text((cols[0], table_top + 24), h, font=hf, fill=GRIS)
        else:
            d.text((cols[j] - d.textlength(h, font=hf), table_top + 24), h, font=hf, fill=GRIS)

    rf = f("Inter-Regular.otf", 25)
    rb = f("Inter-Bold.otf", 25)
    for k, (i, ac, ai, sc, vc) in enumerate(filas):
        y = table_top + 70 + k * row_h
        if k:
            d.line([(tx0 + 20, y), (tx1 - 20, y)], fill=LINEA, width=2)
        yy = y + 19
        d.text((cols[0], yy), f"#{i:02d}", font=rb, fill=AZUL_2)
        for j, v in enumerate([ac, ai, sc, vc], start=1):
            s = cop(v)
            font = rb if j == 4 else rf
            d.text((cols[j] - d.textlength(s, font=font), yy), s, font=font, fill=TEXTO)

    # Pie
    py = ty1 + 50
    nota = [
        "Valores aproximados. Pueden aplicar cobros adicionales según tu perfil.",
        "Crédito sujeto a estudio y aprobación. Incluye seguro de vida.",
    ]
    for n, line in enumerate(nota):
        d.text((PAD, py + n * 38), line, font=f("Inter-Regular.otf", 23), fill=(205, 218, 242))
    bx0, by0 = PAD, py + 100
    d.rounded_rectangle([bx0, by0, W - PAD, by0 + 86], radius=43, fill=CELESTE)
    cta = "Responde SÍ para continuar con tu solicitud"
    cf = f("Inter-Bold.otf", 30)
    d.text(((W - d.textlength(cta, font=cf)) / 2, by0 + 24), cta, font=cf, fill=TEXTO)

    if hasattr(salida, "write"):
        img.save(salida, format="PNG", optimize=True)
    else:
        img.save(salida, optimize=True)
    return {"cuota": cuota, "intereses": total_int, "total": total_pagar}
