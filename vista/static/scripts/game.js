class SnakeGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = 20;
        this.gameLoop = null;
        this.gameSpeed = 150; // ms

        // Botones
        this.startBtn = document.getElementById('startBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.playAgainBtn = document.getElementById('playAgainBtn');
        this.gameOverDiv = document.getElementById('gameOver');

        // Event listeners
        this.startBtn.addEventListener('click', () => this.startGame());
        this.resetBtn.addEventListener('click', () => this.resetGame());
        this.playAgainBtn.addEventListener('click', () => this.resetGame());
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));

        // Inicializar el juego
        this.resetGame();
    }

    async startGame() {
        if (this.gameLoop) return;
        
        this.startBtn.disabled = true;
        this.gameLoop = setInterval(() => this.update(), this.gameSpeed);
    }

    async update() {
        try {
            const response = await fetch('/api/game/move', {
                method: 'POST'
            });
            const gameState = await response.json();
            this.draw(gameState);
            
            if (gameState.game_over) {
                this.endGame(gameState.score);
            }
        } catch (error) {
            console.error('Error updating game:', error);
        }
    }

    async resetGame() {
        try {
            const response = await fetch('/api/game/reset', {
                method: 'POST'
            });
            const gameState = await response.json();
            
            if (this.gameLoop) {
                clearInterval(this.gameLoop);
                this.gameLoop = null;
            }
            
            this.startBtn.disabled = false;
            this.gameOverDiv.style.display = 'none';
            this.draw(gameState);
        } catch (error) {
            console.error('Error resetting game:', error);
        }
    }

    async handleKeyPress(event) {
        if (!this.gameLoop) return;

        let direction;
        switch(event.key) {
            case 'ArrowUp':
                direction = [0, -1];
                break;
            case 'ArrowDown':
                direction = [0, 1];
                break;
            case 'ArrowLeft':
                direction = [-1, 0];
                break;
            case 'ArrowRight':
                direction = [1, 0];
                break;
            default:
                return;
        }

        try {
            await fetch('/api/game/direction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ direction })
            });
        } catch (error) {
            console.error('Error changing direction:', error);
        }
    }

    draw(gameState) {
        // Limpiar canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Dibujar serpiente
        this.ctx.fillStyle = '#4CAF50';
        gameState.snake.forEach(([x, y]) => {
            this.ctx.fillRect(
                x * this.gridSize,
                y * this.gridSize,
                this.gridSize - 1,
                this.gridSize - 1
            );
        });

        // Dibujar comida
        this.ctx.fillStyle = '#FF0000';
        const [foodX, foodY] = gameState.food;
        this.ctx.fillRect(
            foodX * this.gridSize,
            foodY * this.gridSize,
            this.gridSize - 1,
            this.gridSize - 1
        );

        // Actualizar puntuación
        document.getElementById('score').textContent = gameState.score;
    }

    endGame(score) {
        clearInterval(this.gameLoop);
        this.gameLoop = null;
        this.startBtn.disabled = false;
        this.gameOverDiv.style.display = 'block';
        document.getElementById('finalScore').textContent = score;
    }
}

// Inicializar el juego cuando se carga la página
window.addEventListener('load', () => {
    new SnakeGame();
}); 