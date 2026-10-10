"""Capturas de pantalla para verificacion visual de NutriRegion Colombia."""
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://localhost:3000"
OUT = Path(r"C:\nutri-region-colombia\frontend\verificacion-visual")
OUT.mkdir(exist_ok=True)
CHROME = r"C:\Users\reyes\AppData\Local\ms-playwright\chromium-1243\chrome-win64\chrome.exe"


def shoot(page, name: str, full: bool = True):
    path = OUT / f"{name}.png"
    page.screenshot(path=str(path), full_page=full)
    print(f"OK {path.name}")


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    context = browser.new_context(viewport={"width": 1360, "height": 900})
    page = context.new_page()

    # 1. Landing
    page.goto(BASE, wait_until="networkidle")
    time.sleep(1.2)
    shoot(page, "01_landing")

    # 2. Explorador de alimentos
    page.goto(f"{BASE}/alimentos", wait_until="networkidle")
    time.sleep(1.2)
    shoot(page, "02_explorador")

    # 3. Ficha de yuca (dato real FDC)
    page.goto(f"{BASE}/alimentos/FDC-169985", wait_until="networkidle")
    time.sleep(1.2)
    shoot(page, "03_ficha_yuca")

    # 4. Registro via API + token para flujo autenticado
    registro = page.request.post(
        f"{BASE}/api/auth/registro",
        data=json.dumps(
            {
                "email": f"verificacion-{int(time.time())}@example.com",
                "password": "clave-visual-123456",
                "accept_consent": True,
                "display_name": "Verificación",
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    token = registro.json()["access_token"]
    page.goto(f"{BASE}/ingresar")
    page.evaluate(f"window.localStorage.setItem('nutriregion_token', '{token}')")

    # 5. Panel
    page.goto(f"{BASE}/panel", wait_until="networkidle")
    time.sleep(1.2)
    shoot(page, "05_panel")

    # 6. Planificador con plan generado
    page.goto(f"{BASE}/planificador", wait_until="networkidle")
    time.sleep(1.0)
    page.get_by_role("button", name="Generar mi plan").click()
    page.wait_for_timeout(2500)
    shoot(page, "06_planificador")

    # 7. Evidencia
    page.goto(f"{BASE}/evidencia", wait_until="networkidle")
    time.sleep(1.2)
    shoot(page, "07_evidencia")

    # 8. Onboarding (paso 1)
    page.evaluate("window.localStorage.removeItem('nutriregion_token')")
    registro2 = page.request.post(
        f"{BASE}/api/auth/registro",
        data=json.dumps(
            {
                "email": f"onboarding-{int(time.time())}@example.com",
                "password": "clave-visual-123456",
                "accept_consent": True,
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    token2 = registro2.json()["access_token"]
    page.goto(f"{BASE}/ingresar")
    page.evaluate(f"window.localStorage.setItem('nutriregion_token', '{token2}')")
    page.goto(f"{BASE}/onboarding", wait_until="networkidle")
    time.sleep(1.0)
    shoot(page, "08_onboarding")

    browser.close()

print("Capturas completadas en", OUT)
