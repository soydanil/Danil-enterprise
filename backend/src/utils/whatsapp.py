# app/whatsapp_utils.py
from twilio.rest import Client
import os
from src.utils.loggers import logger

from dotenv import load_dotenv
import os
from pathlib import Path

# Cargar variables de entorno desde la raíz del proyecto
env_path = Path(__file__).parent.parent.parent.parent / '.env'
logger.info(f"Cargando .env desde: {env_path}")

# Intentar cargar el archivo .env
try:
    load_dotenv(env_path)
    logger.info("Archivo .env cargado exitosamente")
except Exception as e:
    logger.error(f"Error cargando .env: {str(e)}")
    raise ValueError(f"Error cargando .env: {str(e)}")

# Verificar que las variables de entorno existen
required_env_vars = [
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_WHATSAPP_NUMBER"
]

# Verificar cada variable y levantar error si falta
for var in required_env_vars:
    value = os.getenv(var)
    logger.info(f"{var}: {'***' if value else 'None'}")
    if not value:
        logger.error(f"Variable de entorno {var} no está configurada")
        raise ValueError(f"Variable de entorno {var} no está configurada")

# Cargar variables de entorno
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# Validar formato del número de WhatsApp
if TWILIO_WHATSAPP_NUMBER and not (TWILIO_WHATSAPP_NUMBER.startswith('+1') or TWILIO_WHATSAPP_NUMBER.startswith('+52')):
    logger.error(f"Formato incorrecto en TWILIO_WHATSAPP_NUMBER: {TWILIO_WHATSAPP_NUMBER}")
    raise ValueError("El número de Twilio para WhatsApp debe comenzar con +1 o +52")

def respond(to_number, message: str = "", media_url: str = None) -> None:
    """Función para enviar un mensaje por WhatsApp utilizando Twilio"""
    logger.info(f"Intentando enviar mensaje a (antes de limpieza): {to_number}")
    
    # Verificar que las credenciales de Twilio existan
    if not TWILIO_ACCOUNT_SID:
        logger.error("TWILIO_ACCOUNT_SID no está configurado")
        raise ValueError("TWILIO_ACCOUNT_SID no está configurado")
    if not TWILIO_AUTH_TOKEN:
        logger.error("TWILIO_AUTH_TOKEN no está configurado")
        raise ValueError("TWILIO_AUTH_TOKEN no está configurado")
    if not TWILIO_WHATSAPP_NUMBER:
        logger.error("TWILIO_WHATSAPP_NUMBER no está configurado")
        raise ValueError("TWILIO_WHATSAPP_NUMBER no está configurado")
    
    try:
        # Limpiar y formatear el número destino
        to_number = to_number.replace("whatsapp:", "").lstrip("+")
        to_number = "".join(to_number.split())
        if not to_number.startswith("52"):
            to_number = f"52{to_number}"
        formatted_to_number = f"whatsapp:+{to_number}"
        logger.info(f"Número destino formateado: {formatted_to_number}")

        # Formatear el número de Twilio
        TWILIO_WHATSAPP_PHONE_NUMBER = f"whatsapp:{TWILIO_WHATSAPP_NUMBER}"
        logger.info(f"Usando número Twilio: {TWILIO_WHATSAPP_PHONE_NUMBER}")
        
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message_data = {
            "from_": TWILIO_WHATSAPP_PHONE_NUMBER,
            "to": formatted_to_number
        }

        if media_url:
            message_data["media_url"] = [media_url]
        else:
            message_data["body"] = message

        logger.info(f"Datos del mensaje: {message_data}")
        
        twilio_client.messages.create(**message_data)
        logger.info(f"Mensaje enviado a {formatted_to_number}")
    except Exception as e:
        logger.error(f"Error enviando mensaje con Twilio: {str(e)}")
        raise Exception(f"No se pudo enviar el mensaje por WhatsApp: {str(e)}")
