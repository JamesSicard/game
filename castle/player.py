# castle/player.py
import pygame
import time

class Player:
    def __init__(self, playable_area_size):
        self.original_speed = 5
        self.speed = self.original_speed
        self.size = 25
        self.position = [playable_area_size // 2, playable_area_size // 2]
        self.last_direction = (1, 0)
        self.health = 100
        self.max_health = 100
        self.collected_star_dust = 0
        self.boost_end_time = None
        self.invincibility_end_time = None
        self.double_damage_end_time = None
        self.rapid_fire_end_time = None
        self.laser_cost = 1
        self.lasers = []
        self.playable_area_size = playable_area_size
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_interval = 2000
        self.damage = 2
        self.shoot_interval = 200
        self.last_shot_time = 0  # Track the last shot time

    def handle_movement(self, keys, castle_pos, castle_size):
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
        player_rect = pygame.Rect(x - self.size, y - self.size, self.size * 2, self.size * 2)
        adjusted_castle_hitbox = pygame.Rect(castle_pos[0], castle_pos[1], castle_size[0], castle_size[1])
        return player_rect.colliderect(adjusted_castle_hitbox)

    def collides_with_border(self, x, y):
        border_thickness = 25
        return x - self.size < border_thickness or x + self.size > self.playable_area_size - border_thickness or \
            y - self.size < border_thickness or y + self.size > self.playable_area_size - border_thickness

    def check_collisions(self, stardust_manager):
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
                    self.speed = self.original_speed * 1.5
                    stardust_manager.star_dust_list.remove(star_dust)
                elif star_dust['type'] == 'health':
                    self.health = min(self.health + 10, self.max_health)
                    stardust_manager.star_dust_list.remove(star_dust)
                elif star_dust['type'] == 'arrow_stack':
                    self.collected_star_dust = min(self.collected_star_dust + 5, 100)
                    stardust_manager.star_dust_list.remove(star_dust)
                elif star_dust['type'] == 'mushroom':
                    self.health = min(self.health + 5, self.max_health)
                    stardust_manager.star_dust_list.remove(star_dust)
                elif star_dust['type'] == 'invincibility':
                    self.invincibility_end_time = pygame.time.get_ticks() + stardust_manager.INVINCIBILITY_DURATION * 1000
                    stardust_manager.star_dust_list.remove(star_dust)
                    stardust_manager.active_power_up = None
                elif star_dust['type'] == 'double_damage':
                    self.double_damage_end_time = pygame.time.get_ticks() + stardust_manager.DOUBLE_DAMAGE_DURATION * 1000
                    self.damage = 4
                    stardust_manager.star_dust_list.remove(star_dust)
                    stardust_manager.active_power_up = None
                elif star_dust['type'] == 'rapid_fire':
                    self.rapid_fire_end_time = pygame.time.get_ticks() + stardust_manager.RAPID_FIRE_DURATION * 1000
                    self.shoot_interval = 100
                    self.unlimited_arrows = True  # Enable unlimited arrows
                    stardust_manager.star_dust_list.remove(star_dust)
                    stardust_manager.active_power_up = None

    def shoot_laser(self):
        if self.rapid_fire_end_time and pygame.time.get_ticks() < self.rapid_fire_end_time:
            self.lasers.append({'pos': self.position[:], 'dir': self.last_direction})
        elif self.collected_star_dust >= self.laser_cost:
            self.lasers.append({'pos': self.position[:], 'dir': self.last_direction})
            self.collected_star_dust -= self.laser_cost

    def handle_laser_movement(self, stardust_manager):
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
        if not self.invincibility_end_time or pygame.time.get_ticks() > self.invincibility_end_time:
            self.health = max(self.health - amount, 0)

    def update_status(self):
        if self.boost_end_time and pygame.time.get_ticks() > self.boost_end_time:
            self.speed = self.original_speed
            self.boost_end_time = None
        if self.invincibility_end_time and pygame.time.get_ticks() > self.invincibility_end_time:
            self.invincibility_end_time = None
        if self.double_damage_end_time and pygame.time.get_ticks() > self.double_damage_end_time:
            self.damage = 2
            self.double_damage_end_time = None
        if self.rapid_fire_end_time and pygame.time.get_ticks() > self.rapid_fire_end_time:
            self.shoot_interval = 200
            self.unlimited_arrows = False  # Disable unlimited arrows
            self.rapid_fire_end_time = None
 # Handle shooting when spacebar is held down
    def handle_shooting(self, keys):
        if keys[pygame.K_SPACE]:
            #
            now = pygame.time.get_ticks()
            # Check if the player has rapid fire power-up and if the shoot interval has passed
            if now - self.last_shot_time >= self.shoot_interval:
                self.shoot_laser()
                self.last_shot_time = now