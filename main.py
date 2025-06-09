from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List
import datetime
import time
import threading

# Inicializar Firebase
cred = credentials.Certificate('clave-firebase.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Umbral de sobrecarga (en porcentaje)
SOBRECARGA_CPU = 80
SOBRECARGA_RAM = 80

def calcular_puntuacion_nodo(nodo: Dict) -> float:
    """
    Calcula una puntuación para el nodo basada en su carga actual.
    Menor puntuación significa mejor candidato para asignación.
    """
    cpu_weight = 0.7  # Peso para CPU
    ram_weight = 0.3  # Peso para RAM
    
    # Normalizar valores entre 0 y 1
    cpu_score = nodo['cpu'] / 100
    ram_score = nodo['ram'] / 100
    
    # Calcular puntuación ponderada
    return (cpu_score * cpu_weight) + (ram_score * ram_weight)

def seleccionar_mejor_nodo(nodos: List[Dict]) -> Dict:
    return min(nodos, key=calcular_puntuacion_nodo)

def nodo_sobrecargado(nodo: Dict) -> bool:
    """
    Verifica si un nodo está sobrecargado basado en CPU y RAM
    """
    return nodo['cpu'] > SOBRECARGA_CPU or nodo['ram'] > SOBRECARGA_RAM

def reasignar_tareas(nodo_sobrecargado: Dict):
    """
    Reasigna las tareas cuando un nodo específico está sobrecargado
    """
    try:
        # Obtener todos los nodos
        nodos_ref = db.collection('nodos')
        nodos = [doc.to_dict() for doc in nodos_ref.stream()]
        
        if len(nodos) < 2:
            print("Se necesitan al menos 2 nodos para realizar las asignaciones")
            return
        
        # Encontrar el nodo menos cargado (excluyendo el nodo sobrecargado)
        nodos_disponibles = [n for n in nodos if n['nombre'] != nodo_sobrecargado['nombre']]
        if not nodos_disponibles:
            return
            
        nodo_menos_cargado = min(nodos_disponibles, key=calcular_puntuacion_nodo)
        
        # Actualizar todas las asignaciones al nodo menos cargado
        asignaciones_ref = db.collection('asignaciones')
        asignaciones = asignaciones_ref.stream()
        
        for asignacion in asignaciones:
            asignaciones_ref.document(asignacion.id).update({
                'nodo': nodo_menos_cargado['nombre'],
                'fecha_actualizacion': datetime.datetime.now()
            })
        
        print(f"Tareas reasignadas al nodo {nodo_menos_cargado['nombre']} debido a sobrecarga del nodo {nodo_sobrecargado['nombre']}")
    except Exception as e:
        print(f"Error en reasignación de tareas: {str(e)}")

def monitoreo_por_eventos():
    """
    Función que monitorea los cambios en los nodos usando eventos
    """
    def on_nodo_change(doc_snapshot, changes, read_time):
        for change in changes:
            if change.type.name == 'MODIFIED':
                nodo = change.document.to_dict()
                if nodo_sobrecargado(nodo):
                    print(f"Nodo {nodo['nombre']} sobrecargado - CPU: {nodo['cpu']}%, RAM: {nodo['ram']}%")
                    reasignar_tareas(nodo)

    # Suscribirse a cambios en la colección de nodos
    nodos_ref = db.collection('nodos')
    nodos_ref.on_snapshot(on_nodo_change)

def asignar_tareas():
    # Obtener todos los nodos
    nodos_ref = db.collection('nodos')
    nodos = [doc.to_dict() for doc in nodos_ref.stream()]
    
    if len(nodos) < 2:
        print("Se necesitan al menos 2 nodos para realizar las asignaciones")
        return
    
    # Ordenar nodos por puntuación
    nodos_ordenados = sorted(nodos, key=calcular_puntuacion_nodo)
    
    # Seleccionar los dos mejores nodos
    mejor_nodo = nodos_ordenados[0]
    segundo_mejor_nodo = nodos_ordenados[1]
    
    # Crear o actualizar la colección de asignaciones
    asignaciones_ref = db.collection('asignaciones')
    
    # Asignar tarea de Comida al mejor nodo
    asignaciones_ref.add({
        'nodo': mejor_nodo['nombre'],
        'tarea': 'Comida',
        'fecha_asignacion': datetime.datetime.now()
    })
    
    # Asignar tarea de Obstáculo al segundo mejor nodo
    asignaciones_ref.add({
        'nodo': segundo_mejor_nodo['nombre'],
        'tarea': 'Obstáculo',
        'fecha_asignacion': datetime.datetime.now()
    })

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('inicio.html')

@app.route('/juego')
def juego():
    return render_template('game.html')

@app.route('/asignar')
def asignar():
    asignar_tareas()
    return "Tareas asignadas correctamente"

@app.route('/iniciar-monitoreo')
def iniciar_monitoreo():
    # Iniciar el monitoreo basado en eventos
    thread = threading.Thread(target=monitoreo_por_eventos, daemon=True)
    thread.start()
    return "Monitoreo por eventos iniciado correctamente"

if __name__ == '__main__':
    # Iniciar el monitoreo al arrancar la aplicación
    thread = threading.Thread(target=monitoreo_por_eventos, daemon=True)
    thread.start()
    app.run(debug=True) 