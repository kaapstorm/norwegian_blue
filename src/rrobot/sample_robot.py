"""
Sample robots

See documentation for RobotBase for details of coroutine methods to
overload.

"""
import math
from rrobot.robot_base import RobotBase
from rrobot.settings import settings


class MiddleBot(RobotBase):
    """
    Drives to the middle of the battlefield and stops.
    """
    @staticmethod
    def _get_middle():
        """
        Returns the coordinates of the middle of the battlefield

        >>> settings = {'battlefield_size': (10, 10)}
        >>> MiddleBot._get_middle()
        (5, 5)

        """
        x_max, y_max = settings['battlefield_size']
        return x_max / 2, y_max / 2

    def _move_to_middle(self, coords=None):
        if coords is None:
            coords = self.coords
        x, y = coords
        # Move to middle
        x_mid, y_mid = self._get_middle()
        # Set heading
        rads = math.atan((y_mid - y)/(x_mid - x))
        self.heading = rads
        # Set speed
        self.speed = settings['max_speed']

    def started(self):
        while True:
            coords = yield
            self._move_to_middle(coords)

    def bumped(self):
        while True:
            _ = yield
            self._move_to_middle()

    def radar_updated(self):
        while True:
            _ = yield
            # Are we there yet?
            x, y = self.coords
            x_mid, y_mid = self._get_middle()
            x_d, y_d = x_mid - x, y_mid - y
            dist = math.sqrt(x_d ** 2 + y_d ** 2)
            if dist < 10:
                # Stop
                self.speed = 0


class HunterKiller(RobotBase):
    """
    Chases the closest robot, attacking it constantly.
    """
    def radar_updated(self):
        """
        Called at a regular interval.
        """
        while True:
            radar = yield
            # TODO: hunt, kill
