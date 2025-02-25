import pygame
import sys
import math
from typing import List, Dict, Tuple
import json
import os

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Game settings
TILE_SIZE = 64
GRID_COLS = 16
GRID_ROWS = 10
SIDEBAR_WIDTH = 200

# Initialize fonts
pygame.font.init()
FONT_LARGE = pygame.font.Font(None, 48)
FONT_MEDIUM = pygame.font.Font(None, 36)
FONT_SMALL = pygame.font.Font(None, 24)

class Tower:
    def __init__(self, x: int, y: int, tower_type: dict):
        self.x = x
        self.y = y
        self.type = tower_type
        self.name = tower_type["name"]
        self.element = tower_type["element"]
        self.level = 1
        self.damage = 10  # Base damage, will be modified by element and level
        self.range = 150  # Base range in pixels
        self.attack_speed = 1.0  # Attacks per second
        self.last_attack_time = 0
        self.target = None
        self.upgrades = tower_type["upgrades"]
        
    def draw(self, screen: pygame.Surface):
        # Draw tower base
        pygame.draw.rect(screen, BLACK, (self.x - TILE_SIZE//2, self.y - TILE_SIZE//2, TILE_SIZE, TILE_SIZE))
        
        # Draw element indicator
        color = {
            "fire": RED,
            "ice": BLUE,
            "electricity": (255, 255, 0),  # Yellow
            "earth": (139, 69, 19)  # Brown
        }.get(self.element, WHITE)
        
        pygame.draw.circle(screen, color, (self.x, self.y), TILE_SIZE//3)
        
        # Draw range circle
        pygame.draw.circle(screen, color, (self.x, self.y), self.range, 1)
    
    def update(self, enemies: List["Enemy"], current_time: int):
        if not self.target or not self.target.is_alive:
            self.find_target(enemies)
            
        if self.target and current_time - self.last_attack_time > 1000 / self.attack_speed:
            self.attack(current_time)
    
    def find_target(self, enemies: List["Enemy"]):
        self.target = None
        shortest_dist = float('inf')
        
        for enemy in enemies:
            if not enemy.is_alive:
                continue
                
            dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if dist <= self.range and dist < shortest_dist:
                shortest_dist = dist
                self.target = enemy
    
    def attack(self, current_time: int):
        if self.target:
            self.target.take_damage(self.damage)
            self.last_attack_time = current_time

class Enemy:
    def __init__(self, enemy_type: dict, path: List[Tuple[int, int]]):
        self.type = enemy_type
        self.name = enemy_type["name"]
        self.path = path
        self.path_index = 0
        self.x, self.y = path[0]
        self.speed = 2
        self.health = 100
        self.max_health = 100
        self.is_alive = True
        
    def draw(self, screen: pygame.Surface):
        if not self.is_alive:
            return
            
        # Draw enemy body
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 20)
        
        # Draw health bar
        health_width = 40
        health_height = 5
        health_x = int(self.x - health_width/2)
        health_y = int(self.y - 30)
        
        # Background (red)
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
        # Foreground (green)
        current_health_width = (self.health / self.max_health) * health_width
        pygame.draw.rect(screen, GREEN, (health_x, health_y, current_health_width, health_height))
    
    def update(self):
        if not self.is_alive:
            return
            
        if self.path_index < len(self.path) - 1:
            target_x, target_y = self.path[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < self.speed:
                self.path_index += 1
                self.x, self.y = self.path[self.path_index]
            else:
                self.x += (dx/distance) * self.speed
                self.y += (dy/distance) * self.speed
    
    def take_damage(self, damage: float):
        self.health -= damage
        if self.health <= 0:
            self.is_alive = False

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Elemental Defenders")
        self.clock = pygame.time.Clock()
        
        # Load game data
        self.load_game_data()
        
        # Game state
        self.towers: List[Tower] = []
        self.enemies: List[Enemy] = []
        self.gold = 100
        self.lives = 20
        self.wave = 1
        self.selected_tower_type = None
        self.wave_timer = 0
        self.spawn_delay = 1000  # 1 second between enemy spawns
        self.last_spawn_time = 0
        self.enemies_to_spawn = []
        self.wave_in_progress = False
        
        # Create path
        self.path = self.create_path()
    
    def load_game_data(self):
        try:
            with open("templates/tower-defense/concept.json", "r") as f:
                data = json.load(f)
                self.tower_types = data["towers"]
                self.enemy_types = data["enemies"]
        except FileNotFoundError:
            print("Error: Could not load game data")
            sys.exit(1)
    
    def create_path(self) -> List[Tuple[int, int]]:
        # Create a simple path for now
        path = [
            (0, WINDOW_HEIGHT//2),
            (WINDOW_WIDTH//4, WINDOW_HEIGHT//2),
            (WINDOW_WIDTH//4, WINDOW_HEIGHT//4),
            (WINDOW_WIDTH//2, WINDOW_HEIGHT//4),
            (WINDOW_WIDTH//2, 3*WINDOW_HEIGHT//4),
            (3*WINDOW_WIDTH//4, 3*WINDOW_HEIGHT//4),
            (3*WINDOW_WIDTH//4, WINDOW_HEIGHT//2),
            (WINDOW_WIDTH - SIDEBAR_WIDTH, WINDOW_HEIGHT//2)
        ]
        return path
    
    def draw_path(self):
        if len(self.path) > 1:
            pygame.draw.lines(self.screen, GRAY, False, self.path, 20)
    
    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH - SIDEBAR_WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH - SIDEBAR_WIDTH, y))

    def draw_sidebar(self):
        # Draw sidebar background
        pygame.draw.rect(self.screen, BLACK, (WINDOW_WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
        
        # Draw game info
        gold_text = FONT_MEDIUM.render(f"Gold: {self.gold}", True, WHITE)
        lives_text = FONT_MEDIUM.render(f"Lives: {self.lives}", True, WHITE)
        wave_text = FONT_MEDIUM.render(f"Wave: {self.wave}", True, WHITE)
        
        self.screen.blit(gold_text, (WINDOW_WIDTH - SIDEBAR_WIDTH + 10, 10))
        self.screen.blit(lives_text, (WINDOW_WIDTH - SIDEBAR_WIDTH + 10, 50))
        self.screen.blit(wave_text, (WINDOW_WIDTH - SIDEBAR_WIDTH + 10, 90))

        # Draw tower selection
        y_offset = 150
        for i, tower in enumerate(self.tower_types):
            tower_rect = pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH + 10, y_offset + i * 80, SIDEBAR_WIDTH - 20, 70)
            color = BLUE if self.selected_tower_type == tower else GRAY
            pygame.draw.rect(self.screen, color, tower_rect)
            
            # Tower name
            name_text = FONT_SMALL.render(tower["name"], True, WHITE)
            self.screen.blit(name_text, (tower_rect.x + 5, tower_rect.y + 5))
            
            # Tower cost
            cost_text = FONT_SMALL.render(f"Cost: {50}", True, WHITE)  # Fixed cost for now
            self.screen.blit(cost_text, (tower_rect.x + 5, tower_rect.y + 35))

        # Draw start wave button if no wave in progress
        if not self.wave_in_progress and not self.enemies:
            wave_button = pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH + 10, WINDOW_HEIGHT - 60, SIDEBAR_WIDTH - 20, 50)
            pygame.draw.rect(self.screen, GREEN, wave_button)
            start_text = FONT_SMALL.render("Start Wave", True, BLACK)
            text_rect = start_text.get_rect(center=wave_button.center)
            self.screen.blit(start_text, text_rect)

    def handle_click(self, pos):
        x, y = pos
        
        # Check if click is in sidebar
        if x > WINDOW_WIDTH - SIDEBAR_WIDTH:
            # Check tower selection
            y_offset = 150
            for i, tower in enumerate(self.tower_types):
                tower_rect = pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH + 10, y_offset + i * 80, SIDEBAR_WIDTH - 20, 70)
                if tower_rect.collidepoint(pos):
                    self.selected_tower_type = tower
                    return

            # Check start wave button
            if not self.wave_in_progress and not self.enemies:
                wave_button = pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH + 10, WINDOW_HEIGHT - 60, SIDEBAR_WIDTH - 20, 50)
                if wave_button.collidepoint(pos):
                    self.start_wave()
                    return
        
        # Handle tower placement
        elif self.selected_tower_type and x < WINDOW_WIDTH - SIDEBAR_WIDTH:
            # Snap to grid
            grid_x = (x // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
            grid_y = (y // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
            
            # Check if we can place tower here
            if self.can_place_tower(grid_x, grid_y):
                tower_cost = 50  # Fixed cost for now
                if self.gold >= tower_cost:
                    self.towers.append(Tower(grid_x, grid_y, self.selected_tower_type))
                    self.gold -= tower_cost
                    self.selected_tower_type = None

    def can_place_tower(self, x, y):
        # Check if too close to path
        path_padding = 30
        for i in range(len(self.path) - 1):
            x1, y1 = self.path[i]
            x2, y2 = self.path[i + 1]
            
            # Calculate distance from point to line segment
            line_len = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            if line_len == 0:
                continue
                
            u = ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / (line_len * line_len)
            if u < 0:
                dist = math.sqrt((x - x1)**2 + (y - y1)**2)
            elif u > 1:
                dist = math.sqrt((x - x2)**2 + (y - y2)**2)
            else:
                dist = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / line_len
                
            if dist < path_padding:
                return False
        
        # Check if tower already exists here
        for tower in self.towers:
            if math.sqrt((tower.x - x)**2 + (tower.y - y)**2) < TILE_SIZE:
                return False
        
        return True

    def start_wave(self):
        self.wave_in_progress = True
        self.enemies_to_spawn = []
        
        # Create wave composition
        num_enemies = 5 + self.wave * 2  # Increase enemies per wave
        for _ in range(num_enemies):
            enemy_type = self.enemy_types[0]  # Start with basic enemies
            self.enemies_to_spawn.append(enemy_type)
        
        self.last_spawn_time = pygame.time.get_ticks()

    def update_wave(self, current_time):
        if not self.wave_in_progress:
            return
            
        # Spawn enemies
        if self.enemies_to_spawn and current_time - self.last_spawn_time > self.spawn_delay:
            enemy_type = self.enemies_to_spawn.pop(0)
            self.enemies.append(Enemy(enemy_type, self.path))
            self.last_spawn_time = current_time
            
        # Check if wave is complete
        if not self.enemies_to_spawn and not self.enemies:
            self.wave_in_progress = False
            self.wave += 1
            self.gold += 50  # Reward for completing wave

        # Remove enemies that reached the end
        for enemy in self.enemies[:]:
            if enemy.path_index >= len(enemy.path) - 1:
                self.enemies.remove(enemy)
                self.lives -= 1

    def run(self):
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            # Update
            self.update_wave(current_time)
            for tower in self.towers:
                tower.update(self.enemies, current_time)
            
            for enemy in self.enemies:
                enemy.update()
            
            # Check game over
            if self.lives <= 0:
                running = False
            
            # Draw
            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_path()
            
            for tower in self.towers:
                tower.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            self.draw_sidebar()
            
            # Draw selected tower preview
            if self.selected_tower_type:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if mouse_x < WINDOW_WIDTH - SIDEBAR_WIDTH:
                    grid_x = (mouse_x // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
                    grid_y = (mouse_y // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
                    
                    # Draw semi-transparent tower
                    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    pygame.draw.rect(s, (*BLACK, 128), (0, 0, TILE_SIZE, TILE_SIZE))
                    self.screen.blit(s, (grid_x - TILE_SIZE//2, grid_y - TILE_SIZE//2))
                    
                    # Draw range preview
                    if self.can_place_tower(grid_x, grid_y):
                        pygame.draw.circle(self.screen, (*BLUE, 128), (grid_x, grid_y), 150, 1)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 