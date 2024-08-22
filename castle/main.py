# castle/main.py
import pygame
import sys
import random
import math
from player import Player
from stardust import StarDustManager
from render import Renderer
from utils import gain_experience, reset_game
from wizard_manager import WizardManager
from castle import Castle

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
PLAYABLE_AREA_SIZE = 5000

castle_damage_multiplier = 1.0

def handle_castle_laser_collision(player, castle, stardust_manager, castle_lasers):
    global castle_damage_multiplier
    for laser in player.lasers[:]:
        laser_rect = pygame.Rect(laser['pos'][0], laser['pos'][1], 5, 5)
        adjusted_castle_hitbox = pygame.Rect(castle.position[0], castle.position[1], castle.size[0], castle.size[1])
        if adjusted_castle_hitbox.colliderect(laser_rect):
            castle.take_damage(laser['damage'])
            player.lasers.remove(laser)
            direction_vector = (player.position[0] - castle.position[0], player.position[1] - castle.position[1])
            distance = math.sqrt(direction_vector[0] ** 2 + direction_vector[1] ** 2)
            normalized_direction = (direction_vector[0] / distance, direction_vector[1] / distance)
            castle_lasers.append({'pos': list(castle.position), 'dir': normalized_direction})
        if castle.health <= 0:
            gain_experience(player, 10)
            castle.drop_items(stardust_manager)
            castle.reset()
            castle_damage_multiplier += 0.1

def handle_castle_laser_movement(castle_lasers, player):
    global castle_damage_multiplier
    for laser in castle_lasers[:]:
        laser['pos'][0] += laser['dir'][0] * 10
        laser['pos'][1] += laser['dir'][1] * 10
        laser_rect = pygame.Rect(laser['pos'][0], laser['pos'][1], 5, 5)
        player_rect = pygame.Rect(player.position[0] - player.size, player.position[1] - player.size, player.size * 2, player.size * 2)
        if player_rect.colliderect(laser_rect):
            player.take_damage(2 * castle_damage_multiplier)
            castle_lasers.remove(laser)

def handle_wizard_orb_collision(player, wizard_manager):
    for wizard in wizard_manager.wizards:
        for orb in wizard.orbs[:]:
            orb_rect = pygame.Rect(orb['pos'][0], orb['pos'][1], wizard.orb_image.get_width(), wizard.orb_image.get_height())
            player_rect = pygame.Rect(player.position[0] - player.size, player.position[1] - player.size, player.size * 2, player.size * 2)
            if player_rect.colliderect(orb_rect):
                player.take_damage(5)
                wizard.orbs.remove(orb)

def handle_player_laser_collision_with_wizard(player, wizard_manager):
    for wizard in wizard_manager.wizards:
        for laser in player.lasers[:]:
            laser_rect = pygame.Rect(laser['pos'][0], laser['pos'][1], 5, 5)
            wizard_hitbox = pygame.Rect(wizard.position[0] - wizard.size, wizard.position[1] - wizard.size, wizard.size * 2, wizard.size * 2)
            if wizard_hitbox.colliderect(laser_rect):
                wizard.take_damage(laser['damage'])
                player.lasers.remove(laser)
            if wizard.health <= 0:
                gain_experience(player, 5)
                wizard_manager.handle_collisions(player)

def draw_game_over(screen):
    font_large = pygame.font.Font(None, 74)
    font_small = pygame.font.Font(None, 50)
    loser_text = font_large.render('LOSER', True, (255, 0, 0))
    restart_text = font_small.render('Press (R) to Restart', True, (255, 255, 255))
    quit_text = font_small.render('Press (Q) to Quit', True, (255, 255, 255))
    screen.blit(loser_text, (SCREEN_WIDTH // 2 - loser_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Castle Defense')
    star_img = pygame.image.load('pics/archer.png')
    background_img = pygame.image.load('pics/background.png')
    background_img = pygame.transform.scale(background_img, (PLAYABLE_AREA_SIZE, PLAYABLE_AREA_SIZE))
    boost_img = pygame.image.load('pics/bolt.png')
    arrow1_img = pygame.image.load('pics/arrow1.png')
    castle_img = pygame.image.load('pics/castle.png')
    arrow_img = pygame.image.load('pics/arrow.png')
    health_img = pygame.image.load('pics/health.png')
    arrow_stack_img = pygame.image.load('pics/arrow_stack.png')
    mushroom_img = pygame.image.load('pics/mushroom.png')
    wall_img = pygame.image.load('pics/wall.png')
    bear_img = pygame.image.load('pics/bear.png')
    laser_img = pygame.image.load('pics/laser.png')
    invincibility_img = pygame.image.load('pics/invincibility.png')
    double_damage_img = pygame.image.load('pics/double_damage.png')
    rapid_fire_img = pygame.image.load('pics/rapid_fire.png')
    menu_img = pygame.image.load('pics/menu.png')

    castle_rect = castle_img.get_rect()
    CASTLE_SIZE = castle_rect.size
    
    player = Player(playable_area_size=PLAYABLE_AREA_SIZE)
    stardust_manager = StarDustManager(playable_area_size=PLAYABLE_AREA_SIZE, castle_size=CASTLE_SIZE)
    renderer = Renderer(
        screen, background_img, star_img, boost_img, arrow1_img, castle_img,
        health_img, arrow_img, arrow_stack_img, mushroom_img, wall_img, laser_img,
        invincibility_img, double_damage_img, rapid_fire_img, menu_img,
        SCREEN_WIDTH, SCREEN_HEIGHT, PLAYABLE_AREA_SIZE
    )
    wizard_manager = WizardManager(PLAYABLE_AREA_SIZE, player, stardust_manager)
    castle = Castle(playable_area_size=PLAYABLE_AREA_SIZE, castle_size=CASTLE_SIZE)
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
                        wizard_manager.reset()
                        castle.reset()
                    elif paused and event.key == pygame.K_q:
                        # Quit the game
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if renderer.menu_button_rect.collidepoint(mouse_pos):
                    paused = not paused

        if not paused and not game_over:
            keys = pygame.key.get_pressed()
            player.handle_movement(keys, castle.position, CASTLE_SIZE)
            player.check_collisions(stardust_manager)
            player.handle_laser_movement(stardust_manager, wizard_manager, castle)
            player.update_status()
            player.handle_shooting(keys)
            stardust_manager.spawn_star_dust()
            wizard_manager.update(castle.position, CASTLE_SIZE)
            handle_castle_laser_collision(player, castle, stardust_manager, castle_lasers)
            handle_castle_laser_movement(castle_lasers, player)
            handle_wizard_orb_collision(player, wizard_manager)
            handle_player_laser_collision_with_wizard(player, wizard_manager)
            
            if not paused and player.health <= 0:
                game_over = True            
            screen.fill((0, 0, 0))

            if not game_over:
                renderer.draw_scene(player, stardust_manager, castle.position, castle.health, wizard_manager)
                renderer.draw_castle_lasers(castle_lasers, player.position[0] - SCREEN_WIDTH // 2, player.position[1] - SCREEN_HEIGHT // 2)
                castle.draw_castle(screen, castle_img, player.position[0] - SCREEN_WIDTH // 2, player.position[1] - SCREEN_HEIGHT // 2)
                renderer.draw_menu_button()
                wizard_manager.draw(screen, player.position[0] - SCREEN_WIDTH // 2, player.position[1] - SCREEN_HEIGHT // 2)
            # Draw game over screen
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