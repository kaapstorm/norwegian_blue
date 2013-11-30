try:
    # Support Python >= 3.4
    import asyncio
except ImportError:
    # Support Python < 3.4
    import flower


class Game(object):
    pass
