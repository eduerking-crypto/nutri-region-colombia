"""Fetch reproducible de datos crudos desde USDA FoodData Central.

Lee data/imports/fdc/manifest.json y descarga cada búsqueda a
data/imports/fdc/raw/<slug>.json. Omite archivos ya descargados.
Reintenta con espera ante HTTP 429 (limite de la clave compartida DEMO_KEY).

Uso:
    python scripts/fetch_fdc.py [--key DEMO_KEY] [--reintentos 12] [--espera 120]

Variables de entorno alternativas: FDC_API_KEY.
Este script escribe SOLO datos crudos; la normalizacion vive en import_fdc.py.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import UTC, date, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "data" / "imports" / "fdc" / "manifest.json"
RAW_DIR = ROOT / "data" / "imports" / "fdc" / "raw"
LOG_PATH = ROOT / "data" / "imports" / "fdc" / "fetch_log.txt"


def log(message: str) -> None:
    stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    line = f"{stamp} {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def is_valid(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 5000:
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        return isinstance(payload.get("foods"), list) and len(payload["foods"]) > 0
    except (json.JSONDecodeError, OSError):
        return False


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))
    api_key = sys.argv[sys.argv.index("--key") + 1] if "--key" in sys.argv else None
    if api_key is None:
        import os

        api_key = os.environ.get("FDC_API_KEY", "DEMO_KEY")
    retries = int(sys.argv[sys.argv.index("--reintentos") + 1]) if "--reintentos" in sys.argv else 12
    wait = int(sys.argv[sys.argv.index("--espera") + 1]) if "--espera" in sys.argv else 120

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}"
    body_base = {"dataType": ["Foundation", "SR Legacy"], "pageSize": 3}

    log(f"=== inicio de ronda de descarga ({today}) ===")
    with httpx.Client(timeout=30.0) as client:
        for food in manifest["foods"]:
            slug = food["slug"]
            out = RAW_DIR / f"{slug}.json"
            if is_valid(out):
                log(f"SKIP {slug}: ya descargado")
                continue
            body = {**body_base, "query": food["query"]}
            for attempt in range(1, retries + 1):
                try:
                    response = client.post(url, json=body)
                except httpx.HTTPError as error:
                    log(f"ERROR red en {slug} (intento {attempt}): {error}")
                    time.sleep(wait)
                    continue
                if response.status_code == 200:
                    payload = response.json()
                    if payload.get("foods"):
                        out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
                        log(f"OK {slug}: {len(payload['foods'])} resultados -> raw/{slug}.json")
                        break
                    log(f"VACIO {slug}: sin resultados para '{food['query']}'")
                    break
                if response.status_code == 429:
                    log(f"429 {slug} (intento {attempt}/{retries}): limite de tasa, esperando {wait}s")
                    time.sleep(wait)
                    continue
                log(f"HTTP {response.status_code} en {slug}: {response.text[:120]}")
                break
            else:
                log(f"FALLO definitivo {slug}: reintentos agotados")
            time.sleep(3)
    log("=== fin de ronda de descarga ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
