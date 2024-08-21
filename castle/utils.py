# castle/utils.py
import pygame
import random
from stardust import StarDustManager
from castle import Castle  # Import the Castle class

def calculate_exp_needed(level):
    """
    Calculate the experience needed to reach the next level.
    
    Args:
        level (int): The current level of the player.
    
    Returns:
        int: The experience needed to reach the next level.
    """
    return (level ** 2) * 10

def gain_experience(player, amount):
    """
    Grant experience to the player and level up if enough experience is gained.
    
    Args:
        player (Player): The player object.
        amount (int): The amount of experience to grant.
    """
    player.current_experience += amount
    while player.current_experience >= calculate_exp_needed(player.current_level) and player.current_level < 25:
        player.current_experience -= calculate_exp_needed(player.current_level)
        player.current_level += 1
        player.max_health += 5

def reset_game(player, stardust_manager):
    """
    Reset the game to its initial state.
    
    Args:
        player (Player): The player object.
        stardust_manager (StarDustManager): The stardust manager object.
    """
    # Reset player properties
    player.speed = 5
    player.boost_end_time = 10
    player.collected_star_dust = 0
    player.position = [player.playable_area_size // 2, player.playable_area_size // 2]
    player.lasers = []
    player.last_direction = (1, 0)
    player.current_level = 1
    player.current_experience = 0
    player.health = player.max_health
    player.last_spawn_time = pygame.time.get_ticks()   

    # Reset stardust
    stardust_manager.star_dust_list = [stardust_manager.create_star_dust() for _ in range(40)]