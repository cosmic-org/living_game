import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
GRAVITY = 0.8
JUMP_FORCE = -20
SUPER_JUMP_FORCE = -40  # Force for jump pads
PLAYER_SPEED = 7  # Horizontal movement speed
CAMERA_THRESHOLD = WINDOW_HEIGHT * 0.4  # When player goes above this, camera moves

# Calculate maximum jump heights
# Using physics formula: max_height = -v0^2 / (2 * gravity)
MAX_JUMP_HEIGHT = -(JUMP_FORCE ** 2) / (2 * GRAVITY)
MAX_SUPER_JUMP_HEIGHT = -(SUPER_JUMP_FORCE ** 2) / (2 * GRAVITY)

# Platform spacing
MIN_PLATFORM_SPACING = 50  # Minimum vertical space between platforms
MAX_NORMAL_JUMP_SPACING = MAX_JUMP_HEIGHT * 0.8  # 80% of max jump height for safety
MAX_SUPER_JUMP_SPACING = MAX_SUPER_JUMP_HEIGHT * 0.8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)  # Color for jump pads

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Vertical Jumper")
clock = pygame.time.Clock()

class Player:
    def __init__(self, start_platform):
        # Position player on top of the starting platform
        self.world_y = start_platform.world_y - PLAYER_HEIGHT  # Actual position in the world
        self.rect = pygame.Rect(
            start_platform.rect.centerx - PLAYER_WIDTH // 2,
            self.world_y,
            PLAYER_WIDTH, PLAYER_HEIGHT
        )
        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = True

    def move(self, camera_y):
        # Horizontal movement
        keys = pygame.key.get_pressed()
        self.velocity_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = PLAYER_SPEED

        # Update horizontal position
        self.rect.x += self.velocity_x
        
        # Screen wrapping
        if self.rect.right < 0:  # Completely off the left side
            self.rect.left = WINDOW_WIDTH
        elif self.rect.left > WINDOW_WIDTH:  # Completely off the right side
            self.rect.right = 0

        # Auto-jump when on ground
        if self.on_ground:
            self.velocity_y = JUMP_FORCE
            self.on_ground = False

        # Apply gravity
        self.velocity_y += GRAVITY
        self.world_y += self.velocity_y
        
        # Ensure world_y and camera_y calculations result in a valid screen position
        screen_y = max(min(self.world_y - camera_y, 2147483647), -2147483648)
        self.rect.y = int(screen_y)  # Convert to integer and set position

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)

class Platform:
    def __init__(self, x, y, is_jump_pad=False):
        self.world_y = y  # Actual position in the world
        self.rect = pygame.Rect(x, int(y), PLATFORM_WIDTH, PLATFORM_HEIGHT)
        self.is_jump_pad = is_jump_pad

    def move(self, camera_y):
        # Update screen position based on world position
        screen_y = int(self.world_y - camera_y)
        self.rect.y = screen_y
        
    def draw(self):
        # Only draw if platform is visible on screen
        if -PLATFORM_HEIGHT <= self.rect.y <= WINDOW_HEIGHT:
            color = ORANGE if self.is_jump_pad else GREEN
            pygame.draw.rect(screen, color, self.rect)

def find_nearest_platform(platforms, y_position):
    nearest = None
    min_dist = float('inf')
    for platform in platforms:
        dist = abs(platform.world_y - y_position)
        if dist < min_dist:
            min_dist = dist
            nearest = platform
    return nearest

