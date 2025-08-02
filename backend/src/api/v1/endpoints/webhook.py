from fastapi import APIRouter, Request, HTTPException
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from src.db import get_supabase
from src.utils.loggers import logger
from src.utils.model import gpt_without_functions
from src.utils.whatsapp import respond as send_whatsapp_message

# Cargar variables de entorno
load_dotenv()

router = APIRouter()

def get_current_timestamp() -> str:
    """Obtiene la hora actual en la zona horaria de México (UTC-6 o UTC-5)."""
    # Obtener la hora UTC
    utc_now = datetime.now(timezone.utc)
    
    # Ajustar a la zona horaria de México (UTC-6)
    mexico_offset = timedelta(hours=-6)
    
    # Verificar si estamos en horario de verano (aproximado)
    # En México, el horario de verano es de abril a octubre
    if 4 <= utc_now.month <= 10:
        mexico_offset = timedelta(hours=-5)  # UTC-5 en horario de verano
    
    # Aplicar el desplazamiento
    mexico_time = utc_now + mexico_offset
    
    return mexico_time.isoformat()

async def get_conversation_history(phone_number: str) -> List[Dict[str, str]]:
    """
    Obtiene el historial de mensajes desde Supabase.
    """
    try:
        supabase = get_supabase()
        response = supabase.table('conversations') \
                        .select('messages') \
                        .eq('phone_number', phone_number) \
                        .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0].get('messages', [])
        return []
    except Exception as e:
        logger.error(f"Error al obtener historial de Supabase: {str(e)}")
        return []

async def save_conversation_history(phone_number: str, messages: List[Dict[str, str]]):
    """
    Guarda el historial de mensajes en Supabase.
    Si ya existe una conversación para el número, la actualiza.
    Si no existe, crea una nueva.
    """
    try:
        logger.info(f"🔧 INICIANDO GUARDADO DE MENSAJES PARA {phone_number}")
        logger.info(f"📝 Cantidad de mensajes a guardar: {len(messages)}")
        
        # Obtener el cliente de Supabase
        supabase = get_supabase()
        
        # Buscar si ya existe una conversación para este número
        existing = supabase.table('conversations') \
            .select('*') \
            .eq('phone_number', phone_number) \
            .execute()
            
        if existing.data:
            # Actualizar conversación existente
            logger.info(f"🔄 Actualizando conversación existente para {phone_number}")
            result = supabase.table('conversations') \
                .update({
                    'messages': messages,
                    'modified_at': 'now()'  # Usando la función now() de PostgreSQL
                }) \
                .eq('phone_number', phone_number) \
                .execute()
        else:
            # Crear nueva conversación
            logger.info(f"🆕 Creando nueva conversación para {phone_number}")
            result = supabase.table('conversations') \
                .insert({
                    'phone_number': phone_number,
                    'messages': messages,
                    'created_at': 'now()',
                    'modified_at': 'now()'
                }) \
                .execute()
                
        logger.info(f"✅ Mensajes guardados exitosamente para {phone_number}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error al guardar en Supabase: {str(e)}")
        raise

async def add_message_to_conversation(phone_number: str, role: str, message: str) -> List[Dict[str, str]]:
    """
    Agrega un nuevo mensaje a la conversación existente o crea una nueva si no existe.
    """
    try:
        messages = await get_conversation_history(phone_number)
        new_message = {
            "role": role,
            "content": message,
            "timestamp": get_current_timestamp()
        }
        messages.append(new_message)
        await save_conversation_history(phone_number, messages)
        return messages
    except Exception as e:
        logger.error(f"Error al agregar mensaje a la conversación: {str(e)}")
        raise

def normalize_phone_number(phone_number: str) -> str:
    """Normaliza el número de teléfono al formato internacional."""
    # Eliminar cualquier carácter que no sea dígito
    digits = ''.join(filter(str.isdigit, phone_number))
    
    # Si el número comienza con 0, reemplazar con el código de país
    if digits.startswith('0'):
        return '52' + digits[1:]
    # Si el número ya tiene código de país, devolverlo tal cual
    elif digits.startswith('52'):
        return digits
    # Si no tiene código de país ni empieza con 0, asumir que es un número mexicano
    else:
        return '52' + digits

# Cargar el system prompt desde el archivo
def load_system_prompt() -> str:
    try:
        # Construir la ruta al archivo system_prompt.txt
        base_dir = Path(__file__).parent.parent.parent.parent  # Subir hasta la raíz de src
        prompt_path = base_dir / "prompts" / "system_prompt.txt"
        
        # Leer el contenido del archivo
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Error al cargar el system prompt: {str(e)}")
        # Mensaje de respaldo en caso de error
        return "Eres Danil, un asistente virtual amigable y profesional que trabaja para Danil AI. Tu objetivo es ayudar a los usuarios con sus consultas de manera útil y profesional. Responde siempre en el mismo idioma que el mensaje del usuario."

