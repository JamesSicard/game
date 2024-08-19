# castle/castle.py
import pygame
import random
import math

class Castle:
    def __init__(self, playable_area_size, castle_size):
        """
        Initializes the Castle.
        
        Args:
            playable_area_size (int): The size of the playable area.
            castle_size (tuple): The size of the castle.
        """
        self.playable_area_size = playable_area_size
        self.size = castle_size
        self.max_health = 25
        self.health = self.max_health
        self.position = self.generate_random_position()

    def generate_random_position(self):
        """
        Generates a random position for the castle within the playable area.
        
        Returns:
            list: A list containing the x and y coordinates.
        """
        margin = 10
        x = random.randint(margin, self.playable_area_size - self.size[0] - margin)
        y = random.randint(margin, self.playable_area_size - self.size[1] - margin)
        return [x, y]

    def take_damage(self, amount):
        """
        Reduces the castle's health by the specified amount.
        
        Args:
            amount (int): The amount of damage to take.
        """
        self.health = max(self.health - amount, 0)

    def draw_castle(self, screen, castle_img, offset_x, offset_y):
        """
        Draws the castle and its health bar.
        
        Args:
            screen (pygame.Surface): The screen to draw on.
            castle_img (pygame.Surface): The castle image.
            offset_x (int): The x offset for drawing.
            offset_y (int): The y offset for drawing.
        """
        screen.blit(castle_img, (self.position[0] - offset_x, self.position[1] - offset_y))

        # Draw castle health bar
        if self.health < self.max_health:
            health_bar_length = castle_img.get_width()
            health_ratio = self.health / self.max_health
            health_bar_width = health_ratio * health_bar_length
            pygame.draw.rect(screen, (255, 0, 0),
                             (self.position[0] - offset_x, self.position[1] + castle_img.get_height() - offset_y, health_bar_length, 5))
            pygame.draw.rect(screen, (0, 255, 0),
                             (self.position[0] - offset_x, self.position[1] + castle_img.get_height() - offset_y, health_bar_width, 5))

    def drop_items(self, stardust_manager):
        """
        Drops items around the castle's position when it is destroyed.
        
        Args:
            stardust_manager (StarDustManager): The stardust manager to handle creating star dust.
        """
        item_offset_range = 30  # The range within which items will be spread out
        for _ in range(2):  # Drop two 'arrow_stack' items
            offset_x = random.randint(-item_offset_range, item_offset_range)
            offset_y = random.randint(-item_offset_range, item_offset_range)
            item_position = [self.position[0] + offset_x, self.position[1] + offset_y]
            stardust_manager.star_dust_list.append(stardust_manager.create_star_dust(position=item_position, type='arrow_stack'))
            
        # Optionally, other items can be added below:
        # Make sure they don't fall into exactly the same spot
        health_item_offset_x = random.randint(-item_offset_range, item_offset_range)
        health_item_offset_y = random.randint(-item_offset_range, item_offset_range)
        health_item_position = [self.position[0] + health_item_offset_x, self.position[1] + health_item_offset_y]
        stardust_manager.star_dust_list.append(stardust_manager.create_star_dust(position=health_item_position, type='health'))

    def reset(self):
        """
        Resets the castle's health and position.
        """
        self.health = self.max_health
        self.position = self.generate_random_position()