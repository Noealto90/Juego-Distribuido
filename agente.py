import firebase_admin
from firebase_admin import credentials, firestore
import random
import os
from dotenv import load_dotenv
import time
import threading
import socket
import psutil
from datetime import datetime, timezone

# Cargar variables de entorno
load_dotenv()

class Agente:
    def __init__(self):
        # Obtener el nombre del nodo actual
        self.nombre_nodo = socket.gethostname()
        
        # Inicializar Firebase con el archivo de credenciales correcto
        cred = credentials.Certificate("clave-firebase.json")
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        
        # Iniciar el monitoreo de recursos en un hilo separado
        self.monitor_recursos_thread = threading.Thread(target=self._monitorear_recursos, daemon=True)
        self.monitor_recursos_thread.start()
        
        # Verificar las tareas asignadas
        tarea_comida = self._verificar_asignacion_tarea('Comida')
        tarea_obstaculo = self._verificar_asignacion_tarea('Obstáculo')
        
        # Iniciar el procesamiento de puntos solo si tiene la tarea de obstáculo
        if tarea_obstaculo:
            print("Este nodo tiene asignada la tarea de Obstáculo. Iniciando procesamiento de puntos...")
            # Generar obstáculos aleatorios al inicio
            self.obstaculos = self._generar_obstaculos_aleatorios()
            self.procesar_puntos_thread = threading.Thread(target=self._procesar_puntos_periodicamente, daemon=True)
            self.procesar_puntos_thread.start()
        else:
            print("Este nodo no tiene asignada la tarea de Obstáculo. No se procesarán puntos.")
        
        # Iniciar la tarea de comida si está asignada
        if tarea_comida:
            print("Este nodo tiene asignada la tarea de Comida. Iniciando...")
            self.obstaculos = self._cargar_obstaculos()
            self._inicializar_manzanas()
            self.monitor_thread = threading.Thread(target=self._monitorear_manzanas, daemon=True)
            self.monitor_thread.start()
        else:
            print("Este nodo no tiene asignada la tarea de Comida.")

    def obtener_datos(self):
        """
        Obtiene los datos del sistema
        """
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disco = psutil.disk_usage("/").percent
        red = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        red = round(red / (1024 * 1024), 2)
        tiempo = datetime.now(timezone.utc).isoformat()
        
        ip_local = socket.gethostbyname(socket.gethostname())
        
        return {
            "nombre": self.nombre_nodo,
            "ip": ip_local,
            "cpu": cpu,
            "ram": ram,
            "disco": disco,
            "red": red,
            "ultima_actualizacion": tiempo,
            "descripcion": "Nodo de procesamiento estándar"
        }

    def _monitorear_recursos(self):
        """
        Monitorea los recursos del sistema cada 25 segundos
        """
        while True:
            try:
                datos = self.obtener_datos()
                print(f"{self.nombre_nodo} → {datos}")
                self.db.collection("nodos").document(self.nombre_nodo).set(datos)
                time.sleep(25)
            except Exception as e:
                print(f"Error al monitorear recursos: {e}")
                time.sleep(5)  # Esperar un poco antes de reintentar en caso de error

    def _verificar_asignacion_tarea(self, tarea):
        """Verifica si este nodo tiene asignada una tarea específica"""
        try:
            asignaciones_ref = self.db.collection('asignaciones')
            docs = asignaciones_ref.stream()
            
            for doc in docs:
                datos = doc.to_dict()
                print(f"Verificando asignación: Nodo={datos.get('nodo')}, Tarea={datos.get('tarea')}")  # Debug
                if (datos.get('nodo') == self.nombre_nodo and 
                    datos.get('tarea') == tarea):
                    print(f"¡Tarea {tarea} encontrada para este nodo!")  # Debug
                    return True
            return False
        except Exception as e:
            print(f"Error al verificar asignación de tarea: {e}")
            return False

    def _cargar_obstaculos(self):
        """Carga los obstáculos desde Firebase"""
        obstaculos_ref = self.db.collection('obstaculo')
        obstaculos = []
        
        # Obtener el documento de obstáculos
        docs = obstaculos_ref.stream()
        for doc in docs:
            datos = doc.to_dict()
            if 'obstaculo' in datos and isinstance(datos['obstaculo'], list):
                for obstaculo in datos['obstaculo']:
                    if 'x' in obstaculo and 'y' in obstaculo:
                        obstaculos.append((obstaculo['x'], obstaculo['y']))
        
        print(f"Obstáculos cargados: {obstaculos}")
        return obstaculos

    def _es_posicion_valida(self, x, y):
        """Verifica si una posición está libre de obstáculos"""
        return (x, y) not in self.obstaculos

    def _generar_posicion_aleatoria(self):
        """Genera una posición aleatoria que no esté ocupada por obstáculos"""
        while True:
            x = random.randint(0, 29)  # Ajustado a 20 para coincidir con el rango de obstáculos
            y = random.randint(0, 19)  # Ajustado a 20 para coincidir con el rango de obstáculos
            if self._es_posicion_valida(x, y):
                return x, y

    def _generar_nueva_manzana(self):
        """Genera una nueva manzana con posición aleatoria y tipo aleatorio"""
        x, y = self._generar_posicion_aleatoria()
        tipo = 'Especial' if random.random() < 0.25 else 'Normal'  # 25% de probabilidad de ser especial
        return {
            'tipo': tipo,
            'ubicacion': {
                'x': x,
                'y': y
            },
            'estado': 0
        }

    def actualizar_comida(self, tipo_comida, x, y):
        """Actualiza la posición de la comida en Firebase"""
        comida_ref = self.db.collection('comida')
        comida_ref.document(tipo_comida).update({
            'ubicacion': {
                'x': x,
                'y': y
            }
        })

    def _inicializar_manzanas(self):
        """Inicializa las manzanas en Firebase"""
        comida_ref = self.db.collection('comida')
        
        # Siempre generar nueva manzana normal al inicio
        nueva_manzana_normal = self._generar_nueva_manzana()
        nueva_manzana_normal['estado'] = 0
        comida_ref.document('Normal').set(nueva_manzana_normal)
        print("Nueva manzana Normal generada al inicio")
        
        # Siempre generar nueva manzana de respaldo al inicio
        nueva_manzana_respaldo = self._generar_nueva_manzana()
        nueva_manzana_respaldo['estado'] = 0
        comida_ref.document('Respaldo').set(nueva_manzana_respaldo)
        print("Nueva manzana Respaldo generada al inicio")

    def _monitorear_manzanas(self):
        """Monitorea continuamente el estado de las manzanas"""
        comida_ref = self.db.collection('comida')
        
        # Crear un callback para los cambios
        def on_snapshot(doc_snapshot, changes, read_time):
            for change in changes:
                if change.type.name == 'MODIFIED':
                    doc = change.document
                    datos = doc.to_dict()
                    
                    # Si el estado cambió a 1, generar nueva manzana
                    if datos.get('estado') == 1:
                        print(f"Manzana {doc.id} fue comida, generando nueva...")
                        nueva_manzana = self._generar_nueva_manzana()
                        comida_ref.document(doc.id).set(nueva_manzana)
                        print(f"Nueva manzana generada para {doc.id}: {nueva_manzana}")

        # Suscribirse a los cambios
        comida_ref.on_snapshot(on_snapshot)

    def obtener_comida(self):
        """Obtiene la información de la comida de Firebase"""
        comida_ref = self.db.collection('comida')
        return {doc.id: doc.to_dict() for doc in comida_ref.stream()}

    def _procesar_puntos(self):
        """
        Procesa los puntos no procesados y actualiza la puntuación total
        """
        try:
            # Obtener todos los puntos con estado 0
            puntos_ref = self.db.collection('puntos')
            puntos_no_procesados = puntos_ref.where('estado', '==', 0).stream()
            
            # Obtener el documento de puntuación total
            puntuacion_ref = self.db.collection('puntuacion').document('total')
            puntuacion_doc = puntuacion_ref.get()
            
            if not puntuacion_doc.exists:
                # Si no existe el documento de puntuación, crearlo con total = 0
                puntuacion_ref.set({'total': 0})
                puntuacion_total = 0
            else:
                puntuacion_total = puntuacion_doc.to_dict().get('total', 0)
            
            # Procesar cada punto no procesado
            for punto_doc in puntos_no_procesados:
                punto_data = punto_doc.to_dict()
                cantidad = punto_data.get('cantidad', 0)
                
                # Actualizar la puntuación total
                puntuacion_total += cantidad
                puntuacion_ref.update({'total': puntuacion_total})
                
                # Marcar el punto como procesado
                puntos_ref.document(punto_doc.id).update({'estado': 1})
                
                print(f"Punto procesado: {cantidad}. Nueva puntuación total: {puntuacion_total}")
            
        except Exception as e:
            print(f"Error al procesar puntos: {e}")

    def _procesar_puntos_periodicamente(self):
        """
        Ejecuta el procesamiento de puntos cada 5 segundos
        """
        while True:
            self._procesar_puntos()
            time.sleep(5)

    def _generar_obstaculos_aleatorios(self, cantidad=15):
        """Genera obstáculos aleatorios, reemplaza los existentes en Firebase"""
        print("Generando obstáculos aleatorios...")
        obstaculos = set()
        while len(obstaculos) < cantidad:
            x = random.randint(0, 29)
            y = random.randint(0, 19)
            obstaculos.add((x, y))
            print(f"Obstáculo generado en posición: ({x}, {y})")

        lista_obstaculos = [{'x': x, 'y': y} for x, y in obstaculos]

        # Elimina todos los documentos existentes en la colección "obstaculo"
        obstaculos_ref = self.db.collection("obstaculo")
        docs = obstaculos_ref.stream()
        for doc in docs:
            doc.reference.delete()

        # Guardar los nuevos obstáculos
        obstaculos_ref.document("mapa1").set({
            "obstaculo": lista_obstaculos
        })

        print(f"\nTotal de {len(lista_obstaculos)} obstáculos generados y guardados en Firebase.")
        return obstaculos

if __name__ == "__main__":
    agente = Agente()
    try:
        # Mantener el programa en ejecución
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario")
