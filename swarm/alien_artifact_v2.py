import pygame
import sys
import math
import random
import time
from enum import Enum
from collections import defaultdict

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
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

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
    FUSION = 4
    RIFT = 5
    GAME_OVER = 6
    WIN = 7
    ENTANGLEMENT = 8  # Added for quantum entanglement mechanics

# New class for artifact power components
class ArtifactPower:
    def __init__(self, name, world_effect_func, player_effect_func, description):
        self.name = name
        self.world_effect_func = world_effect_func
        self.player_effect_func = player_effect_func
        self.description = description

# Dictionary to store artifact powers
ARTIFACT_POWERS = {}

# Add artifact powers (will be populated later)

class Artifact:
    def __init__(self, name, description, world_effect, player_effect, image_color, 
                 is_cursed=False, affinity=Affinity.NONE, powers=None):
        self.name = name
        self.description = description
        self.world_effect = world_effect
        self.player_effect = player_effect
        self.image_color = image_color
        self.is_cursed = is_cursed
        self.affinity = affinity
        self.curse_cleansed = False
        self.rect = pygame.Rect(0, 0, TILE_SIZE//2, TILE_SIZE//2)
        
        # New properties for v2 mechanics
        self.stability = 100.0  # 100% stable initially
        self.evolution_progress = 0.0  # 0% evolved initially
        self.last_used_position = None
        self.use_count = 0
        self.powers = powers or []  # For artifact evolution/fusion
        self.entangled_with = None  # For quantum entanglement
        self.last_activation_time = 0  # For quantum entanglement timing
        
    def draw(self, surface, x, y):
        self.rect.x, self.rect.y = x, y
        
        # Draw stability effect
        if self.stability < 100:
            # Jitter effect based on instability
            jitter = int((100 - self.stability) / 10)
            if jitter > 0:
                x += random.randint(-jitter, jitter)
                y += random.randint(-jitter, jitter)
        
        pygame.draw.rect(surface, self.image_color, pygame.Rect(x, y, self.rect.width, self.rect.height))
        
        # Draw border based on stability
        if self.stability < 30:
            border_color = RED  # Unstable
        elif self.stability < 70:
            border_color = YELLOW  # Warning
        else:
            border_color = WHITE  # Stable
            
        pygame.draw.rect(surface, border_color, pygame.Rect(x, y, self.rect.width, self.rect.height), 2)
        
        # Draw a symbol if cursed
        if self.is_cursed and not self.curse_cleansed:
            # Draw a small red X
            start1 = (x + 5, y + 5)
            end1 = (x + self.rect.width - 5, y + self.rect.height - 5)
            start2 = (x + 5, y + self.rect.height - 5)
            end2 = (x + self.rect.width - 5, y + 5)
            pygame.draw.line(surface, RED, start1, end1, 2)
            pygame.draw.line(surface, RED, start2, end2, 2)
        
        # Draw evolution progress indicator
        if self.evolution_progress > 0:
            progress_width = int((self.rect.width - 4) * (self.evolution_progress / 100))
            pygame.draw.rect(surface, GREEN, 
                            pygame.Rect(x + 2, y + self.rect.height - 6, progress_width, 4))
            
        # Draw entanglement indicator
        if self.entangled_with:
            pygame.draw.circle(surface, CYAN, 
                              (x + self.rect.width - 5, y + 5), 3)
    
    def apply_effect(self, game_world, player, position=None):
        """Apply the artifact's effect to the game world and player"""
        # Record position of use
        if position:
            self.last_used_position = position
            self.use_count += 1
        
        # Apply effects
        game_world.show_message(f"You activate the {self.name}.")
        game_world.show_message(f"WORLD EFFECT: {self.world_effect}")
        game_world.apply_artifact_effect(self)
        
        game_world.show_message(f"PLAYER EFFECT: {self.player_effect}")
        player.transform(self)
        
        # Track activation time for quantum entanglement
        self.last_activation_time = time.time()
        
        # Check for entangled artifact
        if self.entangled_with and self.entangled_with in player.inventory:
            time_delta = abs(time.time() - self.entangled_with.last_activation_time)
            # If time difference is small, get a beneficial effect
            if time_delta < 0.5:
                game_world.show_message("Perfect quantum synchronization!")
                # Both artifacts are stable
                self.stability = min(100, self.stability + 10)
                self.entangled_with.stability = min(100, self.entangled_with.stability + 10)
            else:
                # Random quantum effect based on time delta
                effect_seed = int(time_delta * 1000) % 3
                if effect_seed == 0:
                    game_world.show_message("Quantum interference! Effects amplified!")
                    # Apply both effects with double intensity
                    game_world.apply_artifact_effect(self.entangled_with)
                elif effect_seed == 1:
                    game_world.show_message("Quantum inversion! Effects reversed!")
                    # Reverse an effect (like gravity)
                    if "gravity" in self.world_effect.lower():
                        game_world.gravity_inverted = not game_world.gravity_inverted
                else:
                    game_world.show_message("Quantum disruption! Stability decreasing!")
                    # Both artifacts become less stable
                    self.stability = max(10, self.stability - 20)
                    self.entangled_with.stability = max(10, self.entangled_with.stability - 20)
        
        # Apply instability effects
        self.decrease_stability()
        
        # Check for dimensional rift
        if self.use_count >= 3 and self.last_used_position == position:
            game_world.show_message("The fabric of reality weakens... a dimensional rift forms!")
            game_world.create_rift(position[0], position[1])
        
        # Increase evolution progress
        self.evolution_progress += random.uniform(2.0, 5.0)
        if self.evolution_progress >= 100:
            game_world.show_message(f"The {self.name} is evolving!")
            self.evolve(game_world)
        
        # Check for curse
        if self.is_cursed and not self.curse_cleansed:
            game_world.show_message(f"WARNING: This artifact is cursed! {self.curse_effect()}")
            player.apply_curse(self)
    
    def decrease_stability(self):
        """Decrease artifact stability with each use"""
        stability_loss = random.uniform(5.0, 15.0)
        self.stability = max(0, self.stability - stability_loss)
        
        # If completely unstable, trigger a reality quake
        if self.stability <= 0:
            return True
        return False
    
    def repair(self, amount=25.0):
        """Repair artifact stability"""
        self.stability = min(100, self.stability + amount)
    
    def evolve(self, game_world):
        """Evolve the artifact into a more powerful form"""
        # Reset evolution progress
        self.evolution_progress = 0
        
        # Change appearance
        r, g, b = self.image_color
        self.image_color = (
            min(255, r + random.randint(0, 50)),
            min(255, g + random.randint(0, 50)),
            min(255, b + random.randint(0, 50))
        )
        
        # Enhance or change effects
        if "lens" in self.name.lower():
            self.name = "Enhanced Gravity Lens"
            self.world_effect = "Creates localized gravity wells"
            self.player_effect = "Allows you to manipulate gravity in a small area"
        elif "crystal" in self.name.lower():
            self.name = "Supercharged Phase Crystal"
            self.world_effect = "Creates persistent phase rifts in spacetime"
            self.player_effect = "Grants enhanced phasing abilities and partial invisibility"
        elif "scepter" in self.name.lower():
            self.name = "Grand Size Scepter"
            self.world_effect = "Causes dramatic environmental size fluctuations"
            self.player_effect = "Allows precise control over your size"
        elif "mask" in self.name.lower():
            self.name = "Ascendant Void Mask"
            self.world_effect = "Dramatically warps reality in unpredictable ways"
            self.player_effect = "Grants insight into chaos patterns, mitigating control inversion"
        else:
            # For fused artifacts
            self.name = "Evolved " + self.name
            self.world_effect += " (Enhanced)"
            self.player_effect += " (Enhanced)"
        
        game_world.show_message(f"The artifact has evolved into: {self.name}!")
        game_world.show_message(f"New effect: {self.world_effect}")
    
    def entangle_with(self, other_artifact):
        """Create quantum entanglement between artifacts"""
        self.entangled_with = other_artifact
        other_artifact.entangled_with = self
    
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

class ArtifactFusion:
    @staticmethod
    def fuse_artifacts(artifact1, artifact2):
        """Create a new artifact by fusing two existing ones"""
        # Create name
        name_parts = artifact1.name.split()[-1:] + artifact2.name.split()[-1:]
        new_name = f"Fused {name_parts[0]}-{name_parts[1]}"
        
        # Blend colors
        r1, g1, b1 = artifact1.image_color
        r2, g2, b2 = artifact2.image_color
        new_color = (
            (r1 + r2) // 2,
            (g1 + g2) // 2,
            (b1 + b2) // 2
        )
        
        # Create descriptions
        new_description = f"A fusion of {artifact1.name} and {artifact2.name}"
        
        # Combine effects
        world_effects = [artifact1.world_effect, artifact2.world_effect]
        player_effects = [artifact1.player_effect, artifact2.player_effect]
        
        # Determine if the fusion creates a curse
        is_cursed = artifact1.is_cursed or artifact2.is_cursed
        
        # Create fused effects with special combinations
        if ("gravity" in artifact1.world_effect.lower() and 
            "phase" in artifact2.player_effect.lower()):
            world_effect = "Creates gravity-phasing fields that allow selective matter tunneling"
            player_effect = "Grants ability to phase through solid objects in altered gravity"
        elif ("size" in artifact1.player_effect.lower() and 
              "control" in artifact2.player_effect.lower()):
            world_effect = "Creates zones of distorted spacetime and perception"
            player_effect = "Grants size control that inverts based on direction of movement"
        else:
            # Generic fusion
            world_effect = f"Combines '{artifact1.world_effect}' and '{artifact2.world_effect}'"
            player_effect = f"Combines '{artifact1.player_effect}' and '{artifact2.player_effect}'"
        
        # Create the new artifact
        fused_artifact = Artifact(
            name=new_name,
            description=new_description,
            world_effect=world_effect,
            player_effect=player_effect,
            image_color=new_color,
            is_cursed=is_cursed,
            affinity=random.choice(list(Affinity))
        )
        
        # If one artifact was entangled, transfer the entanglement
        if artifact1.entangled_with:
            fused_artifact.entangle_with(artifact1.entangled_with)
        elif artifact2.entangled_with:
            fused_artifact.entangle_with(artifact2.entangled_with)
        
        return fused_artifact

class DimensionalRift:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.max_radius = 40
        self.pulse_direction = 1  # 1 for expanding, -1 for contracting
        self.color = (100, 50, 150)  # Purple-ish
        self.alternate_reality = {}  # Dictionary to store alternate reality state
        self.lifespan = 600  # 10 seconds at 60 FPS
        self.active = True
        self.has_paradox = random.random() < 0.3  # 30% chance of paradox
        self.evil_clone = None
        
    def update(self):
        # Update rift appearance
        self.radius += 0.2 * self.pulse_direction
        if self.radius >= self.max_radius:
            self.pulse_direction = -1
        elif self.radius <= 20:
            self.pulse_direction = 1
        
        # Update lifespan
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.active = False
        
    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        if not self.active:
            return
            
        x = self.x * TILE_SIZE - camera_offset_x
        y = self.y * TILE_SIZE - camera_offset_y
        
        # Draw rift
        pygame.draw.circle(surface, self.color, (x + TILE_SIZE//2, y + TILE_SIZE//2), self.radius)
        
        # Draw inner rift
        inner_radius = max(5, self.radius - 10)
        pygame.draw.circle(surface, (200, 150, 255), (x + TILE_SIZE//2, y + TILE_SIZE//2), inner_radius)
        
        # Draw some sparkles
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.radius)
            sparkle_x = x + TILE_SIZE//2 + math.cos(angle) * distance
            sparkle_y = y + TILE_SIZE//2 + math.sin(angle) * distance
            pygame.draw.circle(surface, WHITE, (int(sparkle_x), int(sparkle_y)), 1)
    
    def is_player_inside(self, player):
        """Check if player is inside the rift"""
        player_center_x = player.x * TILE_SIZE + player.width // 2
        player_center_y = player.y * TILE_SIZE + player.height // 2
        rift_center_x = self.x * TILE_SIZE + TILE_SIZE // 2
        rift_center_y = self.y * TILE_SIZE + TILE_SIZE // 2
        
        distance = math.sqrt((player_center_x - rift_center_x)**2 + (player_center_y - rift_center_y)**2)
        return distance < self.radius
    
    def generate_alternate_reality(self, world):
        """Generate alternate reality version of the nearby area"""
        # Copy a portion of the world around the rift
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                tile_x, tile_y = self.x + dx, self.y + dy
                if (tile_x, tile_y) in world.tiles:
                    # Randomly alter some tiles
                    original_tile = world.tiles[(tile_x, tile_y)]
                    if random.random() < 0.3:  # 30% chance to alter
                        if original_tile.type == "floor":
                            self.alternate_reality[(tile_x, tile_y)] = "wall" if random.random() < 0.5 else "water"
                        elif original_tile.type == "wall":
                            self.alternate_reality[(tile_x, tile_y)] = "floor"
        
        # Create paradox if needed
        if self.has_paradox:
            # Find a point for the paradox
            paradox_x, paradox_y = self.x + random.randint(-3, 3), self.y + random.randint(-3, 3)
            if (paradox_x, paradox_y) in world.tiles:
                # Mark this location for the paradox
                self.alternate_reality[(paradox_x, paradox_y)] = "paradox"
    
    def spawn_evil_clone(self, player, world):
        """Spawn an evil clone of the player from the rift"""
        if random.random() < 0.2 and not self.evil_clone:  # 20% chance
            self.evil_clone = EvilClone(self.x, self.y, player)
            world.show_message("An evil version of you emerges from the rift!")
            return self.evil_clone
        return None

class EvilClone:
    def __init__(self, x, y, original_player):
        self.x = x
        self.y = y
        self.width = original_player.width
        self.height = original_player.height
        self.color = (200, 0, 0)  # Red color for evil clone
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, self.width, self.height)
        self.health = 3
        self.direction = Direction.DOWN
        self.speed = 0.05
        self.last_move_time = time.time()
        self.animation_offset = 0
    
    def update(self, player, world):
        # Move toward player occasionally
        current_time = time.time()
        if current_time - self.last_move_time > self.speed:
            self.last_move_time = current_time
            
            # Determine direction to player
            dx = player.x - self.x
            dy = player.y - self.y
            
            # Move in the primary direction
            if abs(dx) > abs(dy):
                self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                new_x = self.x + (1 if dx > 0 else -1)
                new_y = self.y
            else:
                self.direction = Direction.DOWN if dy > 0 else Direction.UP
                new_x = self.x
                new_y = self.y + (1 if dy > 0 else -1)
            
            # Check if movement is valid
            if world.is_valid_move(self, new_x, new_y):
                self.x, self.y = new_x, new_y
                self.rect.x = self.x * TILE_SIZE
                self.rect.y = self.y * TILE_SIZE
            
            # Check for collision with player
            if self.x == player.x and self.y == player.y:
                # Attack player
                player.take_damage(1)
                world.show_message("Your evil clone attacks you!")
        
        # Update animation
        self.animation_offset = int(math.sin(pygame.time.get_ticks() * 0.01) * 3)
    
    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        x = self.rect.x - camera_offset_x
        y = self.rect.y - camera_offset_y + self.animation_offset
        
        # Draw clone with current appearance
        clone_rect = pygame.Rect(x, y, self.width, self.height)
        
        # Draw the clone
        pygame.draw.rect(surface, self.color, clone_rect, border_radius=8)
        
        # Draw direction indicator (eyes)
        eye_size = max(4, int(self.width / 8))
        
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
        
        # Draw health indicators
        for i in range(self.health):
            pygame.draw.rect(surface, GREEN, (x + i*8, y - 10, 6, 6))
    
    def take_damage(self):
        """Clone takes damage"""
        self.health -= 1
        return self.health <= 0  # Return True if destroyed

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
        
        # New properties for v2
        self.health = 5
        self.max_health = 5
        self.is_in_rift = False
        self.current_rift = None
        self.last_reality_quake = 0
        self.quake_effects = []
    
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
            else:
                # For evolved artifacts with more control
                size_change = random.choice([0.5, 0.7, 1.0, 1.5, 2.0])
                self.size = size_change
                self.width = int(TILE_SIZE * size_change)
                self.height = int(TILE_SIZE * size_change)
                
            self.rect.width, self.rect.height = self.width, self.height
        
        if "control" in artifact.player_effect.lower():
            if "mitigating" in artifact.player_effect.lower():
                # For evolved artifacts that help with controls
                self.inverted_controls = False
            else:
                self.inverted_controls = not self.inverted_controls
        
        if "phase" in artifact.player_effect.lower():
            self.can_phase = True
            # Enhanced phasing from evolved artifacts
            if "enhanced" in artifact.player_effect.lower():
                self.movement_range = 2
    
    def collect_artifact(self, artifact, game_world):
        """Add artifact to inventory and apply its effects"""
        self.inventory.append(artifact)
        artifact.apply_effect(game_world, self, (self.x, self.y))
        
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
    
    def take_damage(self, amount):
        """Player takes damage"""
        self.health -= amount
        return self.health <= 0  # Return True if dead
    
    def heal(self, amount):
        """Heal the player"""
        self.health = min(self.max_health, self.health + amount)
    
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
        
        # Check if movement is valid, considering alternate reality if in a rift
        if self.is_in_rift and self.current_rift:
            # Check paradox
            if (new_x, new_y) in self.current_rift.alternate_reality:
                tile_type = self.current_rift.alternate_reality[(new_x, new_y)]
                if tile_type == "paradox":
                    game_world.trigger_paradox(new_x, new_y)
                    return False
                    
            # Check alternate reality movement rules
            can_move = True
            if (new_x, new_y) in self.current_rift.alternate_reality:
                tile_type = self.current_rift.alternate_reality[(new_x, new_y)]
                if tile_type == "wall" and not self.can_phase:
                    can_move = False
                elif tile_type == "water" and self.size > 1.0:
                    can_move = False
            
            if not can_move:
                game_world.show_message("You can't move there in this reality.")
                return False
        
        # Check if movement is valid in normal reality
        if game_world.is_valid_move(self, new_x, new_y):
            self.x, self.y = new_x, new_y
            self.rect.x = self.x * TILE_SIZE
            self.rect.y = self.y * TILE_SIZE
            
            # Start movement animation
            self.animation_timer = 10
            
            # Check for rifts at new position
            if not self.is_in_rift:
                for rift in game_world.rifts:
                    if rift.active and rift.is_player_inside(self):
                        self.is_in_rift = True
                        self.current_rift = rift
                        game_world.show_message("You enter a dimensional rift! Reality seems... different here.")
                        break
            else:
                # Check if still in rift
                still_in_rift = False
                if self.current_rift and self.current_rift.active:
                    still_in_rift = self.current_rift.is_player_inside(self)
                
                if not still_in_rift:
                    self.is_in_rift = False
                    self.current_rift = None
                    game_world.show_message("You exit the dimensional rift and return to normal reality.")
            
            # Check for artifacts at new position
            game_world.check_location_features(self)
            
            # Check for evil clones
            game_world.check_evil_clone_collision(self)
            
            return True
        else:
            return False
    
    def update(self):
        # Update animation
        if self.animation_timer > 0:
            self.animation_timer -= 1
            # Calculate bob effect (move up and down slightly)
            self.animation_offset = int(math.sin(pygame.time.get_ticks() * 0.01) * 3)
        
        # Apply reality quake effects if active
        if time.time() - self.last_reality_quake < 10:  # Quake lasts 10 seconds
            # Random effects
            if "inverted_controls" in self.quake_effects:
                self.inverted_controls = True
            if "phasing" in self.quake_effects:
                self.can_phase = True
            if "size_shift" in self.quake_effects:
                if pygame.time.get_ticks() % 300 < 150:  # Oscillate size
                    self.size = 0.7
                    self.width = int(TILE_SIZE * 0.7)
                    self.height = int(TILE_SIZE * 0.7)
                else:
                    self.size = 1.3
                    self.width = int(TILE_SIZE * 1.3)
                    self.height = int(TILE_SIZE * 1.3)
                self.rect.width, self.rect.height = self.width, self.height
        else:
            # Clear quake effects
            if self.quake_effects:
                self.quake_effects = []
                # Reset some effects
                if not any("control" in a.player_effect.lower() for a in self.inventory):
                    self.inverted_controls = False
                if not any("phase" in a.player_effect.lower() for a in self.inventory):
                    self.can_phase = False
    
    def trigger_reality_quake(self, game_world):
        """Trigger a reality quake from artifact instability"""
        self.last_reality_quake = time.time()
        
        # Random quake effects
        possible_effects = ["inverted_controls", "phasing", "size_shift", 
                           "gravity_flux", "teleportation", "visual_glitch"]
        self.quake_effects = random.sample(possible_effects, k=random.randint(1, 3))
        
        game_world.show_message("REALITY QUAKE! The fabric of reality trembles from artifact instability!")
        effect_desc = []
        for effect in self.quake_effects:
            if effect == "inverted_controls":
                effect_desc.append("Controls are inverted")
            elif effect == "phasing":
                effect_desc.append("You can phase through walls")
            elif effect == "size_shift":
                effect_desc.append("Your size is fluctuating")
            elif effect == "gravity_flux":
                game_world.gravity_inverted = not game_world.gravity_inverted
                effect_desc.append("Gravity is fluctuating")
            elif effect == "teleportation":
                # Teleport to a random valid location
                valid_tiles = []
                for (x, y), tile in game_world.tiles.items():
                    if tile.type == "floor" and tile.walkable:
                        valid_tiles.append((x, y))
                
                if valid_tiles:
                    x, y = random.choice(valid_tiles)
                    self.x, self.y = x, y
                    self.rect.x = x * TILE_SIZE
                    self.rect.y = y * TILE_SIZE
                    effect_desc.append("You were teleported")
            elif effect == "visual_glitch":
                effect_desc.append("Visual distortions")
        
        game_world.show_message("Effects: " + ", ".join(effect_desc))
    
    def attempt_artifact_fusion(self, artifact1, artifact2, game_world):
        """Attempt to fuse two artifacts"""
        if not artifact1 or not artifact2 or artifact1 == artifact2:
            game_world.show_message("You need to select two different artifacts to fuse.")
            return None
        
        # Remove artifacts from inventory
        self.inventory.remove(artifact1)
        self.inventory.remove(artifact2)
        
        # Create fused artifact
        fused = ArtifactFusion.fuse_artifacts(artifact1, artifact2)
        game_world.show_message(f"You've created a new artifact: {fused.name}!")
        
        # Add to inventory
        self.inventory.append(fused)
        self.selected_artifact = fused
        
        return fused
    
    def attempt_entanglement(self, artifact1, artifact2, game_world):
        """Attempt to entangle two artifacts"""
        if not artifact1 or not artifact2 or artifact1 == artifact2:
            game_world.show_message("You need to select two different artifacts to entangle.")
            return False
        
        # Check if either is already entangled
        if artifact1.entangled_with or artifact2.entangled_with:
            game_world.show_message("One of these artifacts is already entangled with another.")
            return False
        
        # Create entanglement
        artifact1.entangle_with(artifact2)
        game_world.show_message(f"You've quantum entangled {artifact1.name} with {artifact2.name}!")
        game_world.show_message("When one is activated, the other will respond based on timing.")
        
        return True
    
    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        x = self.rect.x - camera_offset_x
        y = self.rect.y - camera_offset_y + self.animation_offset
        
        # Draw player with current appearance
        player_rect = pygame.Rect(x, y, self.width, self.height)
        
        # Apply reality quake visual effects
        if time.time() - self.last_reality_quake < 10 and "visual_glitch" in self.quake_effects:
            # Visual glitching - draw multiple overlapping semi-transparent players
            for _ in range(3):
                glitch_x = x + random.randint(-5, 5)
                glitch_y = y + random.randint(-5, 5)
                glitch_rect = pygame.Rect(glitch_x, glitch_y, self.width, self.height)
                glitch_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.rect(glitch_surface, (*self.color, 100), 
                                pygame.Rect(0, 0, self.width, self.height), border_radius=8)
                surface.blit(glitch_surface, (glitch_x, glitch_y))
        
        # Choose color based on state
        color = self.color
        if self.cursed:
            color = (200, 100, 100)  # Reddish when cursed
        
        # Draw differently if in a rift
        if self.is_in_rift:
            # Add a shimmer effect
            shimmer_color = (color[0], color[1], min(255, color[2] + 50))
            shimmer_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(shimmer_surface, (*shimmer_color, 180), 
                            pygame.Rect(0, 0, self.width, self.height), border_radius=8)
            surface.blit(shimmer_surface, (x, y))
        else:
            # Normal drawing
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
        
        # Draw health bar
        health_width = int((self.width - 4) * (self.health / self.max_health))
        health_bg = pygame.Rect(x + 2, y - 8, self.width - 4, 6)
        health_bar = pygame.Rect(x + 2, y - 8, health_width, 6)
        pygame.draw.rect(surface, (100, 0, 0), health_bg)
        pygame.draw.rect(surface, (200, 0, 0), health_bar)

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
        
        # For paradox tiles
        self.is_paradox = False
        self.paradox_timer = 0
        
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
                
        elif self.type == "win":
            # Special tile for win condition
            pygame.draw.rect(surface, (80, 70, 120), (x, y, TILE_SIZE, TILE_SIZE))
            # Add glowing effect
            glow_size = 5 + int(math.sin(pygame.time.get_ticks() * 0.01) * 3)
            pygame.draw.rect(surface, (200, 180, 255), 
                            (x + TILE_SIZE//2 - glow_size, 
                             y + TILE_SIZE//2 - glow_size, 
                             glow_size*2, glow_size*2))
        
        # Draw paradox effect if active
        if self.is_paradox:
            # Swirling paradox effect
            time_factor = pygame.time.get_ticks() * 0.01
            for i in range(5):
                angle = time_factor + i * (2 * math.pi / 5)
                radius = 10 + i * 3
                px = x + TILE_SIZE//2 + int(math.cos(angle) * radius)
                py = y + TILE_SIZE//2 + int(math.sin(angle) * radius)
                pygame.draw.circle(surface, (255, 50, 255), (px, py), 3)
            
            # Countdown visual
            if self.paradox_timer > 0:
                # Draw countdown
                progress = min(1.0, self.paradox_timer / 300)  # 300 frames = 5 seconds
                pygame.draw.arc(surface, RED, 
                               (x + 5, y + 5, TILE_SIZE - 10, TILE_SIZE - 10),
                               0, progress * 2 * math.pi, 3)
        
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
        
        # For v2 mechanics
        self.rifts = []  # List of dimensional rifts
        self.evil_clones = []  # List of evil clones
        self.paradox_tiles = []  # List of tiles with active paradoxes
        self.last_reality_quake = 0
        
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
    
    def is_valid_move(self, entity, new_x, new_y):
        """Check if the entity can move to the new position"""
        # Check if the tile exists and is walkable
        tile = self.tiles.get((new_x, new_y))
        if not tile or not tile.walkable:
            # If entity can phase (player), they can move through walls
            if hasattr(entity, "can_phase") and entity.can_phase and tile:
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
        
        # Check if artifact is stable enough
        if artifact.stability < 30:
            self.show_message(f"The {artifact.name} is too unstable to place! Repair it first.")
            return False
        
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
            has_size = any("size" in a.player_effect.lower() for a in pedestal_artifacts)
            has_void = any("void" in a.name.lower() for a in pedestal_artifacts)
            
            # Different combinations unlock different temple features
            if has_gravity and has_phase:
                self.show_message("**** The temple responds to gravity and phase artifacts! ****")
                self.show_message("A hidden door slides open, revealing a secret chamber.")
                self.temple_unlocked = True
                self.create_secret_chamber("phase")
                return True
            elif has_size and has_void:
                self.show_message("**** The temple responds to size and void artifacts! ****")
                self.show_message("Reality warps, creating a chaotic but navigable path.")
                self.temple_unlocked = True
                self.create_secret_chamber("void")
                return True
            elif len(set([a.affinity for a in pedestal_artifacts])) == 4:
                # All four different affinities
                self.show_message("**** The temple resonates with the diverse affinities! ****")
                self.show_message("Multiple pathways appear, converging on a central chamber.")
                self.temple_unlocked = True
                self.create_secret_chamber("affinity")
                return True
            else:
                self.show_message("The temple stirs but remains dormant. Perhaps a different combination is needed.")
        
        return False
    
    def create_secret_chamber(self, chamber_type):
        """Create a secret chamber based on the artifact combination"""
        # Find a good location near the temple
        temple_center = None
        for x, y in self.temples:
            if self.tiles[(x, y)].is_pedestal:
                temple_center = (x, y)
                break
        
        if not temple_center:
            # Fallback
            temple_center = self.temples[0] if self.temples else (20, 20)
        
        # Choose direction based on chamber type
        if chamber_type == "phase":
            # Create chamber above
            chamber_start = (temple_center[0] - 2, temple_center[1] - 5)
            width, height = 5, 5
        elif chamber_type == "void":
            # Create chamber to the side
            chamber_start = (temple_center[0] + 3, temple_center[1] - 2)
            width, height = 5, 5
        else:  # affinity
            # Create chamber below
            chamber_start = (temple_center[0] - 3, temple_center[1] + 3)
            width, height = 7, 5
        
        # Create the chamber
        for dx in range(width):
            for dy in range(height):
                x, y = chamber_start[0] + dx, chamber_start[1] + dy
                
                # Skip if tile exists already
                if (x, y) in self.tiles:
                    continue
                    
                # Create walls around edges, floor in middle
                if dx == 0 or dy == 0 or dx == width-1 or dy == height-1:
                    self.tiles[(x, y)] = Tile(x, y, "wall", walkable=False)
                else:
                    new_tile = Tile(x, y, "floor")
                    new_tile.is_temple = True
                    self.tiles[(x, y)] = new_tile
                    self.temples.append((x, y))
        
        # Add special win tile in the center
        center_x = chamber_start[0] + width // 2
        center_y = chamber_start[1] + height // 2
        if (center_x, center_y) in self.tiles:
            self.tiles[(center_x, center_y)].type = "win"
        
        # Create a path from the temple to the secret chamber
        self.create_path(temple_center, (center_x, center_y), chamber_type)
    
    def create_path(self, start, end, path_type):
        """Create a path between two points"""
        # Simple path creation
        current = start
        steps = 0
        max_steps = 20  # Prevent infinite loops
        
        while current != end and steps < max_steps:
            # Determine next step direction
            if path_type == "void":
                # Chaotic path
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                dx, dy = random.choice(directions)
                while not self.is_valid_path_direction(current, (dx, dy)):
                    dx, dy = random.choice(directions)
            else:
                # More direct path
                dx = 1 if end[0] > current[0] else -1 if end[0] < current[0] else 0
                dy = 1 if end[1] > current[1] else -1 if end[1] < current[1] else 0
            
            # Move in that direction
            next_pos = (current[0] + dx, current[1] + dy)
            
            # Create or modify tile
            if next_pos not in self.tiles:
                new_tile = Tile(next_pos[0], next_pos[1], "floor")
                new_tile.is_temple = True
                self.tiles[next_pos] = new_tile
                self.temples.append(next_pos)
            elif self.tiles[next_pos].type == "wall":
                self.tiles[next_pos] = Tile(next_pos[0], next_pos[1], "floor")
                self.tiles[next_pos].is_temple = True
                self.temples.append(next_pos)
            
            current = next_pos
            steps += 1
    
    def is_valid_path_direction(self, current, direction):
        """Check if a path direction is valid"""
        dx, dy = direction
        next_pos = (current[0] + dx, current[1] + dy)
        
        # Don't move away from the map boundaries
        if next_pos[0] < 0 or next_pos[0] > 40 or next_pos[1] < 0 or next_pos[1] > 25:
            return False
        
        return True
    
    def apply_artifact_effect(self, artifact):
        """Apply an artifact's effect to the game world"""
        self.artifact_effects.append(artifact.world_effect)
        
        if "gravity" in artifact.world_effect.lower():
            self.gravity_inverted = not self.gravity_inverted
            self.show_message("The gravity has been inverted! Up is now down, and down is now up.")
        
        if "warp" in artifact.world_effect.lower() or "distort" in artifact.world_effect.lower():
            self.landscape_warped = True
            self.show_message("The landscape around you begins to warp and distort in strange ways.")
        
        # Check for artifact breaking
        if artifact.decrease_stability():
            self.trigger_reality_quake(artifact)
    
    def trigger_reality_quake(self, artifact):
        """Trigger a reality quake from an unstable artifact"""
        self.last_reality_quake = time.time()
        self.show_message(f"The {artifact.name} becomes unstable and triggers a REALITY QUAKE!")
        
        # Repair artifact after quake
        artifact.stability = 30
        
        # Apply random environment changes
        num_changes = random.randint(3, 7)
        for _ in range(num_changes):
            # Pick a random tile to change
            tiles = list(self.tiles.values())
            tile = random.choice(tiles)
            
            # Apply a random change
            change_type = random.randint(0, 3)
            if change_type == 0 and tile.type == "floor":
                # Change floor to water
                tile.type = "water"
            elif change_type == 1 and tile.type == "wall":
                # Change wall to floor
                tile.type = "floor"
                tile.walkable = True
            elif change_type == 2 and tile.type != "win":
                # Swap colors
                if hasattr(tile, 'color'):
                    r, g, b = tile.color
                    tile.color = (b, r, g)
        
        # Also create a random rift
        x, y = random.randint(5, 35), random.randint(5, 20)
        self.create_rift(x, y)
    
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
    
    def repair_artifact(self, player):
        """Repair the selected artifact's stability"""
        if not player.selected_artifact:
            self.show_message("You need to select an artifact first (1-9 keys).")
            return False
        
        artifact = player.selected_artifact
        if artifact.stability >= 100:
            self.show_message(f"The {artifact.name} is already at maximum stability.")
            return False
        
        # Check if at temple
        tile = self.tiles.get((player.x, player.y))
        if not tile or not tile.is_temple:
            self.show_message("You can only repair artifacts at the temple.")
            return False
        
        # Repair artifact
        artifact.repair()
        self.show_message(f"The {artifact.name} has been repaired and is more stable now.")
        return True
    
    def create_rift(self, x, y):
        """Create a dimensional rift at the specified location"""
        # Check if there's already a rift nearby
        for rift in self.rifts:
            if rift.active and abs(rift.x - x) + abs(rift.y - y) < 5:
                return None  # Too close to another rift
        
        # Create a new rift
        rift = DimensionalRift(x, y)
        self.rifts.append(rift)
        
        # Generate alternate reality for the rift
        rift.generate_alternate_reality(self)
        
        return rift
    
    def check_evil_clone_collision(self, player):
        """Check for collisions with evil clones"""
        for clone in self.evil_clones:
            if clone.x == player.x and clone.y == player.y:
                # Player attacks clone
                if clone.take_damage():
                    # Clone is defeated
                    self.show_message("You defeat your evil clone!")
                    self.evil_clones.remove(clone)
                else:
                    self.show_message("You strike your evil clone!")
    
    def trigger_paradox(self, x, y):
        """Trigger a paradox at the specified location"""
        self.show_message("PARADOX DETECTED! The fabric of reality is tearing!")
        
        # Create a paradox tile
        if (x, y) in self.tiles:
            tile = self.tiles[(x, y)]
            tile.is_paradox = True
            tile.paradox_timer = 300  # 5 seconds at 60 FPS
            self.paradox_tiles.append(tile)
            
            # After the timer, modify reality
            # This will be checked in the update method
    
    def update_paradoxes(self):
        """Update paradox effects"""
        for tile in self.paradox_tiles[:]:
            if tile.paradox_timer > 0:
                tile.paradox_timer -= 1
                if tile.paradox_timer <= 0:
                    # Paradox resolves and changes reality
                    self.show_message("The paradox resolves, altering reality!")
                    
                    # Create a new path or modify the terrain
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            x, y = tile.x + dx, tile.y + dy
                            if (x, y) in self.tiles and random.random() < 0.5:
                                if self.tiles[(x, y)].type == "wall":
                                    self.tiles[(x, y)] = Tile(x, y, "floor")
                                elif self.tiles[(x, y)].type == "floor":
                                    if random.random() < 0.3:
                                        self.tiles[(x, y)] = Tile(x, y, "wall", walkable=False)
                    
                    # Remove from active paradoxes
                    tile.is_paradox = False
                    self.paradox_tiles.remove(tile)
    
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
        
        # Update rifts
        for rift in self.rifts[:]:
            rift.update()
            if not rift.active:
                self.rifts.remove(rift)
        
        # Update evil clones
        for clone in self.evil_clones[:]:
            clone.update(None, self)  # Will be updated with player in game.py
        
        # Update paradoxes
        self.update_paradoxes()
    
    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        """Draw the world"""
        # Apply reality quake visual effects
        quake_active = time.time() - self.last_reality_quake < 10
        
        # Loop all world tiles
        for coords, tile in self.tiles.items():
            if quake_active and random.random() < 0.01:
                # Skip some tiles randomly during quake for glitch effect
                continue
                
            tile.draw(surface, camera_offset_x, camera_offset_y)
        
        # Draw rifts
        for rift in self.rifts:
            rift.draw(surface, camera_offset_x, camera_offset_y)
        
        # Draw evil clones
        for clone in self.evil_clones:
            clone.draw(surface, camera_offset_x, camera_offset_y)
        
        # Draw reality quake effects
        if quake_active:
            # Visual distortions
            for _ in range(5):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                width = random.randint(20, 100)
                height = random.randint(10, 30)
                
                # Create a glitchy rectangle
                glitch_surface = pygame.Surface((width, height), pygame.SRCALPHA)
                glitch_color = (random.randint(50, 255), random.randint(50, 255), 
                               random.randint(50, 255), random.randint(30, 100))
                pygame.draw.rect(glitch_surface, glitch_color, (0, 0, width, height))
                surface.blit(glitch_surface, (x, y))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Alien Artifact Explorer v2")
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
        self.show_controls = True  # Controls visibility flag
        self.controls_timer = 0  # Remove auto-hide timer
        
        # For fusion mechanic
        self.fusion_artifacts = [None, None]
        
        # For entanglement
        self.entanglement_artifacts = [None, None]
    
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
        status_surface = pygame.Surface((200, 120))
        status_surface.set_alpha(180)
        status_surface.fill(BLACK)
        self.screen.blit(status_surface, (10, 10))
        
        # Draw status text
        status_text = [f"Health: {self.player.health}/{self.player.max_health}"]
        if self.player.inverted_controls:
            status_text.append("Controls: INVERTED")
        if self.player.can_phase:
            status_text.append("Phasing: ACTIVE")
        if self.player.cursed:
            status_text.append("Cursed: YES")
        if self.player.size != 1.0:
            size_text = "Size: LARGE" if self.player.size > 1.0 else "Size: SMALL"
            status_text.append(size_text)
        if self.player.is_in_rift:
            status_text.append("IN RIFT DIMENSION")
        
        for i, text in enumerate(status_text):
            text_surface = self.font_small.render(text, True, YELLOW)
            self.screen.blit(text_surface, (20, 15 + i * 20))
        
        # Draw selected artifact info
        if self.player.selected_artifact:
            artifact = self.player.selected_artifact
            selected_text = f"Selected: {artifact.name}"
            stability_text = f"Stability: {int(artifact.stability)}%"
            evolution_text = f"Evolution: {int(artifact.evolution_progress)}%"
            
            selected_surface = self.font_small.render(selected_text, True, WHITE)
            stability_color = GREEN if artifact.stability > 70 else YELLOW if artifact.stability > 30 else RED
            stability_surface = self.font_small.render(stability_text, True, stability_color)
            evolution_surface = self.font_small.render(evolution_text, True, CYAN)
            
            self.screen.blit(selected_surface, (SCREEN_WIDTH - 200, 15))
            self.screen.blit(stability_surface, (SCREEN_WIDTH - 200, 35))
            self.screen.blit(evolution_surface, (SCREEN_WIDTH - 200, 55))
        
        # Draw controls help (temporary)
        if self.show_controls:
            help_surface = pygame.Surface((320, 220))
            help_surface.set_alpha(200)
            help_surface.fill(BLACK)
            self.screen.blit(help_surface, (SCREEN_WIDTH - 330, 80))
            
            controls = [
                "Controls:",
                "Arrow Keys: Move",
                "E: Collect Artifact",
                "1-9: Select Artifact",
                "P: Place on Pedestal",
                "R: Repair Artifact",
                "C: Cleanse Artifact",
                "F: Fusion Menu",
                "Q: Quantum Entangle",
                "I: Inventory",
                "ESC: Quit"
            ]
            
            for i, text in enumerate(controls):
                text_surface = self.font_small.render(text, True, WHITE)
                self.screen.blit(text_surface, (SCREEN_WIDTH - 320, 85 + i * 20))
        
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
    
    def draw_fusion_screen(self):
        """Draw the artifact fusion screen"""
        # Draw semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title_text = self.font_large.render("Artifact Fusion", True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 30))
        
        # Draw instruction
        instruction_text = self.font_medium.render("Select two artifacts to fuse", True, YELLOW)
        self.screen.blit(instruction_text, (SCREEN_WIDTH//2 - instruction_text.get_width()//2, 80))
        
        # Draw slots for the two artifacts
        slot_width, slot_height = 150, 150
        slot1_rect = pygame.Rect(SCREEN_WIDTH//4 - slot_width//2, 150, slot_width, slot_height)
        slot2_rect = pygame.Rect(SCREEN_WIDTH*3//4 - slot_width//2, 150, slot_width, slot_height)
        
        pygame.draw.rect(self.screen, DARK_GRAY, slot1_rect)
        pygame.draw.rect(self.screen, WHITE, slot1_rect, 2)
        pygame.draw.rect(self.screen, DARK_GRAY, slot2_rect)
        pygame.draw.rect(self.screen, WHITE, slot2_rect, 2)
        
        # Draw fusion arrow
        arrow_points = [
            (SCREEN_WIDTH//2 - 50, 200),
            (SCREEN_WIDTH//2 + 50, 200),
            (SCREEN_WIDTH//2, 250)
        ]
        pygame.draw.polygon(self.screen, YELLOW, arrow_points)
        
        # Draw selected artifacts
        for i, artifact in enumerate(self.fusion_artifacts):
            if artifact:
                slot_rect = slot1_rect if i == 0 else slot2_rect
                # Draw larger artifact
                pygame.draw.rect(self.screen, artifact.image_color, 
                                pygame.Rect(slot_rect.x + 25, slot_rect.y + 25, 
                                           slot_rect.width - 50, slot_rect.height - 50))
                # Draw name
                name_surface = self.font_small.render(artifact.name, True, WHITE)
                self.screen.blit(name_surface, 
                                (slot_rect.x + slot_rect.width//2 - name_surface.get_width()//2, 
                                 slot_rect.y + slot_rect.height + 10))
        
        # Draw available artifacts
        if self.player.inventory:
            for i, artifact in enumerate(self.player.inventory):
                if artifact not in self.fusion_artifacts:
                    x = 50 + i * 80
                    y = 350
                    artifact.draw(self.screen, x, y)
                    # Draw number
                    num_text = self.font_small.render(str(i+1), True, WHITE)
                    self.screen.blit(num_text, (x, y - 20))
        
        # Draw fusion button
        if all(self.fusion_artifacts):
            button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 450, 200, 50)
            pygame.draw.rect(self.screen, GREEN, button_rect)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2)
            
            button_text = self.font_medium.render("FUSE", True, BLACK)
            self.screen.blit(button_text, 
                            (button_rect.x + button_rect.width//2 - button_text.get_width()//2, 
                             button_rect.y + button_rect.height//2 - button_text.get_height()//2))
        
        # Draw back button
        back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 520, 200, 40)
        pygame.draw.rect(self.screen, RED, back_rect)
        pygame.draw.rect(self.screen, WHITE, back_rect, 2)
        
        back_text = self.font_medium.render("BACK", True, BLACK)
        self.screen.blit(back_text, 
                        (back_rect.x + back_rect.width//2 - back_text.get_width()//2, 
                         back_rect.y + back_rect.height//2 - back_text.get_height()//2))
    
    def draw_rift_screen(self):
        """Draw the rift view screen"""
        # First draw the game world with alternate reality overlay
        self.screen.fill((0, 0, 0))
        
        # Draw normal world first
        self.world.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw alternate reality overlay for the current rift
        if self.player.current_rift and self.player.current_rift.alternate_reality:
            # Semi-transparent overlay
            rift_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            # Draw altered tiles
            for (x, y), tile_type in self.player.current_rift.alternate_reality.items():
                screen_x = x * TILE_SIZE - int(self.camera_x)
                screen_y = y * TILE_SIZE - int(self.camera_y)
                
                # Skip if off screen
                if (screen_x < -TILE_SIZE or screen_x > SCREEN_WIDTH or 
                    screen_y < -TILE_SIZE or screen_y > SCREEN_HEIGHT):
                    continue
                
                # Draw different tile types with transparency
                if tile_type == "wall":
                    pygame.draw.rect(rift_overlay, (*DARK_GRAY, 150), 
                                    (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                elif tile_type == "water":
                    pygame.draw.rect(rift_overlay, (*BLUE, 150), 
                                    (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                elif tile_type == "paradox":
                    # Swirling effect for paradox
                    time_factor = pygame.time.get_ticks() * 0.01
                    for i in range(5):
                        angle = time_factor + i * (2 * math.pi / 5)
                        radius = 10 + i * 3
                        px = screen_x + TILE_SIZE//2 + int(math.cos(angle) * radius)
                        py = screen_y + TILE_SIZE//2 + int(math.sin(angle) * radius)
                        pygame.draw.circle(rift_overlay, (255, 50, 255, 200), (px, py), 3)
            
            # Draw the overlay
            self.screen.blit(rift_overlay, (0, 0))
        
        # Draw rift visual effects
        if self.player.is_in_rift:
            # Add edge distortion
            edge_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            for i in range(20):
                thickness = 3
                alpha = 150 - i * 7
                if alpha <= 0:
                    break
                pygame.draw.rect(edge_surface, (100, 50, 150, alpha), 
                                (i*thickness, i*thickness, 
                                 SCREEN_WIDTH - i*thickness*2, SCREEN_HEIGHT - i*thickness*2), 
                                thickness)
            self.screen.blit(edge_surface, (0, 0))
            
            # Add "rift dimension" text
            rift_text = self.font_medium.render("RIFT DIMENSION", True, (200, 100, 255))
            self.screen.blit(rift_text, (SCREEN_WIDTH//2 - rift_text.get_width()//2, 20))
        
        # Draw player and UI on top
        self.player.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw evil clones
        for clone in self.world.evil_clones:
            clone.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw UI
        self.draw_ui()
    
    def draw_entanglement_screen(self):
        """Draw the quantum entanglement screen"""
        # Draw semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title_text = self.font_large.render("Quantum Entanglement", True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 30))
        
        # Draw instruction
        instruction_text = self.font_medium.render("Select two artifacts to entangle", True, CYAN)
        self.screen.blit(instruction_text, (SCREEN_WIDTH//2 - instruction_text.get_width()//2, 80))
        
        # Draw explanation
        explanation_text = [
            "Entangled artifacts will activate together.",
            "Time your activations for optimal effects.",
            "The closer to simultaneous, the more predictable the outcome."
        ]
        
        for i, text in enumerate(explanation_text):
            text_surface = self.font_small.render(text, True, GRAY)
            self.screen.blit(text_surface, 
                            (SCREEN_WIDTH//2 - text_surface.get_width()//2, 
                             120 + i * 25))
        
        # Draw slots for the two artifacts
        slot_width, slot_height = 150, 150
        slot1_rect = pygame.Rect(SCREEN_WIDTH//4 - slot_width//2, 200, slot_width, slot_height)
        slot2_rect = pygame.Rect(SCREEN_WIDTH*3//4 - slot_width//2, 200, slot_width, slot_height)
        
        pygame.draw.rect(self.screen, DARK_GRAY, slot1_rect)
        pygame.draw.rect(self.screen, CYAN, slot1_rect, 2)
        pygame.draw.rect(self.screen, DARK_GRAY, slot2_rect)
        pygame.draw.rect(self.screen, CYAN, slot2_rect, 2)
        
        # Draw entanglement visualization
        time_factor = pygame.time.get_ticks() * 0.01
        for i in range(5):
            t = time_factor + i * 0.5
            x1 = slot1_rect.x + slot1_rect.width
            y1 = slot1_rect.y + slot1_rect.height//2
            x2 = slot2_rect.x
            y2 = slot2_rect.y + slot2_rect.height//2
            
            # Draw wavy line
            points = []
            for j in range(20):
                progress = j / 19
                x = x1 + (x2 - x1) * progress
                # Add wave effect
                y = (y1 + y2) / 2 + math.sin(t + progress * 10) * 20
                points.append((x, y))
            
            # Draw quantum line
            if len(points) >= 2:
                pygame.draw.lines(self.screen, CYAN, False, points, 2)
        
        # Draw selected artifacts
        for i, artifact in enumerate(self.entanglement_artifacts):
            if artifact:
                slot_rect = slot1_rect if i == 0 else slot2_rect
                # Draw larger artifact
                pygame.draw.rect(self.screen, artifact.image_color, 
                                pygame.Rect(slot_rect.x + 25, slot_rect.y + 25, 
                                           slot_rect.width - 50, slot_rect.height - 50))
                # Draw name
                name_surface = self.font_small.render(artifact.name, True, WHITE)
                self.screen.blit(name_surface, 
                                (slot_rect.x + slot_rect.width//2 - name_surface.get_width()//2, 
                                 slot_rect.y + slot_rect.height + 10))
                
                # Show if already entangled
                if artifact.entangled_with:
                    entangled_text = self.font_small.render("Already Entangled", True, YELLOW)
                    self.screen.blit(entangled_text, 
                                    (slot_rect.x + slot_rect.width//2 - entangled_text.get_width()//2, 
                                     slot_rect.y + slot_rect.height + 35))
        
        # Draw available artifacts
        if self.player.inventory:
            for i, artifact in enumerate(self.player.inventory):
                if artifact not in self.entanglement_artifacts:
                    x = 50 + i * 80
                    y = 400
                    artifact.draw(self.screen, x, y)
                    # Draw number
                    num_text = self.font_small.render(str(i+1), True, WHITE)
                    self.screen.blit(num_text, (x, y - 20))
                    
                    # Show if already entangled
                    if artifact.entangled_with:
                        entangled_with = self.font_small.render("Entangled", True, YELLOW)
                        self.screen.blit(entangled_with, (x, y + 30))
        
        # Draw entanglement button
        if all(self.entanglement_artifacts) and not any(a.entangled_with for a in self.entanglement_artifacts):
            button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 480, 200, 50)
            pygame.draw.rect(self.screen, CYAN, button_rect)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2)
            
            button_text = self.font_medium.render("ENTANGLE", True, BLACK)
            self.screen.blit(button_text, 
                            (button_rect.x + button_rect.width//2 - button_text.get_width()//2, 
                             button_rect.y + button_rect.height//2 - button_text.get_height()//2))
        
        # Draw back button
        back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 550, 200, 40)
        pygame.draw.rect(self.screen, RED, back_rect)
        pygame.draw.rect(self.screen, WHITE, back_rect, 2)
        
        back_text = self.font_medium.render("BACK", True, BLACK)
        self.screen.blit(back_text, 
                        (back_rect.x + back_rect.width//2 - back_text.get_width()//2, 
                         back_rect.y + back_rect.height//2 - back_text.get_height()//2))
    
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
                    if self.state in [GameState.FUSION, GameState.RIFT, GameState.INVENTORY]:
                        self.state = GameState.PLAYING
                    else:
                        return False
                
                # Toggle instructions with H key
                if event.key == pygame.K_h:
                    self.show_controls = not self.show_controls
                
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
                
                # Repair artifact
                if event.key == pygame.K_r and self.state == GameState.PLAYING:
                    self.world.repair_artifact(self.player)
                
                # Fusion menu
                if event.key == pygame.K_f:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.FUSION
                        self.fusion_artifacts = [None, None]
                    elif self.state == GameState.FUSION:
                        self.state = GameState.PLAYING
                
                # Quantum entanglement menu
                if event.key == pygame.K_q:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.ENTANGLEMENT
                        self.entanglement_artifacts = [None, None]
                    elif self.state == GameState.ENTANGLEMENT:
                        self.state = GameState.PLAYING
                
                # Select artifact (number keys 1-9)
                if event.key in range(pygame.K_1, pygame.K_9 + 1) and self.player.inventory:
                    index = event.key - pygame.K_1
                    if index < len(self.player.inventory):
                        artifact = self.player.inventory[index]
                        
                        if self.state == GameState.PLAYING:
                            # Normal selection
                            self.player.selected_artifact = artifact
                            self.world.show_message(f"Selected: {artifact.name}")
                            
                        elif self.state == GameState.FUSION:
                            # Add to fusion slots
                            if artifact not in self.fusion_artifacts:
                                if self.fusion_artifacts[0] is None:
                                    self.fusion_artifacts[0] = artifact
                                elif self.fusion_artifacts[1] is None:
                                    self.fusion_artifacts[1] = artifact
                                    
                        elif self.state == GameState.ENTANGLEMENT:
                            # Add to entanglement slots
                            if artifact not in self.entanglement_artifacts:
                                if self.entanglement_artifacts[0] is None:
                                    self.entanglement_artifacts[0] = artifact
                                elif self.entanglement_artifacts[1] is None:
                                    self.entanglement_artifacts[1] = artifact
                
                # Handle fusion screen specific inputs
                if self.state == GameState.FUSION:
                    if event.key == pygame.K_SPACE:
                        # Attempt fusion if both slots filled
                        if all(self.fusion_artifacts):
                            fused = self.player.attempt_artifact_fusion(
                                self.fusion_artifacts[0], 
                                self.fusion_artifacts[1], 
                                self.world
                            )
                            if fused:
                                self.state = GameState.PLAYING
                                
                    elif event.key == pygame.K_BACKSPACE:
                        # Clear fusion slots
                        if self.fusion_artifacts[1] is not None:
                            self.fusion_artifacts[1] = None
                        elif self.fusion_artifacts[0] is not None:
                            self.fusion_artifacts[0] = None
                
                # Handle entanglement screen specific inputs
                if self.state == GameState.ENTANGLEMENT:
                    if event.key == pygame.K_SPACE:
                        # Attempt entanglement if both slots filled
                        if all(self.entanglement_artifacts) and not any(a.entangled_with for a in self.entanglement_artifacts):
                            entangled = self.player.attempt_entanglement(
                                self.entanglement_artifacts[0], 
                                self.entanglement_artifacts[1], 
                                self.world
                            )
                            if entangled:
                                self.state = GameState.PLAYING
                                
                    elif event.key == pygame.K_BACKSPACE:
                        # Clear entanglement slots
                        if self.entanglement_artifacts[1] is not None:
                            self.entanglement_artifacts[1] = None
                        elif self.entanglement_artifacts[0] is not None:
                            self.entanglement_artifacts[0] = None
                
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
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Handle mouse clicks for UI
                    if self.state == GameState.FUSION:
                        # Check if clicked the fusion button
                        if all(self.fusion_artifacts):
                            button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 450, 200, 50)
                            if button_rect.collidepoint(event.pos):
                                fused = self.player.attempt_artifact_fusion(
                                    self.fusion_artifacts[0], 
                                    self.fusion_artifacts[1], 
                                    self.world
                                )
                                if fused:
                                    self.state = GameState.PLAYING
                        
                        # Check if clicked the back button
                        back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 520, 200, 40)
                        if back_rect.collidepoint(event.pos):
                            self.state = GameState.PLAYING
                    
                    elif self.state == GameState.ENTANGLEMENT:
                        # Check if clicked the entangle button
                        if all(self.entanglement_artifacts) and not any(a.entangled_with for a in self.entanglement_artifacts):
                            button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 480, 200, 50)
                            if button_rect.collidepoint(event.pos):
                                entangled = self.player.attempt_entanglement(
                                    self.entanglement_artifacts[0], 
                                    self.entanglement_artifacts[1], 
                                    self.world
                                )
                                if entangled:
                                    self.state = GameState.PLAYING
                        
                        # Check if clicked the back button
                        back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 550, 200, 40)
                        if back_rect.collidepoint(event.pos):
                            self.state = GameState.PLAYING
        
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
                y_pos = 100 + i * 90
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
                
                # Draw stability and evolution
                stability_text = f"Stability: {int(artifact.stability)}%"
                stability_color = GREEN if artifact.stability > 70 else YELLOW if artifact.stability > 30 else RED
                stability_surface = self.font_small.render(stability_text, True, stability_color)
                self.screen.blit(stability_surface, (500, y_pos + 10))
                
                evolution_text = f"Evolution: {int(artifact.evolution_progress)}%"
                evolution_surface = self.font_small.render(evolution_text, True, CYAN)
                self.screen.blit(evolution_surface, (500, y_pos + 30))
                
                # Draw entanglement status
                if artifact.entangled_with:
                    entangled_text = f"Entangled with: {artifact.entangled_with.name}"
                    entangled_surface = self.font_small.render(entangled_text, True, CYAN)
                    self.screen.blit(entangled_surface, (500, y_pos + 50))
                
                # Draw curse status if applicable
                if artifact.is_cursed:
                    status = "CURSED" if not artifact.curse_cleansed else "CLEANSED"
                    curse_text = self.font_small.render(status, True, RED if not artifact.curse_cleansed else GREEN)
                    self.screen.blit(curse_text, (100, y_pos + 70))
        
        # Draw instruction
        instruction_text = self.font_small.render("Press I or ESC to return to game", True, WHITE)
        self.screen.blit(instruction_text, (SCREEN_WIDTH//2 - instruction_text.get_width()//2, SCREEN_HEIGHT - 50))
    
    def draw_title_screen(self):
        """Draw the title screen"""
        # Fill background with dark color
        self.screen.fill((20, 20, 40))
        
        # Draw title
        title_text = self.font_large.render("Alien Artifact Explorer v2", True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
        
        # Draw subtitle
        subtitle_text = self.font_medium.render("Explore an alien world with advanced artifact mechanics", True, CYAN)
        self.screen.blit(subtitle_text, (SCREEN_WIDTH//2 - subtitle_text.get_width()//2, 170))
        
        # Draw game features
        features = [
            "NEW FEATURES:",
            "",
            "• ARTIFACT FUSION - Combine artifacts for unpredictable hybrid effects",
            "• ARTIFACT INSTABILITY - Artifacts degrade with use, can cause reality quakes",
            "• DIMENSIONAL RIFTS - Using artifacts repeatedly creates portals to alternate realities",
            "• QUANTUM ENTANGLEMENT - Link artifacts for synchronized activation",
            "• ARTIFACT EVOLUTION - Artifacts gain power through continued use",
            "",
            "Can you master these complex mechanics to unlock the temple's secrets?"
        ]
        
        for i, line in enumerate(features):
            line_text = self.font_small.render(line, True, WHITE)
            self.screen.blit(line_text, (SCREEN_WIDTH//2 - line_text.get_width()//2, 250 + i * 30))
        
        # Draw start instruction
        if pygame.time.get_ticks() % 1000 < 500:  # Blink effect
            start_text = self.font_medium.render("Press ENTER to begin your expedition", True, YELLOW)
            self.screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 500))
    
    def draw_win_screen(self):
        """Draw the win screen"""
        # Fill background with triumphant color
        self.screen.fill((20, 50, 70))
        
        # Draw title
        title_text = self.font_large.render("Temple Secrets Unlocked!", True, YELLOW)
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
        
        # Draw description
        description = [
            "Congratulations! You've mastered the complex artifact mechanics",
            "and unlocked the temple's secrets!",
            "",
            "The ancient alien technology activates, revealing the truth about",
            "the civilization that created these reality-bending artifacts.",
            "",
            "Their knowledge of quantum entanglement, dimensional rifts,",
            "and artifact fusion is now yours to command...",
            "",
            "Until your next expedition!"
        ]
        
        for i, line in enumerate(description):
            line_text = self.font_medium.render(line, True, WHITE)
            self.screen.blit(line_text, (SCREEN_WIDTH//2 - line_text.get_width()//2, 200 + i * 40))
        
        # Draw restart instruction
        if pygame.time.get_ticks() % 1000 < 500:  # Blink effect
            restart_text = self.font_medium.render("Press ENTER to play again", True, GREEN)
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 550))
    
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
            "The alien artifacts proved too complex to control,",
            "and their combined effects have overwhelmed you.",
            "",
            "The rifts between dimensions have grown unstable,",
            "the quantum entanglements have collapsed,",
            "and the artifact fusions have backfired.",
            "",
            "Perhaps another explorer will succeed where you failed..."
        ]
        
        for i, line in enumerate(description):
            line_text = self.font_medium.render(line, True, WHITE)
            self.screen.blit(line_text, (SCREEN_WIDTH//2 - line_text.get_width()//2, 200 + i * 40))
        
        # Draw restart instruction
        if pygame.time.get_ticks() % 1000 < 500:  # Blink effect
            restart_text = self.font_medium.render("Press ENTER to try again", True, YELLOW)
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 550))
    
    def update_evil_clones(self):
        """Update all evil clones"""
        # Update evil clones from rifts
        for rift in self.world.rifts:
            if rift.active and random.random() < 0.001:  # Small chance each frame
                clone = rift.spawn_evil_clone(self.player, self.world)
                if clone:
                    self.world.evil_clones.append(clone)
        
        # Update existing clones
        for clone in self.world.evil_clones[:]:
            clone.update(self.player, self.world)
    
    def check_player_health(self):
        """Check if player has died"""
        if self.player.health <= 0:
            self.state = GameState.GAME_OVER
    
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
                self.update_evil_clones()
                self.update_camera()
                self.check_player_health()
                self.check_win_condition()
                
            # Draw the current screen
            if self.state == GameState.TITLE:
                self.draw_title_screen()
            
            elif self.state == GameState.PLAYING:
                # Clear screen
                self.screen.fill((0, 0, 0))
                
                # Draw world
                self.world.draw(self.screen, int(self.camera_x), int(self.camera_y))
                
                # Draw player and UI
                self.player.draw(self.screen, int(self.camera_x), int(self.camera_y))
                
                # Draw evil clones
                for clone in self.world.evil_clones:
                    clone.draw(self.screen, int(self.camera_x), int(self.camera_y))
                
                # Draw UI
                self.draw_ui()
            
            elif self.state == GameState.INVENTORY:
                # First draw the game world (will be overlaid)
                self.screen.fill((0, 0, 0))
                self.world.draw(self.screen, int(self.camera_x), int(self.camera_y))
                self.player.draw(self.screen, int(self.camera_x), int(self.camera_y))
                
                # Then draw inventory screen
                self.draw_inventory_screen()
            
            elif self.state == GameState.FUSION:
                # First draw the game world (will be overlaid)
                self.screen.fill((0, 0, 0))
                self.world.draw(self.screen, int(self.camera_x), int(self.camera_y))
                self.player.draw(self.screen, int(self.camera_x), int(self.camera_y))
                
                # Draw fusion screen
                self.draw_fusion_screen()
            
            elif self.state == GameState.ENTANGLEMENT:
                # First draw the game world (will be overlaid)
                self.screen.fill((0, 0, 0))
                self.world.draw(self.screen, int(self.camera_x), int(self.camera_y))
                self.player.draw(self.screen, int(self.camera_x), int(self.camera_y))
                
                # Draw entanglement screen
                self.draw_entanglement_screen()
            
            elif self.state == GameState.RIFT:
                # Draw rift view
                self.draw_rift_screen()
            
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