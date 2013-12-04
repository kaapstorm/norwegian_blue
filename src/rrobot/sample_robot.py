import math
from rrobot.robot_base import RobotBase
from rrobot.settings import settings


class SampleRobot(RobotBase):
    """
    Drives to the middle of the battlefield and stops
    """
    @staticmethod
    def _get_middle():
        """
        Returns the coordinates of the middle of the battlefield
        """
        x_max, y_max = settings['battlefield_size']
        return x_max / 2, y_max / 2

    def started(self):
        """
        Called when the game starts
        """
        x, y = yield
        # Move to middle
        x_mid, y_mid = self._get_middle()
        # Set heading
        rads = math.atan((y_mid - y)/(x_mid - x))
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
        Called at a regular interval.
        """
        while True:
            radar = yield
            # Are we there yet?
            x, y = self.coords
            x_mid, y_mid = self._get_middle()
            x_d, y_d = x_mid - x, y_mid - y
            dist = math.sqrt(pow(x_d, 2) + pow(y_d, 2))
            if dist < 10:
                # Stop
                self.speed = 0
