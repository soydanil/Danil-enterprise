import os
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
import logging
from dotenv import load_dotenv
from pathlib import Path
from src.utils.loggers import logger

# Configurar logger
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde la raíz del proyecto
env_path = Path(__file__).parent.parent.parent.parent / '.env'
logger.info(f"Cargando .env desde: {env_path}")

# Cargar el archivo .env manualmente
load_dotenv(env_path, override=True)

# Configuración de OpenAI
MODEL_NAME = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# Logging detallado
logger.info(f"Modelo configurado: {MODEL_NAME}")
logger.info(f"OPENAI_API_KEY configurada: {'Sí' if OPENAI_API_KEY else 'No'}")
if OPENAI_API_KEY:
    logger.info(f"Longitud de la API key: {len(OPENAI_API_KEY)} caracteres")
    logger.info(f"Prefijo de la API key: {OPENAI_API_KEY[:8]}...{OPENAI_API_KEY[-4:] if len(OPENAI_API_KEY) > 12 else ''}")
    
    # Verificar que la clave no tenga caracteres no deseados
    if '\n' in OPENAI_API_KEY or '\r' in OPENAI_API_KEY:
        logger.warning("¡La API key contiene saltos de línea! Limpiando...")
        OPENAI_API_KEY = OPENAI_API_KEY.strip()

# Verificar que la clave de API esté configurada
if not OPENAI_API_KEY:
    error_msg = "ERROR: OPENAI_API_KEY no está configurada en las variables de entorno"
    logger.error(error_msg)
    raise ValueError(error_msg)

# Inicializar el cliente de OpenAI
try:
    client = AsyncOpenAI(
        api_key=OPENAI_API_KEY,
        # Asegurarse de usar la URL base correcta
        base_url="https://api.openai.com/v1"
    )
    logger.info("Cliente de OpenAI inicializado correctamente")
except Exception as e:
    logger.error(f"Error al inicializar el cliente de OpenAI: {str(e)}")
    raise

async def gpt_without_functions(model: str = None, messages: List[Dict[str, str]] = None) -> str:
    """
    Función para interactuar con la API de OpenAI sin funciones.
    
    Args:
        model: Nombre del modelo a utilizar
        messages: Lista de mensajes en formato de chat
        
    Returns:
        str: Respuesta del modelo
    """
    try:
        if not messages:
            logger.warning("No se proporcionaron mensajes para el modelo")
            return "Lo siento, no recibí ningún mensaje para procesar."
            
        # Usar el modelo especificado o el predeterminado
        model_name = model or MODEL_NAME
        logger.info(f"Usando modelo: {model_name}")
        
        # Realizar la llamada a la API
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extraer la respuesta
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        
        logger.error("No se pudo extraer la respuesta del modelo")
        return "Lo siento, no pude generar una respuesta en este momento. Por favor, inténtalo de nuevo."
        
    except Exception as e:
        logger.error(f"Error en gpt_without_functions: {str(e)}", exc_info=True)
        return "Lo siento, estoy teniendo problemas para procesar tu solicitud. Por favor, inténtalo de nuevo más tarde."

async def summarise_conversation(history: List[Dict[str, str]]) -> str:
    """
    Resumir el historial de conversación en una sola frase.
    
    Args:
        history: Historial de la conversación
        
    Returns:
        str: Resumen de la conversación
    """
    try:
        if not history:
            return "No hay historial de conversación para resumir."
            
        # Tomar solo los últimos 10 mensajes para evitar exceder el límite de tokens
        recent_history = history[-10:]
        
        # Crear mensaje de sistema para el resumen
        system_message = {
            "role": "system",
            "content": "Eres un asistente útil que resume conversaciones. Proporciona un resumen conciso de la conversación."
        }
        
        # Crear mensaje de usuario con el historial
        user_message = {
            "role": "user",
            "content": f"Por favor, resume la siguiente conversación en una o dos frases: {recent_history}"
        }
        
        # Llamar al modelo para generar el resumen
        response = await gpt_without_functions(messages=[system_message, user_message])
        return response
        
    except Exception as e:
        logger.error(f"Error en summarise_conversation: {str(e)}")
        return "No se pudo generar un resumen de la conversación."
