"""Diagnostico: respuesta cruda de qwen3-vl."""
import base64
import json
import sys

import httpx

OLLAMA = "http://localhost:11434"
image_path = sys.argv[1]
with open(image_path, "rb") as handle:
    image_b64 = base64.b64encode(handle.read()).decode("utf-8")

payload = {
    "model": "qwen3-vl:8b",
    "messages": [
        {
            "role": "user",
            "content": (
                "Evalua esta captura de una web de nutricion. Responde en espanol, "
                "maximo 90 palabras: CALIDAD 1-10, PROBLEMAS concretos (o 'ninguno'), "
                "IMPRESION premium/generica. Ve directo al punto, sin razonamiento previo."
            ),
            "images": [image_b64],
        }
    ],
    "stream": False, "think": False,
    "options": {"num_predict": 220, "temperature": 0.2},
}
response = httpx.post(f"{OLLAMA}/api/chat", json=payload, timeout=600.0)
data = response.json()
message = data.get("message", {})
print(json.dumps(
    {
        "keys": list(message.keys()),
        "content_len": len(message.get("content", "")),
        "thinking_len": len(message.get("thinking", "") or ""),
        "thinking": (message.get("thinking") or "")[:1500], "content": message.get("content", "")[:400],
        "done_reason": data.get("done_reason"),
        "eval_count": data.get("eval_count"),
    },
    ensure_ascii=False,
    indent=2,
))
