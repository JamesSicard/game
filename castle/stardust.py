# castle/stardust.py
import random

class StarDustManager:
    STAR_DUST_SIZE = 30
    BOOST_DURATION = 10
    INVINCIBILITY_DURATION = 10
    DOUBLE_DAMAGE_DURATION = 10
    RAPID_FIRE_DURATION = 10
    CASTLE_HEALTH = 25
    CASTLE_SIZE = 25
    STAR_DUST_CAP = 100  # Cap for the number of star dust on the playable area at one time

    def __init__(self, playable_area_size, castle_size):
        """
        Initializes the StarDustManager.
        
        Args:
            playable_area_size (int): The size of the playable area.
            castle_size (tuple): The size of the castle.
        """
        self.star_dust_list = []
        self.playable_area_size = playable_area_size
        self.castle_size = castle_size
        self.arrow1_ratio = 3  # Ensuring ratio of arrow1 to boost is 3:1
        self.arrow_stack_ratio = 5  # arrow_stack appears at a 1:5 ratio compared to arrow1
        self.mushroom_ratio = 4  # Mushroom appears at a 1:4 ratio compared to arrow1
        self.total_castles_destroyed = 0

        # Initialize castle properties
        self.castle_health = self.CASTLE_HEALTH
        self.castle_pos = self.generate_random_position(self.castle_size[0], self.castle_size[1])

        # Track if a power-up is active
        self.active_power_up = None

    def generate_random_position(self, width, height):
        """
        Generates a random position within the playable area, respecting a 10-pixel border offset.
        
        Args:
            width (int): The width of the object to be placed.
            height (int): The height of the object to be placed.

        Returns:
            list: A list containing the x and y coordinates.
        """
        margin = 10
        x = random.randint(margin, self.playable_area_size - width - margin)
        y = random.randint(margin, self.playable_area_size - height - margin)
        return [x, y]
    
    def create_star_dust(self, position=None, health=False, type=None):
        """
        Creates a stardust object.
        
        Args:
            position (tuple, optional): The position of the stardust. Defaults to None.
            health (bool, optional): Whether the stardust is a health type. Defaults to False.
            type (str, optional): The type of stardust to create. If specified, overrides other settings.
        
        Returns:
            dict: A dictionary representing the stardust with its position and type.
        """
        if type:
            star_dust_type = type
        elif health:
            star_dust_type = 'health'
        elif random.randint(1, self.arrow_stack_ratio + 1) == 1:
            star_dust_type = 'arrow_stack'
        elif random.randint(1, self.mushroom_ratio + 1) == 1:
            star_dust_type = 'mushroom'
        elif random.randint(1, self.arrow1_ratio + 1) == 1:
            star_dust_type = 'boost'
        else:
            star_dust_type = 'arrow1'

        if not position:
            position = self.generate_random_position(self.STAR_DUST_SIZE, self.STAR_DUST_SIZE)
        
        return {'pos': position, 'type': star_dust_type}

    def spawn_star_dust(self):
        """
        Spawns a new stardust object if the cap has not been reached and power-up rules are respected.
        """
        if len(self.star_dust_list) < self.STAR_DUST_CAP:
            # Ensure only one power-up is active on the map
            if not self.active_power_up:
                power_up_type = random.choice(['invincibility', 'double_damage', 'rapid_fire'])
                self.active_power_up = self.create_star_dust(type=power_up_type)
                self.star_dust_list.append(self.active_power_up)
            else:
                self.star_dust_list.append(self.create_star_dust())

    def check_laser_collision(self, position):
        """
        Checks for collisions between lasers and stardust objects.
        
        Args:
            position (tuple): The position of the laser.
        
        Returns:
            bool: True if there is a collision, False otherwise.
        """
        for star_dust in self.star_dust_list[:]:
            if star_dust['pos'][0] <= position[0] <= star_dust['pos'][0] + self.STAR_DUST_SIZE and \
               star_dust['pos'][1] <= position[1] <= star_dust['pos'][1] + self.STAR_DUST_SIZE:
                self.star_dust_list.remove(star_dust)
                if star_dust == self.active_power_up:
                    self.active_power_up = None
                return True
        return False

    def reset_castle(self):
        self.castle_health = self.CASTLE_HEALTH
        self.castle_pos = self.generate_random_position(self.castle_size[0], self.castle_size[1])
        self.total_castles_destroyed += 1