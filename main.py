import os
import time
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

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

if __name__ == "__main__":
    print("Iniciando secuencia de mensajes...")

    # Mensaje 1: De parte del bot / recordatorio del evento
    mensaje_bot = (
        "🤖 [Recordatorio automático del sistema]\n"
        "¡Hace exactamente 1 mes fue el concierto! Esperamos que lo hayas disfrutado al máximo. 🎶✨"
    )
    
    success1 = send_telegram_alert(mensaje_bot)
    
    # Esperamos 3 segundos para que se vea natural en el chat de Telegram
    time.sleep(3)

    # Mensaje 2: Tu mensaje personalizado con la "prueba" de que se programó hace un mes
    mensaje_personalizado = (
        "💌 Mensaje personalizado (Programado el 28/09/2026):\n\n"
        "Anii! Hace 1 mes fue el concierto! ¿Puedes creerlooo? Yo aún no JAJA\n\n"
        "Hoy es 28 de sept, mañana liberan las entradas y tengo un presentimiento de que ambos la lograremos 🤩 pero si no, haré lo posible para que vayas el viernes, lo prometo, sé que irás cueste lo que cueste!!. Pero si no voy yo, quedo reee feliz sabiendo que irás tu, lit me alegraría tantooooo!!\n\n"
        "Ani, siempre te deseo lo mejor y soy tan feliz de saber que irás el sábado y que (con fé) también irás el viernes. Puede que no hablemos nunca más pero siempre seré feliz al verte feliz, te mereces siempre lo más lindo del mundo!\n\n"
        "No sé como estemos dentro de 1 mes, la verdad espero que bien jeje, pero nunca dudes lo mucho que te aprecio y deseo lo mejor. Y me pone feliz el ver cómo cumples tus sueños y metas, estemos en la página que estemos, siempre te estaré apoyando en silencio, lo prometooo\n\n"
        "Disfruta muuuucho el conciertooo! Vendrán más bendiciones para tu vidaaa\n\n"
        "Pd: Dios, espero que en un mes estemos nice, si no, cuando veas este mensaje me sentiré como un tonto JSJS si te moleste, perdón, no es mi intención :(. Pero pero, si estamos nice, sabes que un mensaje tuyo hablando del concierto o al menos saludando, me alegra todo el año y la vida jojooo\n\n"
        "Pd2: ¿Sonaron tus canciones sorpresas que queríassss? Cruzo dedos para que así sea 🤞🏽\n\n"
        "Pd3: Si en algún momento quieres contarle a alguien del concierto o de las otras fechas, sabes que estoy sho. Veré los otros shows que vienen JSJS (admito que a veces veía algunos jijii)"
    )
    
    success2 = send_telegram_alert(mensaje_personalizado)

    if success1 and success2:
        print("¡Ambos mensajes fueron enviados con éxito al grupo!")
    else:
        print("Hubo algún problema enviando los mensajes.")
