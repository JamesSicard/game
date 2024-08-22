# wizard_manager.py
import pygame
import random
from wizard import Wizard

class WizardManager:
    def __init__(self, playable_area_size, player, stardust_manager):
        self.playable_area_size = playable_area_size
        self.player = player
        self.stardust_manager = stardust_manager
        self.wizards = []
        self.last_spawn_time = 0
        self.respawn_delay = 5000  # 5 seconds

    def update(self, castle_pos, castle_size):
        now = pygame.time.get_ticks()
        if len(self.wizards) < self.player.current_level and now - self.last_spawn_time >= self.respawn_delay:
            self.wizards.append(Wizard(self.playable_area_size, self.player, self.stardust_manager))
            self.last_spawn_time = now
        
        for wizard in self.wizards:
            wizard.update(castle_pos, castle_size)

    def draw(self, screen, offset_x, offset_y):
        for wizard in self.wizards:
            wizard.draw(screen, offset_x, offset_y)

    def handle_collisions(self, player):
        for wizard in self.wizards[:]:
            if wizard.health <= 0:
                self.wizards.remove(wizard)

    def check_laser_collision(self, laser_pos, laser_damage):
        wizard_hit = False
        for wizard in self.wizards[:]:
            if wizard.collides_with(laser_pos):
                wizard.take_damage(laser_damage)
                wizard_hit = True
                if wizard.health <= 0:
                    self.wizards.remove(wizard)
        return wizard_hit

    def reset(self):
        self.wizards = []
        self.last_spawn_time = pygame.time.get_ticks()