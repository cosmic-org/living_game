import pygame
import sys
from pygame.locals import *
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
WORLD_WIDTH = 2000
WORLD_HEIGHT = 2000

# Player constants
PLAYER_SPEED = 5
PLAYER_SIZE = 32

# Mini-map constants
MINIMAP_WIDTH = 150
MINIMAP_HEIGHT = 150
MINIMAP_MARGIN = 10
MINIMAP_SCALE = 0.2
MINIMAP_PLAYER_SIZE = 4

# UI constants
TOP_BAR_HEIGHT = 60
UPGRADE_PANEL_WIDTH = 250

# Resource constants
NUM_RESOURCE_NODES = 100
RESOURCE_RESPAWN_TIME = 10000  # milliseconds
RESOURCE_SPAWN_INTERVAL = 5000  # Time between new resource spawns in milliseconds
MAX_RESOURCES = 150  # Maximum number of resources that can exist at once

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
GOLD = (255, 215, 0)

@dataclass
class Upgrade:
    name: str
    cost: int
    multiplier: float
    level: int = 0
    description: str = ""

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
        x = -target.rect.x + WINDOW_WIDTH // 2
        y = -target.rect.y + WINDOW_HEIGHT // 2
        
        x = min(0, x)
        y = min(0, y)
        x = max(-(WORLD_WIDTH - WINDOW_WIDTH), x)
        y = max(-(WORLD_HEIGHT - WINDOW_HEIGHT), y)
        
        self.x = x
        self.y = y