def create_platform(camera_y, platforms):
    try:
        # Calculate the target y position range for the new platform
        min_y = camera_y - WINDOW_HEIGHT * 0.3  # Don't spawn too high
        max_y = camera_y - WINDOW_HEIGHT * 0.1  # Don't spawn too close to top of screen
        
        # Find a suitable y position
        y = random.uniform(min_y, max_y)
        
        # Find nearest platform to this y position
        nearest = find_nearest_platform(platforms, y)
        
        # Choose x position
        if nearest:
            # Calculate maximum horizontal distance player can travel during jump
            jump_time = abs(JUMP_FORCE / GRAVITY) * 2  # Time to reach peak and fall back
            max_travel = PLAYER_SPEED * jump_time
            
            # Keep platform within reachable distance
            min_x = max(0, nearest.rect.x - max_travel)
            max_x = min(WINDOW_WIDTH - PLATFORM_WIDTH, nearest.rect.x + max_travel)
            
            # Add some randomness but keep within reachable range
            x = random.randint(int(min_x), int(max_x))
            
            # Determine if this should be a jump pad based on distance to nearest platform
            vertical_dist = abs(nearest.world_y - y)
            is_jump_pad = vertical_dist > MAX_NORMAL_JUMP_SPACING
        else:
            # If no nearest platform found, place randomly but ensure reachable
            x = random.randint(0, WINDOW_WIDTH - PLATFORM_WIDTH)
            is_jump_pad = False
        
        return Platform(x, y, is_jump_pad)
    except Exception:
        # Fallback: create a safe platform if anything goes wrong
        x = random.randint(0, WINDOW_WIDTH - PLATFORM_WIDTH)
        return Platform(x, camera_y - WINDOW_HEIGHT * 0.2, False)

def create_starting_platforms():
    platforms = []
    # Create main starting platform in the middle
    start_y = WINDOW_HEIGHT - 100
    start_platform = Platform(WINDOW_WIDTH // 2 - PLATFORM_WIDTH // 2, start_y)
    platforms.append(start_platform)
    
    # Create additional starting platforms at different heights
    num_platforms = 4  # Fixed number of starting platforms
    height_step = 150  # Fixed vertical distance between platforms
    
    for i in range(num_platforms):
        y = start_y - (i + 1) * height_step
        x = random.randint(PLATFORM_WIDTH, WINDOW_WIDTH - 2 * PLATFORM_WIDTH)
        # Add jump pad if the gap is too large
        is_jump_pad = height_step > MAX_NORMAL_JUMP_SPACING
        platforms.append(Platform(x, y, is_jump_pad))
    
    return platforms, start_platform

def reset_game():
    # Create starting platforms and player
    platforms, start_platform = create_starting_platforms()
    player = Player(start_platform)
    score = 0
    game_over = False
    camera_y = 0
    return player, platforms, score, game_over, camera_y

# Initialize game objects
player, platforms, score, game_over, camera_y = reset_game()

# Game loop
running = True
platform_spawn_timer = 0

# Font setup
font = pygame.font.Font(None, 36)

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_SPACE:
                # Reset the game
                player, platforms, score, game_over, camera_y = reset_game()

    if not game_over:
        # Camera movement
        target_y = player.world_y - CAMERA_THRESHOLD
        camera_y += (target_y - camera_y) * 0.1  # Smooth camera following

        # Game logic
        player.move(camera_y)
        
        # Platform logic
        platform_spawn_timer += 1
        if platform_spawn_timer > 40:  # Spawn new platform every 40 frames
            platforms.append(create_platform(camera_y, platforms))
            platform_spawn_timer = 0

        # Update platforms and check collisions
        for platform in platforms[:]:
            platform.move(camera_y)
            
            # Remove platforms that are too far below
            if platform.world_y > camera_y + WINDOW_HEIGHT * 1.5:
                platforms.remove(platform)
                score += 1

            # Platform collision
            if (player.rect.bottom >= platform.rect.top and
                player.rect.bottom <= platform.rect.bottom and
                player.rect.right >= platform.rect.left and
                player.rect.left <= platform.rect.right and
                player.velocity_y > 0):
                player.world_y = platform.world_y - PLAYER_HEIGHT
                if platform.is_jump_pad:
                    player.velocity_y = SUPER_JUMP_FORCE  # Super jump!
                else:
                    player.velocity_y = 0
                    player.on_ground = True

        # Check for game over (falling too far below camera view)
        if player.world_y > camera_y + WINDOW_HEIGHT * 1.2:
            game_over = True

    # Drawing
    screen.fill(BLACK)
    
    if game_over:
        game_over_text = font.render('Game Over! Press SPACE to restart', True, WHITE)
        final_score_text = font.render(f'Final Score: {score}', True, WHITE)
        screen.blit(game_over_text, 
                   (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 
                    WINDOW_HEIGHT // 2 - 50))
        screen.blit(final_score_text, 
                   (WINDOW_WIDTH // 2 - final_score_text.get_width() // 2, 
                    WINDOW_HEIGHT // 2 + 50))
    else:
        player.draw()
        for platform in platforms:
            platform.draw()
        # Draw score
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 10))

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit() 