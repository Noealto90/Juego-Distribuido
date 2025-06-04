import firebase_admin
from firebase_admin import credentials
import os

def initialize_firebase():
    """
    Inicializa la conexión con Firebase
    """
    try:
        # Intentar obtener la ruta del archivo de credenciales desde variables de entorno
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'clave-firebase.json')
        
        # Inicializar Firebase
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        
        return True
    except Exception as e:
        print(f"Error al inicializar Firebase: {str(e)}")
        return False 