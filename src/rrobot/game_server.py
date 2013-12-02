"""
The game server reads tasks off the queue.

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
