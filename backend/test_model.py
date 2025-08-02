"""Script para probar la función gpt_without_functions."""
import sys
import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Añadir el directorio src al path para poder importar los módulos
sys.path.append(str(Path(__file__).parent / 'src'))

from src.utils.model import gpt_without_functions
from langchain_core.messages import SystemMessage, HumanMessage

def main():
    print("🚀 Iniciando prueba de gpt_without_functions")
    print("-" * 60)
    
    # Mensaje del sistema
    system_message = SystemMessage(content="Eres un asistente útil que responde de manera concisa.")
    
    # Mensaje del usuario
    user_message = HumanMessage(content="Hola, ¿cómo estás?")
    
    # Llamar a la función
    response = gpt_without_functions(
        messages=[system_message, user_message],
        model="gpt-3.5-turbo",  # Usando 3.5 para pruebas rápidas
        temperature=0.7,
        max_tokens=100
    )
    
    print("\n" + "=" * 60)
    print("📋 RESULTADO FINAL")
    print("=" * 60)
    
    if response["success"]:
        print(f"✅ Éxito!")
        print(f"📝 Respuesta: {response['content']}")
        print(f"🤖 Modelo: {response['model']}")
        print(f"🪙 Tokens usados: {response['tokens_used']['total_tokens']}")
    else:
        print(f"❌ Error: {response['error']}")

if __name__ == "__main__":
    main()
