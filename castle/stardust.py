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
    POWER_UP_CAP = 4  # Cap for the number of power-ups on the playable area at one time

    def __init__(self, playable_area_size, castle_size):
        self.star_dust_list = []
        self.playable_area_size = playable_area_size
        self.castle_size = castle_size
        self.arrow1_ratio = 3  # Ensuring ratio of arrow1 to boost is 3:1
        self.arrow_stack_ratio = 5  # arrow_stack appears at a 1:5 ratio compared to arrow1
        self.mushroom_ratio = 4  # Mushroom appears at a 1:4 ratio compared to arrow1
        self.total_castles_destroyed = 0
        self.active_power_ups = []  # Track active power-ups

        self.castle_health = self.CASTLE_HEALTH
        self.castle_pos = self.generate_random_position(self.castle_size[0], self.castle_size[1])

    def generate_random_position(self, width, height):
        margin = 10
        x = random.randint(margin, self.playable_area_size - width - margin)
        y = random.randint(margin, self.playable_area_size - height - margin)
        return [x, y]
    
    def create_star_dust(self, position=None, health=False, type=None):
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
        if len(self.star_dust_list) < self.STAR_DUST_CAP:
            power_up_types = ['invincibility', 'double_damage', 'rapid_fire']
            active_power_up_count = sum(1 for sd in self.star_dust_list if sd['type'] in power_up_types)
            if active_power_up_count < self.POWER_UP_CAP:
                power_up_type = random.choice(power_up_types)
                power_up = self.create_star_dust(type=power_up_type)
                self.star_dust_list.append(power_up)
                self.active_power_ups.append(power_up)
            else:
                self.star_dust_list.append(self.create_star_dust())

    def check_laser_collision(self, position):
        for star_dust in self.star_dust_list[:]:
            if star_dust['pos'][0] <= position[0] <= star_dust['pos'][0] + self.STAR_DUST_SIZE and \
               star_dust['pos'][1] <= position[1] <= star_dust['pos'][1] + self.STAR_DUST_SIZE:
                self.star_dust_list.remove(star_dust)
                if star_dust in self.active_power_ups:
                    self.active_power_ups.remove(star_dust)
                return True
        return False

    def reset_castle(self):
        self.castle_health = self.CASTLE_HEALTH
        self.castle_pos = self.generate_random_position(self.castle_size[0], self.castle_size[1])
        self.total_castles_destroyed += 1