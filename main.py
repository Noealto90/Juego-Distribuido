from flask import Flask, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
from config.firebase_config import initialize_firebase
from controlador.central.game_manager import GameManager
from controlador.central.load_balancer import LoadBalancer
from controlador.score.score_manager import ScoreManager

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)
CORS(app)

# Inicializar Firebase
initialize_firebase()

# Inicializar componentes
game_manager = GameManager()
load_balancer = LoadBalancer()
score_manager = ScoreManager()

@app.route('/')
def index():
    return render_template('game.html')

@app.route('/ws')
def websocket():
    # Implementar WebSocket
    pass

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    app.run(host=host, port=port) 