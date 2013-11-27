class Game(object):
    def get_coords(self, robot_id):
        pass

    def get_damage(self, robot_id):
        pass

    def get_heading(self, robot_id):
        pass

    def enqueue_heading(self, robot_id, radians):
        pass

    def get_speed(self, robot_id):
        pass

    def enqueue_speed(self, robot_id, mps):
        pass

    def enqueue_strike(self, robot_id):
        pass


game = Game()
