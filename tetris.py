import pygame
import random
import math
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
BLOCK_SIZE = 30
GRID_WIDTH = 12
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Movement timing
AUTO_REPEAT_DELAY = 200  # milliseconds before movement starts repeating
AUTO_REPEAT_RATE = 50    # milliseconds between movements when key is held

# Colors - Now with more sparkle! ✨
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PINK = (255, 182, 193)
HOT_PINK = (255, 105, 180)
PURPLE = (147, 112, 219)
CYAN = (0, 255, 255)
RAINBOW_COLORS = [
    (255, 105, 180),  # Hot Pink
    (255, 20, 147),   # Deep Pink
    (255, 0, 255),    # Magenta
    (138, 43, 226),   # Blue Violet
    (75, 0, 130),     # Indigo
    (0, 191, 255),    # Deep Sky Blue
    (0, 255, 255),    # Cyan
]

# Sparkle colors
SPARKLE_COLORS = [
    (255, 255, 255),  # White sparkle
    (255, 215, 0),    # Gold sparkle
    (255, 192, 203),  # Pink sparkle
]

# Tetris shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

class Sparkle:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.lifetime = random.randint(10, 30)
        self.color = random.choice(SPARKLE_COLORS)
        self.size = random.randint(2, 4)

    def update(self):
        self.lifetime -= 1
        return self.lifetime > 0

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("✨Fabulous Tetris✨")
        self.clock = pygame.time.Clock()
        self.reset_game()
        
    def reset_game(self):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.game_over = False
        self.score = 0
        self.fall_time = 0
        self.normal_fall_speed = 500
        self.fast_fall_speed = self.normal_fall_speed // 10
        self.fall_speed = self.normal_fall_speed
        self.left_press_time = 0
        self.right_press_time = 0
        self.left_last_move = 0
        self.right_last_move = 0
        self.keys_held = {'left': False, 'right': False}
        self.sparkles: List[Sparkle] = []
        self.rainbow_offset = 0
        self.new_piece()

    def new_piece(self):
        """Create a new piece at the top of the grid."""
        shape_idx = random.randint(0, len(SHAPES) - 1)
        self.current_piece = {
            'shape': SHAPES[shape_idx],
            'color': random.choice(RAINBOW_COLORS),
            'x': GRID_WIDTH // 2 - len(SHAPES[shape_idx][0]) // 2,
            'y': -len(SHAPES[shape_idx])  # Start above the grid
        }
        # Check if the new piece can be placed
        if not self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
            self.game_over = True
        else:
            self.add_sparkles(self.current_piece['x'] * BLOCK_SIZE, 0, 5)

    def valid_move(self, piece, new_x: int, new_y: int) -> bool:
        """Check if a piece can be moved to the given position."""
        shape_matrix = piece['shape']
        for i, row in enumerate(shape_matrix):
            for j, cell in enumerate(row):
                if cell:
                    grid_x = new_x + j
                    grid_y = new_y + i
                    
                    # Check boundaries
                    if (grid_x < 0 or grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT):
                        return False
                    
                    # Allow movement above the grid
                    if grid_y < 0:
                        continue
                    
                    # Check collision with placed pieces
                    if self.grid[grid_y][grid_x] != BLACK:
                        return False
        return True

    def rotate_matrix(self, matrix: List[List[int]], clockwise: bool = True) -> List[List[int]]:
        """Rotate a matrix clockwise or counterclockwise."""
        if clockwise:
            return [[matrix[j][i] for j in range(len(matrix)-1, -1, -1)]
                    for i in range(len(matrix[0]))]
        else:
            return [[matrix[j][i] for j in range(len(matrix))]
                    for i in range(len(matrix[0])-1, -1, -1)]

    def rotate_piece(self, clockwise: bool = True):
        """Attempt to rotate the current piece."""
        if not self.current_piece:
            return
            
        # Create a copy of the current piece
        new_piece = self.current_piece.copy()
        new_piece['shape'] = self.rotate_matrix(self.current_piece['shape'], clockwise)
        
        # Try normal rotation
        if self.valid_move(new_piece, new_piece['x'], new_piece['y']):
            self.current_piece = new_piece
            self.add_sparkles(self.current_piece['x'] * BLOCK_SIZE,
                            self.current_piece['y'] * BLOCK_SIZE, 5)
            return
            
        # Wall kick attempts
        kicks = [-1, 1, -2, 2]  # Try these horizontal offsets
        for kick in kicks:
            if self.valid_move(new_piece, new_piece['x'] + kick, new_piece['y']):
                new_piece['x'] += kick
                self.current_piece = new_piece
                self.add_sparkles(self.current_piece['x'] * BLOCK_SIZE,
                                self.current_piece['y'] * BLOCK_SIZE, 5)
                return

    def rotate_piece_clockwise(self):
        self.rotate_piece(True)

    def rotate_piece_counterclockwise(self):
        self.rotate_piece(False)

    def move_left(self):
        """Move the current piece left if possible."""
        if (self.current_piece and 
            self.valid_move(self.current_piece,
                          self.current_piece['x'] - 1,
                          self.current_piece['y'])):
            self.current_piece['x'] -= 1
            self.add_sparkles(self.current_piece['x'] * BLOCK_SIZE,
                            self.current_piece['y'] * BLOCK_SIZE, 2)

    def move_right(self):
        """Move the current piece right if possible."""
        if (self.current_piece and 
            self.valid_move(self.current_piece,
                          self.current_piece['x'] + 1,
                          self.current_piece['y'])):
            self.current_piece['x'] += 1
            self.add_sparkles(self.current_piece['x'] * BLOCK_SIZE,
                            self.current_piece['y'] * BLOCK_SIZE, 2)

    def hard_drop(self):
        """Drop the piece to the lowest possible position."""
        if not self.current_piece:
            return
            
        while self.valid_move(self.current_piece,
                            self.current_piece['x'],
                            self.current_piece['y'] + 1):
            self.current_piece['y'] += 1
            self.add_sparkles(self.current_piece['x'] * BLOCK_SIZE,
                            self.current_piece['y'] * BLOCK_SIZE, 1)
        
        self.lock_piece()

    def lock_piece(self):
        """Lock the current piece in place and check for completed lines."""
        if not self.current_piece:
            return
            
        # Add the piece to the grid
        shape = self.current_piece['shape']
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    grid_y = self.current_piece['y'] + i
                    if grid_y >= 0:  # Only add cells that are within the grid
                        self.grid[grid_y][self.current_piece['x'] + j] = self.current_piece['color']
        
        # Check for completed lines
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(cell != BLACK for cell in self.grid[y]):
                # Add extra sparkles for line clear
                for x in range(GRID_WIDTH):
                    self.add_sparkles(x * BLOCK_SIZE, y * BLOCK_SIZE, 5)
                # Remove the line and add a new one at the top
                self.grid.pop(y)
                self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
                lines_cleared += 1
            else:
                y -= 1
        
        # Update score
        if lines_cleared > 0:
            self.score += (100 * lines_cleared) * lines_cleared  # Bonus for multiple lines
        
        # Create new piece
        self.new_piece()

    def add_sparkles(self, x: int, y: int, count: int = 3):
        """Add sparkle effects at the specified position."""
        for _ in range(count):
            sparkle_x = x + random.randint(-15, 15)
            sparkle_y = y + random.randint(-15, 15)
            self.sparkles.append(Sparkle(sparkle_x, sparkle_y))

    def update_sparkles(self):
        """Update and remove dead sparkles."""
        self.sparkles = [s for s in self.sparkles if s.update()]

    def get_rainbow_color(self, offset: int) -> Tuple[int, int, int]:
        """Generate a rainbow color based on the given offset."""
        hue = (offset % 360) / 360
        r = int(abs(math.sin(hue * 2 * math.pi)) * 255)
        g = int(abs(math.sin((hue + 1/3) * 2 * math.pi)) * 255)
        b = int(abs(math.sin((hue + 2/3) * 2 * math.pi)) * 255)
        return (r, g, b)

    def handle_movement(self, current_time):
        """Handle continuous movement when keys are held."""
        keys = pygame.key.get_pressed()
        
        # Handle left movement
        if keys[pygame.K_LEFT]:
            if not self.keys_held['left']:
                self.move_left()
                self.left_press_time = current_time
                self.keys_held['left'] = True
            elif current_time - self.left_press_time >= AUTO_REPEAT_DELAY:
                if current_time - self.left_last_move >= AUTO_REPEAT_RATE:
                    self.move_left()
                    self.left_last_move = current_time
        else:
            self.keys_held['left'] = False
            
        # Handle right movement
        if keys[pygame.K_RIGHT]:
            if not self.keys_held['right']:
                self.move_right()
                self.right_press_time = current_time
                self.keys_held['right'] = True
            elif current_time - self.right_press_time >= AUTO_REPEAT_DELAY:
                if current_time - self.right_last_move >= AUTO_REPEAT_RATE:
                    self.move_right()
                    self.right_last_move = current_time
        else:
            self.keys_held['right'] = False
            
    def clamp_color(self, color: Tuple[int, int, int], shimmer: int) -> Tuple[int, int, int]:
        """
        Clamp color values to valid RGB range (0-255).
        
        Args:
            color: Original RGB color tuple
            shimmer: Shimmer value to add
            
        Returns:
            Tuple[int, int, int]: Valid RGB color values
        """
        return tuple(max(0, min(255, c + shimmer)) for c in color)

    def draw(self):
        """Draw the game state to the screen."""
        # Update rainbow effect
        self.rainbow_offset = (self.rainbow_offset + 1) % 360
        
        # Fill with gradient background
        for y in range(SCREEN_HEIGHT):
            color = self.get_rainbow_color((self.rainbow_offset + y) % 360)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        # Draw grid
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                color = self.grid[i][j]
                if color != BLACK:
                    # Add shimmer effect to placed blocks
                    shimmer = int(20 * math.sin((self.rainbow_offset + i * j) / 10))
                    shimmer_color = self.clamp_color(color, shimmer)
                    
                    # Ensure x and y are valid integers
                    x = j * BLOCK_SIZE
                    y = i * BLOCK_SIZE
                    
                    try:
                        pygame.draw.rect(
                            self.screen,
                            shimmer_color,
                            (x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                        )
                        
                        if random.random() < 0.01:
                            self.add_sparkles(x, y)
                    except ValueError as e:
                        # Skip drawing this block if there's still an error
                        continue

        # Draw current piece
        if self.current_piece:
            for i, row in enumerate(self.current_piece['shape']):
                for j, cell in enumerate(row):
                    if cell:
                        x = (self.current_piece['x'] + j) * BLOCK_SIZE
                        y = (self.current_piece['y'] + i) * BLOCK_SIZE
                        if y >= 0:  # Only draw if visible
                            shimmer = int(30 * math.sin(self.rainbow_offset / 10))
                            shimmer_color = self.clamp_color(
                                self.current_piece['color'],
                                shimmer
                            )
                            
                            try:
                                pygame.draw.rect(
                                    self.screen,
                                    shimmer_color,
                                    (x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                                )
                                
                                if random.random() < 0.05:
                                    self.add_sparkles(x, y)
                            except ValueError as e:
                                # Skip drawing this block if there's still an error
                                continue

        # Draw sparkles
        for sparkle in self.sparkles:
            try:
                pygame.draw.circle(
                    self.screen,
                    sparkle.color,
                    (int(sparkle.x), int(sparkle.y)),
                    sparkle.size
                )
            except ValueError:
                continue

        # Draw score with fabulous gradient
        font = pygame.font.Font(None, 36)
        score_text = f'Score: {self.score}'
        for i, char in enumerate(score_text):
            color = self.get_rainbow_color((self.rainbow_offset + i * 20) % 360)
            text_surface = font.render(char, True, color)
            self.screen.blit(text_surface, (GRID_WIDTH * BLOCK_SIZE + 10 + i * 15, 10))

        # Draw controls with sparkly effect
        controls_font = pygame.font.Font(None, 24)
        controls = [
            "✨Controls:✨",
            "W/Up: Hard Drop",
            "Left/Right: Move",
            "A: Rotate CW",
            "D: Rotate CCW",
            "S/Down: Fast Fall"
        ]
        for i, text in enumerate(controls):
            color = self.get_rainbow_color((self.rainbow_offset + i * 30) % 360)
            control_text = controls_font.render(text, True, color)
            self.screen.blit(control_text, (GRID_WIDTH * BLOCK_SIZE + 10, 100 + i * 25))

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while not self.game_over:
            self.clock.tick(60)
            current_time = pygame.time.get_ticks()

            # Update sparkles
            self.update_sparkles()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.rotate_piece_clockwise()
                    if event.key == pygame.K_d:
                        self.rotate_piece_counterclockwise()
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.hard_drop()
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.fall_speed = self.fast_fall_speed
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.fall_speed = self.normal_fall_speed

            # Handle continuous movement
            self.handle_movement(current_time)

            # Handle piece falling
            if current_time - self.fall_time > self.fall_speed:
                self.fall_time = current_time
                if self.current_piece and self.valid_move(
                    self.current_piece,
                    self.current_piece['x'],
                    self.current_piece['y'] + 1
                ):
                    self.current_piece['y'] += 1
                else:
                    self.lock_piece()

            self.draw()

        # Fabulous game over screen
        font = pygame.font.Font(None, 48)
        for i in range(50):  # Animate game over text
            self.screen.fill(BLACK)
            color = self.get_rainbow_color(self.rainbow_offset + i)
            game_over_text = font.render('Game Over!', True, color)
            score_text = font.render(f'Final Score: {self.score}', True, color)
            self.screen.blit(game_over_text, 
                           (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(score_text, 
                           (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 30))
            # Add lots of sparkles
            self.add_sparkles(random.randint(0, SCREEN_WIDTH), 
                            random.randint(0, SCREEN_HEIGHT))
            self.update_sparkles()
            for sparkle in self.sparkles:
                pygame.draw.circle(self.screen, sparkle.color, 
                                 (sparkle.x, sparkle.y), sparkle.size)
            pygame.display.flip()
            pygame.time.wait(50)
        
        # Wait for a moment before closing
        pygame.time.wait(2000)

if __name__ == '__main__':
    game = Tetris()
    game.run()
    pygame.quit()