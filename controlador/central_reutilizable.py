import os
import firebase_admin
from firebase_admin import credentials, firestore
import psutil
import time
from datetime import datetime
import socket

# Configuración de Firebase
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "config", "clave-firebase.json")

# Inicializar Firebase
credenciales = credentials.Certificate(CREDENTIALS_PATH)
firebase_admin.initialize_app(credenciales)
db = firestore.client()

# Nombre del nodo
nombre_nodo = socket.gethostname()

def obtener_datos():
    """
    Obtiene los datos del sistema
    """
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disco = psutil.disk_usage("/").percent
    red = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
    red = round(red / (1024 * 1024), 2)
    tiempo = datetime.now().isoformat()
    
    ip_local = socket.gethostbyname(socket.gethostname())
    
    return {
        "nombre": nombre_nodo,
        "ip": ip_local,
        "cpu": cpu,
        "ram": ram,
        "disco": disco,
        "red": red,
        "ultima_actualizacion": tiempo,
        "descripcion": "Nodo de procesamiento"
    }

def monitorear_carga(identificador: str, tipo: str, estado: str, datos_adicionales: dict = None):
    """
    Monitorea la carga de un proceso
    """
    datos = obtener_datos()
    datos.update({
        "identificador": identificador,
        "tipo": tipo,
        "estado": estado,
        "ultima_actualizacion": datetime.now().isoformat()
    })
    
    if datos_adicionales:
        datos.update(datos_adicionales)
    
    db.collection('monitoreo').document(identificador).set(datos)
    return datos

def balancear_carga():
    """
    Balancea la carga entre nodos
    """
    nodos = db.collection('nodos').get()
    return min(nodos, key=lambda x: x.get('cpu', 100)) 