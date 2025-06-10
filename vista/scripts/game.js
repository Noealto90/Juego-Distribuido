class GameClient {
  constructor() {
    this.canvas = document.getElementById("gameCanvas");
    this.ctx = this.canvas.getContext("2d");
    this.score = 0;
    this.gameId = null;
    this.playerId = null;
    this.isRunning = false;
    this.isPaused = false;

    // Configuración del juego
    this.gridSize = 20;
    this.snake = [];
    this.food = null;
    this.direction = "right";

    // Inicializar controles
    this.initializeControls();

    // Inicializar WebSocket
    this.initializeWebSocket();
  }

  initializeControls() {
    document
      .getElementById("startButton")
      .addEventListener("click", () => this.startGame());
    document
      .getElementById("pauseButton")
      .addEventListener("click", () => this.togglePause());

    document.addEventListener("keydown", (e) => this.handleKeyPress(e));
  }

  initializeWebSocket() {
    this.ws = new WebSocket("ws://localhost:5000/ws");

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleWebSocketMessage(data);
    };

    this.ws.onclose = () => {
      console.log("WebSocket cerrado");
      setTimeout(() => this.initializeWebSocket(), 1000);
    };
  }

  startGame() {
    if (!this.isRunning) {
      this.isRunning = true;
      this.score = 0;
      this.snake = [
        { x: 5, y: 5 },
        { x: 4, y: 5 },
        { x: 3, y: 5 },
      ];
      this.direction = "right";
      this.generateFood();
      this.gameLoop();

      // Crear nueva partida
      fetch("/crear-juego/" + this.playerId, {
        method: "POST",
      })
        .then((response) => response.json())
        .then((data) => {
          this.gameId = data.game_id;
        });
    }
  }

  togglePause() {
    this.isPaused = !this.isPaused;
    if (!this.isPaused) {
      this.gameLoop();
    }
  }

  handleKeyPress(e) {
    const key = e.key.toLowerCase();

    if (key === "arrowup" && this.direction !== "down") {
      this.direction = "up";
    } else if (key === "arrowdown" && this.direction !== "up") {
      this.direction = "down";
    } else if (key === "arrowleft" && this.direction !== "right") {
      this.direction = "left";
    } else if (key === "arrowright" && this.direction !== "left") {
      this.direction = "right";
    }
  }

  generateFood() {
    const maxX = this.canvas.width / this.gridSize - 1;
    const maxY = this.canvas.height / this.gridSize - 1;

    this.food = {
      x: Math.floor(Math.random() * maxX),
      y: Math.floor(Math.random() * maxY),
    };

    // Verificar que la comida no esté sobre la serpiente
    while (
      this.snake.some(
        (segment) => segment.x === this.food.x && segment.y === this.food.y
      )
    ) {
      this.food = {
        x: Math.floor(Math.random() * maxX),
        y: Math.floor(Math.random() * maxY),
      };
    }
  }

  moveSnake() {
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

    // Verificar colisiones
    if (this.checkCollision(head)) {
      this.gameOver();
      return;
    }

    this.snake.unshift(head);

    // Verificar si come
    if (head.x === this.food.x && head.y === this.food.y) {
      this.score += 10;
      this.generateFood();
      this.updateScore();
    } else {
      this.snake.pop();
    }
  }

  checkCollision(head) {
    // Colisión con paredes
    if (
      head.x < 0 ||
      head.x >= this.canvas.width / this.gridSize ||
      head.y < 0 ||
      head.y >= this.canvas.height / this.gridSize
    ) {
      return true;
    }

    // Colisión con la serpiente
    return this.snake.some(
      (segment) => segment.x === head.x && segment.y === head.y
    );
  }

  gameOver() {
    this.isRunning = false;
    this.ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    this.ctx.fillStyle = "white";
    this.ctx.font = "48px Arial";
    this.ctx.textAlign = "center";
    this.ctx.fillText(
      "Game Over",
      this.canvas.width / 2,
      this.canvas.height / 2
    );

    // Finalizar partida
    if (this.gameId) {
      fetch("/terminar-juego/" + this.gameId, {
        method: "POST",
      });
    }
  }

  updateScore() {
    document.getElementById("score").textContent = this.score;

    // Enviar actualización al servidor
    if (this.gameId) {
      this.ws.send(
        JSON.stringify({
          type: "score_update",
          game_id: this.gameId,
          score: this.score,
        })
      );
    }
  }

  draw() {
    // Limpiar canvas
    this.ctx.fillStyle = "black";
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Dibujar serpiente
    this.ctx.fillStyle = "lime";
    this.snake.forEach((segment) => {
      this.ctx.fillRect(
        segment.x * this.gridSize,
        segment.y * this.gridSize,
        this.gridSize - 2,
        this.gridSize - 2
      );
    });

    // Dibujar comida
    this.ctx.fillStyle = "red";
    this.ctx.fillRect(
      this.food.x * this.gridSize,
      this.food.y * this.gridSize,
      this.gridSize - 2,
      this.gridSize - 2
    );
  }

  gameLoop() {
    if (!this.isRunning || this.isPaused) return;

    this.moveSnake();
    this.draw();

    setTimeout(() => this.gameLoop(), 100);
  }

  handleWebSocketMessage(data) {
    switch (data.type) {
      case "game_state":
        // Actualizar estado del juego
        break;
      case "leaderboard":
        this.updateLeaderboard(data.players);
        break;
    }
  }

  updateLeaderboard(players) {
    const leaderboardList = document.getElementById("leaderboardList");
    leaderboardList.innerHTML = "";

    players.forEach((player) => {
      const item = document.createElement("div");
      item.className = "leaderboard-item";
      item.innerHTML = `
                <span>${player.nombre}</span>
                <span>${player.puntuacion_maxima}</span>
            `;
      leaderboardList.appendChild(item);
    });
  }
}

// Inicializar el juego cuando se carga la página
window.addEventListener("load", () => {
  const game = new GameClient();
});
