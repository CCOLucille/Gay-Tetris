import pygame
import asyncio
import random

# Initialize Pygame
pygame.init()

# Constants
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)  # Extra space for next piece
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        
        self.clock = pygame.time.Clock()
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_color = None
        
        self.next_piece = None
        self.next_color = None
        
        self.score = 0
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 0.5  # Seconds between automatic falling
        
        self.new_piece()

    def new_piece(self):
        if self.next_piece is None:
            shape_idx = random.randint(0, len(SHAPES) - 1)
            self.next_piece = SHAPES[shape_idx]
            self.next_color = COLORS[shape_idx]
        
        self.current_piece = self.next_piece
        self.current_color = self.next_color
        
        shape_idx = random.randint(0, len(SHAPES) - 1)
        self.next_piece = SHAPES[shape_idx]
        self.next_color = COLORS[shape_idx]
        
        self.current_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0
        
        if self.check_collision():
            self.game_over = True

    def check_collision(self):
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    if (self.current_y + y >= GRID_HEIGHT or
                        self.current_x + x < 0 or
                        self.current_x + x >= GRID_WIDTH or
                        self.grid[self.current_y + y][self.current_x + x] != BLACK):
                        return True
        return False

    def lock_piece(self):
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_y + y][self.current_x + x] = self.current_color
        
        self.clear_lines()
        self.new_piece()

    def clear_lines(self):
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(cell != BLACK for cell in self.grid[y]):
                lines_cleared += 1
                del self.grid[y]
                self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
            else:
                y -= 1
        
        self.score += lines_cleared * 100

    def rotate_piece(self):
        rotated = list(zip(*self.current_piece[::-1]))
        old_piece = self.current_piece
        self.current_piece = rotated
        
        if self.check_collision():
            self.current_piece = old_piece

    async def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.current_x -= 1
            if self.check_collision():
                self.current_x += 1
        
        if keys[pygame.K_RIGHT]:
            self.current_x += 1
            if self.check_collision():
                self.current_x -= 1
        
        if keys[pygame.K_DOWN]:
            self.current_y += 1
            if self.check_collision():
                self.current_y -= 1
                self.lock_piece()
        
        if keys[pygame.K_UP]:
            self.rotate_piece()

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw grid
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                if color != BLACK:
                    pygame.draw.rect(self.screen, color,
                                   (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))
        
        # Draw current piece
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.current_color,
                                   ((self.current_x + x) * BLOCK_SIZE,
                                    (self.current_y + y) * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))
        
        # Draw next piece preview
        preview_x = GRID_WIDTH * BLOCK_SIZE + BLOCK_SIZE
        preview_y = BLOCK_SIZE
        
        for y, row in enumerate(self.next_piece):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.next_color,
                                   (preview_x + x * BLOCK_SIZE,
                                    preview_y + y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + BLOCK_SIZE, 
                                    BLOCK_SIZE * 6))
        
        pygame.display.flip()

    async def game_loop(self):
        last_fall = pygame.time.get_ticks()
        
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
            
            await self.handle_input()
            
            current_time = pygame.time.get_ticks()
            if current_time - last_fall > self.fall_speed * 1000:
                self.current_y += 1
                if self.check_collision():
                    self.current_y -= 1
                    self.lock_piece()
                last_fall = current_time
            
            self.draw()
            
            self.clock.tick(60)
            await asyncio.sleep(0)  # Required for web deployment
        
        # Game Over screen
        font = pygame.font.Font(None, 48)
        game_over_text = font.render('Game Over!', True, WHITE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        self.screen.blit(game_over_text, text_rect)
        pygame.display.flip()
        
        await asyncio.sleep(2)  # Show game over for 2 seconds

async def main():
    game = Tetris()
    await game.game_loop()

# Run the game
asyncio.run(main())