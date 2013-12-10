Norwegiɑn Blue rrɒbot
=====================

    "Remarkable rrɒbot, the Norwegiɑn Blue, id'n it, ay?" -- A pet shop keeper
    (sort of)

Norwegiɑn Blue rrɒbot (pronounced "norwegian blue robot") is primarily an
exercise in asynchronous programming in Python using the asyncio library,
available from Python 3.3 and incorporated in the standard library from Python
3.4.

It is also a game where programmed robots battle each other.


How to write a robot
--------------------

Extend the RobotBase class, and implement one or more of the following
methods:

* started, which is called when the game starts

* attacked, which is called when your robot is attacked by another robot

* bumped, which is called when your robot bumps or is bumped

* radar_updated, which is called at a (configurable) regular interval

Each method is a coroutine, and is sent relevant data.

Robots can set their speed and heading, and attack other robots.

A couple of sample robots are provided for reference.


Installation
------------

On a Debian-based operating system (Ubuntu, Mint, Raspbian, etc.), use the
following commands: ::

    $ sudo apt-get install python3 python3-dev python-virtualenv
    $ virtualenv -p /usr/bin/python3 venv
    $ source venv/bin/activate
    (venv)$ pip install -r requirements.txt


Testing
-------

To run tests and play games, use the following commands: ::

    (venv)$ export PYTHONPATH="`pwd`/src"
    (venv)$ cd src/rrobots
    (venv)$ python -m unittest tests.py
    (venv)$ python game.py sample_robots.MiddleBot sample_robots.HunterKiller


What's with the stupid name?
----------------------------

It alludes to the Monty Python "Parrot" sketch and "rrɒbot" is an anagram of
Parrot with a couple of letters rotated.
