# -*- coding: utf-8 -*-
import argparse
from importlib import import_module
import math
import asyncio
import logging
import random
import sys
from rrobot.settings import settings
from rrobot.maths import is_in_angle, get_dist
from rrobot import visualisation


# TODO: Add power. Attacks, acceleration, and maintaining speed should cost power


logger = logging.getLogger(__name__)


class Game(object):
    def __init__(self, robot_classes):
        """
        Accepts an iterable of Robot classes, and initialises a battlefield
        with them.
        """
        self._start_time = None  # Used to calculate game duration
        self._robots = []  # List of robots in the game
        x_max, y_max = settings['battlefield_size']
        for robot_id, Robot in enumerate(robot_classes):
            x_rand, y_rand = random.randrange(0, x_max), random.randrange(0, y_max)
            self._robots.append({
                'instance': Robot(self, robot_id),
                'coords': (float(x_rand), float(y_rand)),
                'speed': 0.0,
                'damage': 0,
                'heading': 0.0,
                'moved_at': None,  # Timestamp of last move
                'attacked_at': None  # Timestamp of last attack
            })

    def _get_robot_attr(self, robot_id, attr):
        return self._robots[robot_id][attr]

    def _set_robot_attr(self, robot_id, attr, value):
        logger.info('{robot} {attr} = {value!r}'.format(
            robot=self._robots[robot_id]['instance'],
            attr=attr,
            value=value))
        self._robots[robot_id][attr] = value

    @property
    def time(self):
        if self._start_time is None:
            return None  # Game not started
        loop = asyncio.get_event_loop()
        return loop.time() - self._start_time

    def get_coords(self, robot_id):
        return self._get_robot_attr(robot_id, 'coords')

    def get_damage(self, robot_id):
        return self._get_robot_attr(robot_id, 'damage')

    def get_heading(self, robot_id):
        return self._get_robot_attr(robot_id, 'heading')

    def set_heading(self, robot_id, rads):
        self._set_robot_attr(robot_id, 'heading', rads)
        logger.debug('({}°)'.format(int(math.degrees(rads))))

    def get_speed(self, robot_id):
        return self._get_robot_attr(robot_id, 'speed')

    def set_speed(self, robot_id, mps):
        mps = min(mps, settings['max_speed'])
        self._set_robot_attr(robot_id, 'speed', mps)

    def attack(self, robot_id):
        """
        Attacking is modelled on a Claymore. Damage is determined by the
        `inverse square`_ of the distance.


        .. _inverse square: http://en.wikipedia.org/wiki/Inverse-square_law
        """
        loop = asyncio.get_event_loop()
        now = loop.time()
        attacker = self._robots[robot_id]
        if (
            attacker['attacked_at'] is not None and
            (now - attacker['attacked_at']) * 1000 < settings['attack_interval']
        ):
            # Attacker must wait a second before firing
            logger.info('{robot} unable to attack yet'.format(robot=attacker['instance']))
            return
        attacker['attacked_at'] = now
        logger.info('{robot} attack'.format(robot=attacker['instance']))
        for target in self.active_robots():
            if is_in_angle(attacker['coords'],
                           attacker['heading'],
                           settings['attack_angle'],
                           target['coords']):
                dist = get_dist(attacker['coords'], target['coords'])
                dist = max(dist, 1)  # Make sure distance between robots is reasonable
                # Inverse square law. Drop values < 0
                damage = int(settings['attack_damage'] / dist ** 2)
                if damage:
                    logger.info('{robot} suffered {damage} damage'.format(
                        robot=target['instance'],
                        damage=damage))
                    target['damage'] += damage
                    target['instance'].attacked().send(attacker['instance'].__class__.__name__)

    def active_robots(self):
        """
        Returns a set of robot IDs with damage < 100%
        """
        return [r for r in self._robots if r['damage'] < 100]

    @staticmethod
    def _get_dest(data, now):
        """
        Calculates the destination of a move based on the given robot data and
        the current time.

        >>> data = {
        ...     'coords': (2, 2),
        ...     'moved_at': 1,
        ...     'speed': 5,
        ...     'heading': 0
        ... }
        >>> Game._get_dest(data, 2)
        (7.0, 2.0)

        """
        # Calc new position
        x, y = data['coords']
        t_d = now - data['moved_at']
        dist = data['speed'] * t_d  # speed is in m/s; t_d is in s
        x_d = math.cos(data['heading']) * dist
        y_d = math.sin(data['heading']) * dist
        x_new = x + x_d
        y_new = y + y_d
        # Set 0 <= x_new, y_new <= settings['battlefield_size']
        # TODO: Use line segment intersection with border if out of bounds
        x_max, y_max = settings['battlefield_size']
        x_new = max(0, min(x_new, x_max))
        y_new = max(0, min(y_new, y_max))
        return x_new, y_new

    @asyncio.coroutine
    def _update_radar(self, robots):
        radar = [{'name': r['instance'].__class__.__name__, 'coords': r['coords']} for r in self._robots]
        logger.info('Radar: %s', radar)
        for robot in robots:
            logger.info('{robot} radar updated'.format(robot=robot['instance']))
            robot['instance'].radar_updated().send(radar)

    @visualisation.visualise(visualisation.HTML, 'output.html')
    # @visualisation.visualise(visualisation.JSON, 'output.json')
    @asyncio.coroutine
    def _move_robots(self, robots):
        loop = asyncio.get_event_loop()
        now = loop.time()
        # TODO: Calculate collisions of robots with each other using vectors
        for robot in robots:
            dest = self._get_dest(robot, now)
            # Move robots to "to" points
            robot.update({
                'coords': dest,
                'moved_at': now
            })
            # Stop bumped robots and notify them
            x_max, y_max = settings['battlefield_size']
            x, y = dest
            bumper = None
            if x == 0:
                bumper = 'left'
            elif x == x_max:
                bumper = 'right'
            elif y == 0:
                bumper = 'bottom'
            elif y == y_max:
                bumper = 'top'
            if bumper:
                self.set_speed(robot['instance'].id, 0)
                robot['instance'].bumped().send(bumper)

    @asyncio.coroutine
    def run_robots(self):
        loop = asyncio.get_event_loop()
        now = loop.time()
        self._start_time = now
        for robot in self._robots:
            logger.info('{robot} started at {coords}'.format(
                robot=robot['instance'],
                coords=robot['coords']))
            robot['instance'].started().send(robot['coords'])
            robot['moved_at'] = now

        robots = self.active_robots()
        while len(robots) > 1 and self.time < settings['max_duration']:
            logger.info('----------------------------------------')
            logger.info('Time: %s', self.time)
            yield from self._update_radar(robots)
            yield from self._move_robots(robots)
            yield from asyncio.sleep(settings['radar_interval'] / 1000)
            robots = self.active_robots()

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run_robots())

        winners = ["{} (damage {})".format(r['instance'].__class__.__name__, r['damage'])
                   for r in self.active_robots()]
        return winners


def import_robots(robot_names):
    classes = []
    for robot_name in robot_names:
        module_name, class_name = robot_name.rsplit('.', 1)
        try:
            module = import_module(module_name)
            class_ = getattr(module, class_name)
        except ImportError as err:
            logger.error('Unable to import "{}". Skipping robot.'.format(robot_name))
            continue
        classes.append(class_)
    return classes


def main(parser_args):
    logger.addHandler(logging.StreamHandler(sys.stderr))
    logger.setLevel(settings['log_level'])
    logger.info('Robots: {}'.format(parser_args.robot_names))
    robot_classes = import_robots(parser_args.robot_names)
    game = Game(robot_classes)
    winners = game.run()
    if len(winners) > 1:
        print('Stalemate. The survivors are ' + ', '.join(winners))
    elif len(winners) == 1:
        print('The winner is ' + winners[0])
    else:
        print('All robots were destroyed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('robot_names', nargs='+', help='names of robot classes')
    args = parser.parse_args()
    main(args)
