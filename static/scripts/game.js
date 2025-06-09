// Importar Firebase
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import {
  getFirestore,
  collection,
  getDocs,
  updateDoc,
  onSnapshot,
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";

// Configuración de Firebase
const firebaseConfig = {
  apiKey: "AIzaSyDxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx",
  authDomain: "proyectoso-89112.firebaseapp.com",
  projectId: "proyectoso-89112",
  storageBucket: "proyectoso-89112.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef1234567890",
};

// Inicializar Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

console.log("Conectada a Firebase desde 1");

class SnakeGame {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.gridSize = 20;
    this.snake = [{ x: 5, y: 5 }];
    this.direction = "right";
    this.nextDirection = "right";
    this.food = null; // Inicialmente no hay comida
    this.obstacles = []; // Array para almacenar obstáculos
    this.score = 0;
    this.gameOver = false;
    this.speed = 200;
    this.lastRenderTime = 0;
    this.startTime = null;
    this.elapsedTime = 0;
    this.gameStarted = false;
    this.foodPulse = 0;
    this.foodPulseDirection = 1;
    this.specialFood = null;
    this.specialFoodTimer = null;
    this.isSpecialMode = false;
    this.specialModeEndTime = 0;
    this.colorHue = 0;
    this.segmentHues = [];
    this.foodRotation = 0;
    this.snakeScale = 0.9; // Escala para hacer la serpiente más delgada
    this.snakePattern = 0; // Para animación del patrón
    this.rainbowOffset = 0; // Para efecto arcoíris
    this.rainbowSpeed = 60; // Velocidad ultra rápida del efecto arcoíris
    this.glowIntensity = 0; // Intensidad del brillo
    this.glowDirection = 1; // Dirección del brillo
    this.colorChangeSpeed = 0.4; // Velocidad de cambio de color ultra rápida
    this.numObstacles = 15;

    // Elementos del DOM
    this.scoreElement = document.getElementById("score");
    this.timeElement = document.getElementById("time");
    this.specialModeElement = document.getElementById("specialMode");
    this.specialTimeElement = document.getElementById("specialTime");
    this.gameOverElement = document.getElementById("gameOver");
    this.finalScoreElement = document.getElementById("finalScore");
    this.finalTimeElement = document.getElementById("finalTime");

    // Agregar propiedades para el monitoreo
    this.nodoActual = null;
    this.tareaActual = null;
    this.monitoreoActivo = false;
    this.ultimoCPU = 0;
    this.ultimoRAM = 0;
    this.umbralCambio = 5; // Porcentaje de cambio mínimo para actualizar

    // Iniciar monitoreo de asignaciones
    this.iniciarMonitoreoAsignaciones();
  }

  async iniciarMonitoreoAsignaciones() {
    try {
      const asignacionesRef = collection(db, "asignaciones");

      // Escuchar cambios en las asignaciones
      onSnapshot(asignacionesRef, (snapshot) => {
        snapshot.docChanges().forEach((change) => {
          if (change.type === "modified") {
            const nuevaAsignacion = change.doc.data();

            // Si la asignación es para este nodo, actualizar el estado
            if (nuevaAsignacion.nodo === this.nodoActual) {
              this.tareaActual = nuevaAsignacion.tarea;
              console.log(`Tarea actualizada: ${this.tareaActual}`);
            }
          }
        });
      });
    } catch (error) {
      console.error("Error al iniciar monitoreo de asignaciones:", error);
    }
  }

  async actualizarEstadoNodo(cpu, ram) {
    try {
      if (!this.nodoActual) return;

      // Verificar si el cambio es significativo
      const cambioCPU = Math.abs(cpu - this.ultimoCPU);
      const cambioRAM = Math.abs(ram - this.ultimoRAM);

      if (cambioCPU >= this.umbralCambio || cambioRAM >= this.umbralCambio) {
        const nodosRef = collection(db, "nodos");
        const querySnapshot = await getDocs(nodosRef);

        querySnapshot.forEach(async (doc) => {
          if (doc.data().nombre === this.nodoActual) {
            await updateDoc(doc.ref, {
              cpu: cpu,
              ram: ram,
              ultima_actualizacion: new Date(),
            });

            // Actualizar valores últimos
            this.ultimoCPU = cpu;
            this.ultimoRAM = ram;

            console.log(
              `Estado del nodo actualizado - CPU: ${cpu}%, RAM: ${ram}%`
            );
          }
        });
      }
    } catch (error) {
      console.error("Error al actualizar estado del nodo:", error);
    }
  }

  async generateFood() {
    const maxX = Math.floor(this.canvas.width / this.gridSize);
    const maxY = Math.floor(this.canvas.height / this.gridSize);

    try {
      const comidaRef = collection(db, "comida");
      const querySnapshot = await getDocs(comidaRef);

      let normalFood = null;
      let respaldoFood = null;
      let normalDocRef = null;
      let respaldoDocRef = null;

      querySnapshot.forEach((doc) => {
        const data = doc.data();
        if (doc.id === "Normal") {
          normalFood = data;
          normalDocRef = doc.ref;
        } else if (doc.id === "Respaldo") {
          respaldoFood = data;
          respaldoDocRef = doc.ref;
        }
      });

      // Intentar usar la manzana Normal primero
      if (normalFood && normalFood.estado === 0) {
        await updateDoc(normalDocRef, { estado: 1 });
        console.log("Usando manzana Normal");
        return {
          x: normalFood.ubicacion.x,
          y: normalFood.ubicacion.y,
          isSpecial: normalFood.tipo === "Especial",
        };
      }

      // Si Normal no está disponible, intentar usar Respaldo
      if (respaldoFood && respaldoFood.estado === 0) {
        await updateDoc(respaldoDocRef, { estado: 1 });
        console.log("Usando manzana Respaldo");
        return {
          x: respaldoFood.ubicacion.x,
          y: respaldoFood.ubicacion.y,
          isSpecial: respaldoFood.tipo === "Especial",
        };
      }

      // Si ninguna está disponible, usar posición por defecto
      console.log("No hay manzanas disponibles en Firebase");
      return {
        x: 17,
        y: 18,
        isSpecial: false,
      };
    } catch (error) {
      console.error("Error al consultar la colección comida:", error);
      return {
        x: 17,
        y: 18,
        isSpecial: false,
      };
    }
  }

  generateObstacles() {
    this.obstacles = [];
    const maxX = Math.floor(this.canvas.width / this.gridSize);
    const maxY = Math.floor(this.canvas.height / this.gridSize);

    for (let i = 0; i < this.numObstacles; i++) {
      let obstacle;
      do {
        obstacle = {
          x: Math.floor(Math.random() * maxX),
          y: Math.floor(Math.random() * maxY),
        };
      } while (
        // Evitar que los obstáculos aparezcan sobre la serpiente
        this.snake.some(
          (segment) => segment.x === obstacle.x && segment.y === obstacle.y
        ) ||
        // Evitar que los obstáculos aparezcan sobre la comida
        (this.food.x === obstacle.x && this.food.y === obstacle.y) ||
        // Evitar que los obstáculos aparezcan sobre otros obstáculos
        this.obstacles.some(
          (obs) => obs.x === obstacle.x && obs.y === obstacle.y
        )
      );
      this.obstacles.push(obstacle);
    }
  }

  async update() {
    if (this.gameOver) return;

    // Update direction based on nextDirection
    this.direction = this.nextDirection;

    const head = { ...this.snake[0] };
    switch (this.direction) {
      case "up":
        head.y--;
        break;
      case "down":
        head.y++;
        break;
      case "left":
        head.x--;
        break;
      case "right":
        head.x++;
        break;
    }

    // Check collision with walls
    if (
      head.x < 0 ||
      head.x >= this.canvas.width / this.gridSize ||
      head.y < 0 ||
      head.y >= this.canvas.height / this.gridSize
    ) {
      this.gameOver = true;
      this.showGameOver();
      return;
    }

    // Check collision with self
    if (
      this.snake.some((segment) => segment.x === head.x && segment.y === head.y)
    ) {
      this.gameOver = true;
      this.showGameOver();
      return;
    }

    // Check collision with obstacles
    if (
      !this.isSpecialMode &&
      this.obstacles.some(
        (obstacle) => obstacle.x === head.x && obstacle.y === head.y
      )
    ) {
      this.gameOver = true;
      this.showGameOver();
      return;
    }

    // Check if obstacle is eaten during special mode
    if (this.isSpecialMode) {
      const obstacleIndex = this.obstacles.findIndex(
        (obstacle) => obstacle.x === head.x && obstacle.y === head.y
      );
      if (obstacleIndex !== -1) {
        // Remove the eaten obstacle
        this.obstacles.splice(obstacleIndex, 1);
        // Add points for eating obstacle
        this.score += 20;
        this.showScoreAnimation(head.x, head.y, 20, "#9B59B6");
        // Update score display
        this.scoreElement.textContent = this.score;
      }
    }

    this.snake.unshift(head);

    // Check if food is eaten
    if (head.x === this.food.x && head.y === this.food.y) {
      if (this.food.isSpecial) {
        this.score += 15;
        this.activateSpecialMode();
        this.showScoreAnimation(head.x, head.y, 15, "#FFD700");
      } else {
        this.score += 10;
        this.showScoreAnimation(head.x, head.y, 10, "#2ECC71");
      }
      // Solo generar nueva comida si la serpiente realmente se comió la comida actual
      if (this.food) {
        this.food = await this.generateFood();
      }
      // Increase speed only if not in special mode
      if (!this.isSpecialMode) {
        this.speed = Math.max(100, this.speed - 5);
      }
      // Actualizar el score en el DOM
      this.scoreElement.textContent = this.score;
    } else {
      this.snake.pop();
    }

    // Update elapsed time
    if (this.startTime) {
      this.elapsedTime = Math.floor((Date.now() - this.startTime) / 1000);
      this.timeElement.textContent = this.formatTime(this.elapsedTime);
    }

    // Update food pulse animation
    this.foodPulse += 0.1 * this.foodPulseDirection;
    if (this.foodPulse > 1) {
      this.foodPulse = 1;
      this.foodPulseDirection = -1;
    } else if (this.foodPulse < 0) {
      this.foodPulse = 0;
      this.foodPulseDirection = 1;
    }

    // Update food rotation
    this.foodRotation = (this.foodRotation + 2) % 360;

    // Update snake pattern animation
    this.snakePattern = (this.snakePattern + 0.1) % 1;
    this.rainbowOffset = (this.rainbowOffset + this.rainbowSpeed) % 360;

    // Update glow effect
    if (this.isSpecialMode) {
      this.glowIntensity += 0.3 * this.glowDirection;
      if (this.glowIntensity >= 1) {
        this.glowIntensity = 1;
        this.glowDirection = -1;
      } else if (this.glowIntensity <= 0.3) {
        this.glowIntensity = 0.3;
        this.glowDirection = 1;
      }
    } else {
      this.glowIntensity = 0;
    }

    // Update color hues for special mode
    if (this.isSpecialMode) {
      this.colorHue = (this.colorHue + 3) % 360;
      this.segmentHues = this.snake.map(
        (_, index) => (this.colorHue + index * 30) % 360
      );
      if (Date.now() > this.specialModeEndTime) {
        this.deactivateSpecialMode();
      } else {
        const remainingTime = Math.ceil(
          (this.specialModeEndTime - Date.now()) / 1000
        );
        this.specialTimeElement.textContent = `${remainingTime}s`;
      }
    }
  }

  showGameOver() {
    this.gameOverElement.style.display = "block";
    this.finalScoreElement.textContent = this.score;
    this.finalTimeElement.textContent = this.formatTime(this.elapsedTime);
  }

  activateSpecialMode() {
    this.isSpecialMode = true;
    this.specialModeEndTime = Date.now() + 3000; // 3 segundos
    this.speed = 200; // Velocidad inicial ajustada en el método start
    this.segmentHues = this.snake.map(
      (_, index) => (this.colorHue + index * 30) % 360
    );
    this.specialModeElement.style.display = "block";
  }

  deactivateSpecialMode() {
    this.isSpecialMode = false;
    this.speed = 200; // Velocidad inicial ajustada para reducir lag
    this.specialModeElement.style.display = "none";
  }

  showScoreAnimation(x, y, points, color) {
    const scoreElement = document.createElement("div");
    scoreElement.textContent = `+${points}`;
    scoreElement.style.position = "absolute";
    scoreElement.style.left = `${x * this.gridSize + this.canvas.offsetLeft}px`;
    scoreElement.style.top = `${y * this.gridSize + this.canvas.offsetTop}px`;
    scoreElement.style.color = color;
    scoreElement.style.fontSize = "24px";
    scoreElement.style.fontWeight = "bold";
    scoreElement.style.pointerEvents = "none";
    scoreElement.style.transition = "all 0.5s ease-out";
    scoreElement.style.opacity = "1";
    scoreElement.style.transform = "translateY(0)";
    scoreElement.style.textShadow = "0 0 10px rgba(255, 255, 255, 0.5)";
    document.body.appendChild(scoreElement);

    setTimeout(() => {
      scoreElement.style.opacity = "0";
      scoreElement.style.transform = "translateY(-20px)";
      setTimeout(() => scoreElement.remove(), 500);
    }, 100);
  }

  draw() {
    // Clear canvas
    this.ctx.fillStyle = "#2C3E50";
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw grid
    this.ctx.strokeStyle = "#34495E";
    this.ctx.lineWidth = 0.5;
    for (let i = 0; i < this.canvas.width; i += this.gridSize) {
      this.ctx.beginPath();
      this.ctx.moveTo(i, 0);
      this.ctx.lineTo(i, this.canvas.height);
      this.ctx.stroke();
    }
    for (let i = 0; i < this.canvas.height; i += this.gridSize) {
      this.ctx.beginPath();
      this.ctx.moveTo(0, i);
      this.ctx.lineTo(this.canvas.width, i);
      this.ctx.stroke();
    }

    // Draw obstacles
    this.ctx.fillStyle = "#9B59B6";
    this.ctx.shadowColor = "#8E44AD";
    this.ctx.shadowBlur = 10;
    for (const obstacle of this.obstacles) {
      this.ctx.beginPath();
      this.ctx.arc(
        obstacle.x * this.gridSize + this.gridSize / 2,
        obstacle.y * this.gridSize + this.gridSize / 2,
        this.gridSize / 2 - 2,
        0,
        Math.PI * 2
      );
      this.ctx.fill();
    }
    this.ctx.shadowBlur = 0;

    // Draw snake body
    const segmentSize = this.gridSize * this.snakeScale;
    const offset = (this.gridSize - segmentSize) / 2;

    // Dibujar el cuerpo de la serpiente como una unidad continua
    this.ctx.beginPath();
    this.ctx.lineWidth = segmentSize;
    this.ctx.lineCap = "round";
    this.ctx.lineJoin = "round";

    // Crear el gradiente para todo el cuerpo
    let bodyGradient;
    if (this.isSpecialMode) {
      // Efecto arcoíris ultra mega dinámico
      const hue1 = this.rainbowOffset % 360;
      const hue2 = (hue1 + 20) % 360; // Espacio entre colores reducido al mínimo
      const hue3 = (hue1 + 40) % 360;
      const hue4 = (hue1 + 60) % 360;
      const hue5 = (hue1 + 80) % 360;
      const hue6 = (hue1 + 100) % 360;

      bodyGradient = this.ctx.createLinearGradient(
        0,
        0,
        this.canvas.width,
        this.canvas.height
      );
      bodyGradient.addColorStop(
        0,
        `hsla(${hue1}, 100%, 90%, ${0.98 + this.glowIntensity * 0.02})`
      );
      bodyGradient.addColorStop(
        0.17,
        `hsla(${hue2}, 100%, 95%, ${0.98 + this.glowIntensity * 0.02})`
      );
      bodyGradient.addColorStop(
        0.33,
        `hsla(${hue3}, 100%, 90%, ${0.98 + this.glowIntensity * 0.02})`
      );
      bodyGradient.addColorStop(
        0.5,
        `hsla(${hue4}, 100%, 95%, ${0.98 + this.glowIntensity * 0.02})`
      );
      bodyGradient.addColorStop(
        0.67,
        `hsla(${hue5}, 100%, 90%, ${0.98 + this.glowIntensity * 0.02})`
      );
      bodyGradient.addColorStop(
        0.83,
        `hsla(${hue6}, 100%, 95%, ${0.98 + this.glowIntensity * 0.02})`
      );
      bodyGradient.addColorStop(
        1,
        `hsla(${hue1}, 100%, 90%, ${0.98 + this.glowIntensity * 0.02})`
      );

      // Añadir efecto de brillo ultra intenso
      this.ctx.shadowColor = `hsla(${hue1}, 100%, 80%, ${
        0.8 + this.glowIntensity * 0.2
      })`;
      this.ctx.shadowBlur = 30 + this.glowIntensity * 25;
    } else {
      bodyGradient = this.ctx.createLinearGradient(
        0,
        0,
        this.canvas.width,
        this.canvas.height
      );
      bodyGradient.addColorStop(0, "#2ECC71");
      bodyGradient.addColorStop(0.5, "#27AE60");
      bodyGradient.addColorStop(1, "#2ECC71");
      this.ctx.shadowBlur = 10;
    }
    this.ctx.strokeStyle = bodyGradient;

    // Dibujar el cuerpo como una línea continua
    for (let i = 0; i < this.snake.length - 1; i++) {
      const current = this.snake[i];
      const next = this.snake[i + 1];

      const x1 = current.x * this.gridSize + this.gridSize / 2;
      const y1 = current.y * this.gridSize + this.gridSize / 2;
      const x2 = next.x * this.gridSize + this.gridSize / 2;
      const y2 = next.y * this.gridSize + this.gridSize / 2;

      if (i === 0) {
        this.ctx.moveTo(x1, y1);
      }
      this.ctx.lineTo(x2, y2);
    }
    this.ctx.stroke();

    // Dibujar la cabeza
    const head = this.snake[0];
    const headX = head.x * this.gridSize + offset;
    const headY = head.y * this.gridSize + offset;

    if (this.isSpecialMode) {
      const hue = this.rainbowOffset % 360;
      const gradient = this.ctx.createRadialGradient(
        headX + segmentSize / 2,
        headY + segmentSize / 2,
        0,
        headX + segmentSize / 2,
        headY + segmentSize / 2,
        segmentSize / 2
      );
      gradient.addColorStop(
        0,
        `hsla(${hue}, 100%, 95%, ${0.99 + this.glowIntensity * 0.01})`
      );
      gradient.addColorStop(
        0.25,
        `hsla(${(hue + 20) % 360}, 100%, 90%, ${
          0.99 + this.glowIntensity * 0.01
        })`
      );
      gradient.addColorStop(
        0.5,
        `hsla(${(hue + 40) % 360}, 100%, 85%, ${
          0.99 + this.glowIntensity * 0.01
        })`
      );
      gradient.addColorStop(
        0.75,
        `hsla(${(hue + 60) % 360}, 100%, 80%, ${
          0.99 + this.glowIntensity * 0.01
        })`
      );
      gradient.addColorStop(
        1,
        `hsla(${(hue + 80) % 360}, 100%, 75%, ${
          0.99 + this.glowIntensity * 0.01
        })`
      );
      this.ctx.fillStyle = gradient;
      this.ctx.shadowColor = `hsla(${hue}, 100%, 80%, ${
        0.8 + this.glowIntensity * 0.2
      })`;
      this.ctx.shadowBlur = 35 + this.glowIntensity * 30;
    } else {
      const gradient = this.ctx.createRadialGradient(
        headX + segmentSize / 2,
        headY + segmentSize / 2,
        0,
        headX + segmentSize / 2,
        headY + segmentSize / 2,
        segmentSize / 2
      );
      gradient.addColorStop(0, "#2ECC71");
      gradient.addColorStop(1, "#27AE60");
      this.ctx.fillStyle = gradient;
      this.ctx.shadowColor = "#2ECC71";
      this.ctx.shadowBlur = 15;
    }

    // Dibujar la cabeza con forma más ovalada
    this.ctx.beginPath();
    this.ctx.ellipse(
      headX + segmentSize / 2,
      headY + segmentSize / 2,
      segmentSize / 2,
      segmentSize / 1.5,
      0,
      0,
      Math.PI * 2
    );
    this.ctx.fill();

    // Dibujar los ojos
    const eyeSize = segmentSize * 0.2;
    const eyeOffset = segmentSize * 0.2;
    let eyeX1, eyeY1, eyeX2, eyeY2;

    switch (this.direction) {
      case "right":
        eyeX1 = eyeX2 = headX + segmentSize - eyeOffset;
        eyeY1 = headY + eyeOffset;
        eyeY2 = headY + segmentSize - eyeOffset;
        break;
      case "left":
        eyeX1 = eyeX2 = headX + eyeOffset;
        eyeY1 = headY + eyeOffset;
        eyeY2 = headY + segmentSize - eyeOffset;
        break;
      case "up":
        eyeY1 = eyeY2 = headY + eyeOffset;
        eyeX1 = headX + eyeOffset;
        eyeX2 = headX + segmentSize - eyeOffset;
        break;
      case "down":
        eyeY1 = eyeY2 = headY + segmentSize - eyeOffset;
        eyeX1 = headX + eyeOffset;
        eyeX2 = headX + segmentSize - eyeOffset;
        break;
    }

    // Ojos con brillo
    this.ctx.shadowBlur = 0;
    this.ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
    this.ctx.beginPath();
    this.ctx.arc(eyeX1, eyeY1, eyeSize, 0, Math.PI * 2);
    this.ctx.arc(eyeX2, eyeY2, eyeSize, 0, Math.PI * 2);
    this.ctx.fill();

    // Pupilas con brillo
    this.ctx.fillStyle = "#000000";
    const pupilSize = eyeSize * 0.6;
    this.ctx.beginPath();
    this.ctx.arc(eyeX1, eyeY1, pupilSize, 0, Math.PI * 2);
    this.ctx.arc(eyeX2, eyeY2, pupilSize, 0, Math.PI * 2);
    this.ctx.fill();

    // Reflejo en las pupilas
    this.ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
    const highlightSize = pupilSize * 0.3;
    this.ctx.beginPath();
    this.ctx.arc(
      eyeX1 - highlightSize / 2,
      eyeY1 - highlightSize / 2,
      highlightSize,
      0,
      Math.PI * 2
    );
    this.ctx.arc(
      eyeX2 - highlightSize / 2,
      eyeY2 - highlightSize / 2,
      highlightSize,
      0,
      Math.PI * 2
    );
    this.ctx.fill();

    // Draw food
    const pulseSize = 2 + this.foodPulse;
    if (this.food.isSpecial) {
      // Manzana especial dorada
      this.ctx.save();
      this.ctx.translate(
        this.food.x * this.gridSize + this.gridSize / 2,
        this.food.y * this.gridSize + this.gridSize / 2
      );
      this.ctx.rotate((this.foodRotation * Math.PI) / 180);

      // Brillo
      const glowGradient = this.ctx.createRadialGradient(
        0,
        0,
        0,
        0,
        0,
        this.gridSize
      );
      glowGradient.addColorStop(0, "rgba(255, 215, 0, 0.8)");
      glowGradient.addColorStop(1, "rgba(255, 215, 0, 0)");
      this.ctx.fillStyle = glowGradient;
      this.ctx.beginPath();
      this.ctx.arc(0, 0, this.gridSize, 0, Math.PI * 2);
      this.ctx.fill();

      // Manzana dorada
      const gradient = this.ctx.createRadialGradient(
        0,
        0,
        0,
        0,
        0,
        this.gridSize / 2
      );
      gradient.addColorStop(0, "#FFD700");
      gradient.addColorStop(0.5, "#FFA500");
      gradient.addColorStop(1, "#FF8C00");
      this.ctx.fillStyle = gradient;
      this.ctx.shadowColor = "#FFD700";
      this.ctx.shadowBlur = 20;

      // Dibujar la manzana
      this.drawApple(0, 0, this.gridSize / 2 - pulseSize);

      this.ctx.restore();
    } else {
      // Manzana normal
      this.ctx.save();
      this.ctx.translate(
        this.food.x * this.gridSize + this.gridSize / 2,
        this.food.y * this.gridSize + this.gridSize / 2
      );

      // Brillo
      const glowGradient = this.ctx.createRadialGradient(
        0,
        0,
        0,
        0,
        0,
        this.gridSize
      );
      glowGradient.addColorStop(0, "rgba(231, 76, 60, 0.8)");
      glowGradient.addColorStop(1, "rgba(231, 76, 60, 0)");
      this.ctx.fillStyle = glowGradient;
      this.ctx.beginPath();
      this.ctx.arc(0, 0, this.gridSize, 0, Math.PI * 2);
      this.ctx.fill();

      // Manzana roja
      const gradient = this.ctx.createRadialGradient(
        0,
        0,
        0,
        0,
        0,
        this.gridSize / 2
      );
      gradient.addColorStop(0, "#E74C3C");
      gradient.addColorStop(0.5, "#C0392B");
      gradient.addColorStop(1, "#A93226");
      this.ctx.fillStyle = gradient;
      this.ctx.shadowColor = "#E74C3C";
      this.ctx.shadowBlur = 15;

      // Dibujar la manzana
      this.drawApple(0, 0, this.gridSize / 2 - pulseSize);

      this.ctx.restore();
    }
    this.ctx.shadowBlur = 0;
  }

  drawApple(x, y, size) {
    // Dibujar el cuerpo de la manzana
    this.ctx.beginPath();
    this.ctx.arc(x, y, size, 0, Math.PI * 2);
    this.ctx.fill();

    // Dibujar el tallo
    this.ctx.strokeStyle = "#2C3E50";
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    this.ctx.moveTo(x, y - size);
    this.ctx.quadraticCurveTo(
      x + size / 2,
      y - size - 5,
      x + size / 2,
      y - size
    );
    this.ctx.stroke();

    // Dibujar la hoja
    this.ctx.fillStyle = "#27AE60";
    this.ctx.beginPath();
    this.ctx.ellipse(
      x + size / 2,
      y - size,
      size / 4,
      size / 2,
      Math.PI / 4,
      0,
      Math.PI * 2
    );
    this.ctx.fill();
  }

  formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, "0")}:${remainingSeconds
      .toString()
      .padStart(2, "0")}`;
  }

  gameLoop(currentTime) {
    if (this.lastRenderTime === 0) {
      this.lastRenderTime = currentTime;
    }

    const elapsed = currentTime - this.lastRenderTime;

    if (elapsed > this.speed) {
      this.update();
      this.draw();
      this.lastRenderTime = currentTime;
    }

    if (!this.gameOver) {
      requestAnimationFrame(this.gameLoop.bind(this));
    }
  }

  async start() {
    this.gameOver = false;
    this.snake = [{ x: 5, y: 5 }];
    this.direction = "right";
    this.nextDirection = "right";
    this.score = 0;
    this.speed = 200;
    this.food = await this.generateFood();
    this.generateObstacles(); // Generar obstáculos al iniciar
    this.lastRenderTime = 0;
    this.startTime = Date.now();
    this.elapsedTime = 0;
    this.gameStarted = true;
    this.isSpecialMode = false;
    this.colorHue = 0;
    this.segmentHues = [];
    this.foodRotation = 0;

    // Resetear elementos del DOM
    this.scoreElement.textContent = "0";
    this.timeElement.textContent = "00:00";
    this.specialModeElement.style.display = "none";
    this.gameOverElement.style.display = "none";

    requestAnimationFrame(this.gameLoop.bind(this));

    // Iniciar monitoreo del sistema
    this.iniciarMonitoreoSistema();
  }

  iniciarMonitoreoSistema() {
    if (this.monitoreoActivo) return;

    this.monitoreoActivo = true;

    // Simular monitoreo de CPU y RAM (en un caso real, esto vendría del sistema)
    setInterval(() => {
      const cpu = Math.random() * 100; // Simulación de uso de CPU
      const ram = Math.random() * 100; // Simulación de uso de RAM

      this.actualizarEstadoNodo(cpu, ram);
    }, 5000); // Actualizar cada 5 segundos, pero solo si hay cambios significativos
  }
}

// Initialize game when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("gameCanvas");
  const game = new SnakeGame(canvas);

  // Handle keyboard controls (WASD)
  document.addEventListener("keydown", (e) => {
    if (!game.gameStarted) return;

    switch (e.key.toLowerCase()) {
      case "w":
        if (game.direction !== "down") game.nextDirection = "up";
        break;
      case "s":
        if (game.direction !== "up") game.nextDirection = "down";
        break;
      case "a":
        if (game.direction !== "right") game.nextDirection = "left";
        break;
      case "d":
        if (game.direction !== "left") game.nextDirection = "right";
        break;
    }
  });

  // Handle button controls
  document.getElementById("startBtn").addEventListener("click", async () => {
    await game.start();
  });

  document
    .getElementById("playAgainBtn")
    .addEventListener("click", async () => {
      await game.start();
    });

  // Iniciar el monitoreo del servidor
  fetch("/iniciar-monitoreo")
    .then((response) => response.text())
    .then((data) => console.log(data))
    .catch((error) => console.error("Error al iniciar monitoreo:", error));
});
