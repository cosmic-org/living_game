import pygame
import sys
import time
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
TRANSPARENT = (128, 128, 128, 128)

# Font
pygame.font.init()
font = pygame.font.SysFont('Arial', 40)
help_font = pygame.font.SysFont('Arial', 30)
round_font = pygame.font.SysFont('Arial', 80)

class Fighter:
    def __init__(self, x, y, flip=False):
        self.rect = pygame.Rect((x, y, 60, 120))  # Adjusted size for stick figure
        self.vel_y = 0
        self.jump = False
        self.attacking = False
        self.blocking = False
        self.attack_type = 0  # 1: punch, 2: kick
        self.health = 100
        self.flip = flip
        self.attack_cooldown = 0
        self.hit = False
        self.alive = True
        self.rounds_won = 0
        self.initial_x = x
        self.initial_y = y
        self.attack_frame = 0
        self.color = BLACK

    def draw_stick_figure(self, surface):
        if not self.alive:
            return

        # Calculate positions based on flip
        x = self.rect.centerx
        y = self.rect.centery
        direction = -1 if self.flip else 1
        
        # Head
        pygame.draw.circle(surface, self.color, (x, y - 45), 15)
        
        # Body
        pygame.draw.line(surface, self.color, (x, y - 30), (x, y + 10), 2)
        
        # Legs
        leg_angle = math.sin(time.time() * 5) * 0.2 if abs(self.vel_y) < 0.1 else 0.5
        pygame.draw.line(surface, self.color, (x, y + 10),
                        (x + math.cos(leg_angle) * 40 * direction,
                         y + 40 + math.sin(leg_angle) * 20), 2)
        pygame.draw.line(surface, self.color, (x, y + 10),
                        (x - math.cos(leg_angle) * 40 * direction,
                         y + 40 - math.sin(leg_angle) * 20), 2)
        
        # Arms
        if self.blocking:
            # Blocking pose - arms crossed in front
            pygame.draw.line(surface, self.color, (x, y - 20),
                           (x + 20 * direction, y - 10), 2)
            pygame.draw.line(surface, self.color, (x, y - 20),
                           (x + 20 * direction, y - 30), 2)
            # Draw block indicator
            pygame.draw.circle(surface, BLUE, (x + 25 * direction, y - 20), 10)
        elif self.attacking:
            if self.attack_type == 1:  # Punch
                # Back arm
                pygame.draw.line(surface, self.color, (x, y - 20),
                               (x - 30 * direction, y - 10), 2)
                # Punching arm
                arm_extend = min(40, self.attack_frame * 8)
                pygame.draw.line(surface, self.color, (x, y - 20),
                               (x + (30 + arm_extend) * direction, y - 10), 2)
                
            elif self.attack_type == 2:  # Kick
                # Arms in fighting stance
                pygame.draw.line(surface, self.color, (x, y - 20),
                               (x + 30 * direction, y - 30), 2)
                pygame.draw.line(surface, self.color, (x, y - 20),
                               (x - 20 * direction, y - 30), 2)
                # Kicking leg
                kick_angle = min(math.pi/3, self.attack_frame * 0.2)
                pygame.draw.line(surface, self.color, (x, y + 10),
                               (x + math.cos(kick_angle) * 60 * direction,
                                y + math.sin(kick_angle) * 60), 2)
        else:
            # Normal arms
            arm_angle = math.sin(time.time() * 5) * 0.2
            pygame.draw.line(surface, self.color, (x, y - 20),
                           (x + math.cos(arm_angle) * 30 * direction,
                            y - 20 + math.sin(arm_angle) * 10), 2)
            pygame.draw.line(surface, self.color, (x, y - 20),
                           (x - math.cos(arm_angle) * 30 * direction,
                            y - 20 - math.sin(arm_angle) * 10), 2)

    def attack(self, target, attack_type):
        if self.attack_cooldown == 0 and not self.blocking:
            self.attacking = True
            self.attack_type = attack_type
            self.attack_frame = 0
            
            # Calculate attack hitbox based on attack type
            if attack_type == 1:  # Punch
                attack_rect = pygame.Rect(
                    self.rect.centerx + (50 * (-1 if self.flip else 1)),
                    self.rect.y,
                    60,
                    60
                )
            else:  # Kick
                attack_rect = pygame.Rect(
                    self.rect.centerx + (70 * (-1 if self.flip else 1)),
                    self.rect.centery,
                    80,
                    40
                )
            
            if attack_rect.colliderect(target.rect):
                damage = 10 if attack_type == 1 else 15
                if target.blocking:
                    damage = damage // 2  # Reduce damage by half when blocking
                target.health -= damage
                target.hit = True
                target.color = RED
            
            self.attack_cooldown = 20

    def draw(self, surface):
        # Draw stick figure
        self.draw_stick_figure(surface)
        
        # Update attack animation
        if self.attacking:
            self.attack_frame += 1
            if self.attack_frame >= 5:  # Reset attack after 5 frames
                self.attacking = False
                self.attack_frame = 0
        
        # Reset hit color
        if self.hit:
            self.color = RED
        else:
            self.color = BLACK
        self.hit = False

    def reset_position(self):
        self.rect.x = self.initial_x
        self.rect.y = self.initial_y
        self.vel_y = 0
        self.jump = False
        self.attacking = False
        self.blocking = False
        self.attack_type = 0
        self.health = 100
        self.attack_cooldown = 0
        self.hit = False
        self.alive = True
        self.color = BLACK
        self.attack_frame = 0

    def move(self, screen_width, target):
        SPEED = 10
        GRAVITY = 0.8
        dx = 0
        dy = 0

        # Get key presses
        key = pygame.key.get_pressed()

        # Update blocking state
        self.blocking = (key[pygame.K_f] and not self.flip) or (key[pygame.K_b] and self.flip)

        # Can only perform actions if not attacking and not blocking
        if not self.attacking and not self.blocking and self.alive:
            # Movement
            if key[pygame.K_a] and not self.flip:
                dx = -SPEED
            if key[pygame.K_d] and not self.flip:
                dx = SPEED
            if key[pygame.K_LEFT] and self.flip:
                dx = -SPEED
            if key[pygame.K_RIGHT] and self.flip:
                dx = SPEED

            # Jump
            if key[pygame.K_w] and not self.jump and not self.flip:
                self.vel_y = -16
                self.jump = True
            if key[pygame.K_UP] and not self.jump and self.flip:
                self.vel_y = -16
                self.jump = True

            # Attack
            if key[pygame.K_r] and not self.flip:
                self.attack(target, 1)  # Punch
            if key[pygame.K_t] and not self.flip:
                self.attack(target, 2)  # Kick
            if key[pygame.K_n] and self.flip:
                self.attack(target, 1)  # Punch
            if key[pygame.K_m] and self.flip:
                self.attack(target, 2)  # Kick

        # Apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # Ensure player stays on screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > WINDOW_HEIGHT - 110:
            self.vel_y = 0
            self.jump = False
            dy = WINDOW_HEIGHT - 110 - self.rect.bottom

        # Update player position only if not blocking
        if not self.blocking:
            self.rect.x += dx
            self.rect.y += dy

        # Handle attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def draw_health(self, surface, x, y):
        ratio = self.health / 100
        pygame.draw.rect(surface, WHITE, (x - 2, y - 2, 404, 34))
        pygame.draw.rect(surface, RED, (x, y, 400, 30))
        pygame.draw.rect(surface, YELLOW, (x, y, 400 * ratio, 30))

        if self.health <= 0:
            self.health = 0
            self.alive = False

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Fighting Game")
        self.clock = pygame.time.Clock()
        self.round_number = 1
        self.max_rounds = 3
        self.round_over = False
        self.round_over_time = 0
        self.round_over_cooldown = 2  # seconds
        self.game_over = False
        self.show_controls = False
        
        # Create fighters
        self.fighter_1 = Fighter(200, 310)
        self.fighter_2 = Fighter(700, 310, flip=True)

        # Help button
        self.help_button = pygame.Rect(WINDOW_WIDTH - 60, 20, 40, 40)

    def draw_round_info(self):
        # Draw round number
        round_text = font.render(f'Round {self.round_number}', True, BLUE)
        self.screen.blit(round_text, (WINDOW_WIDTH // 2 - round_text.get_width() // 2, 20))

        # Draw rounds won
        p1_rounds = font.render(f'P1 Wins: {self.fighter_1.rounds_won}', True, BLUE)
        p2_rounds = font.render(f'P2 Wins: {self.fighter_2.rounds_won}', True, BLUE)
        self.screen.blit(p1_rounds, (20, 60))
        self.screen.blit(p2_rounds, (WINDOW_WIDTH - 220, 60))

    def check_round_over(self):
        if not self.round_over:
            if not self.fighter_1.alive or not self.fighter_2.alive:
                self.round_over = True
                self.round_over_time = time.time()
                
                # Increment rounds won
                if not self.fighter_1.alive and self.fighter_2.alive:
                    self.fighter_2.rounds_won += 1
                elif not self.fighter_2.alive and self.fighter_1.alive:
                    self.fighter_1.rounds_won += 1

    def start_new_round(self):
        self.round_number += 1
        self.round_over = False
        self.fighter_1.reset_position()
        self.fighter_2.reset_position()

    def check_game_over(self):
        if self.fighter_1.rounds_won >= 2 or self.fighter_2.rounds_won >= 2:
            self.game_over = True

    def draw_game_over(self):
        winner = "Player 1" if self.fighter_1.rounds_won >= 2 else "Player 2"
        text = round_font.render(f'{winner} Wins!', True, BLUE)
        restart_text = font.render('Press SPACE to restart', True, BLACK)
        self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))

    def reset_game(self):
        self.round_number = 1
        self.round_over = False
        self.game_over = False
        self.fighter_1.rounds_won = 0
        self.fighter_2.rounds_won = 0
        self.fighter_1.reset_position()
        self.fighter_2.reset_position()

    def draw_help_button(self):
        # Draw button background
        pygame.draw.rect(self.screen, BLUE, self.help_button, border_radius=20)
        
        # Draw "?" symbol
        text = font.render("?", True, WHITE)
        text_rect = text.get_rect(center=self.help_button.center)
        self.screen.blit(text, text_rect)

    def draw_controls_overlay(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(WHITE)
        overlay.set_alpha(230)
        self.screen.blit(overlay, (0, 0))

        # Title
        title = round_font.render("Controls", True, BLUE)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))

        # Player 1 Controls
        p1_title = font.render("Player 1", True, BLUE)
        self.screen.blit(p1_title, (150, 150))

        p1_controls = [
            "A/D - Move Left/Right",
            "W - Jump",
            "R - Punch",
            "T - Kick",
            "F - Block"
        ]

        y = 220
        for control in p1_controls:
            text = help_font.render(control, True, BLACK)
            self.screen.blit(text, (100, y))
            y += 40

        # Player 2 Controls
        p2_title = font.render("Player 2", True, BLUE)
        self.screen.blit(p2_title, (WINDOW_WIDTH - 350, 150))

        p2_controls = [
            "←/→ - Move Left/Right",
            "↑ - Jump",
            "N - Punch",
            "M - Kick",
            "B - Block"
        ]

        y = 220
        for control in p2_controls:
            text = help_font.render(control, True, BLACK)
            self.screen.blit(text, (WINDOW_WIDTH - 400, y))
            y += 40

        # General Controls
        general_title = font.render("General", True, BLUE)
        self.screen.blit(general_title, (WINDOW_WIDTH // 2 - general_title.get_width() // 2, 400))

        general_controls = [
            "? - Show/Hide Controls",
            "SPACE - Restart (after game over)"
        ]

        y = 460
        for control in general_controls:
            text = help_font.render(control, True, BLACK)
            self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y))
            y += 40

    def run(self):
        run = True
        while run:
            self.clock.tick(FPS)
            
            # Fill background
            self.screen.fill(WHITE)
            
            # Draw ground
            pygame.draw.line(self.screen, BLACK, (0, WINDOW_HEIGHT - 110), 
                           (WINDOW_WIDTH, WINDOW_HEIGHT - 110), 3)
            
            # Draw health bars and round info
            self.fighter_1.draw_health(self.screen, 20, 20)
            self.fighter_2.draw_health(self.screen, WINDOW_WIDTH - 420, 20)
            self.draw_round_info()
            
            if not self.game_over and not self.show_controls:
                # Move fighters
                self.fighter_1.move(WINDOW_WIDTH, self.fighter_2)
                self.fighter_2.move(WINDOW_WIDTH, self.fighter_1)
                
                # Draw fighters
                self.fighter_1.draw(self.screen)
                self.fighter_2.draw(self.screen)
                
                # Check round status
                self.check_round_over()
                
                # Handle round transition
                if self.round_over and time.time() - self.round_over_time >= self.round_over_cooldown:
                    self.check_game_over()
                    if not self.game_over:
                        self.start_new_round()
            elif self.game_over and not self.show_controls:
                self.draw_game_over()

            # Draw help button
            self.draw_help_button()

            # Draw controls overlay if active
            if self.show_controls:
                self.draw_controls_overlay()

            # Event handler
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_over:
                        self.reset_game()
                    elif event.key == pygame.K_SLASH:  # '?' key
                        self.show_controls = not self.show_controls
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.help_button.collidepoint(event.pos):
                            self.show_controls = not self.show_controls

            # Update display
            pygame.display.update()

        pygame.quit()
        sys.exit()

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run() 