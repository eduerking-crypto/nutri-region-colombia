"""Capturas viewport-only para analisis visual rapido."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://localhost:3000"
OUT = Path(r"C:\nutri-region-colombia\frontend\verificacion-visual")
CHROME = r"C:\Users\reyes\AppData\Local\ms-playwright\chromium-1243\chrome-win64\chrome.exe"

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    for ruta, nombre in [
        ("/", "v1_landing"),
        ("/alimentos", "v2_explorador"),
        ("/alimentos/FDC-169985", "v3_ficha"),
        ("/evidencia", "v4_evidencia"),
    ]:
        page.goto(f"{BASE}{ruta}", wait_until="networkidle")
        time.sleep(1.0)
        page.screenshot(path=str(OUT / f"{nombre}.png"))
        print(f"OK {nombre}")
    browser.close()
print("listo")
