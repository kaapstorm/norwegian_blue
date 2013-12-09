"""
Sample robots

See documentation for RobotBase for details of coroutine methods to
overload.

"""
import math
from rrobot.maths import get_heading_p2p
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

        >>> MiddleBot._get_middle()  # Assumes default 100 x 100 battlefield
        (50.0, 50.0)

        """
        x_max, y_max = settings['battlefield_size']
        return x_max / 2, y_max / 2

    def _move_to_middle(self, coords=None):
        """
        Sets heading and speed to move to the middle of the battlefield
        """
        if coords is None:
            coords = self.coords
        # Move to middle
        middle = self._get_middle()
        # Set heading
        self.heading = get_heading_p2p(coords, middle)
        # Set speed
        # TODO: Set speed according to how close we are
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
        """
        Stops when the robot is close to the middle
        """
        while True:
            _ = yield
            # Are we there yet?
            x, y = self.coords
            x_mid, y_mid = self._get_middle()
            x_d, y_d = x_mid - x, y_mid - y
            dist = math.sqrt(x_d ** 2 + y_d ** 2)
            # TODO: Reduce speed as we approach
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
        dist = closest = None
        for robot in radar:
            x_r, y_r = robot['coords']
            name = robot['name']
            if name == self.__class__.__name__:
                continue
            d = math.sqrt((x_r - x) ** 2 + (y_r - y) ** 2)
            if dist is None or d < dist:
                dist = d
                closest = (x_r, y_r)
        return closest, dist

    @coroutine
    def radar_updated(self):
        while True:
            radar = yield
            coords = self.coords
            closest, dist = self._find_closest(radar, coords)
            if dist is not None:  # distance to closest is None if there are no other robots
                self.heading = get_heading_p2p(coords, closest)
                # Hunt
                self.speed = settings['max_speed']
                # Kill. Attacking is free. Why not do it all the time?
                self.attack()


if __name__ == '__main__':
    from rrobot.game import Game
    game = Game([MiddleBot, HunterKiller])
    winners = game.run()
    print(winners)
