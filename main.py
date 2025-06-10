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
SOBRECARGA_RAM = 100

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

def contar_tareas_por_nodo() -> Dict[str, int]:
    """
    Cuenta cuántas tareas tiene asignadas cada nodo.
    """
    asignaciones = db.collection('asignaciones').stream()
    conteo = {}
    for asignacion in asignaciones:
        data = asignacion.to_dict()
        nodo = data.get('nodo')
        if nodo:
            conteo[nodo] = conteo.get(nodo, 0) + 1
    return conteo

def reasignar_tareas(nodo_actual: Dict):
    try:
        nodos_ref = db.collection('nodos')
        nodos = [doc.to_dict() for doc in nodos_ref.stream()]
        
        if len(nodos) < 2:
            print("Se necesitan al menos 2 nodos para realizar reasignaciones.")
            return

        conteo_tareas = contar_tareas_por_nodo()

        print("📊 Tareas por nodo al momento de reasignar:")
        for nodo in nodos:
            print(f" - {nodo['nombre']}: {conteo_tareas.get(nodo['nombre'], 0)} tarea(s)")

        # Primero, buscar nodos que no tienen tareas y no están sobrecargados
        nodos_sin_tareas = [
            n for n in nodos
            if n['nombre'] != nodo_actual['nombre']
            and not nodo_sobrecargado(n)
            and conteo_tareas.get(n['nombre'], 0) == 0
        ]

        # Si no hay nodos sin tareas, buscar nodos no sobrecargados
        if not nodos_sin_tareas:
            nodos_disponibles = [
                n for n in nodos
                if n['nombre'] != nodo_actual['nombre']
                and not nodo_sobrecargado(n)
            ]
        else:
            nodos_disponibles = nodos_sin_tareas

        if not nodos_disponibles:
            print("No hay nodos disponibles para reasignar tareas.")
            return

        # Ordenar nodos disponibles por carga (mejor puntuación primero)
        nodos_disponibles.sort(key=calcular_puntuacion_nodo)

        asignaciones_ref = db.collection('asignaciones')
        asignaciones = list(asignaciones_ref.stream())
        tareas_reasignadas = 0

        # Obtener tareas del nodo sobrecargado
        tareas_a_reasignar = [a for a in asignaciones if a.to_dict().get('nodo') == nodo_actual['nombre']]

        if not tareas_a_reasignar:
            print("No hay tareas que reasignar.")
            return

        # Reasignar tareas al mejor nodo disponible
        for asignacion in tareas_a_reasignar:
            # Siempre usar el primer nodo disponible (el mejor según calcular_puntuacion_nodo)
            nodo_destino = nodos_disponibles[0]
            asignaciones_ref.document(asignacion.id).update({
                'nodo': nodo_destino['nombre'],
                'fecha_actualizacion': datetime.datetime.now()
            })
            tareas_reasignadas += 1
            print(f"Tarea reasignada a {nodo_destino['nombre']} (CPU: {nodo_destino['cpu']}%, RAM: {nodo_destino['ram']}%)")

        print(f"{tareas_reasignadas} tarea(s) reasignadas de forma distribuida.")

    except Exception as e:
        print(f"Error en la reasignación de tareas: {str(e)}")


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

def obtener_carga_promedio(nodo: Dict) -> float:
    """
    Calcula la carga promedio de un nodo (CPU + RAM) / 2
    """
    return (nodo['cpu'] + nodo['ram']) / 2

def obtener_tareas_asignadas(nodo_nombre: str) -> List[str]:
    """
    Obtiene la lista de tareas asignadas a un nodo específico
    """
    asignaciones_ref = db.collection('asignaciones')
    asignaciones = asignaciones_ref.where('nodo', '==', nodo_nombre).stream()
    return [doc.to_dict()['tarea'] for doc in asignaciones]

def asignar_tareas():
    """
    Asigna las tareas "Comida" y "Obstáculo" siguiendo el algoritmo de asignación
    basado en la carga de recursos de los nodos.
    """
    # Obtener todos los nodos
    nodos_ref = db.collection('nodos')
    nodos = [doc.to_dict() for doc in nodos_ref.stream()]
    
    if len(nodos) < 1:
        print("Se necesita al menos 1 nodo para realizar las asignaciones")
        return
    
    # Tareas a asignar
    tareas = ["Comida", "Obstáculo"]
    
    for tarea in tareas:
        # Paso a: Buscar nodos no sobrecargados sin tareas
        nodos_candidatos = []
        for nodo in nodos:
            tareas_asignadas = obtener_tareas_asignadas(nodo['nombre'])
            if not nodo_sobrecargado(nodo) and not tareas_asignadas:
                nodos_candidatos.append(nodo)
        
        # Paso b: Si no hay candidatos sin tareas, buscar nodos no sobrecargados
        if not nodos_candidatos:
            nodos_candidatos = [nodo for nodo in nodos if not nodo_sobrecargado(nodo)]
        
        # Paso c: Si aún no hay candidatos, incluir todos los nodos
        if not nodos_candidatos:
            nodos_candidatos = nodos
        
        # Paso d: Seleccionar el nodo con menor carga promedio
        mejor_nodo = min(nodos_candidatos, key=obtener_carga_promedio)
        
        # Paso e: Asignar la tarea
        asignaciones_ref = db.collection('asignaciones')
        asignaciones_ref.add({
            'nodo': mejor_nodo['nombre'],
            'tarea': tarea,
            'fecha_asignacion': datetime.datetime.now()
        })
        
        print(f"Tarea '{tarea}' asignada al nodo {mejor_nodo['nombre']} (CPU: {mejor_nodo['cpu']}%, RAM: {mejor_nodo['ram']}%)")

def limpiar_asignacion():
    """
    Elimina todas las asignaciones existentes en la colección 'asignaciones'
    """
    try:
        asignaciones_ref = db.collection('asignaciones')
        asignaciones = asignaciones_ref.stream()
        
        for asignacion in asignaciones:
            asignaciones_ref.document(asignacion.id).delete()
        
        print("Todas las asignaciones han sido eliminadas correctamente")
    except Exception as e:
        print(f"Error al limpiar asignaciones: {str(e)}")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('inicio.html')

@app.route('/juego')
def juego():
    # Reiniciar la puntuación a 0 en Firebase
    try:
        puntuacion_ref = db.collection('puntuacion').document('total')
        puntuacion_ref.set({'total': 0})
        print("Puntuación reiniciada a 0 correctamente")
        
        # Actualizar el estado del juego a "reiniciar"
        estado_juego_ref = db.collection('estado_juego').document('juego')
        estado_juego_ref.set({'estado': 'reiniciar'})
        print("Estado del juego actualizado a 'reiniciar'")
    except Exception as e:
        print(f"Error al reiniciar el juego: {str(e)}")
    
    return render_template('game.html')

@app.route('/asignar')
def asignar():
    limpiar_asignacion()
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