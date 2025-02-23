import pygame
import random
import os
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 8
        self.health = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        # Horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        # Vertical movement
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        # Keep player on screen
        self.rect.clamp_ip(screen.get_rect())

    def shoot(self) -> 'Bullet':
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            return Bullet(self.rect.centerx, self.rect.top)
        return None

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > SCREEN_HEIGHT + 10 or self.rect.left < -25 or self.rect.right > SCREEN_WIDTH + 20:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 0))  # Green color for power-ups
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT + 10:
            self.kill()

class Game:
    def __init__(self):
        self.score = 0
        self.game_over = False
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        # Create player
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Spawn initial enemies
        for _ in range(8):
            self.spawn_enemy()

    def spawn_enemy(self):
        enemy = Enemy()
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)

    def spawn_powerup(self):
        if random.random() < 0.01:  # 1% chance each frame
            powerup = PowerUp()
            self.all_sprites.add(powerup)
            self.powerups.add(powerup)

    def handle_collisions(self):
        # Check bullet-enemy collisions
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        for hit in hits:
            self.score += 50
            self.spawn_enemy()

        # Check player-enemy collisions
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        for hit in hits:
            self.player.health -= 20
            self.spawn_enemy()
            if self.player.health <= 0:
                self.game_over = True

        # Check player-powerup collisions
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for hit in hits:
            self.player.health = min(100, self.player.health + 20)

    def update(self):
        self.all_sprites.update()
        self.handle_collisions()
        self.spawn_powerup()

    def draw(self):
        screen.fill(BLACK)
        self.all_sprites.draw(screen)
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw health bar
        health_width = 200
        health_height = 20
        health_rect = pygame.Rect(SCREEN_WIDTH - health_width - 10, 10, 
                                health_width * (self.player.health / 100), health_height)
        pygame.draw.rect(screen, RED, health_rect)
        
        pygame.display.flip()

def main():
    game = Game()
    running = True

    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                bullet = game.player.shoot()
                if bullet:
                    game.all_sprites.add(bullet)
                    game.bullets.add(bullet)

        if not game.game_over:
            game.update()
            game.draw()
        else:
            # Display game over screen
            screen.fill(BLACK)
            font = pygame.font.Font(None, 74)
            text = font.render('Game Over', True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(text, text_rect)
            pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main() 