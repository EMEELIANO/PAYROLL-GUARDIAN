from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os, json, httpx
from pathlib import Path

app = FastAPI(title="Payroll Guardian API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_URL     = "https://api.anthropic.com/v1/messages"
ANTHROPIC_HEADERS = {
    "x-api-key":           ANTHROPIC_API_KEY,
    "anthropic-version":   "2023-06-01",
    "content-type":        "application/json",
}

# ── Cargar base de conocimiento ───────────────────────────────────────────────
def load_conocimiento():
    path = Path(__file__).parent / "conocimiento.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}

conocimiento = load_conocimiento()
print(f"✅ Base de conocimiento cargada: "
      f"{len(conocimiento.get('LCT_MAP_CCT', {}))} conceptos LCT, "
      f"{len(conocimiento.get('CONCEPTO_MAP', {}))} conceptos SAP, "
      f"{len(conocimiento.get('CECO_CCT_MAP', {}))} CECOs")

# ── Helper Anthropic ──────────────────────────────────────────────────────────
async def call_anthropic(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            ANTHROPIC_URL,
            headers={**ANTHROPIC_HEADERS, "x-api-key": ANTHROPIC_API_KEY},
            json=payload,
        )
    return resp.status_code, resp.json()

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "Payroll Guardian API",
        "version": "2.0",
        "conocimiento": {
            "lct_conceptos":  len(conocimiento.get("LCT_MAP_CCT", {})),
            "sap_conceptos":  len(conocimiento.get("CONCEPTO_MAP", {})),
            "cecos":          len(conocimiento.get("CECO_CCT_MAP", {})),
        }
    }

@app.get("/conocimiento")
def get_conocimiento():
    """El HTML carga la base de conocimiento desde acá al iniciar."""
    return conocimiento

@app.post("/chat")
async def chat(request: Request):
    """Chat con contexto del recibo."""
    try:
        body = await request.json()
        payload = {
            "model":      "claude-sonnet-4-5",
            "max_tokens": body.get("max_tokens", 800),
            "messages":   body.get("messages", []),
        }
        if body.get("system"):
            payload["system"] = body["system"]

        status, data = await call_anthropic(payload)
        if status != 200:
            return JSONResponse(status_code=status, content={"error": data})
        return data

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/analyze")
async def analyze(request: Request):
    """Resumen IA del recibo."""
    try:
        body = await request.json()
        payload = {
            "model":      "claude-sonnet-4-5",
            "max_tokens": 500,
            "messages":   [{"role": "user", "content": body.get("prompt", "")}],
        }
        status, data = await call_anthropic(payload)
        if status != 200:
            return JSONResponse(status_code=status, content={"error": data})
        return {"text": data.get("content", [{}])[0].get("text", "")}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
