"""
Sample robots

See documentation for RobotBase for details of coroutine methods to
overload.

"""
import math
from rrobot.robot_base import RobotBase, coroutine
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
        if x == x_mid:
            # Horizontal
            if y_mid >= y:
                rads = 0  # To the right
            else:
                rads = math.pi  # To the left
        else:
            rads = math.atan((y_mid - y)/(x_mid - x))
        self.heading = rads
        # Set speed
        self.speed = settings['max_speed']

    @coroutine
    def started(self):
        while True:
            coords = yield
            self._move_to_middle(coords)

    @coroutine
    def bumped(self):
        while True:
            _ = yield
            self._move_to_middle()

    @coroutine
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
    def _find_closest(self, radar, coords=None):
        """
        Find the closest other robot.

        Returns coordinates, distance.
        """
        if coords is None:
            coords = self.coords
        x, y = coords
        d_c = x_c = y_c = None
        for data in radar:
            x_r, y_r = data['coords']
            name = data['name']
            if name == self.__class__.__name__:
                continue
            d = math.sqrt((x_r - x) ** 2 + (y_r - y) ** 2)
            if d_c is None or d < d_c:
                d_c = d
                x_c = x_r
                y_c = y_r
        return (x_c, y_c), d_c

    @coroutine
    def radar_updated(self):
        while True:
            radar = yield
            coords = self.coords
            x, y = coords
            (x_c, y_c), d_c = self._find_closest(radar, coords)
            if d_c is not None:  # distance to closest is None if there are no other robots
                rads = math.atan((y_c - y)/(x_c - x))
                self.heading = rads
                # Hunt
                self.speed = settings['max_speed']
                # Kill. Attacking is free. Why not do it all the time?
                self.attack()


if __name__ == '__main__':
    from rrobot.game import Game
    game = Game([MiddleBot, HunterKiller])
    winners = game.run()
    print(winners)
