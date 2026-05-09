from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import httpx

app = FastAPI(title="Payroll Guardian API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

@app.get("/")
def health():
    return {"status": "ok", "service": "Payroll Guardian API", "version": "1.1"}

@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        payload = {
            "model": "claude-sonnet-4-5",
            "max_tokens": body.get("max_tokens", 800),
            "messages": body.get("messages", []),
        }
        if body.get("system"):
            payload["system"] = body["system"]

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                ANTHROPIC_URL,
                headers={**ANTHROPIC_HEADERS, "x-api-key": ANTHROPIC_API_KEY},
                json=payload,
            )
        data = resp.json()
        if resp.status_code != 200:
            return JSONResponse(status_code=resp.status_code, content={"error": data})
        return data

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/analyze")
async def analyze(request: Request):
    try:
        body = await request.json()
        payload = {
            "model": "claude-sonnet-4-5",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": body.get("prompt", "")}],
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                ANTHROPIC_URL,
                headers={**ANTHROPIC_HEADERS, "x-api-key": ANTHROPIC_API_KEY},
                json=payload,
            )
        data = resp.json()
        if resp.status_code != 200:
            return JSONResponse(status_code=resp.status_code, content={"error": data})
        return {"text": data.get("content", [{}])[0].get("text", "")}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
