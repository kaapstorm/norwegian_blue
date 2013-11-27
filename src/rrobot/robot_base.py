from game import game


class RobotBase(object):
    """
    Extend the RobotBase class to create your robot.

    RobotBase provides the following read-only properties:
     * coords: Cartesian coordinates of the robot with the origin in the
               southwest corner of the battlefield
     * damage: A rating from 0 (healthy) to 99 (brink of destruction)

    Robot status can be read and set using:
     * heading: The robot's heading in radians clockwise from north
     * speed: The robot's speed in metres per second

    The robot can attack another robot using the "strike" method.

    It is alerted to activity with the following methods:
     * bumped: No data is passed. The robot will need to use the last radar
               data and its coordinates to figure out what happened.
     * was_struck: The robot was successfully attacked by another robot
     * radar_updated: This method is called every 500 milliseconds with the
                      latest radar data

    """
    def __init__(self, id_):
        self.__id = id_
        self.__heading = self.__set_heading()
        next(self.__heading)
        self.__speed = self.__set_speed()
        next(self.__speed)

    @property
    def coords(self):
        """Coordinates (origin southwest corner of battlefield)"""
        return game.get_coords(self.__id)

    @property
    def damage(self):
        """Damage rating of 0 to 99"""
        return game.get_damage(self.__id)

    @property
    def heading(self):
        """Heading (radians clockwise from north)"""
        return game.get_heading(self.__id)

    @heading.setter
    def heading(self, radians):
        self.__heading.send(radians)

    @property
    def speed(self):
        """Speed (metres per second)"""
        return game.get_speed(self.__id)

    @speed.setter
    def speed(self, mps):
        self.__speed.send(mps)

    def strike(self):
        game.enqueue_strike(self.__id)

    def bumped(self):
        """
        Called when robot bumps or is bumped
        """
        pass

    def radar_updated(self, radar):
        """
        Called every 500ms
        """
        pass

    def was_struck(self):
        """
        Called when robot is struck
        """
        pass

    def __set_heading(self):
        """
        Coroutine that accepts a heading in radians clockwise from north
        """
        while True:
            radians = yield  # radians clockwise from north
            game.enqueue_heading(self.__id, radians)

    def __set_speed(self):
        """
        Coroutine that accepts a speed in metres per second
        """
        while True:
            mps = yield  # radians clockwise from north
            game.enqueue_heading(self.__id, mps)
