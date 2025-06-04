from flask import Flask, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import uuid

# Importar código reutilizable
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from controlador.central_reutilizable import monitorear_carga, balancear_carga

app = Flask(__name__)
CORS(app)

# Inicializar Firebase
db = firestore.client()

class GameManager:
    def __init__(self):
        self.active_games = {}
        
    def create_game(self, player_id):
        """
        Crea una nueva partida
        """
        game_id = str(uuid.uuid4())
        nodo = balancear_carga()
        
        game_data = {
            "id": game_id,
            "player_id": player_id,
            "nodo_asignado": nodo.id,
            "estado": "activo",
            "puntuacion": 0,
            "fecha_creacion": datetime.now().isoformat()
        }
        
        # Guardar en Firebase
        db.collection('juegos').document(game_id).set(game_data)
        
        # Monitorear la nueva partida
        monitorear_carga(game_id, "juego", "activo", game_data)
        
        return game_id
    
    def end_game(self, game_id):
        """
        Finaliza una partida
        """
        game_ref = db.collection('juegos').document(game_id)
        game_ref.update({
            "estado": "terminado",
            "fecha_fin": datetime.now().isoformat()
        })
        
        monitorear_carga(game_id, "juego", "terminado")
        
        return True

# Rutas de la API
@app.route('/crear-juego/<player_id>', methods=['POST'])
def crear_juego(player_id):
    game_manager = GameManager()
    game_id = game_manager.create_game(player_id)
    return jsonify({"game_id": game_id})

@app.route('/terminar-juego/<game_id>', methods=['POST'])
def terminar_juego(game_id):
    game_manager = GameManager()
    result = game_manager.end_game(game_id)
    return jsonify({"success": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 