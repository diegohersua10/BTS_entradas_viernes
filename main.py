import os
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = "8751729052:AAHdAauzEW7qHHsPVrRHoyq5wtWhCfbjJ_I"
CHAT_ID = "-1004373332483"
EVENT_URL = "https://www.ticketmaster.co/event/bts-world-tour-venta-general-viernes-2-octubre"

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

        # Solo abortamos imágenes pesadas para no alterar la estructura del texto/clases
        page.route("**/*.{png,jpg,jpeg,svg,woff,woff2}", lambda route: route.abort())
        
        try:
            print("Cargando la página en el navegador...")
            page.goto(EVENT_URL, wait_until="domcontentloaded", timeout=30000)
            
            # Esperar 5 segundos para que los scripts rendericen el banner 'AGOTADO'
            page.wait_for_timeout(5000)
            
            content = page.content().lower()
            
            is_sold_out = "agotado" in content or "soldout" in content or "status-soldout" in content
            
            if not is_sold_out:
                print("¡Entradas detectadas! Intentando enviar alerta a Telegram...")
                sent = send_telegram_alert(f"🚨 ¡ENTRADAS DISPONIBLES! Corre a comprar: {EVENT_URL}")
                if sent:
                    print("¡Alerta enviada exitosamente a Telegram!")
            else:
                print("El evento sigue AGOTADO. No se envió alerta.")
                
        except Exception as e:
            print(f"Error al verificar la página con Playwright: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_tickets()
