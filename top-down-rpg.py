import pygame
import sys
from pygame.locals import *
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLAYER_SPEED = 5

# Mini-map constants
MINIMAP_WIDTH = 150
MINIMAP_HEIGHT = 150
MINIMAP_MARGIN = 10
MINIMAP_SCALE = 0.2  # Scale factor for the mini-map
MINIMAP_PLAYER_SIZE = 4

# World size (for demonstration)
WORLD_WIDTH = 2000
WORLD_HEIGHT = 2000

# Landmark constants
NUM_TREES = 50
NUM_ROCKS = 30
NUM_HOUSES = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def apply(self, entity):
        return pygame.Rect(entity.rect.x + self.x, entity.rect.y + self.y, entity.rect.width, entity.rect.height)

    def update(self, target):
        # Center the camera on the target
        x = -target.rect.x + WINDOW_WIDTH // 2
        y = -target.rect.y + WINDOW_HEIGHT // 2
        
        # Limit scrolling to world size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(WORLD_WIDTH - WINDOW_WIDTH), x)  # right
        y = max(-(WORLD_HEIGHT - WINDOW_HEIGHT), y)  # bottom
        
        self.x = x
        self.y = y

class Landmark(pygame.sprite.Sprite):
    def __init__(self, x, y, landmark_type):
        super().__init__()
        self.landmark_type = landmark_type
        self.world_x = x
        self.world_y = y
        
        # Set up the landmark appearance based on type
        if landmark_type == 'tree':
            self.image = pygame.Surface((20, 20))
            self.image.fill(DARK_GREEN)
            self.minimap_color = DARK_GREEN
            self.minimap_size = 3
        elif landmark_type == 'rock':
            self.image = pygame.Surface((15, 15))
            self.image.fill(GRAY)
            self.minimap_color = GRAY
            self.minimap_size = 2
        elif landmark_type == 'house':
            self.image = pygame.Surface((40, 40))
            self.image.fill(BROWN)
            self.minimap_color = BROWN
            self.minimap_size = 4
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Temporary player rectangle (replace with sprite later)
        self.image = pygame.Surface((32, 32))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        
        # Set initial position
        self.rect.x = x
        self.rect.y = y
        self.world_x = x
        self.world_y = y
        
        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Stats
        self.health = 100
        self.max_health = 100
        self.stamina = 100
        self.max_stamina = 100

    def update(self):
        # Update world position
        new_world_x = self.world_x + self.velocity_x
        new_world_y = self.world_y + self.velocity_y
        
        # Check world boundaries
        if 0 <= new_world_x <= WORLD_WIDTH - self.rect.width:
            self.world_x = new_world_x
            self.rect.x = self.world_x
            
        if 0 <= new_world_y <= WORLD_HEIGHT - self.rect.height:
            self.world_y = new_world_y
            self.rect.y = self.world_y

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Top-Down RPG")
        self.clock = pygame.time.Clock()
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.landmarks = pygame.sprite.Group()
        
        # Create player at world center
        self.player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        self.all_sprites.add(self.player)
        
        # Create camera
        self.camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Create mini-map surface
        self.minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT))
        
        # Generate landmarks
        self.generate_landmarks()

    def generate_landmarks(self):
        # Generate trees
        for _ in range(NUM_TREES):
            x = random.randint(0, WORLD_WIDTH)
            y = random.randint(0, WORLD_HEIGHT)
            tree = Landmark(x, y, 'tree')
            self.landmarks.add(tree)
            self.all_sprites.add(tree)
            
        # Generate rocks
        for _ in range(NUM_ROCKS):
            x = random.randint(0, WORLD_WIDTH)
            y = random.randint(0, WORLD_HEIGHT)
            rock = Landmark(x, y, 'rock')
            self.landmarks.add(rock)
            self.all_sprites.add(rock)
            
        # Generate houses
        for _ in range(NUM_HOUSES):
            x = random.randint(0, WORLD_WIDTH)
            y = random.randint(0, WORLD_HEIGHT)
            house = Landmark(x, y, 'house')
            self.landmarks.add(house)
            self.all_sprites.add(house)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Reset velocity
        self.player.velocity_x = 0
        self.player.velocity_y = 0
        
        # Handle movement
        if keys[K_w] or keys[K_UP]:
            self.player.velocity_y = -PLAYER_SPEED
        if keys[K_s] or keys[K_DOWN]:
            self.player.velocity_y = PLAYER_SPEED
        if keys[K_a] or keys[K_LEFT]:
            self.player.velocity_x = -PLAYER_SPEED
        if keys[K_d] or keys[K_RIGHT]:
            self.player.velocity_x = PLAYER_SPEED
            
        # Normalize diagonal movement
        if self.player.velocity_x != 0 and self.player.velocity_y != 0:
            self.player.velocity_x *= 0.7071  # 1/√2
            self.player.velocity_y *= 0.7071

    def draw_hud(self):
        # Draw health bar
        pygame.draw.rect(self.screen, RED, (10, 10, 200, 20))
        health_width = (self.player.health / self.player.max_health) * 200
        pygame.draw.rect(self.screen, GREEN, (10, 10, health_width, 20))
        
        # Draw stamina bar
        pygame.draw.rect(self.screen, BLACK, (10, 40, 200, 20))
        stamina_width = (self.player.stamina / self.player.max_stamina) * 200
        pygame.draw.rect(self.screen, WHITE, (10, 40, stamina_width, 20))

    def draw_minimap(self):
        # Clear mini-map surface
        self.minimap_surface.fill(BLACK)
        
        # Draw world border
        pygame.draw.rect(self.minimap_surface, GRAY, (0, 0, MINIMAP_WIDTH, MINIMAP_HEIGHT), 1)
        
        # Draw landmarks on mini-map
        for landmark in self.landmarks:
            minimap_x = (landmark.world_x / WORLD_WIDTH) * MINIMAP_WIDTH
            minimap_y = (landmark.world_y / WORLD_HEIGHT) * MINIMAP_HEIGHT
            pygame.draw.rect(self.minimap_surface, landmark.minimap_color,
                           (minimap_x - landmark.minimap_size // 2,
                            minimap_y - landmark.minimap_size // 2,
                            landmark.minimap_size, landmark.minimap_size))
        
        # Calculate player position on mini-map
        minimap_x = (self.player.world_x / WORLD_WIDTH) * MINIMAP_WIDTH
        minimap_y = (self.player.world_y / WORLD_HEIGHT) * MINIMAP_HEIGHT
        
        # Draw player on mini-map
        pygame.draw.rect(self.minimap_surface, GREEN, 
                        (minimap_x - MINIMAP_PLAYER_SIZE // 2,
                         minimap_y - MINIMAP_PLAYER_SIZE // 2,
                         MINIMAP_PLAYER_SIZE, MINIMAP_PLAYER_SIZE))
        
        # Draw mini-map frame
        pygame.draw.rect(self.minimap_surface, WHITE, 
                        (0, 0, MINIMAP_WIDTH, MINIMAP_HEIGHT), 2)
        
        # Draw mini-map on screen (top-right corner)
        self.screen.blit(self.minimap_surface, 
                        (WINDOW_WIDTH - MINIMAP_WIDTH - MINIMAP_MARGIN,
                         MINIMAP_MARGIN))

    def draw_game_world(self):
        self.screen.fill(BLACK)
        
        # Draw all sprites with camera offset
        for sprite in self.all_sprites:
            screen_rect = self.camera.apply(sprite)
            self.screen.blit(sprite.image, screen_rect)

    def run(self):
        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    running = False
                    
            # Handle input
            self.handle_input()
            
            # Update
            self.all_sprites.update()
            self.camera.update(self.player)
            
            # Draw
            self.draw_game_world()
            self.draw_hud()
            self.draw_minimap()
            
            # Refresh display
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 