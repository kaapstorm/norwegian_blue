"""
The game client places tasks on a queue which are handled by a game server.

.. TODO:: Use PUB SUB pattern as described here:
          http://zguide.zeromq.org/py:all
          Or async client/server


Async client/server: ::

    import zmq
    import threading
    import time
    from random import choice

    __author__ = "Felipe Cruz <felipecruz@loogica.net>"
    __license__ = "MIT/X11"

    class ClientTask(threading.Thread):
        '''ClientTask'''
        def __init__(self):
            threading.Thread.__init__ (self)

        def run(self):
            context = zmq.Context()
            socket = context.socket(zmq.DEALER)
            identity = 'worker-%d' % (choice([0,1,2,3,4,5,6,7,8,9]))
            socket.setsockopt(zmq.IDENTITY, identity )
            socket.connect('tcp://localhost:5570')
            print 'Client %s started' % (identity)
            poll = zmq.Poller()
            poll.register(socket, zmq.POLLIN)
            reqs = 0
            while True:
                for i in xrange(5):
                    sockets = dict(poll.poll(1000))
                    if socket in sockets:
                        if sockets[socket] == zmq.POLLIN:
                            msg = socket.recv()
                            print 'Client %s received: %s\n' % (identity, msg)
                            del msg
                reqs = reqs + 1
                print 'Req #%d sent..' % (reqs)
                socket.send('request #%d' % (reqs))

            socket.close()
            context.term()

    class ServerTask(threading.Thread):
        '''ServerTask'''
        def __init__(self):
            threading.Thread.__init__ (self)

        def run(self):
            context = zmq.Context()
            frontend = context.socket(zmq.ROUTER)
            frontend.bind('tcp://*:5570')

            backend = context.socket(zmq.DEALER)
            backend.bind('inproc://backend')

            workers = []
            for i in xrange(5):
                worker = ServerWorker(context)
                worker.start()
                workers.append(worker)

            poll = zmq.Poller()
            poll.register(frontend, zmq.POLLIN)
            poll.register(backend, zmq.POLLIN)

            while True:
                sockets = dict(poll.poll())
                if frontend in sockets:
                    if sockets[frontend] == zmq.POLLIN:
                        _id = frontend.recv()
                        msg = frontend.recv()
                        print 'Server received %s id %s\n' % (msg, _id)
                        backend.send(_id, zmq.SNDMORE)
                        backend.send(msg)
                if backend in sockets:
                    if sockets[backend] == zmq.POLLIN:
                        _id = backend.recv()
                        msg = backend.recv()
                        print 'Sending to frontend %s id %s\n' % (msg, _id)
                        frontend.send(_id, zmq.SNDMORE)
                        frontend.send(msg)

            frontend.close()
            backend.close()
            context.term()

    class ServerWorker(threading.Thread):
        '''ServerWorker'''
        def __init__(self, context):
            threading.Thread.__init__ (self)
            self.context = context

        def run(self):
            worker = self.context.socket(zmq.DEALER)
            worker.connect('inproc://backend')
            print 'Worker started'
            while True:
                _id = worker.recv()
                msg = worker.recv()
                print 'Worker received %s from %s' % (msg, _id)
                replies = choice(xrange(5))
                for i in xrange(replies):
                    time.sleep(1/choice(range(1,10)))
                    worker.send(_id, zmq.SNDMORE)
                    worker.send(msg)

                del msg

            worker.close()

    def main():
        '''main function'''
        server = ServerTask()
        server.start()
        for i in xrange(3):
            client = ClientTask()
            client.start()

        server.join()

    if __name__ == "__main__":
        main()


"""
import zmq


class GameClient(object):
    def __init__(self):
        context = zmq.Context()
        self._socket = context.socket(zmq.REQ)
        # Connect to game server
        self._socket.connect("tcp://localhost:5555")

    def send_sync(self, name, robot_id):
        """
        Send a synchronous request to the game server
        """
        request = ' '.join([name, str(robot_id)])
        self._socket.send(request.encode('utf-8'))
        reply = self._socket.recv()
        return reply

    def send_async(self, name, robot_id, *args):
        if args:
            params = u' '.join([str(a) for a in args])  # Support Python 2 & 3
            request = u' '.join([name, str(robot_id), params])
        else:
            request = u' '.join([name, str(robot_id)])
        self._socket.send(request.encode('utf-8'))
