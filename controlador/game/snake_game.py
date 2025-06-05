import random
from typing import List, Tuple, Dict

class SnakeGame:
    def __init__(self, width: int = 20, height: int = 20):
        self.width = width
        self.height = height
        self.reset_game()

    def reset_game(self) -> None:
        """Reinicia el juego a su estado inicial"""
        self.snake = [(self.width // 2, self.height // 2)]
        self.direction = (1, 0)  # Comienza moviéndose a la derecha
        self.food = self._generate_food()
        self.score = 0
        self.game_over = False

    def _generate_food(self) -> Tuple[int, int]:
        """Genera comida en una posición aleatoria"""
        while True:
            food = (random.randint(0, self.width - 1), 
                   random.randint(0, self.height - 1))
            if food not in self.snake:
                return food

    def move(self) -> Dict:
        """Mueve la serpiente y actualiza el estado del juego"""
        if self.game_over:
            return self._get_game_state()

        # Calcular nueva posición de la cabeza
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], 
                   head[1] + self.direction[1])

        # Verificar colisiones con paredes
        if (new_head[0] < 0 or new_head[0] >= self.width or
            new_head[1] < 0 or new_head[1] >= self.height):
            self.game_over = True
            return self._get_game_state()

        # Verificar colisiones con la serpiente
        if new_head in self.snake:
            self.game_over = True
            return self._get_game_state()

        # Mover la serpiente
        self.snake.insert(0, new_head)

        # Verificar si come la comida
        if new_head == self.food:
            self.score += 10
            self.food = self._generate_food()
        else:
            self.snake.pop()

        return self._get_game_state()

    def change_direction(self, new_direction: Tuple[int, int]) -> None:
        """Cambia la dirección de la serpiente"""
        # Evitar que la serpiente se mueva en dirección opuesta
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def _get_game_state(self) -> Dict:
        """Retorna el estado actual del juego"""
        return {
            'snake': self.snake,
            'food': self.food,
            'score': self.score,
            'game_over': self.game_over
        }

    def draw(self):
        """
        Dibuja el juego
        """
        self.screen.fill((0, 0, 0))
        
        # Dibujar serpiente
        for segment in self.snake:
            pygame.draw.rect(self.screen, (0, 255, 0),
                           (segment[0], segment[1], self.grid_size, self.grid_size))
        
        # Dibujar comida
        pygame.draw.rect(self.screen, (255, 0, 0),
                        (self.food[0], self.food[1], self.grid_size, self.grid_size))
        
        # Dibujar puntuación
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
    
    def run(self):
        """
        Ejecuta el juego
        """
        clock = pygame.time.Clock()
        
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.change_direction((0, -self.grid_size))
                    elif event.key == pygame.K_DOWN:
                        self.change_direction((0, self.grid_size))
                    elif event.key == pygame.K_LEFT:
                        self.change_direction((-self.grid_size, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.change_direction((self.grid_size, 0))
            
            self.move()
            self.draw()
            clock.tick(10)
        
        pygame.quit()
        return self.score 