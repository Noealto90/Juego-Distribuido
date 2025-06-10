# 🐍 Snake Game Distribuido

Este proyecto consiste en la implementación de un juego tipo Snake con una arquitectura distribuida. Cada componente del sistema se encarga de tareas específicas como la gestión de partidas, la lógica del juego, el monitoreo de nodos y la administración de puntuaciones. Se utilizan tecnologías como Flask, Firebase y Pygame para lograr un entorno interactivo, escalable y eficiente.

# Imagen del Juego

![image](https://github.com/user-attachments/assets/b0074e56-d5a4-48d2-b351-1bbd50c954d4)

## 📦 Estructura del Proyecto

```
snake-game-distribuido/
├── config/
│   ├── config.py
│   └── firebase_config.py
├── controlador/
│   ├── central/
│   │   ├── game_manager.py
│   │   └── load_balancer.py
│   ├── game/
│   │   └── snake_game.py
│   ├── score/
│   │   └── score_manager.py
│   ├── agente_reutilizable.py
│   ├── central_reutilizable.py
│   └── websocket_manager.py
├── vista/
│   ├── templates/
│   │   └── game.html
│   ├── styles/
│   │   └── game.css
│   └── scripts/
│       └── game.js
├── .env
├── main.py
├── README.md
└── requirements.txt
```

## 🚀 Tecnologías Utilizadas

- Python 3.8+
- Flask
- Firebase Admin SDK
- Pygame
- WebSockets
- HTML5 / CSS3 / JavaScript
- Git

## ⚙️ Instalación

1. **Clonar el repositorio**:

```bash
git clone <url-del-repositorio>
cd snake-game-distribuido
```

2. **Crear y activar entorno virtual**:

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Instalar dependencias**:

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**:

- Crear un archivo `.env` en la raíz del proyecto
- Copiar el siguiente contenido:

```
# Configuración del servidor
HOST=0.0.0.0
PORT=5000

# Configuración de Firebase
FIREBASE_CREDENTIALS_PATH=clave-firebase.json

# Configuración del juego
GRID_SIZE=20
GAME_SPEED=100

# Configuración de WebSocket
WS_HOST=localhost
WS_PORT=5000
```

5. **Configurar Firebase**:

- Copiar el archivo `clave-firebase.json` a la raíz del proyecto
- Asegurarse de que el archivo tenga los permisos correctos

## 🎮 Ejecución

1. **Iniciar el servidor backend**:

```bash
# Asegurarse de estar en el entorno virtual
python main.py
```

2. **Acceder al frontend**:

- Abrir el navegador web
- Navegar a `http://localhost:5000`

3. **Verificar la conexión**:

- El juego debería cargar en el navegador
- La tabla de clasificación debería estar visible
- Los controles del juego deberían funcionar

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

## 👥 División de Roles

### Nodo Central

- Gestión de partidas
- Balanceo de carga
- Monitoreo del sistema

### Nodo de Juego

- Lógica del juego
- Control de la serpiente
- Detección de colisiones

### Agente: Tarea - Obstáculos

- Gestión de puntuaciones
- Generar los obstáculos del juego
- Actualizar los obstáculos cada vez que se reinicia el juego

### Agente: Tarea - Comida

- Generar las manzanas del juego (ubicación y tipo).
- Actualiza las manzanas cada vez que la serpiente se come alguna.
- Cuenta con una manzana de respaldo por si la serpiente se come dos manzanas muy seguidas.

## 📈 Funcionalidades Destacadas

- Juego de Snake distribuido
- Balanceo de carga entre nodos
- Monitoreo en tiempo real
- Tabla de clasificación
- Comunicación WebSocket
- Persistencia de datos con Firebase
- Interfaz web responsiva
- Comunicación eficiente con Firebase

## 🔍 Detalles Técnicos Adicionales

### Balanceo de Carga

El sistema implementa un balanceo de carga inteligente con las siguientes características:

- Umbral de sobrecarga configurable:

  - CPU: 80%
  - RAM: 80%

- Algoritmo de puntuación para nodos:
  - Peso CPU: 70%
  - Peso RAM: 30%

### Funciones Principales

1. **Cálculo de Puntuación de Nodos**

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

3. **Reasignación de Tareas**

- Sistema de reasignación automática cuando se detecta sobrecarga
- Priorización de nodos sin tareas
- Distribución equitativa de la carga

### Endpoints Disponibles

1. `/` - Página de inicio
2. `/juego` - Interfaz del juego
3. `/asignar` - Asignación de tareas
4. `/iniciar-monitoreo` - Inicio del sistema de monitoreo

### Monitoreo en Tiempo Real

- Sistema de eventos para detectar cambios en nodos
- Reasignación automática de tareas
- Monitoreo de CPU y RAM
- Registro de tareas por nodo

### Gestión de Tareas

- Asignación automática de tareas "Comida" y "Obstáculo"
- Sistema de priorización de nodos
- Limpieza y reinicio de asignaciones
- Persistencia de datos en Firebase

## 🤝 Colaboradores

- Noelia Alpízar Torres
- Yeilyn Espinoza Zumbado
- Jorge Valladares Blanco

## 📄 Licencia

Este proyecto es de uso académico para el curso de **Sistemas Operativos** - I Semestre 2025.
