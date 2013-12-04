import math
from rrobot.robot_base import RobotBase
from rrobot.settings import settings


class SampleRobot(RobotBase):
    """
    Drives to the middle of the battlefield and stops
    """
    def started(self):
        """
        Called when the game starts
        """
        x, y = yield
        # Move to middle
        x_max, y_max = settings['battlefield_size']
        x_mid, y_mid = x_max / 2, y_max / 2
        # Set heading
        rads = math.tan((y_mid - y)/(x_mid - x))
        self.heading = rads
        # Set speed
        self.speed = 10

    def attacked(self):
        """
        Called when this robot is attacked by another robot
        """
        while True:
            heading = yield

    def bumped(self):
        """
        Called when this robot bumps or is bumped
        """
        while True:
            heading = yield

    def radar_updated(self):
        """
        Called at a regular interval
        """
        while True:
            radar = yield
            # Are we there yet?
            x, y = self.coords
            x_max, y_max = settings['battlefield_size']
            x_mid, y_mid = x_max / 2, y_max / 2
            x_dist, y_dist = x_mid - x, y_mid - y
            hyp = math.sqrt(pow(x_dist, 2) + pow(y_dist, 2))
            if hyp < 10:
                # Stop
                self.speed = 0
