# castle/main.py
import pygame
import sys
import random
import math
from player import Player
from stardust import StarDustManager
from render import Renderer
from utils import gain_experience, reset_game
from wizard_manager import WizardManager  # Import the WizardManager class
from castle import Castle  # Import the Castle class

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
PLAYABLE_AREA_SIZE = 5000

# Damage multiplier starts at 1.0
castle_damage_multiplier = 1.0

def handle_castle_laser_collision(player, castle, stardust_manager, castle_lasers):
    """
    Handles collisions between player lasers and the castle.
    """
    global castle_damage_multiplier
    for laser in player.lasers[:]:
        laser_rect = pygame.Rect(laser['pos'][0], laser['pos'][1], 5, 5)
        adjusted_castle_hitbox = pygame.Rect(castle.position[0], castle.position[1], castle.size[0], castle.size[1])
        if adjusted_castle_hitbox.colliderect(laser_rect):
            castle.take_damage(2)
            player.lasers.remove(laser)
            # Castle counters with a laser
            direction_vector = (player.position[0] - castle.position[0], player.position[1] - castle.position[1])
            distance = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)
            normalized_direction = (direction_vector[0] / distance, direction_vector[1] / distance)
            castle_lasers.append({'pos': list(castle.position), 'dir': normalized_direction})
        # Check if the castle is defeated
        if castle.health <= 0:
            gain_experience(player, 2)  # Grant experience for destroying the castle
            castle.drop_items(stardust_manager)  # Drop items around the castle's position
            castle.reset()
            castle_damage_multiplier += 0.1  # Increase the damage multiplier with each new castle

def handle_castle_laser_movement(castle_lasers, player):
    """
    Handles the movement of the castle's lasers and checks for collisions with the player.
    """
    global castle_damage_multiplier
    for laser in castle_lasers[:]:
        laser['pos'][0] += laser['dir'][0] * 10
        laser['pos'][1] += laser['dir'][1] * 10
        laser_rect = pygame.Rect(laser['pos'][0], laser['pos'][1], 5, 5)
        player_rect = pygame.Rect(player.position[0] - player.size, player.position[1] - player.size, player.size * 2, player.size * 2)
        if player_rect.colliderect(laser_rect):
            player.take_damage(2 * castle_damage_multiplier)  # Player takes damage multiplied by the castle damage multiplier
            castle_lasers.remove(laser)

def handle_wizard_orb_collision(player, wizard_manager):
    """
    Handles the collision between wizard's orbs and the player.
    """
    for wizard in wizard_manager.wizards:
        for orb in wizard.orbs[:]:
            orb_rect = pygame.Rect(orb['pos'][0], orb['pos'][1], wizard.orb_image.get_width(), wizard.orb_image.get_height())
            player_rect = pygame.Rect(player.position[0] - player.size, player.position[1] - player.size, player.size * 2, player.size * 2)
            if player_rect.colliderect(orb_rect):
                player.take_damage(5)  # Player takes 5 damage from the wizard orb
                wizard.orbs.remove(orb)

def handle_player_laser_collision_with_wizard(player, wizard_manager):
    """
    Handles the collision between player's lasers and the wizard.
    """
    for wizard in wizard_manager.wizards:
        for laser in player.lasers[:]:
            laser_rect = pygame.Rect(laser['pos'][0], laser['pos'][1], 5, 5)
            wizard_hitbox = pygame.Rect(wizard.position[0] - wizard.size, wizard.position[1] - wizard.size, wizard.size * 2, wizard.size * 2)
            if wizard_hitbox.colliderect(laser_rect):
                wizard.take_damage(5)  # Wizard takes 5 damage from player's laser
                player.lasers.remove(laser)
            if wizard.health <= 0:
                gain_experience(player, 5)  # Grant experience for killing the wizard
                wizard_manager.handle_collisions(player)  # Handle wizard removal

