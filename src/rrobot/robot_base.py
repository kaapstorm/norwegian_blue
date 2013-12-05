import asyncio
#from rrobot.game_client import GameClient


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
     * bumped: The robot collided with the border or another robot.
     * attacked: The robot was successfully attacked by another robot.
     * radar_updated: This method is called at a regular interval with the
                      latest radar data. The interval is configured in
                      settings['radar_interval'].

    """
    # <METHODS_TO_OVERLOAD>

    def started(self):
        """
        Coroutine, called when the game starts

        Is sent the coordinates of this robot, e.g. (56, 32)
        """
        while True:
            coords = yield

    def attacked(self):
        """
        Coroutine, called when this robot is attacked by another robot

        Is sent the class name of the attacking robot
        """
        while True:
            attacker = yield

    def bumped(self):
        """
        Coroutine, called when this robot bumps another robot or a boundary

        Is sent the class name of the other robot, or "top", "bottom", "left"
        or "right"
        """
        while True:
            bumper = yield

    def radar_updated(self):
        """
        Coroutine, called at the regular interval settings['radar_interval']

        The coroutine is sent a dictionary of coordinates and robot class
        names, e.g. ::

            {(15, 40): 'Clango', (56, 32): 'Daneel'}

        """
        while True:
            radar = yield

    # </METHODS_TO_OVERLOAD>

    def __init__(self, game, id_):
        self._id = id_
        self._game = game
        # Start coroutines
        next(self.started())
        next(self.attacked())
        next(self.bumped())
        next(self.radar_updated())

    @property
    @asyncio.coroutine
    def coords(self):
        """Coordinates (origin southwest corner of battlefield)"""
        coords = yield from self._game.get_coords(self._id)
        return coords

    @property
    @asyncio.coroutine
    def damage(self):
        """Damage rating of 0 to 99"""
        damage = yield from self._game.get_damage(self._id)
        return damage

    @property
    @asyncio.coroutine
    def heading(self):
        """Heading (radians counterclockwise from east)"""
        rads = yield from self._game.get_heading(self._id)
        return rads

    @heading.setter
    def heading(self, rads):
        self._game.set_heading(self._id, rads)

    @property
    @asyncio.coroutine
    def speed(self):
        """Speed (metres per second)"""
        mps = yield from self._game.get_speed(self._id)
        return mps

    @speed.setter
    def speed(self, mps):
        self._game.set_speed(self._id, mps)

    def attack(self):
        self._game.attack(self._id)
