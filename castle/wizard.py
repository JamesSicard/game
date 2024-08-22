# castle/wizard.py
import pygame
import math
import random

class Wizard:
    def __init__(self, playable_area_size, player, stardust_manager):
        """
        Initializes the wizard.
        Args:
            playable_area_size (int): The size of the playable area.
            player (Player): The player object.
            stardust_manager (StarDustManager): The stardust manager object.
        """
        self.image = pygame.image.load('pics/wizard.png').convert_alpha()
        self.original_image = self.image
        self.size = player.size  # Set the wizard's size to be the same as the player's size

        self.playable_area_size = playable_area_size
        self.player = player
        self.stardust_manager = stardust_manager
        
        # Initialize wizard properties
        self.position = self.generate_random_position()
        self.speed = 2
        self.health = 25
        self.max_health = 25
        self.orbs = []
        self.orb_image = pygame.image.load('pics/orb.png').convert_alpha()  # Ensure alpha is handled
        self.orb_speed = 3
        self.last_shot_time = pygame.time.get_ticks()
        self.shot_interval = 4000  # Time between shots in milliseconds; slowed down from 2000 to 4000

    def generate_random_position(self):
        """
        Generates a random position for the wizard, respecting the playable area.
        """
        margin = 10
        x = random.randint(margin, self.playable_area_size - self.size * 2 - margin)
        y = random.randint(margin, self.playable_area_size - self.size * 2 - margin)
        return [x, y]

    def spawn_wizard(self):
        """
        Spawns additional wizards based on the player's current level.
        """
        for _ in range(self.player.current_level):
            self.stardust_manager.star_dust_list.append(self.stardust_manager.create_star_dust(position=self.generate_random_position(), type='wizard'))

    def check_player_level(self):
        """
        Checks the player's current level.
        """
        if self.player.current_level > 1:
            self.spawn_wizard()

    def respawn(self):
        """
        Respawns the wizard at a new position and regenerates its health.
        """
        self.position = self.generate_random_position()
        self.health = self.max_health
        self.last_shot_time = pygame.time.get_ticks() + 5000
        self.check_player_level()
        self.spawn_wizard()

    def move_towards_player(self, castle_pos, castle_size):
        """
        Moves the wizard towards the player.
        Args:
            castle_pos (tuple): The position of the castle.
            castle_size (tuple): The size of the castle.
        """
        direction_vector = (self.player.position[0] - self.position[0], self.player.position[1] - self.position[1])
        distance = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)

        # Maintain a minimum distance of 30 pixels from the player
        if distance > 100:
            normalized_direction = (direction_vector[0] / distance, direction_vector[1] / distance)
            new_pos_x = self.position[0] + normalized_direction[0] * self.speed
            new_pos_y = self.position[1] + normalized_direction[1] * self.speed
            if not self.collides_with_castle(new_pos_x, new_pos_y, castle_pos, castle_size):
                self.position[0] = new_pos_x
                self.position[1] = new_pos_y

    def angle_to_player(self):
        """
        Calculates the angle to the player.
        """
        direction_vector = (self.player.position[0] - self.position[0], self.player.position[1] - self.position[1])
        return math.degrees(math.atan2(-direction_vector[1], direction_vector[0]))

    def shoot_orb(self):
        """
        Shoots an orb towards the player if the shot interval has passed.
        """
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.shot_interval:
            direction_vector = (self.player.position[0] - self.position[0], self.player.position[1] - self.position[1])
            distance = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)
            if distance != 0:
                normalized_direction = (direction_vector[0] / distance, direction_vector[1] / distance)
                self.orbs.append({'pos': list(self.position), 'dir': normalized_direction})
                self.last_shot_time = now

    def update(self, castle_pos, castle_size):
        """
        Updates the wizard's position and action.
        Args:
            castle_pos (tuple): The position of the castle.
            castle_size (tuple): The size of the castle.
        """
        self.move_towards_player(castle_pos, castle_size)
        self.shoot_orb()

        # Rotate the wizard to face the player
        angle = self.angle_to_player()
        self.image = pygame.transform.rotate(self.original_image, angle)

    def draw(self, screen, offset_x, offset_y):
        """
        Draws the wizard and its orbs.
        Args:
            screen (pygame.Surface): The screen to draw on.
            offset_x (int): The x offset for drawing.
            offset_y (int): The y offset for drawing.
        """
        wizard_rect = self.image.get_rect(center=(self.position[0] - offset_x, self.position[1] - offset_y))
        screen.blit(self.image, wizard_rect.topleft)

        # Draw wizard health bar
        health_bar_length = self.size * 2
        health_ratio = self.health / self.max_health
        health_bar_width = health_ratio * health_bar_length
        health_bar_x = self.position[0] - offset_x - self.size
        health_bar_y = self.position[1] - offset_y + self.size + 10

        pygame.draw.rect(screen, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_length, 5))
        pygame.draw.rect(screen, (0, 255, 0), (health_bar_x, health_bar_y, health_bar_width, 5))

        for orb in self.orbs:
            orb['pos'][0] += orb['dir'][0] * self.orb_speed
            orb['pos'][1] += orb['dir'][1] * self.orb_speed
            screen.blit(self.orb_image, (orb['pos'][0] - offset_x, orb['pos'][1] - offset_y))

    def take_damage(self, amount):
        """
        Reduces the wizard's health by the specified amount and drops a mushroom if killed.
        Args:
        amount (int): The amount of damage to take.
        """
        self.health = max(self.health - amount, 0)
        if self.health <= 0:
            self.stardust_manager.star_dust_list.append(self.stardust_manager.create_star_dust(position=self.position, type='mushroom'))

    def collides_with_castle(self, x, y, castle_pos, castle_size):
        """
        Checks if the wizard collides with the castle.
        Args:
            x: The x position of the wizard.
            y: The y position of the wizard.
            castle_pos: The position of the castle.
            castle_size: The size of the castle.
        Returns:
            bool: True if the wizard collides with the castle, False otherwise.
        """
        wizard_rect = pygame.Rect(x - self.size, y - self.size, self.size * 2, self.size * 2)
        adjusted_castle_hitbox = pygame.Rect(castle_pos[0], castle_pos[1], castle_size[0], castle_size[1])
        return wizard_rect.colliderect(adjusted_castle_hitbox)

    def collides_with(self, pos):
        """
        Checks if the wizard collides with a given position (e.g., a laser position).
        Args:
            pos: The position to check for collision.
        Returns:
            bool: True if the wizard collides with the position, False otherwise.
        """
        wizard_rect = pygame.Rect(self.position[0] - self.size, self.position[1] - self.size, self.size * 2, self.size * 2)
        return wizard_rect.collidepoint(pos)