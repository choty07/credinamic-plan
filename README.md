# Generador de plan de pagos — Credinamic

Crea la imagen del plan de pagos con la misma fórmula del simulador de credinamic.com.co
(quincenal 0,7% por periodo, mensual 1,65% por periodo, cuota fija).

## Enlaces

- Imagen PNG: `/api/plan?monto=1500000&tipo=quincenales&cuotas=14&nombre=Laura`
- Enlace para WhatsApp (muestra la imagen como vista previa): `/p?monto=1500000&tipo=quincenales&cuotas=14&nombre=Laura`

Parámetros:
- `monto`: entre 300000 y 1500000
- `tipo`: `quincenales` (6 a 14 cuotas) o `mensuales` (3 a 14 cuotas)
- `cuotas`: número de cuotas
- `nombre` (opcional): primer nombre del cliente

## Cambiar tasas, montos o textos

Todo está en `api/_core.py`: `TASAS`, `LIMITES` y la función `generar`.

## Publicar

Subir esta carpeta a un repositorio de GitHub e importarlo en Vercel (Framework: Other). No necesita configuración extra.
