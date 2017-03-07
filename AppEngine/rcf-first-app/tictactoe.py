"""
Tic Tac Toe driver program.

Utilize a table which, for each position,
gives a list of best moves.

Copyright 2009, Robert C. Field

"""
import sys
import os
import datetime
import cgi
import random

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

import MoveTable
import ClickRecord
import Analysis


google_analytics_insert="""
<script type="text/javascript">

var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-18951803-1']);
_gaq.push(['_trackPageview']);

(function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();

</script>
"""

class Position(object):
  """

  Positions in tic-tac-toe can be convienently summarized by a single
  integer, representing individual squares by an integer multiple of a
  power of three.

  .X.
  .X0
  .0X

  would be, having the upper left square as the units position:

  0*1 + 1*3 + 0*9 + 0*27 + 1*81 + 2*243 + 0*729 + 2*2187 + 1*6561

  which sums to 11505.  That value could be used as the lookup into a
  table of moves.

  This class provides functions to do this, while recording a
  position.

  """

  EMPTY = 0
  X = 1
  Oh = 2

  def __init__(self, position):
    self.pos = position

  def square_value(self, row, col):
    """

    Go from (row, column) do an index into an array.

    """
    where =3*row + col
    value = (self.pos / (3 ** where)) % 3
    return value

  def is_filled(self, row, col):
    value = self.square_value(row, col)
    return value != 0

  def get_pos(self):
    return self.pos

  def add_x(self, row, col):
    where = 3*row + col
    self.pos += (Position.X * (3 ** where))

  def add_oh(self, row, col):
    where = 3*row + col
    self.pos += (Position.Oh * (3 ** where))

  def get_empty_squares(self):
    """

    Return a list of the empty squares as (row, column) tuples.

    """
    return [(r, c) for r in range(0,3) for c in range(0, 3) if not self.is_filled(r, c)]

  def explode_position(self):
    """

    Return an array which has the position, based on the stored
    integer value.

    """

    result = []
    num = self.pos
    for where in range(9):
      result.append(int(num % 3))
      num /= 3
    return result

class WinDetector(object):
  wins = [[0, 1, 2], [3, 4, 5], [6, 7, 8],
          [0, 3, 6], [1, 4, 7], [2, 5, 8],
          [0, 4, 8], [2, 4, 6]]

  @staticmethod
  def is_winner(position):
    explode = position.explode_position()
    for w in WinDetector.wins:
      #print >>sys.stderr, w
      if ((explode[w[0]] == explode[w[1]]) and
          (explode[w[0]] == explode[w[2]]) and
          (explode[w[0]] != 0)):
        if explode[w[0]] == 1:
          return [Position.X, w]
        else:
          return [Position.Oh, w]
    return None # nobody is winning
        
class MoveGenerator(object):
  def __init__(self, pos, is_perfect = True):
    self.position = Position(pos)
    self.is_perfect = is_perfect

  def get_move(self):
    if self.is_perfect:
      if not MoveTable.MoveTable.move_dictionary.has_key(self.position.get_pos()):
        return None
      possible = MoveTable.MoveTable.move_dictionary[self.position.get_pos()]
      if len(possible) == 0:
        return None
      else:
        choice = random.choice(possible)
        return (choice / 3, choice % 3)
    else:
      possible = self.position.get_empty_squares()
      if len(possible) == 0:
        return None
      else:
        choice = random.choice(possible)
        return choice

