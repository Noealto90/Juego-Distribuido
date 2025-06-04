# 🐍 Snake Game Distribuido

Este proyecto consiste en la implementación de un juego tipo Snake con una arquitectura distribuida. Cada componente del sistema se encarga de tareas específicas como la gestión de partidas, la lógica del juego, el monitoreo de nodos y la administración de puntuaciones. Se utilizan tecnologías como Flask, Firebase y Pygame para lograr un entorno interactivo, escalable y eficiente.

---

## 📦 Estructura General del Proyecto

```
Proyecto-Sistemas-Operativos/
├── controlador/       # Lógica de backend distribuido
├── game/              # Motor del juego y lógica del Snake
├── score/             # Gestión de puntuaciones y estadísticas
├── vista/             # Interfaz de usuario (HTML, CSS, JS)
└── config/            # Configuración general del sistema
```

---

## 🚀 Tecnologías Utilizadas

- Python 3.11+
- Flask
- Firebase Admin SDK
- Pygame
- WebSockets
- HTML5 / CSS3 / JavaScript

---

## ⚙️ Instalación y Ejecución

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/snake-distribuido.git
   cd snake-distribuido
   ```

2. **Crea y activa un entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # En Linux/macOS
   venv\Scripts\activate.bat  # En Windows
   ```

3. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las credenciales de Firebase** en la carpeta `/config`.

5. **Ejecuta los servicios según el nodo asignado**:
   ```bash
   python controlador/central/game_manager.py   # Nodo central
   python controlador/game/snake_game.py        # Nodo de juego
   python controlador/score/score_manager.py    # Nodo de puntuación
   ```

---

## 👥 División de Roles

* **Persona 1**: Backend Central (gestión y monitoreo)
* **Persona 2**: Lógica del Juego (Snake, colisiones, estado)
* **Persona 3**: Frontend y Score (interfaz, puntuaciones, rankings)

---

## 📈 Funcionalidades Destacadas

* Gestión distribuida de partidas
* Balanceo de carga en nodos
* Lógica de juego en tiempo real
* Registro de puntuaciones y estadísticas
* Interfaz web responsiva
* Comunicación eficiente con Firebase

---

## 📄 Licencia

Este proyecto es de uso académico para el curso de **Sistemas Operativos** - I Semestre 2025.

---

## 🤝 Colaboradores

* Noelia Alpízar Torres
* Yeilyn Espinoza Zumbado
* Jorge Valladares Blanco
