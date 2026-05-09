from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import anthropic
import os
import json
from datetime import datetime

app = FastAPI(title="Payroll Guardian API")

# CORS — permite que el HTML de Netlify hable con este servidor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente Anthropic — la key viene de una variable de entorno (segura, no visible)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.get("/")
def health():
    return {"status": "ok", "service": "Payroll Guardian API", "version": "1.0"}

@app.post("/chat")
async def chat(request: Request):
    """Recibe el contexto del recibo + pregunta del usuario y devuelve respuesta de Claude."""
    try:
        body = await request.json()
        system_prompt = body.get("system", "")
        messages      = body.get("messages", [])
        max_tokens    = body.get("max_tokens", 800)

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
        )

        return {
            "content": [{"text": response.content[0].text}],
            "usage": {
                "input_tokens":  response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/analyze")
async def analyze(request: Request):
    """Recibe datos del recibo y genera el resumen IA."""
    try:
        body   = await request.json()
        prompt = body.get("prompt", "")

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        return {"text": response.content[0].text}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

