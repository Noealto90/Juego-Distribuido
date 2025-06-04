import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración del servidor
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# Configuración del juego
GRID_SIZE = int(os.getenv('GRID_SIZE', 20))
GAME_SPEED = int(os.getenv('GAME_SPEED', 100))

# Configuración de WebSocket
WS_HOST = os.getenv('WS_HOST', 'localhost')
WS_PORT = int(os.getenv('WS_PORT', 5000))

# Configuración de Firebase
FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'clave-firebase.json') 