import logging
import math


settings = {
    'battlefield_size': (100, 100),  # metres
    'radar_interval': 10,  # milliseconds
    'max_turns': 1000,  # Limit the game to detect stalemates

    'attack_damage': 20,  # Damage inflicted at range 1m  (decreases by inverse-square law)
    'attack_angle': math.radians(15),  # Attack blasts outwards at this angle (think Claymore)

    'max_speed': 10,  # metres per second
    'log_level': logging.DEBUG
}
