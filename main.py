import pygame
import sys
import os
from pathlib import Path
import subprocess

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
HIGHLIGHT = (70, 130, 180)

class GameSelector:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Game Template Selector")
        self.clock = pygame.time.Clock()
        
        # Get available templates
        self.templates_dir = Path("templates")
        self.templates = [d.name for d in self.templates_dir.iterdir() if d.is_dir()]
        
        # Font setup
        self.title_font = pygame.font.Font(None, 64)
        self.menu_font = pygame.font.Font(None, 36)
        
        # Button dimensions
        self.button_height = 50
        self.button_width = 300
        self.button_padding = 20
        
        # Calculate total menu height
        self.total_height = len(self.templates) * (self.button_height + self.button_padding)
        self.start_y = (WINDOW_HEIGHT - self.total_height) // 2

    def draw_button(self, text, y_pos, highlighted=False):
        button_x = (WINDOW_WIDTH - self.button_width) // 2
        button_rect = pygame.Rect(button_x, y_pos, self.button_width, self.button_height)
        
        # Draw button
        color = HIGHLIGHT if highlighted else GRAY
        pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, button_rect, 2, border_radius=10)
        
        # Draw text
        text_surface = self.menu_font.render(text.replace("-", " ").title(), True, WHITE)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
        
        return button_rect

    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, template in enumerate(self.templates):
                        button_y = self.start_y + i * (self.button_height + self.button_padding)
                        button_rect = pygame.Rect(
                            (WINDOW_WIDTH - self.button_width) // 2,
                            button_y,
                            self.button_width,
                            self.button_height
                        )
                        
                        if button_rect.collidepoint(mouse_pos):
                            template_path = self.templates_dir / template
                            main_file = template_path / "main.py"
                            
                            if main_file.exists():
                                pygame.quit()
                                # Use the same Python interpreter that's running this script
                                subprocess.run([sys.executable, str(main_file)])
                                return
                            else:
                                print(f"Error: main.py not found in {template} template")
            
            # Draw
            self.screen.fill(BLACK)
            
            # Draw title
            title_surface = self.title_font.render("Select a Game Template", True, WHITE)
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 80))
            self.screen.blit(title_surface, title_rect)
            
            # Draw buttons
            for i, template in enumerate(self.templates):
                button_y = self.start_y + i * (self.button_height + self.button_padding)
                button_rect = pygame.Rect(
                    (WINDOW_WIDTH - self.button_width) // 2,
                    button_y,
                    self.button_width,
                    self.button_height
                )
                highlighted = button_rect.collidepoint(mouse_pos)
                self.draw_button(template, button_y, highlighted)
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    selector = GameSelector()
    selector.run() 