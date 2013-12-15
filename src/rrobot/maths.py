# -*- coding: utf-8 -*-
import math
import numpy as np


def is_in_angle(p1, h1, rads, p2):
    """
    Given the heading h1 of a vector from p1, and the range of radians
    rads across h1 (i.e. rads/2 on either side of h1), determine
    whether p2 is within that range.

    >>> is_in_angle((1, 1), 0, 0.2, (1, 2))
    True
    >>> is_in_angle((1, 2), 0, 0.2, (1, 1))
    False

    """
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2:
        if y2 >= y1:
            h2 = 0
        else:
            h2 = math.pi
    else:
        h2 = math.atan((y2 - y1)/(x2 - x1))
    half_rads = rads / 2
    return h1 - half_rads < h2 < h1 + half_rads


def get_heading_p2p(p1, p2):
    """
    Return the heading from p1 to p2 in radians

    >>> get_heading_p2p((0, 0), (1, 1))
    0.7853981633974483

    """
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    if dx == 0:
        # Vertical
        if dy > 0:
            # p2 is above p1
            rads = math.pi / 2  # 90°
        else:
            # p2 is below p1
            rads = math.pi * 1.5  # 270°
    else:
        if dx > 0 and dy >= 0:
            # First quadrant
            rads = math.atan(dy/dx)
        elif dx > 0 and dy < 0:
            # Fourth quadrant
            rads = math.atan(dy/dx) + 2 * math.pi
        else:
            # Second and third quadrants
            rads = math.atan(dy/dx) + math.pi
    return rads


def get_dist(p1, p2):
    """
    Return the distance between two points

    >>> get_dist((0, 0), (3, 4))
    5.0

    """
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
