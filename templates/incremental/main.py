import pygame
import sys
from typing import Dict, List
from dataclasses import dataclass
from pygame import Surface, Rect

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
TOP_BAR_HEIGHT = 60
BOTTOM_BAR_HEIGHT = 40
UPGRADE_PANEL_WIDTH = int(WINDOW_WIDTH * 0.3)
MAIN_AREA_WIDTH = WINDOW_WIDTH - UPGRADE_PANEL_WIDTH

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (100, 150, 255)
DARK_BLUE = (50, 100, 200)

@dataclass
class Upgrade:
    name: str
    cost: int
    multiplier: float
    level: int = 0
    description: str = ""

class IncrementalGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Incremental Game")
        
        # Game state
        self.points = 0
        self.points_per_click = 1
        self.points_per_second = 0
        self.total_clicks = 0
        
        # UI state
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Upgrades
        self.upgrades: List[Upgrade] = [
            Upgrade("Click Power", 10, 2, description="Double your click power"),
            Upgrade("Auto Clicker", 50, 1, description="Adds 1 point per second"),
            Upgrade("Multiplier", 100, 1.5, description="Increases all gains by 50%")
        ]
        
        # Last auto-click time
        self.last_auto_time = pygame.time.get_ticks()

    def handle_click(self, pos: tuple) -> None:
        x, y = pos
        # Check if click is in main play area
        if y > TOP_BAR_HEIGHT and y < WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT and x < MAIN_AREA_WIDTH:
            self.points += self.points_per_click
            self.total_clicks += 1
        
        # Check upgrade panel clicks
        elif x > MAIN_AREA_WIDTH:
            self.handle_upgrade_click(pos)

    def handle_upgrade_click(self, pos: tuple) -> None:
        x, y = pos
        upgrade_area_start = TOP_BAR_HEIGHT
        for i, upgrade in enumerate(self.upgrades):
            upgrade_rect = Rect(MAIN_AREA_WIDTH, upgrade_area_start + i * 100, 
                              UPGRADE_PANEL_WIDTH, 80)
            if upgrade_rect.collidepoint(pos) and self.points >= upgrade.cost:
                self.purchase_upgrade(i)

    def purchase_upgrade(self, index: int) -> None:
        upgrade = self.upgrades[index]
        if self.points >= upgrade.cost:
            self.points -= upgrade.cost
            upgrade.level += 1
            upgrade.cost = int(upgrade.cost * 1.5)  # Increase cost for next level
            
            if upgrade.name == "Click Power":
                self.points_per_click *= upgrade.multiplier
            elif upgrade.name == "Auto Clicker":
                self.points_per_second += 1
            elif upgrade.name == "Multiplier":
                self.points_per_click *= upgrade.multiplier
                self.points_per_second *= upgrade.multiplier

    def update(self) -> None:
        current_time = pygame.time.get_ticks()
        # Auto-click update (every second)
        if current_time - self.last_auto_time >= 1000:
            self.points += self.points_per_second
            self.last_auto_time = current_time

    def draw(self) -> None:
        self.screen.fill(WHITE)
        
        # Draw top bar
        pygame.draw.rect(self.screen, LIGHT_BLUE, (0, 0, WINDOW_WIDTH, TOP_BAR_HEIGHT))
        points_text = self.font.render(f"Points: {int(self.points)}", True, BLACK)
        self.screen.blit(points_text, (20, 20))
        
        # Draw main play area
        pygame.draw.rect(self.screen, WHITE, 
                        (0, TOP_BAR_HEIGHT, MAIN_AREA_WIDTH, 
                         WINDOW_HEIGHT - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT))
        
        # Draw click prompt in main area
        click_text = self.font.render("Click here!", True, BLACK)
        text_rect = click_text.get_rect(center=(MAIN_AREA_WIDTH/2, WINDOW_HEIGHT/2))
        self.screen.blit(click_text, text_rect)
        
        # Draw upgrade panel
        pygame.draw.rect(self.screen, GRAY, 
                        (MAIN_AREA_WIDTH, TOP_BAR_HEIGHT, UPGRADE_PANEL_WIDTH,
                         WINDOW_HEIGHT - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT))
        
        # Draw upgrades
        for i, upgrade in enumerate(self.upgrades):
            upgrade_rect = Rect(MAIN_AREA_WIDTH, TOP_BAR_HEIGHT + i * 100, 
                              UPGRADE_PANEL_WIDTH, 80)
            pygame.draw.rect(self.screen, DARK_BLUE if self.points >= upgrade.cost else GRAY, 
                           upgrade_rect)
            
            # Upgrade name and level
            name_text = self.font.render(f"{upgrade.name} (Lvl {upgrade.level})", True, WHITE)
            self.screen.blit(name_text, (MAIN_AREA_WIDTH + 10, TOP_BAR_HEIGHT + i * 100 + 10))
            
            # Upgrade cost
            cost_text = self.small_font.render(f"Cost: {upgrade.cost}", True, WHITE)
            self.screen.blit(cost_text, (MAIN_AREA_WIDTH + 10, TOP_BAR_HEIGHT + i * 100 + 45))
        
        # Draw bottom bar
        pygame.draw.rect(self.screen, LIGHT_BLUE, 
                        (0, WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT, WINDOW_WIDTH, BOTTOM_BAR_HEIGHT))
        stats_text = self.small_font.render(
            f"CPS: {self.points_per_second:.1f} | Click Power: {self.points_per_click:.1f} | Total Clicks: {self.total_clicks}",
            True, BLACK)
        self.screen.blit(stats_text, (20, WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT + 10))
        
        pygame.display.flip()

    def run(self) -> None:
        clock = pygame.time.Clock()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.handle_click((MAIN_AREA_WIDTH/2, WINDOW_HEIGHT/2))
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        # Number keys for quick upgrade purchase
                        upgrade_index = event.key - pygame.K_1
                        if upgrade_index < len(self.upgrades):
                            self.purchase_upgrade(upgrade_index)
            
            self.update()
            self.draw()
            clock.tick(60)

if __name__ == "__main__":
    game = IncrementalGame()
    game.run() 