# Obtener el system prompt
SYSTEM_PROMPT = {
    "role": "system",
    "content": load_system_prompt()
}

# Mensaje de bienvenida
WELCOME_MESSAGE = "¡Hola! Soy Danil, tu asistente virtual de Danil AI. ¿En qué puedo ayudarte hoy? 😊"

@router.post("/whatsapp-endpoint")
async def whatsapp_endpoint(request: Request):
    try:
        # Log de inicio de la solicitud
        logger.info("="*50)
        logger.info("🔔 NUEVA SOLICITUD RECIBIDA")
        logger.info(f"URL: {request.url}")
        logger.info(f"Método: {request.method}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Parsear los datos del formulario
        try:
            form_data = await request.form()
            logger.info(f"Datos del formulario: {dict(form_data)}")
            
            from_number = form_data.get('From', '')
            body = form_data.get('Body', '').strip()
            
            if not from_number:
                logger.error("❌ Error: Falta el campo 'From' en la solicitud")
                raise HTTPException(status_code=400, detail="Missing 'From' field")
                
            if not body:
                logger.error("❌ Error: Falta el campo 'Body' en la solicitud")
                raise HTTPException(status_code=400, detail="Missing 'Body' field")
                
        except Exception as e:
            logger.error(f"❌ Error al procesar los datos del formulario: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Error processing form data: {str(e)}")
        
        # Normalizar el número de teléfono
        try:
            normalized_number = normalize_phone_number(from_number)
            logger.info(f"📞 Número normalizado: {normalized_number}")
        except Exception as e:
            logger.error(f"❌ Error al normalizar el número de teléfono: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid phone number format")
        
        logger.info(f"💬 Mensaje recibido: {body}")
        
        # Obtener el historial de la conversación
        try:
            conversation_history = await get_conversation_history(normalized_number)
            logger.info(f"📚 Historial de conversación obtenido: {len(conversation_history)} mensajes")
        except Exception as e:
            logger.error(f"❌ Error al obtener el historial de la conversación: {str(e)}", exc_info=True)
            # Continuar con una lista vacía en caso de error
            conversation_history = []
        
        # Si es un nuevo usuario, enviar mensaje de bienvenida
        if not conversation_history:
            logger.info("👤 Nuevo usuario detectado, enviando mensaje de bienvenida")
            try:
                await add_message_to_conversation(
                    phone_number=normalized_number,
                    role="assistant",
                    message=WELCOME_MESSAGE
                )
                try:
                    send_whatsapp_message(
                        to_number=normalized_number,
                        message=WELCOME_MESSAGE
                    )
                    logger.info("✅ Mensaje de bienvenida enviado con éxito")
                except Exception as e:
                    logger.error(f"⚠️ No se pudo enviar el mensaje de WhatsApp: {str(e)}")
                    # Continuar aunque falle el envío del mensaje
                    
                return {
                    "status": "success", 
                    "message": "Welcome message processed",
                    "is_new_user": True
                }
            except Exception as e:
                logger.error(f"❌ Error al procesar nuevo usuario: {str(e)}", exc_info=True)
                # Continuar con el flujo normal en lugar de fallar
                pass
        
        # Agregar el mensaje del usuario a la conversación
        await add_message_to_conversation(
            phone_number=normalized_number,
            role="user",
            message=body
        )
        
        # Preparar mensajes para el modelo, comenzando con el system prompt
        messages_for_model = [SYSTEM_PROMPT]
        
        # Agregar el historial de la conversación (últimos 9 mensajes para no exceder el límite de tokens)
        for msg in conversation_history[-9:]:
            messages_for_model.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Obtener respuesta del modelo
        bot_response = await gpt_without_functions(
            model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
            messages=messages_for_model
        )
        
        # Agregar la respuesta del bot a la conversación
        await add_message_to_conversation(
            phone_number=normalized_number,
            role="assistant",
            message=bot_response
        )
        
        # Enviar respuesta por WhatsApp (llamada síncrona sin await)
        send_whatsapp_message(
            to_number=normalized_number,
            message=bot_response
        )
        
        return {"status": "success", "message": "Message processed successfully"}
        
    except HTTPException as he:
        # Re-lanzar las excepciones HTTP
        logger.error(f"❌ Error HTTP {he.status_code}: {he.detail}")
        raise he
    except Exception as e:
        # Capturar cualquier otra excepción
        logger.error(f"❌ Error inesperado en el webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        logger.info("🏁 FIN DE LA SOLICITUD")
        logger.info("="*50 + "\n")