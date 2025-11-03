# Distributed Snake Game

This project implements a **Snake-style game** with a **distributed architecture**.  
Each system component handles specific tasks such as game management, logic processing, node monitoring, and score tracking.  
It uses technologies like **Flask**, **Firebase**, and **Pygame** to create an interactive and scalable environment.

# Game Preview

![image](https://github.com/user-attachments/assets/b0074e56-d5a4-48d2-b351-1bbd50c954d4)

## Technologies Used

- Python 3.8+
- Flask
- Firebase Admin SDK
- Pygame
- WebSockets
- HTML5 / CSS3 / JavaScript
- Git

## ⚙️ Installation

1. **Clone the repository**:

```bash
git clone <url-del-repositorio>
cd snake-game-distribuido
```

2. **Create and activate a virtual environment**:

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:

- Create a file named `.env` in the project root with the following content:

```

HOST=0.0.0.0
PORT=5000

FIREBASE_CREDENTIALS_PATH=clave-firebase.json

GRID_SIZE=20
GAME_SPEED=100

WS_HOST=localhost
WS_PORT=5000
```

5. **Configure Firebase**:

- Copiar el archivo `clave-firebase.json` a la raíz del proyecto
- Asegurarse de que el archivo tenga los permisos correctos

## Run the Game

1. **Start the backend server:**:

```bash
# Ensure you are in the virtual environment
python main.py
```

2. **Open the frontend**:

- Open your web browser
- Go to `http://localhost:5000`

3. **Check everything is working**:

- The game should load in the browser.
- The leaderboard should be visible.
- The controls should respond correctly

## 🔧 Solución de problemas comunes

1. **Error de conexión a Firebase**:

- Verificar que `clave-firebase.json` existe y tiene el formato correcto
- Comprobar la conexión a internet
- Verificar las credenciales de Firebase

2. **Error al iniciar el servidor**:

- Asegurarse de que el puerto 5000 no está en uso
- Verificar que todas las dependencias están instaladas
- Comprobar que el archivo `.env` existe y está configurado correctamente

3. **Problemas con el frontend**:

- Limpiar la caché del navegador
- Verificar la consola del navegador para errores
- Asegurarse de que el servidor backend está corriendo

## Role Distribution

### Central Node

- Manages matches
- Load balancing
- System monitoring

### Game Node

- Game logic
- Snake movement
- Collision detection

### Agent – Obstacles

- Manages scores
- Generates and updates obstacles

### Agent – Food

- Generates apples (location and type)
- Updates when the snake eats an apple
- Keeps a backup apple in case of quick sequences

## Main Features

- Distributed Snake game
- Load balancing between nodes
- Real-time monitoring
- Leaderboard system
- WebSocket communication
- Firebase data persistence
- Responsive web interface

## Technical Details

### Load Balancing

The system includes smart load balancing with:

- Overload threshold:

  - CPU: 80%
  - RAM: 80%

- Node scoring algorithm:
  - Peso CPU: 70%
  - Peso RAM: 30%

1. **Node Score Calculation**

```python
def calcular_puntuacion_nodo(nodo: Dict) -> float:
    cpu_weight = 0.7
    ram_weight = 0.3
    cpu_score = nodo['cpu'] / 100
    ram_score = nodo['ram'] / 100
    return (cpu_score * cpu_weight) + (ram_score * ram_weight)
```

2. **Detección de Sobrecarga**

```python
def nodo_sobrecargado(nodo: Dict) -> bool:
    return nodo['cpu'] > SOBRECARGA_CPU or nodo['ram'] > SOBRECARGA_RAM
```

3. **Task Reassignment**

- Automatic reassignment system when overload is detected
- Prioritization of nodes without tasks
- Equitable distribution of load

### Available Endpoints

1. `/` - Home page
2. `/game` - Game interface
3. `/assign` - Task assignment
4. `/start-monitoring` - Start monitoring system

### Real-Time Monitoring

- Event system to detect changes in nodes
- Automatic task reassignment
- CPU and RAM monitoring
- Task log per node

### Task Management

- Automatic assignment of “Food” and “Obstacle” tasks
- Node prioritization system
- Cleaning and restarting assignments
- Data persistence in Firebase

## Contributors

- Noelia Alpízar Torres
- Yeilyn Espinoza Zumbado
- Jorge Valladares Blanco

## License

This project was developed for academic purposes for the Operating Systems course – I Semester 2025.
