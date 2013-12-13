from rrobot.settings import settings
import copy
import json


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
        self.turns = {}
        self.robot_names = {}
        self.total_turns = 0

    def get_data(self, game):
        return {
            'robots': self.robot_names,
            'turns': {
                'total_turns': self.total_turns,
                'turns': self.turns
            }
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
        self.turns[game.time] = turn_state
        self.total_turns = max(self.total_turns, game.time)


class HTML(JSON):
    def done(self, game, *args, **kwargs):
        data = self.get_data(game)
        with open(self.filename, 'w') as f:
            f.write("""<html>
<head>
  <style>
    #stop{display:none}
  </style>
  <script src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
</head>
<body>
  <script>
    var current_turn = 1;
    var playing = true;
    var playback_speed = 10;
    var xDimension = 500;
    var yDimension = 500;
    var xMultiplier = xDimension/100.0;
    var yMultiplier = yDimension/100.0;
    function draw_robot(robot_id) {
      var robot_state = game_data['turns']['turns'][current_turn]['robots']['state'][robot_id];
      var context = document.getElementById("battle").getContext("2d");
      context.textAlign="left";
      context.textBaseLine="top";
      context.font = "bold 12px sans-serif";
      context.fillStyle= 'hsl(' + robot_id*robot_hue_multiplier + ', 100%, 35%)';

      context.fillText( game_data['robots'][robot_id], 0, robot_id+9);

      if ( robot_state == undefined )
      {
        context.fillText( "Destroyed", xDimension/2, robot_id+9);
      }
      else
      {
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
    function render()
    {
      $('#turn').text("Turn " + current_turn + " of " + game_data["turns"]["total_turns"]);
      var context = document.getElementById("battle").getContext("2d");
      context.clearRect(0,0,500,500);
      Object.keys(game_data["robots"]).forEach(function(robot_id){
        draw_robot( robot_id );
      });
    }
    function stop() {
      playing = false;
      $('#stop').hide();
      $('#play').show();
    }
    function play() {
      if(playing)
      {
        if (current_turn < game_data["turns"]["total_turns"])
        {
          current_turn += 1;
          render();
          setTimeout(play,playback_speed);
        }
        else
        {
          stop();
        }
      }
    }
  </script>
  <canvas id="battle" width="500" height="500"></canvas>
  <button id="start">&laquo;</button>
  <button id="prev">prev</button>
  <span id="turn"></span>
  <button id="next">next</button>
  <button id="play">play</button>
  <button id="stop">stop</button>
  <script>
    $().ready(function(){
      render();
    });
    $('#start').click(function(){
      stop();
      current_turn = 1;
      render();
    });
    $('#prev').click(function(){
      stop();
      if (current_turn > 1 )
      {
        current_turn -= 1;
        render();
      }
    });
    $('#next').click(function(){
      stop();
      if (current_turn < game_data["turns"]["total_turns"])
      {
        current_turn += 1;
        render();
      }
    });
    $('#play').click(function(){
      playing = true;
      setTimeout(play,playback_speed);
      $('#play').hide();
      $('#stop').show();
    });
    $('#stop').click(function(){
      stop();
    });
    var game_data=""" + format(json.dumps(data)) + """;
    var robot_hue_multiplier = 360/Object.keys(game_data["robots"]).length;
  </script>
</body>
</html>
""")


class visualise:
    def __init__(self, VisualisationKlass, *args, **kwargs):
        self.visualisor = VisualisationKlass(*args, **kwargs)

    def done(self, game):
        return not (len(game.active_robots()) > 1 and game.time < settings['max_duration'])

    def __call__(self, function):
        def __wrapped(game, *args, **kwargs):
            turn_len = settings['max_duration'] * 1000 / settings['radar_interval']
            if game.time < 2 * turn_len:
                self.visualisor.start(game, *args, **kwargs)
            self.visualisor.before(game, *args, **kwargs)
            result = function(game, *args, **kwargs)
            self.visualisor.after(game, *args, **kwargs)
            if self.done(game):
                self.visualisor.done(game, *args, **kwargs)
            return result
        return __wrapped