class MainPage(webapp.RequestHandler):

  """

  Put up a page with the tic-tac-toe board, and interpret clicks as
  moves.

  Only empty squares are "live".

  In addition, have a "New Game" clickable area.

  """

  # If True, the computer makes perfect moves,
  # otherwise random moves.
  is_perfect = False

  @staticmethod
  def interpret_choice(choice):
    if len(choice) != 2:
      return None
    if choice[0] != 'C':
      return None
    if choice[1].isdigit():
      return int(choice[1])
    else:
      return None

  @staticmethod
  def generate_tag_for_image(image):
    return '<td><IMG src="%s" ALT="Marker"/></td>' % image

  @staticmethod
  def generate_tag_for_input_image(image, command):
    return (('<input type="image" src="images/%s" ' % image)
              + ('name="%s" ' % command)
              + '/>')

  @staticmethod
  def generate_empty_tag(row, col, is_live):
    # if it's a live square, have a clickable image
    # otherwise just a the image
    if is_live:
      return ('<td>'
              + '<input type="image" src="/images/blank.png" '
              + ('name="C%d%d" ' % (row, col))
              + '/></td>')
    else:
      return MainPage.generate_tag_for_image('/images/blank.png')

  @staticmethod
  def generate_used_tag(val, winner):
    # Determine the image for a square
    # X or Oh, part of a winning row or not
    if val == Position.X:
      if winner:
        return MainPage.generate_tag_for_image('/images/reverse_x.png')
      else:
        return MainPage.generate_tag_for_image('/images/big_x.png')
    else:
      if winner:
        return MainPage.generate_tag_for_image('/images/reverse_oh.png')
      else:
        return MainPage.generate_tag_for_image('/images/big_oh.png')

  @staticmethod
  def generate_tag(position, winner, row, col):
    # create the correct image tag for (row, col)
    value = position.square_value(row, col)
    where = 3*row + col
    if winner != None:
      winning_square = (where in winner[1]) and (value == winner[0])
    else:
      winning_square = None
    if value == Position.X:
      return MainPage.generate_used_tag(Position.X, winning_square)
    elif value == Position.Oh:
      return MainPage.generate_used_tag(Position.Oh, winning_square)
    else:
      return MainPage.generate_empty_tag(row, col, winner == None)

  @staticmethod
  def build_table(pos):
    # Build the entire table, including the clickable and non-clicable
    # squares and the separators, inside a table.
    the_position = Position(pos)
    #print >>sys.stderr, "EMPTY", the_position.get_empty_squares()
    #print >>sys.stderr, the_position.explode_position()
    winner = WinDetector.is_winner(the_position)
    #print >>sys.stderr, winner
    out = '<table class="mono" border="0" cellspacing="0" cellpadding="0">'
    index = 0
    for row in range(0, 5):
      out = out + '<tr>'
      for col in range(0, 5):
        if (row % 2) == 0:
          if (col % 2) == 0:
            out = out + MainPage.generate_tag(the_position, winner, row/2, col/2)
          else:
            out = out + '<td><IMG src="/images/vert_bar.png" alt="VERT BAR"/></td>'
        else:
          if (col %2 == 0):
            out = out + '<td><IMG src="/images/horiz_bar.png" alt="VERT BAR"/></td>'
          else:
            out = (out
                   + '<td>'
                   + '<input type="IMAGE" name="little_square" '
                   + 'src="/images/little_square.png" BORDER="0" '
                   + 'alt="LITTLE SQUARE"/></td>')
      out = out + '</tr>'
    out += '</table>'
    return out

  @staticmethod
  def generate_move_type(text):
    return """<button class="choice_button" name="move_type" value="move_type">%s</button>""" % text

  @staticmethod
  def generate_button_switch_to_perfect():
    return MainPage.generate_move_type("UNBEATABLE")

  @staticmethod
  def generate_button_switch_to_random():
    return MainPage.generate_move_type("RANDOM PLAY")

  def determine_if_local(self):
    # return true of it appears to be running on local
    # development machine
    the_key = "SERVER_NAME"
    if os.environ.has_key(the_key):
      return (os.environ[the_key].find('localhost') > -1)
    # default to local operation
    return True

  def process_form_for_square(self, form, perfect_play):
    # scan the possible clicks, including on live
    # squares, then allow the computer to move, and
    # make any needed changes on the position.
    if form.has_key('position'):
      pos_value = int(form['position'].value)
    else:
      pos_value = 0
    the_position = Position(pos_value)
    for row in range(0,3):
      for col in range(0,3):
        key = 'C%d%d.x' % (row, col)
        if form.has_key(key):
          the_position.add_x(row, col)
          winner = WinDetector.is_winner(the_position)
          if winner == None:
            m_gen = MoveGenerator(the_position.get_pos(),
                                  is_perfect = perfect_play)
            move = m_gen.get_move()
            if move != None:
              the_position.add_oh(move[0], move[1])
              #print >>sys.stderr, "MOVE", move, the_position.get_pos()
          return the_position.get_pos()
    return the_position.get_pos()

  def allow_analytics(self):
    return True
    return False

  def analysis_text(self):
    if self.allow_analytics():
      return (('<br>RUNNING LOCALLY</br>')
              if self.determine_if_local() 
              else (('<br>RUNNING ON GOOGLE %s</br>')
                    % (Analysis.Analytics.analytics_text())))
    else:
      return ""

  def determine_host(self):
    key = 'REMOTE_ADDR'
    if os.environ.has_key(key):
      return str(os.environ[key])
    else:
      return "**UNKNOWN**"

  def is_skippable_host(self, the_host = None):
    if the_host is None:
      the_host = self.determine_host()
    return (the_host,
            ((the_host == '69.12.245.117') or
             (the_host == '**UNKNOWN**')))

  def conditionally_record_host(self):
    (should_skip, the_host) = self.is_skippable_host()
    if not should_skip:
      click_record = ClickRecord(refer=the_host,
                                 position = 93, click = -193)
      click_record.put()
    else:
      pass

  def create_move_indicators(self, perfect_play):
    return 'PERFECT' if perfect_play else 'STUPID'
    if perfect_play:
      move_type = MainPage.generate_button_switch_to_random()
      play_type = 'PERFECT'
    else:
      move_type = MainPage.generate_button_switch_to_perfect()
      play_type = 'STUPID'
    return (move_type, play_type)

  def create_game_status(self, perfect_play):
    return ("""<input type="hidden" name="play_algorithm" value="%s"></input>"""
            % ('perfect' if perfect_play else 'random'))

  def get(self):
    self.conditionally_record_host()
    form = cgi.FieldStorage()
    action = "NONE"
    add_on = 0
    special_text = 'special ' + str(form)
    #print >>sys.stderr, form.keys()
    # the ".x" is for the graphic reset button
    old_game = form.has_key("existing_game")
    perfect_play = MainPage.is_perfect
    if form.has_key("play_algorithm"):
      special_text += "has algo key"
      perfect_play = (form["play_algorithm"].value == "perfect")
    if form.has_key('gimme_perfect'):
      perfect_play = True
    elif form.has_key('gimme_stupid'):
      perfect_play = False

    
    if form.has_key('reset_game') or form.has_key('reset.x'):
      pos_value = 0 # corresponds to empty board
    else:
      pos_value = self.process_form_for_square(form, perfect_play)

    play_type = self.create_move_indicators(perfect_play)

    special_text = ''

    winning = WinDetector.is_winner(Position(pos_value))
    winner_text = "WINNER" if winning else "PLAY ON"

    template_values = {
      'winner_text':winner_text,
      'action': action,
      'pos': pos_value,
      'the_table': MainPage.build_table(pos_value),
      'play_type': play_type,
      'analytics_insert':("%s<br>%s<br>" % (self.analysis_text(), "")),
      'game_status':self.create_game_status(perfect_play) + special_text,
      }

    path = os.path.join (os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):
    self.get()

application = webapp.WSGIApplication(
  [('/', MainPage),
   ('/button', MainPage),
   ('/buttontwo', MainPage)],
  debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  #print >>sys.stderr, "MAIN CALLED"
  main()
