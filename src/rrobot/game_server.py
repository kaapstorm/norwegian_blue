"""
The game server reads tasks off the queue and executes them.

Requests are pulled off the message queue, timestamped, and added to the
ActionQueue. If the last item in the ActionQueue has a later timestamp than
the new item, it is inserted, not appended.

After a minimum period, to allow late robots to submit requests, ActionQueue
items are executed. Requests submitted later than the last executed item are
performed late -- we do not change the past.

The timestamp allows accurate calculation of location at speed.

"""
import zmq


class GameServer(object):
    def __init__(self):
        context = zmq.Context()
        self._socket = context.socket(zmq.REP)
        self._socket.bind('tcp://*:5555')

    def run(self):
        while True:
            req = self._socket.recv()
            params = req.decode('utf-8').split(' ')
            cmd = params.pop(0)
            if cmd.startswith('get_'):
                # This is a synchronous request. Reply immediately.
                # TODO: Do stuff here
                reply = 'foo'
                self._socket.send(reply.encode('utf-8'))
            else:
                # This is an asynchronous request
                # TODO: Do stuff here
                pass


if __name__ == '__main__':
    server = GameServer()
    server.run()
