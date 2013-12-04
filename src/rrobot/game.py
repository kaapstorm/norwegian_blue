import argparse
import math
import asyncio
import logging
import random
import sys
from rrobot.settings import settings
from rrobot.maths import seg_intersect


# TODO: Add power. Attacks, accelleration, and maintaining speed cost power
# TODO: Manage speed.


logger = logging.getLogger(__name__)


class Game(object):
    def __init__(self, robot_classes):
        """
        Accepts an iterable of Robot classes, and initialises a battlefield
        with them.
        """
        x_max, y_max = settings['battlefield_size']
        x_rand, y_rand = random.randrange(0, x_max), random.randrange(0, y_max)
        self._field = {}  # Dictionary of battlefield data, keyed by robot ID
        for robot_id, Robot in enumerate(robot_classes):
            self._field[robot_id] = {
                'robot': Robot(robot_id),
                'coords': (float(x_rand), float(y_rand)),
                'speed': 0.0,
                'damage': 0,
                'heading': 0.0,
                'then': None  # Timestamp of last move
            }

    def _get_robot_attr(self, robot_id, attr):
        return self._field[robot_id][attr]

    def _set_robot_attr(self, robot_id, attr, value):
        logger.info('<{name} {robot_id}> {attr} = {value!r}'.format(
            name=self._field[robot_id].__class__.__name__,
            robot_id=robot_id,
            attr=attr,
            value=value))
        self._field[robot_id][attr] = value

    def get_coords(self, robot_id):
        return self._get_robot_attr(robot_id, 'coords')

    def get_damage(self, robot_id):
        return self._get_robot_attr(robot_id, 'damage')

    def get_heading(self, robot_id):
        return self._get_robot_attr(robot_id, 'heading')

    def set_heading(self, robot_id, rads):
        self._set_robot_attr(robot_id, 'heading', rads)

    def get_speed(self, robot_id):
        return self._get_robot_attr(robot_id, 'speed')

    def set_speed(self, robot_id, mps):
        self._set_robot_attr(robot_id, 'speed', mps)

    def attack(self, robot_id):
        # TODO: attack
        pass

    def active_robots(self):
        """
        Returns a set of robot IDs with damage < 100%
        """
        return {i for i, d in self._field.items() if d['damage'] < 100}

    @staticmethod
    def _get_line_seg(data, now):
        """
        Calculates the line segment representing a move based on the passed
        robot data and the current time.

        >>> data = {
        ...     'coords': (2, 2),
        ...     'then': 1,
        ...     'speed': 5,
        ...     'heading': 0
        ... }
        >>> Game._get_line_seg(data, 2)
        ((2, 2), (7, 2))

        """
        # Calc new position
        x, y = data['coords']
        t_d = now - data['then']
        dist = data['speed'] * t_d
        x_d = math.cos(data['heading']) * dist
        y_d = math.sin(data['heading']) * dist
        x_new, y_new = x + x_d, y + y_d
        return (x, y), (x_new, y_new)

    @asyncio.coroutine
    def _update_radar(self, robot_ids):
        radar = {d['coords']: d['robot'].__class__.__name__ for d in self._field.values()}
        for robot_id in robot_ids:
            logger.info('<{name} {robot_id}> radar_updated'.format(
                name=self._field[robot_id]['robot'].__class__.__name__,
                robot_id=robot_id))
            # yield from self._field[robot_id]['robot'].radar_updated().send(radar)  # TODO: Wait?
            self._field[robot_id]['robot'].radar_updated().send(radar)

    @staticmethod
    def _get_intersections(line_segs):
        """
        Return the intersections line segments.

        >>> line_segs = {
        ...     'foo': ((1, 1), (5, 5)),
        ...     'bar': ((1, 3), (3, 1)),
        ...     'baz': ((2, 4), (4, 2))
        ... }
        >>> Game._get_intersections(line_segs) == {
        ...     ('foo', 'bar'): (2, 2),
        ...     ('bar', 'foo'): (2, 2)
        ... }
        True

        """
        # Check intersections of each line segment with each other
        intersections = {}
        for a_id, (a1, a2) in line_segs.items():
            for b_id, (b1, b2) in line_segs.items():
                if a_id == b_id:
                    continue
                intersection = seg_intersect(a1, a2, b1, b1)
                if intersection:
                    intersections[(a_id, b_id)] = intersection
        # TODO: Find where line segments intersect multiple times, and return first intersections
        return intersections

    @asyncio.coroutine
    def _move_robots(self, robot_ids):
        # Calculate moves as line segments
        loop = asyncio.get_event_loop()
        now = loop.time()
        x_max, y_max = settings['battlefield_size']
        line_segs = {
            'left': ((0, 0), (0, y_max)),
            'top': ((0, y_max), (x_max, y_max)),
            'right': ((x_max, y_max), (x_max, 0)),
            'bottom': ((x_max, 0), (0, 0))
        }
        for robot_id in robot_ids:
            data = self._field[robot_id]
            line_segs[robot_id] = self._get_line_seg(data, now)
        # Calculate bumps as intersections of line segments
        bumps = self._get_intersections(line_segs)
        for (a_id, b_id), coords in bumps.items():
            if isinstance(a_id, str):
                # a_id is a border
                continue
            # Set the "to" point to the intersection
            # TODO: Do not put robots on top of each other
            line_segs[a_id][1] = coords
        # Move robots to "to" points
        for robot_id in robot_ids:
            data = self._field[robot_id]
            data.update({
                'coords': line_segs[robot_id][1],
                'then': now
            })
        # Notify bumped robots
        for (a_id, b_id) in bumps.keys():
            if isinstance(a_id, str):
                # a_id is a border
                continue
            self._field[a_id]['robot'].bumped().send(None)

    @asyncio.coroutine
    def run_robots(self):
        loop = asyncio.get_event_loop()
        for robot_id, data in self._field.items():
            logger.info('<{name} {robot_id}> started'.format(
                name=data['robot'].__class__.__name__,
                robot_id=robot_id))
            # yield from data['robot'].started.send(data['coords'])  # TODO: Wait?
            data['robot'].started.send(data['coords'])
            data['then'] = loop.time()

        robot_ids = self.active_robots()
        while len(robot_ids) > 1:
            yield from self._update_radar(robot_ids)
            yield from self._move_robots(robot_ids)

    def run(self):
        asyncio.Task(self.run_robots())
        loop = asyncio.get_event_loop()
        loop.run_until_complete()

        winners = self.active_robots()
        if len(winners):
            winner = winners.pop()
            name = self._field[winner]['robot'].__class__.__name__
            return name


def import_robots(robot_names):
    classes = []
    for robot_name in robot_names:
        module_name, class_name = robot_name.rsplit('.', 1)
        try:
            module = __import__(module_name, globals(), locals(), class_name, -1)
            class_ = getattr(module, class_name)
        except ImportError:
            print('Unable to import "{}". Skipping robot.'.format(robot_name), file=sys.stderr)
            continue
        classes.append(class_)
    return classes


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('robot_names', nargs='+', help='names of robot classes')
    args = parser.parse_args()

    Robots = import_robots(args.robot_names)
    game = Game(Robots)
    winner_name = game.run()
    if winner_name:
        print('The winner is {}'.format(winner_name))
    else:
        print('All robots were destroyed')
