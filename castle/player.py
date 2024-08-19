# castle/player.py
import pygame
import time

class Player:
    def __init__(self, playable_area_size):
        """
        Initializes the player.
        Args:
        playable_area_size (int): The size of the playable area.
        """
        self.original_speed = 5
        self.speed = self.original_speed
        self.size = 25
        self.position = [playable_area_size // 2, playable_area_size // 2]
        self.last_direction = (1, 0)
        self.health = 100
        self.max_health = 100
        self.collected_star_dust = 0
        self.boost_end_time = None  # Keep track of when boost ends
        self.invincibility_end_time = None  # Track invincibility duration
        self.double_damage_end_time = None  # Track double damage duration
        self.rapid_fire_end_time = None  # Track rapid-fire duration
        self.laser_cost = 1
        self.lasers = []
        self.playable_area_size = playable_area_size
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_interval = 2000
        self.damage = 2  # Default damage
        self.shoot_interval = 500  # Default shoot interval

    def handle_movement(self, keys, castle_pos, castle_size):
        """
        Handles player movement based on keyboard input.
        Args:
        keys: The state of the keyboard.
        castle_pos: The position of the castle.
        castle_size: The size of the castle.
        """
        if keys[pygame.K_LEFT] and self.position[0] - self.speed - self.size > 0:
            new_pos_x = self.position[0] - self.speed
            if not self.collides_with_castle(new_pos_x, self.position[1], castle_pos, castle_size) and not self.collides_with_border(new_pos_x, self.position[1]):
                self.position[0] = new_pos_x
                self.last_direction = (-1, 0)
        elif keys[pygame.K_RIGHT] and self.position[0] + self.speed + self.size < self.playable_area_size:
            new_pos_x = self.position[0] + self.speed
            if not self.collides_with_castle(new_pos_x, self.position[1], castle_pos, castle_size) and not self.collides_with_border(new_pos_x, self.position[1]):
                self.position[0] = new_pos_x
                self.last_direction = (1, 0)
        elif keys[pygame.K_UP] and self.position[1] - self.speed - self.size > 0:
            new_pos_y = self.position[1] - self.speed
            if not self.collides_with_castle(self.position[0], new_pos_y, castle_pos, castle_size) and not self.collides_with_border(self.position[0], new_pos_y):
                self.position[1] = new_pos_y
                self.last_direction = (0, -1)
        elif keys[pygame.K_DOWN] and self.position[1] + self.speed + self.size < self.playable_area_size:
            new_pos_y = self.position[1] + self.speed
            if not self.collides_with_castle(self.position[0], new_pos_y, castle_pos, castle_size) and not self.collides_with_border(self.position[0], new_pos_y):
                self.position[1] = new_pos_y
                self.last_direction = (0, 1)

    def collides_with_castle(self, x, y, castle_pos, castle_size):
        """
        Checks if the player collides with the castle.
        Args:
        x: The x position of the player.
        y: The y position of the player.
        castle_pos: The position of the castle.
        castle_size: The size of the castle.
        Returns:
        bool: True if the player collides with the castle, False otherwise.
        """
        player_rect = pygame.Rect(x - self.size, y - self.size, self.size * 2, self.size * 2)
        adjusted_castle_hitbox = pygame.Rect(castle_pos[0], castle_pos[1], castle_size[0], castle_size[1])
        return player_rect.colliderect(adjusted_castle_hitbox)

    def collides_with_border(self, x, y):
        """
        Checks if the player collides with the border.
        Args:
        x: The x position of the player.
        y: The y position of the player.
        Returns:
        bool: True if the player collides with the border, False otherwise.
        """
        border_thickness = 25  # Set the border thickness to match wall image size
        return x - self.size < border_thickness or x + self.size > self.playable_area_size - border_thickness or \
            y - self.size < border_thickness or y + self.size > self.playable_area_size - border_thickness

    def check_collisions(self, stardust_manager):
        """
        Checks for collisions with stardust objects.
        Args:
        stardust_manager (StarDustManager): The stardust manager containing all stardust objects.
        """
        for star_dust in stardust_manager.star_dust_list[:]:
            dx = self.position[0] - star_dust['pos'][0]
            dy = self.position[1] - star_dust['pos'][1]
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < self.size + stardust_manager.STAR_DUST_SIZE / 2:
                if star_dust['type'] == 'arrow1':
                    self.collected_star_dust = min(self.collected_star_dust + 1, 100)
                    stardust_manager.star_dust_list.remove(star_dust)
                elif star_dust['type'] == 'boost':
                    self.boost_end_time = pygame.time.get_ticks() + stardust_manager.BOOST_DURATION * 1000
                    self.speed = self.original_speed * 1.5  # Increase speed by 50%
                    stardust_manager.star_dust_list.remove(star_dust)
                elif star_dust['type'] == 'health':
                    self.health = min(self.health + 10, self.max_health)
                    stardust_manager.star_dust_list.remove(star_dust)
                elif star_dust['type'] == 'arrow_stack':
                    self.collected_star_dust = min(self.collected_star_dust + 5, 100)
                    stardust_manager.star_dust_list.remove(star_dust)
                elif star_dust['type'] == 'mushroom':
                    self.health = min(self.health + 5, self.max_health)  # Mushroom adds 5 health to the player
                    stardust_manager.star_dust_list.remove(star_dust)
                elif star_dust['type'] == 'invincibility':
                    self.invincibility_end_time = pygame.time.get_ticks() + stardust_manager.INVINCIBILITY_DURATION * 1000
                    stardust_manager.star_dust_list.remove(star_dust)
                    stardust_manager.active_power_up = None
                elif star_dust['type'] == 'double_damage':
                    self.double_damage_end_time = pygame.time.get_ticks() + stardust_manager.DOUBLE_DAMAGE_DURATION * 1000
                    self.damage = 4  # Double the damage
                    stardust_manager.star_dust_list.remove(star_dust)
                    stardust_manager.active_power_up = None
                elif star_dust['type'] == 'rapid_fire':
                    self.rapid_fire_end_time = pygame.time.get_ticks() + stardust_manager.RAPID_FIRE_DURATION * 1000
                    self.shoot_interval = 200  # Reduce shoot interval for rapid fire
                    stardust_manager.star_dust_list.remove(star_dust)
                    stardust_manager.active_power_up = None

    def shoot_laser(self):
        """
        Shoots a laser.
        """
        self.lasers.append({'pos': self.position[:], 'dir': self.last_direction})
        self.collected_star_dust -= self.laser_cost

    def handle_laser_movement(self, stardust_manager):
        """
        Handles the movement of lasers.
        Args:
        stardust_manager (StarDustManager): The stardust manager containing all stardust objects.
        """
        for laser in self.lasers[:]:
            laser['pos'][0] += laser['dir'][0] * 10
            laser['pos'][1] += laser['dir'][1] * 10
            if laser['pos'][0] < 0 or laser['pos'][0] > self.playable_area_size or \
                    laser['pos'][1] < 0 or laser['pos'][1] > self.playable_area_size:
                self.lasers.remove(laser)
                continue
            if stardust_manager.check_laser_collision(laser['pos']):
                self.lasers.remove(laser)

    def take_damage(self, amount):
        """
        Reduces the player's health by the specified amount.
        Args:
        amount (int): The amount of damage to take.
        """
        if not self.invincibility_end_time or pygame.time.get_ticks() > self.invincibility_end_time:
            self.health = max(self.health - amount, 0)

    def update_status(self):
        """
        Updates the player's status, especially after effects like boosts.
        """
        if self.boost_end_time and pygame.time.get_ticks() > self.boost_end_time:
            self.speed = self.original_speed
            self.boost_end_time = None
        if self.invincibility_end_time and pygame.time.get_ticks() > self.invincibility_end_time:
            self.invincibility_end_time = None
        if self.double_damage_end_time and pygame.time.get_ticks() > self.double_damage_end_time:
            self.damage = 2  # Reset damage
            self.double_damage_end_time = None
        if self.rapid_fire_end_time and pygame.time.get_ticks() > self.rapid_fire_end_time:
            self.shoot_interval = 500  # Reset shoot interval to default
            self.rapid_fire_end_time = None