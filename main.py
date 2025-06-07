from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List
import datetime

# Inicializar Firebase
cred = credentials.Certificate('clave-firebase.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

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

if __name__ == '__main__':
    app.run(debug=True) 