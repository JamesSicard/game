# castle/render.py
import pygame
import math
from utils import calculate_exp_needed
from stardust import StarDustManager

# Constants for Mini-map
MINIMAP_WIDTH = 200
MINIMAP_HEIGHT = 200
MINIMAP_MARGIN = 10
MINIMAP_SCALE = 0.04  # Adjust scale as needed

# Constants for Boost Duration
BOOST_DURATION = 10  # Adjust to your game's boost duration

class Renderer:
    def __init__(self, screen, background_img, star_img, boost_img, arrow1_img, castle_img,
                 health_img, arrow_img, arrow_stack_img, mushroom_img, wall_img, laser_img,
                 invincibility_img, double_damage_img, rapid_fire_img,
                 screen_width, screen_height, playable_area_size):
        """
        Initializes the Renderer.
        Args:
            screen (pygame.Surface): The screen to draw on.
            background_img (pygame.Surface): The background image.
            star_img (pygame.Surface): The player's star image.
            boost_img (pygame.Surface): The boost stardust image.
            arrow1_img (pygame.Surface): The arrow1 stardust image.
            castle_img (pygame.Surface): The castle image.
            health_img (pygame.Surface): The health stardust image.
            arrow_img (pygame.Surface): The arrow image.
            arrow_stack_img (pygame.Surface): The arrow_stack stardust image.
            mushroom_img (pygame.Surface): The mushroom stardust image.
            wall_img (pygame.Surface): The wall image.
            laser_img (pygame.Surface): The laser image.
            invincibility_img (pygame.Surface): The invincibility power-up image.
            double_damage_img (pygame.Surface): The double damage power-up image.
            rapid_fire_img (pygame.Surface): The rapid fire power-up image.
            screen_width (int): The width of the screen.
            screen_height (int): The height of the screen.
            playable_area_size (int): The size of the playable area.
        """
        self.screen = screen
        self.background_img = background_img
        self.star_img = star_img
        self.boost_img = boost_img
        self.arrow1_img = arrow1_img
        self.castle_img = castle_img
        self.health_img = health_img
        self.arrow_img = arrow_img
        self.arrow_stack_img = arrow_stack_img
        self.mushroom_img = mushroom_img
        self.wall_img = wall_img
        self.laser_img = laser_img
        self.invincibility_img = invincibility_img
        self.double_damage_img = double_damage_img
        self.rapid_fire_img = rapid_fire_img
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.playable_area_size = playable_area_size

    def draw_scene(self, player, stardust_manager, castle_pos, castle_health, wizard_manager):
        """
        Draws the entire scene including the background, player, stardust, lasers, castle, UI, and mini-map.
        Args:
            player (Player): The player object.
            stardust_manager (StarDustManager): The stardust manager object.
            castle_pos (tuple): The position of the castle.
            castle_health (int): The health of the castle.
            wizard_manager (WizardManager): The wizard manager object.
        """
        offset_x = player.position[0] - self.screen_width // 2
        offset_y = player.position[1] - self.screen_height // 2
        self.screen.blit(self.background_img, (-offset_x, -offset_y))
        self.draw_border(offset_x, offset_y)
        self.draw_player(player)
        self.draw_star_dust(stardust_manager.star_dust_list, offset_x, offset_y)
        self.draw_lasers(player.lasers, offset_x, offset_y)
        self.draw_castle(castle_pos, castle_health, offset_x, offset_y)
        self.draw_ui(player)
        self.draw_minimap(player.position, castle_pos, wizard_manager)

    def draw_wizards(self, wizard_manager, player):
        """
        Draws the wizards and their orbs.
        Args:
            wizard_manager (WizardManager): The wizard manager object.
            player (Player): The player object.
        """
        for wizard in wizard_manager.wizards:
            for orb in wizard.orbs[:]:
                orb_rect = pygame.Rect(orb['pos'][0], orb['pos'][1], wizard.orb_image.get_width(), wizard.orb_image.get_height())
                player_rect = pygame.Rect(player.position[0] - player.size, player.position[1] - player.size, player.size * 2, player.size * 2)
                if player_rect.colliderect(orb_rect):
                    player.take_damage(5)

    def draw_castle_lasers(self, castle_lasers, offset_x, offset_y):
        """
        Draws the castle's lasers.
        Args:
            castle_lasers (list): List of the castle's lasers.
            offset_x (int): The x offset for drawing.
            offset_y (int): The y offset for drawing.
        """
        for laser in castle_lasers:
            pygame.draw.rect(self.screen, (255, 0, 0), (laser['pos'][0] - offset_x, laser['pos'][1] - offset_y, 5, 5))

    def draw_border(self, offset_x, offset_y):
        """
        Draws a border around the playable area using the wall image.
        Args:
            offset_x (int): The x offset for drawing.
            offset_y (int): The y offset for drawing.
        """
        wall_width, wall_height = self.wall_img.get_size()
        # Draw top and bottom borders just outside the playable area
        for x in range(-wall_width, self.playable_area_size + wall_width * 2, wall_width):
            self.screen.blit(self.wall_img, (x - offset_x, -wall_height - offset_y))
            self.screen.blit(self.wall_img, (x - offset_x, self.playable_area_size - offset_y))
        # Draw left and right borders just outside the playable area
        for y in range(-wall_height, self.playable_area_size + wall_height * 2, wall_height):
            self.screen.blit(self.wall_img, (-wall_width - offset_x, y - offset_y))
            self.screen.blit(self.wall_img, (self.playable_area_size - offset_x, y - offset_y))

    def draw_player(self, player):
        """
        Draws the player.
        Args:
            player (Player): The player object.
        """
        scaled_star_img = pygame.transform.scale(self.star_img, (player.size * 2, player.size * 2))
        if player.invincibility_end_time and pygame.time.get_ticks() < player.invincibility_end_time:
            # Apply a gold glow effect for invincibility
            gold_glow = pygame.Surface(scaled_star_img.get_size())
            gold_glow.fill((255, 215, 0))  # Gold color
            scaled_star_img.blit(gold_glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        self.screen.blit(scaled_star_img, (self.screen_width // 2 - player.size, self.screen_height // 2 - player.size))
        # Player health bar
        health_bar_length = player.size * 2
        health_ratio = player.health / player.max_health
        health_bar_width = health_ratio * health_bar_length
        pygame.draw.rect(self.screen, (255, 0, 0),
                         (self.screen_width // 2 - player.size, self.screen_height // 2 + player.size, health_bar_length, 5))
        pygame.draw.rect(self.screen, (0, 255, 0),
                         (self.screen_width // 2 - player.size, self.screen_height // 2 + player.size, health_bar_width, 5))
        # Direction arrow
        arrow_radius = player.size + 10
        angle = math.atan2(player.last_direction[1], player.last_direction[0])
        arrow_rotated = pygame.transform.rotate(self.arrow_img, -math.degrees(angle))
        arrow_pos_x = self.screen_width // 2 + arrow_radius * math.cos(angle) - arrow_rotated.get_width() / 2
        arrow_pos_y = self.screen_height // 2 + arrow_radius * math.sin(angle) - arrow_rotated.get_height() / 2
        self.screen.blit(arrow_rotated, (arrow_pos_x, arrow_pos_y))

    def draw_star_dust(self, star_dust_list, offset_x, offset_y):
        """
        Draws the stardust.
        Args:
            star_dust_list (list): List of stardust objects.
            offset_x (int): The x offset for drawing.
            offset_y (int): The y offset for drawing.
        """
        for star_dust in star_dust_list:
            if star_dust['type'] == 'boost':
                self.screen.blit(self.boost_img, (star_dust['pos'][0] - offset_x, star_dust['pos'][1] - offset_y))
            elif star_dust['type'] == 'health':
                self.screen.blit(self.health_img, (star_dust['pos'][0] - offset_x, star_dust['pos'][1] - offset_y))
            elif star_dust['type'] == 'arrow_stack':
                self.screen.blit(self.arrow_stack_img, (star_dust['pos'][0] - offset_x, star_dust['pos'][1] - offset_y))
            elif star_dust['type'] == 'mushroom':
                self.screen.blit(self.mushroom_img, (star_dust['pos'][0] - offset_x, star_dust['pos'][1] - offset_y))
            elif star_dust['type'] == 'invincibility':
                self.screen.blit(self.invincibility_img, (star_dust['pos'][0] - offset_x, star_dust['pos'][1] - offset_y))
            elif star_dust['type'] == 'double_damage':
                self.screen.blit(self.double_damage_img, (star_dust['pos'][0] - offset_x, star_dust['pos'][1] - offset_y))
            elif star_dust['type'] == 'rapid_fire':
                self.screen.blit(self.rapid_fire_img, (star_dust['pos'][0] - offset_x, star_dust['pos'][1] - offset_y))
            else:
                self.screen.blit(self.arrow1_img, (star_dust['pos'][0] - offset_x, star_dust['pos'][1] - offset_y))

    def draw_lasers(self, lasers, offset_x, offset_y):
        """
        Draws the player's lasers.
        Args:
            lasers (list): List of player lasers.
            offset_x (int): The x offset for drawing.
            offset_y (int): The y offset for drawing.
        """
        for laser in lasers:
            # Rotate the laser image based on the direction
            angle = math.degrees(math.atan2(-laser['dir'][1], laser['dir'][0]))
            rotated_laser_img = pygame.transform.rotate(self.laser_img, angle)
            laser_rect = rotated_laser_img.get_rect(center=(laser['pos'][0] - offset_x, laser['pos'][1] - offset_y))
            self.screen.blit(rotated_laser_img, laser_rect.topleft)

    def draw_castle(self, castle_pos, castle_health, offset_x, offset_y):
        """
        Draws the castle and its health bar.
        Args:
            castle_pos (tuple): The position of the castle.
            castle_health (int): The health of the castle.
            offset_x (int): The x offset for drawing.
            offset_y (int): The y offset for drawing.
        """
        self.screen.blit(self.castle_img, (castle_pos[0] - offset_x, castle_pos[1] - offset_y))
        # Draw castle health bar
        if castle_health < StarDustManager.CASTLE_HEALTH:
            health_bar_length = self.castle_img.get_width()
            health_ratio = castle_health / StarDustManager.CASTLE_HEALTH
            health_bar_width = health_ratio * health_bar_length
            pygame.draw.rect(self.screen, (255, 0, 0),
                             (castle_pos[0] - offset_x, castle_pos[1] + self.castle_img.get_height() - offset_y, health_bar_length, 5))
            pygame.draw.rect(self.screen, (0, 255, 0),
                             (castle_pos[0] - offset_x, castle_pos[1] + self.castle_img.get_height() - offset_y, health_bar_width, 5))

    def draw_minimap(self, player_pos, castle_pos, wizard_manager):
        """
        Draws the mini-map showing player, castle, and wizard positions.
        Args:
            player_pos (tuple): The position of the player.
            castle_pos (tuple): The position of the castle.
            wizard_manager (WizardManager): The wizard manager object.
        """
        # Define mini-map position
        minimap_x = self.screen_width - MINIMAP_WIDTH - MINIMAP_MARGIN
        minimap_y = MINIMAP_MARGIN
        # Draw mini-map background
        pygame.draw.rect(self.screen, (50, 50, 50), (minimap_x, minimap_y, MINIMAP_WIDTH, MINIMAP_HEIGHT))
        # Calculate scaled positions
        scale_x = MINIMAP_WIDTH / self.playable_area_size
        scale_y = MINIMAP_HEIGHT / self.playable_area_size
        minimap_player_x = minimap_x + player_pos[0] * scale_x
        minimap_player_y = minimap_y + player_pos[1] * scale_y
        minimap_castle_x = minimap_x + castle_pos[0] * scale_x
        minimap_castle_y = minimap_y + castle_pos[1] * scale_y
        # Draw player position
        pygame.draw.circle(self.screen, (0, 255, 0), (int(minimap_player_x), int(minimap_player_y)), 5)
        # Draw castle position
        pygame.draw.circle(self.screen, (255, 0, 0), (int(minimap_castle_x), int(minimap_castle_y)), 5)
        # Draw wizard positions
        for wizard in wizard_manager.wizards:
            minimap_wizard_x = minimap_x + wizard.position[0] * scale_x
            minimap_wizard_y = minimap_y + wizard.position[1] * scale_y
            pygame.draw.circle(self.screen, (0, 0, 255), (int(minimap_wizard_x), int(minimap_wizard_y)), 5)  # Blue for wizard

    def draw_ui(self, player):
        """
        Draws the UI elements such as arrow1, boost bar, level, and experience bar.
        Args:
            player (Player): The player object.
        """
        font = pygame.font.Font(None, 36)
        arrow1_text = font.render(f'ARROWS: {player.collected_star_dust}', True, (255, 255, 255))
        self.screen.blit(arrow1_text, (10, 10))
        if player.boost_end_time:
            boost_elapsed = (player.boost_end_time - pygame.time.get_ticks()) / 1000.0
            boost_ratio = max(boost_elapsed / BOOST_DURATION, 0)
            boost_bar_width = 100 * boost_ratio
            pygame.draw.rect(self.screen, (255, 0, 0), (10, 50, 100, 10))
            pygame.draw.rect(self.screen, (0, 255, 0), (10, 50, boost_bar_width, 10))
        
        # Pulsing effect for text
        pulse = abs(math.sin(pygame.time.get_ticks() / 250)) * 255  # Pulsing effect
        
        if player.double_damage_end_time and pygame.time.get_ticks() < player.double_damage_end_time:
            double_damage_text = font.render('Double Damage', True, (255, pulse, pulse))
            self.screen.blit(double_damage_text, (10, 80))
        
        if player.rapid_fire_end_time and pygame.time.get_ticks() < player.rapid_fire_end_time:
            rapid_fire_text = font.render('Rapid Fire', True, (255, pulse, pulse))
            self.screen.blit(rapid_fire_text, (10, 110))
            
        level_text = font.render(f'Level: {player.current_level}', True, (255, 255, 255))
        self.screen.blit(level_text, (10, self.screen_height - 50))
        if player.current_level < 99:
            exp_needed = calculate_exp_needed(player.current_level)
            exp_ratio = min(player.current_experience / exp_needed, 1.0)
            exp_bar_width = 100 * exp_ratio
            pygame.draw.rect(self.screen, (255, 0, 0),
                             (10, self.screen_height - 30, 100, 10))
            pygame.draw.rect(self.screen, (0, 255, 0),
                             (10, self.screen_height - 30, exp_bar_width, 10))

    def draw_menu(self):
        """
        Draws the pause menu.
        """
        font = pygame.font.Font(None, 74)
        menu_text = font.render('Paused', True, (255, 255, 255))
        self.screen.blit(menu_text, (self.screen_width // 2 - menu_text.get_width() // 2, self.screen_height // 2 - 100))
        smaller_font = pygame.font.Font(None, 50)
        restart_text = smaller_font.render('Press R to Restart', True, (255, 255, 255))
        self.screen.blit(restart_text, (self.screen_width // 2 - restart_text.get_width() // 2, self.screen_height // 2))