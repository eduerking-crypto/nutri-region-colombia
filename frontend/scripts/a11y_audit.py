"""Auditoria de accesibilidad (chequeos DOM basicos WCAG) con Playwright."""
import time

from playwright.sync_api import sync_playwright

BASE = "http://localhost:3000"
CHROME = r"C:\Users\reyes\AppData\Local\ms-playwright\chromium-1243\chrome-win64\chrome.exe"

CHECK_JS = """
() => {
  const issues = [];
  // 1. Un solo h1
  const h1s = document.querySelectorAll('h1');
  if (h1s.length === 0) issues.push('Sin h1');
  if (h1s.length > 1) issues.push('Mas de un h1 (' + h1s.length + ')');
  // 2. Botones/enlaces sin nombre accesible
  const sinNombre = [...document.querySelectorAll('button, a[role="button"]')]
    .filter(el => !el.textContent.trim() && !el.getAttribute('aria-label'));
  if (sinNombre.length) issues.push(sinNombre.length + ' botones sin nombre accesible');
  // 3. Inputs sin label asociado (label[for], label envolvente o aria)
  const inputs = [...document.querySelectorAll('input:not([type="checkbox"]):not([type="hidden"])')];
  const sinLabel = inputs.filter(el => {
    if (el.getAttribute('aria-label') || el.getAttribute('aria-labelledby')) return false;
    if (el.closest('label')) return false;
    const id = el.id;
    return !id || !document.querySelector(`label[for="${id}"]`);
  });
  if (sinLabel.length) issues.push(sinLabel.length + ' inputs sin label');
  // 4. Imagenes sin alt
  const sinAlt = [...document.querySelectorAll('img')].filter(img => !img.hasAttribute('alt'));
  if (sinAlt.length) issues.push(sinAlt.length + ' imagenes sin alt');
  // 5. lang correcto
  if (!document.documentElement.lang || !document.documentElement.lang.startsWith('es'))
    issues.push('lang no es es: ' + document.documentElement.lang);
  // 6. Skip link presente
  if (!document.querySelector('a[href="#contenido"]')) issues.push('Sin skip link');
  return issues;
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    page = browser.new_context(viewport={"width": 1280, "height": 800}).new_page()
    resultados = {}
    for ruta in ["/", "/alimentos", "/alimentos/FDC-169985", "/ingresar", "/registro", "/evidencia", "/recetas", "/planificador", "/presupuesto", "/seguimiento", "/profesional", "/admin"]:
        page.goto(f"{BASE}{ruta}", wait_until="networkidle")
        time.sleep(1.2)
        issues = page.evaluate(CHECK_JS)
        # 7. navegacion por teclado: el foco sigue el orden del DOM (tabIndex positivo = problema)
        tabindex_positivos = page.evaluate(
            "() => [...document.querySelectorAll('[tabindex]')].filter(el => Number(el.tabIndex) > 0).length"
        )
        if tabindex_positivos:
            issues.append(f"{tabindex_positivos} elementos con tabindex > 0")
        resultados[ruta] = issues if issues else "OK"

    for ruta, resultado in resultados.items():
        print(f"{ruta}: {resultado}")
    browser.close()
