#!/usr/bin/env python3
import time
import sys

def test_logs():
    print("\n" + "="*50)
    print("🔍 INICIANDO PRUEBA DE LOGS")
    print(f"Hora del sistema: {time.ctime()}")
    
    # Mensaje directo a stdout
    print("\n📝 MENSAJE DE PRUEBA (stdout)")
    
    # Mensaje a stderr
    print("\n❌ MENSAJE DE ERROR (stderr)", file=sys.stderr)
    
    # Forzar flush
    sys.stdout.flush()
    sys.stderr.flush()
    
    print("\n✅ PRUEBA COMPLETADA")
    print("="*50 + "\n")

if __name__ == "__main__":
    test_logs()
