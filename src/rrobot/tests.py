import doctest
import unittest
import math
import rrobot.game
import rrobot.maths
import rrobot.sample_robot


def load_tests(loader, tests, ignore):

    # Nest GetHeadingP2PTest so that it can't be run without passing __init__ params
    class GetHeadingP2PTest(unittest.TestCase):
        known_values = [
            # p1, p2, known heading in degrees
            ((0, 0), (1, 0), 0),
            ((0, 0), (1, 1), 45),
            ((0, 0), (0, 1), 90),
            ((0, 0), (-1, 1), 135),
            ((0, 0), (-1, 0), 180),
            ((0, 0), (-1, -1), 225),
            ((0, 0), (0, -1), 270),
            ((0, 0), (1, -1), 315),
        ]

        def __init__(self, p1, p2, degs):
            unittest.TestCase.__init__(self)
            self.p1 = p1
            self.p2 = p2
            self.degs = degs

        def runTest(self):
            """
            The heading from self.p1 to self.p2 should equal self.degs
            """
            heading = rrobot.maths.get_heading_p2p(self.p1, self.p2)
            rads = math.radians(self.degs)
            self.assertEqual(heading, rads)

    # Add GetHeadingP2PTest for all known values
    tests.addTests(GetHeadingP2PTest(p1, p2, degs) for p1, p2, degs in GetHeadingP2PTest.known_values)
    # Add doctests
    tests.addTests(doctest.DocTestSuite(rrobot.maths))
    tests.addTests(doctest.DocTestSuite(rrobot.game))
    tests.addTests(doctest.DocTestSuite(rrobot.sample_robot))
    return tests


if __name__ == '__main__':
    unittest.main()
