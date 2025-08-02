import logging
from logging.handlers import RotatingFileHandler

# Configuración del logger
logger = logging.getLogger('logtest')
logger.setLevel(logging.DEBUG)  # Establecer el nivel global a DEBUG

# Formato del log
formatter = logging.Formatter(fmt='%(asctime)s pid/%(process)d [%(filename)s:%(lineno)d] %(message)s')

# File handler: Guardar logs en un archivo con rotación
file_handler = RotatingFileHandler('./logs/aws-log.log', maxBytes=1024 * 1024, backupCount=10)
file_handler.setLevel(logging.DEBUG)  # Nivel de logs en archivo
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console handler: Mostrar logs en la consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Nivel de logs en consola
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