class ResourceNode(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(GOLD)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.world_x = x
        self.world_y = y
        self.value = 1
        self.active = True
        self.respawn_time = 0

    def collect(self, current_time):
        if self.active:
            self.active = False
            # Apply spawn time multiplier from the game instance
            game_instance = pygame.display.get_surface().get_parent()
            if isinstance(game_instance, Game):
                self.respawn_time = current_time + (RESOURCE_RESPAWN_TIME * game_instance.spawn_time_multiplier)
            else:
                self.respawn_time = current_time + RESOURCE_RESPAWN_TIME
            self.image.fill(GRAY)
            return self.value
        return 0

    def update(self, current_time):
        if not self.active and current_time >= self.respawn_time:
            self.active = True
            self.image.fill(GOLD)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        
        self.rect.x = x
        self.rect.y = y
        self.world_x = x
        self.world_y = y
        
        self.velocity_x = 0
        self.velocity_y = 0
        
        # RPG Stats
        self.health = 100
        self.max_health = 100
        self.stamina = 100
        self.max_stamina = 100
        
        # Incremental Stats
        self.resources = 0
        self.collection_range = 50
        self.collection_power = 1
        self.movement_speed = PLAYER_SPEED

    def update(self):
        new_world_x = self.world_x + (self.velocity_x * self.movement_speed)
        new_world_y = self.world_y + (self.velocity_y * self.movement_speed)
        
        if 0 <= new_world_x <= WORLD_WIDTH - self.rect.width:
            self.world_x = new_world_x
            self.rect.x = self.world_x
            
        if 0 <= new_world_y <= WORLD_HEIGHT - self.rect.height:
            self.world_y = new_world_y
            self.rect.y = self.world_y

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Incremental RPG")
        self.clock = pygame.time.Clock()
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.resource_nodes = pygame.sprite.Group()
        
        # Create player
        self.player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        self.all_sprites.add(self.player)
        
        # Create camera
        self.camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Create mini-map surface
        self.minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT))
        
        # Font setup
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Resource spawn timer
        self.last_spawn_time = pygame.time.get_ticks()
        
        # Upgrades
        self.upgrades: List[Upgrade] = [
            Upgrade("Movement Speed", 50, 1.2, description="Increase movement speed by 20%"),
            Upgrade("Collection Range", 100, 1.5, description="Increase resource collection range by 50%"),
            Upgrade("Collection Power", 150, 2, description="Double resource collection amount"),
            Upgrade("Spawn Speed", 200, 0.8, description="Reduce resource respawn time by 20%")
        ]
        
        # Resource spawn multiplier
        self.spawn_time_multiplier = 1.0
        
        # Generate world
        self.generate_world()

    def generate_world(self):
        # Clear existing resources
        self.resource_nodes.empty()
        
        # Generate initial resources
        for _ in range(NUM_RESOURCE_NODES):
            self.spawn_resource()

    def spawn_resource(self):
        if len(self.resource_nodes) < MAX_RESOURCES:
            x = random.randint(0, WORLD_WIDTH)
            y = random.randint(0, WORLD_HEIGHT)
            node = ResourceNode(x, y)
            self.resource_nodes.add(node)
            self.all_sprites.add(node)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        self.player.velocity_x = 0
        self.player.velocity_y = 0
        
        if keys[K_w] or keys[K_UP]:
            self.player.velocity_y = -1
        if keys[K_s] or keys[K_DOWN]:
            self.player.velocity_y = 1
        if keys[K_a] or keys[K_LEFT]:
            self.player.velocity_x = -1
        if keys[K_d] or keys[K_RIGHT]:
            self.player.velocity_x = 1
            
        if self.player.velocity_x != 0 and self.player.velocity_y != 0:
            self.player.velocity_x *= 0.7071
            self.player.velocity_y *= 0.7071

    def handle_upgrade_click(self, pos: tuple) -> None:
        x, y = pos
        upgrade_area_start = TOP_BAR_HEIGHT
        for i, upgrade in enumerate(self.upgrades):
            upgrade_rect = Rect(WINDOW_WIDTH - UPGRADE_PANEL_WIDTH, 
                              upgrade_area_start + i * 100, 
                              UPGRADE_PANEL_WIDTH, 80)
            if upgrade_rect.collidepoint(pos) and self.player.resources >= upgrade.cost:
                self.purchase_upgrade(i)

    def purchase_upgrade(self, index: int) -> None:
        upgrade = self.upgrades[index]
        if self.player.resources >= upgrade.cost:
            self.player.resources -= upgrade.cost
            upgrade.level += 1
            upgrade.cost = int(upgrade.cost * 1.5)
            
            if upgrade.name == "Movement Speed":
                self.player.movement_speed *= upgrade.multiplier
            elif upgrade.name == "Collection Range":
                self.player.collection_range *= upgrade.multiplier
            elif upgrade.name == "Collection Power":
                self.player.collection_power *= upgrade.multiplier
            elif upgrade.name == "Spawn Speed":
                self.spawn_time_multiplier *= upgrade.multiplier

    def check_resource_collection(self):
        current_time = pygame.time.get_ticks()
        
        # Update existing resources
        for node in self.resource_nodes:
            node.update(current_time)
            if node.active:
                distance = ((self.player.rect.centerx - node.rect.centerx) ** 2 + 
                          (self.player.rect.centery - node.rect.centery) ** 2) ** 0.5
                if distance <= self.player.collection_range:
                    collected = node.collect(current_time)
                    self.player.resources += collected * self.player.collection_power
        
        # Spawn new resources periodically
        if current_time - self.last_spawn_time >= RESOURCE_SPAWN_INTERVAL:
            self.spawn_resource()
            self.last_spawn_time = current_time

    def draw_hud(self):
        # Draw top bar
        pygame.draw.rect(self.screen, BLUE, (0, 0, WINDOW_WIDTH, TOP_BAR_HEIGHT))
        
        # Draw resources
        resources_text = self.font.render(f"Resources: {int(self.player.resources)}", True, WHITE)
        self.screen.blit(resources_text, (20, 20))
        
        # Draw health and stamina bars
        pygame.draw.rect(self.screen, RED, (200, 10, 200, 20))
        health_width = (self.player.health / self.player.max_health) * 200
        pygame.draw.rect(self.screen, GREEN, (200, 10, health_width, 20))
        
        pygame.draw.rect(self.screen, BLACK, (200, 35, 200, 20))
        stamina_width = (self.player.stamina / self.player.max_stamina) * 200
        pygame.draw.rect(self.screen, BLUE, (200, 35, stamina_width, 20))

    def draw_upgrade_panel(self):
        panel_rect = Rect(WINDOW_WIDTH - UPGRADE_PANEL_WIDTH, TOP_BAR_HEIGHT,
                         UPGRADE_PANEL_WIDTH, WINDOW_HEIGHT - TOP_BAR_HEIGHT)
        pygame.draw.rect(self.screen, GRAY, panel_rect)
        
        for i, upgrade in enumerate(self.upgrades):
            upgrade_rect = Rect(WINDOW_WIDTH - UPGRADE_PANEL_WIDTH,
                              TOP_BAR_HEIGHT + i * 100,
                              UPGRADE_PANEL_WIDTH, 80)
            pygame.draw.rect(self.screen, BLUE if self.player.resources >= upgrade.cost else GRAY,
                           upgrade_rect)
            
            name_text = self.font.render(f"{upgrade.name} (Lvl {upgrade.level})", True, WHITE)
            self.screen.blit(name_text, (WINDOW_WIDTH - UPGRADE_PANEL_WIDTH + 10,
                                       TOP_BAR_HEIGHT + i * 100 + 10))
            
            cost_text = self.small_font.render(f"Cost: {upgrade.cost}", True, WHITE)
            self.screen.blit(cost_text, (WINDOW_WIDTH - UPGRADE_PANEL_WIDTH + 10,
                                       TOP_BAR_HEIGHT + i * 100 + 45))

    def draw_minimap(self):
        self.minimap_surface.fill(BLACK)
        
        # Draw world border
        pygame.draw.rect(self.minimap_surface, GRAY, (0, 0, MINIMAP_WIDTH, MINIMAP_HEIGHT), 1)
        
        # Draw resource nodes on mini-map
        for node in self.resource_nodes:
            if node.active:
                minimap_x = (node.world_x / WORLD_WIDTH) * MINIMAP_WIDTH
                minimap_y = (node.world_y / WORLD_HEIGHT) * MINIMAP_HEIGHT
                pygame.draw.rect(self.minimap_surface, GOLD,
                               (minimap_x - 1, minimap_y - 1, 2, 2))
        
        # Draw player on mini-map
        minimap_x = (self.player.world_x / WORLD_WIDTH) * MINIMAP_WIDTH
        minimap_y = (self.player.world_y / WORLD_HEIGHT) * MINIMAP_HEIGHT
        pygame.draw.rect(self.minimap_surface, GREEN,
                        (minimap_x - MINIMAP_PLAYER_SIZE // 2,
                         minimap_y - MINIMAP_PLAYER_SIZE // 2,
                         MINIMAP_PLAYER_SIZE, MINIMAP_PLAYER_SIZE))
        
        # Draw mini-map frame and blit to screen
        pygame.draw.rect(self.minimap_surface, WHITE, (0, 0, MINIMAP_WIDTH, MINIMAP_HEIGHT), 2)
        self.screen.blit(self.minimap_surface,
                        (WINDOW_WIDTH - MINIMAP_WIDTH - MINIMAP_MARGIN - UPGRADE_PANEL_WIDTH,
                         MINIMAP_MARGIN))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    self.handle_upgrade_click(event.pos)
            
            self.handle_input()
            self.player.update()
            self.camera.update(self.player)
            self.check_resource_collection()
            
            # Draw everything
            self.screen.fill(BLACK)
            
            # Draw game world
            for sprite in self.all_sprites:
                screen_rect = self.camera.apply(sprite)
                self.screen.blit(sprite.image, screen_rect)
            
            self.draw_hud()
            self.draw_upgrade_panel()
            self.draw_minimap()
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run() 