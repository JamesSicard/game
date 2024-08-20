# castle/wizard.py
import pygame
import math
import random

class Wizard:
    def __init__(wizard, playable_area_size, player, stardust_manager):
        """
        Initializes the wizard.
        Args:
            playable_area_size (int): The size of the playable area.
            player (Player): The player object.
            stardust_manager (StarDustManager): The stardust manager object.
        """
        wizard.image = pygame.image.load('pics/wizard.png').convert_alpha()
        wizard.original_image = wizard.image
        wizard.size = player.size  # Set the wizard's size to be the same as the player's size

        wizard.playable_area_size = playable_area_size
        wizard.player = player
        wizard.stardust_manager = stardust_manager  # Add the stardust manager
        
        # Initialize wizard properties
        wizard.position = wizard.generate_random_position()
        wizard.speed = 2
        wizard.health = 25
        wizard.max_health = 25
        wizard.orbs = []
        wizard.orb_image = pygame.image.load('pics/orb.png').convert_alpha()  # Ensure alpha is handled
        wizard.orb_speed = 3
        wizard.last_shot_time = pygame.time.get_ticks()
        wizard.shot_interval = 4000  # Time between shots in milliseconds; slowed down from 2000 to 4000

    def generate_random_position(wizard):
        """
        Generates a random position for the wizard, respecting the playable area.
        """
        margin = 10
        x = random.randint(margin, wizard.playable_area_size - wizard.size * 2 - margin)
        y = random.randint(margin, wizard.playable_area_size - wizard.size * 2 - margin)
        return [x, y]

    def spawn_wizard(wizard):
        """
        Spawns additional wizards based on the player's current level.
        """
        for _ in range(wizard.player.current_level):
            wizard.stardust_manager.star_dust_list.append(wizard.stardust_manager.create_star_dust(position=wizard.generate_random_position(), type='wizard'))

    def check_player_level(wizard):
        """
        Checks the player's current level.
        """
        if wizard.player.current_level > 1:
            wizard.spawn_wizard()

    def respawn(wizard):
        """
        Respawns the wizard at a new position and regenerates its health.
        """
        wizard.position = wizard.generate_random_position()
        wizard.health = wizard.max_health
        wizard.last_shot_time = pygame.time.get_ticks() + 5000
        wizard.check_player_level()
        wizard.spawn_wizard()

    def move_towards_player(wizard, castle_pos, castle_size):
        """
        Moves the wizard towards the player.
        Args:
            castle_pos (tuple): The position of the castle.
            castle_size (tuple): The size of the castle.
        """
        direction_vector = (wizard.player.position[0] - wizard.position[0], wizard.player.position[1] - wizard.position[1])
        distance = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)

        # Maintain a minimum distance of 30 pixels from the player
        if distance > 100:
            normalized_direction = (direction_vector[0] / distance, direction_vector[1] / distance)
            new_pos_x = wizard.position[0] + normalized_direction[0] * wizard.speed
            new_pos_y = wizard.position[1] + normalized_direction[1] * wizard.speed
            if not wizard.collides_with_castle(new_pos_x, new_pos_y, castle_pos, castle_size):
                wizard.position[0] = new_pos_x
                wizard.position[1] = new_pos_y

    def angle_to_player(wizard):
        """
        Calculates the angle to the player.
        """
        direction_vector = (wizard.player.position[0] - wizard.position[0], wizard.player.position[1] - wizard.position[1])
        return math.degrees(math.atan2(-direction_vector[1], direction_vector[0]))

    def shoot_orb(wizard):
        """
        Shoots an orb towards the player if the shot interval has passed.
        """
        now = pygame.time.get_ticks()
        if now - wizard.last_shot_time >= wizard.shot_interval:
            direction_vector = (wizard.player.position[0] - wizard.position[0], wizard.player.position[1] - wizard.position[1])
            distance = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)
            if distance != 0:
                normalized_direction = (direction_vector[0] / distance, direction_vector[1] / distance)
                wizard.orbs.append({'pos': list(wizard.position), 'dir': normalized_direction})
                wizard.last_shot_time = now

    def update(wizard, castle_pos, castle_size):
        """
        Updates the wizard's position and action.
        Args:
            castle_pos (tuple): The position of the castle.
            castle_size (tuple): The size of the castle.
        """
        wizard.move_towards_player(castle_pos, castle_size)
        wizard.shoot_orb()

        # Rotate the wizard to face the player
        angle = wizard.angle_to_player()
        wizard.image = pygame.transform.rotate(wizard.original_image, angle)

    def draw(wizard, screen, offset_x, offset_y):
        """
        Draws the wizard and its orbs.
        Args:
            screen (pygame.Surface): The screen to draw on.
            offset_x (int): The x offset for drawing.
            offset_y (int): The y offset for drawing.
        """
        wizard_rect = wizard.image.get_rect(center=(wizard.position[0] - offset_x, wizard.position[1] - offset_y))
        screen.blit(wizard.image, wizard_rect.topleft)

        # Draw wizard health bar
        health_bar_length = wizard.size * 2
        health_ratio = wizard.health / wizard.max_health
        health_bar_width = health_ratio * health_bar_length
        health_bar_x = wizard.position[0] - offset_x - wizard.size
        health_bar_y = wizard.position[1] - offset_y + wizard.size + 10

        pygame.draw.rect(screen, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_length, 5))
        pygame.draw.rect(screen, (0, 255, 0), (health_bar_x, health_bar_y, health_bar_width, 5))

        for orb in wizard.orbs:
            orb['pos'][0] += orb['dir'][0] * wizard.orb_speed
            orb['pos'][1] += orb['dir'][1] * wizard.orb_speed
            screen.blit(wizard.orb_image, (orb['pos'][0] - offset_x, orb['pos'][1] - offset_y))

    def take_damage(wizard, amount):
        """
        Reduces the wizard's health by the specified amount and drops a mushroom if killed.
        Args:
            amount (int): The amount of damage to take.
        """
        wizard.health = max(wizard.health - amount, 0)
        if wizard.health <= 0:
            wizard.stardust_manager.star_dust_list.append(wizard.stardust_manager.create_star_dust(position=wizard.position, type='mushroom'))

    def collides_with_castle(wizard, x, y, castle_pos, castle_size):
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
        wizard_rect = pygame.Rect(x - wizard.size, y - wizard.size, wizard.size * 2, wizard.size * 2)
        adjusted_castle_hitbox = pygame.Rect(castle_pos[0], castle_pos[1], castle_size[0], castle_size[1])
        return wizard_rect.colliderect(adjusted_castle_hitbox)