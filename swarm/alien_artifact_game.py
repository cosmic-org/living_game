import pygame
import sys
import math
import random
from enum import Enum

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 50
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
TEAL = (0, 128, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class Affinity(Enum):
    ATTRACT = 'attract'
    REPEL = 'repel'
    ORBIT = 'orbit'
    LINK = 'link'
    NONE = 'none'

class GameState(Enum):
    TITLE = 0
    PLAYING = 1
    INVENTORY = 2
    DIALOGUE = 3
    GAME_OVER = 4
    WIN = 5
    ENTANGLEMENT = 6

class Artifact:
    def __init__(self, name, description, world_effect, player_effect, image_color, is_cursed=False, affinity=Affinity.NONE):
        self.name = name
        self.description = description
        self.world_effect = world_effect
        self.player_effect = player_effect
        self.image_color = image_color
        self.is_cursed = is_cursed
        self.affinity = affinity
        self.curse_cleansed = False
        self.rect = pygame.Rect(0, 0, TILE_SIZE//2, TILE_SIZE//2)
        
    def draw(self, surface, x, y):
        self.rect.x, self.rect.y = x, y
        pygame.draw.rect(surface, self.image_color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)  # Border
        
        # Draw a symbol if cursed
        if self.is_cursed and not self.curse_cleansed:
            # Draw a small red X
            start1 = (self.rect.x + 5, self.rect.y + 5)
            end1 = (self.rect.x + self.rect.width - 5, self.rect.y + self.rect.height - 5)
            start2 = (self.rect.x + 5, self.rect.y + self.rect.height - 5)
            end2 = (self.rect.x + self.rect.width - 5, self.rect.y + 5)
            pygame.draw.line(surface, RED, start1, end1, 2)
            pygame.draw.line(surface, RED, start2, end2, 2)
    
    def apply_effect(self, game_world, player):
        """Apply the artifact's effect to the game world and player"""
        game_world.show_message(f"You activate the {self.name}.")
        game_world.show_message(f"WORLD EFFECT: {self.world_effect}")
        game_world.apply_artifact_effect(self)
        
        game_world.show_message(f"PLAYER EFFECT: {self.player_effect}")
        player.transform(self)
        
        if self.is_cursed and not self.curse_cleansed:
            game_world.show_message(f"WARNING: This artifact is cursed! {self.curse_effect()}")
            player.apply_curse(self)
    
    def curse_effect(self):
        """Return the curse effect description"""
        if self.is_cursed and not self.curse_cleansed:
            return "The curse drains your energy, reducing your movement range."
        return ""
    
    def cleanse_curse(self):
        """Cleanse the curse from the artifact"""
        if self.is_cursed:
            self.curse_cleansed = True
            return True
        return False

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.color = (0, 0, 255)  # Blue player
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, self.width, self.height)
        self.inventory = []
        self.size = 1.0  # Normal size
        self.inverted_controls = False
        self.can_phase = False
        self.movement_range = 1
        self.cursed = False
        self.direction = Direction.DOWN
        self.selected_artifact = None
        self.animation_offset = 0
        self.animation_timer = 0
    
    def transform(self, artifact):
        """Apply artifact transformation to the player"""
        if "size" in artifact.player_effect.lower():
            if "increase" in artifact.player_effect.lower():
                self.size = 2.0
                self.width = int(TILE_SIZE * 1.5)
                self.height = int(TILE_SIZE * 1.5)
            elif "decrease" in artifact.player_effect.lower():
                self.size = 0.5
                self.width = int(TILE_SIZE * 0.7)
                self.height = int(TILE_SIZE * 0.7)
            self.rect.width, self.rect.height = self.width, self.height
        
        if "control" in artifact.player_effect.lower():
            self.inverted_controls = not self.inverted_controls
        
        if "phase" in artifact.player_effect.lower():
            self.can_phase = True
    
    def collect_artifact(self, artifact, game_world):
        """Add artifact to inventory and apply its effects"""
        self.inventory.append(artifact)
        artifact.apply_effect(game_world, self)
        
        # Check for artifact combinations
        self.check_artifact_combinations(game_world)
    
    def check_artifact_combinations(self, game_world):
        """Check for special artifact combinations and their effects"""
        if len(self.inventory) < 2:
            return
        
        # Check for gravity inversion + phasing combination
        has_gravity_artifact = any("gravity" in a.world_effect.lower() for a in self.inventory)
        has_phase_artifact = any("phase" in a.player_effect.lower() for a in self.inventory)
        
        if has_gravity_artifact and has_phase_artifact:
            game_world.show_message("\nDISCOVERY: With inverted gravity and phasing abilities, you can now walk on ceilings and through barriers!")
    
    def apply_curse(self, artifact):
        """Apply curse effect to player"""
        self.cursed = True
        self.movement_range = max(1, self.movement_range - 1)
    
    def remove_curse(self):
        """Remove curse effects from player"""
        self.cursed = False
        self.movement_range = 1
    
    def move(self, direction, game_world):
        """Move the player in the specified direction"""
        move_dir = direction
        
        # Handle inverted controls
        if self.inverted_controls:
            if direction == Direction.UP:
                move_dir = Direction.DOWN
            elif direction == Direction.DOWN:
                move_dir = Direction.UP
            elif direction == Direction.RIGHT:
                move_dir = Direction.LEFT
            elif direction == Direction.LEFT:
                move_dir = Direction.RIGHT
        
        # Set facing direction
        self.direction = move_dir
        
        # Calculate new position
        new_x, new_y = self.x, self.y
        if move_dir == Direction.UP:
            new_y -= self.movement_range
        elif move_dir == Direction.DOWN:
            new_y += self.movement_range
        elif move_dir == Direction.RIGHT:
            new_x += self.movement_range
        elif move_dir == Direction.LEFT:
            new_x -= self.movement_range
        
        # Check if movement is valid
        if game_world.is_valid_move(self, new_x, new_y):
            self.x, self.y = new_x, new_y
            self.rect.x = self.x * TILE_SIZE
            self.rect.y = self.y * TILE_SIZE
            
            # Start movement animation
            self.animation_timer = 10
            
            # Check for artifacts at new position
            game_world.check_location_features(self)
            return True
        else:
            return False
    
    def update(self):
        # Update animation
        if self.animation_timer > 0:
            self.animation_timer -= 1
            # Calculate bob effect (move up and down slightly)
            self.animation_offset = int(math.sin(pygame.time.get_ticks() * 0.01) * 3)
    
    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        x = self.rect.x - camera_offset_x
        y = self.rect.y - camera_offset_y + self.animation_offset
        
        # Draw player with current appearance
        player_rect = pygame.Rect(x, y, self.width, self.height)
        
        # Choose color based on state
        color = self.color
        if self.cursed:
            color = (200, 100, 100)  # Reddish when cursed
        
        # Draw player with appropriate effects
        pygame.draw.rect(surface, color, player_rect, border_radius=8)
        
        # Draw phasing effect
        if self.can_phase:
            # Ghostly outline
            larger_rect = player_rect.inflate(6, 6)
            pygame.draw.rect(surface, (200, 200, 255, 128), larger_rect, 2, border_radius=10)
        
        # Draw direction indicator (eyes)
        eye_size = max(4, int(self.width / 8))
        eye_offset = max(2, int(self.width / 10))
        
        if self.direction == Direction.DOWN:
            # Two eyes at the bottom
            pygame.draw.circle(surface, WHITE, (x + self.width//3, y + self.height//3*2), eye_size)
            pygame.draw.circle(surface, WHITE, (x + self.width//3*2, y + self.height//3*2), eye_size)
        elif self.direction == Direction.UP:
            # Two eyes at the top
            pygame.draw.circle(surface, WHITE, (x + self.width//3, y + self.height//3), eye_size)
            pygame.draw.circle(surface, WHITE, (x + self.width//3*2, y + self.height//3), eye_size)
        elif self.direction == Direction.LEFT:
            # Two eyes on the left side
            pygame.draw.circle(surface, WHITE, (x + self.width//3, y + self.height//3), eye_size)
            pygame.draw.circle(surface, WHITE, (x + self.width//3, y + self.height//3*2), eye_size)
        elif self.direction == Direction.RIGHT:
            # Two eyes on the right side
            pygame.draw.circle(surface, WHITE, (x + self.width//3*2, y + self.height//3), eye_size)
            pygame.draw.circle(surface, WHITE, (x + self.width//3*2, y + self.height//3*2), eye_size)

class Tile:
    def __init__(self, x, y, tile_type, walkable=True):
        self.x = x
        self.y = y
        self.type = tile_type
        self.walkable = walkable
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.artifact = None
        self.is_temple = False
        self.is_pedestal = False
        self.pedestal_name = ""
        self.pedestal_artifact = None
        
    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        x = self.x * TILE_SIZE - camera_offset_x
        y = self.y * TILE_SIZE - camera_offset_y
        
        # Skip drawing if off screen
        if (x < -TILE_SIZE or x > SCREEN_WIDTH or 
            y < -TILE_SIZE or y > SCREEN_HEIGHT):
            return
        
        # Draw different tile types
        if self.type == "floor":
            color = (20, 100, 20)  # Green for normal floor
            if self.is_temple:
                color = (80, 70, 120)  # Purple-ish for temple floors
            pygame.draw.rect(surface, color, (x, y, TILE_SIZE, TILE_SIZE))
            
            # Draw grid lines
            pygame.draw.rect(surface, (40, 40, 40), (x, y, TILE_SIZE, TILE_SIZE), 1)
            
        elif self.type == "wall":
            pygame.draw.rect(surface, DARK_GRAY, (x, y, TILE_SIZE, TILE_SIZE))
            # Add some texture to walls
            for i in range(3):
                pygame.draw.line(surface, GRAY, 
                                (x + i*15, y), 
                                (x + i*15, y + TILE_SIZE), 
                                2)
                
        elif self.type == "water":
            pygame.draw.rect(surface, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
            # Add wave effects
            wave_offset = math.sin(pygame.time.get_ticks() * 0.005 + self.x * 0.5) * 2
            for i in range(3):
                wave_y = y + 10 + i*10 + wave_offset
                pygame.draw.line(surface, (100, 200, 255), 
                                (x, wave_y), 
                                (x + TILE_SIZE, wave_y), 
                                2)
        
        # Draw pedestal if this is one
        if self.is_pedestal:
            pedestal_rect = pygame.Rect(x + TILE_SIZE//4, y + TILE_SIZE//4, 
                                     TILE_SIZE//2, TILE_SIZE//2)
            pygame.draw.rect(surface, TEAL, pedestal_rect)
            
            # Draw artifact on pedestal if one is placed
            if self.pedestal_artifact:
                self.pedestal_artifact.draw(surface, 
                                          x + TILE_SIZE//4 + 5, 
                                          y + TILE_SIZE//4 + 5)
        
        # Draw artifact if present
        if self.artifact:
            self.artifact.draw(surface, x + TILE_SIZE//4, y + TILE_SIZE//4)

class World:
    def __init__(self):
        self.tiles = {}  # (x, y): Tile
        self.gravity_inverted = False
        self.landscape_warped = False
        self.temple_unlocked = False
        self.artifact_effects = []
        self.temples = []  # List of temple tile coordinates
        self.pedestals = {}  # {pedestal_name: (x, y)}
        self.message_queue = []
        self.current_message = ""
        self.message_timer = 0
        
    def generate_world(self):
        """Generate a simple world map"""
        # Create a basic map layout
        world_layout = [
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "W..........................W...........W",
            "W....A.......................A........W",
            "W..........................W...........W",
            "W..........................WWWWWWWWWWWWW",
            "W..........W.........................A.W",
            "W..........W............................W",
            "W..........W............................W",
            "W..........W............................W",
            "W....................................................W",
            "W....................................................W",
            "W....................................................W",
            "W............................................WWWWWWW",
            "W.........A..............................W........W",
            "W............................................W........W",
            "W............................................W........W",
            "W....................................................W",
            "W....................................................W",
            "W....................................................W",
            "W.................................................T..W",
            "W............................................WWWWWWW",
            "W....................................................W",
            "W....T.............................................W",
            "W..............................................PPPW",
            "W............................................T.....W",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        ]
        
        # Create tiles based on the layout
        for y, row in enumerate(world_layout):
            for x, cell in enumerate(row):
                if cell == 'W':  # Wall
                    self.tiles[(x, y)] = Tile(x, y, "wall", walkable=False)
                elif cell == '.':  # Floor
                    self.tiles[(x, y)] = Tile(x, y, "floor")
                elif cell == 'A':  # Floor with artifact
                    tile = Tile(x, y, "floor")
                    self.tiles[(x, y)] = tile
                elif cell == 'T':  # Temple floor
                    tile = Tile(x, y, "floor")
                    tile.is_temple = True
                    self.tiles[(x, y)] = tile
                    self.temples.append((x, y))
                elif cell == 'P':  # Pedestal
                    tile = Tile(x, y, "floor")
                    tile.is_temple = True
                    tile.is_pedestal = True
                    self.tiles[(x, y)] = tile
                    self.temples.append((x, y))
        
        # Assign pedestals
        pedestal_locations = [(x, y) for (x, y), tile in self.tiles.items() 
                             if tile.is_pedestal]
        
        if len(pedestal_locations) >= 4:
            # Sort by coordinates to ensure deterministic assignment
            pedestal_locations.sort()
            
            # Assign pedestal names
            pedestal_names = ["North", "East", "South", "West"]
            for i, (x, y) in enumerate(pedestal_locations[:4]):
                self.pedestals[pedestal_names[i]] = (x, y)
                self.tiles[(x, y)].pedestal_name = pedestal_names[i]
                
        # Place artifact at specific locations
        artifact_locations = [(x, y) for (x, y), tile in self.tiles.items() 
                             if tile.type == "floor" and not tile.is_temple and not tile.is_pedestal]
        
        # Create artifacts
        artifacts = [
            Artifact(
                "Gravity Lens", 
                "A strange crystalline lens that bends light and gravity", 
                "Inverts gravity in the surrounding area", 
                "Allows you to perceive gravitational waves",
                BLUE,
                False,
                Affinity.ATTRACT
            ),
            Artifact(
                "Phase Crystal", 
                "A shimmering crystal that seems to exist in multiple states at once", 
                "Creates phasing rifts in nearby structures", 
                "Grants you the ability to phase through certain barriers",
                PURPLE,
                False,
                Affinity.LINK
            ),
            Artifact(
                "Size Scepter", 
                "An ornate rod that pulses with energy", 
                "Causes objects in the environment to randomly grow or shrink", 
                "Changes your size depending on how you hold it",
                YELLOW,
                False,
                Affinity.ORBIT
            ),
            Artifact(
                "Void Mask", 
                "A dark mask with swirling patterns that hurt to look at", 
                "Warps and distorts the landscape", 
                "Inverts your movement controls",
                RED,
                True,
                Affinity.REPEL
            )
        ]
        
        # Place artifacts at random positions in the world
        random.shuffle(artifact_locations)
        for i, artifact in enumerate(artifacts):
            if i < len(artifact_locations):
                x, y = artifact_locations[i]
                self.tiles[(x, y)].artifact = artifact
    
    def is_valid_move(self, player, new_x, new_y):
        """Check if the player can move to the new position"""
        # Check if the tile exists and is walkable
        tile = self.tiles.get((new_x, new_y))
        if not tile or not tile.walkable:
            # If player can phase, they can move through walls
            if player.can_phase and tile:
                return True
            return False
        return True
    
    def check_location_features(self, player):
        """Check for interactive features at the player's location"""
        tile = self.tiles.get((player.x, player.y))
        if not tile:
            return
        
        # Check for artifacts
        if tile.artifact:
            self.show_message(f"You found a {tile.artifact.name}!")
            self.show_message(f"Press 'E' to collect it.")
    
    def collect_artifact(self, player):
        """Player collects an artifact at their current position"""
        tile = self.tiles.get((player.x, player.y))
        if tile and tile.artifact:
            artifact = tile.artifact
            player.collect_artifact(artifact, self)
            self.show_message(f"You collected the {artifact.name}.")
            tile.artifact = None
            return True
        return False
    
    def place_artifact(self, player):
        """Place the selected artifact on a pedestal"""
        if not player.selected_artifact:
            self.show_message("You need to select an artifact first (1-9 keys).")
            return False
        
        tile = self.tiles.get((player.x, player.y))
        if not tile or not tile.is_pedestal:
            self.show_message("You can only place artifacts on pedestals in the temple.")
            return False
        
        # Place on pedestal
        artifact = player.selected_artifact
        tile.pedestal_artifact = artifact
        
        # Update pedestal record
        if tile.pedestal_name:
            pedestal_name = tile.pedestal_name
            self.show_message(f"You placed the {artifact.name} on the {pedestal_name} pedestal.")
            player.inventory.remove(artifact)
            player.selected_artifact = None
            
            # Check if all pedestals filled
            self.check_pedestals()
            return True
        
        return False
    
    def check_pedestals(self):
        """Check if all pedestals have artifacts and activate temple if so"""
        all_filled = True
        pedestal_artifacts = []
        
        # Check each pedestal
        for pedestal_name, (x, y) in self.pedestals.items():
            tile = self.tiles.get((x, y))
            if not tile or not tile.pedestal_artifact:
                all_filled = False
                break
            pedestal_artifacts.append(tile.pedestal_artifact)
        
        if all_filled:
            self.show_message("\nAncient mechanisms begin to whir as all pedestals are filled!")
            
            # Check artifact combinations
            has_gravity = any("gravity" in a.world_effect.lower() for a in pedestal_artifacts)
            has_phase = any("phase" in a.player_effect.lower() for a in pedestal_artifacts)
            
            if has_gravity and has_phase:
                self.show_message("**** The temple responds to your artifact combination! ****")
                self.show_message("A hidden door slides open, revealing a secret chamber.")
                self.temple_unlocked = True
                
                # Create a new passage to secret chamber
                secret_room_coords = []
                for x, y in self.temples:
                    # Find tiles adjacent to temple tiles
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        new_x, new_y = x + dx, y + dy
                        if (new_x, new_y) not in self.tiles:
                            # Create new temple room
                            for rx in range(3):
                                for ry in range(3):
                                    new_tile = Tile(new_x + rx, new_y + ry, "floor")
                                    new_tile.is_temple = True
                                    self.tiles[(new_x + rx, new_y + ry)] = new_tile
                                    secret_room_coords.append((new_x + rx, new_y + ry))
                            break
                    if secret_room_coords:
                        break
                
                # Add special marker for win condition
                if secret_room_coords:
                    center = secret_room_coords[len(secret_room_coords)//2]
                    self.tiles[center].type = "win"
                
                return True
        
        return False
    
    def apply_artifact_effect(self, artifact):
        """Apply an artifact's effect to the game world"""
        self.artifact_effects.append(artifact.world_effect)
        
        if "gravity" in artifact.world_effect.lower():
            self.gravity_inverted = not self.gravity_inverted
            self.show_message("The gravity has been inverted! Up is now down, and down is now up.")
        
        if "warp" in artifact.world_effect.lower() or "distort" in artifact.world_effect.lower():
            self.landscape_warped = True
            self.show_message("The landscape around you begins to warp and distort in strange ways.")
    
    def cleanse_artifact(self, player):
        """Cleanse the selected cursed artifact"""
        if not player.selected_artifact:
            self.show_message("You need to select an artifact first (1-9 keys).")
            return False
        
        artifact = player.selected_artifact
        if not artifact.is_cursed or artifact.curse_cleansed:
            self.show_message(f"The {artifact.name} is not cursed or has already been cleansed.")
            return False
        
        # Check if at temple
        tile = self.tiles.get((player.x, player.y))
        if not tile or not tile.is_temple:
            self.show_message("You can only cleanse artifacts at the temple.")
            return False
        
        # Cleanse artifact
        if artifact.cleanse_curse():
            player.remove_curse()
            self.show_message(f"The {artifact.name} has been cleansed!")
            self.show_message("You feel the curse's grip on you weaken.")
            return True
        
        return False
    
    def show_message(self, message):
        """Add a message to the message queue"""
        self.message_queue.append(message)
        if not self.current_message:
            self.next_message()
    
    def next_message(self):
        """Display the next message in the queue"""
        if self.message_queue:
            self.current_message = self.message_queue.pop(0)
            self.message_timer = max(60, len(self.current_message) * 3)  # Time based on message length
    
    def update(self):
        """Update world state"""
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0 and self.message_queue:
                self.next_message()
        elif self.current_message and not self.message_queue:
            self.current_message = ""
    
    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        """Draw the world"""
        # Loop all world tiles
        for coords, tile in self.tiles.items():
            tile.draw(surface, camera_offset_x, camera_offset_y)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Alien Artifact Explorer")
        self.clock = pygame.time.Clock()
        self.state = GameState.TITLE
        
        self.world = World()
        self.world.generate_world()
        
        # Calculate a good starting position (find first floor tile)
        self.player = None
        for coords, tile in self.world.tiles.items():
            if tile.type == "floor" and not tile.is_temple:
                self.player = Player(coords[0], coords[1])
                break
        
        if not self.player:
            # Fallback starting position
            self.player = Player(1, 1)
        
        self.camera_x = 0
        self.camera_y = 0
        
        # Set up fonts
        self.font_large = pygame.font.SysFont(None, 48)
        self.font_medium = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 24)
        
        # Input handling
        self.keys_down = set()
        
        # Initialize UI elements
        self.ui_rect = pygame.Rect(0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100)
        
        # HUD information
        self.show_controls = True
        self.controls_timer = 300  # Show controls for first 5 seconds
    
    def update_camera(self):
        """Update camera position to center on player"""
        target_x = self.player.x * TILE_SIZE - SCREEN_WIDTH // 2
        target_y = self.player.y * TILE_SIZE - SCREEN_HEIGHT // 2
        
        # Smooth camera movement
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
        
        # Keep camera within bounds
        self.camera_x = max(0, min(self.camera_x, 1000 * TILE_SIZE - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, 1000 * TILE_SIZE - SCREEN_HEIGHT))
    
    def draw_ui(self):
        """Draw game UI elements"""
        # Draw message box
        if self.world.current_message:
            # Draw semi-transparent background
            message_surface = pygame.Surface((SCREEN_WIDTH, 80))
            message_surface.set_alpha(200)
            message_surface.fill(BLACK)
            self.screen.blit(message_surface, (0, SCREEN_HEIGHT - 80))
            
            # Draw message text with word wrapping
            words = self.world.current_message.split(' ')
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                test_line = ' '.join(current_line)
                test_width = self.font_small.size(test_line)[0]
                
                if test_width > SCREEN_WIDTH - 40:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            for i, line in enumerate(lines):
                text_surface = self.font_small.render(line, True, WHITE)
                self.screen.blit(text_surface, (20, SCREEN_HEIGHT - 70 + i * 24))
        
        # Draw HUD info
        # Status indicators at top-left
        status_surface = pygame.Surface((200, 80))
        status_surface.set_alpha(180)
        status_surface.fill(BLACK)
        self.screen.blit(status_surface, (10, 10))
        
        # Draw status text
        status_text = []
        if self.player.inverted_controls:
            status_text.append("Controls: INVERTED")
        if self.player.can_phase:
            status_text.append("Phasing: ACTIVE")
        if self.player.cursed:
            status_text.append("Cursed: YES")
        if self.player.size != 1.0:
            size_text = "Size: LARGE" if self.player.size > 1.0 else "Size: SMALL"
            status_text.append(size_text)
        
        for i, text in enumerate(status_text):
            text_surface = self.font_small.render(text, True, YELLOW)
            self.screen.blit(text_surface, (20, 15 + i * 20))
        
        # Draw controls help (temporary)
        if self.show_controls:
            help_surface = pygame.Surface((300, 180))
            help_surface.set_alpha(200)
            help_surface.fill(BLACK)
            self.screen.blit(help_surface, (SCREEN_WIDTH - 310, 10))
            
            controls = [
                "Controls:",
                "Arrow Keys: Move",
                "E: Collect Artifact",
                "1-9: Select Artifact",
                "P: Place on Pedestal",
                "C: Cleanse Artifact",
                "I: Inventory",
                "ESC: Quit"
            ]
            
            for i, text in enumerate(controls):
                text_surface = self.font_small.render(text, True, WHITE)
                self.screen.blit(text_surface, (SCREEN_WIDTH - 300, 15 + i * 20))
        
        # Draw inventory bar at bottom
        if self.player.inventory:
            inventory_surface = pygame.Surface((SCREEN_WIDTH, 50))
            inventory_surface.set_alpha(200)
            inventory_surface.fill(BLACK)
            self.screen.blit(inventory_surface, (0, SCREEN_HEIGHT - 50))
            
            # Draw inventory slots
            for i, artifact in enumerate(self.player.inventory[:9]):
                slot_rect = pygame.Rect(10 + i * 55, SCREEN_HEIGHT - 45, 50, 40)
                # Highlight selected artifact
                if artifact == self.player.selected_artifact:
                    pygame.draw.rect(self.screen, (100, 100, 255), slot_rect, 2)
                else:
                    pygame.draw.rect(self.screen, GRAY, slot_rect, 1)
                
                # Draw artifact in slot
                artifact.draw(self.screen, 15 + i * 55, SCREEN_HEIGHT - 40)
                
                # Draw slot number
                num_text = self.font_small.render(str(i+1), True, WHITE)
                self.screen.blit(num_text, (10 + i * 55, SCREEN_HEIGHT - 45))
    
    def handle_input(self):
        """Handle player input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                # Add key to keys_down set
                self.keys_down.add(event.key)
                
                # Handle key presses
                if event.key == pygame.K_ESCAPE:
                    return False
                
                # Toggle inventory
                if event.key == pygame.K_i:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.INVENTORY
                    elif self.state == GameState.INVENTORY:
                        self.state = GameState.PLAYING
                
                # Collect artifact
                if event.key == pygame.K_e and self.state == GameState.PLAYING:
                    self.world.collect_artifact(self.player)
                
                # Place artifact on pedestal
                if event.key == pygame.K_p and self.state == GameState.PLAYING:
                    self.world.place_artifact(self.player)
                
                # Cleanse artifact
                if event.key == pygame.K_c and self.state == GameState.PLAYING:
                    self.world.cleanse_artifact(self.player)
                
                # Select artifact (number keys 1-9)
                if event.key in range(pygame.K_1, pygame.K_9 + 1) and self.player.inventory:
                    index = event.key - pygame.K_1
                    if index < len(self.player.inventory):
                        self.player.selected_artifact = self.player.inventory[index]
                        self.world.show_message(f"Selected: {self.player.selected_artifact.name}")
                
                # Handle title screen
                if self.state == GameState.TITLE and event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self.state = GameState.PLAYING
                
                # Handle game over / win screens
                if (self.state in [GameState.GAME_OVER, GameState.WIN] and 
                    event.key in [pygame.K_RETURN, pygame.K_SPACE]):
                    # Reset the game
                    self.__init__()
            
            elif event.type == pygame.KEYUP:
                # Remove key from keys_down set
                if event.key in self.keys_down:
                    self.keys_down.remove(event.key)
        
        return True
    
    def process_continuous_input(self):
        """Process keys that are currently held down"""
        if self.state != GameState.PLAYING:
            return
        
        # Movement with arrow keys (check if not moved recently to avoid too fast movement)
        if pygame.time.get_ticks() % 8 == 0:  # Control movement speed
            if pygame.K_UP in self.keys_down:
                self.player.move(Direction.UP, self.world)
            elif pygame.K_DOWN in self.keys_down:
                self.player.move(Direction.DOWN, self.world)
            elif pygame.K_LEFT in self.keys_down:
                self.player.move(Direction.LEFT, self.world)
            elif pygame.K_RIGHT in self.keys_down:
                self.player.move(Direction.RIGHT, self.world)
    
    def draw_inventory_screen(self):
        """Draw the inventory screen"""
        # Draw semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title_text = self.font_large.render("Inventory", True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 30))
        
        # Draw inventory items with descriptions
        if not self.player.inventory:
            empty_text = self.font_medium.render("Your inventory is empty.", True, WHITE)
            self.screen.blit(empty_text, (SCREEN_WIDTH//2 - empty_text.get_width()//2, SCREEN_HEIGHT//2))
        else:
            for i, artifact in enumerate(self.player.inventory):
                # Draw artifact icon
                y_pos = 100 + i * 80
                artifact.draw(self.screen, 50, y_pos)
                
                # Draw name
                name_text = self.font_medium.render(artifact.name, True, WHITE)
                self.screen.blit(name_text, (100, y_pos))
                
                # Draw description
                desc_text = self.font_small.render(artifact.description, True, GRAY)
                self.screen.blit(desc_text, (100, y_pos + 30))
                
                # Draw effects
                effect_text = self.font_small.render(f"Effect: {artifact.player_effect}", True, YELLOW)
                self.screen.blit(effect_text, (100, y_pos + 50))
                
                # Draw curse status if applicable
                if artifact.is_cursed:
                    status = "CURSED" if not artifact.curse_cleansed else "CLEANSED"
                    curse_text = self.font_small.render(status, True, RED if not artifact.curse_cleansed else GREEN)
                    self.screen.blit(curse_text, (400, y_pos))
        
        # Draw instruction
        instruction_text = self.font_small.render("Press I to return to game", True, WHITE)
        self.screen.blit(instruction_text, (SCREEN_WIDTH//2 - instruction_text.get_width()//2, SCREEN_HEIGHT - 50))
    
    def draw_title_screen(self):
        """Draw the title screen"""
        # Fill background with dark color
        self.screen.fill((20, 20, 40))
        
        # Draw title
        title_text = self.font_large.render("Alien Artifact Explorer", True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
        
        # Draw subtitle
        subtitle_text = self.font_medium.render("Explore an alien world and discover reality-bending artifacts", True, GRAY)
        self.screen.blit(subtitle_text, (SCREEN_WIDTH//2 - subtitle_text.get_width()//2, 170))
        
        # Draw game description
        description = [
            "You find yourself on a strange alien planet filled with mysterious artifacts.",
            "Each artifact you collect will change the world and grant you new abilities.",
            "Find the ancient temple and unlock its secrets!",
            "",
            "Some artifacts are cursed and will burden you until cleansed at the temple.",
            "Experiment with artifact combinations to discover hidden passages."
        ]
        
        for i, line in enumerate(description):
            line_text = self.font_small.render(line, True, WHITE)
            self.screen.blit(line_text, (SCREEN_WIDTH//2 - line_text.get_width()//2, 250 + i * 30))
        
        # Draw start instruction
        if pygame.time.get_ticks() % 1000 < 500:  # Blink effect
            start_text = self.font_medium.render("Press ENTER to begin your expedition", True, YELLOW)
            self.screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 450))
    
    def draw_win_screen(self):
        """Draw the win screen"""
        # Fill background with triumphant color
        self.screen.fill((20, 50, 70))
        
        # Draw title
        title_text = self.font_large.render("Temple Secrets Unlocked!", True, YELLOW)
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
        
        # Draw description
        description = [
            "Congratulations! You've unlocked the temple's secrets!",
            "",
            "The ancient alien technology activates, revealing the truth about",
            "the civilization that created these reality-bending artifacts.",
            "",
            "Their knowledge and power is now yours to command...",
            "",
            "Until your next expedition!"
        ]
        
        for i, line in enumerate(description):
            line_text = self.font_medium.render(line, True, WHITE)
            self.screen.blit(line_text, (SCREEN_WIDTH//2 - line_text.get_width()//2, 200 + i * 40))
        
        # Draw restart instruction
        if pygame.time.get_ticks() % 1000 < 500:  # Blink effect
            restart_text = self.font_medium.render("Press ENTER to play again", True, GREEN)
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 500))
    
    def draw_game_over_screen(self):
        """Draw the game over screen"""
        # Fill background with dark color
        self.screen.fill((50, 20, 20))
        
        # Draw title
        title_text = self.font_large.render("Expedition Failed", True, RED)
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
        
        # Draw description
        description = [
            "Your expedition has ended in failure.",
            "",
            "The alien artifacts proved too powerful to control,",
            "and their combined effects have overwhelmed you.",
            "",
            "Perhaps another explorer will succeed where you failed..."
        ]
        
        for i, line in enumerate(description):
            line_text = self.font_medium.render(line, True, WHITE)
            self.screen.blit(line_text, (SCREEN_WIDTH//2 - line_text.get_width()//2, 200 + i * 40))
        
        # Draw restart instruction
        if pygame.time.get_ticks() % 1000 < 500:  # Blink effect
            restart_text = self.font_medium.render("Press ENTER to try again", True, YELLOW)
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 450))
    
    def check_win_condition(self):
        """Check if player has won the game"""
        # Win if player reaches the secret chamber after temple is unlocked
        if self.world.temple_unlocked:
            tile = self.world.tiles.get((self.player.x, self.player.y))
            if tile and tile.type == "win":
                self.state = GameState.WIN
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle input
            running = self.handle_input()
            
            # Process continuous input
            self.process_continuous_input()
            
            # Update game state
            if self.state == GameState.PLAYING:
                self.player.update()
                self.world.update()
                self.update_camera()
                self.check_win_condition()
                
                # Update controls timer
                if self.controls_timer > 0:
                    self.controls_timer -= 1
                    if self.controls_timer <= 0:
                        self.show_controls = False
            
            # Draw the current screen
            if self.state == GameState.TITLE:
                self.draw_title_screen()
            
            elif self.state == GameState.PLAYING:
                # Clear screen
                self.screen.fill((0, 0, 0))
                
                # Draw world
                self.world.draw(self.screen, int(self.camera_x), int(self.camera_y))
                
                # Draw player
                self.player.draw(self.screen, int(self.camera_x), int(self.camera_y))
                
                # Draw UI
                self.draw_ui()
            
            elif self.state == GameState.INVENTORY:
                # First draw the game world (will be overlaid)
                self.screen.fill((0, 0, 0))
                self.world.draw(self.screen, int(self.camera_x), int(self.camera_y))
                self.player.draw(self.screen, int(self.camera_x), int(self.camera_y))
                
                # Then draw inventory screen
                self.draw_inventory_screen()
            
            elif self.state == GameState.WIN:
                self.draw_win_screen()
            
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over_screen()
            
            # Update display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()