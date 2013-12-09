import doctest
import unittest
import rrobot.game
import rrobot.maths
import rrobot.sample_robot


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(rrobot.maths))
    tests.addTests(doctest.DocTestSuite(rrobot.game))
    tests.addTests(doctest.DocTestSuite(rrobot.sample_robot))
    return tests
