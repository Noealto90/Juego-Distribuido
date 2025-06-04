import pygame
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from controlador.agente_reutilizable import actualizar_estado

class SnakeGame:
    def __init__(self, game_id):
        self.game_id = game_id
        self.width = 800
        self.height = 600
        self.grid_size = 20
        self.snake = [(self.width//2, self.height//2)]
        self.direction = (self.grid_size, 0)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        
        # Inicializar Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(f"Snake Game - {game_id}")
        
    def generate_food(self):
        """
        Genera comida en una posición aleatoria
        """
        while True:
            x = random.randrange(0, self.width, self.grid_size)
            y = random.randrange(0, self.height, self.grid_size)
            if (x, y) not in self.snake:
                return (x, y)
    
    def move(self):
        """
        Mueve la serpiente
        """
        if self.game_over:
            return
            
        # Calcular nueva posición
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Verificar colisiones
        if (new_head[0] < 0 or new_head[0] >= self.width or
            new_head[1] < 0 or new_head[1] >= self.height or
            new_head in self.snake):
            self.game_over = True
            actualizar_estado(self.game_id, "terminado", {"puntuacion": self.score})
            return
        
        # Mover serpiente
        self.snake.insert(0, new_head)
        
        # Verificar si come
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
            actualizar_estado(self.game_id, "activo", {"puntuacion": self.score})
        else:
            self.snake.pop()
    
    def change_direction(self, new_direction):
        """
        Cambia la dirección de la serpiente
        """
        # Evitar movimiento en dirección opuesta
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction
    
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