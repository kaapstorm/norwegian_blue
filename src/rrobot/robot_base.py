import asyncio
from rrobot.game_client import GameClient


class RobotBase(object):
    """
    Extend the RobotBase class to create your robot.

    RobotBase provides the following read-only properties:
     * coords: Cartesian coordinates of the robot with the origin in the
               southwest corner of the battlefield
     * damage: An integer percentage, where 0 is healthy and 100 is destroyed.

    Robot status can be read and set using:
     * heading: The robot's heading in radians counterclockwise from east
     * speed: The robot's speed in metres per second

    The robot can attack another robot using the "attack" method. It takes no
    parameters. It simply strikes out in front of the robot.

    The robot is notified of activity with the following coroutines:
     * started: The game is started. Starting coordinates are sent.
     * bumped: The (absolute) heading of the bump is sent.
     * attacked: The robot was successfully attacked by another robot. The
                 (absolute) heading of the attack is sent.
     * radar_updated: This method is called at a regular interval with the
                      latest radar data. The interval is configured in
                      settings['radar_interval'].

    """
    # <METHODS_TO_OVERLOAD>

    def started(self):
        """
        Called when the game starts

        The coroutine is sent a tuple of x-y coordinates of the robot, e.g.
        (56, 32)
        """
        coords = yield

    def attacked(self):
        """
        Called when this robot is attacked by another robot,

        The coroutine is sent the (absolute) heading in radians from which the
        robot was attacked.
        """
        while True:
            heading = yield

    def bumped(self):
        """
        Called when robot this bumps or is bumped

        The coroutine is sent the (absolute) heading in radians where the
        robot was bumped.
        """
        while True:
            heading = yield

    def radar_updated(self):
        """
        Called at a regular interval.

        The coroutine is sent a dictionary of coordinates and robot class
        names, e.g. ::

            {(15, 40): 'Clango', (56, 32): 'Daneel'}

        """
        while True:
            radar = yield

    # </METHODS_TO_OVERLOAD>

    def __init__(self, id_):
        self.__id = id_
        self._client = GameClient()
        # Start coroutines
        next(self.started())
        next(self.attacked())
        next(self.bumped())
        next(self.radar_updated())

    @property
    @asyncio.coroutine
    def coords(self):
        """Coordinates (origin southwest corner of battlefield)"""
        #return self._game.send_sync('get_coords', self.__id)
        coords = yield from self._client.send_async('get_coords', self.__id)
        return coords

    @property
    @asyncio.coroutine
    def damage(self):
        """Damage rating of 0 to 99"""
        #return self._game.send_sync('get_damage', self.__id)
        damage = yield from self._client.send_async('get_damage', self.__id)
        return damage

    @property
    @asyncio.coroutine
    def heading(self):
        """Heading (radians counterclockwise from east)"""
        #return self._game.send_sync('get_heading', self.__id)
        rads = yield from self._client.send_async('get_heading', self.__id)
        return rads

    @heading.setter
    def heading(self, rads):
        #self.__heading.send(rads)
        self._client.send_async('set_heading', self.__id, rads)

    @property
    @asyncio.coroutine
    def speed(self):
        """Speed (metres per second)"""
        #return self._game.send_sync('get_speed', self.__id)
        mps = yield from self._client.send_async('get_speed', self.__id)
        return mps

    @speed.setter
    def speed(self, mps):
        #self.__speed.send(mps)
        self._client.send_async('set_speed', self.__id, mps)

    def attack(self):
        self._client.send_async('attack', self.__id)
