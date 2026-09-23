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

        # No bloqueamos recursos estáticos para asegurar que el JS y los componentes carguen completos
        try:
            print(f"Cargando la página general del evento en el navegador...")
            page.goto(EVENT_URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)

            # Buscamos los elementos interactivos o botones dentro del contenedor del evento
            buttons = page.query_selector_all("button, a.btn, a[class*='btn'], div[role='button']")
            
            available_option_found = False
            found_details = ""

            for btn in buttons:
                text = btn.inner_text().strip().lower()
                
                # Ignoramos botones del menú superior o footer
                if not text or any(ignored in text for ignored in ["soporte", "ingresar", "registrarse", "términos", "t&c"]):
                    continue
                
                # Palabras que indican que la casilla sigue cerrada
                is_disabled_status = any(kw in text for kw in ["agotado", "finalizado", "sold out", "soldout"])
                
                # Si encontramos un botón de acción en las tarjetas que NO diga agotado/finalizado
                # O si aparece un botón explícito de "comprar" / "seleccionar"
                if any(buy_kw in text for buy_kw in ["comprar", "seleccionar", "disponible", "entradas"]) or (not is_disabled_status and "ver" in text):
                    available_option_found = True
                    found_details = text
                    break

            if available_option_found:
                print(f"¡Oportunidad detectada!: {found_details}")
                msg = f"🚨 ¡ENTRADAS DETECTADAS EN LA PÁGINA PRINCIPAL!\n\nUna de las casillas habilitó boletería ({found_details}):\n{EVENT_URL}"
                send_telegram_alert(msg)
            else:
                print("Todas las casillas leídas siguen en estado 'Agotado' / 'Finalizado'. No se envió alerta.")

        except Exception as e:
            print(f"Error al verificar la página con Playwright: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_tickets()
