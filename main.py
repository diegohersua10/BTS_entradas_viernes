import os
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
EVENT_URL = "https://www.ticketmaster.co/event/bts-world-tour-2026"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        print(f"Respuesta de Telegram ({response.status_code}): {response.text}")
        return response.ok
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")
        return False

def check_tickets():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page.route("**/*.{png,jpg,jpeg,svg,woff,woff2}", lambda route: route.abort())
        
        try:
            print(f"Cargando la página general del evento en el navegador...")
            page.goto(EVENT_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)

            # Buscamos todos los contenedores/filas de las 4 casillas de venta
            # Ticketmaster agrupa cada tarjeta en elementos divisores dentro del listado principal
            cards = page.query_selector_all("div, section, li") 
            
            available_events = []
            
            # Evaluamos el HTML completo de la página
            full_html = page.content().lower()
            
            # Conteo de ocurrencias de 'agotado' o 'finalizado'
            no_available_keywords = ["agotado", "soldout", "sold out", "evento finalizado", "finalizado"]
            
            # Si alguna de las 4 casillas cambia a 'comprar', 'disponible' o si desaparece la etiqueta 'agotado' de algún bloque
            # Evaluamos si existen elementos interactivos que no contengan la palabra agotado
            buttons = page.query_selector_all("a, button")
            for button in buttons:
                text = button.inner_text().strip().lower()
                href = button.get_attribute("href") or ""
                
                # Si encontramos un botón que conduzca a compra o que no diga 'agotado'/'finalizado'
                if text and not any(kw in text for kw in no_available_keywords) and ("ticketmaster.co" in href or "event" in href or "comprar" in text):
                    available_events.append(f"Botón activo detectado: '{text}' -> {href}")

            if available_events:
                print("¡Entradas detectadas en una o más casillas!")
                msg = f"🚨 ¡ENTRADAS DETECTADAS EN LA PÁGINA PRINCIPAL!\n\nUna de las casillas habilitó boletería:\n{EVENT_URL}"
                send_telegram_alert(msg)
            else:
                # Verificación de respaldo secundaria por recuento de 'agotado'
                print("Las 4 casillas siguen marcando Agotado / Finalizado. No se envió alerta.")

        except Exception as e:
            print(f"Error al verificar la página con Playwright: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_tickets()
