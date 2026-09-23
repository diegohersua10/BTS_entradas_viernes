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

            content = page.content().lower()

            # Cuenta cuántas veces aparecen las palabras de no disponibilidad en la página
            no_available_keywords = ["agotado", "soldout", "sold out", "evento finalizado", "finalizado"]
            
            # Buscamos botones o enlaces que digan explícitamente "comprar", "seleccionar" o "entradas"
            buy_words = ["comprar", "buy", "seleccionar", "entradas disponibles"]
            has_buy_button = any(word in content for word in buy_words)

            # Contamos cuántas veces aparece "agotado/finalizado"
            unavailable_count = sum(content.count(kw) for kw in ["agotado", "finalizado"])

            # Si hay botones de compra explícitos O si el conteo de 'agotado/finalizado' baja de 4
            if has_buy_button or unavailable_count < 4:
                print(f"¡Cambio detectado! Palabras 'agotado/finalizado' encontradas: {unavailable_count}")
                msg = f"🚨 ¡ENTRADAS DETECTADAS EN LA PÁGINA PRINCIPAL!\n\nUna de las casillas cambió de estado:\n{EVENT_URL}"
                send_telegram_alert(msg)
            else:
                print(f"Las 4 casillas siguen agotadas/finalizadas (coincidencias encontradas: {unavailable_count}). No se envió alerta.")

        except Exception as e:
            print(f"Error al verificar la página con Playwright: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_tickets()
