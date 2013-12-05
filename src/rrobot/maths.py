"""
2D line segment intersection using vectors

see Computer Graphics by F.S. Hill

Copied shamelessly from http://www.cs.mun.ca/~rod/2500/notes/numpy-arrays/numpy-arrays.html


>>> p1 = (0.0, 0.0)
>>> p2 = (1.0, 0.0)
>>> p3 = (4.0, -5.0)
>>> p4 = (4.0, 2.0)
>>> seg_intersect(p1,p2, p3,p4)
(4.0, 0.0)

>>> p1 = (2.0, 2.0)
>>> p2 = (4.0, 3.0)
>>> p3 = (6.0, 0.0)
>>> p4 = (6.0, 3.0)
>>> print(seg_intersect(p1,p2, p3,p4))
(6.0, 4.0)

"""
import math
import numpy as np


def perp(a):
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b


def seg_intersect(a1, a2, b1, b2):
    """
    line segment a given by endpoints a1, a2
    line segment b given by endpoints b1, b2
    """
    a1 = np.array(a1)
    a2 = np.array(a2)
    b1 = np.array(b1)
    b2 = np.array(b2)
    da = a2 - a1
    db = b2 - b1
    dp = a1 - b1
    dap = perp(da)
    denom = np.dot(dap, db)
    if denom == 0:
        return None
    num = np.dot(dap, dp)
    intersect = (num / denom) * db + b1
    return tuple(intersect)


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
    h2 = math.atan((y2 - y1)/(x2 - x1))
    half_rads = rads / 2
    return h1 - half_rads < h2 < h1 + half_rads


def get_inverse_square(p1, p2, intensity):
    """
    Calculate the intensity at p2 if intensity (given at range == 1)
    drops at the inverse square of the distance from p1.

    >>> get_inverse_square((1, 1), (1, 2), 20)
    20.0
    >>> get_inverse_square((1, 1), (1, 3), 20)
    5.0

    """
    x1, y1 = p1
    x2, y2 = p2
    r = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return intensity / (r ** 2)


# From http://stackoverflow.com/a/9110966/245672
def find_intersections(a1, a2, b1, b2):
    a = np.matrix([a1, a2])
    b = np.matrix([b1, b2])
    # min, max and all for arrays
    amin = lambda x1, x2: np.where(x1 < x2, x1, x2)
    amax = lambda x1, x2: np.where(x1 > x2, x1, x2)
    aall = lambda abools: np.dstack(abools).all(axis=2)
    slope = lambda line: (lambda d: d[:, 1] / d[:, 0])(np.diff(line, axis=0))

    x11, x21 = np.meshgrid(a[:-1, 0], b[:-1, 0])
    x12, x22 = np.meshgrid(a[1:, 0], b[1:, 0])
    y11, y21 = np.meshgrid(a[:-1, 1], b[:-1, 1])
    y12, y22 = np.meshgrid(a[1:, 1], b[1:, 1])

    m1, m2 = np.meshgrid(slope(a), slope(b))
    m1inv, m2inv = 1 / m1, 1 / m2

    yi = (m1 * (x21 - x11 - m2inv * y21) + y11) / (1 - m1 * m2inv)
    xi = (yi - y21) * m2inv + x21

    xconds = (amin(x11, x12) < xi, xi <= amax(x11, x12),
              amin(x21, x22) < xi, xi <= amax(x21, x22) )
    yconds = (amin(y11, y12) < yi, yi <= amax(y11, y12),
              amin(y21, y22) < yi, yi <= amax(y21, y22) )

    return xi[aall(xconds)], yi[aall(yconds)]