def draw_game_over(screen):
    """
    Draws the game over screen with 'LOSER' and the restart instructions.
    """
    font_large = pygame.font.Font(None, 74)
    font_small = pygame.font.Font(None, 50)
    loser_text = font_large.render('LOSER', True, (255, 0, 0))
    restart_text = font_small.render('Press (R) to Restart', True, (255, 255, 255))
    screen.blit(loser_text, (SCREEN_WIDTH // 2 - loser_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Castle Defense')
    # Assets loading here
    star_img = pygame.image.load('pics/archer.png')
    background_img = pygame.image.load('pics/background.png')
    background_img = pygame.transform.scale(background_img, (PLAYABLE_AREA_SIZE, PLAYABLE_AREA_SIZE))
    boost_img = pygame.image.load('pics/bolt.png')
    arrow1_img = pygame.image.load('pics/arrow1.png')
    castle_img = pygame.image.load('pics/castle.png')
    arrow_img = pygame.image.load('pics/arrow.png')
    health_img = pygame.image.load('pics/health.png')
    arrow_stack_img = pygame.image.load('pics/arrow_stack.png')
    mushroom_img = pygame.image.load('pics/mushroom.png')  # Load the mushroom image
    wall_img = pygame.image.load('pics/wall.png')  # Load the wall image
    bear_img = pygame.image.load('pics/bear.png')  # Load the bear image
    laser_img = pygame.image.load('pics/laser.png')  # Load the laser image
    
    # Load power-up images
    invincibility_img = pygame.image.load('pics/invincibility.png')
    double_damage_img = pygame.image.load('pics/double_damage.png')
    rapid_fire_img = pygame.image.load('pics/rapid_fire.png')
    
    # Get castle rect
    castle_rect = castle_img.get_rect()
    CASTLE_SIZE = castle_rect.size

    # Initial player properties
    player = Player(playable_area_size=PLAYABLE_AREA_SIZE)
    stardust_manager = StarDustManager(playable_area_size=PLAYABLE_AREA_SIZE, castle_size=CASTLE_SIZE)
    renderer = Renderer(
        screen, background_img, star_img, boost_img, arrow1_img, castle_img,
        health_img, arrow_img, arrow_stack_img, mushroom_img, wall_img, laser_img,
        invincibility_img, double_damage_img, rapid_fire_img,
        SCREEN_WIDTH, SCREEN_HEIGHT, PLAYABLE_AREA_SIZE
    )
    wizard_manager = WizardManager(PLAYABLE_AREA_SIZE, player, stardust_manager)  # Create a wizard manager instance
    castle = Castle(playable_area_size=PLAYABLE_AREA_SIZE, castle_size=CASTLE_SIZE)  # Create a castle instance
    castle_lasers = []

    clock = pygame.time.Clock()
    running = True
    paused = False
    game_over = False

    reset_game(player, stardust_manager)
    wizard_manager.reset()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        reset_game(player, stardust_manager)
                        wizard_manager.reset()
                        game_over = False
                else:
                    if event.key == pygame.K_p:
                        paused = not paused
                    elif paused and event.key == pygame.K_r:
                        reset_game(player, stardust_manager)
                        paused = False
                    elif event.key == pygame.K_SPACE and player.collected_star_dust >= player.laser_cost:
                        player.shoot_laser()

        if not paused and not game_over:
            keys = pygame.key.get_pressed()
            player.handle_movement(keys, castle.position, CASTLE_SIZE)
            player.check_collisions(stardust_manager)
            player.handle_laser_movement(stardust_manager)
            player.update_status()  # This will update the player's status, including resetting the speed if boost ends
            stardust_manager.spawn_star_dust()
            
            # Handle wizard manager updates, including spawning new wizards based on the player's level
            wizard_manager.update(castle.position, CASTLE_SIZE)

            # Handle laser collision with the castle
            handle_castle_laser_collision(player, castle, stardust_manager, castle_lasers)

            # Handle castle laser movement
            handle_castle_laser_movement(castle_lasers, player)

            # Handle wizard orb collision with player
            handle_wizard_orb_collision(player, wizard_manager)

            # Handle player laser collision with wizard
            handle_player_laser_collision_with_wizard(player, wizard_manager)

            # Check for game over condition
            if player.health <= 0:
                game_over = True

            # Clear screen
            screen.fill((0, 0, 0))
            if not game_over:
                renderer.draw_scene(player, stardust_manager, castle.position, castle.health, wizard_manager)
                renderer.draw_castle_lasers(castle_lasers, player.position[0] - SCREEN_WIDTH // 2, player.position[1] - SCREEN_HEIGHT // 2)
                castle.draw_castle(screen, castle_img, player.position[0] - SCREEN_WIDTH // 2, player.position[1] - SCREEN_HEIGHT // 2)
                wizard_manager.draw(screen, player.position[0] - SCREEN_WIDTH // 2, player.position[1] - SCREEN_HEIGHT // 2)
            if game_over:
                draw_game_over(screen)
            elif paused:
                renderer.draw_menu()

        elif paused:
            renderer.draw_menu()
            pygame.display.flip()
            clock.tick(60)
            continue

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()