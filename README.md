# Payroll Guardian — Backend API

Backend para el agente de análisis de recibos de sueldo de Farmacity.

## Deploy en Render

1. Subir este repositorio a GitHub
2. Conectar con Render
3. Agregar variable de entorno: `ANTHROPIC_API_KEY`
4. Deploy automático

## Endpoints

- `GET /` — Health check
- `POST /chat` — Chat con contexto del recibo
- `POST /analyze` — Resumen IA del recibo
