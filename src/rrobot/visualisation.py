import copy
import json
from string import Template
from rrobot.settings import settings


class Visualisor:
    def start(self, game, *args, **kwargs):
        pass

    def before(self, game, *args, **kwargs):
        pass

    def after(self, game, *args, **kwargs):
        pass

    def done(self, game, *args, **kwargs):
        pass


class JSON(Visualisor):
    def __init__(self, filename):
        self.filename = filename
        self.turns = []
        self.robot_names = {}

    def get_data(self, game):
        return {
            'robots': self.robot_names,
            'turns': self.turns
        }

    def done(self, game, *args, **kwargs):
        data = self.get_data(game)
        with open(self.filename, 'w') as f:
            f.write(json.dumps(data))

    def after(self, game, *args, **kwargs):
        turn_state = {'robots': {'state': {}}}
        for robot in game.active_robots():
            robot_id = robot['instance'].id
            if not robot_id in self.robot_names:
                self.robot_names[robot_id] = robot['instance'].__class__.__name__
            robot_state = copy.copy(robot)
            del robot_state['instance']
            turn_state['robots']['state'][robot_id] = robot_state
        self.turns.append(turn_state)


class HTML(JSON):
    def done(self, game, *args, **kwargs):

        class EuroTemplate(Template):
            delimiter = '€'

        data = self.get_data(game)
        template = EuroTemplate("""
<!DOCTYPE html>
<html>
<head>
  <style>
    #stop { display: none; }
    #battle { display: block; }
  </style>
  <script type="text/javascript" src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
  <script type="text/javascript">

    var game_data = €{game_data};

    var current_turn = 0;
    var playing = true;
    var playback_speed = 10;
    var xDimension = 500;
    var yDimension = 500;
    var xMultiplier = xDimension/100.0;
    var yMultiplier = yDimension/100.0;
    var robot_hue_multiplier = 360/Object.keys(game_data["robots"]).length;

    function draw_robot(robot_id) {
      if (current_turn < game_data['turns'].length) {
        var robot_state = game_data['turns'][current_turn]['robots']['state'][robot_id];
      }
      var context = document.getElementById("battle").getContext("2d");
      context.textAlign="left";
      context.textBaseLine="top";
      context.font = "bold 12px sans-serif";
      context.fillStyle= 'hsl(' + robot_id*robot_hue_multiplier + ', 100%, 35%)';

      context.fillText( game_data['robots'][robot_id], 0, robot_id+9);

      if ( robot_state == undefined ) {
        context.fillText( "Destroyed", xDimension/2, robot_id+9);
      } else {
        var x = robot_state['coords'][0]*xMultiplier;
        var y = robot_state['coords'][1]*yMultiplier;
        context.fillRect(x-1,y-1,3,3);

        var health = 100 - robot_state['damage'];
        if (health > 0)
        {
          context.fillRect( xDimension/2, robot_id*12 + 5, health*xDimension*4/500, 3 );
        }
      }
    }

    function render() {
      $('#turn').text("Turn " + (current_turn + 1) + " of " + game_data["turns"].length);
      var context = document.getElementById("battle").getContext("2d");
      context.clearRect(0,0,500,500);
      Object.keys(game_data["robots"]).forEach(function(robot_id) {
        draw_robot( robot_id );
      });
    }
    function stop() {
      playing = false;
      $('#stop').hide();
      $('#play').show();
    }
    function play() {
      if (playing) {
        if (current_turn < game_data["turns"].length) {
          render();
          current_turn += 1;
          setTimeout(play,playback_speed);
        } else {
          stop();
        }
      }
    }

    $().ready(function() {
      $('#start').click(function() {
        stop();
        current_turn = 0;
        render();
      });
      $('#prev').click(function() {
        stop();
        if (current_turn > 0) {
          current_turn -= 1;
          render();
        }
      });
      $('#next').click(function() {
        stop();
        if (current_turn < game_data["turns"].length) {
          render();
          current_turn += 1;
        }
      });
      $('#play').click(function() {
        playing = true;
        setTimeout(play,playback_speed);
        $('#play').hide();
        $('#stop').show();
      });
      $('#stop').click(function() {
        stop();
      });

      render();
    });

  </script>
</head>
<body>
  <canvas id="battle" width="500" height="500"></canvas>
  <button id="start">&laquo;</button>
  <button id="prev">prev</button>
  <span id="turn"></span>
  <button id="next">next</button>
  <button id="play">play</button>
  <button id="stop">stop</button>
</body>
</html>""")
        with open(self.filename, 'w') as f:
            f.write(template.substitute(game_data=json.dumps(data)))


class visualise:
    def __init__(self, VisualisationKlass, *args, **kwargs):
        self.visualisor = VisualisationKlass(*args, **kwargs)

    def done(self, game):
        return not (len(game.active_robots()) > 1 and game.time < settings['max_duration'])

    def __call__(self, function):
        def __wrapped(game, *args, **kwargs):
            turn_len = settings['max_duration'] * 1000 / settings['radar_interval']
            if game.time * 1000 < 2 * turn_len:
                self.visualisor.start(game, *args, **kwargs)
            self.visualisor.before(game, *args, **kwargs)
            result = function(game, *args, **kwargs)
            self.visualisor.after(game, *args, **kwargs)
            if self.done(game):
                self.visualisor.done(game, *args, **kwargs)
            return result
        return __wrapped
