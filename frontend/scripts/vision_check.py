"""Analisis visual directo con Ollama (qwen3-vl) sin truncamiento de num_predict."""
import base64
import json
import sys
import time

import httpx

OLLAMA = "http://localhost:11434"
PROMPT = (
    "Evalua esta captura de una plataforma web de nutricion cientifica colombiana. "
    "Responde en espanol, maximo 120 palabras, con este formato: "
    "CALIDAD: <1-10>; PROBLEMAS: <lista concreta de problemas visuales: desbordes, "
    "alineaciones, contraste, jerarquia, elementos rotos; escribe 'ninguno evidente' si no hay>; "
    "IMPRESION: <premium o generica, y por que>."
)


def analizar(image_path: str, prompt: str = PROMPT) -> str:
    with open(image_path, "rb") as handle:
        image_b64 = base64.b64encode(handle.read()).decode("utf-8")
    payload = {
        "model": "qwen3-vl:8b",
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [image_b64],
            }
        ],
        "stream": False,
        "think": False,
        "options": {"num_predict": 250, "temperature": 0.3},
    }
    start = time.time()
    response = httpx.post(f"{OLLAMA}/api/chat", json=payload, timeout=600.0)
    response.raise_for_status()
    message = response.json().get("message", {})
    content = message.get("content", "")
    if not content.strip():
        # qwen3-vl enruta la respuesta al campo thinking en esta version de ollama
        thinking = message.get("thinking") or ""
        thinking = thinking.replace("", "").strip()
        # conservar la parte final (conclusiones) y las menciones clave
        if len(thinking) > 900:
            thinking = "…" + thinking[-900:]
        content = thinking if thinking else "(sin respuesta del modelo)"
    elapsed = round(time.time() - start, 1)
    return f"[{elapsed}s] {content}"


if __name__ == "__main__":
    image = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else PROMPT
    print(json.dumps({"image": image, "analisis": analizar(image, prompt)}, ensure_ascii=False, indent=2))
